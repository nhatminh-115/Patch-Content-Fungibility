"""End-to-end timing for actual pretrained models and carrier methods."""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import torch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.implicit_carrier_operator import construct_analytic_correction_basis
from patch_fungibility.practical_operator_compression import create_fixed_spatial_grouping
from patch_fungibility.real_final_carriers import clean_logits_from_prefix, forward_with_carriers
from scripts.run_real_final_accuracy import ARCH, checksum_state


OUT = ROOT / "outputs" / "fungibility_real_final"
BATCH_SIZES = [1, 8, 16, 32, 64]
METHODS = ["Clean", "Hybrid Group Mean", "Static Feature-PCA q=16",
           "Static Feature-PCA q=32", "Selective Feature-PCA q16 target30"]


def one_method(model, key, cfg, images, method, budget, params, device):
    if method == "Clean":
        return model(images)
    depth = cfg["depth"]
    from patch_fungibility.practical_operator_compression import forward_prefix_only
    h = forward_prefix_only(model, key, depth, images)
    p = h[:, 1:, :]
    s, m, _ = create_fixed_spatial_grouping(cfg["n"], budget, *cfg["grid"], device=device)
    c_mean = torch.matmul(s.T.unsqueeze(0), p) / m.view(1, -1, 1)
    if method == "Hybrid Group Mean":
        c = c_mean
    elif method in ("Static Feature-PCA q=16", "Static Feature-PCA q=32"):
        q = 16 if "16" in method else 32
        basis = params[f"pca{q}"].to(device)
        alpha = params[f"alpha{q}"].to(device)
        r = construct_analytic_correction_basis(p, s, m, q=q, basis_type="feature_pca", pca_basis=basis)
        c = c_mean + torch.einsum("q,bjdq->bjd", alpha, r)
    else:
        basis = params["pca16"].to(device)
        alpha = params["alpha16"].to(device)
        r = construct_analytic_correction_basis(p, s, m, q=16, basis_type="feature_pca", pca_basis=basis)
        c_static = c_mean + torch.einsum("q,bjdq->bjd", alpha, r)
        residual = p - torch.matmul(s.unsqueeze(0), c_mean)
        risk = 0.6 * residual.norm(dim=(-2,-1)) / p.norm(dim=(-2,-1)).clamp_min(1e-6) + 0.2
        threshold = params["gate_thresholds"][budget]["30"]
        active = (risk > threshold).view(images.shape[0], 1, 1)
        c = torch.where(active, c_static, c_mean)
    mults = torch.cat([torch.ones(1, device=device), m])
    h_comp = torch.cat([h[:, :1, :], c], dim=1)
    return forward_with_carriers(model, key, images, depth, s, c, m, prefix_hidden=h)


