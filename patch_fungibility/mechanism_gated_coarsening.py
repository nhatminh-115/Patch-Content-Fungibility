"""Fixed 2x2 spatial coarsening and mechanism diagnostics for the pilot."""

from __future__ import annotations

import math
from dataclasses import dataclass

import torch
import torch.nn.functional as F


GRID_SIDE = 14
CELL_SIDE = 2
NUM_PATCHES = GRID_SIDE * GRID_SIDE
NUM_CELLS = (GRID_SIDE // CELL_SIDE) ** 2
PREFIX_LAST_BLOCK = 6
SUFFIX_FIRST_BLOCK = 7
NUM_BLOCKS = 12


def pool_2x2(patch_tokens: torch.Tensor, grid_side: int = GRID_SIDE) -> torch.Tensor:
    """Mean-pool [B, grid_side**2, D] on fixed nonoverlapping 2x2 cells."""
    if patch_tokens.ndim != 3 or patch_tokens.shape[1] != grid_side * grid_side:
        raise ValueError("Expected patch tokens shaped [B, grid_side**2, D]")
    if grid_side % 2:
        raise ValueError("Grid side must be divisible by two")
    batch, _, width = patch_tokens.shape
    side = grid_side // 2
    return (
        patch_tokens.reshape(batch, side, 2, side, 2, width)
        .mean(dim=(2, 4))
        .reshape(batch, side * side, width)
    )


def pool_2x2_reference(patch_tokens: torch.Tensor, grid_side: int = GRID_SIDE) -> torch.Tensor:
    """Independent slice-and-stack reference used only for parity checks."""
    if patch_tokens.ndim != 3 or patch_tokens.shape[1] != grid_side * grid_side:
        raise ValueError("Expected patch tokens shaped [B, grid_side**2, D]")
    batch, _, width = patch_tokens.shape
    grid = patch_tokens.reshape(batch, grid_side, grid_side, width)
    return torch.stack(
        (grid[:, 0::2, 0::2], grid[:, 0::2, 1::2],
         grid[:, 1::2, 0::2], grid[:, 1::2, 1::2]),
        dim=0,
    ).mean(dim=0).reshape(batch, (grid_side // 2) ** 2, width)


def pool_with_cls(tokens: torch.Tensor) -> torch.Tensor:
    """Preserve CLS and replace 196 patch tokens by 49 fixed cell means."""
    if tokens.ndim != 3 or tokens.shape[1] != NUM_PATCHES + 1:
        raise ValueError("Expected [B, 197, D] tokens including CLS")
    patches = pool_2x2(tokens[:, 1:])
    return torch.cat((tokens[:, :1], patches), dim=1)


def suffix_key_bias(reference: torch.Tensor) -> torch.Tensor:
    """Additive attention mask restoring multiplicity under equal logits."""
    bias = reference.new_full((1, 1, 1, NUM_CELLS + 1), math.log(4.0))
    bias[..., 0] = 0.0
    return bias


def cell_values(values: torch.Tensor) -> torch.Tensor:
    """Convert [B,H,196,Dh] values to [B,H,49,4,Dh] cell order."""
    if values.ndim != 4 or values.shape[2] != NUM_PATCHES:
        raise ValueError("Expected patch values shaped [B,H,196,Dh]")
    b, h, _, d = values.shape
    return (
        values.reshape(b, h, GRID_SIDE // 2, 2, GRID_SIDE // 2, 2, d)
        .permute(0, 1, 2, 4, 3, 5, 6)
        .reshape(b, h, NUM_CELLS, 4, d)
    )


def cell_scalars(values: torch.Tensor) -> torch.Tensor:
    """Convert [B,H,196] patch scalars to [B,H,49,4] cell order."""
    if values.ndim != 3 or values.shape[2] != NUM_PATCHES:
        raise ValueError("Expected patch scalars shaped [B,H,196]")
    b, h, _ = values.shape
    return (
        values.reshape(b, h, GRID_SIDE // 2, 2, GRID_SIDE // 2, 2)
        .permute(0, 1, 2, 4, 3, 5)
        .reshape(b, h, NUM_CELLS, 4)
    )


def _prefix_tokens(model, images: torch.Tensor) -> torch.Tensor:
    x = model.patch_embed(images)
    x = model._pos_embed(x)
    x = model.patch_drop(x)
    x = model.norm_pre(x)
    for block_idx in range(PREFIX_LAST_BLOCK + 1):
        x = model.blocks[block_idx](x)
    return x


def _suffix_tokens(model, tokens: torch.Tensor, compressed: bool) -> torch.Tensor:
    x = tokens
    bias = suffix_key_bias(x) if compressed else None
    for block_idx in range(SUFFIX_FIRST_BLOCK, NUM_BLOCKS):
        x = model.blocks[block_idx](x, attn_mask=bias)
    return x


def forward_clean_manual(model, images: torch.Tensor) -> torch.Tensor:
    """Standard uncompressed forward with explicit block iteration."""
    x = model.patch_embed(images)
    x = model._pos_embed(x)
    x = model.patch_drop(x)
    x = model.norm_pre(x)
    for block in model.blocks:
        x = block(x)
    return model.forward_head(model.norm(x))


def forward_compressed(model, images: torch.Tensor) -> torch.Tensor:
    """Blocks 0–6 full, vectorized 2x2 pool, blocks 7–11 at 50 tokens."""
    prefix = _prefix_tokens(model, images)
    pooled = pool_with_cls(prefix)
    suffix = _suffix_tokens(model, pooled, compressed=True)
    return model.forward_head(model.norm(suffix))


def forward_compressed_with_omega(model, images: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Compressed logits plus differentiable pre-pool cellwise variance."""
    prefix = _prefix_tokens(model, images)
    with torch.autocast(device_type=prefix.device.type, enabled=False):
        omega, _ = omega_cell(model, prefix.float())
    pooled = pool_with_cls(prefix)
    suffix = _suffix_tokens(model, pooled, compressed=True)
    return model.forward_head(model.norm(suffix)), omega


def forward_from_block6(model, full_tokens: torch.Tensor, compressed: bool) -> torch.Tensor:
    """Continue from the output of block 6, optionally applying coarsening."""
    if full_tokens.ndim != 3 or full_tokens.shape[1] != NUM_PATCHES + 1:
        raise ValueError("Input must be the full 197-token block-6 output")
    start = pool_with_cls(full_tokens) if compressed else full_tokens
    suffix = _suffix_tokens(model, start, compressed=compressed)
    return model.forward_head(model.norm(suffix))


def forward_compressed_from_block6(model, full_tokens: torch.Tensor) -> torch.Tensor:
    """Continue from block 6 with the fixed coarsening intervention."""
    return forward_from_block6(model, full_tokens, compressed=True)


def omega_cell(model, block6_tokens: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
    """Return per-image Omega and per-head/cell within-cell logit variance."""
    block = model.blocks[SUFFIX_FIRST_BLOCK]
    attn = block.attn
    normed = block.norm1(block6_tokens)
    b, n, _ = normed.shape
    qkv = attn.qkv(normed).reshape(b, n, 3, attn.num_heads, attn.head_dim)
    q, k, _ = qkv.permute(2, 0, 3, 1, 4).unbind(0)
    q = attn.q_norm(q)
    k = attn.k_norm(k)
    logits = (q[:, :, :1] * attn.scale) @ k[:, :, 1:].transpose(-2, -1)
    cell_logits = cell_scalars(logits.squeeze(2))
    variance = (cell_logits - cell_logits.mean(dim=-1, keepdim=True)).square().mean(dim=-1)
    return variance.mean(dim=(1, 2)), variance


@dataclass
class MechanismBatch:
    omega: torch.Tensor
    attention_logit_std: torch.Tensor
    covariance_norm: torch.Tensor
    actual_attention_error: torch.Tensor
    block_output_error: torch.Tensor
    final_logit_distortion: torch.Tensor
    group_mass_tv: torch.Tensor
    pooled_key_mismatch: torch.Tensor
    pooled_value_mismatch: torch.Tensor
    full_entropy: torch.Tensor
    compressed_entropy: torch.Tensor
    covariance_ratio: torch.Tensor
    covariance_residual_max: torch.Tensor
    cell_omega: torch.Tensor
    cell_covariance_norm: torch.Tensor


def _layer_scale(block, x: torch.Tensor) -> torch.Tensor:
    return block.ls1(x)


def _relative_norm(delta: torch.Tensor, reference: torch.Tensor) -> torch.Tensor:
    return delta.flatten(start_dim=1).norm(dim=1) / (reference.flatten(start_dim=1).norm(dim=1) + 1e-12)


@torch.no_grad()
def mechanism_diagnostics(model, block6_tokens: torch.Tensor) -> MechanismBatch:
    """Measure exact frozen-attention identity and actual compressed operation."""
    if model.training:
        raise ValueError("Mechanism diagnostics require model.eval()")
    block = model.blocks[SUFFIX_FIRST_BLOCK]
    attn = block.attn
    if not isinstance(attn.norm, torch.nn.Identity):
        raise ValueError("This pilot's additive covariance projection assumes identity attention norm")
    b, n, _ = block6_tokens.shape
    norm_full = block.norm1(block6_tokens)
    pooled_tokens = pool_with_cls(block6_tokens)
    norm_pool = block.norm1(pooled_tokens)

    def qkv_parts(x):
        length = x.shape[1]
        qkv = attn.qkv(x).reshape(b, length, 3, attn.num_heads, attn.head_dim)
        q, k, v = qkv.permute(2, 0, 3, 1, 4).unbind(0)
        return attn.q_norm(q), attn.k_norm(k), v

    q_full, k_full, v_full = qkv_parts(norm_full)
    q_comp, k_comp, v_comp = qkv_parts(norm_pool)
    logits_full = (q_full[:, :, :1] * attn.scale) @ k_full.transpose(-2, -1)
    logits_comp = (q_comp[:, :, :1] * attn.scale) @ k_comp.transpose(-2, -1)
    prob_full = logits_full.softmax(dim=-1).squeeze(2)
    prob_comp = (logits_comp + suffix_key_bias(block6_tokens)).softmax(dim=-1).squeeze(2)

    omega, per_cell_omega = omega_cell(model, block6_tokens)
    full_patch_a = cell_scalars(prob_full[:, :, 1:])
    full_patch_v = cell_values(v_full[:, :, 1:])
    a_bar = full_patch_a.mean(dim=-1, keepdim=True)
    v_bar = full_patch_v.mean(dim=-2, keepdim=True)
    cov_head = ((full_patch_a - a_bar).unsqueeze(-1) * (full_patch_v - v_bar)).sum(dim=-2)
    full_group_mass = full_patch_a.sum(dim=-1)
    comp_group_mass = prob_comp[:, :, 1:]
    comp_value = v_comp[:, :, 1:]
    comp_cls_value = v_comp[:, :, :1]
    full_cls_value = v_full[:, :, :1]

    group_reroute = (full_group_mass - comp_group_mass).unsqueeze(-1) * v_bar.squeeze(-2)
    cls_reroute = (prob_full[:, :, :1] - prob_comp[:, :, :1]).unsqueeze(-1) * full_cls_value
    value_mismatch = comp_group_mass.unsqueeze(-1) * (
        v_bar.squeeze(-2) - comp_value
    )
    decomposition = (
        cov_head.sum(dim=2)
        + group_reroute.sum(dim=2)
        + cls_reroute.squeeze(2)
        + value_mismatch.sum(dim=2)
    )

    full_heads = (prob_full.unsqueeze(-1) * v_full).sum(dim=2)
    comp_heads = (prob_comp.unsqueeze(-1) * v_comp).sum(dim=2)
    head_delta = full_heads - comp_heads
    residual = head_delta - decomposition
    residual_max = residual.abs().amax(dim=(1, 2))

    full_attn = block.drop_path1(_layer_scale(block, attn(norm_full)))
    comp_attn = block.drop_path1(
        _layer_scale(block, attn(norm_pool, attn_mask=suffix_key_bias(block6_tokens)))
    )
    actual_attn_delta = full_attn[:, 0] - comp_attn[:, 0]
    cov_concat = cov_head.sum(dim=2).reshape(b, -1)
    cov_projected = F.linear(cov_concat, attn.proj.weight, bias=None)
    # Match LayerScale (DeiT-Small uses Identity, but retain a vector scale if present).
    cov_projected = _layer_scale(block, cov_projected)
    cov_norm = cov_projected.norm(dim=-1)
    actual_attn_norm = actual_attn_delta.norm(dim=-1)

    cell_cov_norms = []
    for head_idx in range(attn.num_heads):
        start = head_idx * attn.head_dim
        end = start + attn.head_dim
        projected = F.linear(
            cov_head[:, head_idx],
            attn.proj.weight[:, start:end],
            bias=None,
        )
        projected = _layer_scale(block, projected)
        cell_cov_norms.append(projected.norm(dim=-1))
    per_cell_cov_norm = torch.stack(cell_cov_norms, dim=1)

    full_block = block(block6_tokens)
    comp_block = block(pooled_tokens, attn_mask=suffix_key_bias(block6_tokens))
    block_error = (full_block[:, 0] - comp_block[:, 0]).norm(dim=-1)
    logits_clean = forward_from_block6(model, block6_tokens, compressed=False)
    logits_comp = forward_from_block6(model, block6_tokens, compressed=True)
    centered_clean = logits_clean - logits_clean.mean(dim=-1, keepdim=True)
    centered_delta = (logits_comp - logits_clean)
    centered_delta = centered_delta - centered_delta.mean(dim=-1, keepdim=True)
    distortion = centered_delta.norm(dim=-1) / (centered_clean.norm(dim=-1) + 1e-12)

    group_tv = 0.5 * (
        (full_group_mass - comp_group_mass).abs().sum(dim=-1)
        + (prob_full[:, :, :1] - prob_comp[:, :, :1]).abs().squeeze(-1)
    ).mean(dim=1)
    k_full_cells = cell_values(k_full[:, :, 1:]).mean(dim=-2)
    v_full_cells = v_bar.squeeze(-2)
    k_mismatch = _relative_norm(k_full_cells - k_comp[:, :, 1:], k_full_cells)
    v_mismatch = _relative_norm(v_full_cells - v_comp[:, :, 1:], v_full_cells)
    entropy_full = -(prob_full.clamp_min(1e-12) * prob_full.clamp_min(1e-12).log()).sum(dim=-1).mean(dim=1)
    entropy_comp = -(prob_comp.clamp_min(1e-12) * prob_comp.clamp_min(1e-12).log()).sum(dim=-1).mean(dim=1)

    return MechanismBatch(
        omega=omega,
        attention_logit_std=per_cell_omega.mean(dim=(1, 2)).sqrt(),
        covariance_norm=cov_norm,
        actual_attention_error=actual_attn_norm,
        block_output_error=block_error,
        final_logit_distortion=distortion,
        group_mass_tv=group_tv,
        pooled_key_mismatch=k_mismatch,
        pooled_value_mismatch=v_mismatch,
        full_entropy=entropy_full,
        compressed_entropy=entropy_comp,
        covariance_ratio=cov_norm / (actual_attn_norm + 1e-12),
        covariance_residual_max=residual_max,
        cell_omega=per_cell_omega,
        cell_covariance_norm=per_cell_cov_norm,
    )


def centered_logit_distortion(compressed: torch.Tensor, clean: torch.Tensor) -> torch.Tensor:
    """Per-example translation-invariant logit error used by the protocol."""
    clean_centered = clean - clean.mean(dim=-1, keepdim=True)
    delta = compressed - clean
    delta = delta - delta.mean(dim=-1, keepdim=True)
    return delta.norm(dim=-1) / (clean_centered.norm(dim=-1) + 1e-12)
