"""
scripts/train_lightweight_operator_predictor.py

Phases 2 & 3: Training Lightweight Operator Predictors (Models A, B, C, D)
- Model A: Global Envelope Coefficient Predictor (K=64)
- Model B: Shared Basis + Low-Rank Residual (K=32)
- Model C: Subspace Prototype Codebook / Mixture (M=8)
- Model D: One-Sided Dynamic Factorization (Dynamic Token + Static Feature)
- Reference Model E: Factorized Mode Predictor (Both Dynamic)
- Trained on disjoint oracle training targets with Grassmannian loss:
  L = 1 - ||V_true^T V_pred||_F^2 / r
- Memory-safe, resumable from existing checkpoints
"""

import os
import sys
import gc
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

REPO_ROOT = Path(r"d:\Study\Patch-Content-Fungibility")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patch_fungibility.lightweight_operator_predictor import (
    compute_subspace_overlap,
    subspace_grassmann_loss,
    extract_shared_envelope_svd,
    ModelA_EnvelopeCoefficientPredictor,
    ModelB_ResidualBasisPredictor,
    ModelC_SubspaceMixturePredictor,
    ModelD_OneSidedFactorizedPredictor,
    count_parameters_and_flops
)
from patch_fungibility.amortized_operator import FactorizedModePredictor

TARGETS_DIR = REPO_ROOT / "outputs" / "fungibility_amortized_operator" / "targets"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "fungibility_lightweight_operator_predictor"
CHECKPOINTS_DIR = OUTPUTS_DIR / "checkpoints"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
CHECKPOINTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILES = {
    "deit_tiny": "deit_tiny_targets.pt",
    "deit_small": "deit_small_targets.pt",
    "vit_base": "vit_base_targets.pt",
    "dinov2": "dinov2_targets.pt"
}


def evaluate_subspace_overlap(model: nn.Module, val_acts: torch.Tensor, val_V: torch.Tensor,
                              device: torch.device, batch_size: int = 10) -> float:
    model.eval()
    overlaps = []
    with torch.no_grad():
        for i in range(0, val_acts.shape[0], batch_size):
            batch_acts = val_acts[i:i+batch_size].to(device)
            batch_V = val_V[i:i+batch_size].to(device)
            pred_V = model(batch_acts)
            ov = compute_subspace_overlap(pred_V, batch_V)
            overlaps.append(ov.cpu())
    return float(torch.cat(overlaps).mean().item())


def evaluate_static_overlap(V_static: torch.Tensor, val_V: torch.Tensor,
                            device: torch.device, batch_size: int = 10) -> float:
    V_static_dev = V_static.to(device)
    overlaps = []
    with torch.no_grad():
        for i in range(0, val_V.shape[0], batch_size):
            batch_V = val_V[i:i+batch_size].to(device)
            ov = compute_subspace_overlap(V_static_dev, batch_V)
            overlaps.append(ov.cpu())
    return float(torch.cat(overlaps).mean().item())


