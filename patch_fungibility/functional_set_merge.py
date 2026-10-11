"""Offline functional set selection on a fixed pool of merge actions.

The functions here accept effect vectors but never evaluate a downstream model.
Calling code must keep teacher vectors out of any deployed student path.
"""

import numpy as np


def centered(vector):
    vector = np.asarray(vector, dtype=np.float64)
    return vector - vector.mean(axis=-1, keepdims=True)


def effects_from_logits(current, singles, clean):
    """Return current clean error, one-action changes, and clean-logit norm."""
    current = np.asarray(current, dtype=np.float64)
    singles = np.asarray(singles, dtype=np.float64)
    clean = np.asarray(clean, dtype=np.float64)
    if singles.ndim != 2 or current.shape != clean.shape or singles.shape[1:] != current.shape:
        raise ValueError("Expected current/clean vectors and (candidates, classes) single logits")
    error = centered(current - clean)
    deltas = centered(singles - current[None, :])
    denominator = float(np.dot(centered(clean), centered(clean)) + 1e-8)
    return error, deltas, denominator


def additive_damage(error, deltas, selected, denominator):
    total = error + deltas[list(selected)].sum(axis=0) if selected else error
    return float(np.dot(total, total) / denominator)


def maximum_distinct_destination_matching(candidates):
    """Maximum cardinality source/destination matching within this candidate pool."""
    by_source = {}
    for c in candidates:
        by_source.setdefault(int(c["source"]), set()).add(int(c["destination"]))
    matched = {}

    def augment(source, seen):
        for dest in sorted(by_source[source]):
            if dest in seen:
                continue
            seen.add(dest)
            if dest not in matched or augment(matched[dest], seen):
                matched[dest] = source
                return True
        return False

    for source in sorted(by_source):
        augment(source, set())
    return len(matched)


def remaining_matching(candidates, selected, proposed=None):
    indices = list(selected) + ([] if proposed is None else [proposed])
    used_sources = {candidates[i]["source"] for i in indices}
    used_destinations = {candidates[i]["destination"] for i in indices}
    remaining = [c for c in candidates if c["source"] not in used_sources and
                 c["destination"] not in used_destinations]
    return maximum_distinct_destination_matching(remaining)


def select_greedy(candidates, error, deltas, denominator, limit=16, single_costs=None,
                  destination_penalty=0.0, distinct_destinations=False):
    """Greedy set selection by additive vectors or individual damage.

    single_costs enables the cost-only policy. A positive penalty is a *marginal*
    cost for each already selected action using the proposed destination.
    """
    n = len(candidates)
    if deltas.shape[0] != n:
        raise ValueError("Candidate/effect count mismatch")
    if single_costs is not None and len(single_costs) != n:
        raise ValueError("Candidate/cost count mismatch")
    target = min(limit, maximum_distinct_destination_matching(candidates)) if distinct_destinations else limit
    chosen = []
    total = np.asarray(error, dtype=np.float64).copy()
    used_sources = set()
    loads = {}
    for step in range(target):
        eligible = []
        for i, c in enumerate(candidates):
            source, destination = int(c["source"]), int(c["destination"])
            if source in used_sources or (distinct_destinations and destination in loads):
                continue
            if distinct_destinations and remaining_matching(candidates, chosen, i) < target - step - 1:
                continue
            eligible.append(i)
        if not eligible:
            break
        scores = []
        for i in eligible:
            if single_costs is None:
                vector = total + deltas[i]
                value = float(np.dot(vector, vector) / denominator)
            else:
                value = float(single_costs[i])
            value += destination_penalty * loads.get(int(candidates[i]["destination"]), 0)
            scores.append(value)
        best = eligible[int(np.argmin(scores))]
        chosen.append(best)
        total += deltas[best]
        used_sources.add(int(candidates[best]["source"]))
        dest = int(candidates[best]["destination"])
        loads[dest] = loads.get(dest, 0) + 1
    return chosen


def set_components(error, deltas, selected, single_costs, denominator, actual):
    """Exact scalar accounting relative to the full clean logits."""
    indices = list(selected)
    sum_single = float(np.asarray(single_costs)[indices].sum())
    additive = additive_damage(error, deltas, indices, denominator)
    return {"sum_single": sum_single,
            "output_alignment": additive - sum_single,
            "nonadditive_response": float(actual - additive),
            "additive_prediction": additive}


def gaussian_projection(n_classes, dimension, seed):
    rng = np.random.RandomState(seed)
    return rng.normal(0, 1 / np.sqrt(dimension), size=(n_classes, dimension)).astype(np.float64)
