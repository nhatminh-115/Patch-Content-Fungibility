"""Sequential functional set-aware merge feasibility experiments."""

import argparse
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
    baseline_state, candidate_pool, forward_suffix_batch, initial_state,
    normalized_distortion, state_batch,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.functional_set_merge import (
    effects_from_logits, gaussian_projection, maximum_distinct_destination_matching, select_greedy,
    set_components,
)
from patch_fungibility.merge_interaction_diagnostic import (
    SetEvaluator, greedy_selection, ranked_selection,
)
from scripts.run_counterfactual_merge_pilot import (
    MODEL_CONFIG, SEED_CANDIDATE, calibration_records, image_bytes,
    model_weight_hash, prefix,
)


def sync():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def select_phase_a(evaluator, candidates, clean):
    current = evaluator.evaluate([()])[0]
    singles = np.stack(evaluator.evaluate([(i,) for i in range(len(candidates))]))
    clean_np = clean[0].detach().cpu().numpy()
    error, deltas, denominator = effects_from_logits(current, singles, clean_np)
    single_costs = evaluator.distortions([(i,) for i in range(len(candidates))])
    cosine = -np.asarray([c["cosine"] for c in candidates])
    penalty = float(np.median(single_costs))
    method_orders = {
        "cosine": ranked_selection(cosine, candidates),
        "independent": ranked_selection(single_costs, candidates),
        "conditional": greedy_selection(evaluator, candidates),
    }
    selector_times = {}
    for name, costs, load_penalty, hard in (
        ("additive", None, 0.0, False),
        ("independent_load", single_costs, penalty, False),
        ("additive_load", None, penalty, False),
        ("additive_distinct", None, 0.0, True),
    ):
        sync()
        tic = time.perf_counter()
        method_orders[name] = select_greedy(candidates, error, deltas, denominator,
                                            single_costs=costs, destination_penalty=load_penalty,
                                            distinct_destinations=hard)
        sync()
        selector_times[name] = time.perf_counter() - tic
    max_distinct = maximum_distinct_destination_matching(candidates)
    return method_orders, selector_times, single_costs, error, deltas, denominator, penalty, max_distinct


def evaluate_phase_a(model, model_key, depth, full, clean, global_index, cohort, batch_size):
    offset = 0 if model_key == "deit_small" else 1000003
    candidates = candidate_pool(full, SEED_CANDIDATE + global_index + 1009 * 196 + offset)
    evaluator = SetEvaluator(model, model_key, depth, full, candidates, clean, batch_size)
    parity = float(np.max(np.abs(evaluator.evaluate([()])[0] - clean[0].detach().cpu().numpy())))
    if parity >= 5e-4:
        raise RuntimeError(f"No-merge parity failure {model_key}: {parity}")
    orders, selector_times, costs, error, deltas, denom, penalty, max_distinct = select_phase_a(
        evaluator, candidates, clean)
    rows = []
    for method, order in orders.items():
        for requested_k in range(1, 17):
            k = min(requested_k, len(order))
            if not k:
                continue
            indices = order[:k]
            actual = float(evaluator.distortions([indices])[0])
            components = set_components(error, deltas, indices, costs, denom, actual)
            loads = {}
            for i in indices:
                destination = candidates[i]["destination"]
                loads[destination] = loads.get(destination, 0) + 1
            rows.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                         "method": method, "k": requested_k, "actual_k": k,
                         "distortion": actual, "selected_indices": ";".join(map(str, indices)),
                         "destination_collisions": sum(load - 1 for load in loads.values()),
                         "max_distinct_destination_matching": max_distinct,
                         "destination_penalty": penalty if method.endswith("load") else 0.0,
                         "selector_seconds": selector_times.get(method, 0.0),
                         **components})
    stats = {"model": model_key, "cohort": cohort, "global_index": global_index,
             "parity_max_abs": parity, "max_distinct_destination_matching": max_distinct,
             "teacher_sets": evaluator.teacher_sets, "teacher_batches": evaluator.teacher_batches,
             "teacher_seconds": evaluator.teacher_seconds, "penalty": penalty,
             **{f"selector_seconds_{name}": value for name, value in selector_times.items()}}
    return rows, stats


