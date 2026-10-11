"""Run the frozen PR #4 merge-action diagnostic on calibration-side images."""

import argparse
import hashlib
import io
import json
import platform
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import spearmanr
import torch

from patch_fungibility.counterfactual_merge import (
    baseline_state, candidate_pool, initial_state, normalized_distortion,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.merge_interaction_diagnostic import (
    SetEvaluator, greedy_selection, interaction_measurements, paired_bootstrap,
    pair_categories, ranked_selection, set_residual,
)
from scripts.run_counterfactual_merge_pilot import (
    MODEL_CONFIG, SEED_CANDIDATE, calibration_records, image_bytes,
    model_weight_hash, prefix,
)
from scripts.train_counterfactual_merge_scorer import PairScorer, score_candidates, score_rollout


def candidate_seed(global_index, count, model_offset):
    return SEED_CANDIDATE + global_index + 1009 * count + model_offset


def score_summary(scores, costs):
    scores, costs = np.asarray(scores), np.asarray(costs)
    corr = spearmanr(scores, costs).statistic
    return {"spearman": float(corr) if np.isfinite(corr) else np.nan,
            "top1_agreement": int(np.argmin(scores) == np.argmin(costs)),
            "regret": float(costs[np.argmin(scores)] - costs.min())}


def first_round(evaluator, candidates, student_scores, model_key, cohort, global_index):
    one_costs = evaluator.distortions([(i,) for i in range(len(candidates))])
    cosine_scores = -np.array([c["cosine"] for c in candidates])
    policies = {
        "cosine": ranked_selection(cosine_scores, candidates),
        "student": ranked_selection(student_scores, candidates),
        "independent_oracle": ranked_selection(one_costs, candidates),
        "conditional_greedy_oracle": greedy_selection(evaluator, candidates),
    }
    candidate_rows = [{"model": model_key, "cohort": cohort, "global_index": global_index,
                       "candidate_index": i, "source": c["source"], "destination": c["destination"],
                       "cosine": c["cosine"], "student_score": float(student_scores[i]),
                       "single_action_distortion": float(one_costs[i])}
                      for i, c in enumerate(candidates)]
    curve, residuals = [], []
    for method, order in policies.items():
        for k in (1, 2, 4, 8, 16):
            size = min(k, len(order))
            if not size:
                continue
            key = tuple(order[:size])
            actual = float(evaluator.distortions([key])[0])
            curve.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                          "method": method, "k": k, "actual_k": size, "distortion": actual,
                          "selected_indices": ";".join(map(str, order[:size]))})
            residuals.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                              "method": method, "k": k, **set_residual(evaluator, key)})
    categories = pair_categories(candidates, one_costs)
    pairs = []
    for category, pair in categories.items():
        if pair is None:
            pairs.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                          "category": category, "available": 0})
            continue
        pairs.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                      "category": category, "available": 1, "a": pair[0], "b": pair[1],
                      "same_destination": int(candidates[pair[0]]["destination"] == candidates[pair[1]]["destination"]),
                      **interaction_measurements(evaluator, pair)})
    rank = []
    for method, scores in (("cosine", cosine_scores), ("student", student_scores)):
        rank.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                     "method": method, "state_policy": "uncompressed", "count": 196,
                     **score_summary(scores, one_costs)})
    return curve, residuals, pairs, rank, policies, candidate_rows


def state_diagnostic(model, model_key, depth, full, clean, global_index,
                     scorer, mean, std, device, batch_size, offset):
    rows = []
    for count in (180, 164, 147, 98):
        for policy in ("tome", "student"):
            if policy == "tome":
                state = baseline_state(full, count)
            else:
                state = score_rollout(full, count, global_index, "counterfactual_pair",
                                      {"counterfactual_pair": scorer}, mean, std, device)
            assert state.count == count and abs(float(state.multiplicities.sum()) - 196) < 1e-3
            candidates = candidate_pool(state, candidate_seed(global_index, count, offset))
            evaluator = SetEvaluator(model, model_key, depth, state, candidates, clean, batch_size)
            costs = evaluator.distortions([(i,) for i in range(32)])
            scores = {
                "cosine": -np.array([c["cosine"] for c in candidates]),
                "student": score_candidates("counterfactual_pair", {"counterfactual_pair": scorer},
                                            state, candidates, mean, std, device),
                "oracle": costs,
            }
            for method, values in scores.items():
                rows.append({"model": model_key, "global_index": global_index,
                             "state_policy": policy, "count": count, "method": method,
                             **score_summary(values, costs),
                             "teacher_seconds_for_32": evaluator.teacher_seconds,
                             "teacher_sets_for_32": evaluator.teacher_sets})
    return rows


