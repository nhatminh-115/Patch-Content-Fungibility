"""Build the manuscript's combined regularization-sensitivity figure from v2 CSV."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "outputs/fungibility_regularization_sensitivity_v2_class_randomized/aggregated_by_architecture_budget_factor.csv"
OUT = ROOT / "figures/paper_final_v4/supp"
FACTORS = [0.01, 0.1, 1, 3, 10, 30, 100]
MODELS = ["DeiT-Tiny", "DeiT-Small", "ViT-B/16 AugReg", "DINOv2 ViT-S/14"]
COLORS = {
    "DeiT-Tiny": "#2F6FB0",
    "DeiT-Small": "#4C956C",
    "ViT-B/16 AugReg": "#D17A22",
    "DINOv2 ViT-S/14": "#7656A5",
}
METRICS = [
    ("top1_rate", "Top-1 accuracy (%)", "(a) Nonlinear Top-1", False, 100.0),
    ("mean_logit_l2_damage", "Final-logit L₂ damage", "(b) Nonlinear logit damage", True, 1.0),
    ("mean_operator_residual_JE", "Linearized residual ‖JE‖", "(c) Operator residual", True, 1.0),
    ("mean_carrier_displacement_fro", "Carrier displacement ‖Copt − Cmean‖F", "(d) Carrier displacement", True, 1.0),
]


def main() -> None:
    with DATA.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.DictReader(stream))
    data = [row for row in rows if row["method"] == "operator_aware"]
    keys = {(r["model"], int(r["budget"]), float(r["lambda_factor"])) for r in data}
    expected = {
        (model, budget, factor)
        for model in MODELS
        for budget in ((42, 128) if model.startswith("DINOv2") else (32, 98))
        for factor in FACTORS
    }
    if len(data) != 56 or keys != expected or any(int(r["n"]) != 200 for r in data):
        raise ValueError("Expected exactly 56 complete N=200 model-budget-factor aggregate rows")

    plt.rcParams.update({
        "font.family": "DejaVu Sans",
        "font.size": 8.0,
        "axes.labelsize": 8.4,
        "axes.titlesize": 9.0,
        "legend.fontsize": 7.2,
        "svg.fonttype": "none",
    })
    fig, axes = plt.subplots(2, 2, figsize=(7.2, 5.5), constrained_layout=False)
    fig.subplots_adjust(left=0.10, right=0.985, top=0.96, bottom=0.20, hspace=0.38, wspace=0.27)
    budgets = {model: ((42, 128) if model.startswith("DINOv2") else (32, 98)) for model in MODELS}

    for ax, (metric, ylabel, title, log_y, scale) in zip(axes.flat, METRICS):
        for model in MODELS:
            for budget, linestyle, marker in zip(budgets[model], ("-", "--"), ("o", "s")):
                series = sorted(
                    (r for r in data if r["model"] == model and int(r["budget"]) == budget),
                    key=lambda row: float(row["lambda_factor"]),
                )
                xs = [float(r["lambda_factor"]) for r in series]
                ys = [float(r[metric]) * scale for r in series]
                ax.plot(xs, ys, color=COLORS[model], linestyle=linestyle, marker=marker,
                        markersize=3.4, linewidth=1.35, markeredgewidth=0.45)
        ax.set_xscale("log")
        if log_y:
            ax.set_yscale("log")
        ax.set_xticks(FACTORS, labels=["0.01", "0.1", "1", "3", "10", "30", "100"])
        ax.set_xlabel("Regularization factor, f")
        ax.set_ylabel(ylabel)
        ax.set_title(title, loc="left", fontweight="semibold", pad=5)
        ax.grid(axis="y", color="#D9DEE5", linewidth=0.55, alpha=0.85)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(axis="both", labelsize=7.3, length=2.5, pad=2)

    model_handles = [Line2D([0], [0], color=COLORS[m], lw=1.8, label=m) for m in MODELS]
    budget_handles = [
        Line2D([0], [0], color="#4C566A", lw=1.4, linestyle="-", marker="o", markersize=3.2, label="Lower budget"),
        Line2D([0], [0], color="#4C566A", lw=1.4, linestyle="--", marker="s", markersize=3.2, label="Higher budget"),
    ]
    fig.legend(handles=model_handles + budget_handles, loc="lower center", ncol=3,
               frameon=False, bbox_to_anchor=(0.5, 0.015), columnspacing=1.25,
               handlelength=1.8, handletextpad=0.5)
    OUT.mkdir(parents=True, exist_ok=True)
    svg_path = OUT / "figureS15_regularization_sensitivity.svg"
    fig.savefig(svg_path, facecolor="white")
    # Matplotlib's multiline SVG path data contains trailing spaces; strip them
    # so the checked-in vector figure passes whitespace validation.
    svg_path.write_text("\n".join(line.rstrip() for line in svg_path.read_text().splitlines()) + "\n", encoding="utf-8")
    fig.savefig(OUT / "figureS15_regularization_sensitivity.png", dpi=400, facecolor="white")
    plt.close(fig)
    print(f"Rendered S15 from {len(data)} aggregate rows: {OUT}")


if __name__ == "__main__":
    main()
