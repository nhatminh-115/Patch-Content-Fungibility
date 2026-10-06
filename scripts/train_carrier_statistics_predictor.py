"""
scripts/train_carrier_statistics_predictor.py

Phases 5 & 6: Distillation of Sufficient Statistics for Carrier Correction
Compares 4 predictor parameterizations:
- Option A: Predict g_q only (out_dim=q) with calibrated static H_bar
- Option B: Predict diag(H_q) + g_q (out_dim=2q)
- Option C: Predict full Cholesky L_q + g_q (out_dim=q(q+1)/2 + q)
- Option D: Predict alpha* directly (out_dim=q)

Evaluates:
- Parameter count, FLOPs, output dimension
- Relative prediction MSE on test set
- Downstream ||JE|| transmission error recovery
- Level C2 evaluation (>=50% restricted oracle recovery)

Generates:
- outputs/fungibility_implicit_carrier_operator/sufficient_statistics_ablation.csv
- outputs/fungibility_implicit_carrier_operator/predictor_accuracy.csv
- figures/fungibility_implicit_carrier_operator/figure_c_hg_prediction_quality.png
- figures/fungibility_implicit_carrier_operator/figure_d_operator_information_vs_output_dim.png
"""

import sys
import gc
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import TensorDataset, DataLoader

REPO_ROOT = Path(r"d:\Study\Patch-Content-Fungibility")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patch_fungibility.implicit_carrier_operator import (
    construct_analytic_correction_basis,
    compute_restricted_carrier_oracle_quantities,
    solve_restricted_carrier_from_hg,
    CarrierStatisticsPredictor
)
from patch_fungibility.practical_operator_compression import create_fixed_spatial_grouping

TARGETS_DIR = REPO_ROOT / "outputs" / "fungibility_amortized_operator" / "targets"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "fungibility_implicit_carrier_operator"
FIGURES_DIR = REPO_ROOT / "figures" / "fungibility_implicit_carrier_operator"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

ARCH_CONFIGS = {
    "deit_tiny": {"N": 196, "D": 192, "r": 32, "depth": 8, "target_file": "deit_tiny_targets.pt", "B_tok": 98},
    "deit_small": {"N": 196, "D": 384, "r": 32, "depth": 8, "target_file": "deit_small_targets.pt", "B_tok": 98},
    "vit_base": {"N": 196, "D": 768, "r": 32, "depth": 7, "target_file": "vit_base_targets.pt", "B_tok": 98},
    "dinov2": {"N": 256, "D": 384, "r": 32, "depth": 8, "target_file": "dinov2_targets.pt", "B_tok": 128}
}

Q = 16


