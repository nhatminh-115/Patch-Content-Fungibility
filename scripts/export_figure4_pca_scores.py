#!/usr/bin/env python3
"""Export actual PC1/bottom-PC patch scores for the Figure 4 PCA map.

Forward-only visualization data from the same first 100 calibration images and
model path used by the functional-geometry pilot. This does not compute Jacobians,
run perturbations, or alter the audited outputs under outputs/.
"""
from __future__ import annotations

import csv
import os
import sys
import time
from pathlib import Path

import torch
from torch.utils.data import DataLoader, Subset

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from patch_fungibility.dense_fraction_models import load_model_and_transform, forward_block_by_block
from patch_fungibility.v0_6_dataset import get_disjoint_imagenet_splits

N_IMAGES = 100
DEPTH = 8
MODELS = ("deit_small", "vit_base")
OUTPUT = ROOT / "figures/paper_final_v4/source/figure4_pca_scores.csv"


def main() -> None:
    started = time.time()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    calib_ds, _, _, _ = get_disjoint_imagenet_splits()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["model_key", "depth", "image_index_within_pilot", "patch_index", "pc1_score", "pc_bottom_score"])
        for model_key in MODELS:
            model, transform, meta = load_model_and_transform(model_key, device)
            calib_ds.transform = transform
            subset = Subset(calib_ds, list(range(N_IMAGES)))
            loader = DataLoader(subset, batch_size=25, shuffle=False)
            images = torch.cat([batch for batch, _ in loader], dim=0).to(device)
            with torch.no_grad():
                _, collected = forward_block_by_block(model, model_key, x=images, collect_depths=(DEPTH,))
                patches = collected[DEPTH][:, 1:, :].reshape(-1, meta["embed_dim"]).to(torch.float64)
                centered = patches - patches.mean(dim=0)
                covariance = ((centered.T @ centered) / (patches.shape[0] - 1)).float()
                eigenvalues, eigenvectors = torch.linalg.eigh(covariance)
                order = torch.argsort(eigenvalues, descending=True)
                eigenvectors = eigenvectors[:, order]
                # Canonicalize signs so regenerated maps use stable orientations.
                for column in (0, eigenvectors.shape[1] - 1):
                    vector = eigenvectors[:, column]
                    pivot = int(torch.argmax(torch.abs(vector)).item())
                    if vector[pivot] < 0:
                        eigenvectors[:, column] *= -1
                scores = centered.float() @ eigenvectors[:, [0, -1]]
                scores = scores.cpu().numpy()
                patch_count = meta["num_patches"]
                for flat_index, (pc1, pc_bottom) in enumerate(scores):
                    writer.writerow([model_key, DEPTH, flat_index // patch_count, flat_index % patch_count,
                                     f"{pc1:.9g}", f"{pc_bottom:.9g}"])
            del model, images, patches, centered, covariance, eigenvalues, eigenvectors, scores
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    print(f"Saved PC scores for {N_IMAGES} pilot images/model to {OUTPUT} in {time.time() - started:.2f}s on {device}.")


if __name__ == "__main__":
    main()
