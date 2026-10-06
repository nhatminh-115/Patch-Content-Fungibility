"""
scripts/analyze_restricted_carrier_oracle.py

Phase 3 & 4: Upper Bound Evaluation of Restricted Carrier Oracle
Tests whether restricting carrier corrections to delta_c = R alpha with q in {4, 8, 16, 32, 64}
captures the full operator oracle benefits without ever constructing ambient ND x r tensors.

Evaluates 5 candidate correction bases:
A. Group-residual directions
B. Calibration feature PCA basis
C. Group-wise mean/variance basis
D. Hybrid semantic residual basis
E. Random matched control

Generates:
- outputs/fungibility_implicit_carrier_operator/restricted_oracle_recovery.csv
- outputs/fungibility_implicit_carrier_operator/correction_basis_ablation.csv
- figures/fungibility_implicit_carrier_operator/figure_a_restricted_oracle_recovery.png
- figures/fungibility_implicit_carrier_operator/figure_b_correction_basis_ablation.png
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

REPO_ROOT = Path(r"d:\Study\Patch-Content-Fungibility")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patch_fungibility.implicit_carrier_operator import (
    construct_analytic_correction_basis,
    compute_restricted_carrier_oracle_quantities
)
from patch_fungibility.practical_operator_compression import create_fixed_spatial_grouping
from patch_fungibility.batched_operator_compression import batched_solve_amortized_carrier

TARGETS_DIR = REPO_ROOT / "outputs" / "fungibility_amortized_operator" / "targets"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "fungibility_implicit_carrier_operator"
FIGURES_DIR = REPO_ROOT / "figures" / "fungibility_implicit_carrier_operator"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

ARCH_CONFIGS = {
    "deit_tiny": {"N": 196, "D": 192, "r": 32, "depth": 8, "target_file": "deit_tiny_targets.pt", "budgets": [98, 49, 32]},
    "deit_small": {"N": 196, "D": 384, "r": 32, "depth": 8, "target_file": "deit_small_targets.pt", "budgets": [98, 49, 32]},
    "vit_base": {"N": 196, "D": 768, "r": 32, "depth": 7, "target_file": "vit_base_targets.pt", "budgets": [98, 49, 32]},
    "dinov2": {"N": 256, "D": 384, "r": 32, "depth": 8, "target_file": "dinov2_targets.pt", "budgets": [128, 64, 42]}
}

Q_VALUES = [4, 8, 16, 32, 64]
BASIS_TYPES = ["group_residual", "feature_pca", "group_statistics", "hybrid_semantic", "random_control"]


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Running Restricted Carrier Oracle Analysis on {device}", flush=True)

    oracle_recovery_rows = []
    basis_ablation_rows = []

    for arch_name, cfg in ARCH_CONFIGS.items():
        fpath = TARGETS_DIR / cfg["target_file"]
        if not fpath.exists():
            print(f"Skipping {arch_name}: {fpath} not found", flush=True)
            continue

        print(f"\n==========================================", flush=True)
        print(f"Evaluating Restricted Carrier Oracle for {arch_name}", flush=True)
        print(f"==========================================", flush=True)

        data = torch.load(fpath, map_location="cpu")
        val_acts = data["val_acts"].float() # (100, 1+N, D)
        val_V = data["val_V"].float()       # (100, ND, r)
        depth = cfg["depth"]
        N = cfg["N"]
        D = cfg["D"]
        r = cfg["r"]
        ND = N * D

        # Compute calibration feature PCA basis for feature_pca
        P_all = val_acts[:, 1:, :].reshape(-1, D)
        _, _, Vh_pca = torch.linalg.svd(P_all[:2000], full_matrices=False)
        pca_basis = Vh_pca[:64, :].t().to(device) # (D, 64)

        for B_tok in cfg["budgets"]:
            pct = int(round((B_tok / N) * 100))
            grid_size = int(math.isqrt(N))
            S_group, m_group, _ = create_fixed_spatial_grouping(N, B_tok, grid_h=grid_size, grid_w=grid_size, device=device)

            # Evaluate Group Mean and Full Operator Oracle baseline first
            gm_je_list = []
            full_oracle_je_list = []

            with torch.no_grad():
                for idx in range(0, min(100, val_acts.shape[0]), 10):
                    b_acts = val_acts[idx:idx+10].to(device)
                    b_V = val_V[idx:idx+10].to(device)
                    BS = b_acts.shape[0]
                    P = b_acts[:, 1:, :]

                    # Group mean
                    C_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1).transpose(1, 2), P) / m_group.view(1, B_tok, 1)
                    recon_mean = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), C_mean)
                    E_mean = (P - recon_mean).reshape(BS, ND, 1)
                    je_mean = torch.bmm(b_V.transpose(1, 2), E_mean).norm(dim=1).squeeze(-1)
                    gm_je_list.extend(je_mean.cpu().tolist())

                    # Full Operator Oracle
                    res_full = batched_solve_amortized_carrier(P, S_group, m_group, b_V)
                    recon_full = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), res_full["C_opt"])
                    E_full = (P - recon_full).reshape(BS, ND, 1)
                    je_full = torch.bmm(b_V.transpose(1, 2), E_full).norm(dim=1).squeeze(-1)
                    full_oracle_je_list.extend(je_full.cpu().tolist())

            mean_gm_je = float(np.mean(gm_je_list))
            mean_full_je = float(np.mean(full_oracle_je_list))
            total_oracle_gap = mean_gm_je - mean_full_je

            print(f"  [Budget {pct}% ({B_tok} tokens)] Group Mean ||JE||: {mean_gm_je:.4f} | Full Oracle ||JE||: {mean_full_je:.4f} | Gap: {total_oracle_gap:.4f}", flush=True)

            # 1. Sweep q values with primary basis (group_residual)
            for q in Q_VALUES:
                q_je_list = []
                with torch.no_grad():
                    for idx in range(0, min(100, val_acts.shape[0]), 10):
                        b_acts = val_acts[idx:idx+10].to(device)
                        b_V = val_V[idx:idx+10].to(device)
                        BS = b_acts.shape[0]
                        P = b_acts[:, 1:, :]

                        R = construct_analytic_correction_basis(P, S_group, m_group, q=q, basis_type="group_residual", pca_basis=pca_basis)
                        oracle_res = compute_restricted_carrier_oracle_quantities(b_V, P, S_group, m_group, R)
                        recon_q = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), oracle_res["C_opt"])
                        E_q = (P - recon_q).reshape(BS, ND, 1)
                        je_q = torch.bmm(b_V.transpose(1, 2), E_q).norm(dim=1).squeeze(-1)
                        q_je_list.extend(je_q.cpu().tolist())

                mean_q_je = float(np.mean(q_je_list))
                recovered_gain = mean_gm_je - mean_q_je
                pct_recovered = (recovered_gain / max(total_oracle_gap, 1e-4)) * 100.0

                oracle_recovery_rows.append({
                    "architecture": arch_name,
                    "depth": depth,
                    "budget_tokens": B_tok,
                    "budget_percent": pct,
                    "q_dimension": q,
                    "group_mean_je": mean_gm_je,
                    "full_oracle_je": mean_full_je,
                    "restricted_oracle_je": mean_q_je,
                    "recovered_gain": recovered_gain,
                    "oracle_recovery_pct": pct_recovered,
                    "level_c1_passed": bool(q <= 32 and pct_recovered >= 50.0)
                })
                print(f"    q={q:2d}: Restricted ||JE||={mean_q_je:.4f} | Recovery={pct_recovered:5.2f}%", flush=True)

            # 2. Sweep basis types at q=16
            for b_type in BASIS_TYPES:
                b_je_list = []
                with torch.no_grad():
                    for idx in range(0, min(100, val_acts.shape[0]), 10):
                        b_acts = val_acts[idx:idx+10].to(device)
                        b_V = val_V[idx:idx+10].to(device)
                        BS = b_acts.shape[0]
                        P = b_acts[:, 1:, :]

                        R = construct_analytic_correction_basis(P, S_group, m_group, q=16, basis_type=b_type, pca_basis=pca_basis)
                        oracle_res = compute_restricted_carrier_oracle_quantities(b_V, P, S_group, m_group, R)
                        recon_b = torch.bmm(S_group.unsqueeze(0).expand(BS, -1, -1), oracle_res["C_opt"])
                        E_b = (P - recon_b).reshape(BS, ND, 1)
                        je_b = torch.bmm(b_V.transpose(1, 2), E_b).norm(dim=1).squeeze(-1)
                        b_je_list.extend(je_b.cpu().tolist())

                mean_b_je = float(np.mean(b_je_list))
                b_gain = mean_gm_je - mean_b_je
                b_pct_recovered = (b_gain / max(total_oracle_gap, 1e-4)) * 100.0

                basis_ablation_rows.append({
                    "architecture": arch_name,
                    "depth": depth,
                    "budget_tokens": B_tok,
                    "budget_percent": pct,
                    "basis_type": b_type,
                    "q_dimension": 16,
                    "restricted_je": mean_b_je,
                    "recovered_gain": b_gain,
                    "oracle_recovery_pct": b_pct_recovered
                })

        del val_acts, val_V, data, pca_basis
        torch.cuda.empty_cache()
        gc.collect()

    df_rec = pd.DataFrame(oracle_recovery_rows)
    df_rec.to_csv(OUTPUTS_DIR / "restricted_oracle_recovery.csv", index=False)
    print(f"\nSaved {OUTPUTS_DIR / 'restricted_oracle_recovery.csv'}", flush=True)

    df_bas = pd.DataFrame(basis_ablation_rows)
    df_bas.to_csv(OUTPUTS_DIR / "correction_basis_ablation.csv", index=False)
    print(f"Saved {OUTPUTS_DIR / 'correction_basis_ablation.csv'}", flush=True)

    # Plot Figure A: Restricted Oracle Recovery vs q
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    for arch in ARCH_CONFIGS.keys():
        sub = df_rec[(df_rec["architecture"] == arch) & (df_rec["budget_percent"] == 50)].sort_values("q_dimension")
        if len(sub) > 0:
            ax.plot(sub["q_dimension"], sub["oracle_recovery_pct"], marker="o", label=arch, linewidth=2)

    ax.axhline(50.0, color="black", linestyle="--", linewidth=1.5, label="Level C1 Target (50%)")
    ax.set_xlabel("Restricted Carrier Subspace Dimension (q)", fontsize=11, fontweight="bold")
    ax.set_ylabel("Full Operator Oracle Gain Recovered (%)", fontsize=11, fontweight="bold")
    ax.set_title("Figure A: Restricted Carrier Oracle Recovery vs Dimension q (Budget 50%)", fontsize=12, fontweight="bold")
    ax.set_xticks(Q_VALUES)
    ax.legend(frameon=True)
    ax.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "figure_a_restricted_oracle_recovery.png")
    plt.close()
    print(f"Generated {FIGURES_DIR / 'figure_a_restricted_oracle_recovery.png'}", flush=True)

    # Plot Figure B: Correction Basis Ablation (q=16)
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    archs = list(ARCH_CONFIGS.keys())
    x = np.arange(len(archs))
    width = 0.16

    for idx, b_type in enumerate(BASIS_TYPES):
        vals = []
        for a in archs:
            sub = df_bas[(df_bas["architecture"] == a) & (df_bas["budget_percent"] == 50) & (df_bas["basis_type"] == b_type)]
            val = sub["oracle_recovery_pct"].values[0] if len(sub) > 0 else 0.0
            vals.append(val)
        ax.bar(x + idx * width - 2 * width, vals, width, label=b_type)

    ax.set_xticks(x)
    ax.set_xticklabels(archs, fontweight="bold")
    ax.set_ylabel("Full Oracle Recovery (%) at q=16", fontsize=11, fontweight="bold")
    ax.set_title("Figure B: Analytic Correction Basis Comparison (q=16, Budget 50%)", fontsize=12, fontweight="bold")
    ax.legend(frameon=True, fontsize=9)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    fig.savefig(FIGURES_DIR / "figure_b_correction_basis_ablation.png")
    plt.close()
    print(f"Generated {FIGURES_DIR / 'figure_b_correction_basis_ablation.png'}", flush=True)


if __name__ == "__main__":
    main()
