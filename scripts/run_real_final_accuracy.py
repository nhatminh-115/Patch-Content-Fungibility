"""Run actual pretrained-model carrier accuracy benchmarks.

Default is a 64-image smoke run. Use --max-images 1000 for the canonical held-out
run. Calibration uses the first 500 train_seed=7101 samples from the existing
four-way disjoint ImageNet split and precomputed actual-model Jacobian targets.
Evaluation does not use J/VJP or labels for carrier selection/gating.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy.stats as stats
import torch
import torch.nn.functional as F
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from patch_fungibility.amortized_operator import get_amortized_imagenet_splits
from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.implicit_carrier_operator import (
    SelectiveOperatorGate,
    compute_restricted_carrier_oracle_quantities,
    construct_analytic_correction_basis,
)
from patch_fungibility.practical_operator_compression import (
    create_fixed_spatial_grouping,
    forward_prefix_only,
    forward_suffix_from_hidden,
)
from patch_fungibility.real_final_carriers import forward_with_carriers


OUT = ROOT / "outputs" / "fungibility_real_final"
TARGETS = ROOT / "outputs" / "fungibility_amortized_operator" / "targets"
ARCH = {
    "deit_tiny": {"name": "DeiT-Tiny", "depth": 8, "n": 196, "d": 192, "grid": (14, 14), "budgets": [98, 49, 32], "target": "deit_tiny_targets.pt"},
    "deit_small": {"name": "DeiT-Small", "depth": 8, "n": 196, "d": 384, "grid": (14, 14), "budgets": [98, 49, 32], "target": "deit_small_targets.pt"},
    "vit_base": {"name": "ViT-B/16 AugReg", "depth": 7, "n": 196, "d": 768, "grid": (14, 14), "budgets": [98, 49, 32], "target": "vit_base_targets.pt"},
    "dinov2": {"name": "DINOv2 ViT-S/14", "depth": 8, "n": 256, "d": 384, "grid": (16, 16), "budgets": [128, 64, 42], "target": "dinov2_targets.pt"},
}
Q_METHODS = ["Hybrid Group Mean", "Static Feature-PCA q=16", "Static Feature-PCA q=32",
             "Selective Feature-PCA q16 target20", "Selective Feature-PCA q16 target30",
             "Selective Feature-PCA q16 target50"]


def image_id(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def logits_margin(logits: torch.Tensor, target: int) -> float:
    mask = torch.ones(logits.shape[-1], dtype=torch.bool, device=logits.device)
    mask[target] = False
    return float((logits[target] - logits[mask].max()).item())


def checksum_state(model) -> str:
    h = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        h.update(name.encode("utf-8"))
        h.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return h.hexdigest()


def make_calibration(target_path: Path, cfg: dict, budgets: list[int], device: torch.device):
    data = torch.load(target_path, map_location="cpu", weights_only=False)
    if int(data["depth"]) != cfg["depth"] or int(data["N"]) != cfg["n"] or int(data["D"]) != cfg["d"]:
        raise ValueError(f"Target metadata mismatch: {target_path}")
    train_acts = data["train_acts"].float()
    train_v = data["train_V"].float()
    if len(train_acts) != 500 or len(train_v) != 500:
        raise ValueError("Static carrier calibration requires exactly 500 calibration targets")

    # Match the existing audited calibration formulation: PCA uses only the
    # first 2,000 patch vectors from the calibration split.
    pca_samples = train_acts[:50, 1:, :].reshape(-1, cfg["d"])[:2000].to(device)
    _, _, vh = torch.linalg.svd(pca_samples, full_matrices=False)
    pca32 = vh[:32, :].T.contiguous()
    pca16 = pca32[:, :16].contiguous()
    alphas = {16: [], 32: []}
    chunk = 8 if cfg["d"] >= 768 else 16
    b_cal = budgets[0]
    s_cal, m_cal, _ = create_fixed_spatial_grouping(cfg["n"], b_cal, *cfg["grid"], device=device)
    for start in range(0, 500, chunk):
        p = train_acts[start:start + chunk, 1:, :].to(device)
        v = train_v[start:start + chunk].to(device)
        for q, basis in ((16, pca16), (32, pca32)):
            r = construct_analytic_correction_basis(p, s_cal, m_cal, q=q,
                                                    basis_type="feature_pca", pca_basis=basis)
            solved = compute_restricted_carrier_oracle_quantities(v, p, s_cal, m_cal, r, lam=1e-3)
            alphas[q].append(solved["alpha_star"].detach().cpu())
        del p, v
        if device.type == "cuda":
            torch.cuda.empty_cache()
    alpha16 = torch.cat(alphas[16]).mean(0).to(device)
    alpha32 = torch.cat(alphas[32]).mean(0).to(device)

    # The validated gate uses only per-image clean-prefix residual risk. Calling
    # its existing score with batch size one makes its variance term batch
    # invariant (sigmoid(0)=0.5), so the deployed score is 0.6*norm_risk + 0.2.
    gate = SelectiveOperatorGate(D=cfg["d"]).to(device).eval()
    gate_thresholds = {}
    for budget in budgets:
        s, m, _ = create_fixed_spatial_grouping(cfg["n"], budget, *cfg["grid"], device=device)
        scores = []
        with torch.inference_mode():
            for start in range(0, 500, 64):
                p = train_acts[start:start + 64, 1:, :].to(device)
                c_mean = torch.matmul(s.T.unsqueeze(0), p) / m.view(1, -1, 1)
                residual = p - torch.matmul(s.unsqueeze(0), c_mean)
                # Match SelectiveOperatorGate's first term and fixed single-image
                # variance contribution without batch-relative evaluation stats.
                risk = 0.6 * (residual.norm(dim=(-2, -1)) / p.norm(dim=(-2, -1)).clamp_min(1e-6)) + 0.2
                scores.extend(risk.cpu().tolist())
        score = torch.tensor(scores, dtype=torch.float64)
        gate_thresholds[budget] = {str(pct): float(torch.quantile(score, 1.0 - pct / 100.0))
                                   for pct in (20, 30, 50)}

    params = {"pca16": pca16.cpu(), "pca32": pca32.cpu(), "alpha16": alpha16.cpu(),
              "alpha32": alpha32.cpu(), "gate_thresholds": gate_thresholds,
              "calibration_n": 500, "calibration_seed": 7101,
              "alpha_calibration_budget": b_cal}
    del train_acts, train_v, data, vh, pca_samples
    return params


def build_carrier_set(p: torch.Tensor, s: torch.Tensor, m: torch.Tensor,
                      pca16: torch.Tensor, pca32: torch.Tensor,
                      alpha16: torch.Tensor, alpha32: torch.Tensor,
                      thresholds: dict, scores: torch.Tensor):
    bs, n, _ = p.shape
    s_b = s.unsqueeze(0).expand(bs, -1, -1)
    c_mean = torch.bmm(s_b.transpose(1, 2), p) / m.view(1, -1, 1)
    outputs = {"Hybrid Group Mean": c_mean}
    for q, basis, alpha in ((16, pca16, alpha16), (32, pca32, alpha32)):
        r = construct_analytic_correction_basis(p, s, m, q=q, basis_type="feature_pca", pca_basis=basis)
        dc = torch.einsum("q,bjdq->bjd", alpha, r)
        outputs[f"Static Feature-PCA q={q}"] = c_mean + dc
        if q == 16:
            for pct in (20, 30, 50):
                active = (scores > thresholds[str(pct)]).view(bs, 1, 1)
                outputs[f"Selective Feature-PCA q16 target{pct}"] = torch.where(active, c_mean + dc, c_mean)
    return outputs


def summarize_and_write(per_image: pd.DataFrame, budgets: list[int], arch: str):
    summary = []
    for (budget, method), g in per_image.groupby(["budget_tokens", "method"], sort=True):
        n = len(g)
        correct = int(g["correct"].sum())
        assert all(float(v).is_integer() for v in g["correct"])
        top1 = 100.0 * correct / n
        summary.append({"architecture": arch, "budget_tokens": int(budget), "method": method,
                        "n": n, "correct_count": correct, "top1_accuracy": top1,
                        "prediction_flip_rate": float(g["prediction_flip"].mean()),
                        "mean_logit_l2": float(g["logit_l2"].mean()),
                        "mean_margin_damage": float(g["margin_damage"].mean())})
    summary_df = pd.DataFrame(summary)
    for row in summary_df.itertuples():
        assert abs(row.top1_accuracy - 100 * row.correct_count / row.n) < 1e-12
        if row.n == 1000:
            assert abs(row.top1_accuracy * 10 - round(row.top1_accuracy * 10)) < 1e-8
    return summary_df


def paired_rows(per_image: pd.DataFrame, arch: str):
    rows = []
    methods = ["Static Feature-PCA q=16", "Static Feature-PCA q=32"]
    for (budget, method), g in per_image[per_image.method.isin(methods)].groupby(["budget_tokens", "method"]):
        gm = per_image[(per_image.budget_tokens == budget) & (per_image.method == "Hybrid Group Mean")].set_index("image_id")
        gg = g.set_index("image_id")
        merged = gm.join(gg, lsuffix="_gm", rsuffix="_pca", validate="one_to_one")
        dcorrect = merged.correct_pca.astype(int) - merged.correct_gm.astype(int)
        rescued = ((merged.prediction_gm != merged.clean_prediction_gm) &
                   (merged.prediction_pca == merged.clean_prediction_pca)).sum()
        introduced = ((merged.prediction_gm == merged.clean_prediction_gm) &
                      (merged.prediction_pca != merged.clean_prediction_pca)).sum()
        b = int(dcorrect.gt(0).sum())
        c = int(dcorrect.lt(0).sum())
        p_mcnemar = float(stats.binomtest(min(b, c), b + c, 0.5).pvalue) if b + c else 1.0
        def paired_wilcoxon(a, bvals):
            diff = np.asarray(a) - np.asarray(bvals)
            if np.allclose(diff, 0):
                return 1.0
            return float(stats.wilcoxon(diff).pvalue)
        rows.append({"architecture": arch, "budget_tokens": int(budget), "method_vs": method,
                     "baseline": "Hybrid Group Mean", "n": len(merged),
                     "delta_top1_pp": 100.0 * float(dcorrect.mean()),
                     "mcnemar_pvalue": p_mcnemar,
                     "delta_mean_logit_l2": float(merged.logit_l2_pca.mean() - merged.logit_l2_gm.mean()),
                     "logit_l2_wilcoxon_pvalue": paired_wilcoxon(merged.logit_l2_pca, merged.logit_l2_gm),
                     "delta_mean_margin_damage": float(merged.margin_damage_pca.mean() - merged.margin_damage_gm.mean()),
                     "margin_wilcoxon_pvalue": paired_wilcoxon(merged.margin_damage_pca, merged.margin_damage_gm),
                     "prediction_flips_rescued": int(rescued), "prediction_flips_introduced": int(introduced)})
    # q32 vs q16 paired comparison.
    for budget in sorted(per_image.budget_tokens.unique()):
        a = per_image[(per_image.budget_tokens == budget) & (per_image.method == methods[0])].set_index("image_id")
        b = per_image[(per_image.budget_tokens == budget) & (per_image.method == methods[1])].set_index("image_id")
        if a.empty or b.empty:
            continue
        d = b.correct.astype(int) - a.correct.astype(int)
        wins, losses = int(d.gt(0).sum()), int(d.lt(0).sum())
        rows.append({"architecture": arch, "budget_tokens": int(budget), "method_vs": methods[1],
                     "baseline": methods[0], "n": len(d), "delta_top1_pp": 100*float(d.mean()),
                     "mcnemar_pvalue": float(stats.binomtest(min(wins, losses), wins+losses, 0.5).pvalue) if wins+losses else 1.0,
                     "delta_mean_logit_l2": float(b.logit_l2.mean()-a.logit_l2.mean()),
                     "logit_l2_wilcoxon_pvalue": float(stats.wilcoxon(b.logit_l2-a.logit_l2).pvalue) if not np.allclose(b.logit_l2,a.logit_l2) else 1.0,
                     "delta_mean_margin_damage": float(b.margin_damage.mean()-a.margin_damage.mean()),
                     "margin_wilcoxon_pvalue": float(stats.wilcoxon(b.margin_damage-a.margin_damage).pvalue) if not np.allclose(b.margin_damage,a.margin_damage) else 1.0,
                     "prediction_flips_rescued": int(((b.prediction != a.clean_prediction) & (a.prediction == a.clean_prediction)).sum()),
                     "prediction_flips_introduced": int(((a.prediction == a.clean_prediction) & (b.prediction != a.clean_prediction)).sum())})
    return rows


def run_model(model_key: str, max_images: int, device: torch.device, split_sets: tuple,
              calib_ids: list[str], eval_ids: list[str]):
    cfg = ARCH[model_key]
    model, transform, meta = load_model_and_transform(model_key, device)
    model.eval()
    model_hash = checksum_state(model)
    calib_set, eval_set, train_set, _ = split_sets
    train_set.transform = transform
    eval_set.transform = transform
    n = min(max_images, len(eval_set))
    target_path = TARGETS / cfg["target"]
    params = make_calibration(target_path, cfg, cfg["budgets"], device)
    params_path = OUT / f"calibration_{model_key}.pt"
    torch.save(params, params_path)
    pca16 = params["pca16"].to(device)
    pca32 = params["pca32"].to(device)
    alpha16 = params["alpha16"].to(device)
    alpha32 = params["alpha32"].to(device)

    # Verify the cached target activations match the current validated loader.
    target_data = torch.load(target_path, map_location="cpu", weights_only=False)
    with torch.inference_mode():
        for i in (0, 1, 2):
            raw, _ = train_set._samples[i]
            img = Image.open(__import__("io").BytesIO(raw)).convert("RGB")
            x = transform(img).unsqueeze(0).to(device)
            h = forward_prefix_only(model, model_key, cfg["depth"], x)
            err = (h[0].cpu() - target_data["train_acts"][i].float()).abs().max().item()
            if err > 2e-3:
                raise RuntimeError(f"Calibration target/model prefix parity failed for {model_key}: {err}")
    del target_data

    clean_logits_by_budget = {b: [] for b in cfg["budgets"]}
    logit_arrays = {b: {"Clean": [], **{m: [] for m in Q_METHODS}} for b in cfg["budgets"]}
    rows = []
    timing_start = time.time()
    for idx in range(n):
        raw, target = eval_set._samples[idx]
        img = Image.open(__import__("io").BytesIO(raw)).convert("RGB")
        x = transform(img).unsqueeze(0).to(device)
        with torch.inference_mode():
            h = forward_prefix_only(model, model_key, cfg["depth"], x)
            logits_clean = forward_suffix_from_hidden(model, model_key, cfg["depth"], h, None, cfg["n"])[0]
            if idx == 0:
                normal = model(x)[0]
                max_err = float((normal - logits_clean).abs().max().item())
                if max_err > 3e-4:
                    raise RuntimeError(f"Clean prefix/suffix parity failed for {model_key}: {max_err}")
            clean_pred = int(logits_clean.argmax().item())
            clean_margin = logits_margin(logits_clean, int(target))
            p = h[:, 1:, :]
            for budget in cfg["budgets"]:
                s, m, _ = create_fixed_spatial_grouping(cfg["n"], budget, *cfg["grid"], device=device)
                c_mean = torch.bmm(s.T.unsqueeze(0), p) / m.view(1, -1, 1)
                residual = p - torch.matmul(s.unsqueeze(0), c_mean)
                risk = (0.6 * residual.norm(dim=(-2,-1)) /
                        p.norm(dim=(-2,-1)).clamp_min(1e-6) + 0.2)
                thresholds = params["gate_thresholds"][budget]
                carriers = build_carrier_set(p, s, m, pca16, pca32, alpha16, alpha32, thresholds, risk)
                method_order = Q_METHODS
                compressed = torch.cat([carriers[method] for method in method_order], dim=0)
                mults = torch.cat([torch.ones(1, device=device), m])
                h_comp = torch.cat([h[:, :1, :].expand(len(method_order), -1, -1), compressed], dim=1)
                # The tested multiplicity-aware suffix accepts one multiplicity
                # vector shared by the homogeneous batch.
                logits_comp = forward_suffix_from_hidden(model, model_key, cfg["depth"], h_comp,
                                                         mults, cfg["n"])
                if idx == 0 and budget == cfg["budgets"][0]:
                    direct = forward_with_carriers(model, model_key, x, cfg["depth"], s,
                                                   carriers[method_order[0]], m, prefix_hidden=h)[0]
                    direct_error = float((direct - logits_comp[0]).abs().max().item())
                    if direct_error > 3e-4:
                        raise RuntimeError(f"Reusable carrier path parity failed for {model_key}: {direct_error}")
                logits_for_methods = {method: logits_comp[j] for j, method in enumerate(method_order)}
                configs = {"Clean": logits_clean, **logits_for_methods}
                for method, logits in configs.items():
                    pred = int(logits.argmax().item())
                    correct = int(pred == int(target))
                    l2 = float(torch.linalg.vector_norm(logits - logits_clean).item())
                    margin = logits_margin(logits, int(target))
                    gate_threshold = (thresholds[method.rsplit("target", 1)[1]]
                                      if method.startswith("Selective") else "")
                    rows.append({"architecture": cfg["name"], "image_id": eval_ids[idx], "target": int(target),
                                 "budget_tokens": budget, "method": method, "prediction": pred,
                                 "correct": correct, "clean_prediction": clean_pred,
                                 "prediction_flip": int(pred != clean_pred), "logit_l2": l2,
                                 "clean_true_class_margin": clean_margin,
                                 "compressed_true_class_margin": margin,
                                 "margin_damage": clean_margin - margin,
                                 "gate_risk_score": float(risk.item()) if method.startswith("Selective") else "",
                                 "gate_threshold": gate_threshold,
                                 "gate_active": int(float(risk.item()) > float(gate_threshold)) if method.startswith("Selective") else ""})
                    logit_arrays[budget][method].append(logits.detach().cpu().numpy().astype(np.float32))
                del s, m, c_mean, residual, carriers, compressed, logits_comp
        if (idx + 1) % 16 == 0:
            print(f"[{model_key}] evaluated {idx+1}/{n} images ({time.time()-timing_start:.1f}s)", flush=True)

    df = pd.DataFrame(rows)
    per_path = OUT / "real_accuracy_per_image.csv"
    df.to_csv(per_path, mode="a" if per_path.exists() else "w",
              header=not per_path.exists(), index=False)
    summary = summarize_and_write(df, cfg["budgets"], cfg["name"])
    summ_path = OUT / "real_accuracy_summary.csv"
    summary.to_csv(summ_path, mode="a" if summ_path.exists() else "w",
                  header=not summ_path.exists(), index=False)
    comparisons = paired_rows(df, cfg["name"])
    ablation_path = OUT / "real_static_carrier_ablation.csv"
    pd.DataFrame(comparisons).to_csv(ablation_path, mode="a" if ablation_path.exists() else "w",
                                     header=not ablation_path.exists(), index=False)
    gate_rows = []
    for budget in cfg["budgets"]:
        for method in ["Hybrid Group Mean", "Static Feature-PCA q=16"] + [m for m in Q_METHODS if m.startswith("Selective")]:
            g = df[(df.budget_tokens == budget) & (df.method == method)]
            gate_rows.append({"architecture": cfg["name"], "budget_tokens": budget, "method": method,
                              "n": len(g), "correct_count": int(g.correct.sum()),
                              "top1_accuracy": 100*float(g.correct.mean()),
                              "activation_rate": float(g.gate_active.replace("", 0).astype(int).mean()) if method.startswith("Selective") else (1.0 if method.startswith("Static") else 0.0),
                              "frozen_calibration_threshold": float(g.gate_threshold.replace("", np.nan).dropna().iloc[0]) if method.startswith("Selective") else ""})
    gate_path = OUT / "real_selective_gate_summary.csv"
    pd.DataFrame(gate_rows).to_csv(gate_path, mode="a" if gate_path.exists() else "w",
                                   header=not gate_path.exists(), index=False)

    arrays = {}
    for budget, methods in logit_arrays.items():
        for method, vectors in methods.items():
            arrays[f"b{budget}__{method}"] = np.stack(vectors).astype(np.float32)
    np.savez_compressed(OUT / f"real_accuracy_logits_{model_key}.npz", **arrays)

    return {"architecture": cfg["name"], "model_key": model_key, "checkpoint_id": meta["model_id"],
            "checkpoint_state_sha256": model_hash, "depth": cfg["depth"], "n": n,
            "clean_parity_max_abs_error": max_err, "precision": "float32",
            "calibration_file": str(params_path.relative_to(ROOT)).replace("\\", "/"),
            "elapsed_seconds": time.time() - timing_start}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-images", type=int, default=64, help="Smoke: 32-64. Full canonical evaluation: 1000.")
    parser.add_argument("--models", nargs="+", default=list(ARCH), choices=list(ARCH))
    args = parser.parse_args()
    if args.max_images not in (32, 64, 1000) and args.max_images < 1:
        raise SystemExit("--max-images must be positive (recommended 64 smoke or 1000 full)")
    OUT.mkdir(parents=True, exist_ok=True)
    # A run starts fresh so an interrupted earlier attempt cannot silently mix
    # image counts or calibration settings into its aggregate CSVs.
    for filename in ("real_accuracy_per_image.csv", "real_accuracy_summary.csv",
                     "real_static_carrier_ablation.csv", "real_selective_gate_summary.csv"):
        path = OUT / filename
        if path.exists():
            path.unlink()
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    calib_set, eval_set, train_set, val_set = get_amortized_imagenet_splits(
        calib_seed=9101, eval_seed=9201, train_seed=7101, val_seed=7201,
        n_calib=1000, n_eval=1000, n_train=500, n_val=500)
    train_set._samples = train_set._samples[:500]
    eval_ids = [image_id(raw) for raw, _ in eval_set._samples]
    calib_ids = [image_id(raw) for raw, _ in train_set._samples]
    overlap = set(calib_ids) & set(eval_ids)
    if overlap:
        raise RuntimeError(f"Calibration/evaluation image overlap: {len(overlap)}")
    base_sample_rows = ([{"image_id": image_id(raw), "label": int(label), "split": "calibration",
                         "split_seed": 7101, "sample_index": i} for i,(raw,label) in enumerate(train_set._samples)] +
                        [{"image_id": image_id(raw), "label": int(label), "split": "evaluation",
                         "split_seed": 9201, "sample_index": i} for i,(raw,label) in enumerate(eval_set._samples)])
    preprocessing = {
        "deit_tiny": "Resize(256,bicubic);CenterCrop(224);ToTensor;Normalize(ImageNet mean=.485,.456,.406 std=.229,.224,.225)",
        "deit_small": "Resize(256,bicubic);CenterCrop(224);ToTensor;Normalize(ImageNet mean=.485,.456,.406 std=.229,.224,.225)",
        "vit_base": "Resize(248,bicubic);CenterCrop(224);MaybeToTensor;Normalize(mean=.5,.5,.5 std=.5,.5,.5)",
        "dinov2": "Resize(256,bicubic);CenterCrop(224);ToTensor;Normalize(ImageNet mean=.485,.456,.406 std=.229,.224,.225)",
    }
    sample_rows = [{**r, "architecture": ARCH[key]["name"], "preprocessing": preprocessing[key]}
                   for key in args.models for r in base_sample_rows]
    pd.DataFrame(sample_rows).to_csv(OUT / "sample_manifest.csv", index=False)
    manifest_hash = hashlib.sha256("\n".join(
        f"{r['architecture']}:{r['split']}:{r['image_id']}:{r['label']}:{r['preprocessing']}"
        for r in sample_rows).encode()).hexdigest()
    if device.type == "cuda":
        print(f"Device: {torch.cuda.get_device_name(0)}; VRAM={torch.cuda.get_device_properties(0).total_memory/1024**3:.2f} GiB", flush=True)
    run_records = []
    for model_key in args.models:
        if device.type == "cuda":
            torch.cuda.empty_cache()
        run_records.append(run_model(model_key, args.max_images, device,
                                     (calib_set, eval_set, train_set, val_set), calib_ids, eval_ids))
    run_manifest = {"status": "SMOKE_PASS" if args.max_images < 1000 else "ACCURACY_RUN_COMPLETE",
                    "run_images_per_architecture": args.max_images, "eval_split_seed": 9201,
                    "calibration_split_seed": 7101, "calibration_n": 500, "calibration_eval_overlap": len(overlap),
                    "split_manifest_sha256": manifest_hash,
                    "methods": ["Clean"] + Q_METHODS, "architectures": run_records,
                    "note": "Static alpha and PCA basis use calibration-only actual-model targets; evaluation performs no J/VJP or label-guided fitting."}
    previous_manifest = OUT / "measurement_manifest.json"
    if previous_manifest.exists():
        previous = json.loads(previous_manifest.read_text(encoding="utf-8"))
        if "throughput" in previous:
            run_manifest["throughput"] = previous["throughput"]
    (OUT / "measurement_manifest.json").write_text(json.dumps(run_manifest, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(run_manifest, indent=2), flush=True)


if __name__ == "__main__":
    main()
