"""Frozen G1 evaluation for signed Value-error token merging.

Run smoke, stability, pilot, then summarize. Later gates must not run after a
failed G1. All teacher suffix calls here are offline diagnostics only.
"""

import argparse
import io
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import spearmanr
import scipy
import timm
import torch

from patch_fungibility.counterfactual_merge import (
    apply_action, candidate_pool, forward_suffix_batch, initial_state,
    normalized_distortion, state_batch,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.signed_value_merging import captured_prefix, candidate_proxies, choose_minimum
from scripts.run_counterfactual_merge_pilot import (
    MODEL_CONFIG, SEED_CANDIDATE, calibration_records, image_bytes,
    model_weight_hash, portable_parquet_identity, prefix, sync,
)

PROTOCOL_COMMIT = "edb7fba"
BOOTSTRAP_SEED = 77112
METHODS = ("cosine", "attention_importance", "attention_value_distance", "raw_norm", "projected_norm")
SCALAR = METHODS[:3]
SIGNED = METHODS[3:]


def score_array(candidates, proxies):
    return {
        "cosine": np.array([-c["cosine"] for c in candidates]),
        **{key: proxies[key].detach().cpu().numpy() for key in METHODS[1:]},
    }


def paired_interval(values, seed=BOOTSTRAP_SEED):
    values = np.asarray(values, dtype=np.float64)
    rng = np.random.RandomState(seed)
    draws = values[rng.randint(len(values), size=(2000, len(values)))].mean(axis=1)
    return [float(v) for v in np.percentile(draws, [2.5, 97.5])]


def summarize_candidates(rows):
    """Image is the unit of selection and uncertainty, never a candidate."""
    frame = pd.DataFrame(rows)
    results = []
    per_image = []
    for (model, cohort), group in frame.groupby(["model", "cohort"], sort=True):
        for image_id, g in group.groupby("global_index", sort=True):
            g = g.sort_values("candidate_index")
            actual = g["actual_d"].to_numpy()
            oracle = int(np.argmin(actual))
            row = {"model": model, "cohort": cohort, "global_index": int(image_id),
                   "oracle_d": float(actual[oracle]), "oracle_index": oracle}
            for method in METHODS:
                score = g[method].to_numpy()
                choice = int(np.argmin(score))
                rank = spearmanr(score, actual).statistic
                row[f"{method}_d"] = float(actual[choice])
                row[f"{method}_regret"] = float(actual[choice] - actual[oracle])
                row[f"{method}_oracle_agree"] = int(choice == oracle)
                row[f"{method}_spearman"] = float(rank) if np.isfinite(rank) else None
            per_image.append(row)
    image_df = pd.DataFrame(per_image)
    for (model, cohort), g in image_df.groupby(["model", "cohort"], sort=True):
        record = {"model": model, "cohort": cohort, "n_images": len(g),
                  "oracle_mean_d": float(g.oracle_d.mean())}
        for method in METHODS:
            record[method] = {
                "mean_d": float(g[f"{method}_d"].mean()),
                "mean_regret": float(g[f"{method}_regret"].mean()),
                "oracle_agreement": float(g[f"{method}_oracle_agree"].mean()),
                "mean_spearman": float(g[f"{method}_spearman"].mean()),
            }
        results.append(record)
    return image_df, results


def gate_stability(image_df, runtime):
    """Frozen 64-image G1 test; select only one signed variant on DeiT."""
    a = image_df.query("model == 'deit_small' and cohort == 'stability'")
    b = image_df.query("model == 'vit_base' and cohort == 'stability'")
    if len(a) != 64 or len(b) != 64:
        return {"status": "INCOMPLETE", "reason": "64 per model required"}
    signed = min(SIGNED, key=lambda m: a[f"{m}_d"].mean())
    scalar = min(SCALAR, key=lambda m: a[f"{m}_d"].mean())
    contrast_a = a[f"{scalar}_d"].to_numpy() - a[f"{signed}_d"].to_numpy()
    # ViT uses its own best scalar but the signed variant is held fixed.
    scalar_b = min(SCALAR, key=lambda m: b[f"{m}_d"].mean())
    contrast_b = b[f"{scalar_b}_d"].to_numpy() - b[f"{signed}_d"].to_numpy()
    mean_a = float(contrast_a.mean())
    mean_b = float(contrast_b.mean())
    ci_a, ci_b = paired_interval(contrast_a), paired_interval(contrast_b)
    relative_a = mean_a / max(float(a[f"{scalar}_d"].mean()), 1e-12)
    overhead_ok = runtime_smoke_gate(runtime)["status"] == "GO"
    passed = mean_a >= 1e-6 and relative_a >= .1 and ci_a[0] > 0 and ci_b[0] > 0 and mean_b > 0 and overhead_ok
    return {"status": "GO_PROVISIONAL" if passed else "KILL", "selected_signed": signed,
            "deit_best_scalar": scalar, "vit_best_scalar": scalar_b,
            "deit_mean_gain": mean_a, "deit_relative_gain": float(relative_a), "deit_ci95": ci_a,
            "vit_mean_gain": mean_b, "vit_ci95": ci_b, "overhead_ok": overhead_ok}


def runtime_smoke_gate(runtime):
    """The frozen statistic is the pooled median of 2 x 50 runs *per model*."""
    by_model = {}
    for model in ("deit_small", "vit_base"):
        records = [r for r in runtime if r["model"] == model]
        if len(records) != 2 or any("baseline_times_ms" not in r for r in records):
            return {"status": "INCOMPLETE", "reason": "two raw 50-run timing series per model required"}
        base = np.concatenate([r["baseline_times_ms"] for r in records])
        route = np.concatenate([r["capture_proxy_times_ms"] for r in records])
        if len(base) != 100 or len(route) != 100:
            return {"status": "INCOMPLETE", "reason": "100 timings per arm required"}
        base_median, route_median = float(np.median(base)), float(np.median(route))
        increment = route_median / base_median - 1
        by_model[model] = {"uncaptured_prefix_median_ms": base_median,
                           "capture_proxy_median_ms": route_median,
                           "increment_fraction": increment,
                           "extra_peak_mib_max": max(r["extra_peak_mib"] for r in records),
                           "fused_attention": all(r["fused_attention"] for r in records),
                           "one_qkv_hook_call": all(r["hook_calls"] == 1 for r in records)}
    passed = all(r["increment_fraction"] <= .2 and r["extra_peak_mib_max"] <= 128
                 and r["fused_attention"] and r["one_qkv_hook_call"]
                 for r in by_model.values())
    return {"status": "GO" if passed else "KILL", "by_model": by_model}


def gate_pilot(image_df, provisional):
    if provisional.get("status") != "GO_PROVISIONAL":
        return {"status": "KILL", "reason": "64-image or runtime gate failed"}
    signed = provisional["selected_signed"]
    details = {}
    for model, baseline in (("deit_small", provisional["deit_best_scalar"]),
                            ("vit_base", provisional["vit_best_scalar"])):
        g = image_df.query("model == @model and cohort == 'pilot'")
        if len(g) != 128:
            return {"status": "INCOMPLETE", "reason": "128 per model required"}
        diff = g[f"{baseline}_d"].to_numpy() - g[f"{signed}_d"].to_numpy()
        details[model] = {"mean_gain": float(diff.mean()), "ci95": paired_interval(diff)}
    return {"status": "GO" if all(v["mean_gain"] > 0 for v in details.values()) else "KILL",
            "selected_signed": signed, "pilot": details}


def benchmark_capture(model, model_key, depth, x, candidates):
    """Common candidate pool is precomputed and excluded from both timing arms."""
    # Original-state masses are all one.  State construction is already part of
    # the shared candidate-matching path, so do not count it a second time here.
    masses = torch.ones(196, device=x.device, dtype=x.dtype)
    def no_capture():
        return prefix(model, model_key, depth, x)

    def hook_only():
        return captured_prefix(model, depth, x)

    def with_capture():
        h, signal = captured_prefix(model, depth, x)
        proxy = candidate_proxies(signal, candidates, masses)
        choice = choose_minimum(proxy["raw_norm"])
        return h, signal, choice

    def measure(fn):
        for _ in range(20):
            result = fn()
            sync()
            del result
        sync()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            baseline_alloc = torch.cuda.memory_allocated()
        else:
            baseline_alloc = 0
        times = []
        observations = []
        for _ in range(50):
            sync()
            start = time.perf_counter()
            result = fn()
            sync()
            times.append(1000 * (time.perf_counter() - start))
            if isinstance(result, tuple):
                observations.append((result[1].hook_calls, result[1].fused_attention))
            del result
        peak = torch.cuda.max_memory_allocated() - baseline_alloc if torch.cuda.is_available() else 0
        return float(np.median(times)), max(peak, 0) / 2 ** 20, observations, times

    base_ms, base_mib, _, base_times = measure(no_capture)
    hook_ms, hook_mib, _, hook_times = measure(hook_only)
    route_ms, route_mib, observed, route_times = measure(with_capture)
    return {"baseline_prefix_median_ms": base_ms, "capture_proxy_median_ms": route_ms,
            "hooked_prefix_median_ms": hook_ms,
            "post_prefix_proxy_median_ms": max(route_ms - hook_ms, 0),
            "overhead_fraction": route_ms / max(base_ms, 1e-9) - 1,
            "baseline_incremental_peak_mib": base_mib,
            "hook_incremental_peak_mib": hook_mib,
            "capture_incremental_peak_mib": route_mib,
            "extra_peak_mib": max(route_mib - base_mib, 0),
            "hook_calls": min(v[0] for v in observed),
            "fused_attention": all(v[1] for v in observed),
            "baseline_times_ms": base_times, "hook_times_ms": hook_times,
            "capture_proxy_times_ms": route_times}


def evaluate_image(model, model_key, depth, x, record, batch_size, benchmark):
    with torch.inference_mode():
        sync()
        start = time.perf_counter()
        hidden, signal = captured_prefix(model, depth, x)
        state = initial_state(hidden)
        seed = SEED_CANDIDATE + record["global_index"] + 1009 * 196 + (0 if model_key == "deit_small" else 1000003)
        candidates = candidate_pool(state, seed)
        proxies = candidate_proxies(signal, candidates, state.multiplicities)
        scores = score_array(candidates, proxies)
        sync()
        capture_proxy_ms = 1000 * (time.perf_counter() - start)
        runtime = benchmark_capture(model, model_key, depth, x, candidates) if benchmark else None
        clean = model(x)
        full_h, full_m = state_batch([state])
        no_merge = forward_suffix_batch(model, model_key, depth, full_h, full_m)
        parity = float((clean - no_merge).abs().max())
        if parity >= 5e-4:
            raise RuntimeError(f"No-merge parity failed: {model_key} {parity}")
        sync()
        teacher_start = time.perf_counter()
        teacher_calls = 0
        actual = []
        for first in range(0, len(candidates), batch_size):
            chunk = candidates[first:first + batch_size]
            alternatives = [apply_action(state, c["source"], c["destination"]) for c in chunk]
            h, m = state_batch(alternatives)
            logits = forward_suffix_batch(model, model_key, depth, h, m)
            actual.extend(normalized_distortion(logits, clean).detach().cpu().tolist())
            teacher_calls += 1
        sync()
        teacher_ms = 1000 * (time.perf_counter() - teacher_start)
        rows = []
        for index, candidate in enumerate(candidates):
            rows.append({"model": model_key, "cohort": record["cohort"],
                         "global_index": record["global_index"], "candidate_index": index,
                         "source": candidate["source"], "destination": candidate["destination"],
                         "kind": candidate["kind"], "actual_d": actual[index],
                         "feature_distance": candidate["feature_distance"],
                         **{key: float(value[index]) for key, value in scores.items()}})
        telemetry = {"model": model_key, "cohort": record["cohort"], "global_index": record["global_index"],
                     "candidate_seed": seed, "parity_max_abs": parity,
                     "capture_proxy_pool_ms": capture_proxy_ms, "teacher_suffix_ms": teacher_ms,
                     "teacher_suffix_calls": teacher_calls, "hook_calls": signal.hook_calls,
                     "fused_attention": signal.fused_attention}
        if runtime is not None:
            telemetry.update(runtime)
        return rows, telemetry


def run_phase(args):
    root = Path(args.output_dir).resolve()
    out = root / args.phase
    out.mkdir(parents=True, exist_ok=False)
    records, paths = calibration_records()
    cohort = "stability" if args.phase == "smoke" else args.phase
    limit = 2 if args.phase == "smoke" else (64 if args.phase == "stability" else 128)
    selected = [r for r in records if r["cohort"] == cohort][:limit]
    image_bytes(selected)
    pd.DataFrame([{k: portable_parquet_identity(v) if k == "parquet_path" else v
                   for k, v in r.items() if k != "image_bytes"} for r in selected]).to_csv(out / "source_image_ids.csv", index=False)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    manifest = {"protocol_commit": PROTOCOL_COMMIT, "phase": args.phase,
                "models": {}, "calibration_seed": 9101, "split_seed": 64011,
                "candidate_seed_base": SEED_CANDIDATE, "bootstrap_seed": BOOTSTRAP_SEED,
                "candidate_count": 32, "candidate_batch_size": args.batch_size,
                "cohort": cohort, "n_images_per_model": len(selected),
                "source_parquets": [{"path": portable_parquet_identity(p), "size_bytes": os.path.getsize(p)} for p in paths],
                "torch": torch.__version__, "timm": timm.__version__, "scipy": scipy.__version__,
                "python": platform.python_version(), "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None,
                "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()}
    all_rows, all_telemetry = [], []
    started = time.perf_counter()
    try:
        for model_key, depth, _ in MODEL_CONFIG:
            model, transform, meta = load_model_and_transform(model_key, device)
            model.eval()
            manifest["models"][model_key] = {**meta, "intervention_depth": depth,
                                               "weight_state_sha256": model_weight_hash(model)}
            for ix, record in enumerate(selected):
                x = transform(Image.open(io.BytesIO(record["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
                rows, telemetry = evaluate_image(model, model_key, depth, x, record, args.batch_size,
                                                 benchmark=args.phase == "smoke")
                all_rows.extend(rows)
                all_telemetry.append(telemetry)
                if (ix + 1) % 8 == 0 or args.phase == "smoke":
                    print(f"{args.phase} {model_key}: {ix + 1}/{len(selected)}", flush=True)
                    pd.DataFrame(all_rows).to_csv(out / "candidates.partial.csv", index=False)
            del model
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    finally:
        manifest["wall_seconds"] = time.perf_counter() - started
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf8")
        if all_rows:
            pd.DataFrame(all_rows).to_csv(out / "candidates.partial.csv", index=False)
        if all_telemetry:
            pd.DataFrame(all_telemetry).to_csv(out / "telemetry.csv", index=False)
    pd.DataFrame(all_rows).to_csv(out / "candidates.csv", index=False)
    image_df, summary = summarize_candidates(all_rows)
    image_df.to_csv(out / "per_image.csv", index=False)
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf8")
    if args.phase == "smoke":
        runtime = all_telemetry
        smoke = {**runtime_smoke_gate(runtime), "runtime": runtime}
        (out / "gate_smoke.json").write_text(json.dumps(smoke, indent=2), encoding="utf8")
        print(json.dumps(smoke, indent=2), flush=True)
    else:
        print(json.dumps(summary, indent=2), flush=True)


def summarize_gate(root):
    root = Path(root)
    smoke = json.loads((root / "smoke" / "gate_smoke.json").read_text(encoding="utf8"))
    stability = pd.read_csv(root / "stability" / "per_image.csv")
    provisional = gate_stability(stability, smoke["runtime"])
    if smoke["status"] != "GO":
        provisional["status"] = "KILL"
        provisional["reason"] = "smoke runtime failed"
    result = {"G0": "GO", "G1_stability": provisional, "G1": "KILL"}
    if provisional["status"] == "GO_PROVISIONAL" and (root / "pilot" / "per_image.csv").exists():
        pilot = pd.read_csv(root / "pilot" / "per_image.csv")
        result["G1_pilot"] = gate_pilot(pilot, provisional)
        result["G1"] = result["G1_pilot"]["status"]
    elif provisional["status"] == "GO_PROVISIONAL":
        result["G1"] = "AWAIT_PILOT"
    (root / "gate_decisions.json").write_text(json.dumps(result, indent=2), encoding="utf8")
    candidates = pd.read_csv(root / "stability" / "candidates.csv")
    diagnostics = {}
    for model, g in stability.groupby("model", sort=True):
        signed = "raw_norm" if model == "deit_small" else "projected_norm"
        gain = g.cosine_d.to_numpy() - g[f"{signed}_d"].to_numpy()
        ordered = np.argsort(gain)
        correlations = []
        for _, image in candidates[candidates.model == model].groupby("global_index"):
            correlations.append({key: float(spearmanr(image.raw_norm, image[key]).statistic)
                                 for key in ("cosine", "attention_importance", "attention_value_distance", "feature_distance")})
        diagnostics[model] = {
            "diagnostic_signed_variant": signed,
            "cosine_minus_signed_mean_d": float(gain.mean()),
            "cosine_minus_signed_ci95": paired_interval(gain),
            "signed_better_images": int(np.sum(gain > 0)),
            "cosine_better_images": int(np.sum(gain < 0)),
            "median_gain": float(np.median(gain)),
            "largest_signed_failures": [
                {"global_index": int(g.iloc[i].global_index), "cosine_minus_signed_d": float(gain[i])}
                for i in ordered[:3]],
            "largest_signed_wins": [
                {"global_index": int(g.iloc[i].global_index), "cosine_minus_signed_d": float(gain[i])}
                for i in ordered[-3:][::-1]],
            "mean_candidate_spearman_raw_vs_features": {
                key: float(np.mean([row[key] for row in correlations])) for key in correlations[0]},
        }
        examples = []
        for position in (int(ordered[0]), int(ordered[-1])):
            image_id = int(g.iloc[position].global_index)
            image = candidates[(candidates.model == model) & (candidates.global_index == image_id)].sort_values("candidate_index")
            picks = {}
            for method in ("cosine", "raw_norm", "projected_norm", "actual_d"):
                c = image.loc[image[method].idxmin()]
                picks[method] = {"candidate_index": int(c.candidate_index),
                                 "source": int(c.source), "destination": int(c.destination),
                                 "actual_d": float(c.actual_d), "cosine_cost": float(c.cosine),
                                 "raw_norm": float(c.raw_norm),
                                 "projected_norm": float(c.projected_norm),
                                 "attention_importance": float(c.attention_importance)}
            examples.append({"global_index": image_id, "cosine_minus_signed_d": float(gain[position]),
                             "picks": picks})
        diagnostics[model]["inspected_examples"] = examples
    (root / "stability" / "diagnostics.json").write_text(json.dumps(diagnostics, indent=2), encoding="utf8")
    print(json.dumps(result, indent=2), flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=["smoke", "stability", "pilot", "summarize"], required=True)
    parser.add_argument("--output-dir", default="outputs/signed_value_merging")
    parser.add_argument("--batch-size", type=int, default=8)
    args = parser.parse_args()
    root = Path(args.output_dir).resolve()
    if args.phase == "summarize":
        summarize_gate(root)
        return
    if args.phase != "smoke":
        smoke = json.loads((root / "smoke" / "gate_smoke.json").read_text(encoding="utf8"))
        if smoke["status"] != "GO":
            raise RuntimeError("Smoke overhead gate failed; no full G1 evaluation permitted")
    if args.phase == "pilot":
        stability = pd.read_csv(root / "stability" / "per_image.csv")
        smoke = json.loads((root / "smoke" / "gate_smoke.json").read_text(encoding="utf8"))
        if gate_stability(stability, smoke["runtime"])["status"] != "GO_PROVISIONAL":
            raise RuntimeError("64-image G1 gate failed; pilot replication prohibited")
    run_phase(args)
    if args.phase == "stability":
        summarize_gate(root)
    if args.phase == "pilot":
        summarize_gate(root)


if __name__ == "__main__":
    main()
