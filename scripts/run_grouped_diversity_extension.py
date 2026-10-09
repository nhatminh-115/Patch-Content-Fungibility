"""Run the frozen grouped-token-diversity extension for ViT-B/16 and DINOv2.

The design is documented in
docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md. This script never
changes archived V0.8/V1 results.
"""
from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import scipy
from scipy import stats
import torch
from torch.utils.data import DataLoader

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.v0_6_dataset import (  # noqa: E402
    get_disjoint_imagenet_splits,
    ParquetImageSubset,
)
from patch_fungibility.v1_models import (  # noqa: E402
    get_vitb_model,
    get_dinov2_model,
    forward_vitb_manual,
    forward_dinov2_manual,
)
from patch_fungibility.v1_interventions import compute_calibration_statistics  # noqa: E402

SEEDS = [26001, 26002, 26003, 26004, 26005]
CALIBRATION_SEED = 9101
EVALUATION_SEED = 9201
N_PER_SPLIT = 1000
DEPTH = 8
BATCH_SIZES = {"vitb": 16, "dinov2": 32}
MODEL_CONFIG = {
    "vitb": {
        "name": "ViT-B/16 AugReg",
        "n_patches": 196,
        "stats_prefix": "vitb",
        "old_parquet": "outputs/fungibility_v1/vitb_image_results.parquet",
        "old_shared_prefix": "SHARED_GAUSSIAN_s",
        "old_independent_prefix": "INDEPENDENT_GAUSSIAN_s",
    },
    "dinov2": {
        "name": "DINOv2 ViT-S/14",
        "n_patches": 256,
        "stats_prefix": "dinov2",
        "old_parquet": "outputs/fungibility_v1/dinov2_image_results.parquet",
        "old_shared_prefix": "SHARED_GAUSSIAN_s",
        "old_independent_prefix": "INDEPENDENT_GAUSSIAN_s",
    },
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def model_state_sha256(model: torch.nn.Module) -> str:
    digest = hashlib.sha256()
    for name, value in sorted(model.state_dict().items()):
        tensor = value.detach().cpu().contiguous()
        digest.update(name.encode("utf-8"))
        digest.update(str(tensor.dtype).encode("ascii"))
        digest.update(str(tuple(tensor.shape)).encode("ascii"))
        digest.update(tensor.view(torch.uint8).numpy().tobytes())
    return digest.hexdigest()


def get_forward_fn(model_type: str):
    return forward_vitb_manual if model_type == "vitb" else forward_dinov2_manual


def logits_metrics(logits: torch.Tensor, labels: torch.Tensor) -> pd.DataFrame:
    logits_np = logits.detach().float().cpu().numpy()
    labels_np = labels.detach().cpu().numpy().astype(np.int64)
    n, _ = logits_np.shape
    true_logits = logits_np[np.arange(n), labels_np]
    incorrect = logits_np.copy()
    incorrect[np.arange(n), labels_np] = -np.inf
    strongest_wrong = incorrect.max(axis=1)
    prediction = logits_np.argmax(axis=1)
    return pd.DataFrame({
        "label": labels_np,
        "true_class_logit": true_logits,
        "strongest_incorrect_logit": strongest_wrong,
        "true_class_margin": true_logits - strongest_wrong,
        "top1_prediction": prediction,
        "correctness": (prediction == labels_np).astype(np.int8),
    })


def extract_calibration_and_eval(
    model: torch.nn.Module,
    model_type: str,
    calib_ds: ParquetImageSubset,
    eval_ds: ParquetImageSubset,
    device: torch.device,
    batch_size: int,
) -> tuple[torch.Tensor, torch.Tensor, pd.DataFrame]:
    """Use the same audited block-by-block forward functions as the V1 run."""
    calib_loader = DataLoader(calib_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    eval_loader = DataLoader(eval_ds, batch_size=batch_size, shuffle=False, num_workers=0)
    calib_blocks: list[torch.Tensor] = []
    eval_blocks: list[torch.Tensor] = []
    clean_metrics: list[pd.DataFrame] = []
    forward_fn = get_forward_fn(model_type)

    with torch.inference_mode():
        for images, _labels in calib_loader:
            _logits, collected = forward_fn(
                model, x=images.to(device), start_depth=0, collect_depths=(DEPTH,)
            )
            calib_blocks.append(collected[DEPTH][:, 1:, :].cpu())
        for images, labels in eval_loader:
            logits, collected = forward_fn(
                model, x=images.to(device), start_depth=0, collect_depths=(DEPTH,)
            )
            eval_blocks.append(collected[DEPTH].cpu())
            clean_metrics.append(logits_metrics(logits, labels))

    return (
        torch.cat(calib_blocks, dim=0),
        torch.cat(eval_blocks, dim=0),
        pd.concat(clean_metrics, ignore_index=True),
    )


def compare_calibration_statistics(
    model_type: str,
    calib_patch_acts: torch.Tensor,
    archived: dict[str, np.ndarray],
) -> dict[str, Any]:
    recomputed = compute_calibration_statistics({DEPTH: calib_patch_acts})
    prefix = MODEL_CONFIG[model_type]["stats_prefix"]
    checks = {}
    for name in ("mu_8", "sigma_8"):
        reference = np.asarray(archived[f"{prefix}_{name}"], dtype=np.float32)
        current = np.asarray(recomputed[name], dtype=np.float32)
        max_abs = float(np.max(np.abs(reference - current)))
        checks[name] = {
            "shape_match": bool(reference.shape == current.shape),
            "max_absolute_difference": max_abs,
            "allclose_atol_1e-6_rtol_1e-5": bool(
                reference.shape == current.shape
                and np.allclose(reference, current, atol=1e-6, rtol=1e-5)
            ),
        }
    if not all(item["allclose_atol_1e-6_rtol_1e-5"] for item in checks.values()):
        raise RuntimeError(f"Recomputed calibration statistics differ from archived V1 values: {checks}")
    return checks


def run_condition(
    model: torch.nn.Module,
    model_type: str,
    eval_hidden: torch.Tensor,
    labels: torch.Tensor,
    mu: torch.Tensor,
    sigma: torch.Tensor,
    k: int,
    seed: int,
    device: torch.device,
    batch_size: int,
) -> pd.DataFrame:
    n_images, seq_len, dim = eval_hidden.shape
    n_patches = seq_len - 1
    if n_patches != MODEL_CONFIG[model_type]["n_patches"]:
        raise AssertionError(f"Unexpected patch count: {n_patches}")
    if not 1 <= k <= n_patches:
        raise ValueError(f"K={k} is invalid for {n_patches} patches")

    # Match V0.8: one CPU generator per condition, continuously advanced across batches.
    generator = torch.Generator(device="cpu")
    generator.manual_seed(seed)
    mu_device = mu.to(device=device, dtype=torch.float32)
    sigma_device = sigma.to(device=device, dtype=torch.float32)
    positions = torch.arange(n_patches, dtype=torch.long, device=device)
    group_indices = positions.remainder(k)
    if int(torch.unique(group_indices).numel()) != k:
        raise AssertionError(f"K={k} does not produce exactly K occupied groups")
    assignment_counts = torch.bincount(group_indices, minlength=k).cpu().numpy()
    if int(assignment_counts.max() - assignment_counts.min()) > 1:
        raise AssertionError(f"K={k} assignment is not balanced: {assignment_counts.tolist()}")

    forward_fn = get_forward_fn(model_type)
    frames = []
    uniqueness_verified = False
    with torch.inference_mode():
        for start in range(0, n_images, batch_size):
            stop = min(start + batch_size, n_images)
            batch_n = stop - start
            z_cpu = torch.randn((batch_n, k, dim), generator=generator, dtype=torch.float32)
            eps = z_cpu.to(device) * sigma_device.reshape(1, 1, dim)
            prototypes = mu_device.reshape(1, 1, dim) + eps
            if not uniqueness_verified:
                # Check sampled prototypes, not merely the index mapping.
                for sample in range(batch_n):
                    observed = torch.unique(prototypes[sample], dim=0).shape[0]
                    if int(observed) != k:
                        raise AssertionError(
                            f"Sampled {observed} distinct prototypes for K={k}; expected {k}"
                        )
                uniqueness_verified = True
            replacement = prototypes[:, group_indices, :]
            h = eval_hidden[start:stop].to(device).clone()
            cls_before = h[:, :1, :].clone()
            h[:, 1:, :] = replacement
            if not torch.equal(h[:, :1, :], cls_before):
                raise AssertionError("CLS token changed at intervention")
            logits, _ = forward_fn(model, start_depth=DEPTH, h_start=h)
            part = logits_metrics(logits, labels[start:stop])
            part.insert(0, "sample_id", np.arange(start, stop, dtype=np.int64))
            part.insert(0, "seed", seed)
            part.insert(0, "k", k)
            part.insert(0, "model", model_type)
            frames.append(part)
    return pd.concat(frames, ignore_index=True)


def seed_summary(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, k, seed), group in raw.groupby(["model", "k", "seed"], sort=True):
        rows.append({
            "model": model,
            "architecture": MODEL_CONFIG[model]["name"],
            "k": int(k),
            "n_patches": MODEL_CONFIG[model]["n_patches"],
            "seed": int(seed),
            "n_eval_images": int(group["sample_id"].nunique()),
            "top1_accuracy": float(group["correctness"].mean()),
            "mean_true_class_margin": float(group["true_class_margin"].mean()),
            "median_true_class_margin": float(group["true_class_margin"].median()),
        })
    return pd.DataFrame(rows)


def aggregate_summary(seed_df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for (model, k), group in seed_df.groupby(["model", "k"], sort=True):
        rows.append({
            "model": model,
            "architecture": MODEL_CONFIG[model]["name"],
            "k": int(k),
            "n_patches": MODEL_CONFIG[model]["n_patches"],
            "n_seeds": int(group["seed"].nunique()),
            "n_eval_images_per_seed": int(group["n_eval_images"].min()),
            "top1_accuracy_mean": float(group["top1_accuracy"].mean()),
            "top1_accuracy_sd_across_seeds": float(group["top1_accuracy"].std(ddof=1)),
            "mean_true_class_margin": float(group["mean_true_class_margin"].mean()),
            "mean_margin_sd_across_seeds": float(group["mean_true_class_margin"].std(ddof=1)),
            "median_true_class_margin_mean": float(group["median_true_class_margin"].mean()),
        })
    return pd.DataFrame(rows)


def benjamini_hochberg(p_values: list[float]) -> list[float]:
    n = len(p_values)
    if n == 0:
        return []
    order = np.argsort(np.asarray(p_values, dtype=float))
    adjusted = np.empty(n, dtype=float)
    running = 1.0
    for rank_idx in range(n - 1, -1, -1):
        original = order[rank_idx]
        rank = rank_idx + 1
        running = min(running, float(p_values[original]) * n / rank)
        adjusted[original] = min(1.0, running)
    return adjusted.tolist()


def paired_comparisons(raw: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, model_data in raw.groupby("model", sort=True):
        ks = sorted(model_data["k"].unique().tolist())
        for metric, metric_name, scale in [
            ("correctness", "top1_accuracy", 100.0),
            ("true_class_margin", "mean_true_class_margin", 1.0),
        ]:
            # Five seed outcomes are averaged within each image before testing.
            image_means = model_data.groupby(["sample_id", "k"], sort=True)[metric].mean().unstack("k")
            metric_rows = []
            for i, k_low in enumerate(ks):
                for k_high in ks[i + 1:]:
                    x = image_means[int(k_low)].to_numpy(dtype=float)
                    y = image_means[int(k_high)].to_numpy(dtype=float)
                    delta = y - x
                    n = int(delta.size)
                    mean_delta = float(delta.mean())
                    sd_delta = float(delta.std(ddof=1))
                    se = sd_delta / np.sqrt(n)
                    t_crit = float(stats.t.ppf(0.975, n - 1))
                    t_result = stats.ttest_rel(y, x, nan_policy="raise")
                    try:
                        wilcoxon_p = (1.0 if np.allclose(delta, 0.0) else
                                      float(stats.wilcoxon(y, x, zero_method="pratt").pvalue))
                    except ValueError:
                        wilcoxon_p = 1.0
                    metric_rows.append({
                        "model": model,
                        "architecture": MODEL_CONFIG[model]["name"],
                        "metric": metric_name,
                        "k_lower": int(k_low),
                        "k_higher": int(k_high),
                        "n_paired_images": n,
                        "seeds_averaged_per_image": int(model_data["seed"].nunique()),
                        "mean_difference_higher_minus_lower": mean_delta * scale,
                        "paired_t_ci95_low": (mean_delta - t_crit * se) * scale,
                        "paired_t_ci95_high": (mean_delta + t_crit * se) * scale,
                        "paired_t_statistic": float(t_result.statistic),
                        "paired_t_p": float(t_result.pvalue),
                        "wilcoxon_p": wilcoxon_p,
                    })
            qvals = benjamini_hochberg([r["wilcoxon_p"] for r in metric_rows])
            for row, qval in zip(metric_rows, qvals):
                row["wilcoxon_bh_q_within_model_metric"] = qval
                rows.append(row)
    return pd.DataFrame(rows)


def endpoint_compatibility(
    new_seed_df: pd.DataFrame,
    old_raw: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    rows = []
    for model, summary in new_seed_df.groupby("model", sort=True):
        old = old_raw[model]
        cfg = MODEL_CONFIG[model]
        for endpoint, old_prefix, condition in [
            (1, cfg["old_shared_prefix"], "shared_gaussian"),
            (cfg["n_patches"], cfg["old_independent_prefix"], "independent_gaussian"),
        ]:
            new_cond = summary[summary["k"] == endpoint]
            old_cond = old[old["condition_key"].str.match(rf"^{old_prefix}2400[1-5]$")].copy()
            if old_cond["condition_key"].nunique() != 5 or len(old_cond) != 5000:
                raise AssertionError(f"Expected 5,000 archived image rows for {model}/{condition}")
            if new_cond["seed"].nunique() != 5 or len(new_cond) != 5:
                raise AssertionError(f"Expected five new seed rows for {model}/K={endpoint}")
            old_seed = old_cond.groupby("condition_key").agg(
                top1_accuracy=("correctness", "mean"),
                mean_true_class_margin=("true_class_margin", "mean"),
            )
            for metric, new_col in [
                ("top1_accuracy", "top1_accuracy"),
                ("mean_true_class_margin", "mean_true_class_margin"),
            ]:
                old_values = old_seed[metric].to_numpy(dtype=float)
                new_values = new_cond[new_col].to_numpy(dtype=float)
                old_mean = float(old_values.mean())
                new_mean = float(new_values.mean())
                old_sd = float(old_values.std(ddof=1))
                new_sd = float(new_values.std(ddof=1))
                combined_se = float(np.sqrt(old_sd**2 / len(old_values) + new_sd**2 / len(new_values)))
                z = (abs(new_mean - old_mean) / combined_se if combined_se > 0 else
                     (0.0 if new_mean == old_mean else float("inf")))
                rows.append({
                    "model": model,
                    "architecture": cfg["name"],
                    "k": int(endpoint),
                    "reference_condition": condition,
                    "metric": metric,
                    "n_new_seeds": len(new_values),
                    "n_archived_seeds": len(old_values),
                    "new_mean": new_mean,
                    "new_sd_across_seeds": new_sd,
                    "archived_mean": old_mean,
                    "archived_sd_across_seeds": old_sd,
                    "absolute_difference": abs(new_mean - old_mean),
                    "combined_standard_error": combined_se,
                    "difference_in_combined_se": z,
                    "compatibility_threshold_combined_se": 2.0,
                    "status": "PASS" if z <= 2.0 else "REVIEW",
                })
    return pd.DataFrame(rows)


def monotonicity_summary(aggregate: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for model, group in aggregate.groupby("model", sort=True):
        group = group.sort_values("k")
        ks = group["k"].astype(int).tolist()
        for metric, col, scale in [
            ("top1_accuracy", "top1_accuracy_mean", 100.0),
            ("mean_true_class_margin", "mean_true_class_margin", 1.0),
        ]:
            values = group[col].to_numpy(dtype=float) * scale
            increments = np.diff(values)
            rows.append({
                "model": model,
                "architecture": MODEL_CONFIG[model]["name"],
                "metric": metric,
                "k_values": json.dumps(ks),
                "values_in_order": json.dumps([float(v) for v in values]),
                "adjacent_increments": json.dumps([float(v) for v in increments]),
                "n_positive_adjacent_increments": int(np.sum(increments > 0)),
                "n_adjacent_steps": int(len(increments)),
                "strictly_monotonic_increasing": bool(np.all(increments > 0)),
                "k64_to_full_increment": float(increments[-1]),
                "largest_prior_positive_increment": float(max(increments[:-1])) if len(increments) > 1 else np.nan,
            })
    return pd.DataFrame(rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/fungibility_v1_grouped_diversity_extension")
    parser.add_argument("--device", default=None)
    parser.add_argument("--batch-size-vitb", type=int, default=BATCH_SIZES["vitb"])
    parser.add_argument("--batch-size-dinov2", type=int, default=BATCH_SIZES["dinov2"])
    args = parser.parse_args()

    output_dir = (ROOT / args.output_dir).resolve()
    if output_dir.exists() and any(output_dir.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output directory: {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()
    device = torch.device(args.device or ("cuda" if torch.cuda.is_available() else "cpu"))
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats(device)

    head_result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    )
    manifest: dict[str, Any] = {
        "experiment": "PCF grouped-token-diversity cross-architecture extension",
        "status": "running",
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "frozen_protocol": "docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md",
        "frozen_protocol_sha256": sha256_file(
            ROOT / "docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md"
        ),
        "repository_head": head_result.stdout.strip(),
        "script_sha256": sha256_file(Path(__file__)),
        "device": str(device),
        "device_name": torch.cuda.get_device_name(device) if device.type == "cuda" else platform.processor(),
        "python": sys.version,
        "platform": platform.platform(),
        "torch": torch.__version__,
        "cuda_runtime": torch.version.cuda,
        "numpy": np.__version__,
        "pandas": pd.__version__,
        "scipy": scipy.__version__,
        "seeds": SEEDS,
        "n_calibration_images": N_PER_SPLIT,
        "n_evaluation_images": N_PER_SPLIT,
        "calibration_split_seed": CALIBRATION_SEED,
        "evaluation_split_seed": EVALUATION_SEED,
        "target_depth_output_block": DEPTH,
        "status_note": "No DeiT outcomes were rerun or modified.",
        "models": {},
    }
    (output_dir / "experiment_metadata.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    try:
        calib_raw, eval_raw, calib_manifest, eval_manifest = get_disjoint_imagenet_splits(
            calib_seed=CALIBRATION_SEED, eval_seed=EVALUATION_SEED, n_per_split=N_PER_SPLIT
        )
        for split_name, current, source_path in [
            ("calibration", calib_manifest, ROOT / "outputs/fungibility_v0_6/calibration_split.csv"),
            ("evaluation", eval_manifest, ROOT / "outputs/fungibility_v0_6/evaluation_split.csv"),
        ]:
            reference = pd.read_csv(source_path)
            for field in ("sample_id", "global_index", "label"):
                if field not in reference or not np.array_equal(current[field].to_numpy(), reference[field].to_numpy()):
                    raise AssertionError(f"{split_name} split differs from archived V0.6 field {field}")
            current.to_csv(output_dir / f"{split_name}_split_used.csv", index=False)
            manifest[f"{split_name}_split_source"] = str(source_path.relative_to(ROOT)).replace("\\", "/")
            manifest[f"{split_name}_split_sha256"] = sha256_file(source_path)
        if set(calib_manifest.global_index).intersection(set(eval_manifest.global_index)):
            raise AssertionError("Calibration and evaluation splits overlap")
        manifest["split_identity_verified"] = True
        manifest["split_overlap_count"] = 0
        stats_path = ROOT / "outputs/fungibility_v1/calibration_statistics.npz"
        archived = dict(np.load(stats_path))
        shutil.copy2(stats_path, output_dir / "calibration_statistics_used.npz")
        manifest["archived_calibration_statistics"] = str(stats_path.relative_to(ROOT)).replace("\\", "/")
        manifest["calibration_statistics_sha256"] = sha256_file(stats_path)
        (output_dir / "experiment_metadata.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

        raw_path = output_dir / "per_image_results.csv"
        seed_rows: list[dict[str, Any]] = []
        clean_rows: dict[str, dict[str, float]] = {}
        old_raw: dict[str, pd.DataFrame] = {}
        calibration_checks: dict[str, Any] = {}

        for model_type in ("vitb", "dinov2"):
            cfg = MODEL_CONFIG[model_type]
            batch_size = args.batch_size_vitb if model_type == "vitb" else args.batch_size_dinov2
            model, transform, model_meta = get_vitb_model(device) if model_type == "vitb" else get_dinov2_model(device)
            model.eval()
            frozen = all(not parameter.requires_grad for parameter in model.parameters())
            if not frozen:
                raise AssertionError(f"{cfg['name']} has trainable parameters")
            model_sha = model_state_sha256(model)
            model_meta["parameters_frozen"] = frozen
            model_meta["state_dict_sha256"] = model_sha

            calib_ds = ParquetImageSubset(calib_raw._samples, transform=transform)
            eval_ds = ParquetImageSubset(eval_raw._samples, transform=transform)
            calib_patch_acts, eval_hidden, clean = extract_calibration_and_eval(
                model, model_type, calib_ds, eval_ds, device, batch_size
            )
            calibration_checks[model_type] = compare_calibration_statistics(model_type, calib_patch_acts, archived)
            del calib_patch_acts
            prefix = cfg["stats_prefix"]
            mu = torch.from_numpy(np.asarray(archived[f"{prefix}_mu_8"], dtype=np.float32))
            sigma = torch.from_numpy(np.asarray(archived[f"{prefix}_sigma_8"], dtype=np.float32))
            if bool(torch.any(sigma <= 0)):
                raise AssertionError("Calibration sigma must be positive for every feature")

            old = pd.read_parquet(ROOT / cfg["old_parquet"])
            old_raw[model_type] = old
            old_clean = old[old["condition_key"] == "CLEAN"].sort_values("sample_id").reset_index(drop=True)
            if len(old_clean) != N_PER_SPLIT:
                raise AssertionError(f"Expected {N_PER_SPLIT} archived clean rows for {model_type}")
            if not np.array_equal(old_clean["sample_id"].to_numpy(), np.arange(N_PER_SPLIT)):
                raise AssertionError("Archived clean sample order differs")
            if not np.array_equal(old_clean["label"].to_numpy(), clean["label"].to_numpy()):
                raise AssertionError("Clean/evaluation labels differ from archived V1 order")
            if not np.array_equal(old_clean["correctness"].to_numpy(), clean["correctness"].to_numpy()):
                raise AssertionError("Current clean predictions differ from archived V1")
            max_clean_margin_diff = float(np.max(np.abs(
                old_clean["true_class_margin"].to_numpy(dtype=float)
                - clean["true_class_margin"].to_numpy(dtype=float)
            )))
            if max_clean_margin_diff > 1e-4:
                raise AssertionError(f"Clean margin parity failed for {model_type}: {max_clean_margin_diff}")

            clean_rows[model_type] = {
                "top1_accuracy": float(clean["correctness"].mean()),
                "mean_true_class_margin": float(clean["true_class_margin"].mean()),
                "max_abs_margin_diff_vs_v1": max_clean_margin_diff,
            }
            manifest["models"][model_type] = {
                "architecture": cfg["name"],
                **model_meta,
                "model_state_sha256": model_sha,
                "batch_size": batch_size,
                "n_patches": cfg["n_patches"],
                "k_values": [1, 2, 4, 8, 16, 32, 64, cfg["n_patches"]],
                "preprocessing": model_meta.get("data_config", "official transform returned by v1_models.py"),
                "clean_top1_accuracy": clean_rows[model_type]["top1_accuracy"],
                "clean_mean_true_class_margin": clean_rows[model_type]["mean_true_class_margin"],
                "clean_margin_max_abs_diff_vs_archived_v1": max_clean_margin_diff,
                "calibration_statistic_checks": calibration_checks[model_type],
            }
            (output_dir / "experiment_metadata.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

            for k in [1, 2, 4, 8, 16, 32, 64, cfg["n_patches"]]:
                for seed in SEEDS:
                    print(f"[{cfg['name']}] K={k}, seed={seed}", flush=True)
                    per_image = run_condition(
                        model, model_type, eval_hidden, torch.from_numpy(clean["label"].to_numpy()),
                        mu, sigma, k, seed, device, batch_size
                    )
                    sample_ids = per_image["sample_id"].to_numpy()
                    per_image["global_index"] = eval_manifest["global_index"].to_numpy()[sample_ids]
                    per_image["margin_damage_vs_clean"] = (
                        clean["true_class_margin"].to_numpy()[sample_ids]
                        - per_image["true_class_margin"].to_numpy()
                    )
                    per_image.to_csv(raw_path, mode="a", header=not raw_path.exists(), index=False)
                    seed_rows.append({
                        "model": model_type,
                        "architecture": cfg["name"],
                        "k": int(k),
                        "n_patches": cfg["n_patches"],
                        "seed": int(seed),
                        "n_eval_images": int(per_image["sample_id"].nunique()),
                        "top1_accuracy": float(per_image["correctness"].mean()),
                        "mean_true_class_margin": float(per_image["true_class_margin"].mean()),
                        "median_true_class_margin": float(per_image["true_class_margin"].median()),
                        "mean_margin_damage_vs_clean": float(per_image["margin_damage_vs_clean"].mean()),
                    })
                    pd.DataFrame(seed_rows).to_csv(output_dir / "seed_level_results.csv", index=False)

            del model, eval_hidden, clean
            gc.collect()
            if device.type == "cuda":
                torch.cuda.empty_cache()

        raw = pd.read_csv(raw_path)
        expected_rows = 2 * 8 * len(SEEDS) * N_PER_SPLIT
        if raw.duplicated(["model", "k", "seed", "sample_id"]).any():
            raise AssertionError("Duplicate per-image keys found")
        if len(raw) != expected_rows:
            raise AssertionError(f"Expected {expected_rows} raw rows, found {len(raw)}")

        seed_df = seed_summary(raw)
        aggregate = aggregate_summary(seed_df)
        paired = paired_comparisons(raw)
        monotonic = monotonicity_summary(aggregate)
        endpoints = endpoint_compatibility(seed_df, old_raw)
        seed_df.to_csv(output_dir / "seed_level_results.csv", index=False)
        aggregate.to_csv(output_dir / "aggregate_results.csv", index=False)
        paired.to_csv(output_dir / "paired_image_comparisons.csv", index=False)
        monotonic.to_csv(output_dir / "monotonicity_summary.csv", index=False)
        endpoints.to_csv(output_dir / "endpoint_validation.csv", index=False)

        validation = {
            "all_passed": bool(
                manifest.get("split_identity_verified")
                and manifest.get("split_overlap_count") == 0
                and all(all(item["allclose_atol_1e-6_rtol_1e-5"] for item in checks.values())
                        for checks in calibration_checks.values())
                and all(item["max_abs_margin_diff_vs_v1"] <= 1e-4 for item in clean_rows.values())
                and len(raw) == expected_rows
                and not raw.duplicated(["model", "k", "seed", "sample_id"]).any()
                and endpoints["status"].eq("PASS").all()
            ),
            "assertions": {
                "exact_historical_split_identity": manifest.get("split_identity_verified", False),
                "disjoint_split_images": manifest.get("split_overlap_count") == 0,
                "models_frozen": {m: bool(manifest["models"][m]["parameters_frozen"]) for m in manifest["models"]},
                "calibration_statistics_match_archived": calibration_checks,
                "clean_prediction_and_margin_parity": clean_rows,
                "raw_row_count": int(len(raw)),
                "expected_raw_row_count": int(expected_rows),
                "unique_per_image_condition_keys": not raw.duplicated(["model", "k", "seed", "sample_id"]).any(),
                "endpoint_compatibility_all_pass": bool(endpoints["status"].eq("PASS").all()),
                "endpoint_rows": endpoints.to_dict(orient="records"),
                "all_k_values_have_five_seeds_and_1000_images": bool(
                    seed_df["n_eval_images"].eq(N_PER_SPLIT).all()
                    and seed_df.groupby(["model", "k"])["seed"].nunique().eq(5).all()
                ),
                "patch_positions_are_not_treated_as_independent_samples": True,
                "seeds_are_not_treated_as_independent_images": True,
            },
        }
        (output_dir / "validation_results.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
        manifest.update({
            "status": "completed" if validation["all_passed"] else "completed_needs_review",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "runtime_seconds": time.time() - started,
            "peak_gpu_memory_gb": float(torch.cuda.max_memory_allocated(device) / 1024**3) if device.type == "cuda" else None,
            "raw_per_image_rows": int(len(raw)),
            "validation_all_passed": validation["all_passed"],
            "validation_file": "validation_results.json",
        })
        (output_dir / "experiment_metadata.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        print(aggregate.to_string(index=False))
        print(endpoints.to_string(index=False))
        print(json.dumps(validation, indent=2))
        return 0 if validation["all_passed"] else 2
    except Exception as exc:
        manifest.update({
            "status": "failed",
            "finished_utc": datetime.now(timezone.utc).isoformat(),
            "error_type": type(exc).__name__,
            "error": str(exc),
            "runtime_seconds": time.time() - started,
        })
        (output_dir / "experiment_metadata.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        raise


if __name__ == "__main__":
    raise SystemExit(main())