def projected_ranking_agreement(candidates, error, deltas, projected_error, projected_deltas,
                                denominator, penalty, full_order):
    full_inner = deltas @ deltas.T
    compressed_inner = projected_deltas @ projected_deltas.T
    pair_indices = [(i, j) for i in range(len(candidates)) for j in range(i + 1, len(candidates))
                    if candidates[i]["source"] != candidates[j]["source"]]
    full_pairs = np.array([full_inner[i, j] for i, j in pair_indices])
    compressed_pairs = np.array([compressed_inner[i, j] for i, j in pair_indices])
    pair_spearman = float(spearmanr(full_pairs, compressed_pairs).statistic)
    rank_agreements = []
    selected = []
    for _ in range(min(16, len(full_order))):
        used_sources = {candidates[i]["source"] for i in selected}
        eligible = [i for i, c in enumerate(candidates) if c["source"] not in used_sources]
        used_destinations = [candidates[i]["destination"] for i in selected]
        true_vector = error + deltas[selected].sum(axis=0) if selected else error
        projected_vector = projected_error + projected_deltas[selected].sum(axis=0) if selected else projected_error
        full_scores = [np.dot(true_vector + deltas[i], true_vector + deltas[i]) / denominator +
                       penalty * used_destinations.count(candidates[i]["destination"]) for i in eligible]
        projected_scores = [np.dot(projected_vector + projected_deltas[i],
                                   projected_vector + projected_deltas[i]) / denominator +
                            penalty * used_destinations.count(candidates[i]["destination"]) for i in eligible]
        if len(eligible) >= 3:
            rank_agreements.append(float(spearmanr(full_scores, projected_scores).statistic))
        selected.append(full_order[len(selected)])
    return pair_spearman, float(np.nanmean(rank_agreements))


def evaluate_phase_b(model, model_key, depth, full, clean, global_index, cohort, batch_size,
                     projections, projection_build_seconds):
    offset = 0 if model_key == "deit_small" else 1000003
    candidates = candidate_pool(full, SEED_CANDIDATE + global_index + 1009 * 196 + offset)
    evaluator = SetEvaluator(model, model_key, depth, full, candidates, clean, batch_size)
    current = evaluator.evaluate([()])[0]
    singles = np.stack(evaluator.evaluate([(i,) for i in range(len(candidates))]))
    error, deltas, denominator = effects_from_logits(current, singles, clean[0].detach().cpu().numpy())
    costs = evaluator.distortions([(i,) for i in range(len(candidates))])
    penalty = float(np.median(costs))
    full_order = select_greedy(candidates, error, deltas, denominator,
                               destination_penalty=penalty)
    rows = []
    for dimension, matrix in projections.items():
        tic = time.perf_counter()
        projected_error = error @ matrix
        projected_deltas = deltas @ matrix
        projection_seconds = time.perf_counter() - tic
        tic = time.perf_counter()
        order = select_greedy(candidates, projected_error, projected_deltas, denominator,
                              destination_penalty=penalty)
        selector_seconds = time.perf_counter() - tic
        pair_spearman, set_rank_spearman = projected_ranking_agreement(
            candidates, error, deltas, projected_error, projected_deltas,
            denominator, penalty, full_order)
        for k in (1, 2, 4, 8, 16):
            indices = order[:k]
            actual = float(evaluator.distortions([indices])[0])
            components = set_components(error, deltas, indices, costs, denominator, actual)
            rows.append({"model": model_key, "cohort": cohort, "global_index": global_index,
                         "dimension": dimension, "k": k, "actual_k": len(indices),
                         "distortion": actual, "selected_indices": ";".join(map(str, indices)),
                         "full_effect_set_overlap": len(set(indices) & set(full_order[:k])),
                         "pair_inner_product_spearman": pair_spearman,
                         "set_damage_rank_spearman": set_rank_spearman,
                         "projection_apply_seconds": projection_seconds,
                         "projection_build_seconds": projection_build_seconds[dimension],
                         "selector_seconds": selector_seconds,
                         **components})
    parity = float(np.max(np.abs(current - clean[0].detach().cpu().numpy())))
    if parity >= 5e-4:
        raise RuntimeError(f"No-merge parity failure {model_key}: {parity}")
    stats = {"model": model_key, "cohort": cohort, "global_index": global_index,
             "parity_max_abs": parity, "teacher_sets": evaluator.teacher_sets,
             "teacher_seconds": evaluator.teacher_seconds}
    return rows, stats


