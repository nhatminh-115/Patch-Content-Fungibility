"""Pre-registered Phase I: counterfactual merge oracle headroom, no training."""

import argparse
import hashlib
import io
import json
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import scipy
from PIL import Image
import timm
import torch

from patch_fungibility.compression_models import forward_downstream_compressed
from patch_fungibility.counterfactual_merge import (
    apply_action, baseline_state, candidate_pool, forward_suffix_batch,
    initial_state, normalized_distortion, state_batch,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform


SEED_SPLIT = 64011
SEED_CANDIDATE = 64021
SEED_BOOTSTRAP = 64012
MODEL_CONFIG = (("deit_small", 8, 0), ("vit_base", 7, 1000003))


def sync():
    if torch.cuda.is_available():
        torch.cuda.synchronize()


def calibration_records():
    """Replicate seed-9101 canonical calibration IDs without reading eval images."""
    import glob
    paths = sorted(glob.glob(os.path.expanduser("~/.cache/huggingface/hub/**/val-*.parquet"), recursive=True))
    if not paths:
        raise FileNotFoundError("Canonical ImageNet validation parquet cache is absent")
    labels = np.concatenate([pq.read_table(path, columns=["label"])["label"].to_numpy() for path in paths])
    rng = np.random.RandomState(9101)
    records = []
    for label in sorted(np.unique(labels))[:1000]:
        indices = np.flatnonzero(labels == label)
        global_index = int(rng.choice(indices))
        records.append({"global_index": global_index, "label": int(label)})
    if len(records) != 1000 or len({r["global_index"] for r in records}) != 1000:
        raise RuntimeError("Unexpected calibration IDs")
    order = np.random.RandomState(SEED_SPLIT).permutation(1000)
    selected = []
    for cohort, subset in (("pilot", order[:128]), ("stability", order[128:192]),
                           ("train", order[192:])):
        for ix in subset:
            selected.append({**records[int(ix)], "cohort": cohort, "canonical_calibration_index": int(ix)})
    counts = [pq.ParquetFile(path).metadata.num_rows for path in paths]
    bounds = np.cumsum([0] + counts)
    for r in selected:
        file_no = int(np.searchsorted(bounds[1:], r["global_index"], side="right"))
        local = r["global_index"] - int(bounds[file_no])
        r["parquet_path"] = paths[file_no]
        r["parquet_row"] = int(local)
    return selected, paths


def image_bytes(records):
    """Read only row groups containing selected calibration images."""
    by_group = {}
    for r in records:
        group = r["parquet_row"] // 100
        by_group.setdefault((r["parquet_path"], group), []).append(r)
    for (path, group), targets in by_group.items():
        file = pq.ParquetFile(path)
        table = file.read_row_group(group, columns=["image"])["image"]
        group_start = group * 100
        for r in targets:
            cell = table[r["parquet_row"] - group_start].as_py()
            r["image_bytes"] = cell["bytes"] if isinstance(cell, dict) else cell
    return records


def prefix(model, model_key, depth, x):
    if model_key in ("deit_small", "vit_base"):
        h = model.norm_pre(model.patch_drop(model._pos_embed(model.patch_embed(x))))
        for block in model.blocks[:depth]:
            h = block(h)
        return h
    raise ValueError(model_key)


def model_weight_hash(model):
    digest = hashlib.sha256()
    for name, tensor in model.state_dict().items():
        digest.update(name.encode("utf8"))
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    return digest.hexdigest()


def evaluate_image(model, model_key, depth, x, global_index, cohort,
                   candidate_batch_size, parity_only=False, collect_pair_tokens=False):
    with torch.inference_mode():
        h = prefix(model, model_key, depth, x)
        clean = model(x)
        full = initial_state(h)
        full_h, full_m = state_batch([full])
        parity_logits = forward_suffix_batch(model, model_key, depth, full_h, full_m)
        parity_error = float((parity_logits - clean).abs().max())
        if parity_error >= 5e-4:
            raise RuntimeError(f"No-merge parity failed: {model_key} {parity_error}")
        # Also compare candidate-batch implementation with the validated legacy suffix.
        one = apply_action(full, 0, 1)
        one_h, one_m = state_batch([one])
        one_new = forward_suffix_batch(model, model_key, depth, one_h, one_m)
        one_old = forward_downstream_compressed(model, model_key, depth,
                                                one_h, one_m[0], full.count)
        merged_parity_error = float((one_new - one_old).abs().max())
        if merged_parity_error >= 5e-4:
            raise RuntimeError(f"Merged parity failed: {model_key} {merged_parity_error}")
        if parity_only:
            return [], {"full": parity_error, "merged": merged_parity_error}, []
        rows = []
        pair_tokens = []
        for target in (196, 147, 98):
            state = baseline_state(full, target)
            assert state.count == target and float(state.multiplicities.sum()) == full.count
            sh, sm = state_batch([state])
            current_logits = forward_suffix_batch(model, model_key, depth, sh, sm)
            current_d = float(normalized_distortion(current_logits, clean)[0])
            seed = SEED_CANDIDATE + global_index + 1009 * target + (0 if model_key == "deit_small" else 1000003)
            candidates = candidate_pool(state, seed)
            if collect_pair_tokens:
                pair_tokens.append(torch.stack([
                    torch.stack([state.patches[c["source"]], state.patches[c["destination"]]])
                    for c in candidates
                ]).detach().cpu().to(torch.float16).numpy())
            sync()
            if torch.cuda.is_available():
                torch.cuda.reset_peak_memory_stats()
            started = time.perf_counter()
            distortions = []
            for start in range(0, len(candidates), candidate_batch_size):
                chunk = candidates[start:start + candidate_batch_size]
                alternatives = [apply_action(state, c["source"], c["destination"]) for c in chunk]
                ch, cm = state_batch(alternatives)
                logits = forward_suffix_batch(model, model_key, depth, ch, cm)
                distortions.extend(normalized_distortion(logits, clean).detach().cpu().tolist())
            sync()
            elapsed_ms = 1000 * (time.perf_counter() - started)
            peak_mib = torch.cuda.max_memory_allocated() / 2 ** 20 if torch.cuda.is_available() else 0.0
            for ix, (candidate, next_d) in enumerate(zip(candidates, distortions)):
                rows.append({
                    "model": model_key, "cohort": cohort, "global_index": global_index,
                    "state_patch_count": target, "candidate_index": ix, **candidate,
                    "current_distortion": current_d, "next_distortion": next_d,
                    "counterfactual_cost": next_d - current_d,
                    "teacher_elapsed_ms_for_32": elapsed_ms, "teacher_peak_mib": peak_mib,
                })
        return rows, {"full": parity_error, "merged": merged_parity_error}, pair_tokens


def summarize(df):
    from scipy.stats import spearmanr
    selections = []
    rng = np.random.RandomState(SEED_BOOTSTRAP)
    for (model, cohort, state_count), group in df.groupby(["model", "cohort", "state_patch_count"], sort=True):
        paired = []
        correlations = []
        for image_id, image_group in group.groupby("global_index", sort=True):
            image_group = image_group.sort_values("candidate_index")
            costs = image_group.next_distortion.to_numpy()
            cosine = image_group.cosine.to_numpy()
            teacher = int(np.argmin(costs))
            cosine_pick = int(np.argmax(cosine))
            random_pick = int(np.random.RandomState(SEED_CANDIDATE + int(image_id) + 1009 * int(state_count) + 7).randint(len(costs)))
            paired.append((costs[cosine_pick], costs[teacher], costs[random_pick],
                           float(image_group.current_distortion.iloc[0]),
                           float(image_group.teacher_elapsed_ms_for_32.iloc[0]),
                           float(image_group.teacher_peak_mib.iloc[0])))
            correlations.append(float(spearmanr(cosine, costs).statistic))
        values = np.asarray(paired)
        diff = values[:, 0] - values[:, 1]
        boot = diff[rng.randint(len(diff), size=(2000, len(diff)))].mean(axis=1)
        ci_lo, ci_hi = np.percentile(boot, [2.5, 97.5])
        cosine_mean = float(values[:, 0].mean())
        advantage = float(diff.mean())
        reduction = advantage / max(cosine_mean, 1e-8)
        selections.append({
            "model": model, "cohort": cohort, "state_patch_count": state_count,
            "n_images": len(values), "mean_current_distortion": float(values[:, 3].mean()),
            "mean_cosine_next_distortion": cosine_mean,
            "mean_teacher_next_distortion": float(values[:, 1].mean()),
            "mean_random_next_distortion": float(values[:, 2].mean()),
            "mean_absolute_advantage": advantage, "relative_mean_reduction": reduction,
            "bootstrap_95_low": float(ci_lo), "bootstrap_95_high": float(ci_hi),
            "strict_teacher_wins": int((diff > 1e-12).sum()),
            "near_zero_cosine_count": int((values[:, 0] < 1e-8).sum()),
            "mean_cosine_cost_spearman": float(np.nanmean(correlations)),
            "mean_teacher_ms_per_candidate": float(values[:, 4].mean() / 32),
            "peak_teacher_mib": float(values[:, 5].max()),
            "pilot_threshold_pass": bool(cohort == "pilot" and reduction >= 0.05 and ci_lo > 0 and advantage > 1e-6),
        })
    return pd.DataFrame(selections)


def gate(summary):
    decisions = {}
    for model in ("deit_small", "vit_base"):
        pilot = summary[(summary.model == model) & (summary.cohort == "pilot")]
        stable = summary[(summary.model == model) & (summary.cohort == "stability")]
        qualified = set(pilot.loc[pilot.pilot_threshold_pass, "state_patch_count"])
        stable_positive = set(stable.loc[stable.mean_absolute_advantage > 0, "state_patch_count"])
        decisions[model] = {"qualified_regimes": sorted(qualified),
                            "stable_positive_regimes": sorted(qualified & stable_positive),
                            "pass": len(qualified & stable_positive) >= 2}
    decisions["G1_pass"] = all(decisions[m]["pass"] for m in ("deit_small", "vit_base"))
    return decisions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/counterfactual_merge_pilot")
    parser.add_argument("--candidate-batch-size", type=int, default=8)
    parser.add_argument("--pilot-limit", type=int, default=128,
                        help="Debug only when below 128; cannot produce a G1 pass")
    parser.add_argument("--stability-limit", type=int, default=64)
    parser.add_argument("--models", nargs="+", default=["deit_small", "vit_base"])
    parser.add_argument("--cohort", choices=["pilot", "train"], default="pilot")
    parser.add_argument("--train-limit", type=int, default=808)
    args = parser.parse_args()
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    records, paths = calibration_records()
    # Preserve seeded order within each cohort, then cap only for debugging.
    if args.cohort == "pilot":
        selected = [r for r in records if r["cohort"] == "pilot"][:args.pilot_limit]
        selected += [r for r in records if r["cohort"] == "stability"][:args.stability_limit]
    else:
        selected = [r for r in records if r["cohort"] == "train"][:args.train_limit]
    image_bytes(selected)
    pd.DataFrame([{k: v for k, v in r.items() if k != "image_bytes"} for r in selected]).to_csv(out / "source_image_ids.csv", index=False)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    manifest = {
        "protocol_commit": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "calibration_seed": 9101, "split_seed": SEED_SPLIT,
        "candidate_seed_base": SEED_CANDIDATE, "bootstrap_seed": SEED_BOOTSTRAP,
        "cohort": args.cohort, "pilot_n": args.pilot_limit, "stability_n": args.stability_limit,
        "train_n": args.train_limit if args.cohort == "train" else 0,
        "candidate_count": 32, "candidate_batch_size": args.candidate_batch_size,
        "source_parquets": [{"path": p, "size_bytes": os.path.getsize(p)} for p in paths],
        "torch": torch.__version__, "timm": timm.__version__, "scipy": scipy.__version__,
        "python": platform.python_version(), "gpu": torch.cuda.get_device_name() if torch.cuda.is_available() else None,
        "models": {}, "parity": {},
    }
    rows = []
    try:
        for model_key, depth, _ in MODEL_CONFIG:
            if model_key not in args.models:
                continue
            model, transform, meta = load_model_and_transform(model_key, device)
            model.eval()
            manifest["models"][model_key] = {**meta, "intervention_depth": depth,
                                              "weight_state_sha256": model_weight_hash(model)}
            manifest["parity"][model_key] = {"full_max": 0.0, "merged_max": 0.0}
            pair_memmap = None
            if args.cohort == "train":
                pair_memmap = np.lib.format.open_memmap(
                    out / f"pair_tokens_{model_key}.npy", mode="w+", dtype=np.float16,
                    shape=(len(selected) * 3 * 32, 2, meta["embed_dim"]),
                )
            for n, r in enumerate(selected):
                x = transform(Image.open(io.BytesIO(r["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
                local, parity, pair_tokens = evaluate_image(
                    model, model_key, depth, x, r["global_index"], r["cohort"],
                    args.candidate_batch_size, collect_pair_tokens=pair_memmap is not None,
                )
                if pair_memmap is not None:
                    pair_memmap[n * 96:(n + 1) * 96] = np.concatenate(pair_tokens, axis=0)
                for ix, row in enumerate(local):
                    row["pair_token_index"] = n * 96 + ix
                rows.extend(local)
                manifest["parity"][model_key]["full_max"] = max(manifest["parity"][model_key]["full_max"], parity["full"])
                manifest["parity"][model_key]["merged_max"] = max(manifest["parity"][model_key]["merged_max"], parity["merged"])
                if (n + 1) % 16 == 0:
                    print(f"{model_key}: {n + 1}/{len(selected)} images", flush=True)
                    pd.DataFrame(rows).to_csv(out / "candidate_results.partial.csv", index=False)
            del model
            if pair_memmap is not None:
                pair_memmap.flush()
                del pair_memmap
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
    finally:
        (out / "manifest.json").write_text(json.dumps(manifest, indent=2, default=str), encoding="utf8")
        if rows:
            pd.DataFrame(rows).to_csv(out / "candidate_results.partial.csv", index=False)
    result = pd.DataFrame(rows)
    result.to_csv(out / "candidate_results.csv", index=False)
    summary = summarize(result)
    summary.to_csv(out / "summary.csv", index=False)
    decision = gate(summary) if args.cohort == "pilot" and args.pilot_limit == 128 and args.stability_limit == 64 and set(args.models) == {"deit_small", "vit_base"} else {"G1_pass": False, "reason": "training labels or debug run"}
    (out / "gate_g1.json").write_text(json.dumps(decision, indent=2), encoding="utf8")
    print(summary.to_string(index=False), flush=True)
    print(json.dumps(decision, indent=2), flush=True)


if __name__ == "__main__":
    main()
