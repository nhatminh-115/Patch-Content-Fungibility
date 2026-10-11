"""Training-free frozen-attention Value proxy for one ViT merge state.

The preceding block's QKV output is captured during its ordinary forward.  The
result is a proxy for the *next* block and is never treated as a teacher label.
"""

from dataclasses import dataclass

import torch
import torch.nn.functional as F


@dataclass
class PrefixSignal:
    attention: torch.Tensor  # (heads, patches), CLS-to-patch, preceding block
    values: torch.Tensor     # (heads, patches, head_dim)
    projection: torch.Tensor # (embed_dim, embed_dim)
    hook_calls: int
    fused_attention: bool


def captured_prefix(model, depth: int, image: torch.Tensor):
    """Run the normal optimized prefix once, retaining the last block's QKV.

    The hook observes the existing projection.  It neither recomputes QKV nor
    changes the attention kernel.  The captured tensor is released on return.
    """
    if not 1 <= depth <= len(model.blocks):
        raise ValueError("Invalid prefix depth")
    attn = model.blocks[depth - 1].attn
    seen = []
    handle = attn.qkv.register_forward_hook(lambda _module, _inputs, output: seen.append(output))
    try:
        hidden = model.norm_pre(model.patch_drop(model._pos_embed(model.patch_embed(image))))
        for block in model.blocks[:depth]:
            hidden = block(hidden)
    finally:
        handle.remove()
    if len(seen) != 1 or seen[0].shape[0] != 1:
        raise RuntimeError(f"Expected one QKV observation, got {len(seen)}")
    qkv = seen[0].reshape(1, seen[0].shape[1], 3, attn.num_heads, -1).permute(2, 0, 3, 1, 4)
    q, k, v = qkv.unbind(0)
    q_cls = attn.q_norm(q[:, :, :1])
    k = attn.k_norm(k)
    weights = (q_cls * attn.scale) @ k.transpose(-2, -1)
    weights = weights.softmax(dim=-1)[0, :, 0, 1:]
    signal = PrefixSignal(weights, v[0, :, 1:], attn.proj.weight, len(seen), bool(attn.fused_attn))
    return hidden, signal


def candidate_proxies(signal: PrefixSignal, candidates, multiplicities: torch.Tensor):
    """Compute all candidate features with one vectorized small-tensor pass."""
    device = signal.values.device
    src = torch.tensor([c["source"] for c in candidates], device=device, dtype=torch.long)
    dst = torch.tensor([c["destination"] for c in candidates], device=device, dtype=torch.long)
    ai, aj = signal.attention[:, src], signal.attention[:, dst]
    vi, vj = signal.values[:, src], signal.values[:, dst]
    mi, mj = multiplicities[src], multiplicities[dst]
    factor = (ai * mj[None, :] - aj * mi[None, :]) / (mi + mj)[None, :]
    difference = vi - vj
    raw = (factor[:, :, None] * difference).permute(1, 0, 2).reshape(len(candidates), -1)
    projected = F.linear(raw, signal.projection)
    # The third control is unsigned.  Both scalar controls use identical heads.
    attention_importance = (ai + aj).mean(dim=0)
    attention_value_distance = attention_importance * torch.linalg.vector_norm(
        difference.permute(1, 0, 2).reshape(len(candidates), -1), dim=-1
    )
    return {
        "raw_vector": raw,
        "projected_vector": projected,
        "raw_norm": torch.linalg.vector_norm(raw, dim=-1),
        "projected_norm": torch.linalg.vector_norm(projected, dim=-1),
        "attention_importance": attention_importance,
        "attention_value_distance": attention_value_distance,
    }


def choose_minimum(scores: torch.Tensor) -> int:
    """Stable candidate-order tie break, matching the frozen pool order."""
    return int(torch.argmin(scores).item())
