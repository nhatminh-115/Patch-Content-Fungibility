"""Post-hoc calibration-only sensitivity study for exact-Jacobian compression.

The script reuses the primary confirmatory feature-similarity grouping,
per-image exact downstream Jacobian, carrier solver, and multiplicity-aware
compressed forward. It never constructs or reads the held-out evaluation split.

Run an 8-image runtime/memory benchmark first:
    python scripts/run_regularization_sensitivity.py --benchmark-only

After reviewing the generated cost estimate, run the full 200-image cohort:
    python scripts/run_regularization_sensitivity.py
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import math
import os
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy.stats as st
import seaborn as sns
import torch
import torch.nn.functional as F

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.v0_6_dataset import ParquetImageSubset
from patch_fungibility.dense_fraction_models import load_model_and_transform, forward_block_by_block
from patch_fungibility.compression_models import forward_downstream_compressed
from patch_fungibility.operator_compression_confirmatory import (
    compute_fast_downstream_jacobian,
    create_groupings_confirmatory,
    solve_operator_aware_carriers_fast,
)


OUT = ROOT / "outputs" / "fungibility_regularization_sensitivity"
FIG = OUT / "figures"
FACTORS = [0.01, 0.1, 1.0, 3.0, 10.0, 30.0, 100.0]
MODEL_SPECS = [
    {"key": "deit_tiny", "name": "DeiT-Tiny", "depth": 8, "patches": 196, "budgets": [32, 98]},
    {"key": "deit_small", "name": "DeiT-Small", "depth": 8, "patches": 196, "budgets": [32, 98]},
    {"key": "vit_base", "name": "ViT-B/16 AugReg", "depth": 7, "patches": 196, "budgets": [32, 98]},
    {"key": "dinov2", "name": "DINOv2 ViT-S/14", "depth": 8, "patches": 256, "budgets": [42, 128]},
]


def load_calibration_only(n_images: int):
    """Match get_disjoint_imagenet_splits(seed=9101) without touching eval IDs."""
    cache_glob = os.path.expanduser("~/.cache/huggingface/hub/**/val-*.parquet")
    files = sorted(__import__("glob").glob(cache_glob, recursive=True))
    if not files:
        raise FileNotFoundError("ImageNet validation parquet files are absent from the local cache.")
    frames = [pd.read_parquet(p, columns=["image", "label"]) for p in files]
    all_df = pd.concat(frames, ignore_index=True)
    all_df["global_index"] = np.arange(len(all_df))
    grouped = all_df.groupby("label")
    classes = sorted(grouped.groups.keys())[:1000]
    if len(classes) < n_images:
        raise RuntimeError(f"Only {len(classes)} calibration classes are available; requested {n_images} images.")
    rng = np.random.RandomState(9101)
    selected = []
    for cls in classes:
        indices = list(grouped.groups[cls])
        selected.append(int(rng.choice(indices)))
    selected = selected[:n_images]
    df = all_df.loc[selected].reset_index(drop=True)
    samples = []
    for _, row in df.iterrows():
        image = row["image"]
        if isinstance(image, dict) and "bytes" in image:
            image_bytes = image["bytes"]
        elif isinstance(image, bytes):
            image_bytes = image
        else:
            raise TypeError(f"Unsupported parquet image value: {type(image)}")
        samples.append((image_bytes, int(row["label"])))
    ids = df["global_index"].astype(int).tolist()
    cohort_hash = hashlib.sha256(",".join(map(str, ids)).encode()).hexdigest()
    return samples, df, ids, cohort_hash


def true_class_margin(logits: torch.Tensor, target: int) -> float:
    row = logits[0]
    mask = torch.ones_like(row, dtype=torch.bool)
    mask[target] = False
    return float((row[target] - row[mask].max()).item())


def metric_row(logits, clean_logits, target, clean_correct, method, model, image_idx,
               global_index, budget, factor, trace_per_dim, lam_abs, residual, displacement):
    with torch.no_grad():
        prediction = int(logits.argmax(dim=-1).item())
        margin_clean = true_class_margin(clean_logits, target)
        margin_compressed = true_class_margin(logits, target)
        return {
            "model": model,
            "image_idx": image_idx,
            "global_index": global_index,
            "target": target,
            "clean_correct": int(clean_correct),
            "budget": budget,
            "method": method,
            "lambda_factor": factor,
            "trace_HJ_per_ds": trace_per_dim,
            "lambda_absolute": lam_abs,
            "compressed_correct": int(prediction == target),
            "compressed_prediction": prediction,
            "logit_l2_damage": float(torch.linalg.vector_norm(logits - clean_logits).item()),
            "true_margin_clean": margin_clean,
            "true_margin_compressed": margin_compressed,
            "true_margin_change": margin_compressed - margin_clean,
            "operator_residual_JE": residual,
            "carrier_displacement_fro": displacement,
        }


def trace_per_readout_dim(J, groups, multiplicities):
    ds, nxd = J.shape
    n = sum(len(g) for g in groups)
    d = nxd // n
    blocks = J.view(ds, n, d)
    trace = 0.0
    for j, members in enumerate(groups):
        kj = blocks[:, members, :].sum(dim=1)
        trace += float(kj.square().sum().item()) / float(multiplicities[j].item())
    return trace / float(ds)


def save_figures(summary: pd.DataFrame):
    FIG.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid", context="notebook")
    for metric, ylabel, filename in [
        ("top1_rate", "Top-1 correctness on calibration cohort", "factor_vs_top1"),
        ("mean_logit_l2_damage", "Clean-to-compressed logit L2 damage", "factor_vs_logit_damage"),
        ("mean_operator_residual_JE", r"Linearized residual $||JE||$", "factor_vs_operator_residual"),
        ("mean_carrier_displacement_fro", r"Carrier displacement $||C^*-C_{mean}||_F$", "factor_vs_carrier_displacement"),
    ]:
        plot = summary[summary["method"] == "operator_aware"].copy()
        g = sns.relplot(data=plot, x="lambda_factor", y=metric, hue="budget", col="model",
                        col_wrap=2, kind="line", marker="o", facet_kws={"sharey": False},
                        height=4.0, aspect=1.35)
        g.set(xscale="log")
        g.set_titles("{col_name}")
        axes = np.asarray(g.axes).reshape(-1)
        for i, ax in enumerate(axes):
            ax.set_ylabel(ylabel if i % 2 == 0 else "")
            ax.set_xlabel(r"Dimensionless $\lambda_{factor}$" if i >= 2 else "")
            ax.tick_params(axis="both", labelsize=10)
        g.figure.suptitle(ylabel, y=1.02, fontsize=15)
        g.figure.savefig(FIG / f"{filename}.png", dpi=180, bbox_inches="tight")
        g.figure.savefig(FIG / f"{filename}.svg", bbox_inches="tight")
        plt.close(g.figure)


def aggregate_rows(raw: pd.DataFrame):
    keys = ["model", "budget", "method", "lambda_factor"]
    summary = raw.groupby(keys, dropna=False).agg(
        n=("compressed_correct", "size"),
        top1_rate=("compressed_correct", "mean"),
        top1_sd=("compressed_correct", "std"),
        mean_logit_l2_damage=("logit_l2_damage", "mean"),
        sd_logit_l2_damage=("logit_l2_damage", "std"),
        mean_true_margin_change=("true_margin_change", "mean"),
        sd_true_margin_change=("true_margin_change", "std"),
        mean_operator_residual_JE=("operator_residual_JE", "mean"),
        sd_operator_residual_JE=("operator_residual_JE", "std"),
        mean_carrier_displacement_fro=("carrier_displacement_fro", "mean"),
        sd_carrier_displacement_fro=("carrier_displacement_fro", "std"),
        mean_trace_HJ_per_ds=("trace_HJ_per_ds", "mean"),
        mean_lambda_absolute=("lambda_absolute", "mean"),
    ).reset_index()
    summary["top1_se"] = summary["top1_sd"] / np.sqrt(summary["n"])
    summary["logit_l2_se"] = summary["sd_logit_l2_damage"] / np.sqrt(summary["n"])
    return summary


def paired_comparisons(raw: pd.DataFrame):
    comparisons = []
    operator = raw[raw["method"] == "operator_aware"]
    for (model, budget), cell in operator.groupby(["model", "budget"]):
        for other_factor in (3.0, 30.0):
            left = cell[cell.lambda_factor == 10.0].set_index("image_idx")
            right = cell[cell.lambda_factor == other_factor].set_index("image_idx")
            left, right = left.align(right, join="inner", axis=0)
            n = len(left)
            dacc = (left.compressed_correct - right.compressed_correct).to_numpy(dtype=float)
            discordant = int(np.sum(dacc != 0))
            wins = int(np.sum(dacc > 0)); losses = int(np.sum(dacc < 0))
            p_top1 = float(st.binomtest(min(wins, losses), wins + losses, 0.5).pvalue) if wins + losses else 1.0
            for metric in ("compressed_correct", "logit_l2_damage", "true_margin_change", "operator_residual_JE", "carrier_displacement_fro"):
                diff = left[metric].to_numpy(float) - right[metric].to_numpy(float)
                sd = float(np.std(diff, ddof=1)) if n > 1 else float("nan")
                se = sd / math.sqrt(n) if n > 1 else float("nan")
                crit = float(st.t.ppf(0.975, n - 1)) if n > 1 else float("nan")
                ttest_p = float(st.ttest_rel(left[metric], right[metric]).pvalue) if n > 1 else float("nan")
                wilcoxon_p = float(st.wilcoxon(diff, zero_method="wilcox").pvalue) if n > 1 and np.any(diff != 0) else 1.0
                comparisons.append({
                    "model": model, "budget": budget, "factor_a": 10.0, "factor_b": other_factor,
                    "metric": metric, "n_paired_images": n, "mean_difference_a_minus_b": float(np.mean(diff)),
                    "sd_paired_difference": sd, "ci95_low": float(np.mean(diff) - crit * se),
                    "ci95_high": float(np.mean(diff) + crit * se), "paired_t_p_unadjusted": ttest_p,
                    "wilcoxon_p_unadjusted": wilcoxon_p, "top1_wins_a": wins,
                    "top1_losses_a": losses, "top1_ties": n - discordant,
                    "top1_mcnemar_exact_p_unadjusted": p_top1,
                    "inference_unit_note": "paired calibration images within this model-budget cell; cells/factors are repeated on the same cohort",
                })
    return pd.DataFrame(comparisons)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--benchmark-only", action="store_true", help="Run the specified 8-image cost benchmark only.")
    parser.add_argument("--postprocess-only", action="store_true", help="Rebuild tables and figures from saved full raw CSV without rerunning models.")
    parser.add_argument("--n-images", type=int, default=200, help="Calibration images per architecture for the full run.")
    args = parser.parse_args()
    if args.postprocess_only:
        raw_path = OUT / "per_image_results.csv"
        if not raw_path.is_file():
            raise FileNotFoundError(f"Missing full raw results: {raw_path}")
        postprocess(pd.read_csv(raw_path))
        return
    n_images = 8 if args.benchmark_only else args.n_images
    if n_images <= 0 or n_images > 1000:
        raise ValueError("n-images must be between 1 and 1000.")
    if not args.benchmark_only and n_images != 200:
        raise ValueError("The requested full design is fixed at 200 images; use --benchmark-only for the 8-image cost probe.")

    OUT.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    all_rows, runtime_rows, model_meta = [], [], []
    cohort_ids, cohort_hash = None, None
    dataset_setup_start = time.perf_counter()
    calibration_samples, calib_df, cohort_ids, cohort_hash = load_calibration_only(n_images)
    data_setup_sec = time.perf_counter() - dataset_setup_start

    for spec in MODEL_SPECS:
        key, model_name = spec["key"], spec["name"]
        load_start = time.perf_counter()
        model, transform, meta = load_model_and_transform(key, device)
        model.eval()
        model_load_sec = time.perf_counter() - load_start
        dataset = ParquetImageSubset(calibration_samples, transform=transform)
        loader = torch.utils.data.DataLoader(dataset, batch_size=1, shuffle=False, num_workers=0)

        if device.type == "cuda":
            torch.cuda.synchronize()
            baseline_mem = torch.cuda.memory_allocated(device)
            torch.cuda.reset_peak_memory_stats(device)
        else:
            baseline_mem = 0
        sums = {k: 0.0 for k in ("image_total_sec", "jacobian_sec", "grouping_sec", "solver_sec", "compressed_forward_sec")}
        image_count = 0
        for image_idx, (img_tensor, label_tensor) in enumerate(loader):
            if image_idx >= n_images:
                break
            image_start = time.perf_counter()
            img_tensor = img_tensor.to(device)
            target = int(label_tensor.item())
            global_index = int(cohort_ids[image_idx])
            with torch.no_grad():
                clean_logits, acts = forward_block_by_block(model, key, x=img_tensor, collect_depths=(spec["depth"],))
            clean_act = acts[spec["depth"]]
            P = clean_act[0, 1:, :]
            cls_token = clean_act[:, 0:1, :]
            clean_correct = int(clean_logits.argmax(dim=-1).item() == target)

            if device.type == "cuda": torch.cuda.synchronize()
            t = time.perf_counter()
            J = compute_fast_downstream_jacobian(model, key, spec["depth"], clean_act, chunk_size=128)
            if device.type == "cuda": torch.cuda.synchronize()
            jac_sec = time.perf_counter() - t

            budget_rows = []
            group_sec = solve_sec = forward_sec = 0.0
            for budget in spec["budgets"]:
                t = time.perf_counter()
                groups, S, mults = create_groupings_confirmatory(P, budget, strategy="feature_similarity", seed=42)
                if device.type == "cuda": torch.cuda.synchronize()
                group_sec += time.perf_counter() - t
                trace_pd = trace_per_readout_dim(J, groups, mults)
                for factor in FACTORS:
                    t = time.perf_counter()
                    sol = solve_operator_aware_carriers_fast(P, S, mults, J, lam_factor=factor)
                    if device.type == "cuda": torch.cuda.synchronize()
                    solve_sec += time.perf_counter() - t
                    lam_abs = factor * trace_pd
                    t_forward = time.perf_counter()
                    with torch.no_grad():
                        h_comp = torch.cat([cls_token, sol["C_opt"].unsqueeze(0)], dim=1)
                        all_mults = torch.cat([torch.ones(1, device=device), mults], dim=0)
                        logits = forward_downstream_compressed(model, key, spec["depth"], h_comp, all_mults, spec["patches"])
                    if device.type == "cuda": torch.cuda.synchronize()
                    forward_sec += time.perf_counter() - t_forward
                    row = metric_row(logits, clean_logits, target, clean_correct, "operator_aware", model_name,
                                     image_idx, global_index, budget, factor, trace_pd, lam_abs,
                                     float(sol["norm_r_opt"]), float(sol["norm_delta_C"]))
                    all_rows.append(row)
                    if factor == FACTORS[0]:
                        budget_rows.append((budget, groups, S, mults, sol["C_mean"], trace_pd))

            # Group Mean is recorded once per image/budget as the common baseline.
            for budget, groups, S, mults, C_mean, trace_pd in budget_rows:
                all_mults = torch.cat([torch.ones(1, device=device), mults], dim=0)
                h_comp = torch.cat([cls_token, C_mean.unsqueeze(0)], dim=1)
                t_forward = time.perf_counter()
                with torch.no_grad():
                    logits = forward_downstream_compressed(model, key, spec["depth"], h_comp, all_mults, spec["patches"])
                if device.type == "cuda": torch.cuda.synchronize()
                forward_sec += time.perf_counter() - t_forward
                residual = float(torch.linalg.vector_norm(J @ (P - S @ C_mean).reshape(-1)).item())
                all_rows.append(metric_row(logits, clean_logits, target, clean_correct, "group_mean", model_name,
                                           image_idx, global_index, budget, np.nan, trace_pd, np.nan,
                                           residual, 0.0))

            image_sec = time.perf_counter() - image_start
            sums["image_total_sec"] += image_sec
            sums["jacobian_sec"] += jac_sec
            sums["grouping_sec"] += group_sec
            sums["solver_sec"] += solve_sec
            sums["compressed_forward_sec"] += forward_sec
            image_count += 1
            print(f"{model_name} calibration image {image_idx+1}/{n_images}: {image_sec:.2f}s", flush=True)

        if device.type == "cuda":
            torch.cuda.synchronize()
            peak_mem = torch.cuda.max_memory_allocated(device)
            peak_reserved = torch.cuda.max_memory_reserved(device)
        else:
            peak_mem = peak_reserved = 0
        mean_img_sec = sums["image_total_sec"] / max(1, image_count)
        runtime_rows.append({
            "model": model_name, "n_benchmark_images": image_count, "model_load_sec": model_load_sec,
            "mean_full_image_sec": mean_img_sec, "mean_jacobian_sec": sums["jacobian_sec"] / max(1, image_count),
            "mean_grouping_sec": sums["grouping_sec"] / max(1, image_count),
            "mean_all_factor_solves_sec": sums["solver_sec"] / max(1, image_count),
            "mean_compressed_forward_sec": sums["compressed_forward_sec"] / max(1, image_count),
            "estimated_200_image_compute_hours": mean_img_sec * 200 / 3600,
            "peak_cuda_allocated_gib": peak_mem / (1024**3),
            "peak_cuda_reserved_gib": peak_reserved / (1024**3),
            "baseline_cuda_allocated_gib_after_model_load": baseline_mem / (1024**3),
        })
        model_meta.append({"model": model_name, "model_id": meta.get("model_id"), "depth": spec["depth"],
                           "patches": spec["patches"], "budgets": spec["budgets"]})
        del model, dataset, loader
        gc.collect()
        if device.type == "cuda": torch.cuda.empty_cache()

    raw = pd.DataFrame(all_rows)
    runtimes = pd.DataFrame(runtime_rows)
    run_suffix = "benchmark8" if args.benchmark_only else "full"
    raw_path = OUT / ("per_image_results_benchmark8.csv" if args.benchmark_only else "per_image_results.csv")
    runtime_path = OUT / ("runtime_benchmark8.csv" if args.benchmark_only else "runtime_by_architecture.csv")
    raw.to_csv(raw_path, index=False)
    runtimes.to_csv(runtime_path, index=False)

    total_hr = float(runtimes["estimated_200_image_compute_hours"].sum())
    manifest = {
        "study": "post-hoc exact-Jacobian regularization sensitivity; not the missing historical pilot",
        "status": "benchmark_only_cost_estimate" if args.benchmark_only else "completed",
        "timestamp_local": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "git_commit": __import__("subprocess").check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
        "device": str(device), "gpu_name": torch.cuda.get_device_name(0) if device.type == "cuda" else None,
        "gpu_total_memory_gib": torch.cuda.get_device_properties(0).total_memory / (1024**3) if device.type == "cuda" else None,
        "calibration_split_seed": 9101, "evaluation_split_seed_used": None,
        "calibration_images_per_architecture": n_images, "calibration_global_index_sha256": cohort_hash,
        "calibration_global_indices": cohort_ids, "factor_grid": FACTORS,
        "models": model_meta, "runtime_benchmark": runtime_rows,
        "estimated_full_200_image_compute_hours_excluding_model_and_dataset_load": total_hr,
        "dataset_setup_sec": data_setup_sec,
        "jacobian_policy": "one exact per-image J, reused for both budgets and all seven factors",
        "grouping": "existing confirmatory feature_similarity, seed 42, computed once per image-budget",
        "downstream_forward": "existing multiplicity-aware compressed forward",
        "primary_solver_modified": False,
        "historical_confirmatory_outputs_modified": False,
    }
    (OUT / f"manifest_{run_suffix}.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    if args.benchmark_only:
        print(json.dumps({"estimated_full_200_image_compute_hours_excluding_model_and_dataset_load": total_hr,
                          "runtime": runtime_rows}, indent=2), flush=True)
        return

    postprocess(raw)
    print(f"Completed calibration-only sensitivity with {len(raw)} per-image rows; estimated 200-image compute {total_hr:.2f} h.")


def postprocess(raw: pd.DataFrame):
    summary = aggregate_rows(raw)
    summary.to_csv(OUT / "aggregated_by_architecture_budget_factor.csv", index=False)
    paired = paired_comparisons(raw)
    paired.to_csv(OUT / "paired_factor10_vs_3_30.csv", index=False)
    robustness = []
    op = raw[raw.method == "operator_aware"]
    for (model_name, budget), cell in op.groupby(["model", "budget"]):
        byf = {float(f): g.set_index("image_idx") for f, g in cell.groupby("lambda_factor")}
        for other in (3.0, 30.0):
            d = byf[10.0].compressed_correct - byf[other].compressed_correct
            robustness.append({"model": model_name, "budget": budget, "factor_10_vs": other,
                               "images_factor10_correct_but_other_wrong": int((d > 0).sum()),
                               "images_other_correct_but_factor10_wrong": int((d < 0).sum()),
                               "images_tied": int((d == 0).sum()), "n_images": len(d),
                               "descriptive_only_same_images_reused_across_cells": True})
    pd.DataFrame(robustness).to_csv(OUT / "cross_cell_robustness_descriptive.csv", index=False)
    save_figures(summary)
    print(f"Postprocessed {len(raw)} per-image rows into {len(summary)} architecture-budget-method-factor summaries and figures.")


if __name__ == "__main__":
    main()
