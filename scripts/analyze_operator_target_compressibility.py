"""
scripts/analyze_operator_target_compressibility.py

Phase 1: Target Compressibility and Factor Variability Analysis
- Phase 1A: Shared Envelope Extraction across K in {16, 32, 48, 64, 96, 128} and evaluation on held-out validation sets.
- Phase 1B: Token-side vs Feature-side variability decomposition (Configs A-D).
- Generates:
  - outputs/fungibility_lightweight_operator_predictor/envelope_capture.csv
  - outputs/fungibility_lightweight_operator_predictor/factor_variability.csv
  - outputs/fungibility_lightweight_operator_predictor/principal_angles.csv
  - figures/fungibility_lightweight_operator_predictor/figure_a_oracle_envelope_spectrum.png
  - figures/fungibility_lightweight_operator_predictor/figure_b_envelope_capture.png
  - figures/fungibility_lightweight_operator_predictor/figure_c_token_vs_feature_variability.png
"""

import gc
import sys
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

REPO_ROOT = Path(r"d:\Study\Patch-Content-Fungibility")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patch_fungibility.lightweight_operator_predictor import (
    compute_subspace_overlap,
    compute_principal_angles,
    compute_envelope_capture,
    extract_shared_envelope_svd
)

TARGETS_DIR = REPO_ROOT / "outputs" / "fungibility_amortized_operator" / "targets"
OUTPUTS_DIR = REPO_ROOT / "outputs" / "fungibility_lightweight_operator_predictor"
FIGURES_DIR = REPO_ROOT / "figures" / "fungibility_lightweight_operator_predictor"

OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

MODEL_FILES = {
    "deit_tiny": "deit_tiny_targets.pt",
    "deit_small": "deit_small_targets.pt",
    "vit_base": "vit_base_targets.pt",
    "dinov2": "dinov2_targets.pt"
}

K_VALUES = [16, 32, 48, 64, 96, 128]


def run_phase_1a_envelope_analysis(device: torch.device):
    print("=== RUNNING PHASE 1A: GLOBAL SUBSPACE ENVELOPE ANALYSIS ===")
    envelope_rows = []
    angles_rows = []
    spectrum_data = {}

    for model_key, fname in MODEL_FILES.items():
        fpath = TARGETS_DIR / fname
        if not fpath.exists():
            print(f"Warning: {fpath} not found, skipping {model_key}")
            continue

        print(f"\nProcessing {model_key} from {fname}...")
        data = torch.load(fpath, map_location="cpu")
        train_V = data["train_V"]  # (500, ND, 32)
        val_V = data["val_V"].float()      # (100, ND, 32)
        depth = data["depth"]
        N = data["N"]
        D = data["D"]
        r = data["r"]
        ND = N * D

        M_train = train_V.shape[0]
        M_val = val_V.shape[0]

        # Stack training bases on CPU to prevent GPU OOM: (ND, M_train * r)
        train_V_reshaped = train_V.permute(1, 0, 2).reshape(ND, M_train * r).float()
        print(f"  Training stack shape: {train_V_reshaped.shape}. Running CPU randomized SVD for K_max=128...")

        # Randomized SVD on CPU
        U_full, S_decay, _ = torch.svd_lowrank(train_V_reshaped, q=128, niter=4)
        spectrum_data[model_key] = S_decay.numpy()

        # Free train_V_reshaped immediately
        del train_V_reshaped
        gc.collect()

        # Move U_full and val_V to GPU for evaluation
        U_full_gpu = U_full.to(device)
        val_V_gpu = val_V.to(device)

        for K in K_VALUES:
            U_K = U_full_gpu[:, :K]
            with torch.no_grad():
                captures = compute_envelope_capture(U_K, val_V_gpu).cpu().numpy()
                mean_cap = float(np.mean(captures))
                median_cap = float(np.median(captures))
                q10_cap = float(np.percentile(captures, 10))
                q90_cap = float(np.percentile(captures, 90))
                std_cap = float(np.std(captures))

                if K == 64:
                    angles = compute_principal_angles(U_K, val_V_gpu).cpu().numpy()
                    mean_angles = np.mean(angles, axis=0)
                    for rank_idx, cos_val in enumerate(mean_angles):
                        angles_rows.append({
                            "architecture": model_key,
                            "depth": depth,
                            "rank_mode": rank_idx + 1,
                            "cos_principal_angle": float(cos_val),
                            "angle_degrees": float(math.degrees(math.acos(min(max(cos_val, 0.0), 1.0))))
                        })

            print(f"  [{model_key}] K={K}: Mean Capture = {mean_cap * 100:.2f}%, Median = {median_cap * 100:.2f}% (q10={q10_cap * 100:.2f}%, q90={q90_cap * 100:.2f}%)")
            
            envelope_rows.append({
                "architecture": model_key,
                "depth": depth,
                "N": N,
                "D": D,
                "ambient_dim": ND,
                "oracle_rank": r,
                "envelope_K": K,
                "mean_capture": mean_cap,
                "median_capture": median_cap,
                "q10_capture": q10_cap,
                "q90_capture": q90_cap,
                "std_capture": std_cap,
                "level_l1_passed": bool(K <= 64 and mean_cap >= 0.80)
            })

        del U_full_gpu, val_V_gpu, data
        torch.cuda.empty_cache()
        gc.collect()

    df_env = pd.DataFrame(envelope_rows)
    df_env.to_csv(OUTPUTS_DIR / "envelope_capture.csv", index=False)
    print(f"\nSaved {OUTPUTS_DIR / 'envelope_capture.csv'}")

    df_ang = pd.DataFrame(angles_rows)
    df_ang.to_csv(OUTPUTS_DIR / "principal_angles.csv", index=False)
    print(f"Saved {OUTPUTS_DIR / 'principal_angles.csv'}")

    return df_env, spectrum_data


