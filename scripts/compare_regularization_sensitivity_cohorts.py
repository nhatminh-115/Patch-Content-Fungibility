"""Compare historical first-200-class and corrected class-randomized summaries."""
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
OLD = ROOT / "outputs" / "fungibility_regularization_sensitivity" / "aggregated_by_architecture_budget_factor.csv"
NEW = ROOT / "outputs" / "fungibility_regularization_sensitivity_v2_class_randomized" / "aggregated_by_architecture_budget_factor.csv"
OUT = ROOT / "outputs" / "fungibility_regularization_sensitivity_v2_class_randomized" / "cohort_comparison_vs_v1.csv"


def main():
    old = pd.read_csv(OLD)
    new = pd.read_csv(NEW)
    keys = ["model", "budget", "method", "lambda_factor"]
    metrics = [
        "n", "top1_rate", "mean_logit_l2_damage", "mean_true_margin_change",
        "mean_operator_residual_JE", "mean_carrier_displacement_fro",
        "mean_trace_HJ_per_ds", "mean_lambda_absolute",
    ]
    merged = old[keys + metrics].merge(
        new[keys + metrics], on=keys, how="outer", suffixes=("_v1_first200_classes", "_v2_class_randomized"),
        validate="one_to_one",
    )
    for metric in metrics:
        merged[f"delta_{metric}_v2_minus_v1"] = (
            merged[f"{metric}_v2_class_randomized"] - merged[f"{metric}_v1_first200_classes"]
        )
    merged["delta_top1_percentage_points_v2_minus_v1"] = 100 * merged["delta_top1_rate_v2_minus_v1"]
    merged["comparison_note"] = (
        "descriptive difference between distinct calibration cohort designs; not paired across cohorts"
    )
    merged.to_csv(OUT, index=False)
    print(f"Saved {len(merged)} matched summary rows: {OUT}")


if __name__ == "__main__":
    main()
