"""Run an isolated depth-6 follow-up to the audited V1 25% replacement sweep.

This script writes only to outputs/fungibility_v1_depth6_followup/ and leaves
the original V1 outputs untouched. It reuses the original split seeds,
preprocessing, intervention mask, and replacement conditions.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader

from patch_fungibility.v0_6_dataset import get_disjoint_imagenet_splits, ParquetImageSubset
from patch_fungibility.v1_interventions import build_nested_masks, compute_calibration_statistics, PatchInterventionHook
from patch_fungibility.v1_models import get_vitb_model, get_dinov2_model, forward_vitb_manual, forward_dinov2_manual
from patch_fungibility.v1_pipeline import evaluate_condition_from_cache


DEPTH = 6
SEEDS = (22001, 22002, 22003)
OUT = Path("outputs/fungibility_v1_depth6_followup")


def extract_depth(model, loader, model_type: str, device: torch.device):
    forward_fn = forward_vitb_manual if model_type == "vitb" else forward_dinov2_manual
    hidden, labels = [], []
    with torch.inference_mode():
        for images, ys in loader:
            _, collected = forward_fn(model, x=images.to(device), collect_depths=(DEPTH,))
            hidden.append(collected[DEPTH].cpu())
            labels.append(ys.cpu())
    return torch.cat(hidden), torch.cat(labels)


def run_model(model_name: str, model_type: str, model, transform, calib_samples, eval_samples,
              device: torch.device, batch_size: int, mask: np.ndarray):
    calib_loader = DataLoader(ParquetImageSubset(calib_samples, transform), batch_size=batch_size, shuffle=False)
    eval_loader = DataLoader(ParquetImageSubset(eval_samples, transform), batch_size=batch_size, shuffle=False)
    calib_h, _ = extract_depth(model, calib_loader, model_type, device)
    eval_h, labels = extract_depth(model, eval_loader, model_type, device)
    stats = compute_calibration_statistics({DEPTH: calib_h[:, 1:, :]})
    mu = stats[f"mu_{DEPTH}"]
    sigma = stats[f"sigma_{DEPTH}"]
    batch_forward = min(batch_size, 64)

    rows = []
    per_image = []

    def evaluate(condition: str, seed: int | None, hook: PatchInterventionHook | None):
        _, frame = evaluate_condition_from_cache(
            model, model_type, start_depth=DEPTH, cached_h_start=eval_h,
            labels=labels, hook=hook, batch_size=batch_forward, device=device
        )
        frame.insert(1, "condition", condition)
        frame.insert(2, "depth", DEPTH)
        frame.insert(3, "seed", seed)
        per_image.append(frame)
        rows.append({
            "depth": DEPTH,
            "condition": condition,
            "seed": seed,
            "top1_accuracy": float(frame["correctness"].mean()),
            "mean_margin": float(frame["true_class_margin"].mean()),
            "median_margin": float(frame["true_class_margin"].median()),
            "margin_damage": float((frame["true_class_margin"].mean() -
                                     frame["true_class_margin"].mean())),
            "corr_to_incorr": int(((frame["correctness"] == 0)).sum()),
            "incorr_to_corr": 0,
        })
        return frame

    clean = evaluate("CLEAN", None, None)
    clean_correct = clean["correctness"].to_numpy()
    clean_margin = clean["true_class_margin"].to_numpy()
    rows[-1]["corr_to_incorr"] = 0

    def run_condition(condition: str, seed: int | None, hook: PatchInterventionHook):
        frame = evaluate(condition, seed, hook)
        margin_damage = clean_margin - frame["true_class_margin"].to_numpy()
        frame["margin_damage_vs_clean"] = margin_damage
        frame["flip_corr_to_incorr"] = ((clean_correct == 1) & (frame["correctness"].to_numpy() == 0)).astype(int)
        frame["flip_incorr_to_corr"] = ((clean_correct == 0) & (frame["correctness"].to_numpy() == 1)).astype(int)
        row = rows[-1]
        row["mean_margin"] = float(frame["true_class_margin"].mean())
        row["median_margin"] = float(frame["true_class_margin"].median())
        row["margin_damage"] = float(margin_damage.mean())
        row["corr_to_incorr"] = int(frame["flip_corr_to_incorr"].sum())
        row["incorr_to_corr"] = int(frame["flip_incorr_to_corr"].sum())

    for cond, seed in (("ZERO", None), ("CENTROID", None)):
        hook = PatchInterventionHook(DEPTH, mask, cond, mu=mu if cond == "CENTROID" else None, device=device)
        run_condition(cond, seed, hook)
    for seed in SEEDS:
        hook = PatchInterventionHook(DEPTH, mask, "DIAGONAL_GAUSSIAN", mu=mu, sigma=sigma, seed=seed, device=device)
        run_condition("DIAGONAL_GAUSSIAN", seed, hook)

    OUT.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(OUT / f"{model_type}_depth6_results.csv", index=False)
    pd.concat(per_image, ignore_index=True).to_csv(OUT / f"{model_type}_depth6_per_image.csv", index=False)
    print(f"{model_name}: clean={rows[0]['top1_accuracy']:.4f}; " + "; ".join(
        f"{r['condition']}{'_'+str(r['seed']) if r['seed'] else ''}={r['top1_accuracy']:.4f}"
        for r in rows[1:]
    ), flush=True)
    return rows


def main():
    started = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    calib_ds, eval_ds, calib_manifest, eval_manifest = get_disjoint_imagenet_splits(
        calib_seed=9101, eval_seed=9201, n_per_split=1000
    )
    calib_samples, eval_samples = calib_ds._samples, eval_ds._samples
    calib_manifest.to_csv(OUT / "calibration_split.csv", index=False)
    eval_manifest.to_csv(OUT / "evaluation_split.csv", index=False)
    metadata = {
        "study": "post hoc depth-6 follow-up to V1 25% patch replacement sweep",
        "depth": DEPTH,
        "evaluation_images_per_architecture": len(eval_samples),
        "calibration_images_per_architecture": len(calib_samples),
        "split_seeds": {"calibration": 9101, "evaluation": 9201},
        "conditions": ["CLEAN", "ZERO", "CENTROID", "DIAGONAL_GAUSSIAN"],
        "gaussian_seeds": list(SEEDS),
        "replacement_fraction": 0.25,
        "mask_seed": 21001,
        "device": str(device),
        "output_directory": str(OUT),
        "original_v1_results_modified": False,
    }
    (OUT / "followup_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")

    mask_vitb = build_nested_masks(196, seed=21001)[0.25]
    mask_dino = build_nested_masks(256, seed=21001)[0.25]
    all_rows = {}
    print(f"Device: {device}; calibration/evaluation N={len(calib_samples)} each; isolated output: {OUT}", flush=True)
    model, transform, _ = get_vitb_model(device)
    all_rows["vitb"] = run_model("ViT-B/16 AugReg", "vitb", model, transform, calib_samples, eval_samples,
                                  device, 16, mask_vitb)
    del model
    if device.type == "cuda":
        torch.cuda.empty_cache()
    model, transform, _ = get_dinov2_model(device)
    all_rows["dinov2"] = run_model("DINOv2 ViT-S/14", "dinov2", model, transform, calib_samples, eval_samples,
                                   device, 32, mask_dino)
    metadata["elapsed_seconds"] = round(time.time() - started, 2)
    (OUT / "followup_manifest.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    print(f"Completed depth-6 follow-up in {metadata['elapsed_seconds']:.1f}s", flush=True)


if __name__ == "__main__":
    main()
