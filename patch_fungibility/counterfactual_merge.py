"""Counterfactual action construction and frozen-suffix evaluation for the pilot.

This module contains no learned component and does not use classification labels.
"""

from dataclasses import dataclass
from typing import List

import numpy as np
import torch
import torch.nn.functional as F

from patch_fungibility.compression_models import forward_compressed_block_timm


@dataclass
class MergeState:
    cls: torch.Tensor                 # (1, D)
    patches: torch.Tensor             # (N, D)
    multiplicities: torch.Tensor      # (N,)
    positions: torch.Tensor           # weighted original patch grid coordinates (N, 2)

    @property
    def count(self) -> int:
        return self.patches.shape[0]


def initial_state(hidden: torch.Tensor) -> MergeState:
    """Take one prefix state, preserving its original CLS representation."""
    if hidden.ndim == 3:
        assert hidden.shape[0] == 1
        hidden = hidden[0]
    n = hidden.shape[0] - 1
    side = int(n ** 0.5)
    if side * side != n:
        raise ValueError("Expected a square patch grid")
    grid = torch.stack(torch.meshgrid(
        torch.arange(side, device=hidden.device),
        torch.arange(side, device=hidden.device), indexing="ij"), dim=-1
    ).reshape(n, 2).to(hidden.dtype)
    return MergeState(hidden[:1].clone(), hidden[1:].clone(),
                      torch.ones(n, device=hidden.device, dtype=hidden.dtype), grid)


def baseline_state(full: MergeState, target_count: int) -> MergeState:
    """One round of PCF's ToMe-style alternating bipartite soft matching."""
    n = full.count
    r = n - target_count
    if r < 0 or r > n // 2:
        raise ValueError("Target must be between half and all original patches")
    if r == 0:
        return MergeState(full.cls.clone(), full.patches.clone(),
                          full.multiplicities.clone(), full.positions.clone())
    a_idx = torch.arange(0, n, 2, device=full.patches.device)
    b_idx = torch.arange(1, n, 2, device=full.patches.device)
    a, b = full.patches[a_idx], full.patches[b_idx]
    sim = F.normalize(a, dim=-1) @ F.normalize(b, dim=-1).T
    best_sim, best_b = sim.max(dim=1)
    # Stable descending similarity; ties retain the earlier even source.
    order = torch.argsort(best_sim, descending=True, stable=True)
    selected = order[:r]
    kept = torch.ones(a.shape[0], device=a.device, dtype=torch.bool)
    kept[selected] = False
    dest = best_b[selected]
    b_mass = full.multiplicities[b_idx].clone()
    b_num = b * b_mass[:, None]
    b_pos_num = full.positions[b_idx] * b_mass[:, None]
    src_mass = full.multiplicities[a_idx][selected]
    b_mass.scatter_add_(0, dest, src_mass)
    b_num.scatter_add_(0, dest[:, None].expand(-1, b.shape[1]), a[selected] * src_mass[:, None])
    b_pos_num.scatter_add_(0, dest[:, None].expand(-1, 2),
                           full.positions[a_idx][selected] * src_mass[:, None])
    return MergeState(
        full.cls.clone(),
        torch.cat([a[kept], b_num / b_mass[:, None]], dim=0),
        torch.cat([full.multiplicities[a_idx][kept], b_mass], dim=0),
        torch.cat([full.positions[a_idx][kept], b_pos_num / b_mass[:, None]], dim=0),
    )


def apply_action(state: MergeState, source: int, destination: int) -> MergeState:
    if source == destination or not (0 <= source < state.count and 0 <= destination < state.count):
        raise ValueError("Invalid distinct patch indices")
    keep = torch.arange(state.count, device=state.patches.device) != source
    patches = state.patches.clone()
    mass = state.multiplicities.clone()
    pos = state.positions.clone()
    total = mass[source] + mass[destination]
    patches[destination] = (mass[source] * patches[source] + mass[destination] * patches[destination]) / total
    pos[destination] = (mass[source] * pos[source] + mass[destination] * pos[destination]) / total
    mass[destination] = total
    return MergeState(state.cls.clone(), patches[keep], mass[keep], pos[keep])


