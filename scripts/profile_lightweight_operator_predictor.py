"""
scripts/profile_lightweight_operator_predictor.py

Phase 4: Predictor Compute and Latency Audit
Benchmarks all predictor families across batch sizes:
BS in {1, 8, 16, 32, 64, 128}

Measures:
- Parameter count
- Output dimension
- Forward FLOPs
- Batch latency (ms)
- Per-image latency (ms)
- Peak GPU memory (MB)
- Speedup vs Reference FactorizedModePredictor

Generates:
- outputs/fungibility_lightweight_operator_predictor/runtime_breakdown.csv
"""

import sys
import gc
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import torch
import torch.nn as nn

REPO_ROOT = Path(r"d:\Study\Patch-Content-Fungibility")
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from patch_fungibility.lightweight_operator_predictor import (
    ModelA_EnvelopeCoefficientPredictor,
    ModelB_ResidualBasisPredictor,
    ModelC_SubspaceMixturePredictor,
    ModelD_OneSidedFactorizedPredictor,
    count_parameters_and_flops
)
from patch_fungibility.amortized_operator import FactorizedModePredictor

OUTPUTS_DIR = REPO_ROOT / "outputs" / "fungibility_lightweight_operator_predictor"
OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

ARCH_CONFIGS = {
    "deit_tiny": {"N": 196, "D": 192, "r": 16, "depth": 6},
    "deit_small": {"N": 196, "D": 384, "r": 32, "depth": 8},
    "vit_base": {"N": 196, "D": 768, "r": 32, "depth": 8},
    "dinov2": {"N": 256, "D": 384, "r": 32, "depth": 8}
}

BATCH_SIZES = [1, 8, 16, 32, 64, 128]


