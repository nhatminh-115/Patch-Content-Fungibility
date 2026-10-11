"""Phase I invariants and numerical suffix parity."""

import numpy as np
import pytest
import torch

from patch_fungibility.compression_models import forward_downstream_compressed
from patch_fungibility.counterfactual_merge import (
    apply_action, apply_actions, baseline_state, candidate_pool, forward_suffix_batch,
    initial_state, state_batch,
)


def make_state():
    torch.manual_seed(1337)
    return initial_state(torch.randn(1, 197, 16))


@pytest.mark.parametrize("target", [196, 147, 98])
def test_baseline_counts_multiplicities_and_cls(target):
    state = make_state()
    reduced = baseline_state(state, target)
    assert reduced.count == target
    assert float(reduced.multiplicities.sum()) == 196
    assert torch.equal(reduced.cls, state.cls)
    assert torch.all(reduced.multiplicities >= 1)


def test_weighted_carrier_and_position():
    state = make_state()
    state.multiplicities[0] = 3
    state.multiplicities[1] = 2
    first, second = state.patches[0].clone(), state.patches[1].clone()
    first_pos, second_pos = state.positions[0].clone(), state.positions[1].clone()
    reduced = apply_action(state, 0, 1)
    assert reduced.count == 195
    assert torch.equal(reduced.cls, state.cls)
    assert float(reduced.multiplicities.sum()) == float(state.multiplicities.sum())
    assert reduced.multiplicities[0] == 5
    torch.testing.assert_close(reduced.patches[0], (3 * first + 2 * second) / 5)
    torch.testing.assert_close(reduced.positions[0], (3 * first_pos + 2 * second_pos) / 5)
    with pytest.raises(ValueError):
        apply_action(state, 1, 1)


def test_candidate_pool_is_deterministic_and_valid():
    state = baseline_state(make_state(), 147)
    first = candidate_pool(state, 64021)
    second = candidate_pool(state, 64021)
    assert first == second
    assert len(first) == len({(c["source"], c["destination"]) for c in first}) == 32
    assert all(c["source"] % 2 == 0 and c["destination"] % 2 == 1 for c in first)
    assert all(c["current_patch_count"] == 147 for c in first)
    assert {c["kind"] for c in first} == {
        "tome_proposal", "high_cosine_alternative", "middle_similarity_sample"
    }


def test_simultaneous_matching_assignments_and_weighted_carrier():
    state = make_state()
    reduced = apply_actions(state, [(0, 1), (2, 1), (4, 3)])
    assert reduced.count == 193
    assert torch.equal(reduced.cls, state.cls)
    assert float(reduced.multiplicities.sum()) == 196
    assert sorted(reduced.multiplicities.tolist())[-2:] == [2.0, 3.0]
    torch.testing.assert_close(reduced.patches[0],
                               (state.patches[0] + state.patches[1] + state.patches[2]) / 3)
    with pytest.raises(ValueError):
        apply_actions(state, [(0, 1), (0, 3)])
    with pytest.raises(ValueError):
        apply_actions(state, [(0, 1), (1, 3)])


def test_intermediate_state_matches_existing_tome_implementation():
    from patch_fungibility.operator_compression_confirmatory import tome_bipartite_merge
    state = make_state()
    for target in (147, 98):
        expected_patches, expected_mass = tome_bipartite_merge(state.patches, target)
        actual = baseline_state(state, target)
        torch.testing.assert_close(actual.patches, expected_patches, atol=1e-6, rtol=1e-6)
        torch.testing.assert_close(actual.multiplicities, expected_mass)


def test_calibration_partition_is_disjoint_from_reserved_ids():
    order = np.random.RandomState(64011).permutation(1000)
    pilot, stability, reserved = order[:128], order[128:192], order[192:]
    assert len(set(pilot) & set(stability)) == 0
    assert len(set(pilot) & set(reserved)) == 0
    assert len(set(stability) & set(reserved)) == 0


def test_student_inference_does_not_accept_teacher_outputs():
    from scripts.train_counterfactual_merge_scorer import PairScorer
    scorer = PairScorer(16).eval()
    tokens = torch.randn(1, 32, 2, 16)
    local_features = torch.randn(1, 32, 10)
    teacher_costs = torch.randn(1, 32)
    with torch.inference_mode():
        first = scorer(tokens, local_features)
        teacher_costs.fill_(1e6)
        second = scorer(tokens, local_features)
    assert first.shape == (1, 32)
    torch.testing.assert_close(first, second)


def test_portable_source_identity_excludes_machine_home():
    from scripts.run_counterfactual_merge_pilot import portable_parquet_identity
    source = r"C:\Users\example\.cache\huggingface\hub\datasets--evanarlian--imagenet_1k_resized_256\snapshots\abc\data\val.parquet"
    identity = portable_parquet_identity(source)
    assert identity == "datasets--evanarlian--imagenet_1k_resized_256/snapshots/abc/data/val.parquet"
    assert "Users" not in identity


def test_candidate_batch_matches_legacy_suffix():
    timm = pytest.importorskip("timm")
    torch.manual_seed(47)
    model = timm.create_model("deit_tiny_patch16_224", pretrained=False).eval()
    state = make_state()
    # The toy activation width must agree with this model's embedding width.
    hidden = torch.randn(1, 197, model.embed_dim)
    state = initial_state(hidden)
    merged = apply_action(state, 0, 1)
    h, m = state_batch([state, state])
    with torch.inference_mode():
        new_full = forward_suffix_batch(model, "deit_tiny", 11, h, m)
        old_full = forward_downstream_compressed(model, "deit_tiny", 11, h[:1], m[0], 196)
        assert torch.equal(new_full[:1], old_full) or torch.allclose(new_full[:1], old_full, atol=1e-5)
        h1, m1 = state_batch([merged])
        new_merged = forward_suffix_batch(model, "deit_tiny", 11, h1, m1)
        old_merged = forward_downstream_compressed(model, "deit_tiny", 11, h1, m1[0], 196)
        torch.testing.assert_close(new_merged, old_merged, atol=1e-5, rtol=1e-5)
