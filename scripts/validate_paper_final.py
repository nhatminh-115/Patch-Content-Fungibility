"""Fail-closed publication gate for the final manuscript and figure set."""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DRAFT = DOCS / "PAPER_DRAFT.md"
TRACE = DOCS / "PAPER_NUMBER_TRACEABILITY.md"
CLAIMS = DOCS / "PAPER_FINAL_CLAIMS_TABLE.md"
SAMPLES = DOCS / "PAPER_SAMPLE_SIZE_MAP.md"
FIGS = ROOT / "figures" / "paper_final_v3"


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def main() -> int:
    checks: dict[str, dict[str, str]] = {}

    def record(name: str, ok: bool, detail: str) -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail}

    required = [DRAFT, TRACE, CLAIMS, SAMPLES, ROOT / "docs/PAPER_SUBMISSION_READINESS.md"]
    record("required_manuscript_and_audit_docs", all(p.is_file() for p in required),
           "Draft, claims, traceability, sample-size map, and readiness record must exist.")
    text = DRAFT.read_text(encoding="utf-8-sig") if DRAFT.exists() else ""
    all_paper = "\n".join(p.read_text(encoding="utf-8-sig") for p in (DRAFT, TRACE, CLAIMS, SAMPLES) if p.exists())

    # Historical consolidation accuracy/timing tables were proxy-backed and are prohibited.
    proxy = re.search(r"fungibility_final_consolidation/(?:final_accuracy_table|final_throughput_table|final_pareto_frontier)\.csv", all_paper, re.I)
    record("no_proxy_accuracy_timing_or_frontier_sources", proxy is None,
           "No historical proxy accuracy, toy timing, or frontier CSV may be cited as empirical support.")
    stale = ["4432.0", "77.20", "sub-0.25 ms", "sub-0.25ms"]
    found = [s for s in stale if s.lower() in text.lower()]
    record("no_stale_practical_headline_values", not found,
           "Removed stale throughput, accuracy, and isolated-overhead headline claims." if not found else f"Found: {found}")

    # Sample units must be explicit and correctly separated.
    sample_ok = all(s in text for s in ("N=100 images", "N=100 held-out perturbations", "N=1,000 held-out images per architecture"))
    sample_ok = sample_ok and "N=1000" not in text
    record("mechanistic_sample_units_correct", sample_ok,
           "Attention/geometry image audits use N=100, multi-block uses perturbations, and confirmatory/carrier accuracy uses N=1,000 per model.")
    record("sample_map_and_claims_correct", all(s in SAMPLES.read_text(encoding="utf-8-sig") for s in ("N=100 evaluation images", "N=100 held-out perturbations", "N=1,000 held-out images per architecture"))
           and "N=100 held-out operator-space images" in CLAIMS.read_text(encoding="utf-8-sig"),
           "C2, C4/C5, confirmatory, and real-final counts are separately stated.")

    denom = re.search(r">\s*98\s*%.*?full[- ]J oracle compression benefit.*?(?:denominator|Group-Mean-to-full-J-oracle gain)", text, re.I | re.S)
    denom = denom or re.search(r"denominator.*?Group-Mean-to-full-J-oracle.*?benefit", text, re.I | re.S)
    record("full_j_benefit_denominator_explicit", bool(denom),
           "The >98% statement names the Group-Mean-to-full-J-oracle compression-benefit denominator.")
    pareto_overclaim = re.search(r"\b(?:strictly|universally|always)\s+(?:Pareto\s+)?(?:dominates?|dominant|frontier improvement)\b|general Pareto (?:dominance|improvement)", text, re.I)
    record("no_unsupported_pareto_dominance", pareto_overclaim is None,
           "Frontier language is limited to measured non-dominated points and bounded regimes.")
    unresolved = re.search(r"\b(?:TODO|FIXME|PLACEHOLDER|TBD|xxxxx|yyyyy)\b", text, re.I)
    record("no_unresolved_placeholders", unresolved is None,
           "No unresolved editorial or bibliography placeholders remain in the manuscript.")
    record("no_local_file_urls", "file:///" not in text.lower(),
           "Manuscript contains no machine-local file URL.")
    record("canonical_repo_name_correct", "ResCancel" not in text and "github.com/nhatminh-115/Patch-Content-Fungibility" in text,
           "Canonical repository is Patch-Content-Fungibility; workspace folder name is not presented as canonical.")
    record("no_invalid_v2_figure_paths", "paper_final_v2" not in text and "../figures/paper_final_v3/" in text,
           "Manuscript points only to regenerated v3 figures.")

    # BibTeX citation/reference consistency, including duplicate entries.
    cite_keys = set()
    for match in re.finditer(r"\\cite\w*\{([^}]+)\}", text):
        cite_keys.update(k.strip() for k in match.group(1).split(","))
    bib = text.split("```bibtex", 1)[1].split("```", 1)[0] if "```bibtex" in text else ""
    bib_keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib)
    duplicates = len(bib_keys) != len(set(bib_keys))
    unresolved_keys = cite_keys - set(bib_keys)
    uncited = set(bib_keys) - cite_keys
    record("bibliography_resolves_without_duplicates", not duplicates and not unresolved_keys and not uncited,
           f"{len(bib_keys)} entries; unresolved citations={sorted(unresolved_keys)}; uncited entries={sorted(uncited)}; duplicates={duplicates}.")

    paths = re.findall(r"\]\((\.\./figures/[^)]+)\)", text)
    missing = [p for p in paths if not (DOCS / p).resolve().is_file()]
    invalid = [p for p in paths if "paper_final_v2" in p or not p.endswith(".svg")]
    record("all_manuscript_figures_exist_and_are_v3_svg", bool(paths) and not missing and not invalid,
           f"Referenced figures={len(paths)}; missing={missing}; invalid={invalid}.")

    # Figure generation must be reproducible from the declared audited sources.
    figure_names = ["figure1_conceptual.svg", "figure2_depthwise.svg", "figure3_geometry_diversity.svg",
                    "figure4_anisotropy.svg", "figure5_value_end_to_end.svg", "figure6_confirmatory_frontier.svg",
                    "figure7_low_rank.svg", "supp/figureS1_real_carrier_boundary.svg"]
    absent = [n for n in figure_names if not (FIGS/n).is_file()]
    script = ROOT/"scripts/render_paper_final_v3.py"
    script_ok = script.exists() and "fungibility_real_final/real_accuracy_throughput_frontier.csv" in script.read_text(encoding="utf-8")
    record("publication_figures_present_and_source_scoped", not absent and script_ok,
           f"Missing figures={absent}; generator has real-final frontier input={script_ok}.")

    # Traceability matrix covers every numeric claim family carried into the draft.
    tr = TRACE.read_text(encoding="utf-8-sig") if TRACE.exists() else ""
    claim_families = ["+4.2 to +17.3", ">98%", "54.91%", "0.7079985", ".974717", "1.473962", "76.4/76.3/76.0", "0.784"]
    absent_families = [v for v in claim_families if v not in tr]
    record("quantitative_claims_traceable", not absent_families,
           f"Numeric evidence families absent from traceability map: {absent_families}.")

    passed = all(v["status"] == "PASS" for v in checks.values())
    manifest = {"status":"PASS" if passed else "FAIL", "checks":checks,
                "passed_count":sum(v["status"]=="PASS" for v in checks.values()), "assertion_count":len(checks)}
    out=ROOT/"outputs/fungibility_real_final/paper_final_validation.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