def count_parameters_and_flops(module: nn.Module) -> Tuple[int, float]:
    p_cnt = sum(p.numel() for p in module.parameters() if p.requires_grad)
    flops = 0.0
    for m in module.modules():
        if isinstance(m, nn.Linear):
            flops += 2.0 * m.in_features * m.out_features
    return p_cnt, flops


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running Carrier Statistics Distillation on {device}", flush=True)

    ablation_rows = []
    accuracy_rows = []

    for arch_name, cfg in ARCH_CONFIGS.items():
        fpath = TARGETS_DIR / cfg["target_file"]
        if not fpath.exists():
            continue

        print(f"\n==========================================", flush=True)
        print(f"Distilling Carrier Statistics for {arch_name}", flush=True)
        print(f"==========================================", flush=True)

        data = torch.load(fpath, map_location="cpu")
        train_acts = data["train_acts"].float() # (500, 1+N, D)
        train_V = data["train_V"].float()       # (500, ND, r)
        val_acts = data["val_acts"].float()     # (100, 1+N, D)
        val_V = data["val_V"].float()           # (100, ND, r)
        N = cfg["N"]
        D = cfg["D"]
        r = cfg["r"]
        ND = N * D
        B_tok = cfg["B_tok"]

        grid_size = int(math.isqrt(N))
        S_group, m_group, _ = create_fixed_spatial_grouping(N, B_tok, grid_h=grid_size, grid_w=grid_size, device=device)

        # 1. Feature PCA basis
        P_all = train_acts[:, 1:, :].reshape(-1, D)
        _, _, Vh_pca = torch.linalg.svd(P_all[:2000], full_matrices=False)
        pca_basis = Vh_pca[:64, :].t().to(device)

        # 2. Extract pooled inputs x = [cls; mean(P)] -> (B, 2D)
        train_x = torch.cat([train_acts[:, 0, :], train_acts[:, 1:, :].mean(dim=1)], dim=-1) # (500, 2D)
        val_x = torch.cat([val_acts[:, 0, :], val_acts[:, 1:, :].mean(dim=1)], dim=-1)       # (100, 2D)
        d_in = 2 * D

        # 3. Compute oracle training targets (H_q, g_q, alpha*) on training set
        print("  Computing oracle training targets in carrier space...", flush=True)
        train_H_list, train_g_list, train_alpha_list = [], [], []
        with torch.no_grad():
            for idx in range(0, train_acts.shape[0], 20):
                b_acts = train_acts[idx:idx+20].to(device)
                b_V = train_V[idx:idx+20].to(device)
                P = b_acts[:, 1:, :]
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                ores = compute_restricted_carrier_oracle_quantities(b_V, P, S_group, m_group, R)
                train_H_list.append(ores["H_q"].cpu())
                train_g_list.append(ores["g_q"].cpu())
                train_alpha_list.append(ores["alpha_star"].cpu())

        train_H = torch.cat(train_H_list, dim=0) # (500, q, q)
        train_g = torch.cat(train_g_list, dim=0) # (500, q)
        train_alpha = torch.cat(train_alpha_list, dim=0) # (500, q)
        H_bar = train_H.mean(dim=0).to(device) # (q, q) static average Hessian

        # 4. Compute validation oracle targets
        val_H_list, val_g_list, val_alpha_list, val_gm_je_list, val_ora_je_list = [], [], [], [], []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]

                # Group mean error
                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                recon_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), C_mean)
                E_mean = (P - recon_mean).reshape(BS, ND, 1)
                je_mean = torch.bmm(b_V.transpose(1, 2), E_mean).norm(dim=1).squeeze(-1)
                val_gm_je_list.extend(je_mean.cpu().tolist())

                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                ores = compute_restricted_carrier_oracle_quantities(b_V, P, S_group, m_group, R)
                recon_ora = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), ores["C_opt"])
                E_ora = (P - recon_ora).reshape(BS, ND, 1)
                je_ora = torch.bmm(b_V.transpose(1, 2), E_ora).norm(dim=1).squeeze(-1)
                val_ora_je_list.extend(je_ora.cpu().tolist())

                val_H_list.append(ores["H_q"].cpu())
                val_g_list.append(ores["g_q"].cpu())
                val_alpha_list.append(ores["alpha_star"].cpu())

        val_H = torch.cat(val_H_list, dim=0)
        val_g = torch.cat(val_g_list, dim=0)
        val_alpha = torch.cat(val_alpha_list, dim=0)

        mean_val_gm_je = float(np.mean(val_gm_je_list))
        mean_val_ora_je = float(np.mean(val_ora_je_list))
        oracle_gap = mean_val_gm_je - mean_val_ora_je

        print(f"  Validation Group Mean ||JE||: {mean_val_gm_je:.4f} | Restricted Oracle ||JE||: {mean_val_ora_je:.4f} | Gap: {oracle_gap:.4f}", flush=True)

        # Baseline: Static Average Alpha
        alpha_bar = train_alpha.mean(dim=0).to(device)
        static_je_list = []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]
                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                delta_C = torch.einsum('q,bjgq->bjg', alpha_bar, R)
                C_stat = C_mean + delta_C
                recon_stat = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), C_stat)
                E_stat = (P - recon_stat).reshape(BS, ND, 1)
                je_stat = torch.bmm(b_V.transpose(1, 2), E_stat).norm(dim=1).squeeze(-1)
                static_je_list.extend(je_stat.cpu().tolist())

        mean_static_je = float(np.mean(static_je_list))
        static_gain = mean_val_gm_je - mean_static_je
        static_recovery = (static_gain / max(oracle_gap, 1e-4)) * 100.0

        ablation_rows.append({
            "architecture": arch_name,
            "option": "Static_Average_Alpha",
            "output_dim": 0,
            "params": 0,
            "flops": 0.0,
            "test_relative_mse": 1.0,
            "downstream_je": mean_static_je,
            "recovered_gain": static_gain,
            "oracle_recovery_pct": static_recovery,
            "level_c2_passed": False
        })

        # ----------------------------------------------------
        # OPTION A: Predict g_q only (with static H_bar)
        # ----------------------------------------------------
        print("\n  Training Option A (g_q only)...", flush=True)
        model_A = CarrierStatisticsPredictor(d_in=d_in, q=Q, mode="g_only").to(device)
        model_A.static_H.copy_(H_bar)
        opt_A = torch.optim.AdamW(model_A.parameters(), lr=1e-3, weight_decay=1e-4)

        ds_A = TensorDataset(train_x, train_g)
        loader_A = DataLoader(ds_A, batch_size=32, shuffle=True)
        for ep in range(20):
            model_A.train()
            for bx, bg in loader_A:
                bx, bg = bx.to(device), bg.to(device)
                opt_A.zero_grad()
                pred_g = model_A(bx)
                loss = F.mse_loss(pred_g, bg)
                loss.backward()
                opt_A.step()

        # Evaluate Option A
        model_A.eval()
        p_A, f_A = count_parameters_and_flops(model_A)
        je_A_list, err_A_list = [], []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                bx = val_x[idx:idx+20].to(device)
                bg = val_g[idx:idx+20].to(device)
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]

                pred_g = model_A(bx)
                rel_err = (pred_g - bg).norm(dim=-1) / bg.norm(dim=-1).clamp(min=1e-4)
                err_A_list.extend(rel_err.cpu().tolist())

                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                sres = solve_restricted_carrier_from_hg(H_bar.unsqueeze(0).expand(BS, -1, -1), pred_g, R, C_mean)
                recon_A = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), sres["C_opt"])
                E_A = (P - recon_A).reshape(BS, ND, 1)
                je_A = torch.bmm(b_V.transpose(1, 2), E_A).norm(dim=1).squeeze(-1)
                je_A_list.extend(je_A.cpu().tolist())

        mean_je_A = float(np.mean(je_A_list))
        gain_A = mean_val_gm_je - mean_je_A
        rec_A = (gain_A / max(oracle_gap, 1e-4)) * 100.0
        mse_A = float(np.mean(err_A_list))

        ablation_rows.append({
            "architecture": arch_name,
            "option": "Option_A_g_only_static_H",
            "output_dim": Q,
            "params": p_A,
            "flops": f_A,
            "test_relative_mse": mse_A,
            "downstream_je": mean_je_A,
            "recovered_gain": gain_A,
            "oracle_recovery_pct": rec_A,
            "level_c2_passed": bool(rec_A >= 50.0)
        })
        print(f"  Option A: Relative MSE={mse_A:.4f} | ||JE||={mean_je_A:.4f} | Recovery={rec_A:.2f}%", flush=True)

        # ----------------------------------------------------
        # OPTION B: Predict diag(H_q) + g_q
        # ----------------------------------------------------
        print("\n  Training Option B (diag(H_q) + g_q)...", flush=True)
        model_B = CarrierStatisticsPredictor(d_in=d_in, q=Q, mode="diag_h_g").to(device)
        opt_B = torch.optim.AdamW(model_B.parameters(), lr=1e-3, weight_decay=1e-4)

        train_diag_H = torch.diagonal(train_H, dim1=-2, dim2=-1) # (500, q)
        val_diag_H = torch.diagonal(val_H, dim1=-2, dim2=-1)

        ds_B = TensorDataset(train_x, train_diag_H, train_g)
        loader_B = DataLoader(ds_B, batch_size=32, shuffle=True)
        for ep in range(20):
            model_B.train()
            for bx, b_dh, bg in loader_B:
                bx, b_dh, bg = bx.to(device), b_dh.to(device), bg.to(device)
                opt_B.zero_grad()
                pred_H, pred_g = model_B(bx)
                pred_diag = torch.diagonal(pred_H, dim1=-2, dim2=-1)
                loss = F.mse_loss(pred_diag, b_dh) + F.mse_loss(pred_g, bg)
                loss.backward()
                opt_B.step()

        model_B.eval()
        p_B, f_B = count_parameters_and_flops(model_B)
        je_B_list, err_B_list = [], []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                bx = val_x[idx:idx+20].to(device)
                bg = val_g[idx:idx+20].to(device)
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]

                pred_H, pred_g = model_B(bx)
                rel_err = (pred_g - bg).norm(dim=-1) / bg.norm(dim=-1).clamp(min=1e-4)
                err_B_list.extend(rel_err.cpu().tolist())

                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                sres = solve_restricted_carrier_from_hg(pred_H, pred_g, R, C_mean)
                recon_B = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), sres["C_opt"])
                E_B = (P - recon_B).reshape(BS, ND, 1)
                je_B = torch.bmm(b_V.transpose(1, 2), E_B).norm(dim=1).squeeze(-1)
                je_B_list.extend(je_B.cpu().tolist())

        mean_je_B = float(np.mean(je_B_list))
        gain_B = mean_val_gm_je - mean_je_B
        rec_B = (gain_B / max(oracle_gap, 1e-4)) * 100.0
        mse_B = float(np.mean(err_B_list))

        ablation_rows.append({
            "architecture": arch_name,
            "option": "Option_B_diag_H_and_g",
            "output_dim": 2 * Q,
            "params": p_B,
            "flops": f_B,
            "test_relative_mse": mse_B,
            "downstream_je": mean_je_B,
            "recovered_gain": gain_B,
            "oracle_recovery_pct": rec_B,
            "level_c2_passed": bool(rec_B >= 50.0)
        })
        print(f"  Option B: Relative MSE={mse_B:.4f} | ||JE||={mean_je_B:.4f} | Recovery={rec_B:.2f}%", flush=True)

        # ----------------------------------------------------
        # OPTION C: Predict full Cholesky L_q + g_q
        # ----------------------------------------------------
        print("\n  Training Option C (Full Cholesky L_q + g_q)...", flush=True)
        model_C = CarrierStatisticsPredictor(d_in=d_in, q=Q, mode="full_h_g").to(device)
        opt_C = torch.optim.AdamW(model_C.parameters(), lr=1e-3, weight_decay=1e-4)

        ds_C = TensorDataset(train_x, train_H, train_g)
        loader_C = DataLoader(ds_C, batch_size=32, shuffle=True)
        for ep in range(20):
            model_C.train()
            for bx, bH, bg in loader_C:
                bx, bH, bg = bx.to(device), bH.to(device), bg.to(device)
                opt_C.zero_grad()
                pred_H, pred_g = model_C(bx)
                loss = F.mse_loss(pred_H, bH) + F.mse_loss(pred_g, bg)
                loss.backward()
                opt_C.step()

        model_C.eval()
        p_C, f_C = count_parameters_and_flops(model_C)
        je_C_list, err_C_list = [], []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                bx = val_x[idx:idx+20].to(device)
                bg = val_g[idx:idx+20].to(device)
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]

                pred_H, pred_g = model_C(bx)
                rel_err = (pred_g - bg).norm(dim=-1) / bg.norm(dim=-1).clamp(min=1e-4)
                err_C_list.extend(rel_err.cpu().tolist())

                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                sres = solve_restricted_carrier_from_hg(pred_H, pred_g, R, C_mean)
                recon_C = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), sres["C_opt"])
                E_C = (P - recon_C).reshape(BS, ND, 1)
                je_C = torch.bmm(b_V.transpose(1, 2), E_C).norm(dim=1).squeeze(-1)
                je_C_list.extend(je_C.cpu().tolist())

        mean_je_C = float(np.mean(je_C_list))
        gain_C = mean_val_gm_je - mean_je_C
        rec_C = (gain_C / max(oracle_gap, 1e-4)) * 100.0
        mse_C = float(np.mean(err_C_list))

        ablation_rows.append({
            "architecture": arch_name,
            "option": "Option_C_full_H_and_g",
            "output_dim": (Q * (Q + 1)) // 2 + Q,
            "params": p_C,
            "flops": f_C,
            "test_relative_mse": mse_C,
            "downstream_je": mean_je_C,
            "recovered_gain": gain_C,
            "oracle_recovery_pct": rec_C,
            "level_c2_passed": bool(rec_C >= 50.0)
        })
        print(f"  Option C: Relative MSE={mse_C:.4f} | ||JE||={mean_je_C:.4f} | Recovery={rec_C:.2f}%", flush=True)

        # ----------------------------------------------------
        # OPTION D: Direct alpha* prediction
        # ----------------------------------------------------
        print("\n  Training Option D (Direct alpha*)...", flush=True)
        model_D = CarrierStatisticsPredictor(d_in=d_in, q=Q, mode="alpha").to(device)
        opt_D = torch.optim.AdamW(model_D.parameters(), lr=1e-3, weight_decay=1e-4)

        ds_D = TensorDataset(train_x, train_alpha)
        loader_D = DataLoader(ds_D, batch_size=32, shuffle=True)
        for ep in range(20):
            model_D.train()
            for bx, ba in loader_D:
                bx, ba = bx.to(device), ba.to(device)
                opt_D.zero_grad()
                pred_a = model_D(bx)
                loss = F.mse_loss(pred_a, ba)
                loss.backward()
                opt_D.step()

        model_D.eval()
        p_D, f_D = count_parameters_and_flops(model_D)
        je_D_list, err_D_list = [], []
        with torch.no_grad():
            for idx in range(0, val_acts.shape[0], 20):
                bx = val_x[idx:idx+20].to(device)
                ba = val_alpha[idx:idx+20].to(device)
                b_acts = val_acts[idx:idx+20].to(device)
                b_V = val_V[idx:idx+20].to(device)
                BS = b_acts.shape[0]
                P = b_acts[:, 1:, :]

                pred_a = model_D(bx)
                rel_err = (pred_a - ba).norm(dim=-1) / ba.norm(dim=-1).clamp(min=1e-4)
                err_D_list.extend(rel_err.cpu().tolist())

                C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                R = construct_analytic_correction_basis(P, S_group, m_group, q=Q, basis_type="feature_pca", pca_basis=pca_basis)
                delta_C = torch.einsum('bq,bjgq->bjg', pred_a, R)
                C_opt = C_mean + delta_C
                recon_D = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), C_opt)
                E_D = (P - recon_D).reshape(BS, ND, 1)
                je_D = torch.bmm(b_V.transpose(1, 2), E_D).norm(dim=1).squeeze(-1)
                je_D_list.extend(je_D.cpu().tolist())

        mean_je_D = float(np.mean(je_D_list))
        gain_D = mean_val_gm_je - mean_je_D
        rec_D = (gain_D / max(oracle_gap, 1e-4)) * 100.0
        mse_D = float(np.mean(err_D_list))

        ablation_rows.append({
            "architecture": arch_name,
            "option": "Option_D_direct_alpha",
            "output_dim": Q,
            "params": p_D,
            "flops": f_D,
            "test_relative_mse": mse_D,
            "downstream_je": mean_je_D,
            "recovered_gain": gain_D,
            "oracle_recovery_pct": rec_D,
            "level_c2_passed": bool(rec_D >= 50.0)
        })
        print(f"  Option D: Relative MSE={mse_D:.4f} | ||JE||={mean_je_D:.4f} | Recovery={rec_D:.2f}%", flush=True)

        accuracy_rows.append({
            "architecture": arch_name,
            "option_A_rel_mse": mse_A,
            "option_B_rel_mse": mse_B,
            "option_C_rel_mse": mse_C,
            "option_D_rel_mse": mse_D,
            "best_option": "Option_D_direct_alpha" if rec_D >= max(rec_A, rec_B, rec_C) else ("Option_A_g_only" if rec_A >= max(rec_B, rec_C) else "Option_B_diag_H")
        })

        # Save best model checkpoint
        torch.save(model_D.state_dict(), OUTPUTS_DIR / f"predictor_alpha_{arch_name}.pt")
        del val_acts, val_V, train_acts, train_V, data, model_A, model_B, model_C, model_D
        torch.cuda.empty_cache()
        gc.collect()

    df_abl = pd.DataFrame(ablation_rows)
    df_abl.to_csv(OUTPUTS_DIR / "sufficient_statistics_ablation.csv", index=False)
    print(f"\nSaved {OUTPUTS_DIR / 'sufficient_statistics_ablation.csv'}", flush=True)

    df_acc = pd.DataFrame(accuracy_rows)
    df_acc.to_csv(OUTPUTS_DIR / "predictor_accuracy.csv", index=False)
    print(f"Saved {OUTPUTS_DIR / 'predictor_accuracy.csv'}", flush=True)

    # Plot Figure C: Prediction Quality Comparison across Options
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    archs = list(ARCH_CONFIGS.keys())
    x = np.arange(len(archs))
    width = 0.2

    opts = ["Option_A_g_only_static_H", "Option_B_diag_H_and_g", "Option_C_full_H_and_g", "Option_D_direct_alpha"]
    labels = ["Option A (g only)", "Option B (diag H + g)", "Option C (full H + g)", "Option D (direct alpha)"]

    for idx, (opt, lbl) in enumerate(zip(opts, labels)):
        vals = []
        for a in archs:
            sub = df_abl[(df_abl["architecture"] == a) & (df_abl["option"] == opt)]
            vals.append(sub["oracle_recovery_pct"].values[0] if len(sub) > 0 else 0.0)
        ax.bar(x + idx * width - 1.5 * width, vals, width, label=lbl)

    ax.axhline(50.0, color="black", linestyle="--", linewidth=1.5, label="Level C2 Target (50%)")
    ax.set_xticks(x)
    ax.set_xticklabels(archs, fontweight="bold")
    ax.set_ylabel("Restricted Oracle Recovery (%)", fontsize=11, fontweight="bold")
    ax.set_title("Figure C: Sufficient Statistics Distillation Comparison", fontsize=12, fontweight="bold")
    ax.legend(frameon=True, fontsize=9)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "figure_c_hg_prediction_quality.png")
    plt.close()
    print(f"Generated {FIGURES_DIR / 'figure_c_hg_prediction_quality.png'}", flush=True)

    # Plot Figure D: Output Dimension vs Recovery
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    for opt, lbl, color, marker in zip(opts, labels, ["blue", "green", "red", "purple"], ["o", "s", "^", "D"]):
        sub = df_abl[df_abl["option"] == opt]
        ax.scatter(sub["output_dim"], sub["oracle_recovery_pct"], s=100, color=color, marker=marker, label=lbl)

    ax.set_xlabel("Predictor Output Dimension (number of predicted scalars)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Restricted Oracle Recovery (%)", fontsize=11, fontweight="bold")
    ax.set_title("Figure D: Operator Information vs Predictor Output Bandwidth", fontsize=12, fontweight="bold")
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "figure_d_operator_information_vs_output_dim.png")
    plt.close()
    print(f"Generated {FIGURES_DIR / 'figure_d_operator_information_vs_output_dim.png'}", flush=True)


if __name__ == "__main__":
    main()
