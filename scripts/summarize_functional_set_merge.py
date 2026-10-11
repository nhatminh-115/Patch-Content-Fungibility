"""Apply the frozen functional-set gates to saved per-image measurements."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from patch_fungibility.merge_interaction_diagnostic import paired_bootstrap


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/functional_set_merge")
    args = parser.parse_args()
    out = Path(args.output_dir)
    cohorts = [c for c in ("stability", "pilot") if (out / f"phase_a_{c}_per_image.csv").exists()]
    if "stability" not in cohorts:
        raise RuntimeError("Phase A stability data absent")
    frame = pd.concat([pd.read_csv(out / f"phase_a_{c}_per_image.csv") for c in cohorts])
    summary = frame.groupby(["cohort", "model", "method", "k"]).agg(
        n_images=("distortion", "size"), mean_distortion=("distortion", "mean"),
        mean_sum_single=("sum_single", "mean"), mean_alignment=("output_alignment", "mean"),
        mean_nonadditive=("nonadditive_response", "mean"),
        mean_collisions=("destination_collisions", "mean"),
        min_actual_k=("actual_k", "min"),
        min_max_matching=("max_distinct_destination_matching", "min"),
        mean_selector_ms=("selector_seconds", lambda x: float(1000 * x.mean())),
    ).reset_index()
    summary.to_csv(out / "phase_a_summary.csv", index=False)
    hard_rows = []
    for cohort in cohorts:
        for model in ("deit_small", "vit_base"):
            subset = frame[(frame.cohort == cohort) & (frame.model == model)]
            for global_index, group in subset.groupby("global_index"):
                hard = group[(group.method == "additive_distinct") & (group.k == 16)].iloc[0]
                cardinality = int(hard.actual_k)
                for method in ("cosine", "independent", "independent_load", "additive", "additive_load", "conditional"):
                    control = group[(group.method == method) & (group.k == cardinality)].iloc[0]
                    hard_rows.append({"cohort": cohort, "model": model, "global_index": global_index,
                                      "cardinality": cardinality, "control": method,
                                      "control_distortion": control.distortion,
                                      "distinct_distortion": hard.distortion,
                                      "control_minus_distinct": control.distortion - hard.distortion})
    hard_matched = pd.DataFrame(hard_rows)
    hard_matched.to_csv(out / "phase_a_distinct_destination_matched.csv", index=False)
    hard_contrasts = []
    for (cohort, model, method), group in hard_matched.groupby(["cohort", "model", "control"]):
        hard_contrasts.append({"cohort": cohort, "model": model, "control": method,
                               "min_cardinality": int(group.cardinality.min()),
                               "n_below_16": int((group.cardinality < 16).sum()),
                               **paired_bootstrap(group.control_distortion.values,
                                                  group.distinct_distortion.values, seed=76112)})
    pd.DataFrame(hard_contrasts).to_csv(out / "phase_a_distinct_destination_contrasts.csv", index=False)
    comparisons = []
    for cohort in cohorts:
        for model in ("deit_small", "vit_base"):
            wide = frame[(frame.cohort == cohort) & (frame.model == model) & (frame.k == 16)].pivot(
                index="global_index", columns="method", values="distortion")
            for left in ("cosine", "independent", "independent_load", "additive", "additive_load"):
                for right in ("independent", "independent_load", "additive", "additive_load",
                              "conditional"):
                    if left == right:
                        continue
                    comparisons.append({"cohort": cohort, "model": model, "left": left, "right": right,
                                        "left_mean": float(wide[left].mean()),
                                        "right_mean": float(wide[right].mean()),
                                        **paired_bootstrap(wide[left].values, wide[right].values, seed=76112)})
    contrasts = pd.DataFrame(comparisons)
    contrasts.to_csv(out / "phase_a_paired_contrasts.csv", index=False)
    tome_contrasts = []
    for cohort in cohorts:
        tome_file = out / f"phase_tome_{cohort}_per_image.csv"
        if not tome_file.exists():
            continue
        tome = pd.read_csv(tome_file)
        for model in ("deit_small", "vit_base"):
            baseline = tome[tome.model == model].set_index("global_index").tome_distortion
            for method, group in frame[(frame.cohort == cohort) & (frame.model == model) &
                                       (frame.k == 16) &
                                       (frame.method != "additive_distinct")].groupby("method"):
                proposal = group.set_index("global_index").distortion.reindex(baseline.index)
                tome_contrasts.append({"cohort": cohort, "model": model, "method": method,
                                       "tome_mean": float(baseline.mean()),
                                       "method_mean": float(proposal.mean()),
                                       **paired_bootstrap(baseline.values, proposal.values, seed=76112)})
    if tome_contrasts:
        pd.DataFrame(tome_contrasts).to_csv(out / "phase_tome_paired_contrasts.csv", index=False)
    primary = summary[(summary.cohort == "stability") & (summary.model == "deit_small") & (summary.k == 16)]
    value = dict(zip(primary.method, primary.mean_distortion))
    best_cost = min(("independent", "independent_load"), key=lambda method: value[method])
    best_functional = min(("additive", "additive_load"), key=lambda method: value[method])

    def contrast(cohort, model, left, right):
        return contrasts[(contrasts.cohort == cohort) & (contrasts.model == model) &
                         (contrasts.left == left) & (contrasts.right == right)].iloc[0]

    measured = contrast("stability", "deit_small", best_cost, best_functional)
    oracle_gain = value["independent"] - value["conditional"]
    recovery = float(measured.mean_difference / oracle_gain) if oracle_gain > 0 else float("nan")
    same_sign = "pilot" not in cohorts or contrast("pilot", "deit_small", best_cost, best_functional).mean_difference > 0
    gate_a = bool(measured.mean_difference >= 1e-5 and recovery >= .5 and measured.ci_low > 0 and
                  "pilot" in cohorts and same_sign)
    gates = {"A": "GO" if gate_a else ("PENDING_REPLICATION" if measured.mean_difference >= 1e-5 and
                                       recovery >= .5 and measured.ci_low > 0 and "pilot" not in cohorts else "KILL"),
             "best_cost_control": best_cost, "best_functional_variant": best_functional,
             "deit_mean_absolute_improvement": float(measured.mean_difference),
             "deit_bootstrap_ci_low": float(measured.ci_low),
             "deit_bootstrap_ci_high": float(measured.ci_high),
             "independent_to_conditional_gain": float(oracle_gain),
             "gain_recovery_fraction": recovery,
             "pilot_replication_available": "pilot" in cohorts,
             "B": "NOT_ENTERED", "C": "NOT_ENTERED", "D": "NOT_ENTERED"}
    b_cohorts = [c for c in ("stability", "pilot") if (out / f"phase_b_{c}_per_image.csv").exists()]
    if gate_a and "stability" in b_cohorts:
        b_frame = pd.concat([pd.read_csv(out / f"phase_b_{c}_per_image.csv") for c in b_cohorts])
        b_summary = b_frame[b_frame.k == 16].groupby(["cohort", "model", "dimension"]).agg(
            n_images=("distortion", "size"), mean_distortion=("distortion", "mean"),
            median_pair_spearman=("pair_inner_product_spearman", "median"),
            mean_set_rank_spearman=("set_damage_rank_spearman", "mean"),
            mean_selector_ms=("selector_seconds", lambda x: float(1000 * x.mean())),
            mean_projection_apply_ms=("projection_apply_seconds", lambda x: float(1000 * x.mean())),
            mean_full_effect_overlap=("full_effect_set_overlap", "mean"),
        ).reset_index()
        b_summary.to_csv(out / "phase_b_summary.csv", index=False)
        b_contrasts = []
        for cohort in b_cohorts:
            for model in ("deit_small", "vit_base"):
                control = frame[(frame.cohort == cohort) & (frame.model == model) &
                                (frame.method == best_cost) & (frame.k == 16)].set_index("global_index").distortion
                full = frame[(frame.cohort == cohort) & (frame.model == model) &
                             (frame.method == best_functional) & (frame.k == 16)].set_index("global_index").distortion
                for dimension, group in b_frame[(b_frame.cohort == cohort) & (b_frame.model == model) &
                                                (b_frame.k == 16)].groupby("dimension"):
                    projected = group.set_index("global_index").distortion.reindex(control.index)
                    if projected.isna().any():
                        raise RuntimeError("Projected cohort IDs do not match Phase A")
                    for reference, values in (("cost_control", control), ("full_effect", full)):
                        b_contrasts.append({"cohort": cohort, "model": model, "dimension": dimension,
                                            "reference": reference,
                                            **paired_bootstrap(values.values, projected.values, seed=76112)})
        b_contrasts = pd.DataFrame(b_contrasts)
        b_contrasts.to_csv(out / "phase_b_paired_contrasts.csv", index=False)
        candidates = []
        for row in b_summary[(b_summary.cohort == "stability") &
                             (b_summary.model == "deit_small") & (b_summary.dimension <= 64)].itertuples():
            effect = b_contrasts[(b_contrasts.cohort == "stability") &
                                 (b_contrasts.model == "deit_small") &
                                 (b_contrasts.dimension == row.dimension) &
                                 (b_contrasts.reference == "cost_control")].iloc[0]
            recovery_b = effect.mean_difference / measured.mean_difference if measured.mean_difference > 0 else float("nan")
            meets = (recovery_b >= .8 and effect.mean_difference > 0 and effect.ci_low > 0 and
                     row.median_pair_spearman >= .7 and row.mean_selector_ms <= 5)
            candidates.append({"dimension": int(row.dimension), "retention_fraction": float(recovery_b),
                               "median_pair_spearman": float(row.median_pair_spearman),
                               "mean_selector_ms": float(row.mean_selector_ms),
                               "mean_improvement": float(effect.mean_difference),
                               "ci_low": float(effect.ci_low), "passes_stability": bool(meets)})
        passing = [row for row in candidates if row["passes_stability"]]
        gates["B_candidates"] = candidates
        if not passing:
            gates["B"] = "KILL"
        else:
            chosen_dimension = min(row["dimension"] for row in passing)
            gates["B_dimension"] = chosen_dimension
            if "pilot" not in b_cohorts:
                gates["B"] = "PENDING_REPLICATION"
            else:
                replication = b_contrasts[(b_contrasts.cohort == "pilot") &
                                          (b_contrasts.model == "deit_small") &
                                          (b_contrasts.dimension == chosen_dimension) &
                                          (b_contrasts.reference == "cost_control")]
                gates["B"] = "GO" if len(replication) and replication.iloc[0].mean_difference > 0 else "KILL"
    if not gate_a and gates["A"] == "KILL":
        gates["recommendation"] = "KILL"
    elif gates["B"] == "KILL":
        gates["recommendation"] = "KILL"
    else:
        gates["recommendation"] = "PENDING"
    (out / "gates.json").write_text(json.dumps(gates, indent=2), encoding="utf8")
    fig, axes = plt.subplots(1, 2, figsize=(12, 4), layout="constrained")
    names = ("cosine", "independent", "independent_load", "additive", "additive_load",
             "conditional")
    for axis, model in zip(axes, ("deit_small", "vit_base")):
        subset = summary[(summary.cohort == "stability") & (summary.model == model)]
        for method in names:
            row = subset[(subset.method == method) & (subset.k.isin((1, 2, 4, 8, 16)))].sort_values("k")
            axis.plot(row.k, row.mean_distortion, marker="o", label=method.replace("_", " "))
        axis.set(xlabel="Number of selected merges", ylabel="Mean actual normalized logit distortion",
                 title=model)
        axis.set_xticks((1, 2, 4, 8, 16))
        axis.set_yscale("log")
        axis.grid(alpha=.2)
    axes[0].legend(fontsize=7)
    fig.savefig(out / "phase_a_curves.png", dpi=170)
    plt.close(fig)
    if gate_a and "stability" in b_cohorts:
        fig, axes = plt.subplots(1, 2, figsize=(10, 4), layout="constrained")
        for model in ("deit_small", "vit_base"):
            rows = b_summary[(b_summary.cohort == "stability") &
                             (b_summary.model == model)].sort_values("dimension")
            axes[0].plot(rows.dimension, rows.mean_distortion, marker="o", label=model)
            axes[1].plot(rows.dimension, rows.median_pair_spearman, marker="o", label=model)
        axes[0].axhline(value[best_cost], color="C0", linestyle=":", alpha=.7,
                        label="DeiT cost control")
        axes[0].axhline(value[best_functional], color="C0", linestyle="--", alpha=.7,
                        label="DeiT full effect")
        axes[0].set(xlabel="Projection dimension", ylabel="Mean actual 16-merge distortion")
        axes[1].axhline(.70, color="gray", linestyle=":", label="Gate B minimum")
        axes[1].set(xlabel="Projection dimension", ylabel="Median pair inner-product Spearman")
        for axis in axes:
            axis.set_xticks((16, 32, 64, 128))
            axis.grid(alpha=.2)
            axis.legend(fontsize=7)
        fig.savefig(out / "phase_b_projection_sensitivity.png", dpi=170)
        plt.close(fig)
    print(json.dumps(gates, indent=2))


if __name__ == "__main__":
    main()
