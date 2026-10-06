"""
patch_fungibility/lightweight_operator_predictor.py

Core implementation for Lightweight Operator Predictors in Vision Transformers:
- Phase 1: Shared Envelope Extraction & Factor Variability Analysis
- Model A: Global Envelope Coefficient Predictor (U_K * C(x))
- Model B: Shared Basis + Low-Rank Residual Deformation (V_0 + sum_k alpha_k(x) Delta V_k)
- Model C: Subspace Prototype Codebook / Mixture
- Model D: One-Sided Dynamic Factorization (Static Feature + Dynamic Token, or vice versa)
- Subspace-invariant Grassmannian loss and evaluation metrics
"""

import math
from typing import Dict, List, Tuple, Optional, Union
import torch
import torch.nn as nn
import torch.nn.functional as F


def compute_subspace_overlap(V1: torch.Tensor, V2: torch.Tensor) -> torch.Tensor:
    """
    Computes basis-independent subspace overlap:
    overlap = ||V1^T V2||_F^2 / r in [0, 1]
    Supports unbatched (ND, r) or batched (B, ND, r).
    """
    orig_dtype = V1.dtype
    if V1.dtype == torch.float16 or V2.dtype == torch.float16:
        V1 = V1.float()
        V2 = V2.float()

    if V1.dim() == 2 and V2.dim() == 2:
        M = torch.matmul(V1.t(), V2)
        r = float(V1.shape[1])
        res = (torch.norm(M, p="fro") ** 2) / r
    elif V1.dim() == 3 and V2.dim() == 3:
        M = torch.bmm(V1.transpose(1, 2), V2)
        r = float(V1.shape[-1])
        res = (torch.norm(M, p="fro", dim=(-2, -1)) ** 2) / r
    elif V1.dim() == 2 and V2.dim() == 3:
        B = V2.shape[0]
        V1_exp = V1.unsqueeze(0).expand(B, -1, -1)
        M = torch.bmm(V1_exp.transpose(1, 2), V2)
        r = float(V1.shape[-1])
        res = (torch.norm(M, p="fro", dim=(-2, -1)) ** 2) / r
    else:
        raise ValueError(f"Incompatible dimensions: V1 {V1.shape}, V2 {V2.shape}")

    return res.to(orig_dtype)


def compute_principal_angles(V1: torch.Tensor, V2: torch.Tensor) -> torch.Tensor:
    """
    Computes cosines of principal angles: cos(theta_k) = sigma_k(V1^T V2).
    Returns tensor of shape (r,) or (B, r) in descending order.
    """
    V1_f = V1.float()
    V2_f = V2.float()
    if V1_f.dim() == 2 and V2_f.dim() == 2:
        M = torch.matmul(V1_f.t(), V2_f)
        S = torch.linalg.svdvals(M)
        return torch.clamp(S, 0.0, 1.0)
    elif V1_f.dim() == 3 and V2_f.dim() == 3:
        M = torch.bmm(V1_f.transpose(1, 2), V2_f)
        S = torch.linalg.svdvals(M)
        return torch.clamp(S, 0.0, 1.0)
    elif V1_f.dim() == 2 and V2_f.dim() == 3:
        B = V2_f.shape[0]
        V1_exp = V1_f.unsqueeze(0).expand(B, -1, -1)
        M = torch.bmm(V1_exp.transpose(1, 2), V2_f)
        S = torch.linalg.svdvals(M)
        return torch.clamp(S, 0.0, 1.0)
    else:
        raise ValueError(f"Incompatible dimensions: V1 {V1.shape}, V2 {V2.shape}")


def compute_envelope_capture(U_K: torch.Tensor, V: torch.Tensor) -> torch.Tensor:
    """
    Measures the fraction of subspace energy captured by shared orthonormal envelope U_K:
    capture = ||U_K^T V||_F^2 / r
    U_K: (ND, K) orthonormal basis
    V: (ND, r) or (B, ND, r)
    """
    orig_dtype = V.dtype
    U_K_f = U_K.float()
    V_f = V.float()
    if V_f.dim() == 2:
        proj = torch.matmul(U_K_f.t(), V_f)  # (K, r)
        r = float(V_f.shape[1])
        res = (torch.norm(proj, p="fro") ** 2) / r
    elif V_f.dim() == 3:
        B = V_f.shape[0]
        U_exp = U_K_f.unsqueeze(0).expand(B, -1, -1)  # (B, ND, K)
        proj = torch.bmm(U_exp.transpose(1, 2), V_f)  # (B, K, r)
        r = float(V_f.shape[-1])
        res = (torch.norm(proj, p="fro", dim=(-2, -1)) ** 2) / r
    else:
        raise ValueError(f"Unsupported V dim: {V.dim()}")
    return res.to(orig_dtype)


