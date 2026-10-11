"""Arithmetic, feasibility, and compressed-forward invariants for Phase A."""

import numpy as np
import pytest
import torch

from patch_fungibility.compression_models import forward_downstream_compressed
from patch_fungibility.counterfactual_merge import (
    apply_actions, forward_suffix_batch, initial_state, state_batch,
)
from patch_fungibility.functional_set_merge import (
    additive_damage, effects_from_logits, gaussian_projection, maximum_distinct_destination_matching,
    select_greedy, set_components,
)


def test_additive_effects_and_scalar_accounting():
    clean = np.array([2.0, -2.0, 0.0])
    current = clean.copy()
    singles = np.array([[2.1, -2.1, 0.0], [2.2, -2.2, 0.0]])
    error, deltas, denom = effects_from_logits(current, singles, clean)
    assert np.allclose(error, 0)
    expected = np.sum((np.array([.3, -.3, 0])) ** 2) / denom
    assert additive_damage(error, deltas, [0, 1], denom) == pytest.approx(expected)
    individual = np.array([additive_damage(error, deltas, [i], denom) for i in range(2)])
    components = set_components(error, deltas, [0, 1], individual, denom, expected)
    assert components["output_alignment"] > 0
    assert components["nonadditive_response"] == pytest.approx(0)
    assert sum(components[k] for k in ("sum_single", "output_alignment", "nonadditive_response")) == pytest.approx(expected)


def test_destination_penalty_and_maximum_matching():
    candidates = [{"source": 0, "destination": 1}, {"source": 2, "destination": 1},
                  {"source": 4, "destination": 3}]
    error, deltas, denom = np.zeros(2), np.zeros((3, 2)), 1.0
    costs = np.array([0.0, .1, .2])
    assert maximum_distinct_destination_matching(candidates) == 2
    assert select_greedy(candidates, error, deltas, denom, limit=2, single_costs=costs) == [0, 1]
    assert select_greedy(candidates, error, deltas, denom, limit=2, single_costs=costs,
                         destination_penalty=1.0) == [0, 2]
    hard = select_greedy(candidates, error, deltas, denom, limit=3, single_costs=costs,
                         distinct_destinations=True)
    assert hard == [0, 2] and len(hard) == maximum_distinct_destination_matching(candidates)


def test_projection_is_fixed_and_identity_preserves_selection():
    first = gaussian_projection(4, 2, 76151)
    second = gaussian_projection(4, 2, 76151)
    assert first.shape == (4, 2) and np.array_equal(first, second)
    candidates = [{"source": 0, "destination": 1}, {"source": 2, "destination": 3},
                  {"source": 4, "destination": 5}]
    error = np.array([.1, -.1, .05, -.05])
    deltas = np.array([[.2, -.2, 0, 0], [-.1, .1, 0, 0], [0, 0, .1, -.1]])
    original = select_greedy(candidates, error, deltas, 1.0, limit=2)
    identity = np.eye(4)
    projected = select_greedy(candidates, error @ identity, deltas @ identity, 1.0, limit=2)
    assert original == projected


def test_multiple_weighted_merges_and_suffix_equivalence():
    timm = pytest.importorskip("timm")
    torch.manual_seed(76101)
    model = timm.create_model("deit_tiny_patch16_224", pretrained=False).eval()
    full = initial_state(torch.randn(1, 197, model.embed_dim))
    merged = apply_actions(full, [(0, 1), (2, 1), (4, 3), (6, 5)])
    assert merged.count == 192
    assert torch.equal(merged.cls, full.cls)
    assert float(merged.multiplicities.sum()) == 196
    torch.testing.assert_close(merged.patches[0],
                               (full.patches[0] + full.patches[1] + full.patches[2]) / 3)
    hidden, mass = state_batch([merged])
    with torch.inference_mode():
        new = forward_suffix_batch(model, "deit_tiny", 11, hidden, mass)
        old = forward_downstream_compressed(model, "deit_tiny", 11, hidden, mass[0], 196)
    torch.testing.assert_close(new, old, atol=1e-5, rtol=1e-5)