def run_phase_1b_factor_variability(device: torch.device):
    print("\n=== RUNNING PHASE 1B: TOKEN-SIDE VS FEATURE-SIDE VARIABILITY ===")
    factor_rows = []

    for model_key, fname in MODEL_FILES.items():
        fpath = TARGETS_DIR / fname
        if not fpath.exists():
            continue

        print(f"\nDecomposing factors for {model_key}...")
        data = torch.load(fpath, map_location="cpu")
        val_V = data["val_V"].float().to(device)  # (100, ND, 32)
        V_static = data["V_static"].float().to(device)  # (ND, 32)
        depth = data["depth"]
        N = data["N"]
        D = data["D"]
        r = data["r"]
        M_val = val_V.shape[0]

        # Extract static factor components from V_static
        V_static_mat = V_static.view(N, D, r)
        A_static = torch.zeros(N, r, device=device)
        B_static = torch.zeros(D, r, device=device)
        for k in range(r):
            U_m, S_m, Vh_m = torch.linalg.svd(V_static_mat[:, :, k], full_matrices=False)
            A_static[:, k] = U_m[:, 0]
            B_static[:, k] = Vh_m[0, :]

        val_V_mat = val_V.view(M_val, N, D, r)
        
        # Config D: Both Static (V_static)
        overlap_D = compute_subspace_overlap(V_static, val_V).cpu().numpy()
        
        # Config A: Dynamic Token + Static Feature
        V_A_list = []
        for i in range(M_val):
            v_modes = []
            for k in range(r):
                Q_k = val_V_mat[i, :, :, k]
                b_k = B_static[:, k]
                a_dyn = torch.matmul(Q_k, b_k).unsqueeze(1)
                mode_k = torch.matmul(a_dyn, b_k.unsqueeze(0)).view(N * D)
                v_modes.append(mode_k)
            V_recon = torch.stack(v_modes, dim=-1)
            Q_recon, _ = torch.linalg.qr(V_recon)
            V_A_list.append(Q_recon)
        V_A = torch.stack(V_A_list, dim=0)
        overlap_A = compute_subspace_overlap(V_A, val_V).cpu().numpy()

        # Config B: Static Token + Dynamic Feature
        V_B_list = []
        for i in range(M_val):
            v_modes = []
            for k in range(r):
                Q_k = val_V_mat[i, :, :, k]
                a_k = A_static[:, k]
                b_dyn = torch.matmul(Q_k.t(), a_k).unsqueeze(0)
                mode_k = torch.matmul(a_k.unsqueeze(1), b_dyn).view(N * D)
                v_modes.append(mode_k)
            V_recon = torch.stack(v_modes, dim=-1)
            Q_recon, _ = torch.linalg.qr(V_recon)
            V_B_list.append(Q_recon)
        V_B = torch.stack(V_B_list, dim=0)
        overlap_B = compute_subspace_overlap(V_B, val_V).cpu().numpy()

        # Config C: Both Dynamic (Rank-1 SVD of each Q_k)
        V_C_list = []
        for i in range(M_val):
            v_modes = []
            for k in range(r):
                Q_k = val_V_mat[i, :, :, k]
                u, s, vh = torch.linalg.svd(Q_k, full_matrices=False)
                mode_k = torch.matmul(u[:, :1], vh[:1, :]).view(N * D)
                v_modes.append(mode_k)
            V_recon = torch.stack(v_modes, dim=-1)
            Q_recon, _ = torch.linalg.qr(V_recon)
            V_C_list.append(Q_recon)
        V_C = torch.stack(V_C_list, dim=0)
        overlap_C = compute_subspace_overlap(V_C, val_V).cpu().numpy()

        print(f"  [{model_key}] Overlap Results:")
        print(f"    Config A (Dyn Token + Stat Feat):  {np.mean(overlap_A) * 100:.2f}%")
        print(f"    Config B (Stat Token + Dyn Feat):  {np.mean(overlap_B) * 100:.2f}%")
        print(f"    Config C (Both Dynamic Factor):    {np.mean(overlap_C) * 100:.2f}%")
        print(f"    Config D (Both Static Baseline):   {np.mean(overlap_D) * 100:.2f}%")

        configs = [
            ("A_DynamicToken_StaticFeature", overlap_A, N * r),
            ("B_StaticToken_DynamicFeature", overlap_B, D * r),
            ("C_BothDynamic_Factorized", overlap_C, (N + D) * r),
            ("D_BothStatic_Baseline", overlap_D, 0)
        ]

        for cfg_name, ov_vals, out_dim in configs:
            factor_rows.append({
                "architecture": model_key,
                "depth": depth,
                "configuration": cfg_name,
                "predictor_output_dim": out_dim,
                "mean_overlap": float(np.mean(ov_vals)),
                "median_overlap": float(np.median(ov_vals)),
                "std_overlap": float(np.std(ov_vals)),
                "gain_over_static": float(np.mean(ov_vals) - np.mean(overlap_D))
            })

        del val_V, V_static, V_A, V_B, V_C, data
        torch.cuda.empty_cache()
        gc.collect()

    df_factor = pd.DataFrame(factor_rows)
    df_factor.to_csv(OUTPUTS_DIR / "factor_variability.csv", index=False)
    print(f"\nSaved {OUTPUTS_DIR / 'factor_variability.csv'}")

    return df_factor


