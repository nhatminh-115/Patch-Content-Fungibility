"""Multi-action construction, suffix parity, and diagnostic arithmetic."""

import numpy as np
import pytest
import torch

from patch_fungibility.compression_models import forward_downstream_compressed
from patch_fungibility.counterfactual_merge import apply_actions, initial_state, state_batch
from patch_fungibility.merge_interaction_diagnostic import (
    SetEvaluator, admissible, interaction_measurements, paired_bootstrap,
    ranked_selection,
)


def test_ranked_selection_respects_distinct_sources_and_shared_destinations():
    candidates = [{"source": 0, "destination": 1},
                  {"source": 0, "destination": 3},
                  {"source": 2, "destination": 1}]
    assert ranked_selection([0, 1, 2], candidates, 2) == [0, 2]
    assert not admissible(candidates[1], [0], candidates)
    assert admissible(candidates[2], [0], candidates)


def test_multiple_actions_preserve_cls_mass_and_weighted_shared_destination():
    torch.manual_seed(71)
    full = initial_state(torch.randn(1, 197, 12))
    full.multiplicities[0] = 2
    full.multiplicities[1] = 3
    full.multiplicities[2] = 4
    reduced = apply_actions(full, [(0, 1), (2, 1), (4, 3)])
    assert reduced.count == 193
    torch.testing.assert_close(reduced.cls, full.cls)
    torch.testing.assert_close(reduced.multiplicities.sum(), full.multiplicities.sum())
    torch.testing.assert_close(reduced.patches[0],
                               (2 * full.patches[0] + 3 * full.patches[1] + 4 * full.patches[2]) / 9)
    assert reduced.multiplicities[0] == 9


def test_batched_multi_action_suffix_matches_individual_legacy_suffix():
    timm = pytest.importorskip("timm")
    torch.manual_seed(72)
    model = timm.create_model("deit_tiny_patch16_224", pretrained=False).eval()
    full = initial_state(torch.randn(1, 197, model.embed_dim))
    edges = [[(0, 1), (2, 1), (4, 3)], [(6, 7), (8, 9), (10, 7)]]
    states = [apply_actions(full, e) for e in edges]
    assert all(s.count == 193 and float(s.multiplicities.sum()) == 196 for s in states)
    hidden, mass = state_batch(states)
    with torch.inference_mode():
        from patch_fungibility.counterfactual_merge import forward_suffix_batch
        batch = forward_suffix_batch(model, "deit_tiny", 11, hidden, mass)
        single = torch.cat([forward_downstream_compressed(model, "deit_tiny", 11,
                                                           hidden[i:i+1], mass[i], 196)
                            for i in range(2)])
    torch.testing.assert_close(batch, single, atol=1e-5, rtol=1e-5)
    candidates = [{"source": 0, "destination": 1},
                  {"source": 2, "destination": 1},
                  {"source": 4, "destination": 3}]
    evaluator = SetEvaluator(model, "deit_tiny", 11, full, candidates, batch[:1], 2)
    first = evaluator.evaluate([(0, 1, 2)])[0]
    second = evaluator.evaluate([(2, 0, 1)])[0]
    np.testing.assert_allclose(first, batch[0].detach().numpy(), atol=1e-5, rtol=1e-5)
    assert np.array_equal(first, second) and evaluator.teacher_sets == 1


def test_pair_decomposition_distinguishes_alignment_from_nonadditivity():
    # A scalar additive model gives positive squared-error interaction without non-additive response.
    class FakeEvaluator:
        clean = torch.tensor([[2.0, -2.0]])
        def evaluate(self, keys):
            values = {(): np.array([2.0, -2.0]), (0,): np.array([2.1, -2.1]),
                      (1,): np.array([2.2, -2.2]), (0, 1): np.array([2.3, -2.3])}
            return [values[tuple(sorted(k))] for k in keys]
        def distortions(self, keys):
            z = self.evaluate(keys)
            return np.array([np.sum((v - self.clean.numpy()[0]) ** 2) / 8 for v in z])
    result = interaction_measurements(FakeEvaluator(), (0, 1))
    assert result["interaction"] > 0
    assert result["alignment_cosine"] == pytest.approx(1.0)
    assert result["residual_norm"] == pytest.approx(0.0, abs=1e-12)
    assert result["nonadditive_scalar_remainder"] == pytest.approx(0.0, abs=1e-10)
    ci = paired_bootstrap([1, 2, 3], [0, 1, 2], n_resamples=100)
    assert ci["mean_difference"] == ci["ci_low"] == ci["ci_high"] == 1.0
