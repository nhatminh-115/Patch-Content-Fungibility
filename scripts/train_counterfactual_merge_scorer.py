"""Phase II/III: train compact action rankers and test complete rollouts.

Requires the frozen Phase I G1 pass. Uses calibration-training counterfactual
labels and the disjoint 64-image calibration-validation cohort only.
"""

import io
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import numpy as np
import pandas as pd
from PIL import Image
from scipy.stats import spearmanr
import torch
import torch.nn as nn
import torch.nn.functional as F

from patch_fungibility.batched_operator_compression import create_hybrid_dynamic_grouping
from patch_fungibility.counterfactual_merge import (
    MergeState, apply_actions, candidate_pool, forward_suffix_batch, initial_state,
    normalized_distortion, state_batch,
)
from patch_fungibility.dense_fraction_models import load_model_and_transform
from patch_fungibility.operator_compression_confirmatory import tome_bipartite_merge
from scripts.run_counterfactual_merge_pilot import (
    SEED_CANDIDATE, calibration_records, image_bytes, prefix,
)

FEATURE_COLUMNS = (
    "cosine", "feature_distance", "source_norm", "destination_norm",
    "source_multiplicity", "destination_multiplicity", "spatial_distance",
    "source_cls_cosine", "destination_cls_cosine", "current_patch_count",
)


def fixed_features(frame):
    x = frame[list(FEATURE_COLUMNS)].to_numpy(dtype=np.float32, copy=True)
    for col in (1, 2, 3, 4, 5, 6):
        x[:, col] = np.log1p(x[:, col])
    x[:, 9] /= 196.0
    return x


class FixedScorer(nn.Module):
    def __init__(self, n_features=10):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(n_features, 32), nn.GELU(),
                                 nn.Linear(32, 16), nn.GELU(), nn.Linear(16, 1))

    def forward(self, tokens, features):
        return self.net(features).squeeze(-1)


class PairScorer(nn.Module):
    def __init__(self, dim, n_features=10):
        super().__init__()
        self.proj = nn.Linear(dim, 16)
        self.net = nn.Sequential(nn.Linear(64 + n_features, 64), nn.GELU(),
                                 nn.Linear(64, 32), nn.GELU(), nn.Linear(32, 1))

    def forward(self, tokens, features):
        a, b = self.proj(tokens[:, :, 0]), self.proj(tokens[:, :, 1])
        pair = torch.cat([a, b, (a - b).abs(), a * b, features], dim=-1)
        return self.net(pair).squeeze(-1)


class CosineProjection(nn.Module):
    def __init__(self, dim):
        super().__init__()
        self.proj = nn.Linear(dim, 16, bias=False)

    def forward(self, tokens, features=None):
        a, b = self.proj(tokens[:, :, 0]), self.proj(tokens[:, :, 1])
        return -F.cosine_similarity(a, b, dim=-1)