def plot_phase_1_figures(df_env: pd.DataFrame, spectrum_data: Dict[str, np.ndarray], df_factor: pd.DataFrame):
    print("\n=== GENERATING PHASE 1 FIGURES ===")
    sns.set_theme(style="whitegrid", font_scale=1.1)

    palette = {"deit_tiny": "#1f77b4", "deit_small": "#2ca02c", "vit_base": "#d62728", "dinov2": "#9467bd"}

    # Figure A: Oracle Envelope Spectrum Decay
    fig, ax = plt.subplots(figsize=(8, 5))
    for m_key, spec in spectrum_data.items():
        cum_energy = np.cumsum(spec**2) / np.sum(spec**2)
        ax.plot(np.arange(1, len(spec) + 1), cum_energy, label=f"{m_key} (top-128)", color=palette.get(m_key, "black"), lw=2.2)
    ax.axhline(0.80, color="gray", linestyle="--", alpha=0.7, label="80% Energy Threshold (Level L1)")
    ax.axvline(64, color="red", linestyle=":", alpha=0.7, label="K=64 Cutoff")
    ax.set_xlabel("Number of Shared Envelope Dimensions (K)")
    ax.set_ylabel("Cumulative Subspace Energy Captured")
    ax.set_title("Figure A: Oracle Subspace Envelope Spectrum Across Architectures")
    ax.legend(loc="lower right")
    ax.set_ylim([0.0, 1.02])
    plt.tight_layout()
    fig_path = FIGURES_DIR / "figure_a_oracle_envelope_spectrum.png"
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Saved {fig_path}")

    # Figure B: Envelope Capture vs K on Held-out Images
    fig, ax = plt.subplots(figsize=(8, 5))
    for m_key, grp in df_env.groupby("architecture"):
        ax.plot(grp["envelope_K"], grp["mean_capture"] * 100, marker="o", lw=2.2, label=m_key, color=palette.get(m_key, "black"))
        ax.fill_between(grp["envelope_K"], grp["q10_capture"] * 100, grp["q90_capture"] * 100, alpha=0.15, color=palette.get(m_key, "black"))
    ax.axhline(80.0, color="gray", linestyle="--", label="Target >= 80% Capture (Level L1)")
    ax.set_xlabel("Shared Envelope Dimension (K)")
    ax.set_ylabel("Held-out Oracle Subspace Capture (%)")
    ax.set_title("Figure B: Subspace Envelope Capture vs K (10th-90th Percentile Bands)")
    ax.legend(loc="lower right")
    ax.set_ylim([0, 100])
    plt.tight_layout()
    fig_path = FIGURES_DIR / "figure_b_envelope_capture.png"
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Saved {fig_path}")

    # Figure C: Token vs Feature Variability Decomposition
    fig, ax = plt.subplots(figsize=(10, 5))
    cfg_labels = {
        "A_DynamicToken_StaticFeature": "Dyn Token + Stat Feat\n(Cost: N×r)",
        "B_StaticToken_DynamicFeature": "Stat Token + Dyn Feat\n(Cost: D×r)",
        "C_BothDynamic_Factorized": "Both Dynamic\n(Cost: (N+D)×r)",
        "D_BothStatic_Baseline": "Both Static\n(Cost: 0)"
    }
    df_plot = df_factor.copy()
    df_plot["config_label"] = df_plot["configuration"].map(cfg_labels)
    df_plot["mean_overlap_pct"] = df_plot["mean_overlap"] * 100

    sns.barplot(data=df_plot, x="config_label", y="mean_overlap_pct", hue="architecture", ax=ax, palette=palette)
    ax.set_xlabel("Factor Decomposition Configuration")
    ax.set_ylabel("Held-out Subspace Overlap (%)")
    ax.set_title("Figure C: Token-Side vs Feature-Side Asymmetry in Operator Geometry")
    ax.legend(title="Architecture", loc="upper left")
    ax.set_ylim([0, 95])
    plt.tight_layout()
    fig_path = FIGURES_DIR / "figure_c_token_vs_feature_variability.png"
    fig.savefig(fig_path, dpi=300)
    plt.close(fig)
    print(f"Saved {fig_path}")


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    
    df_env, spectrum_data = run_phase_1a_envelope_analysis(device)
    df_factor = run_phase_1b_factor_variability(device)
    plot_phase_1_figures(df_env, spectrum_data, df_factor)
    print("\nPhase 1 Analysis Complete!")


if __name__ == "__main__":
    main()