def benchmark_module_latency(module: nn.Module, sample_input: torch.Tensor,
                             num_warmup: int = 10, num_iters: int = 50) -> Tuple[float, float]:
    """
    Measures mean latency (ms) and peak memory (MB) of module(sample_input).
    """
    module.eval()
    device = sample_input.device

    # Warmup
    with torch.no_grad():
        for _ in range(num_warmup):
            _ = module(sample_input)
    if device.type == "cuda":
        torch.cuda.synchronize()
        torch.cuda.reset_peak_memory_stats(device)

    # Benchmark
    t0 = time.perf_counter()
    with torch.no_grad():
        for _ in range(num_iters):
            _ = module(sample_input)
        if device.type == "cuda":
            torch.cuda.synchronize()
    t1 = time.perf_counter()

    mean_latency_ms = ((t1 - t0) / num_iters) * 1000.0
    peak_mem_mb = (torch.cuda.max_memory_allocated(device) / (1024 ** 2)) if device.type == "cuda" else 0.0

    return mean_latency_ms, peak_mem_mb


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Profiling lightweight predictors on: {device}")

    records = []

    for arch_name, cfg in ARCH_CONFIGS.items():
        N = cfg["N"]
        D = cfg["D"]
        r = cfg["r"]
        depth = cfg["depth"]
        ND = N * D
        d_in = 2 * D

        print(f"\n==========================================")
        print(f"Benchmarking Predictors for {arch_name} (N={N}, D={D}, r={r})")
        print(f"==========================================")

        # 1. Instantiate Reference Model E
        model_E = FactorizedModePredictor(N=N, D=D, r=r).to(device)
        p_cnt_E = sum(p.numel() for p in model_E.parameters())
        flops_E = 2.0 * (D * 512 + 512 * (N * r) + D * 512 + 512 * (D * r))

        # 2. Instantiate Model A (K=64)
        U_K = torch.randn(ND, 64, device=device)
        U_K, _ = torch.linalg.qr(U_K)
        model_A = ModelA_EnvelopeCoefficientPredictor(U_K, d_in=d_in, r=r, hidden_dim=256).to(device)
        p_cnt_A, flops_A = count_parameters_and_flops(model_A, (1, d_in))

        # 3. Instantiate Model B (K=32)
        V_0 = torch.randn(ND, r, device=device)
        V_0, _ = torch.linalg.qr(V_0)
        Delta_V = torch.randn(32, ND, r, device=device) * 0.01
        model_B = ModelB_ResidualBasisPredictor(V_0, Delta_V, d_in=d_in, hidden_dim=128).to(device)
        p_cnt_B, flops_B = count_parameters_and_flops(model_B, (1, d_in))

        # 4. Instantiate Model C (M=8)
        protos = torch.randn(8, ND, r, device=device)
        for m in range(8):
            protos[m], _ = torch.linalg.qr(protos[m])
        model_C = ModelC_SubspaceMixturePredictor(protos, d_in=d_in, mode="soft").to(device)
        p_cnt_C, flops_C = count_parameters_and_flops(model_C, (1, d_in))

        # 5. Instantiate Model D (One-Sided)
        if arch_name == "vit_base":
            A_static = torch.randn(N, r, device=device)
            A_static, _ = torch.linalg.qr(A_static)
            model_D = ModelD_OneSidedFactorizedPredictor(N=N, D=D, r=r, d_in=d_in,
                                                        variant="static_token",
                                                        static_basis=A_static,
                                                        hidden_dim=256).to(device)
            out_dim_D = D * r
            family_D = "Model_D_StaticToken_DynFeat"
        else:
            B_static = torch.randn(D, r, device=device)
            B_static, _ = torch.linalg.qr(B_static)
            model_D = ModelD_OneSidedFactorizedPredictor(N=N, D=D, r=r, d_in=d_in,
                                                        variant="static_feature",
                                                        static_basis=B_static,
                                                        hidden_dim=256).to(device)
            out_dim_D = N * r
            family_D = "Model_D_StaticFeat_DynToken"
        p_cnt_D, flops_D = count_parameters_and_flops(model_D, (1, d_in))

        test_models = [
            ("Reference_Factorized_Mode_Predictor", model_E, (N + D) * r, p_cnt_E, flops_E, True),
            ("Model_A_Envelope_K64", model_A, 64 * r, p_cnt_A, flops_A, False),
            ("Model_B_Residual_K32", model_B, 32, p_cnt_B, flops_B, False),
            ("Model_C_Mixture_M8", model_C, 8, p_cnt_C, flops_C, False),
            (family_D, model_D, out_dim_D, p_cnt_D, flops_D, False),
        ]

        ref_latencies_by_bs = {}

        for bs in BATCH_SIZES:
            # Inputs
            x_acts = torch.randn(bs, N + 1, D, device=device)  # (BS, seq_len, D)
            x_pooled = torch.randn(bs, d_in, device=device)     # (BS, 2D)

            for name, mod, out_dim, p_cnt, flps, is_ref in test_models:
                # Reference model expects acts (BS, seq_len, D); others accept x_pooled or acts
                inp = x_acts if is_ref else x_pooled
                try:
                    lat_ms, mem_mb = benchmark_module_latency(mod, inp)
                    if is_ref:
                        ref_latencies_by_bs[bs] = lat_ms
                    ref_lat = ref_latencies_by_bs.get(bs, lat_ms)
                    speedup = ref_lat / max(lat_ms, 1e-6)

                    per_img_ms = lat_ms / bs
                    print(f"  [{arch_name} BS={bs:3d}] {name:35s}: {lat_ms:6.2f} ms ({per_img_ms:6.3f} ms/img) | Speedup: {speedup:5.1f}x | Mem: {mem_mb:5.1f} MB")

                    records.append({
                        "architecture": arch_name,
                        "depth": depth,
                        "batch_size": bs,
                        "model_family": name,
                        "is_reference": is_ref,
                        "parameter_count": p_cnt,
                        "output_dimension": out_dim,
                        "forward_flops": flps,
                        "batch_latency_ms": lat_ms,
                        "per_image_latency_ms": per_img_ms,
                        "peak_memory_mb": mem_mb,
                        "speedup_vs_reference": speedup,
                        "target_10x_reached": bool(speedup >= 10.0),
                        "strong_target_30x_reached": bool(speedup >= 30.0)
                    })
                except torch.cuda.OutOfMemoryError:
                    print(f"  [{arch_name} BS={bs:3d}] {name:35s}: OOM")
                    torch.cuda.empty_cache()

            torch.cuda.empty_cache()

        del model_E, model_A, model_B, model_C, model_D
        torch.cuda.empty_cache()
        gc.collect()

    df = pd.DataFrame(records)
    out_csv = OUTPUTS_DIR / "runtime_breakdown.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved runtime breakdown to: {out_csv}")


if __name__ == "__main__":
    main()