def main():
    if not torch.cuda.is_available():
        raise RuntimeError("The requested CUDA-event benchmark requires CUDA.")
    device = torch.device("cuda")
    gpu_name = torch.cuda.get_device_name(0)
    torch_version = torch.__version__
    cuda_version = torch.version.cuda
    precision = "float32"
    sdp = {"flash": torch.backends.cuda.flash_sdp_enabled(),
           "mem_efficient": torch.backends.cuda.mem_efficient_sdp_enabled(),
           "math": torch.backends.cuda.math_sdp_enabled()}
    raw_rows, skipped = [], []
    for key, cfg in ARCH.items():
        model, _, meta = load_model_and_transform(key, device)
        model.eval()
        checkpoint_hash = checksum_state(model)
        params_path = OUT / f"calibration_{key}.pt"
        if not params_path.exists():
            raise FileNotFoundError(f"Missing calibration artifact: {params_path}")
        params = torch.load(params_path, map_location="cpu", weights_only=False)
        # Runtime comparison uses the registered 50% operating point, keeping
        # timing focused on whole-model method overhead rather than a broad
        # token-budget sweep.
        for budget in cfg["budgets"][:1]:
            for bs in BATCH_SIZES:
                for method in METHODS:
                    if device.type == "cuda":
                        torch.cuda.empty_cache()
                    images = torch.randn(bs, 3, 224, 224, device=device)
                    call = lambda: one_method(model, key, cfg, images, method, budget, params, device)
                    try:
                        with torch.inference_mode():
                            torch.cuda.reset_peak_memory_stats(device)
                            for _ in range(50):
                                call()
                            torch.cuda.synchronize(device)
                            starts = [torch.cuda.Event(enable_timing=True) for _ in range(100)]
                            ends = [torch.cuda.Event(enable_timing=True) for _ in range(100)]
                            for i in range(100):
                                starts[i].record()
                                call()
                                ends[i].record()
                            torch.cuda.synchronize(device)
                            batch_ms = np.asarray([s.elapsed_time(e) for s, e in zip(starts, ends)], dtype=np.float64)
                            p50 = float(np.median(batch_ms))
                            p25, p75 = (float(v) for v in np.percentile(batch_ms, [25, 75]))
                            row = {"architecture": cfg["name"], "checkpoint": meta["model_id"],
                                   "checkpoint_state_sha256": checkpoint_hash, "method": method,
                                   "depth": cfg["depth"], "budget_tokens": budget, "batch_size": bs,
                                   "precision": precision, "gpu": gpu_name, "torch_version": torch_version,
                                   "cuda_version": cuda_version, "compile_mode": "disabled",
                                   "attention_backend": json.dumps(sdp, sort_keys=True),
                                   "warmups": 50, "iterations": 100,
                                   "batch_latency_ms": p50, "batch_latency_p25_ms": p25,
                                   "batch_latency_p75_ms": p75,
                                   "per_image_ms": p50 / bs, "img_per_sec": bs * 1000.0 / p50,
                                   "peak_allocated_mb": torch.cuda.max_memory_allocated(device) / 1024**2,
                                   "peak_reserved_mb": torch.cuda.max_memory_reserved(device) / 1024**2,
                                   "actual_model_execution": True,
                                   "actual_callable": "model.forward" if method == "Clean" else "forward_with_carriers -> forward_prefix_only + forward_suffix_from_hidden",
                                   "status": "MEASURED"}
                            raw_rows.append(row)
                            print(f"[{key} B={budget} BS={bs}] {method}: {p50:.3f}ms ({bs*1000/p50:.1f} img/s)", flush=True)
                    except torch.cuda.OutOfMemoryError:
                        torch.cuda.empty_cache()
                        skipped.append({"architecture": cfg["name"], "method": method,
                                        "budget_tokens": budget, "batch_size": bs,
                                        "status": "UNMEASURED_OOM", "device": gpu_name})
                        print(f"[{key} B={budget} BS={bs}] {method}: UNMEASURED (OOM)", flush=True)
        del model
        torch.cuda.empty_cache()
    raw = pd.DataFrame(raw_rows)
    raw.to_csv(OUT / "real_throughput_raw.csv", index=False)
    group = raw.groupby(["architecture", "checkpoint", "method", "depth", "budget_tokens", "batch_size"], as_index=False)
    summary = group.agg(batch_latency_ms=("batch_latency_ms", "median"),
                        batch_latency_p25_ms=("batch_latency_p25_ms", "median"),
                        batch_latency_p75_ms=("batch_latency_p75_ms", "median"),
                        per_image_ms=("per_image_ms", "median"), img_per_sec=("img_per_sec", "median"),
                        peak_allocated_mb=("peak_allocated_mb", "max"), peak_reserved_mb=("peak_reserved_mb", "max"),
                        warmups=("warmups", "max"), iterations=("iterations", "max"))
    summary.to_csv(OUT / "real_throughput_summary.csv", index=False)
    manifest_path = OUT / "measurement_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["throughput"] = {"status": "COMPLETE_WITH_UNMEASURED_BATCHES" if skipped else "COMPLETE",
                              "gpu": gpu_name, "precision": precision, "warmup_iterations": 50,
                              "measurement_iterations": 100, "compile_mode": "disabled",
                              "attention_backend": sdp, "measured_rows": len(raw_rows), "unmeasured": skipped,
                              "selective_variant_preselected": "target30 from calibration; not selected by eval accuracy"}
    manifest_path.write_text(json.dumps(manifest, indent=2)+"\n", encoding="utf-8")


if __name__ == "__main__":
    main()