def write_csv(rows, path):
    if rows:
        pd.DataFrame(rows).to_csv(path, index=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("first", "state"), default="first")
    parser.add_argument("--cohort", choices=("stability", "pilot"), default="stability")
    parser.add_argument("--limit", type=int, default=0, help="Small correctness/runtime pilot only")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--candidate-schedule", choices=("teacher", "rollout"), default="teacher",
                        help="PR #4 training-label pool or deployed rollout pool; first round only")
    parser.add_argument("--student-dir", default="outputs/counterfactual_merge_student")
    parser.add_argument("--output-dir", default="outputs/merge_interaction_diagnostic")
    args = parser.parse_args()
    if args.limit < 0 or args.batch_size < 1:
        raise ValueError("Invalid limit or batch size")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"{args.phase}_{args.cohort}" + (f"_smoke{args.limit}" if args.limit else "")
    if args.candidate_schedule == "rollout":
        if args.phase != "first":
            raise ValueError("Rollout-pool sensitivity is first-round only")
        suffix += "_rollout_pool"
    records, paths = calibration_records()
    chosen = [r for r in records if r["cohort"] == args.cohort]
    if args.limit:
        chosen = chosen[:args.limit]
    if not args.limit and len(chosen) != (64 if args.cohort == "stability" else 128):
        raise RuntimeError("Unexpected cohort size")
    chosen = image_bytes(chosen)
    student_dir = Path(args.student_dir)
    student_manifest = json.loads((student_dir / "manifest.json").read_text(encoding="utf8"))
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    begin = time.perf_counter()
    curve, residuals, pairs, ranks, states, diagnostics, candidate_rows = [], [], [], [], [], [], []
    manifest = {"protocol_commit": "0f074b4", "phase": args.phase, "cohort": args.cohort,
                "candidate_schedule": args.candidate_schedule,
                "limit": args.limit, "batch_size": args.batch_size, "global_image_ids": [r["global_index"] for r in chosen],
                "source_parquet_files": [str(Path(p).name) for p in paths],
                "device": str(device), "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None,
                "torch": torch.__version__, "python": platform.python_version(),
                "model_hashes": {}, "student_checkpoint_sha256": {},
                "teacher_seconds": 0.0, "teacher_sets": 0,
                "teacher_batches": 0, "max_parity_error": 0.0}
    for model_key, depth, offset in MODEL_CONFIG[:2]:
        model, transform, meta = load_model_and_transform(model_key, device)
        manifest["model_hashes"][model_key] = model_weight_hash(model)
        mean = np.asarray(student_manifest["models"][model_key]["feature_mean"], dtype=np.float32)
        std = np.asarray(student_manifest["models"][model_key]["feature_std"], dtype=np.float32)
        scorer = PairScorer(meta["embed_dim"])
        checkpoint = student_dir / f"{model_key}_counterfactual_pair.pt"
        manifest["student_checkpoint_sha256"][model_key] = hashlib.sha256(checkpoint.read_bytes()).hexdigest()
        scorer.load_state_dict(torch.load(checkpoint,
                                          map_location="cpu", weights_only=True))
        scorer.to(device).eval()
        with torch.inference_mode():
            for n, record in enumerate(chosen):
                x = transform(Image.open(io.BytesIO(record["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
                full = initial_state(prefix(model, model_key, depth, x))
                clean = model(x)
                if args.phase == "first":
                    pool_offset = offset if args.candidate_schedule == "teacher" else 0
                    candidates = candidate_pool(full, candidate_seed(record["global_index"], 196, pool_offset))
                    evaluator = SetEvaluator(model, model_key, depth, full, candidates, clean, args.batch_size)
                    parity = float(np.max(np.abs(evaluator.evaluate([()])[0] - clean[0].detach().cpu().numpy())))
                    manifest["max_parity_error"] = max(manifest["max_parity_error"], parity)
                    if parity >= 5e-4:
                        raise RuntimeError(f"No-merge parity failure: {model_key} {parity}")
                    student_scores = score_candidates("counterfactual_pair", {"counterfactual_pair": scorer},
                                                      full, candidates, mean, std, device)
                    c, res, p, rank, policy, candidate = first_round(evaluator, candidates, student_scores,
                                                                      model_key, args.cohort, record["global_index"])
                    curve.extend(c); residuals.extend(res); pairs.extend(p); ranks.extend(rank)
                    candidate_rows.extend(candidate)
                    manifest["teacher_seconds"] += evaluator.teacher_seconds
                    manifest["teacher_sets"] += evaluator.teacher_sets
                    manifest["teacher_batches"] += evaluator.teacher_batches
                    diagnostics.append({"model": model_key, "global_index": record["global_index"],
                                        "max_feasible": len(policy["conditional_greedy_oracle"]),
                                        "teacher_sets": evaluator.teacher_sets,
                                        "teacher_seconds": evaluator.teacher_seconds})
                else:
                    new_states = state_diagnostic(model, model_key, depth, full, clean,
                                                  record["global_index"], scorer, mean, std,
                                                  device, args.batch_size, offset)
                    states.extend(new_states)
                    manifest["teacher_seconds"] += sum(row["teacher_seconds_for_32"] for row in new_states
                                                       if row["method"] == "oracle")
                    manifest["teacher_sets"] += sum(row["teacher_sets_for_32"] for row in new_states
                                                    if row["method"] == "oracle")
                if (n + 1) % 8 == 0 or n + 1 == len(chosen):
                    print(f"{model_key} {args.phase} {n + 1}/{len(chosen)} elapsed={time.perf_counter()-begin:.1f}s", flush=True)
        del model, scorer
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    manifest["elapsed_seconds"] = time.perf_counter() - begin
    manifest["peak_gpu_mib"] = float(torch.cuda.max_memory_allocated() / 2 ** 20) if torch.cuda.is_available() else 0.0
    write_csv(curve, out / f"curve_{suffix}.csv")
    write_csv(residuals, out / f"residuals_{suffix}.csv")
    write_csv(pairs, out / f"pairs_{suffix}.csv")
    write_csv(ranks, out / f"rank_{suffix}.csv")
    write_csv(candidate_rows, out / f"candidates_{suffix}.csv")
    write_csv(states, out / f"states_{suffix}.csv")
    write_csv(diagnostics, out / f"runtime_{suffix}.csv")
    (out / f"manifest_{suffix}.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf8")
    print(json.dumps({"output": str(out), "suffix": suffix, "elapsed_seconds": manifest["elapsed_seconds"],
                      "teacher_sets": manifest["teacher_sets"], "peak_gpu_mib": manifest["peak_gpu_mib"]}), flush=True)


if __name__ == "__main__":
    main()
