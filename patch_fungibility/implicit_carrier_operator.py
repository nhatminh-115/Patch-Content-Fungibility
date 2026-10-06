"""
patch_fungibility/implicit_carrier_operator.py

Core implementation for Implicit / Carrier-Space Operator Solving and Selective Activation:
- Phase 1 & 2: Minimal Carrier-Space Formulation and Restricted Subspace (q in {4, 8, 16, 32, 64})
- Phase 3: Cheap Analytic Correction Bases R(x, S) (Residual, PCA, Statistical, Hybrid, Control)
- Phase 4: Exact Oracle Restricted Carrier Solver without ambient basis materialization
- Phase 5 & 6: Neural Sufficient-Statistic Predictors (alpha, g-only, diag(H)+g, full H+g)
- Phase 8 & 9: Selective Operator Activation Gate (Margin, Residual Norm, Variance Risk)
"""

import math
from typing import Dict, List, Tuple, Optional, Union
import torch
import torch.nn as nn
import torch.nn.functional as F


def construct_analytic_correction_basis(
    P: torch.Tensor,
    S: torch.Tensor,
    m: torch.Tensor,
    q: int = 16,
    basis_type: str = "group_residual",
    pca_basis: Optional[torch.Tensor] = None
) -> torch.Tensor:
    """
    Constructs an analytic carrier correction basis R of shape (BS, B, D, q).
    For each mode k in 1..q, R[..., k] in R^(B x D) is a candidate direction of carrier adjustment.
    
    Arguments:
    - P: (BS, N, D) uncompressed patch activations
    - S: (N, B) binary grouping matrix
    - m: (B,) cluster token counts
    - q: correction subspace dimension (e.g. 4, 8, 16, 32, 64)
    - basis_type: 'group_residual', 'feature_pca', 'group_statistics', 'hybrid_semantic', 'random_control'
    - pca_basis: optional (D, q) fixed PCA basis
    
    Returns:
    - R: (BS, B, D, q) tensor of correction directions with normalized columns
    """
    if P.dim() == 2:
        P = P.unsqueeze(0)
    BS, N, D = P.shape
    B_tok = S.shape[1]
    device = P.device
    dtype = P.dtype

    # Base Group Mean: (BS, B, D)
    m_safe = m.view(1, B_tok, 1).clamp(min=1.0)
    S_b = S.unsqueeze(0).expand(BS, -1, -1)
    C_mean = torch.bmm(S_b.transpose(1, 2), P) / m_safe

    # Within-group patch residuals: (BS, N, D)
    recon = torch.bmm(S_b, C_mean)
    resids = P - recon

    R = torch.zeros(BS, B_tok, D, q, device=device, dtype=dtype)

    if basis_type == "group_residual":
        # Group-residual SVD directions:
        # Find dominant residual feature directions across the batch
        # resids is (BS, N, D) -> reshape to (BS*N, D)
        # SVD on CPU / lowrank on GPU for speed
        resids_2d = resids.view(-1, D)
        q_feat = min(q, D)
        try:
            _, _, Vh = torch.linalg.svd(resids_2d[:1000], full_matrices=False)
            feat_dirs = Vh[:q_feat, :].t() # (D, q_feat)
        except Exception:
            feat_dirs = torch.randn(D, q_feat, device=device, dtype=dtype)
            feat_dirs, _ = torch.linalg.qr(feat_dirs)

        # Broadcast feature directions across all groups
        # R[b, j, d, k] = feat_dirs[d, k]
        for k in range(q_feat):
            R[:, :, :, k] = feat_dirs[:, k].view(1, 1, D).expand(BS, B_tok, D)

    elif basis_type == "feature_pca":
        if pca_basis is not None:
            q_feat = min(q, pca_basis.shape[1])
            feat_dirs = pca_basis[:, :q_feat].to(device=device, dtype=dtype)
        else:
            P_2d = P.view(-1, D)
            _, _, Vh = torch.linalg.svd(P_2d[:1000], full_matrices=False)
            q_feat = min(q, D)
            feat_dirs = Vh[:q_feat, :].t()

        for k in range(q_feat):
            R[:, :, :, k] = feat_dirs[:, k].view(1, 1, D).expand(BS, B_tok, D)

    elif basis_type == "group_statistics":
        # Combines:
        # 1. Group mean directions C_mean (normalized)
        # 2. Residual variance directions
        # 3. Residual mean directions
        q_quarter = max(1, q // 4)
        c_norm = F.normalize(C_mean, p=2, dim=-1) # (BS, B, D)
        for k in range(min(q_quarter, q)):
            R[:, :, :, k] = c_norm

        # Residual variance per group: (BS, B, D)
        res_sq = torch.bmm(S_b.transpose(1, 2), resids ** 2) / m_safe
        res_sq_norm = F.normalize(res_sq, p=2, dim=-1)
        for k in range(q_quarter, min(2 * q_quarter, q)):
            R[:, :, :, k] = res_sq_norm

        # Global residual directions for remaining slots
        resids_2d = resids.view(-1, D)
        _, _, Vh = torch.linalg.svd(resids_2d[:500], full_matrices=False)
        rem = q - 2 * q_quarter
        if rem > 0:
            feat_dirs = Vh[:rem, :].t()
            for idx, k in enumerate(range(2 * q_quarter, q)):
                R[:, :, :, k] = feat_dirs[:, idx].view(1, 1, D).expand(BS, B_tok, D)

    elif basis_type == "hybrid_semantic":
        # Group mean diffs + residual PCA
        mean_diff = C_mean - C_mean.mean(dim=1, keepdim=True)
        mean_diff_norm = F.normalize(mean_diff, p=2, dim=-1)
        q_half = q // 2
        for k in range(q_half):
            R[:, :, :, k] = mean_diff_norm

        resids_2d = resids.view(-1, D)
        _, _, Vh = torch.linalg.svd(resids_2d[:500], full_matrices=False)
        rem = q - q_half
        feat_dirs = Vh[:rem, :].t()
        for idx, k in enumerate(range(q_half, q)):
            R[:, :, :, k] = feat_dirs[:, idx].view(1, 1, D).expand(BS, B_tok, D)

    else:  # random_control
        R = torch.randn(BS, B_tok, D, q, device=device, dtype=dtype)

    # Normalize each candidate direction across (B * D)
    R_flat = R.view(BS, B_tok * D, q)
    R_norms = torch.norm(R_flat, p=2, dim=1, keepdim=True).clamp(min=1e-6)
    R_flat = R_flat / R_norms
    return R_flat.view(BS, B_tok, D, q)


def compute_restricted_carrier_oracle_quantities(
    V_true: torch.Tensor,
    P: torch.Tensor,
    S: torch.Tensor,
    m: torch.Tensor,
    R: torch.Tensor,
    lam: float = 1e-3
) -> Dict[str, torch.Tensor]:
    """
    Computes exact restricted carrier oracle quantities (H_q, g_q, alpha*, delta_C*, C*):
    H_q = K_R^T K_R in R^(BS x q x q)
    g_q = K_R^T (V_true^T e_0) in R^(BS x q)
    where K_R = V_true^T (A_S R) in R^(BS x r x q).
    
    Arguments:
    - V_true: (BS, ND, r) oracle operator basis
    - P: (BS, N, D) patch activations
    - S: (N, B) grouping matrix
    - m: (B,) cluster counts
    - R: (BS, B, D, q) analytic correction basis
    - lam: Tikhonov regularization factor
    
    Returns:
    - H_q: (BS, q, q)
    - g_q: (BS, q)
    - alpha_star: (BS, q)
    - C_opt: (BS, B, D)
    - delta_C: (BS, B, D)
    - C_mean: (BS, B, D)
    """
    BS, N, D = P.shape
    ND = N * D
    B_tok = S.shape[1]
    q = R.shape[-1]
    r = V_true.shape[-1]
    device = P.device
    dtype = P.dtype
    V_true = V_true.to(dtype=dtype, device=device)

    # 1. Base Group Mean and Residual
    m_safe = m.view(1, B_tok, 1).clamp(min=1.0)
    S_b = S.unsqueeze(0).expand(BS, -1, -1) # (BS, N, B)
    C_mean = torch.bmm(S_b.transpose(1, 2), P) / m_safe # (BS, B, D)
    recon = torch.bmm(S_b, C_mean) # (BS, N, D)
    e_0 = (P - recon).reshape(BS, ND, 1) # (BS, ND, 1)

    # 2. Compute K_R = V_true^T (A_S R) in R^(BS x r x q) directly without materializing AS_R
    K_R_list = []
    for k in range(q):
        R_k = R[:, :, :, k] # (BS, B, D)
        SR_k = torch.bmm(S_b, R_k) # (BS, N, D)
        vec_SR_k = SR_k.reshape(BS, ND, 1)
        kr_k = torch.bmm(V_true.transpose(1, 2), vec_SR_k).squeeze(-1) # (BS, r)
        K_R_list.append(kr_k)
    K_R = torch.stack(K_R_list, dim=-1) # (BS, r, q)

    # 4. Form exact H_q = K_R^T K_R and g_q = K_R^T (V_true^T e_0)
    H_q = torch.bmm(K_R.transpose(1, 2), K_R) # (BS, q, q)
    H_q = 0.5 * (H_q + H_q.transpose(1, 2))

    v_e0 = torch.bmm(V_true.transpose(1, 2), e_0).squeeze(-1) # (BS, r)
    g_q = torch.bmm(K_R.transpose(1, 2), v_e0.unsqueeze(-1)).squeeze(-1) # (BS, q)

    # 5. Solve (H_q + lam * I) alpha* = g_q in R^q
    eye_q = torch.eye(q, device=device, dtype=dtype).unsqueeze(0).expand(BS, -1, -1)
    H_reg = H_q + lam * eye_q
    try:
        L = torch.linalg.cholesky(H_reg)
        alpha_star = torch.cholesky_solve(g_q.unsqueeze(-1), L).squeeze(-1)
    except torch._C._LinAlgError:
        alpha_star = torch.linalg.solve(H_reg + 1e-2 * eye_q, g_q.unsqueeze(-1)).squeeze(-1)

    # 6. Reconstruct delta_C = sum_k alpha*_k R_k
    # R is (BS, B, D, q), alpha_star is (BS, q)
    delta_C = torch.einsum('bq,bjgq->bjg', alpha_star, R) # (BS, B, D)
    C_opt = C_mean + delta_C

    return {
        "H_q": H_q,
        "g_q": g_q,
        "alpha_star": alpha_star,
        "C_mean": C_mean,
        "C_opt": C_opt,
        "delta_C": delta_C
    }


def solve_restricted_carrier_from_hg(
    H_q: torch.Tensor,
    g_q: torch.Tensor,
    R: torch.Tensor,
    C_mean: torch.Tensor,
    lam: float = 1e-3
) -> Dict[str, torch.Tensor]:
    """
    Solves for delta_C given small (q x q) Hessian H_q and gradient g_q.
    """
    BS = g_q.shape[0]
    q = g_q.shape[-1]
    device = g_q.device
    dtype = g_q.dtype

    eye_q = torch.eye(q, device=device, dtype=dtype).unsqueeze(0).expand(BS, -1, -1)
    H_reg = H_q + lam * eye_q
    try:
        L = torch.linalg.cholesky(H_reg)
        alpha = torch.cholesky_solve(g_q.unsqueeze(-1), L).squeeze(-1)
    except torch._C._LinAlgError:
        alpha = torch.linalg.solve(H_reg + 1e-2 * eye_q, g_q.unsqueeze(-1)).squeeze(-1)

    delta_C = torch.einsum('bq,bjgq->bjg', alpha, R)
    C_opt = C_mean + delta_C
    return {
        "alpha": alpha,
        "C_opt": C_opt,
        "delta_C": delta_C
    }


class CarrierStatisticsPredictor(nn.Module):
    """
    Lightweight neural predictor for carrier sufficient statistics:
    - Mode 'alpha': predicts alpha in R^q directly (output dim = q)
    - Mode 'g_only': predicts g in R^q with static H_bar (output dim = q)
    - Mode 'diag_h_g': predicts diag(H) and g (output dim = 2q)
    - Mode 'full_h_g': predicts Cholesky L of H and g (output dim = q(q+1)/2 + q)
    """
    def __init__(self, d_in: int, q: int = 16, mode: str = "alpha", hidden_dim: int = 256):
        super().__init__()
        self.d_in = d_in
        self.q = q
        self.mode = mode

        if mode in ("alpha", "g_only"):
            out_dim = q
        elif mode == "diag_h_g":
            out_dim = 2 * q
        elif mode == "full_h_g":
            out_dim = (q * (q + 1)) // 2 + q
        else:
            raise ValueError(f"Unknown mode: {mode}")

        self.out_dim = out_dim
        self.mlp = nn.Sequential(
            nn.Linear(d_in, hidden_dim),
            nn.LayerNorm(hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, out_dim)
        )

        # Buffer for static H if g_only mode
        if mode == "g_only":
            self.register_buffer("static_H", torch.eye(q))

    def forward(self, x: torch.Tensor) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor]]:
        if x.dim() == 3:
            cls_tok = x[:, 0, :]
            patch_mean = x[:, 1:, :].mean(dim=1)
            x = torch.cat([cls_tok, patch_mean], dim=-1)
        BS = x.shape[0]
        out = self.mlp(x)

        if self.mode in ("alpha", "g_only"):
            return out  # (BS, q)
        elif self.mode == "diag_h_g":
            diag_h = F.softplus(out[:, :self.q]) + 1e-4  # ensure positive
            g = out[:, self.q:]
            H = torch.diag_embed(diag_h)
            return H, g
        else:  # full_h_g
            n_chol = (self.q * (self.q + 1)) // 2
            chol_params = out[:, :n_chol]
            g = out[:, n_chol:]
            # Reconstruct positive-definite H = L L^T
            L = torch.zeros(BS, self.q, self.q, device=x.device, dtype=x.dtype)
            tril_idx = torch.tril_indices(self.q, self.q)
            L[:, tril_idx[0], tril_idx[1]] = chol_params
            diag_idx = torch.arange(self.q)
            L[:, diag_idx, diag_idx] = F.softplus(L[:, diag_idx, diag_idx]) + 1e-4
            H = torch.bmm(L, L.transpose(1, 2))
            return H, g


