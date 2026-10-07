"""Actual-model carrier inference built from validated repository forwards."""

from __future__ import annotations

import torch

from patch_fungibility.practical_operator_compression import (
    forward_prefix_only,
    forward_suffix_from_hidden,
)


def forward_with_carriers(
    model,
    model_key: str,
    images: torch.Tensor,
    depth: int,
    grouping: torch.Tensor,
    carriers: torch.Tensor,
    multiplicities: torch.Tensor,
    prefix_hidden: torch.Tensor | None = None,
) -> torch.Tensor:
    """Run an actual pretrained model prefix, replace patches with carriers,
    then run the repository's multiplicity-aware actual suffix/readout.

    ``grouping`` is an (N, B) assignment matrix. ``carriers`` is (batch,B,D)
    and ``multiplicities`` is (B,), with counts summing to the original N.
    The returned value is genuine classifier/readout logits.
    """
    h = prefix_hidden if prefix_hidden is not None else forward_prefix_only(model, model_key, depth, images)
    if h.shape[0] != images.shape[0]:
        raise ValueError("prefix_hidden batch size must match images")
    patches = h[:, 1:, :]
    if grouping.ndim != 2 or grouping.shape[0] != patches.shape[1]:
        raise ValueError("grouping must have shape (original_patch_count, carrier_count)")
    if carriers.shape != (h.shape[0], grouping.shape[1], h.shape[2]):
        raise ValueError("carriers must have shape (batch, carrier_count, hidden_dim)")
    if multiplicities.shape != (grouping.shape[1],):
        raise ValueError("multiplicities must have one value per carrier")
    if not torch.isclose(multiplicities.sum(), torch.tensor(float(patches.shape[1]), device=multiplicities.device)):
        raise ValueError("carrier multiplicities must sum to the original patch count")
    h_comp = torch.cat([h[:, :1, :], carriers], dim=1)
    mults = torch.cat([torch.ones(1, device=h.device, dtype=multiplicities.dtype), multiplicities.to(h.device)])
    return forward_suffix_from_hidden(
        model, model_key, depth, h_comp, mults, original_n_patches=patches.shape[1]
    )


def clean_logits_from_prefix(model, model_key: str, depth: int, images: torch.Tensor) -> torch.Tensor:
    """Validated prefix + uncompressed suffix path, matching normal forward."""
    h = forward_prefix_only(model, model_key, depth, images)
    return forward_suffix_from_hidden(model, model_key, depth, h, None, original_n_patches=h.shape[1] - 1)