def evaluate_tome_control(model, model_key, depth, full, clean, global_index, cohort, batch_size):
    offset = 0 if model_key == "deit_small" else 1000003
    candidates = candidate_pool(full, SEED_CANDIDATE + global_index + 1009 * 196 + offset)
    indices = [i for i, c in enumerate(candidates) if c["kind"] == "tome_proposal"]
    if len(indices) != 16:
        raise RuntimeError("Expected 16 ToMe proposal edges in the fixed pool")
    evaluator = SetEvaluator(model, model_key, depth, full, candidates, clean, batch_size)
    action_logits = evaluator.evaluate([indices])[0]
    state = baseline_state(full, 180)
    hidden, mass = state_batch([state])
    with torch.inference_mode():
        baseline_logits = forward_suffix_batch(model, model_key, depth, hidden, mass)
    difference = float(np.max(np.abs(action_logits - baseline_logits[0].detach().cpu().numpy())))
    if difference >= 5e-4:
        raise RuntimeError(f"ToMe proposal parity failed {model_key}: {difference}")
    result = {"model": model_key, "cohort": cohort, "global_index": global_index,
              "count": 180, "tome_distortion": float(normalized_distortion(baseline_logits, clean)[0]),
              "proposal_parity_max_abs": difference,
              "teacher_sets": evaluator.teacher_sets, "teacher_seconds": evaluator.teacher_seconds}
    return [result], result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", choices=("a", "b", "tome"), default="a")
    parser.add_argument("--cohort", choices=("stability", "pilot"), default="stability")
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--dimensions", default="16,32,64,128", help="Phase B dimensions")
    parser.add_argument("--output-dir", default="outputs/functional_set_merge")
    args = parser.parse_args()
    if args.limit < 0 or args.batch_size < 1:
        raise ValueError("Invalid limit or batch size")
    dimensions = tuple(int(x) for x in args.dimensions.split(","))
    if args.phase == "b":
        gate = json.loads((Path(args.output_dir) / "gates.json").read_text(encoding="utf8"))
        if gate["A"] != "GO":
            raise RuntimeError("Frozen Gate A has not passed")
        if not dimensions or any(x not in (16, 32, 64, 128) for x in dimensions):
            raise ValueError("Invalid projection dimension")
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    suffix = f"{args.phase}_{args.cohort}" + (f"_smoke{args.limit}" if args.limit else "")
    records, paths = calibration_records()
    selected = [r for r in records if r["cohort"] == args.cohort]
    if args.limit:
        selected = selected[:args.limit]
    selected = image_bytes(selected)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    begin = time.perf_counter()
    manifest = {"protocol_commit": "216406b", "phase": args.phase.upper(), "cohort": args.cohort,
                "smoke_limit": args.limit, "image_ids": [r["global_index"] for r in selected],
                "source_parquet_filenames": [Path(p).name for p in paths],
                "model_hashes": {}, "device": str(device),
                "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None,
                "torch": torch.__version__, "python": platform.python_version(),
                "batch_size": args.batch_size, "candidate_seed": "64021+global_index+1009*196+model_offset",
                "projection_dimensions": dimensions if args.phase == "b" else None,
                "projection_seed": "76151+dimension+model_offset" if args.phase == "b" else None,
                "teacher_sets": 0, "teacher_seconds": 0.0, "max_parity_error": 0.0}
    all_rows, all_runtime = [], []
    for model_key, depth, _ in MODEL_CONFIG[:2]:
        model, transform, _ = load_model_and_transform(model_key, device)
        manifest["model_hashes"][model_key] = model_weight_hash(model)
        projections, build_seconds = {}, {}
        if args.phase == "b":
            for dimension in dimensions:
                tic = time.perf_counter()
                projections[dimension] = gaussian_projection(
                    1000, dimension, 76151 + dimension + (0 if model_key == "deit_small" else 1000003))
                build_seconds[dimension] = time.perf_counter() - tic
        with torch.inference_mode():
            for n, record in enumerate(selected):
                x = transform(Image.open(io.BytesIO(record["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
                full = initial_state(prefix(model, model_key, depth, x))
                clean = model(x)
                if args.phase == "a":
                    rows, runtime = evaluate_phase_a(model, model_key, depth, full, clean,
                                                     record["global_index"], args.cohort, args.batch_size)
                elif args.phase == "b":
                    rows, runtime = evaluate_phase_b(model, model_key, depth, full, clean,
                                                     record["global_index"], args.cohort,
                                                     args.batch_size, projections, build_seconds)
                else:
                    rows, runtime = evaluate_tome_control(model, model_key, depth, full, clean,
                                                          record["global_index"], args.cohort,
                                                          args.batch_size)
                all_rows.extend(rows)
                all_runtime.append(runtime)
                manifest["teacher_sets"] += runtime["teacher_sets"]
                manifest["teacher_seconds"] += runtime["teacher_seconds"]
                manifest["max_parity_error"] = max(
                    manifest["max_parity_error"],
                    runtime.get("parity_max_abs", runtime.get("proposal_parity_max_abs", 0.0)))
                if (n + 1) % 8 == 0 or n + 1 == len(selected):
                    print(f"{model_key} {args.phase.upper()} {n+1}/{len(selected)} elapsed={time.perf_counter()-begin:.1f}s", flush=True)
        del model
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    manifest["elapsed_seconds"] = time.perf_counter() - begin
    manifest["peak_gpu_mib"] = float(torch.cuda.max_memory_allocated() / 2 ** 20) if torch.cuda.is_available() else 0.0
    per_image = pd.DataFrame(all_rows)
    if args.phase == "a":
        # Keep the registered prefix curve and every image-specific feasible
        # cardinality needed for count-matched distinct-destination contrasts.
        per_image = per_image[per_image.k.isin((1, 2, 4, 8, 16)) |
                              (per_image.k == per_image.max_distinct_destination_matching)]
    per_image.to_csv(out / f"phase_{suffix}_per_image.csv", index=False)
    pd.DataFrame(all_runtime).to_csv(out / f"phase_{suffix}_runtime.csv", index=False)
    (out / f"manifest_{suffix}.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf8")
    print(json.dumps({"suffix": suffix, "elapsed_seconds": manifest["elapsed_seconds"],
                      "teacher_sets": manifest["teacher_sets"], "peak_gpu_mib": manifest["peak_gpu_mib"]}), flush=True)


if __name__ == "__main__":
    main()
