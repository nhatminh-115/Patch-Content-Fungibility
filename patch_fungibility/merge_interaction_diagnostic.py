"""Frozen-suffix diagnostics for sets of PR #4 merge candidates."""

from collections import defaultdict
import time

import numpy as np
import torch

from patch_fungibility.counterfactual_merge import (
    apply_actions, forward_suffix_batch, normalized_distortion, state_batch,
)


def admissible(candidate, selected, candidates):
    source = candidate["source"]
    return source not in {candidates[i]["source"] for i in selected}


def ranked_selection(scores, candidates, limit=16):
    chosen = []
    for i in np.argsort(np.asarray(scores), kind="stable"):
        i = int(i)
        if admissible(candidates[i], chosen, candidates):
            chosen.append(i)
        if len(chosen) == limit:
            break
    return chosen


def pair_categories(candidates, costs):
    cosine = np.argsort(-np.asarray([c["cosine"] for c in candidates]), kind="stable")
    oracle = np.argsort(np.asarray(costs), kind="stable")

    def first_pair(order, predicate=lambda a, b: True):
        for x, a in enumerate(order):
            for b in order[x + 1:]:
                a, b = int(a), int(b)
                if candidates[a]["source"] != candidates[b]["source"] and predicate(a, b):
                    return tuple(sorted((a, b)))
        return None

    half = [int(i) for i in cosine[:len(cosine) // 2]]
    harmful = max(half, key=lambda i: (costs[i], -i))
    partner = next((int(i) for i in cosine if candidates[int(i)]["source"] != candidates[harmful]["source"]), None)
    return {
        "high_cosine": first_pair(cosine),
        "high_oracle": first_pair(oracle),
        "high_cosine_high_damage": tuple(sorted((harmful, partner))) if partner is not None else None,
        "low_damage_different_destination": first_pair(
            oracle, lambda a, b: candidates[a]["destination"] != candidates[b]["destination"]),
        "low_damage_same_destination": first_pair(
            oracle, lambda a, b: candidates[a]["destination"] == candidates[b]["destination"]),
    }


class SetEvaluator:
    """Cache original-state action-set logits, batching equal-length sets only."""

    def __init__(self, model, model_key, depth, state, candidates, clean, batch_size=8):
        self.model, self.model_key, self.depth = model, model_key, depth
        self.state, self.candidates, self.clean = state, candidates, clean
        self.batch_size = batch_size
        self.logits = {}
        self.teacher_seconds = 0.0
        self.teacher_batches = 0
        self.teacher_sets = 0

    def evaluate(self, keys):
        keys = [tuple(sorted(set(int(i) for i in key))) for key in keys]
        missing = sorted(set(keys) - self.logits.keys(), key=lambda k: (len(k), k))
        groups = defaultdict(list)
        for key in missing:
            groups[len(key)].append(key)
        for group in groups.values():
            for start in range(0, len(group), self.batch_size):
                chunk = group[start:start + self.batch_size]
                states = [apply_actions(self.state, [(self.candidates[i]["source"],
                                                       self.candidates[i]["destination"]) for i in key])
                          for key in chunk]
                hidden, mass = state_batch(states)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                tic = time.perf_counter()
                with torch.inference_mode():
                    logits = forward_suffix_batch(self.model, self.model_key, self.depth, hidden, mass)
                if torch.cuda.is_available():
                    torch.cuda.synchronize()
                self.teacher_seconds += time.perf_counter() - tic
                self.teacher_batches += 1
                self.teacher_sets += len(chunk)
                for key, z in zip(chunk, logits):
                    self.logits[key] = z.detach().cpu().numpy().astype(np.float64)
        return [self.logits[key] for key in keys]

    def distortions(self, keys):
        logits = self.evaluate(keys)
        tensor = torch.from_numpy(np.stack(logits)).to(self.clean.device, dtype=self.clean.dtype)
        return normalized_distortion(tensor, self.clean).detach().cpu().numpy().astype(np.float64)


def greedy_selection(evaluator, candidates, limit=16):
    selected = []
    for _ in range(limit):
        eligible = [i for i, c in enumerate(candidates) if i not in selected and admissible(c, selected, candidates)]
        if not eligible:
            break
        sets = [tuple(selected + [i]) for i in eligible]
        values = evaluator.distortions(sets)
        selected.append(eligible[int(np.argmin(values))])
    return selected


def center(z):
    return z - np.mean(z)


def interaction_measurements(evaluator, pair):
    a, b = pair
    z0, za, zb, zab = evaluator.evaluate([(), (a,), (b,), (a, b)])
    clean = evaluator.clean.detach().cpu().numpy()[0].astype(np.float64)
    denom = float(np.dot(center(clean), center(clean)) + 1e-8)
    d0, da, db, dab = evaluator.distortions([(), (a,), (b,), (a, b)])
    delta_a, delta_b = center(za - z0), center(zb - z0)
    residual = center(zab - z0) - delta_a - delta_b
    additive = delta_a + delta_b
    alignment = float(np.dot(delta_a, delta_b) /
                      max(np.linalg.norm(delta_a) * np.linalg.norm(delta_b), 1e-12))
    linear_cross = float(2 * np.dot(delta_a, delta_b) / denom)
    return {
        "interaction": float(dab - da - db + d0),
        "alignment_cosine": alignment,
        "additive_cross_term": linear_cross,
        "nonadditive_scalar_remainder": float(dab - da - db + d0 - linear_cross),
        "residual_norm": float(np.linalg.norm(residual)),
        "residual_relative_norm": float(np.linalg.norm(residual) / max(np.linalg.norm(additive), 1e-12)),
        "pair_distortion": float(dab),
    }


def set_residual(evaluator, key):
    z0 = evaluator.evaluate([()])[0]
    zset = evaluator.evaluate([key])[0]
    singles = evaluator.evaluate([(i,) for i in key])
    additive = sum((center(z - z0) for z in singles), np.zeros_like(z0))
    residual = center(zset - z0) - additive
    clean = evaluator.clean.detach().cpu().numpy()[0].astype(np.float64)
    denom = float(np.dot(center(clean), center(clean)) + 1e-8)
    additive_prediction = float(np.dot(center(z0 - clean) + additive,
                                       center(z0 - clean) + additive) / denom)
    actual = float(evaluator.distortions([key])[0])
    return {"residual_norm": float(np.linalg.norm(residual)),
            "residual_relative_norm": float(np.linalg.norm(residual) / max(np.linalg.norm(additive), 1e-12)),
            "additive_prediction": additive_prediction,
            "actual_minus_additive_prediction": actual - additive_prediction}


def paired_bootstrap(left, right, seed=75012, n_resamples=2000):
    left, right = np.asarray(left, dtype=float), np.asarray(right, dtype=float)
    if left.shape != right.shape or left.ndim != 1 or not len(left):
        raise ValueError("Expected nonempty paired image vectors")
    difference = left - right
    rng = np.random.RandomState(seed)
    bootstrap = difference[rng.randint(len(difference), size=(n_resamples, len(difference)))].mean(axis=1)
    low, high = np.percentile(bootstrap, [2.5, 97.5])
    return {"mean_difference": float(difference.mean()), "ci_low": float(low), "ci_high": float(high),
            "relative_to_left": float(difference.mean() / max(left.mean(), 1e-12)), "n_images": len(left)}
