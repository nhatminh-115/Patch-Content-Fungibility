from __future__ import annotations

import math
import unittest

import timm
import torch

from patch_fungibility.mechanism_gated_coarsening import (
    NUM_CELLS,
    NUM_PATCHES,
    forward_clean_manual,
    forward_compressed,
    omega_cell,
    pool_2x2,
    pool_2x2_reference,
    pool_with_cls,
    suffix_key_bias,
)


class CoarseningParityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        torch.manual_seed(92024)
        cls.model = timm.create_model("deit_small_patch16_224.fb_in1k", pretrained=False)
        cls.model.eval()

    def test_vectorized_pool_matches_slice_reference(self) -> None:
        patches = torch.randn(2, NUM_PATCHES, 384, dtype=torch.float64)
        actual = pool_2x2(patches)
        expected = pool_2x2_reference(patches)
        self.assertEqual(actual.shape, (2, NUM_CELLS, 384))
        self.assertTrue(torch.allclose(actual, expected, atol=1e-15, rtol=1e-15))

    def test_cls_mass_and_multiplicity_bias(self) -> None:
        tokens = torch.randn(2, 197, 384)
        pooled = pool_with_cls(tokens)
        self.assertEqual(pooled.shape, (2, 50, 384))
        self.assertTrue(torch.equal(pooled[:, :1], tokens[:, :1]))
        self.assertEqual(1 + 4 * NUM_CELLS, 197)

        full_weights = torch.softmax(torch.zeros(197), dim=0)
        compressed_logits = suffix_key_bias(torch.zeros(1)).flatten()
        compressed_weights = compressed_logits.softmax(dim=0)
        self.assertTrue(torch.allclose(full_weights[1:].reshape(49, 4).sum(-1),
                                       compressed_weights[1:], atol=1e-7, rtol=0))
        self.assertAlmostEqual(float(full_weights[0]), float(compressed_weights[0]), places=7)

    def test_clean_forward_matches_timm_and_compressed_reference(self) -> None:
        images = torch.randn(1, 3, 224, 224)
        with torch.inference_mode():
            standard = self.model(images)
            manual = forward_clean_manual(self.model, images)
            compressed = forward_compressed(self.model, images)

            x = self.model.patch_embed(images)
            x = self.model._pos_embed(x)
            x = self.model.patch_drop(x)
            x = self.model.norm_pre(x)
            for block_idx in range(7):
                x = self.model.blocks[block_idx](x)
            cls = x[:, :1]
            grid = x[:, 1:].reshape(1, 14, 14, 384)
            pooled_ref = torch.stack((grid[:, 0::2, 0::2], grid[:, 0::2, 1::2],
                                      grid[:, 1::2, 0::2], grid[:, 1::2, 1::2]), dim=0).mean(0)
            x_ref = torch.cat((cls, pooled_ref.reshape(1, 49, 384)), dim=1)
            bias = torch.full((1, 1, 1, 50), math.log(4.0))
            bias[..., 0] = 0.0
            for block_idx in range(7, 12):
                x_ref = self.model.blocks[block_idx](x_ref, attn_mask=bias)
            compressed_ref = self.model.forward_head(self.model.norm(x_ref))

        self.assertLessEqual(float((standard - manual).abs().max()), 1e-5)
        self.assertLessEqual(float((compressed - compressed_ref).abs().max()), 1e-5)

    def test_pool_and_omega_have_gradients(self) -> None:
        torch.manual_seed(92025)
        image = torch.randn(1, 3, 224, 224, requires_grad=True)
        hidden = self.model.patch_embed(image)
        hidden = self.model._pos_embed(hidden)
        hidden = self.model.norm_pre(hidden)
        for block_idx in range(7):
            hidden = self.model.blocks[block_idx](hidden)
        pooled = pool_with_cls(hidden)
        omega, _ = omega_cell(self.model, hidden)
        loss = pooled.square().mean() + omega.mean()
        loss.backward()
        self.assertIsNotNone(image.grad)
        self.assertGreater(float(image.grad.abs().sum()), 0.0)
        qkv_grad = self.model.blocks[7].attn.qkv.weight.grad
        self.assertIsNotNone(qkv_grad)
        self.assertGreater(float(qkv_grad.abs().sum()), 0.0)


if __name__ == "__main__":
    unittest.main()