def candidate_pool(state: MergeState, seed: int, count: int = 32) -> List[dict]:
    """Same deterministic pool for teacher, cosine, and random policies."""
    n = state.count
    sources = range(0, n, 2)
    destinations = range(1, n, 2)
    normed = F.normalize(state.patches, dim=-1)
    sim = (normed @ normed.T).detach().cpu().numpy()
    all_edges = [(i, j, float(sim[i, j])) for i in sources for j in destinations]
    ranked = sorted(all_edges, key=lambda e: (-e[2], e[0], e[1]))
    proposed = [max((e for e in all_edges if e[0] == i), key=lambda e: (e[2], -e[1]))
                for i in sources]
    proposed.sort(key=lambda e: (-e[2], e[0], e[1]))
    chosen = []
    chosen_set = set()

    def add(edge, kind):
        key = edge[:2]
        if key not in chosen_set:
            chosen.append((edge, kind))
            chosen_set.add(key)

    for edge in proposed[:16]:
        add(edge, "tome_proposal")
    for edge in ranked:
        if len(chosen) >= min(count, 24):
            break
        add(edge, "high_cosine_alternative")
    remaining = [e for e in ranked if e[:2] not in chosen_set]
    lo, hi = len(remaining) // 4, 3 * len(remaining) // 4
    middle = remaining[lo:hi]
    rng = np.random.RandomState(seed)
    take = min(count - len(chosen), len(middle))
    for idx in rng.choice(len(middle), size=take, replace=False):
        add(middle[int(idx)], "middle_similarity_sample")
    cls_unit = F.normalize(state.cls[0], dim=0)
    out = []
    for (i, j, cosine), kind in chosen:
        x, y = state.patches[i], state.patches[j]
        mi, mj = state.multiplicities[i], state.multiplicities[j]
        out.append({
            "source": i, "destination": j, "kind": kind, "cosine": cosine,
            "feature_distance": float(torch.linalg.vector_norm(x - y)),
            "source_norm": float(torch.linalg.vector_norm(x)),
            "destination_norm": float(torch.linalg.vector_norm(y)),
            "source_multiplicity": float(mi), "destination_multiplicity": float(mj),
            "spatial_distance": float(torch.linalg.vector_norm(state.positions[i] - state.positions[j])),
            "source_cls_cosine": float(F.cosine_similarity(x, cls_unit, dim=0)),
            "destination_cls_cosine": float(F.cosine_similarity(y, cls_unit, dim=0)),
            "current_patch_count": n,
        })
    if len(out) != count:
        raise RuntimeError(f"Candidate pool has {len(out)}, expected {count}")
    return out


def state_batch(states: List[MergeState]):
    """Build equal-length candidate sequences for one batched teacher suffix call."""
    h = torch.stack([torch.cat([s.cls, s.patches], dim=0) for s in states])
    m = torch.stack([torch.cat([s.multiplicities.new_ones(1), s.multiplicities]) for s in states])
    return h, m


def forward_suffix_batch(model, model_key: str, start_depth: int,
                         hidden: torch.Tensor, multiplicities: torch.Tensor) -> torch.Tensor:
    """Independent per-row multiplicity bias; unlike legacy single-vector suffix."""
    if hidden.ndim != 3 or multiplicities.shape != hidden.shape[:2]:
        raise ValueError("Expected hidden (batch,tokens,dim) and sizes (batch,tokens)")
    bias = multiplicities.log()[:, None, None, :].to(hidden.dtype)
    cur = hidden
    if model_key in ("deit_small", "vit_base", "deit_tiny"):
        for block in model.blocks[start_depth:]:
            cur = forward_compressed_block_timm(block, cur, bias)
        return model.forward_head(model.norm(cur))
    if model_key == "dinov2":
        from patch_fungibility.compression_models import forward_compressed_block_dinov2
        for block in model.backbone.blocks[start_depth:]:
            cur = forward_compressed_block_dinov2(block, cur, bias)
        norm = model.backbone.norm(cur)
        patch_mean = (norm[:, 1:] * multiplicities[:, 1:, None]).sum(dim=1) / multiplicities[:, 1:].sum(dim=1, keepdim=True)
        return model.linear_head(torch.cat([norm[:, 0], patch_mean], dim=-1))
    raise ValueError(model_key)


def normalized_distortion(logits: torch.Tensor, clean_logits: torch.Tensor) -> torch.Tensor:
    z = logits - logits.mean(dim=-1, keepdim=True)
    clean = clean_logits - clean_logits.mean(dim=-1, keepdim=True)
    return ((z - clean) ** 2).sum(dim=-1) / ((clean ** 2).sum(dim=-1) + 1e-8)
