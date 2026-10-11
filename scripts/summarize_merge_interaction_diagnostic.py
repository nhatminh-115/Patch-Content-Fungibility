"""Summarize paired calibration diagnostics under the frozen D1-D4 gates."""

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
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="outputs/merge_interaction_diagnostic")
    args = parser.parse_args()
    out = Path(args.output_dir)
    cohorts = [name for name in ("stability", "pilot") if (out / f"curve_first_{name}.csv").exists()]
    if "stability" not in cohorts:
        raise RuntimeError("Primary 64-image result is absent")
    curve = pd.concat([pd.read_csv(out / f"curve_first_{name}.csv") for name in cohorts], ignore_index=True)
    ranks = pd.concat([pd.read_csv(out / f"rank_first_{name}.csv") for name in cohorts], ignore_index=True)
    pairs = pd.concat([pd.read_csv(out / f"pairs_first_{name}.csv") for name in cohorts], ignore_index=True)
    residuals = pd.concat([pd.read_csv(out / f"residuals_first_{name}.csv") for name in cohorts], ignore_index=True)
    curve_summary = curve.groupby(["cohort", "model", "method", "k"]).agg(
        n_images=("distortion", "size"), mean_distortion=("distortion", "mean"),
        median_distortion=("distortion", "median"), min_actual_k=("actual_k", "min"),
    ).reset_index()
    curve_summary.to_csv(out / "curve_summary.csv", index=False)
    rank_summary = ranks.groupby(["cohort", "model", "method"]).agg(
        n_images=("regret", "size"), mean_regret=("regret", "mean"),
        mean_spearman=("spearman", "mean"), top1_agreement=("top1_agreement", "mean")
    ).reset_index()
    rank_summary.to_csv(out / "rank_summary.csv", index=False)
    one_action_contrasts = []
    for cohort in cohorts:
        for model in ("deit_small", "vit_base"):
            wide = ranks[(ranks.cohort == cohort) & (ranks.model == model)].pivot(
                index="global_index", columns="method", values="regret")
            one_action_contrasts.append({"cohort": cohort, "model": model,
                                         "left": "student", "right": "cosine",
                                         **paired_bootstrap(wide.student.values, wide.cosine.values)})
    pd.DataFrame(one_action_contrasts).to_csv(out / "single_action_regret_contrasts.csv", index=False)
    pair_summary = pairs.groupby(["cohort", "model", "category"]).agg(
        n_images=("available", "size"), n_available=("available", "sum"),
        mean_interaction=("interaction", "mean"), median_interaction=("interaction", "median"),
        positive_fraction=("interaction", lambda x: float((x > 0).mean())),
        negative_fraction=("interaction", lambda x: float((x < 0).mean())),
        mean_alignment_cosine=("alignment_cosine", "mean"),
        mean_additive_cross_term=("additive_cross_term", "mean"),
        mean_nonadditive_scalar_remainder=("nonadditive_scalar_remainder", "mean"),
        mean_residual_relative_norm=("residual_relative_norm", "mean"),
    ).reset_index()
    pair_summary.to_csv(out / "pair_summary.csv", index=False)
    shared_destination_contrasts = []
    for cohort in cohorts:
        for model in ("deit_small", "vit_base"):
            wide = pairs[(pairs.cohort == cohort) & (pairs.model == model) &
                         (pairs.category.isin(("low_damage_same_destination",
                                                "low_damage_different_destination")))].pivot(
                index="global_index", columns="category", values="interaction")
            shared_destination_contrasts.append({"cohort": cohort, "model": model,
                                                 **paired_bootstrap(wide.low_damage_same_destination.values,
                                                                    wide.low_damage_different_destination.values)})
    pd.DataFrame(shared_destination_contrasts).to_csv(out / "shared_destination_paired_contrasts.csv", index=False)
    residual_summary = residuals.groupby(["cohort", "model", "method", "k"]).agg(
        n_images=("residual_norm", "size"), mean_residual_norm=("residual_norm", "mean"),
        median_relative_residual=("residual_relative_norm", "median"),
        mean_additive_prediction=("additive_prediction", "mean"),
        mean_actual_minus_additive=("actual_minus_additive_prediction", "mean"),
    ).reset_index()
    residual_summary.to_csv(out / "residual_summary.csv", index=False)
    # Exact set-level accounting: individual squared errors, additive-vector cross
    # terms, then departure from additive logits.
    selection_rows = []
    for cohort in cohorts:
        candidate_file = out / f"candidates_first_{cohort}.csv"
        if not candidate_file.exists():
            continue
        candidate = pd.read_csv(candidate_file).set_index(
            ["model", "global_index", "candidate_index"])
        selected = curve[(curve.cohort == cohort) & (curve.k == 16)]
        selected_residuals = residuals[(residuals.cohort == cohort) & (residuals.k == 16)].set_index(
            ["model", "global_index", "method"])
        oracle_sets = { (r.model, int(r.global_index)): set(map(int, r.selected_indices.split(";")))
                        for r in selected.itertuples() if r.method == "independent_oracle" }
        for row in selected.itertuples():
            indices = list(map(int, row.selected_indices.split(";")))
            costs = [float(candidate.loc[(row.model, row.global_index, i), "single_action_distortion"])
                     for i in indices]
            residual = selected_residuals.loc[(row.model, row.global_index, row.method)]
            additive = float(residual.additive_prediction)
            single_sum = float(sum(costs))
            selection_rows.append({"cohort": cohort, "model": row.model,
                                   "global_index": row.global_index, "method": row.method,
                                   "k": len(indices), "sum_single_action_distortion": single_sum,
                                   "mean_single_action_distortion": single_sum / len(indices),
                                   "output_alignment_component": additive - single_sum,
                                   "nonadditive_component": float(row.distortion) - additive,
                                   "actual_distortion": float(row.distortion),
                                   "oracle_set_overlap": len(set(indices) & oracle_sets[(row.model, row.global_index)])})
    if selection_rows:
        selection = pd.DataFrame(selection_rows)
        selection.to_csv(out / "selection_decomposition.csv", index=False)
        selection.groupby(["cohort", "model", "method"]).agg(
            n_images=("actual_distortion", "size"),
            mean_sum_single=("sum_single_action_distortion", "mean"),
            mean_alignment_component=("output_alignment_component", "mean"),
            mean_nonadditive_component=("nonadditive_component", "mean"),
            mean_actual=("actual_distortion", "mean"),
            mean_oracle_set_overlap=("oracle_set_overlap", "mean"),
        ).reset_index().to_csv(out / "selection_decomposition_summary.csv", index=False)
        decomposition_contrasts = []
        for cohort in cohorts:
            for model in ("deit_small", "vit_base"):
                subset = selection[(selection.cohort == cohort) & (selection.model == model)]
                for left, right in (("student", "independent_oracle"),
                                    ("independent_oracle", "conditional_greedy_oracle"),
                                    ("cosine", "independent_oracle")):
                    for component in ("sum_single_action_distortion", "output_alignment_component",
                                      "nonadditive_component", "actual_distortion"):
                        wide = subset.pivot(index="global_index", columns="method", values=component)
                        decomposition_contrasts.append({"cohort": cohort, "model": model,
                                                        "left": left, "right": right,
                                                        "component": component,
                                                        **paired_bootstrap(wide[left].values, wide[right].values)})
        pd.DataFrame(decomposition_contrasts).to_csv(out / "decomposition_paired_contrasts.csv", index=False)
    contrasts = []
    comparisons = (("cosine", "independent_oracle"),
                   ("independent_oracle", "conditional_greedy_oracle"),
                   ("student", "independent_oracle"),
                   ("student", "conditional_greedy_oracle"),
                   ("cosine", "conditional_greedy_oracle"),
                   ("student", "cosine"))
    for cohort in cohorts:
        for model in ("deit_small", "vit_base"):
            wide = curve[(curve.cohort == cohort) & (curve.model == model) & (curve.k == 16)].pivot(
                index="global_index", columns="method", values="distortion")
            for left, right in comparisons:
                value = paired_bootstrap(wide[left].values, wide[right].values)
                contrasts.append({"cohort": cohort, "model": model, "k": 16,
                                  "left": left, "right": right,
                                  "left_mean": float(wide[left].mean()),
                                  "right_mean": float(wide[right].mean()), **value})
    contrasts = pd.DataFrame(contrasts)
    contrasts.to_csv(out / "paired_contrasts.csv", index=False)
    rollout_pool_path = out / "curve_first_stability_rollout_pool.csv"
    if rollout_pool_path.exists():
        rollout = pd.read_csv(rollout_pool_path)
        rollout.groupby(["model", "method", "k"]).distortion.agg(
            n_images="size", mean_distortion="mean"
        ).reset_index().to_csv(out / "rollout_pool_curve_summary.csv", index=False)
        rollout_contrasts = []
        for model in ("deit_small", "vit_base"):
            wide = rollout[(rollout.model == model) & (rollout.k == 16)].pivot(
                index="global_index", columns="method", values="distortion")
            for left, right in comparisons:
                rollout_contrasts.append({"model": model, "left": left, "right": right,
                                          **paired_bootstrap(wide[left].values, wide[right].values)})
        pd.DataFrame(rollout_contrasts).to_csv(out / "rollout_pool_paired_contrasts.csv", index=False)

    def contrast(cohort, model, left, right):
        return contrasts[(contrasts.cohort == cohort) & (contrasts.model == model) &
                         (contrasts.left == left) & (contrasts.right == right)].iloc[0]

    gates = {"D1": {}, "D2": {}, "D3": {}, "D4": {}}
    for model in ("deit_small", "vit_base"):
        d1 = contrast("stability", model, "cosine", "independent_oracle")
        d2 = contrast("stability", model, "independent_oracle", "conditional_greedy_oracle")
        d3 = contrast("stability", model, "student", "independent_oracle")
        stud_cos = contrast("stability", model, "student", "cosine")
        cond_cos = contrast("stability", model, "cosine", "conditional_greedy_oracle")
        replicated_d1 = ("pilot" not in cohorts or
                         contrast("pilot", model, "cosine", "independent_oracle").mean_difference > 0)
        replicated_d2 = ("pilot" not in cohorts or
                         contrast("pilot", model, "independent_oracle", "conditional_greedy_oracle").mean_difference > 0)
        gates["D1"][model] = bool(d1.mean_difference >= 1e-5 and d1.relative_to_left >= .1 and
                                  d1.ci_low > 0 and replicated_d1)
        gates["D2"][model] = bool(d2.mean_difference >= 1e-5 and d2.relative_to_left >= .1 and
                                  d2.ci_low > 0 and replicated_d2 and
                                  cond_cos.mean_difference >= 1e-5 and
                                  cond_cos.relative_to_left >= .1 and cond_cos.ci_low > 0)
        gates["D3"][model] = bool(gates["D1"][model] and d3.ci_low > 0 and
                                  stud_cos.mean_difference > 0 and
                                  d3.mean_difference >= .5 * stud_cos.mean_difference)
    enter_d = any(gates[gate][model] for gate in ("D1", "D2") for model in ("deit_small", "vit_base"))
    gates["D_entry"] = enter_d
    state_path = out / "states_state_stability.csv"
    state_contrasts = []
    if state_path.exists():
        states = pd.read_csv(state_path)
        state_summary = states.groupby(["model", "state_policy", "count", "method"]).agg(
            n_images=("regret", "size"), mean_regret=("regret", "mean"),
            mean_spearman=("spearman", "mean"), top1_agreement=("top1_agreement", "mean")
        ).reset_index()
        state_summary.to_csv(out / "state_summary.csv", index=False)
        for model in ("deit_small", "vit_base"):
            comparisons_d4 = []
            for count in (180, 164, 147, 98):
                subset = states[(states.model == model) & (states.method == "student") & (states["count"] == count)]
                wide = subset.pivot(index="global_index", columns="state_policy", values="regret")
                value = paired_bootstrap(wide.student.values, wide.tome.values)
                state_contrasts.append({"model": model, "count": count, "comparison": "student_state_minus_tome_state",
                                        **value})
                if count in (147, 98):
                    comparisons_d4.append(value["mean_difference"] >= 1e-5 and value["relative_to_left"] >= 0 and
                                          value["mean_difference"] >= .2 * wide.tome.mean() and value["ci_low"] > 0)
                if count in (180, 164):
                    baseline = ranks[(ranks.cohort == "stability") & (ranks.model == model) &
                                     (ranks.method == "student")].set_index("global_index").regret
                    matched = wide.student.reindex(baseline.index)
                    previous = paired_bootstrap(matched.values, baseline.values)
                    state_contrasts.append({"model": model, "count": count, "comparison": "student_state_minus_196",
                                            **previous})
                    comparisons_d4.append(previous["mean_difference"] >= 1e-5 and
                                          previous["mean_difference"] >= .2 * baseline.mean() and
                                          previous["ci_low"] > 0)
            gates["D4"][model] = bool(any(comparisons_d4))
    else:
        gates["D4"] = {model: "NOT_ENTERED" if not enter_d else "PENDING"
                       for model in ("deit_small", "vit_base")}
    if state_contrasts:
        pd.DataFrame(state_contrasts).to_csv(out / "state_paired_contrasts.csv", index=False)
    if any(gates["D2"].values()):
        path = "B"
    elif any(gates["D1"][m] and gates["D3"][m] for m in gates["D1"]):
        path = "A"
    elif any(v is True for v in gates["D4"].values()):
        path = "C"
    else:
        path = "D"
    gates["recommended_path"] = path
    (out / "gates.json").write_text(json.dumps(gates, indent=2), encoding="utf8")
    fig, axes = plt.subplots(1, 2, figsize=(11, 4), layout="constrained")
    colors = {"cosine": "#555555", "student": "#c44e52",
              "independent_oracle": "#4c72b0", "conditional_greedy_oracle": "#55a868"}
    for axis, model in zip(axes, ("deit_small", "vit_base")):
        table = curve_summary[(curve_summary.cohort == "stability") & (curve_summary.model == model)]
        for method, color in colors.items():
            rows = table[table.method == method].sort_values("k")
            axis.plot(rows.k, rows.mean_distortion, marker="o", label=method.replace("_", " "), color=color)
        axis.set(xlabel="Number of merges", ylabel="Mean normalized logit distortion", title=model)
        axis.set_xticks([1, 2, 4, 8, 16])
        axis.set_yscale("log")
        axis.grid(alpha=.25)
    axes[0].legend(fontsize=8)
    fig.savefig(out / "distortion_curves.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 2, figsize=(12, 4.5), layout="constrained")
    labels = ("high_cosine", "high_oracle", "high_cosine_high_damage",
              "low_damage_different_destination", "low_damage_same_destination")
    short = ("High cosine", "High oracle", "High cosine, harmful",
             "Low damage, distinct dst", "Low damage, shared dst")
    for axis, model, threshold in zip(axes, ("deit_small", "vit_base"), (1e-7, 1e-9)):
        subset = pairs[(pairs.cohort == "stability") & (pairs.model == model)]
        values = [subset[subset.category == label].interaction.dropna().values for label in labels]
        axis.boxplot(values, tick_labels=short, showfliers=False)
        axis.axhline(0, color="black", linewidth=.7)
        axis.set_yscale("symlog", linthresh=threshold)
        axis.set(title=model, ylabel="Pair interaction I(a,b)")
        axis.tick_params(axis="x", rotation=45)
        axis.grid(axis="y", alpha=.25)
    fig.savefig(out / "pair_interaction_distribution.png", dpi=180)
    plt.close(fig)
    print(json.dumps(gates, indent=2))


if __name__ == "__main__":
    main()