class SelectiveOperatorGate(nn.Module):
    """
    Lightweight Adaptive Gate for selective operator activation.
    Evaluates compression risk:
    risk(x) = w1 * margin_risk + w2 * norm_risk + w3 * var_risk
    Zero ground-truth labels used.
    """
    def __init__(self, D: int = 384):
        super().__init__()
        self.D = D
        # Calibrated weights
        self.w_norm = nn.Parameter(torch.tensor(0.5))
        self.w_var = nn.Parameter(torch.tensor(0.5))

    def compute_risk_score(
        self,
        P: torch.Tensor,
        S: torch.Tensor,
        m: torch.Tensor,
        prefix_logits: Optional[torch.Tensor] = None
    ) -> torch.Tensor:
        """
        Computes scalar risk score in [0, 1] per image in batch.
        """
        BS, N, D = P.shape
        B_tok = S.shape[1]
        m_safe = m.view(1, B_tok, 1).clamp(min=1.0)
        S_b = S.unsqueeze(0).expand(BS, -1, -1)

        # 1. Normalized within-group residual norm: ||P - S C_mean||_F / ||P||_F
        C_mean = torch.bmm(S_b.transpose(1, 2), P) / m_safe
        recon = torch.bmm(S_b, C_mean)
        resids = P - recon
        norm_risk = (resids.norm(dim=(-2, -1)) / P.norm(dim=(-2, -1)).clamp(min=1e-6)).clamp(0.0, 1.0)

        # 2. Patch feature variance risk
        patch_var = P.var(dim=1).mean(dim=-1)
        var_risk = torch.sigmoid(patch_var - patch_var.mean())

        # 3. Optional margin risk from prefix proxy logits
        if prefix_logits is not None:
            top2 = torch.topk(F.softmax(prefix_logits, dim=-1), k=2, dim=-1).values
            margin = top2[:, 0] - top2[:, 1]
            margin_risk = (1.0 - margin).clamp(0.0, 1.0)
            risk = 0.4 * norm_risk + 0.3 * var_risk + 0.3 * margin_risk
        else:
            risk = 0.6 * norm_risk + 0.4 * var_risk

        return risk

    def forward(
        self,
        P: torch.Tensor,
        S: torch.Tensor,
        m: torch.Tensor,
        threshold: float = 0.5,
        prefix_logits: Optional[torch.Tensor] = None
    ) -> Tuple[torch.Tensor, torch.Tensor]:
        risk = self.compute_risk_score(P, S, m, prefix_logits)
        is_active = risk > threshold
        return risk, is_active
