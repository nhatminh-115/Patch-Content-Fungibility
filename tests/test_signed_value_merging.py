"""Mechanistic and route invariants for the frozen G1 proxy pilot."""

import numpy as np
import pytest
import torch

from patch_fungibility.counterfactual_merge import apply_actions, initial_state
from patch_fungibility.signed_value_merging import PrefixSignal, candidate_proxies, captured_prefix
from scripts.run_signed_value_merging import gate_stability, paired_interval, runtime_smoke_gate


def test_signed_identity_matches_direct_frozen_value_replacement():
    # Two heads, unequal masses, a nontrivial projection, and opposite signs.
    attention = torch.tensor([[.1, .4], [.5, .2]])
    values = torch.tensor([[[1., 3.], [5., -2.]], [[-2., 4.], [1., 0.]]])
    mass = torch.tensor([2., 3.])
    projection = torch.arange(16, dtype=torch.float32).reshape(4, 4) / 13
    signal = PrefixSignal(attention, values, projection, 1, True)
    candidate = [{"source": 0, "destination": 1}]
    proxy = candidate_proxies(signal, candidate, mass)
    merged_v = (mass[0] * values[:, 0] + mass[1] * values[:, 1]) / mass.sum()
    before = attention[:, 0, None] * values[:, 0] + attention[:, 1, None] * values[:, 1]
    after = (attention[:, 0] + attention[:, 1])[:, None] * merged_v
    expected = (before - after).reshape(-1)
    torch.testing.assert_close(proxy["raw_vector"][0], expected)
    torch.testing.assert_close(proxy["projected_vector"][0], projection @ expected)
    assert expected[0] > 0 and expected[1] < 0


def test_multi_action_preserves_cls_mass_and_exact_budget():
    torch.manual_seed(1)
    state = initial_state(torch.randn(1, 197, 12))
    merged = apply_actions(state, [(2 * i, 1) for i in range(16)])
    assert merged.count == 180
    assert torch.equal(merged.cls, state.cls)
    assert float(merged.multiplicities.sum()) == 196
    with pytest.raises(ValueError):
        apply_actions(state, [(0, 1), (0, 3)])
    with pytest.raises(ValueError):
        apply_actions(state, [(0, 1), (1, 3)])


def test_hook_preserves_fused_attention_and_one_qkv_per_prefix_block():
    timm = pytest.importorskip("timm")
    model = timm.create_model("deit_tiny_patch16_224", pretrained=False).eval()
    calls = [0] * 2
    handles = [model.blocks[i].attn.qkv.register_forward_hook(
        lambda _m, _x, _y, i=i: calls.__setitem__(i, calls[i] + 1)) for i in range(2)]
    image = torch.randn(1, 3, 224, 224)
    with torch.inference_mode():
        original_fused = bool(model.blocks[1].attn.fused_attn)
        hidden, signal = captured_prefix(model, 2, image)
        assert hidden.shape == (1, 197, model.embed_dim)
        assert signal.attention.shape == (model.blocks[1].attn.num_heads, 196)
        assert signal.values.numel() == 196 * model.embed_dim
        assert torch.all(signal.attention.sum(dim=1) > 0)
        assert torch.all(signal.attention.sum(dim=1) <= 1)
        assert signal.fused_attention == original_fused
        assert calls == [1, 1]
        assert signal.hook_calls == 1
    for handle in handles:
        handle.remove()


def test_no_merge_prefix_suffix_parity():
    timm = pytest.importorskip("timm")
    from patch_fungibility.counterfactual_merge import forward_suffix_batch, state_batch
    model = timm.create_model("deit_tiny_patch16_224", pretrained=False).eval()
    image = torch.randn(1, 3, 224, 224)
    with torch.inference_mode():
        h, _ = captured_prefix(model, 11, image)
        state = initial_state(h)
        sh, sm = state_batch([state])
        actual = forward_suffix_batch(model, "deit_tiny", 11, sh, sm)
        clean = model(image)
    torch.testing.assert_close(actual, clean, atol=5e-4, rtol=0)


def test_dataset_isolation_and_bootstrap_units():
    order = np.random.RandomState(64011).permutation(1000)
    assert set(order[:128]).isdisjoint(order[128:192])
    assert set(order[:192]).isdisjoint(order[192:])
    assert paired_interval(np.ones(64)) == [1., 1.]
    # A candidate-level pseudo-replicate must not qualify as 64 images.
    import pandas as pd
    fake = pd.DataFrame([{"model": "deit_small", "cohort": "stability", "global_index": 1}])
    assert gate_stability(fake, [])["status"] == "INCOMPLETE"


def test_runtime_gate_uses_frozen_pooled_median_per_model():
    records = []
    for model in ("deit_small", "vit_base"):
        for route in (1.25, 1.05):
            records.append({"model": model, "baseline_times_ms": [1.] * 50,
                            "capture_proxy_times_ms": [route] * 50,
                            "extra_peak_mib": 2., "fused_attention": True, "hook_calls": 1})
    gate = runtime_smoke_gate(records)
    assert gate["status"] == "GO"
    assert gate["by_model"]["deit_small"]["increment_fraction"] == pytest.approx(.15)