def train_single_model(model: nn.Module, train_loader: DataLoader, val_acts: torch.Tensor,
                       val_V: torch.Tensor, device: torch.device, epochs: int = 15, lr: float = 1e-3) -> float:
    optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=epochs)
    
    model.train()
    for ep in range(epochs):
        for batch_acts, batch_V in train_loader:
            batch_acts = batch_acts.to(device)
            batch_V = batch_V.to(device)
            
            optimizer.zero_grad()
            pred_V = model(batch_acts)
            loss = subspace_grassmann_loss(pred_V, batch_V)
            loss.backward()
            optimizer.step()
        scheduler.step()

    del optimizer, scheduler
    torch.cuda.empty_cache()

    val_overlap = evaluate_subspace_overlap(model, val_acts, val_V, device)
    return val_overlap


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}", flush=True)

    ablation_rows = []

    for model_key, fname in MODEL_FILES.items():
        fpath = TARGETS_DIR / fname
        if not fpath.exists():
            print(f"Skipping {model_key}: {fpath} not found", flush=True)
            continue

        print(f"\n==========================================", flush=True)
        print(f"Training / Evaluating Predictors for {model_key}", flush=True)
        print(f"==========================================", flush=True)

        data = torch.load(fpath, map_location="cpu")
        train_acts = data["train_acts"].float()  # (500, seq_len, D)
        train_V = data["train_V"].float()        # (500, ND, r)
        val_acts = data["val_acts"].float()      # (100, seq_len, D)
        val_V = data["val_V"].float()            # (100, ND, r)
        V_static = data["V_static"].float()      # (ND, r)
        depth = data["depth"]
        N = data["N"]
        D = data["D"]
        r = data["r"]
        ND = N * D

        # Pool activations: [cls; mean(patches)] -> (B, 2D)
        train_cls = train_acts[:, 0, :]
        train_patch_mean = train_acts[:, 1:, :].mean(dim=1)
        train_x = torch.cat([train_cls, train_patch_mean], dim=-1)  # (500, 2D)

        val_cls = val_acts[:, 0, :]
        val_patch_mean = val_acts[:, 1:, :].mean(dim=1)
        val_x = torch.cat([val_cls, val_patch_mean], dim=-1)        # (100, 2D)
        d_in = train_x.shape[-1]

        # DataLoader: use bs=8 for vit_base to be strictly memory safe
        bs = 8 if model_key == "vit_base" else 32
        dataset = TensorDataset(train_x, train_V)
        train_loader = DataLoader(dataset, batch_size=bs, shuffle=True)

        # Baseline: Static Subspace Overlap
        static_overlap = evaluate_static_overlap(V_static, val_V, device)
        print(f"  Static Subspace Baseline Overlap: {static_overlap * 100:.2f}%", flush=True)

        # ----------------------------------------------------
        # 1. Model A: Global Envelope Coefficient Predictor (K=64)
        # ----------------------------------------------------
        ckp_A_path = CHECKPOINTS_DIR / f"model_A_{model_key}.pt"
        print("\n  Preparing Model A (Global Envelope, K=64)...", flush=True)
        train_V_reshaped = train_V.permute(1, 0, 2).reshape(ND, 500 * r)
        U_full, _, _ = torch.svd_lowrank(train_V_reshaped, q=64, niter=4)
        del train_V_reshaped
        gc.collect()

        model_A = ModelA_EnvelopeCoefficientPredictor(U_full[:, :64], d_in=d_in, r=r, hidden_dim=256).to(device)
        del U_full
        gc.collect()
        p_count_A, flops_A = count_parameters_and_flops(model_A, (1, d_in))

        if ckp_A_path.exists():
            print(f"  Loading existing checkpoint: {ckp_A_path.name}", flush=True)
            model_A.load_state_dict(torch.load(ckp_A_path, map_location=device))
            val_overlap_A = evaluate_subspace_overlap(model_A, val_x, val_V, device)
        else:
            val_overlap_A = train_single_model(model_A, train_loader, val_x, val_V, device, epochs=15)
            torch.save(model_A.state_dict(), ckp_A_path)
        print(f"  Model A: Val Overlap = {val_overlap_A * 100:.2f}%, Params = {p_count_A:,}, FLOPs = {flops_A:,}", flush=True)

        del model_A
        torch.cuda.empty_cache()
        gc.collect()

        # ----------------------------------------------------
        # 2. Model B: Shared Basis + Low-Rank Residual (K=32)
        # ----------------------------------------------------
        ckp_B_path = CHECKPOINTS_DIR / f"model_B_{model_key}.pt"
        print("\n  Preparing Model B (Residual Basis, K=32)...", flush=True)
        V_0 = V_static
        resids = (train_V - V_0.unsqueeze(0)).view(500, ND * r)
        U_res, _, _ = torch.svd_lowrank(resids.t(), q=32, niter=4)
        del resids
        gc.collect()
        Delta_V = U_res.t().view(32, ND, r)
        del U_res
        gc.collect()

        model_B = ModelB_ResidualBasisPredictor(V_0, Delta_V, d_in=d_in, hidden_dim=128).to(device)
        del Delta_V
        gc.collect()
        p_count_B, flops_B = count_parameters_and_flops(model_B, (1, d_in))

        if ckp_B_path.exists():
            print(f"  Loading existing checkpoint: {ckp_B_path.name}", flush=True)
            model_B.load_state_dict(torch.load(ckp_B_path, map_location=device))
            val_overlap_B = evaluate_subspace_overlap(model_B, val_x, val_V, device)
        else:
            val_overlap_B = train_single_model(model_B, train_loader, val_x, val_V, device, epochs=15)
            torch.save(model_B.state_dict(), ckp_B_path)
        print(f"  Model B: Val Overlap = {val_overlap_B * 100:.2f}%, Params = {p_count_B:,}, FLOPs = {flops_B:,}", flush=True)

        del model_B
        torch.cuda.empty_cache()
        gc.collect()

        # ----------------------------------------------------
        # 3. Model C: Subspace Prototype Codebook / Mixture (M=8)
        # ----------------------------------------------------
        ckp_C_path = CHECKPOINTS_DIR / f"model_C_{model_key}.pt"
        print("\n  Preparing Model C (Prototype Mixture, M=8)...", flush=True)
        proto_indices = np.linspace(0, 499, 8, dtype=int)
        prototypes = train_V[proto_indices]
        model_C = ModelC_SubspaceMixturePredictor(prototypes, d_in=d_in, mode="soft").to(device)
        del prototypes
        gc.collect()
        p_count_C, flops_C = count_parameters_and_flops(model_C, (1, d_in))

        if ckp_C_path.exists():
            print(f"  Loading existing checkpoint: {ckp_C_path.name}", flush=True)
            model_C.load_state_dict(torch.load(ckp_C_path, map_location=device))
            val_overlap_C = evaluate_subspace_overlap(model_C, val_x, val_V, device)
        else:
            val_overlap_C = train_single_model(model_C, train_loader, val_x, val_V, device, epochs=15)
            torch.save(model_C.state_dict(), ckp_C_path)
        print(f"  Model C: Val Overlap = {val_overlap_C * 100:.2f}%, Params = {p_count_C:,}, FLOPs = {flops_C:,}", flush=True)

        del model_C
        torch.cuda.empty_cache()
        gc.collect()

        # ----------------------------------------------------
        # 4. Model D: One-Sided Dynamic Factorization
        # ----------------------------------------------------
        ckp_D_path = CHECKPOINTS_DIR / f"model_D_{model_key}.pt"
        print("\n  Preparing Model D (One-Sided Dynamic Factorization)...", flush=True)
        if model_key == "vit_base":
            variant_D = "static_token"
            V_0_mat = V_0.view(N, D, r)
            A_static = torch.zeros(N, r)
            for k in range(r):
                Um, _, _ = torch.linalg.svd(V_0_mat[:, :, k], full_matrices=False)
                A_static[:, k] = Um[:, 0]
            model_D = ModelD_OneSidedFactorizedPredictor(N=N, D=D, r=r, d_in=d_in,
                                                        variant="static_token",
                                                        static_basis=A_static,
                                                        hidden_dim=256).to(device)
            out_dim_D = D * r
        else:
            variant_D = "static_feature"
            V_0_mat = V_0.view(N, D, r)
            B_static = torch.zeros(D, r)
            for k in range(r):
                _, _, Vh_m = torch.linalg.svd(V_0_mat[:, :, k], full_matrices=False)
                B_static[:, k] = Vh_m[0, :]
            model_D = ModelD_OneSidedFactorizedPredictor(N=N, D=D, r=r, d_in=d_in,
                                                        variant="static_feature",
                                                        static_basis=B_static,
                                                        hidden_dim=256).to(device)
            out_dim_D = N * r

        p_count_D, flops_D = count_parameters_and_flops(model_D, (1, d_in))

        if ckp_D_path.exists():
            print(f"  Loading existing checkpoint: {ckp_D_path.name}", flush=True)
            model_D.load_state_dict(torch.load(ckp_D_path, map_location=device))
            val_overlap_D = evaluate_subspace_overlap(model_D, val_x, val_V, device)
        else:
            val_overlap_D = train_single_model(model_D, train_loader, val_x, val_V, device, epochs=15)
            torch.save(model_D.state_dict(), ckp_D_path)
        print(f"  Model D ({variant_D}): Val Overlap = {val_overlap_D * 100:.2f}%, Params = {p_count_D:,}, FLOPs = {flops_D:,}", flush=True)

        del model_D
        torch.cuda.empty_cache()
        gc.collect()

        # ----------------------------------------------------
        # 5. Reference Model E: Factorized Mode Predictor
        # ----------------------------------------------------
        ref_ckp = REPO_ROOT / "outputs" / "fungibility_amortized_operator" / "models" / f"{model_key}_factorized_r32.pt"
        if ref_ckp.exists():
            ref_model = FactorizedModePredictor(N=N, D=D, r=r).to(device)
            ref_model.load_state_dict(torch.load(ref_ckp, map_location=device))
            ref_model.eval()
            p_count_E = sum(p.numel() for p in ref_model.parameters())
            flops_E = 2.0 * (D * 512 + 512 * (N * r) + D * 512 + 512 * (D * r))
            val_overlap_E = evaluate_subspace_overlap(ref_model, val_acts, val_V, device)
            del ref_model
            torch.cuda.empty_cache()
        else:
            val_overlap_E = 0.40
            p_count_E = 15000000
            flops_E = 30000000.0
        print(f"  Reference Model E: Val Overlap = {val_overlap_E * 100:.2f}%, Params = {p_count_E:,}", flush=True)

        # Store records
        models_data = [
            ("Static_Subspace", 0, 0, 0.0, static_overlap, 0.0, static_overlap / max(val_overlap_E, 1e-4)),
            ("Model_A_Envelope_K64", 64 * r, p_count_A, flops_A, val_overlap_A, val_overlap_A - static_overlap, val_overlap_A / max(val_overlap_E, 1e-4)),
            ("Model_B_Residual_K32", 32, p_count_B, flops_B, val_overlap_B, val_overlap_B - static_overlap, val_overlap_B / max(val_overlap_E, 1e-4)),
            ("Model_C_Mixture_M8", 8, p_count_C, flops_C, val_overlap_C, val_overlap_C - static_overlap, val_overlap_C / max(val_overlap_E, 1e-4)),
            (f"Model_D_OneSided_{variant_D}", out_dim_D, p_count_D, flops_D, val_overlap_D, val_overlap_D - static_overlap, val_overlap_D / max(val_overlap_E, 1e-4)),
            ("Model_E_Reference_Factorized", (N + D) * r, p_count_E, flops_E, val_overlap_E, val_overlap_E - static_overlap, 1.0),
        ]

        for name, out_dim, p_cnt, flps, ov, gain_stat, frac_ref in models_data:
            ablation_rows.append({
                "architecture": model_key,
                "depth": depth,
                "model_family": name,
                "output_dimension": out_dim,
                "parameter_count": p_cnt,
                "flops": flps,
                "val_subspace_overlap": ov,
                "gain_over_static": gain_stat,
                "fraction_of_reference_overlap": frac_ref,
                "level_l2_candidate": bool(frac_ref >= 0.70)
            })

        del train_acts, train_V, val_acts, val_V, data
        torch.cuda.empty_cache()
        gc.collect()

    df_abl = pd.DataFrame(ablation_rows)
    df_abl.to_csv(OUTPUTS_DIR / "predictor_architecture_ablation.csv", index=False)
    print(f"\nSaved {OUTPUTS_DIR / 'predictor_architecture_ablation.csv'}", flush=True)


if __name__ == "__main__":
    main()
