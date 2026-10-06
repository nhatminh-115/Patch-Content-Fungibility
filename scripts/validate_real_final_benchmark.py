"""Fail-closed publication gate for outputs/fungibility_real_final.

This validator never treats historical final-consolidation artifacts as real
classification or latency evidence. It writes assertion results to the
real-final validation manifest and exits nonzero unless every gate passes.
"""

from __future__ import annotations

import csv
import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "fungibility_real_final"
MANIFEST = OUT / "validation_manifest.json"
TOLERANCE = 5e-4


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def record(checks: dict, name: str, passed: bool, detail: str) -> None:
    checks[name] = {"status": "PASS" if passed else "FAIL", "detail": detail}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    checks: dict[str, dict[str, str]] = {}

    # 1-4: guard the real-final generators against known proxy patterns.
    generator_paths = [ROOT / "scripts" / "run_real_final_accuracy.py",
                       ROOT / "scripts" / "run_real_final_throughput.py"]
    generator_text = "\n".join(p.read_text(encoding="utf-8") for p in generator_paths if p.exists())
    record(checks, "1_no_hardcoded_clean_accuracy",
           bool(generator_text) and not re.search(r"clean_acc\s*[:=]\s*\d", generator_text),
           "Real-final generator source must exist and contain no hard-coded clean accuracy.")
    record(checks, "2_no_je_to_top1_heuristic",
           bool(generator_text) and not re.search(r"top.?1.{0,80}(?:JE|je_norm|mean_je)|(?:JE|je_norm|mean_je).{0,80}top.?1", generator_text, re.I),
           "Real-final generator source must not derive Top-1 from JE.")
    record(checks, "3_no_group_mean_je_multiplier_baselines",
           bool(generator_text) and not re.search(r"(?:rand|norm|attn|tome)[^\n=]*=\s*[^\n]*je[^\n]*\*\s*\d", generator_text, re.I),
           "Real-final baselines must execute their implementation rather than scale Group Mean JE.")
    record(checks, "4_no_toy_latency_loop",
           bool(generator_text) and not re.search(r"torch\.randn|for\s+_\s+in\s+range\([^\n]*\):[^\n]*(?:matmul|bmm)", generator_text),
           "Timing must execute actual pretrained models and compression callables.")

    # 5: a reported Top-1 row must be recoverable from an integer count.
    summary_path = OUT / "real_accuracy_summary.csv"
    top1_ok = summary_path.exists()
    top1_detail = "real_accuracy_summary.csv is absent."
    if top1_ok:
        rows = csv_rows(summary_path)
        top1_ok = bool(rows)
        for i, row in enumerate(rows, start=2):
            try:
                n = int(row["n"])
                count_float = float(row["correct_count"])
                top1 = float(row["top1_accuracy"])
                if n <= 0 or not count_float.is_integer() or abs(top1 - 100 * int(count_float) / n) > TOLERANCE:
                    top1_ok = False
                    break
            except (KeyError, ValueError):
                top1_ok = False
                break
        top1_detail = "Each Top-1 row must have integer correct_count, N, and matching 100*correct_count/N."
    record(checks, "5_top1_integer_count_provenance", top1_ok, top1_detail)

    # 6: each timing row carries provenance for the actual model callable.
    timing_path = OUT / "real_throughput_raw.csv"
    timing_ok = timing_path.exists()
    timing_detail = "real_throughput_raw.csv is absent."
    if timing_ok:
        rows = csv_rows(timing_path)
        required = {"actual_model_execution", "actual_callable", "checkpoint", "device", "precision",
                    "batch_size", "warmup_count", "measured_iterations"}
        timing_ok = bool(rows) and required.issubset(rows[0])
        timing_ok = timing_ok and all(row.get("actual_model_execution", "").lower() == "true"
                                      and row.get("actual_callable", "").strip() for row in rows)
        timing_detail = "Every raw timing row must identify the actual model execution and benchmark configuration."
    record(checks, "6_timing_actual_model_metadata", timing_ok, timing_detail)

    # 7: calibration and evaluation manifests must be disjoint.
    sample_path = OUT / "sample_manifest.csv"
    split_ok = sample_path.exists()
    split_detail = "sample_manifest.csv is absent."
    if split_ok:
        rows = csv_rows(sample_path)
        required = {"image_id", "label", "split"}
        split_ok = bool(rows) and required.issubset(rows[0])
        calibration = {r["image_id"] for r in rows if r.get("split", "").lower() == "calibration"}
        evaluation = {r["image_id"] for r in rows if r.get("split", "").lower() == "evaluation"}
        overlap = calibration & evaluation
        split_ok = split_ok and bool(calibration) and bool(evaluation) and not overlap
        split_detail = f"Calibration/evaluation image-id overlap: {len(overlap)}."
    record(checks, "7_calibration_evaluation_disjoint", split_ok, split_detail)

    # 8-9: enforce the known sample-size distinctions using source manifests.
    try:
        fg = read_json(ROOT / "outputs/fungibility_functional_geometry/validation_manifest.json")
        ac = read_json(ROOT / "outputs/fungibility_attention_causal_audit/validation_manifest.json")
        mb = read_json(ROOT / "outputs/fungibility_multiblock_operator/validation_manifest.json")
        record(checks, "8_mechanistic_studies_not_mislabeled_n1000",
               fg.get("num_images_pilot") == 100 and ac.get("num_eval_images") == 100
               and mb.get("num_heldout_perturbations") == 100,
               "Functional geometry=100 images; attention audit=100 images; multi-block=100 perturbations.")
    except (OSError, ValueError, KeyError) as exc:
        record(checks, "8_mechanistic_studies_not_mislabeled_n1000", False, str(exc))
    try:
        confirm = read_json(ROOT / "outputs/fungibility_operator_compression_confirmatory/validation_manifest.json")
        record(checks, "9_confirmatory_study_not_downgraded_to_n100",
               confirm.get("n_eval_images") == 1000,
               "Strict confirmatory operator-compression evaluation must remain N=1,000.")
    except (OSError, ValueError, KeyError) as exc:
        record(checks, "9_confirmatory_study_not_downgraded_to_n100", False, str(exc))

    # 10: publication-facing files may not cite historical proxy accuracy/timing.
    paper_paths = [ROOT / "docs" / name for name in (
        "PAPER_DRAFT.md", "PAPER_FINAL_CLAIMS_TABLE.md", "PAPER_FINAL_AUDIT.md",
        "PAPER_FINAL_EXPERIMENT_SUMMARY.md", "PAPER_NUMBER_TRACEABILITY.md",
        "PAPER_RECONCILIATION_REPORT.md")]
    paper_text = "\n".join(p.read_text(encoding="utf-8-sig") for p in paper_paths if p.exists())
    proxy_reference = re.search(r"fungibility_final_consolidation/(?:final_accuracy_table|final_throughput_table|final_pareto_frontier)\.csv", paper_text, re.I)
    record(checks, "10_no_proxy_accuracy_or_latency_citations", not bool(proxy_reference),
           "Paper-facing documents must not cite proxy consolidation accuracy/throughput/frontier CSVs as evidence.")

    # 11: evaluation-wide top-k selection is not a deployable fixed threshold.
    gate_claim = re.search(r"(?:top[- ]?30%|top[- ]?k).{0,100}deployable|deployable.{0,100}(?:top[- ]?30%|top[- ]?k)", paper_text, re.I)
    record(checks, "11_no_oracle_topk_as_deployable_gate", not bool(gate_claim),
           "Deployable gate claims must use a calibration-frozen threshold applied per image.")

    # 12: prevent paper edits until the new real benchmark is fully validated.
    draft_changed = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", "docs/PAPER_DRAFT.md"],
                                   cwd=ROOT, check=False).returncode != 0
    try:
        state = read_json(MANIFEST)
        outputs_passed = state.get("status") == "PASS" and state.get("authoritative") is True
    except (OSError, ValueError):
        outputs_passed = False
    record(checks, "12_paper_draft_gate", not draft_changed or outputs_passed,
           "PAPER_DRAFT must remain untouched until real outputs and all validation checks pass.")

    passed = all(item["status"] == "PASS" for item in checks.values())
    manifest = {
        "status": "PASS" if passed else "FAIL",
        "authoritative": passed,
        "checks": checks,
        "passed_count": sum(v["status"] == "PASS" for v in checks.values()),
        "assertion_count": len(checks),
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
