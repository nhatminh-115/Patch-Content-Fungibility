#!/usr/bin/env python3
"""Frozen, additive Section 5 cross-architecture audit and targeted extension.

Writes only below outputs/fungibility_section5_cross_arch_extension/.
Existing scientific output directories are never modified.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from scipy.stats import pearsonr, spearmanr
from torch.utils.data import DataLoader, Subset
from torchvision import transforms

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.dense_fraction_models import load_model_and_transform, forward_block_by_block
from patch_fungibility.v0_6_dataset import get_disjoint_imagenet_splits
from patch_fungibility.multiblock_operator import (
    construct_downstream_jacobian,
    evaluate_heldout_prediction,
)
from patch_fungibility.full_fungibility_operator import construct_full_operator

OUT = ROOT / "outputs" / "fungibility_section5_cross_arch_extension"
GEOM_OUT = OUT / "functional_geometry"
PRED_OUT = OUT / "multiblock_prediction"
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
DEPTHS = (5, 7, 8, 10)
GEOM_MODELS = ("deit_tiny", "deit_small", "vit_base", "dinov2")
PRED_MODELS = ("deit_tiny", "vit_base", "dinov2")
N_GEOM = 100
N_PRED_IMAGES = 20
N_PERT = 100
BATCH_GEOM = 10

MODEL_LABELS = {
    "deit_tiny": "DeiT-Tiny",
    "deit_small": "DeiT-Small",
    "vit_base": "ViT-B/16 AugReg",
    "dinov2": "DINOv2 ViT-S/14",
}
PERTURBATION_FAMILIES = [
    (0, 25, "top_end_to_end_modes"),
    (25, 50, "middle_end_to_end_modes"),
    (50, 75, "end_to_end_null_modes"),
    (75, 100, "isotropic_gaussian_controls"),
]


def load_model_for_audit(model_key: str, device: torch.device):
    """Use the project loader, with a local-source route for the cached DINOv2 copy."""
    if model_key != "dinov2":
        return load_model_and_transform(model_key, device)
    cached_repo = Path(torch.hub.get_dir()) / "facebookresearch_dinov2_main"
    if not cached_repo.is_dir():
        raise FileNotFoundError(f"Cached DINOv2 repository missing: {cached_repo}")
    model = torch.hub.load(
        str(cached_repo), "dinov2_vits14_lc", layers=1, pretrained=True, source="local"
    )
    model.eval()
    for parameter in model.parameters():
        parameter.requires_grad_(False)
    model.to(device)
    transform = transforms.Compose([
        transforms.Resize(256, interpolation=transforms.InterpolationMode.BICUBIC),
        transforms.CenterCrop(224),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])
    meta = {
        "model_key": "dinov2",
        "model_id": "dinov2_vits14_lc",
        "embed_dim": 384,
        "num_patches": 256,
        "depth": 12,
        "primary_depth": 9,
        "secondary_depth": 8,
        "readout": "cls_and_patch_mean",
        "cached_repo": str(cached_repo),
    }
    return model, transform, meta

def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def family_for_id(pert_id: int) -> str:
    for lo, hi, name in PERTURBATION_FAMILIES:
        if lo <= pert_id < hi:
            return name
    raise ValueError(f"Unexpected perturbation id: {pert_id}")


def make_loader(dataset, indices: int, batch_size: int) -> DataLoader:
    return DataLoader(Subset(dataset, list(range(indices))), batch_size=batch_size, shuffle=False, num_workers=0)


def get_top_runner(clean_logits: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    top = clean_logits.argmax(dim=-1)
    tmp = clean_logits.clone()
    tmp[torch.arange(clean_logits.shape[0], device=clean_logits.device), top] = -torch.inf
    runner = tmp.argmax(dim=-1)
    return top, runner


def geometry_extension(calib_ds, calib_manifest) -> dict:
    GEOM_OUT.mkdir(parents=True, exist_ok=True)
    id_path = GEOM_OUT / "calibration_sample_ids.csv"
    calib_manifest.iloc[:N_GEOM][["sample_id", "global_index"]].to_csv(id_path, index=False)

    rows_metric = []
    rows_sensitivity = []
    rows_spectrum = []
    matrices: dict[str, np.ndarray] = {}
    model_metadata = {}

    for model_key in GEOM_MODELS:
        started = time.time()
        model, transform, meta = load_model_for_audit(model_key, DEVICE)
        model.eval()
        for p in model.parameters():
            p.requires_grad_(False)
        calib_ds.transform = transform
        loader = make_loader(calib_ds, N_GEOM, BATCH_GEOM)
        D = int(meta["embed_dim"])
        n_img = 0
        patch_chunks: dict[int, list[torch.Tensor]] = {d: [] for d in DEPTHS}

        # Pooled centered activation covariance, matching the original pilot.
        with torch.no_grad():
            for images, _labels in loader:
                images = images.to(DEVICE)
                _, collected = forward_block_by_block(
                    model, model_key, x=images, start_depth=0, collect_depths=DEPTHS
                )
                n_img += int(images.shape[0])
                for depth in DEPTHS:
                    patches = collected[depth][:, 1:, :].reshape(-1, D)
                    patch_chunks[depth].append(patches.detach().to(device="cpu", dtype=torch.float64))
                del images, collected

        if n_img != N_GEOM:
            raise RuntimeError(f"{model_key}: got {n_img} images, expected {N_GEOM}")

        covariances: dict[int, torch.Tensor] = {}
        for depth in DEPTHS:
            patches_all = torch.cat(patch_chunks[depth], dim=0)
            mean = patches_all.mean(dim=0)
            centered = patches_all - mean
            covariance = (centered.T @ centered) / (patches_all.shape[0] - 1)
            covariance = (covariance + covariance.T) * 0.5
            covariances[depth] = covariance.contiguous()
            del patches_all, centered

        # Exact M_l from the implementation's clean predicted-class margin,
        # accumulated in float64 in chunks to preserve PSD and avoid OOM.
        for depth in DEPTHS:
            gram = torch.zeros((D, D), dtype=torch.float64, device=DEVICE)
            n_patch_obs = 0
            loader = make_loader(calib_ds, N_GEOM, BATCH_GEOM)
            for images, _labels in loader:
                images = images.to(DEVICE)
                with torch.no_grad():
                    clean_logits, collected = forward_block_by_block(
                        model, model_key, x=images, start_depth=0, collect_depths=(depth,)
                    )
                    top, runner = get_top_runner(clean_logits)
                    hidden = collected[depth].detach()
                hidden_leaf = hidden.clone().requires_grad_(True)
                logits_down, _ = forward_block_by_block(
                    model, model_key, start_depth=depth, h_start=hidden_leaf
                )
                margins = (
                    logits_down[torch.arange(images.shape[0], device=DEVICE), top]
                    - logits_down[torch.arange(images.shape[0], device=DEVICE), runner]
                )
                grad_hidden = torch.autograd.grad(margins.sum(), hidden_leaf, retain_graph=False)[0]
                grad_flat = grad_hidden[:, 1:, :].reshape(-1, D).to(torch.float64)
                gram += grad_flat.T @ grad_flat
                n_patch_obs += int(grad_flat.shape[0])
                del images, clean_logits, collected, hidden, hidden_leaf, logits_down, margins, grad_hidden, grad_flat
                if DEVICE.type == "cuda":
                    torch.cuda.empty_cache()

            if n_patch_obs != N_GEOM * int(meta["num_patches"]):
                raise RuntimeError(
                    f"{model_key} depth {depth}: gradient token observations={n_patch_obs}, "
                    f"expected {N_GEOM * int(meta['num_patches'])}"
                )
            M = (gram / n_patch_obs).detach().cpu()
            M = (M + M.T) * 0.5
            C = covariances[depth]
            evals_raw, evecs = torch.linalg.eigh(M)
            evals_raw_np = evals_raw.numpy()
            lambda_max = float(evals_raw[-1].item())
            if not np.isfinite(lambda_max) or lambda_max <= 0:
                raise RuntimeError(f"{model_key} depth {depth}: invalid lambda_max={lambda_max}")
            psd_tol = 1e-10 * lambda_max
            severe_negative = int((evals_raw < -psd_tol).sum().item())
            roundoff_negative = int(((evals_raw < 0) & (evals_raw >= -psd_tol)).sum().item())
            evals_clip = evals_raw.clamp_min(0)
            total = float(evals_clip.sum().item())
            if total <= 0:
                raise RuntimeError(f"{model_key} depth {depth}: non-positive clipped spectral trace")
            prob = evals_clip / total
            positive = prob > 0
            effective_rank = float(torch.exp(-(prob[positive] * torch.log(prob[positive])).sum()).item())
            evals_desc = evals_raw.flip(0)
            # Cutoff counts are reported on the symmetric raw spectrum after only
            # treating round-off negatives as zero; materially negative values fail.
            evals_for_cutoff = evals_clip.flip(0)
            for rel_cut in (1e-4, 1e-3, 1e-2):
                null_count = int((evals_for_cutoff <= rel_cut * lambda_max).sum().item())
                rows_metric.append({
                    "model_key": model_key,
                    "architecture": MODEL_LABELS[model_key],
                    "depth": depth,
                    "D": D,
                    "N_img": n_img,
                    "n_patches_per_image": int(meta["num_patches"]),
                    "n_image_patch_observations": n_patch_obs,
                    "metric": "average per-patch clean predicted-class margin-gradient second moment",
                    "readout": meta["readout"],
                    "relative_cutoff": rel_cut,
                    "near_null_count": null_count,
                    "near_null_fraction": null_count / D,
                    "effective_rank": effective_rank,
                    "effective_rank_over_D": effective_rank / D,
                    "trace_M": total,
                    "lambda_max_raw": lambda_max,
                    "lambda_min_raw": float(evals_raw[0].item()),
                    "negative_eigenvalue_count_raw": int((evals_raw < 0).sum().item()),
                    "roundoff_negative_count_clipped": roundoff_negative,
                    "material_negative_count": severe_negative,
                    "psd_tolerance": psd_tol,
                    "psd_check": "PASS" if severe_negative == 0 else "FAIL",
                })
            # PCA directions use centered patch-activation covariance from the same
            # 100 images; covariance PCs are not eigenvectors of M.
            cov_evals, cov_evecs = torch.linalg.eigh(C)
            pc_bottom = cov_evecs[:, 0]
            pc1 = cov_evecs[:, -1]
            sensitivity_pc1 = float((pc1 @ M @ pc1).item())
            sensitivity_bottom = float((pc_bottom @ M @ pc_bottom).item())
            ratio = (
                sensitivity_pc1 / sensitivity_bottom
                if sensitivity_bottom > 0
                else float("nan")
            )
            denominator_threshold = 1e-10 * lambda_max
            denominator_stable = sensitivity_bottom > denominator_threshold
            rows_sensitivity.append({
                "model_key": model_key,
                "architecture": MODEL_LABELS[model_key],
                "depth": depth,
                "D": D,
                "N_img": n_img,
                "sensitivity_PC1": sensitivity_pc1,
                "sensitivity_PC_bottom": sensitivity_bottom,
                "ratio_PC1_to_PC_bottom_raw": ratio,
                "PC_bottom_over_lambda_max_M": sensitivity_bottom / lambda_max,
                "ratio_stability_threshold": denominator_threshold,
                "ratio_numerically_stable": denominator_stable,
                "covariance_min_eigenvalue": float(cov_evals[0].item()),
                "covariance_bottom_eigengap": float((cov_evals[1] - cov_evals[0]).item()),
                "covariance_bottom_eigengap_relative": float(
                    ((cov_evals[1] - cov_evals[0]) / max(abs(float(cov_evals[-1].item())), 1e-300)).item()
                ),
                "lambda_max_M": lambda_max,
            })
            for rank, value in enumerate(evals_desc.tolist(), start=1):
                rows_spectrum.append({
                    "model_key": model_key,
                    "architecture": MODEL_LABELS[model_key],
                    "depth": depth,
                    "D": D,
                    "eigenvalue_index_descending": rank,
                    "eigenvalue_raw": float(value),
                    "eigenvalue_clipped_for_entropy_cutoffs": max(0.0, float(value)),
                    "relative_to_lambda_max": float(value / lambda_max),
                })
            matrices[f"M__{model_key}__depth{depth}"] = M.numpy()
            matrices[f"covariance__{model_key}__depth{depth}"] = C.numpy()
            print(
                f"[geometry] {model_key} depth={depth} D={D} N={n_img} "
                f"near-null@1e-3={int((evals_for_cutoff <= 1e-3*lambda_max).sum())}/{D} "
                f"r_eff={effective_rank:.3f} PC ratio={ratio:.6g} "
                f"PSD={'PASS' if severe_negative == 0 else 'FAIL'}"
            )
            if DEVICE.type == "cuda":
                torch.cuda.empty_cache()

        model_metadata[model_key] = {
            "model_id": meta["model_id"],
            "readout": meta["readout"],
            "embed_dim": D,
            "num_patches": int(meta["num_patches"]),
            "elapsed_seconds": time.time() - started,
        }
        model.to("cpu")
        del model
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()

    pd.DataFrame(rows_metric).to_csv(GEOM_OUT / "functional_spectrum_robustness.csv", index=False)
    pd.DataFrame(rows_sensitivity).to_csv(GEOM_OUT / "pc_directional_sensitivity.csv", index=False)
    pd.DataFrame(rows_spectrum).to_csv(GEOM_OUT / "raw_eigenspectrum.csv", index=False)
    np.savez_compressed(GEOM_OUT / "metric_and_covariance_matrices.npz", **matrices)

    manifest = {
        "status": "PASS" if all(r["psd_check"] == "PASS" for r in rows_metric) else "FAIL",
        "device": str(DEVICE),
        "num_images": N_GEOM,
        "sample_split": "first 100 of existing calibration split",
        "split_seeds": {"calibration": 9101, "evaluation": 9201},
        "depths": list(DEPTHS),
        "models": model_metadata,
        "source": "scripts/run_section5_cross_arch_extension.py",
        "metric_definition": "mean outer product of per-image, per-patch gradient of the clean predicted-class vs clean runner-up logit margin",
        "metric_notation": "D x D margin-gradient second moment; distinct from the all-patch readout Jacobian Gram",
        "DINOv2_readout": "official linear_head on concatenated normalized CLS and mean normalized patch features",
        "covariance_definition": "centered pooled patch activation covariance from the same N_img=100 image cohort",
        "numeric_policy": {
            "accumulation_dtype": "float64",
            "eigensolver_dtype": "float64",
            "psd_tolerance_relative_to_lambda_max": 1e-10,
            "primary_near_null_cutoff": 1e-3,
            "cutoff_sensitivity_values": [1e-4, 1e-3, 1e-2],
            "ratio_denominator_instability_threshold_relative_to_lambda_max": 1e-10,
        },
        "existing_outputs_modified": False,
        "rows": {
            "functional_spectrum_robustness": len(rows_metric),
            "pc_directional_sensitivity": len(rows_sensitivity),
            "raw_eigenspectrum": len(rows_spectrum),
        },
        "git_head_at_run": git_head(),
    }
    (GEOM_OUT / "validation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def corr(x: np.ndarray, y: np.ndarray) -> tuple[float, float]:
    p = float(pearsonr(x, y).statistic)
    s = float(spearmanr(x, y).statistic)
    return p, s


def stratified_bootstrap(df: pd.DataFrame, predictor: str, rng: np.random.Generator, n_boot: int = 2000):
    df = df.reset_index(drop=True)
    groups = [
        df.loc[df["perturbation_family"] == name].index.to_numpy()
        for _, _, name in PERTURBATION_FAMILIES
    ]
    if any(len(g) != 25 for g in groups):
        raise RuntimeError("Expected exactly 25 perturbations in each frozen family.")
    draws = []
    y_all = df["logit_l2"].to_numpy(dtype=float)
    x_all = df[predictor].to_numpy(dtype=float)
    for rep in range(n_boot):
        idx = np.concatenate([rng.choice(group, size=25, replace=True) for group in groups])
        p, s = corr(x_all[idx], y_all[idx])
        draws.append({
            "bootstrap_replicate": rep,
            "predictor": predictor,
            "pearson_r": p,
            "spearman_rho": s,
        })
    return draws


def summarize_prediction(all_rows: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary_rows = []
    family_rows = []
    bootstrap_rows = []
    rng = np.random.default_rng(52026)
    predictors = {
        "single_block": "predicted_tau_single",
        "end_to_end": "predicted_tau_multi",
    }
    for model_key, frame in all_rows.groupby("model_key", sort=False):
        if len(frame) != N_PERT or frame["pert_id"].nunique() != N_PERT:
            raise RuntimeError(f"{model_key}: expected 100 unique perturbations, got {len(frame)}")
        if set(frame["scale_factor"].astype(float)) != {0.4}:
            raise RuntimeError(f"{model_key}: scale mismatch")
        if frame["perturbation_family"].value_counts().to_dict() != {
            name: 25 for _, _, name in PERTURBATION_FAMILIES
        }:
            raise RuntimeError(f"{model_key}: perturbation family counts mismatch")

        for predictor_name, column in predictors.items():
            p, s = corr(frame[column].to_numpy(float), frame["logit_l2"].to_numpy(float))
            boot = stratified_bootstrap(frame, column, rng)
            bootstrap_rows.extend([
                {
                    "model_key": model_key,
                    "architecture": MODEL_LABELS[model_key],
                    "predictor": predictor_name,
                    "bootstrap_replicate": x["bootstrap_replicate"],
                    "pearson_r": x["pearson_r"],
                    "spearman_rho": x["spearman_rho"],
                } for x in boot
            ])
            bdf = pd.DataFrame(boot)
            summary_rows.append({
                "model_key": model_key,
                "architecture": MODEL_LABELS[model_key],
                "predictor": predictor_name,
                "n_perturbations": len(frame),
                "n_reference_images": int(frame["n_reference_images"].iloc[0]),
                "scale_s": 0.4,
                "pearson_r": p,
                "pearson_ci95_low": float(bdf["pearson_r"].quantile(0.025)),
                "pearson_ci95_high": float(bdf["pearson_r"].quantile(0.975)),
                "spearman_rho": s,
                "spearman_ci95_low": float(bdf["spearman_rho"].quantile(0.025)),
                "spearman_ci95_high": float(bdf["spearman_rho"].quantile(0.975)),
                "interval_method": "stratified percentile bootstrap, 2,000 replicates, 25 resamples within each of four perturbation families",
                "inference_unit": "perturbation vector; not image or token",
            })
            for _, _, family in PERTURBATION_FAMILIES:
                sub = frame.loc[frame["perturbation_family"] == family]
                pf, sf = corr(sub[column].to_numpy(float), sub["logit_l2"].to_numpy(float))
                family_rows.append({
                    "model_key": model_key,
                    "architecture": MODEL_LABELS[model_key],
                    "predictor": predictor_name,
                    "perturbation_family": family,
                    "n_perturbations": len(sub),
                    "pearson_r": pf,
                    "spearman_rho": sf,
                    "interpretation": "descriptive within-family check; n=25",
                })
    return pd.DataFrame(summary_rows), pd.DataFrame(family_rows), pd.DataFrame(bootstrap_rows)


def multiblock_prediction_extension(calib_ds, calib_manifest) -> dict:
    PRED_OUT.mkdir(parents=True, exist_ok=True)
    calib_manifest.iloc[:N_PRED_IMAGES][["sample_id", "global_index"]].to_csv(
        PRED_OUT / "calibration_reference_image_ids.csv", index=False
    )
    raw_frames = []

    # Reuse the existing small-model raw rows exactly; only add audit labels in the
    # new derived file, leaving its original source file untouched.
    small_path = ROOT / "outputs" / "fungibility_multiblock_operator" / "random_prediction.csv"
    small = pd.read_csv(small_path)
    if len(small) != N_PERT or small["pert_id"].nunique() != N_PERT:
        raise RuntimeError("Existing DeiT-Small prediction cohort does not match the frozen N=100 protocol.")
    small["model_key"] = "deit_small"
    small["architecture"] = MODEL_LABELS["deit_small"]
    small["depth"] = 8
    small["n_reference_images"] = N_PRED_IMAGES
    small["linearization_image_global_index"] = int(calib_manifest.iloc[0]["global_index"])
    small["perturbation_family"] = small["pert_id"].astype(int).map(family_for_id)
    raw_frames.append(small)

    model_metadata = {}
    for model_key in PRED_MODELS:
        started = time.time()
        model, transform, meta = load_model_for_audit(model_key, DEVICE)
        model.eval()
        for p in model.parameters():
            p.requires_grad_(False)
        calib_ds.transform = transform
        loader = make_loader(calib_ds, N_PRED_IMAGES, N_PRED_IMAGES)
        images, _labels = next(iter(loader))
        images = images.to(DEVICE)
        with torch.no_grad():
            clean_logits, collected = forward_block_by_block(
                model, model_key, x=images, start_depth=0, collect_depths=tuple(range(8, 13))
            )
            h_clean = collected[8]
        op_single = construct_full_operator(model, model_key, 8, h_clean, DEVICE)
        op_multi = construct_downstream_jacobian(model, model_key, 8, h_clean, DEVICE)
        pred = evaluate_heldout_prediction(
            model, model_key, 8, clean_logits, h_clean, op_multi, op_single,
            _labels.to(DEVICE), DEVICE, M=N_PERT, seed=42
        )
        pred["model_key"] = model_key
        pred["architecture"] = MODEL_LABELS[model_key]
        pred["depth"] = 8
        pred["n_reference_images"] = N_PRED_IMAGES
        pred["linearization_image_global_index"] = int(calib_manifest.iloc[0]["global_index"])
        pred["perturbation_family"] = pred["pert_id"].astype(int).map(family_for_id)
        if len(pred) != N_PERT or pred["pert_id"].nunique() != N_PERT:
            raise RuntimeError(f"{model_key}: expected 100 perturbations")
        if float(pred["scale_factor"].iloc[0]) != 0.4:
            raise RuntimeError(f"{model_key}: expected scale 0.4")
        raw_frames.append(pred)
        model_metadata[model_key] = {
            "model_id": meta["model_id"],
            "depth": 8,
            "readout": "DINO official CLS+mean-patch normalized readout" if model_key == "dinov2" else "normalized CLS readout",
            "D_readout": int(op_multi["D_readout"]),
            "N_patches": int(op_multi["N"]),
            "N_reference_images": N_PRED_IMAGES,
            "N_perturbations": len(pred),
            "scale_s": 0.4,
            "elapsed_seconds": time.time() - started,
            "linearization_image_global_index": int(calib_manifest.iloc[0]["global_index"]),
        }
        model.to("cpu")
        del model, images, clean_logits, collected, h_clean, op_single, op_multi, pred, loader
        if DEVICE.type == "cuda":
            torch.cuda.empty_cache()
        print(f"[multiblock-prediction] {model_key} complete")

    raw = pd.concat(raw_frames, ignore_index=True)
    raw.to_csv(PRED_OUT / "per_perturbation_results.csv", index=False)
    summary, families, boot = summarize_prediction(raw)
    summary.to_csv(PRED_OUT / "model_specific_correlations.csv", index=False)
    families.to_csv(PRED_OUT / "within_family_correlations.csv", index=False)
    boot.to_csv(PRED_OUT / "stratified_bootstrap_correlations.csv", index=False)

    manifest = {
        "status": "PASS" if len(raw) == 4 * N_PERT else "FAIL",
        "device": str(DEVICE),
        "models": {
            "deit_small": {
                "source": "existing outputs/fungibility_multiblock_operator/random_prediction.csv",
                "reused_without_rerun": True,
                "depth": 8,
                "N_reference_images": N_PRED_IMAGES,
                "N_perturbations": N_PERT,
                "scale_s": 0.4,
            },
            **model_metadata,
        },
        "calibration_split_seeds": {"calibration": 9101, "evaluation": 9201},
        "prediction_metrics": "Pearson and Spearman between ||A_8 DeltaP|| or ||J_8_to_L DeltaP|| and observed final-logit L2 change",
        "perturbation_families": {name: 25 for _, _, name in PERTURBATION_FAMILIES},
        "bootstrap": {
            "replicates": 2000,
            "seed": 52026,
            "method": "stratified percentile bootstrap; resample 25 perturbations within each family",
            "confidence_level": 0.95,
        },
        "unit_and_limit": "100 designed perturbation vectors per architecture, each evaluated on the same 20-image calibration reference batch; vectors are the correlation unit, not images/tokens. J is linearized at the first image.",
        "existing_outputs_modified": False,
        "git_head_at_run": git_head(),
        "rows": {
            "per_perturbation_results": len(raw),
            "model_specific_correlations": len(summary),
            "within_family_correlations": len(families),
            "stratified_bootstrap_correlations": len(boot),
        },
    }
    (PRED_OUT / "validation_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def summarize_existing_prediction_files() -> dict:
    """Aggregate the already-saved 400 perturbation outcomes; do not rerun models."""
    raw_path = PRED_OUT / "per_perturbation_results.csv"
    if not raw_path.is_file():
        raise FileNotFoundError(raw_path)
    raw = pd.read_csv(raw_path)
    expected_models = {"deit_small", "deit_tiny", "vit_base", "dinov2"}
    if set(raw["model_key"].unique()) != expected_models:
        raise RuntimeError(f"Unexpected model set in saved rows: {set(raw['model_key'].unique())}")
    summary, families, boot = summarize_prediction(raw)
    summary.to_csv(PRED_OUT / "model_specific_correlations.csv", index=False)
    families.to_csv(PRED_OUT / "within_family_correlations.csv", index=False)
    boot.to_csv(PRED_OUT / "stratified_bootstrap_correlations.csv", index=False)

    model_ids = {
        "deit_tiny": "deit_tiny_patch16_224",
        "deit_small": "deit_small_patch16_224",
        "vit_base": "vit_base_patch16_224.augreg_in1k",
        "dinov2": "dinov2_vits14_lc",
    }
    models = {}
    for model_key, frame in raw.groupby("model_key", sort=False):
        if len(frame) != N_PERT or frame["pert_id"].nunique() != N_PERT:
            raise RuntimeError(f"{model_key}: incomplete saved perturbation outcomes")
        models[model_key] = {
            "model_id": model_ids[model_key],
            "depth": 8,
            "readout": "official CLS+mean-patch linear readout" if model_key == "dinov2" else "normalized CLS readout",
            "D_readout": 768 if model_key == "dinov2" else {"deit_tiny": 192, "deit_small": 384, "vit_base": 768}[model_key],
            "N_patches": 256 if model_key == "dinov2" else 196,
            "N_reference_images": int(frame["n_reference_images"].iloc[0]),
            "N_perturbations": len(frame),
            "scale_s": float(frame["scale_factor"].iloc[0]),
            "linearization_image_global_index": int(frame["linearization_image_global_index"].iloc[0]),
        }
    prediction_manifest = {
        "status": "PASS",
        "device": str(DEVICE),
        "models": models,
        "calibration_split_seeds": {"calibration": 9101, "evaluation": 9201},
        "prediction_metrics": "Pearson and Spearman between ||A_8 DeltaP|| or ||J_8_to_L DeltaP|| and observed final-logit L2 change",
        "perturbation_families": {name: 25 for _, _, name in PERTURBATION_FAMILIES},
        "bootstrap": {
            "replicates": 2000,
            "seed": 52026,
            "method": "stratified percentile bootstrap; resample 25 perturbations within each family",
            "confidence_level": 0.95,
        },
        "unit_and_limit": "100 designed perturbation vectors per architecture, each evaluated on the same 20-image calibration reference batch; vectors are the correlation unit, not images/tokens. J is linearized at the first image.",
        "existing_outputs_modified": False,
        "git_head_at_run": git_head(),
        "rows": {
            "per_perturbation_results": len(raw),
            "model_specific_correlations": len(summary),
            "within_family_correlations": len(families),
            "stratified_bootstrap_correlations": len(boot),
        },
    }
    (PRED_OUT / "validation_manifest.json").write_text(
        json.dumps(prediction_manifest, indent=2), encoding="utf-8"
    )
    geom_path = GEOM_OUT / "validation_manifest.json"
    geom = json.loads(geom_path.read_text(encoding="utf-8"))
    overall = {
        "status": "PASS" if geom["status"] == "PASS" and prediction_manifest["status"] == "PASS" else "FAIL",
        "device": str(DEVICE),
        "git_head_at_run": git_head(),
        "functional_geometry": geom,
        "multiblock_prediction": prediction_manifest,
        "existing_outputs_modified": False,
    }
    (OUT / "validation_manifest.json").write_text(json.dumps(overall, indent=2), encoding="utf-8")
    print(summary.to_string(index=False))
    print("Saved summaries from the existing 400-row output; no models were rerun.")
    return overall

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--summarize-existing-predictions", action="store_true")
    args = parser.parse_args()
    if args.summarize_existing_predictions:
        summarize_existing_prediction_files()
        return
    if DEVICE.type != "cuda":
        raise RuntimeError("Frozen protocol expects the available CUDA device; no CPU fallback was authorized.")
    torch.set_num_threads(4)
    torch.manual_seed(42)
    OUT.mkdir(parents=True, exist_ok=True)
    calib_ds, _eval_ds, calib_manifest, _eval_manifest = get_disjoint_imagenet_splits()
    (OUT / "calibration_split_seed_metadata.json").write_text(json.dumps({
        "calibration_seed": 9101,
        "evaluation_seed": 9201,
        "calibration_size": len(calib_ds),
        "evaluation_size": len(_eval_ds),
        "same_first_100_calibration_ids_for_geometry": True,
        "same_first_20_calibration_ids_for_multiblock": True,
    }, indent=2), encoding="utf-8")

    print(f"Device: {DEVICE} ({torch.cuda.get_device_name(0)})")
    print("Starting frozen functional-geometry extension.")
    geom = geometry_extension(calib_ds, calib_manifest)
    if geom["status"] != "PASS":
        raise RuntimeError("Functional-geometry numerical validation failed.")
    print("Starting frozen model-specific multiblock prediction extension.")
    pred = multiblock_prediction_extension(calib_ds, calib_manifest)
    if pred["status"] != "PASS":
        raise RuntimeError("Model-specific multiblock prediction validation failed.")
    (OUT / "validation_manifest.json").write_text(json.dumps({
        "status": "PASS",
        "device": str(DEVICE),
        "git_head_at_run": git_head(),
        "functional_geometry": geom,
        "multiblock_prediction": pred,
        "existing_outputs_modified": False,
    }, indent=2), encoding="utf-8")
    print("Section 5 extension complete.")
    print(f"Outputs: {OUT}")


if __name__ == "__main__":
    main()