def as_states(frame, token_memmap, mean, std):
    if len(frame) % 32 or not np.array_equal(frame.candidate_index.to_numpy().reshape(-1, 32),
                                              np.broadcast_to(np.arange(32), (len(frame) // 32, 32))):
        raise ValueError("Candidate rows are not aligned in 32-action states")
    idx = frame.pair_token_index.to_numpy(dtype=np.int64)
    pairs = np.asarray(token_memmap[idx], dtype=np.float32).reshape(-1, 32, 2, token_memmap.shape[-1])
    fixed = ((fixed_features(frame) - mean) / std).reshape(-1, 32, 10)
    costs = frame.next_distortion.to_numpy(dtype=np.float32).reshape(-1, 32)
    return pairs, fixed, costs


def predict(model, pairs, fixed, device, batch_states=32):
    model.eval()
    outputs = []
    with torch.inference_mode():
        for start in range(0, len(pairs), batch_states):
            p = torch.from_numpy(np.asarray(pairs[start:start + batch_states])).to(device).float()
            f = torch.from_numpy(np.asarray(fixed[start:start + batch_states])).to(device).float()
            outputs.append(model(p, f).cpu().numpy())
    return np.concatenate(outputs, axis=0)


def mean_regret(scores, costs):
    picked = np.argmin(scores, axis=1)
    return float((costs[np.arange(len(costs)), picked] - costs.min(axis=1)).mean())


def train_ranker(model, pairs, fixed, costs, val_pairs, val_fixed, val_costs,
                 device, mode="rank", epochs=14):
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001, weight_decay=1e-4)
    rng = np.random.RandomState(64031)
    best = None
    best_regret = float("inf")
    scale = max(float(costs.std()), 1e-8)
    mean_cost = float(costs.mean())
    for epoch in range(epochs):
        model.train()
        perm = rng.permutation(len(costs))
        for start in range(0, len(perm), 32):
            ids = perm[start:start + 32]
            p = torch.from_numpy(np.asarray(pairs[ids])).to(device).float()
            f = torch.from_numpy(np.asarray(fixed[ids])).to(device).float()
            y = torch.from_numpy(np.asarray(costs[ids])).to(device).float()
            scores = model(p, f)
            if mode == "rank":
                loss = F.cross_entropy(-scores, y.argmin(dim=1))
            else:
                loss = F.mse_loss(scores, (y - mean_cost) / scale)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
        val_scores = predict(model, val_pairs, val_fixed, device)
        regret = mean_regret(val_scores, val_costs)
        if regret < best_regret:
            best_regret = regret
            best = (epoch + 1, {k: v.detach().cpu().clone() for k, v in model.state_dict().items()})
        print(f"{type(model).__name__} {mode} epoch {epoch + 1}: val regret={regret:.8g}", flush=True)
    model.load_state_dict(best[1])
    return model, best[0], best_regret


def train_unsupervised(model, pairs, fixed, device, epochs=6):
    """Learn a decoupled projection to reproduce input cosine, without teacher costs."""
    model.to(device)
    optimizer = torch.optim.AdamW(model.parameters(), lr=0.001)
    rng = np.random.RandomState(64032)
    n = min(len(pairs), 4000)
    flat = pairs.reshape(-1, 2, pairs.shape[-1])
    for epoch in range(epochs):
        for ids in np.array_split(rng.permutation(len(flat))[:n * 32], 100):
            p = torch.from_numpy(np.asarray(flat[ids])).to(device).float().unsqueeze(1)
            target = F.cosine_similarity(p[:, :, 0], p[:, :, 1], dim=-1)
            loss = F.mse_loss(-model(p), target)
            optimizer.zero_grad(set_to_none=True)
            loss.backward()
            optimizer.step()
    return model


def validation_pairs(model, model_key, depth, transform, records, reference, device):
    all_pairs, all_fixed, all_costs, ids = [], [], [], []
    with torch.inference_mode():
        for r in records:
            x = transform(Image.open(io.BytesIO(r["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
            state = initial_state(prefix(model, model_key, depth, x))
            for target in (196, 147, 98):
                from patch_fungibility.counterfactual_merge import baseline_state
                current = baseline_state(state, target)
                seed = SEED_CANDIDATE + r["global_index"] + 1009 * target + (0 if model_key == "deit_small" else 1000003)
                candidates = candidate_pool(current, seed)
                rows = reference[(reference.global_index == r["global_index"]) &
                                 (reference.state_patch_count == target)].sort_values("candidate_index")
                if len(rows) != 32 or any(int(row.source) != c["source"] or int(row.destination) != c["destination"]
                                          for row, c in zip(rows.itertuples(), candidates)):
                    raise RuntimeError("Validation candidate mismatch")
                pair = torch.stack([torch.stack([current.patches[c["source"]],
                                                  current.patches[c["destination"]]]) for c in candidates])
                all_pairs.append(pair.detach().cpu().numpy())
                all_fixed.append(fixed_features(rows))
                all_costs.append(rows.next_distortion.to_numpy(dtype=np.float32))
                ids.append((int(r["global_index"]), target))
    return np.stack(all_pairs), np.stack(all_fixed), np.stack(all_costs), ids


def ranking_metrics(method, scores, costs, ids):
    teacher = costs.argmin(axis=1)
    pred = scores.argmin(axis=1)
    cosine = -scores if method == "cosine" else None
    rank_corr = [spearmanr(scores[i], costs[i]).statistic for i in range(len(costs))]
    top5 = np.argsort(scores, axis=1)[:, :5]
    rows = []
    for state_count in (196, 147, 98):
        mask = np.array([s == state_count for _, s in ids])
        rows.append({"method": method, "state_patch_count": state_count,
                     "n_images": int(mask.sum()),
                     "mean_spearman": float(np.nanmean(np.asarray(rank_corr)[mask])),
                     "top1_agreement": float(np.mean(pred[mask] == teacher[mask])),
                     "top5_teacher_recall": float(np.mean(np.any(top5[mask] == teacher[mask, None], axis=1))),
                     "mean_teacher_regret": float(np.mean(costs[mask, pred[mask]] - costs[mask].min(axis=1)))})
    return rows


def score_candidates(method, models, state, candidates, mean, std, device):
    if method == "cosine":
        return -np.array([c["cosine"] for c in candidates])
    fixed = (fixed_features(pd.DataFrame(candidates)) - mean) / std
    pairs = torch.stack([torch.stack([state.patches[c["source"]], state.patches[c["destination"]]])
                         for c in candidates])[None]
    with torch.inference_mode():
        p = pairs.to(device).float()
        f = torch.from_numpy(fixed[None]).to(device).float()
        return models[method](p, f)[0].detach().cpu().numpy()


def score_rollout(full, budget, global_index, method, models, mean, std, device):
    state = full
    while state.count > budget:
        seed = SEED_CANDIDATE + global_index + 1009 * state.count + 7919 * (196 - state.count)
        candidates = candidate_pool(state, seed)
        scores = score_candidates(method, models, state, candidates, mean, std, device)
        chosen = []
        used_sources = set()
        for ix in np.argsort(scores, kind="stable"):
            c = candidates[int(ix)]
            if c["source"] not in used_sources:
                chosen.append((c["source"], c["destination"]))
                used_sources.add(c["source"])
            if len(chosen) == min(16, state.count - budget):
                break
        if not chosen:
            raise RuntimeError("No admissible merge selected")
        state = apply_actions(state, chosen)
    return state


def baseline_tome(full, budget):
    patches, multiplicities = tome_bipartite_merge(full.patches, budget)
    return MergeState(full.cls, patches, multiplicities, full.positions[:budget])


def baseline_group_mean(full, budget):
    assign, mass = create_hybrid_dynamic_grouping(full.patches[None], budget, K_keep=16)
    patches = torch.bmm(assign.transpose(1, 2), full.patches[None])[0] / mass[0, :, None]
    return MergeState(full.cls, patches, mass[0], full.positions[:budget])


def run_rollout(model, model_key, depth, transform, records, methods, models, mean, std, device):
    results = []
    with torch.inference_mode():
        for n, r in enumerate(records):
            x = transform(Image.open(io.BytesIO(r["image_bytes"])).convert("RGB")).unsqueeze(0).to(device)
            full = initial_state(prefix(model, model_key, depth, x))
            clean = model(x)
            for budget in (98, 49):
                for method in methods + ["tome", "hybrid_group_mean"]:
                    if method == "tome":
                        state = baseline_tome(full, budget)
                    elif method == "hybrid_group_mean":
                        state = baseline_group_mean(full, budget)
                    else:
                        state = score_rollout(full, budget, r["global_index"], method, models, mean, std, device)
                    assert state.count == budget and float(state.multiplicities.sum()) == 196
                    hidden, mass = state_batch([state])
                    logits = forward_suffix_batch(model, model_key, depth, hidden, mass)
                    distortion = float(normalized_distortion(logits, clean)[0])
                    results.append({"model": model_key, "global_index": r["global_index"],
                                    "budget": budget, "method": method,
                                    "distortion": distortion,
                                    "top1_correct": int(logits.argmax(dim=-1).item() == r["label"]),
                                    "clean_top1_correct": int(clean.argmax(dim=-1).item() == r["label"]),
                                    "clean_prediction_preserved": int(logits.argmax(dim=-1).item() == clean.argmax(dim=-1).item())})
            if (n + 1) % 16 == 0:
                print(f"{model_key} rollout {n + 1}/{len(records)}", flush=True)
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--pilot-dir", default="outputs/counterfactual_merge_pilot")
    parser.add_argument("--train-dir", default="outputs/counterfactual_merge_train")
    parser.add_argument("--output-dir", default="outputs/counterfactual_merge_student")
    parser.add_argument("--epochs", type=int, default=14)
    args = parser.parse_args()
    gate = json.loads((Path(args.pilot_dir) / "gate_g1.json").read_text())
    if not gate.get("G1_pass"):
        raise RuntimeError("G1 did not pass; neural training is prohibited")
    out = Path(args.output_dir).resolve()
    out.mkdir(parents=True, exist_ok=False)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    train_all = pd.read_csv(Path(args.train_dir) / "candidate_results.csv")
    pilot_all = pd.read_csv(Path(args.pilot_dir) / "candidate_results.csv")
    train_ids = set(train_all.global_index)
    val_ids = set(pilot_all.loc[pilot_all.cohort == "stability", "global_index"])
    if train_ids & val_ids or len(train_ids) != 808 or len(val_ids) != 64:
        raise RuntimeError("Training and validation image IDs overlap or have wrong counts")
    records, _ = calibration_records()
    val_records = image_bytes([r for r in records if r["cohort"] == "stability"])
    rank_rows, rollout_rows, metadata = [], [], {"train_images": 808, "validation_images": 64, "models": {}}
    for model_key, depth in (("deit_small", 8), ("vit_base", 7)):
        frame = train_all[train_all.model == model_key].reset_index(drop=True)
        ref = pilot_all[(pilot_all.model == model_key) & (pilot_all.cohort == "stability")]
        pair_cache = np.load(Path(args.train_dir) / f"pair_tokens_{model_key}.npy", mmap_mode="r")
        mean = fixed_features(frame).mean(axis=0)
        std = fixed_features(frame).std(axis=0).clip(min=1e-4)
        pairs, fixed, costs = as_states(frame, pair_cache, mean, std)
        model, transform, model_meta = load_model_and_transform(model_key, device)
        val_pairs, val_fixed_raw, val_costs, state_ids = validation_pairs(
            model, model_key, depth, transform, val_records, ref, device)
        val_fixed = (val_fixed_raw - mean) / std
        dim = model_meta["embed_dim"]
        torch.manual_seed(64041)
        learned, learned_epoch, learned_regret = train_ranker(
            PairScorer(dim), pairs, fixed, costs, val_pairs, val_fixed, val_costs, device,
            epochs=args.epochs)
        torch.manual_seed(64042)
        fixed_rank, fixed_epoch, fixed_regret = train_ranker(
            FixedScorer(), pairs, fixed, costs, val_pairs, val_fixed, val_costs, device,
            epochs=args.epochs)
        torch.manual_seed(64043)
        fixed_reg, reg_epoch, reg_regret = train_ranker(
            FixedScorer(), pairs, fixed, costs, val_pairs, val_fixed, val_costs, device,
            mode="regression", epochs=args.epochs)
        torch.manual_seed(64044)
        unsup = train_unsupervised(CosineProjection(dim), pairs, fixed, device)
        scorer_models = {"counterfactual_pair": learned, "fixed_rank": fixed_rank,
                         "fixed_regression": fixed_reg, "embedding_no_teacher": unsup}
        methods = ["cosine", "fixed_rank", "fixed_regression", "embedding_no_teacher", "counterfactual_pair"]
        for method in methods:
            if method == "cosine":
                scores = -val_fixed_raw[:, :, 0]
            else:
                scores = predict(scorer_models[method], val_pairs, val_fixed, device)
            rank_rows.extend({"model": model_key, **r} for r in ranking_metrics(method, scores, val_costs, state_ids))
        for name, scorer in scorer_models.items():
            torch.save(scorer.cpu().state_dict(), out / f"{model_key}_{name}.pt")
            scorer.to(device).eval()
        metadata["models"][model_key] = {
            "feature_mean": mean.tolist(), "feature_std": std.tolist(),
            "chosen_epoch": {"counterfactual_pair": learned_epoch,
                             "fixed_rank": fixed_epoch, "fixed_regression": reg_epoch},
            "validation_regret": {"counterfactual_pair": learned_regret,
                                  "fixed_rank": fixed_regret, "fixed_regression": reg_regret},
            "parameter_count": {name: sum(p.numel() for p in scorer.parameters())
                                for name, scorer in scorer_models.items()},
        }
        rollout_rows.extend(run_rollout(model, model_key, depth, transform, val_records,
                                        methods, scorer_models, mean, std, device))
        pd.DataFrame(rank_rows).to_csv(out / "ranking_summary.partial.csv", index=False)
        pd.DataFrame(rollout_rows).to_csv(out / "rollout_per_image.partial.csv", index=False)
        del model, pairs, fixed, costs, val_pairs, val_fixed, val_costs, scorer_models
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
    pd.DataFrame(rank_rows).to_csv(out / "ranking_summary.csv", index=False)
    rollout = pd.DataFrame(rollout_rows)
    rollout.to_csv(out / "rollout_per_image.csv", index=False)
    summary = rollout.groupby(["model", "budget", "method"]).agg(
        n_images=("distortion", "size"), mean_distortion=("distortion", "mean"),
        top1_accuracy=("top1_correct", "mean"),
        clean_prediction_preservation=("clean_prediction_preserved", "mean"),
    ).reset_index()
    summary.to_csv(out / "rollout_summary.csv", index=False)
    decisions = {}
    for model in ("deit_small", "vit_base"):
        for budget in (98, 49):
            cell = summary[(summary.model == model) & (summary.budget == budget)]
            proposed = cell[cell.method == "counterfactual_pair"].iloc[0]
            controls = cell[cell.method.isin(["cosine", "fixed_rank", "fixed_regression", "embedding_no_teacher"])]
            strongest = controls.loc[controls.mean_distortion.idxmin()]
            decisions[f"{model}_{budget}"] = {
                "best_same_schedule_control": strongest.method,
                "distortion_advantage": float(strongest.mean_distortion - proposed.mean_distortion),
                "accuracy_difference_pp": float(100 * (proposed.top1_accuracy - strongest.top1_accuracy)),
                "pass": bool(proposed.mean_distortion < strongest.mean_distortion and
                             proposed.top1_accuracy >= strongest.top1_accuracy - 0.01),
            }
    decisions["G2_pass"] = all(value["pass"] for value in decisions.values())
    (out / "gate_g2.json").write_text(json.dumps(decisions, indent=2), encoding="utf8")
    (out / "manifest.json").write_text(json.dumps(metadata, indent=2), encoding="utf8")
    print(summary.to_string(index=False), flush=True)
    print(json.dumps(decisions, indent=2), flush=True)


if __name__ == "__main__":
    main()