def subspace_grassmann_loss(V_pred: torch.Tensor, V_true: torch.Tensor) -> torch.Tensor:
    """
    Projection / Grassmannian loss:
    L = 1 - ||V_true^T V_pred||_F^2 / r
    Differentiable and invariant to internal orthonormal rotations of both bases.
    """
    overlap = compute_subspace_overlap(V_pred, V_true)
    return 1.0 - overlap.mean()


def extract_shared_envelope_svd(V_stack: torch.Tensor, K_max: int = 128, niter: int = 4) -> torch.Tensor:
    """
    Extracts top K_max orthonormal shared envelope from stacked training oracle bases.
    V_stack: (ND, M * r)
    Uses randomized SVD in float32 for numerical stability.
    """
    orig_dtype = V_stack.dtype
    V_stack_f = V_stack.float()
    ND, total_cols = V_stack_f.shape
    K_target = min(K_max, total_cols)
    U, S, V = torch.svd_lowrank(V_stack_f, q=K_target, niter=niter)
    return U[:, :K_target].contiguous().to(orig_dtype)


class ModelA_EnvelopeCoefficientPredictor(nn.Module):
    """
    Model A: Global Envelope Coefficient Predictor
    V_hat(x) = orth(U_K * C(x))
    where U_K in R^(ND x K) is fixed, and C(x) in R^(K x r) is predicted.
    """
    def __init__(self, U_K: torch.Tensor, d_in: int, r: int, hidden_dim: int = 256):
        super().__init__()
        ND, K = U_K.shape
        self.register_buffer("U_K", U_K.contiguous().float())
        self.ND = ND
        self.K = K
        self.r = r
        
        self.mlp = nn.Sequential(
            nn.Linear(d_in, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, K * r)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input x: (B, d_in) - e.g. pooled [cls; mean(patches)]
        Returns: (B, ND, r) orthonormal basis
        """
        if x.dim() == 3:
            cls_tok = x[:, 0, :]
            patch_mean = x[:, 1:, :].mean(dim=1)
            x = torch.cat([cls_tok, patch_mean], dim=-1)
        B = x.shape[0]
        c = self.mlp(x).float().view(B, self.K, self.r)  # (B, K, r)
        
        # Batch multiply: U_K is (ND, K), c is (B, K, r) -> V_raw is (B, ND, r)
        U_exp = self.U_K.unsqueeze(0).expand(B, -1, -1)
        V_raw = torch.bmm(U_exp, c)
        
        # Orthonormalize via QR in float32
        Q, R = torch.linalg.qr(V_raw)
        return Q.to(x.dtype)


class ModelB_ResidualBasisPredictor(nn.Module):
    """
    Model B: Shared Basis + Low-Rank Residual / Deformation
    V_hat(x) = orth(V_0 + sum_{k=1}^K alpha_k(x) Delta V_k)
    Predicts only alpha(x) in R^K (e.g. K in {8, 16, 32, 64}).
    """
    def __init__(self, V_0: torch.Tensor, Delta_V: torch.Tensor, d_in: int, hidden_dim: int = 128):
        super().__init__()
        ND, r = V_0.shape
        K = Delta_V.shape[0]
        self.register_buffer("V_0", V_0.contiguous().float())
        self.register_buffer("Delta_V", Delta_V.contiguous().float())
        self.ND = ND
        self.r = r
        self.K = K
        
        self.mlp = nn.Sequential(
            nn.Linear(d_in, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, K)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 3:
            cls_tok = x[:, 0, :]
            patch_mean = x[:, 1:, :].mean(dim=1)
            x = torch.cat([cls_tok, patch_mean], dim=-1)
        B = x.shape[0]
        alpha = self.mlp(x).float()  # (B, K)
        
        Delta_flat = self.Delta_V.view(self.K, self.ND * self.r)
        perturb_flat = torch.matmul(alpha, Delta_flat)
        perturb = perturb_flat.view(B, self.ND, self.r)
        
        V_raw = self.V_0.unsqueeze(0) + perturb
        Q, R = torch.linalg.qr(V_raw)
        return Q.to(x.dtype)


class ModelC_SubspaceMixturePredictor(nn.Module):
    """
    Model C: Subspace Prototype Codebook / Mixture
    Stores M prototype subspaces P_m in R^(ND x r).
    Predicts routing logits w(x) in R^M.
    Supports hard selection, top-2 mixture, and soft mixture.
    """
    def __init__(self, prototypes: torch.Tensor, d_in: int, mode: str = "soft"):
        super().__init__()
        M, ND, r = prototypes.shape
        self.register_buffer("prototypes", prototypes.contiguous().float())
        self.M = M
        self.ND = ND
        self.r = r
        self.mode = mode
        
        self.router = nn.Sequential(
            nn.Linear(d_in, 128),
            nn.GELU(),
            nn.Linear(128, M)
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 3:
            cls_tok = x[:, 0, :]
            patch_mean = x[:, 1:, :].mean(dim=1)
            x = torch.cat([cls_tok, patch_mean], dim=-1)
        B = x.shape[0]
        logits = self.router(x).float()  # (B, M)
        weights = F.softmax(logits, dim=-1)  # (B, M)
        
        if self.mode == "hard":
            top1_idx = torch.argmax(weights, dim=-1)  # (B,)
            return self.prototypes[top1_idx].to(x.dtype)
            
        elif self.mode == "top2":
            top2_vals, top2_idx = torch.topk(weights, k=2, dim=-1)
            top2_norm = top2_vals / top2_vals.sum(dim=-1, keepdim=True)
            P1 = self.prototypes[top2_idx[:, 0]]
            P2 = self.prototypes[top2_idx[:, 1]]
            w1 = top2_norm[:, 0].view(B, 1, 1)
            w2 = top2_norm[:, 1].view(B, 1, 1)
            V_raw = w1 * P1 + w2 * P2
            Q, R = torch.linalg.qr(V_raw)
            return Q.to(x.dtype)
            
        else:  # soft mixture
            proto_flat = self.prototypes.view(self.M, self.ND * self.r)
            V_flat = torch.matmul(weights, proto_flat)
            V_raw = V_flat.view(B, self.ND, self.r)
            Q, R = torch.linalg.qr(V_raw)
            return Q.to(x.dtype)


class ModelD_OneSidedFactorizedPredictor(nn.Module):
    """
    Model D: One-Sided Dynamic Factorization
    Variant 1 ('static_feature'): Static feature basis B_0 in R^(D x r), dynamic token factors A(x) in R^(N x r).
    Variant 2 ('static_token'): Static token basis A_0 in R^(N x r), dynamic feature factors B(x) in R^(D x r).
    """
    def __init__(self, N: int, D: int, r: int, d_in: int, variant: str = "static_feature",
                 static_basis: Optional[torch.Tensor] = None, hidden_dim: int = 256):
        super().__init__()
        self.N = N
        self.D = D
        self.r = r
        self.variant = variant
        
        if variant == "static_feature":
            if static_basis is None:
                static_basis = torch.randn(D, r)
                static_basis, _ = torch.linalg.qr(static_basis)
            self.register_buffer("static_basis", static_basis.contiguous().float())
            self.mlp = nn.Sequential(
                nn.Linear(d_in, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, N * r)
            )
        elif variant == "static_token":
            if static_basis is None:
                static_basis = torch.randn(N, r)
                static_basis, _ = torch.linalg.qr(static_basis)
            self.register_buffer("static_basis", static_basis.contiguous().float())
            self.mlp = nn.Sequential(
                nn.Linear(d_in, hidden_dim),
                nn.GELU(),
                nn.Linear(hidden_dim, D * r)
            )
        else:
            raise ValueError(f"Unknown variant: {variant}")

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        if x.dim() == 3:
            cls_tok = x[:, 0, :]
            patch_mean = x[:, 1:, :].mean(dim=1)
            x = torch.cat([cls_tok, patch_mean], dim=-1)
        B = x.shape[0]
        if self.variant == "static_feature":
            A = self.mlp(x).float().view(B, self.N, self.r)  # (B, N, r)
            V_modes = []
            for k in range(self.r):
                a_k = A[:, :, k].unsqueeze(2)  # (B, N, 1)
                b_k = self.static_basis[:, k].view(1, 1, self.D).expand(B, -1, -1)  # (B, 1, D)
                mode_k = torch.bmm(a_k, b_k).view(B, self.N * self.D)  # (B, ND)
                V_modes.append(mode_k)
            V_raw = torch.stack(V_modes, dim=-1)  # (B, ND, r)
        else:
            B_feat = self.mlp(x).float().view(B, self.D, self.r)  # (B, D, r)
            V_modes = []
            for k in range(self.r):
                a_k = self.static_basis[:, k].view(1, self.N, 1).expand(B, -1, -1)  # (B, N, 1)
                b_k = B_feat[:, :, k].unsqueeze(1)  # (B, 1, D)
                mode_k = torch.bmm(a_k, b_k).view(B, self.N * self.D)  # (B, ND)
                V_modes.append(mode_k)
            V_raw = torch.stack(V_modes, dim=-1)  # (B, ND, r)

        Q, R = torch.linalg.qr(V_raw)
        return Q.to(x.dtype)


def count_parameters_and_flops(module: nn.Module, input_shape: Tuple[int, ...]) -> Tuple[int, float]:
    """
    Computes parameter count and forward FLOPs for a predictor module.
    """
    param_count = sum(p.numel() for p in module.parameters() if p.requires_grad)
    flops = 0.0
    for m in module.modules():
        if isinstance(m, nn.Linear):
            flops += 2.0 * m.in_features * m.out_features
    return param_count, flops
