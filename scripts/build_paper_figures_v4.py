"""Build the publication figure set v4 from audited local outputs only.

No model execution or new empirical measurement is performed.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle, Rectangle, ConnectionPatch
from matplotlib.colors import LogNorm
from PIL import Image, ImageOps, ImageDraw, ImageFont


INK = "#23313D"
MUTED = "#64717B"
GRID = "#E5EAEE"
PAPER = "#FFFFFF"
BLUE = "#246B8E"       # mechanism
TEAL = "#25847A"       # replacement / operator-aware
ORANGE = "#C87931"     # control / comparison
RED = "#B64F52"         # damaging intervention
PURPLE = "#78669B"
GRAY = "#8A949C"
LIGHT = "#F3F6F8"
FONT = "DejaVu Sans"
MODEL_LABELS = {
    "deit_tiny_patch16_224": "DeiT-Tiny",
    "deit_small_patch16_224": "DeiT-Small",
    "deit_small": "DeiT-Small",
    "vit_base": "ViT-B/16 AugReg",
    "vitb": "ViT-B/16 AugReg",
    "dinov2": "DINOv2 ViT-S/14",
    "DINOv2 ViT-S/14": "DINOv2 ViT-S/14",
    "DeiT-Small": "DeiT-Small",
    "DeiT-Tiny": "DeiT-Tiny",
    "ViT-B/16": "ViT-B/16 AugReg",
}
METHOD_COLORS = {
    "CLEAN": GRAY,
    "ZERO": RED,
    "CENTROID": BLUE,
    "DIAGONAL_GAUSSIAN": TEAL,
    "COORDINATE_PERMUTED_CENTROID": ORANGE,
    "SIGN_FLIPPED_CENTROID": PURPLE,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def label(model: str) -> str:
    return MODEL_LABELS.get(model, model)


def setup_style() -> None:
    plt.rcParams.update({
        "font.family": FONT,
        "font.size": 9,
        "axes.titlesize": 11,
        "axes.titleweight": "semibold",
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "svg.fonttype": "none",
        "axes.edgecolor": "#AAB3BA",
        "axes.linewidth": 0.8,
        "figure.facecolor": PAPER,
        "axes.facecolor": PAPER,
        "savefig.facecolor": PAPER,
    })


def panel_label(ax, text: str) -> None:
    ax.text(-0.10, 1.08, f"({text})", transform=ax.transAxes, ha="left", va="top",
            fontsize=10, weight="bold", color=INK)


def polish_axis(ax, *, grid: str | None = "y") -> None:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#AAB3BA")
    ax.spines["bottom"].set_color("#AAB3BA")
    if grid:
        ax.grid(axis=grid, color=GRID, linewidth=0.7)
    ax.set_axisbelow(True)
    ax.tick_params(length=3, color="#87929A", labelcolor=INK)



def save_figure(fig, output_dir: Path, stem: str) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    preview_dir = output_dir / "previews"
    preview_dir.mkdir(exist_ok=True)
    svg = output_dir / f"{stem}.svg"
    png = output_dir / f"{stem}.png"
    fig.savefig(svg, format="svg", bbox_inches="tight", pad_inches=0.08)
    svg_text=svg.read_text(encoding="utf-8")
    svg.write_text("\n".join(line.rstrip() for line in svg_text.splitlines())+"\n",encoding="utf-8",newline="\n")
    fig.savefig(png, format="png", dpi=300, bbox_inches="tight", pad_inches=0.08)
    fig.savefig(preview_dir / f"{stem}.png", format="png", dpi=180, bbox_inches="tight", pad_inches=0.08)
    plt.close(fig)


def fig1(root: Path, out: Path) -> None:
    """Publish the user-supplied overview without altering its raster pixels."""
    source = root / "figures/paper_final_v4/source/figure1_overview_user.png"
    image_bytes = source.read_bytes()
    with Image.open(source) as image:
        width, height = image.size
    (out / "previews").mkdir(parents=True, exist_ok=True)
    (out / "figure1_overview.png").write_bytes(image_bytes)
    (out / "previews/figure1_overview.png").write_bytes(image_bytes)
    encoded = base64.b64encode(image_bytes).decode("ascii")
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">\n'
        f'<image width="{width}" height="{height}" href="data:image/png;base64,{encoded}" '
        'preserveAspectRatio="none"/>\n</svg>\n'
    )
    (out / "figure1_overview.svg").write_text(svg, encoding="utf-8", newline="\n")


def grouped(rows: list[dict[str, str]], key_fields: tuple[str, ...], value_field: str) -> dict[tuple[str, ...], list[float]]:
    result: dict[tuple[str, ...], list[float]] = defaultdict(list)
    for row in rows:
        key = tuple(row[field] for field in key_fields)
        result[key].append(float(row[value_field]))
    return result


def fig2(root: Path, out: Path) -> None:
    depths = list(range(5, 11))

    def deit_series(summary_file: str, seed_file: str, model_id: str) -> dict:
        summary_rows = [r for r in read_csv(root / summary_file)
                        if r["model"] == model_id and r["fraction"] == "25%"]
        if len(summary_rows) != len(depths) or {int(r["depth"]) for r in summary_rows} != set(depths):
            raise ValueError(f"Expected one 25% summary row at each depth for {model_id}")
        summary = {int(r["depth"]): r for r in summary_rows}
        seed_rows = [r for r in read_csv(root / seed_file)
                     if r["model"] == model_id and r["fraction"] == "25%" and r["condition"] == "gaussian"]
        clean_values = {float(r["clean_acc"]) for r in summary_rows}
        if len(clean_values) != 1:
            raise ValueError(f"Clean accuracy varies across {model_id} depth summary rows")

        data = {"depths": depths, "clean": clean_values.pop() * 100,
                "zero": [], "centroid": [], "gaussian": [], "gaussian_sd": []}
        for depth in depths:
            row = summary[depth]
            seeds = [r for r in seed_rows if int(r["depth"]) == depth]
            if len(seeds) != 5 or len({r["seed"] for r in seeds}) != 5:
                raise ValueError(f"Expected five distinct Gaussian seeds for {model_id} depth {depth}")
            # In the V0.6 summary, acc_diff is Gaussian accuracy minus zero accuracy.
            seed_accuracy = [float(row["zero_acc"]) + float(r["acc_diff"]) for r in seeds]
            gaussian_mean = statistics.mean(seed_accuracy)
            if abs(gaussian_mean - float(row["gaussian_acc"])) > 1e-9:
                raise ValueError(f"Seed-level Gaussian mean does not reconcile for {model_id} depth {depth}")
            data["zero"].append(float(row["zero_acc"]) * 100)
            # The paper's centroid is the disjoint-calibration global mean, not same_mean_acc.
            data["centroid"].append(float(row["global_mean_acc"]) * 100)
            data["gaussian"].append(float(row["gaussian_acc"]) * 100)
            data["gaussian_sd"].append(statistics.stdev(seed_accuracy) * 100)
        return data

    def vit_series(depth_file: str, followup_file: str) -> dict:
        original = read_csv(root / depth_file)
        followup = read_csv(root / followup_file)
        original_sweep_depths = {int(r["depth"]) for r in original if r["condition"] != "CLEAN"}
        followup_depths = {int(r["depth"]) for r in followup if r["condition"] != "CLEAN"}
        if original_sweep_depths != {5, 7, 8, 9, 10} or followup_depths != {6}:
            raise ValueError(f"Depth sweep/follow-up coverage is unexpected: {original_sweep_depths}, {followup_depths}")
        clean_original = [r for r in original if r["condition"] == "CLEAN"]
        clean_followup = [r for r in followup if r["condition"] == "CLEAN"]
        if len(clean_original) != 1 or len(clean_followup) != 1:
            raise ValueError("Expected one clean baseline in each ViT/DINO source cohort")
        clean = float(clean_original[0]["top1_accuracy"])
        if int(clean_followup[0]["depth"]) != 6 or abs(float(clean_followup[0]["top1_accuracy"]) - clean) > 1e-12:
            raise ValueError("Depth-6 follow-up clean baseline does not match the original cohort")

        data = {"depths": depths, "clean": clean * 100,
                "zero": [], "centroid": [], "gaussian": [], "gaussian_sd": []}
        conditions = {depth: [r for r in (followup if depth == 6 else original)
                              if int(r["depth"]) == depth] for depth in depths}
        for depth in depths:
            rows = conditions[depth]
            for condition in ("ZERO", "CENTROID"):
                selected = [r for r in rows if r["condition"] == condition]
                if len(selected) != 1:
                    raise ValueError(f"Expected one {condition} value at depth {depth}")
                data["zero" if condition == "ZERO" else "centroid"].append(
                    float(selected[0]["top1_accuracy"]) * 100)
            gaussian = [r for r in rows if r["condition"] == "DIAGONAL_GAUSSIAN"]
            if len(gaussian) != 3 or len({r["seed"] for r in gaussian}) != 3:
                raise ValueError(f"Expected three distinct Gaussian seeds at depth {depth}")
            values = [float(r["top1_accuracy"]) for r in gaussian]
            data["gaussian"].append(statistics.mean(values) * 100)
            data["gaussian_sd"].append(statistics.stdev(values) * 100)
        return data

    panels = [
        ("a", "DeiT-Tiny", deit_series(
            "outputs/fungibility_v0_6/tiny_depth_fraction_summary.csv",
            "outputs/fungibility_v0_6/tiny_seed_results.csv", "deit_tiny_patch16_224")),
        ("b", "DeiT-Small", deit_series(
            "outputs/fungibility_v0_6/small_depth_fraction_summary.csv",
            "outputs/fungibility_v0_6/small_seed_results.csv", "deit_small_patch16_224")),
        ("c", "ViT-B/16 AugReg", vit_series(
            "outputs/fungibility_v1/vitb_depth_results.csv",
            "outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv")),
        ("d", "DINOv2 ViT-S/14", vit_series(
            "outputs/fungibility_v1/dinov2_depth_results.csv",
            "outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv")),
    ]

    fig, axs = plt.subplots(2, 2, figsize=(10.6, 6.55), sharex=True, sharey=True)
    for ax, (panel, model, data) in zip(axs.flat, panels):
        ax.axhline(data["clean"], color=GRAY, linewidth=1.1,
                   linestyle=(0, (3, 2)), zorder=1)
        ax.plot(depths, data["zero"], color=RED, marker="o", markersize=4.5,
                linewidth=1.55, linestyle="--", label="Zero", zorder=3)
        ax.plot(depths, data["centroid"], color=BLUE, marker="s", markersize=4.5,
                markerfacecolor=PAPER, markeredgecolor=BLUE, markeredgewidth=1.0,
                linewidth=1.65, linestyle="-", label="Centroid", zorder=4.5)
        ax.errorbar(depths, data["gaussian"], yerr=data["gaussian_sd"], color=TEAL,
                    marker="^", markersize=4.6, linewidth=1.65, linestyle="-",
                    elinewidth=.9, capsize=2.1, label="Gaussian", zorder=4)
        ax.set_title(f"({panel})  {model}", loc="left", color=INK, pad=9)
        ax.set_xticks(depths)
        ax.set_xlim(4.65, 10.35)
        ax.set_ylim(0, 85)
        ax.set_yticks([0, 20, 40, 60, 80])
        ax.set_xlabel("Intervention depth" if panel in ("c", "d") else "")
        polish_axis(ax, grid="y")
    axs[0, 0].set_ylabel("Top-1 accuracy (%)")
    axs[1, 0].set_ylabel("Top-1 accuracy (%)")

    legend_handles = [
        Line2D([0], [0], color=RED, marker="o", linestyle="--", linewidth=1.55,
               markersize=4.5, label="Zero"),
        Line2D([0], [0], color=BLUE, marker="s", linestyle="-", linewidth=1.65,
               markerfacecolor=PAPER, markeredgecolor=BLUE, markersize=4.5, label="Centroid"),
        Line2D([0], [0], color=TEAL, marker="^", linestyle="-", linewidth=1.65,
               markersize=4.6, label="Gaussian"),
        Line2D([0], [0], color=GRAY, linestyle=(0, (3, 2)), linewidth=1.1,
               label="Clean accuracy"),
    ]
    fig.legend(handles=legend_handles, frameon=False, ncol=4, loc="lower center",
               bbox_to_anchor=(.5, .012), fontsize=8.5, handlelength=2.0)
    fig.tight_layout(rect=(0, .075, 1, .995), w_pad=2.0, h_pad=1.8)
    save_figure(fig, out, "figure2_depthwise")


def fig3(root: Path, out: Path) -> None:
    fig = plt.figure(figsize=(14.6, 7.1))
    grid = fig.add_gridspec(2, 3, width_ratios=[1.55, .95, .95], hspace=.40, wspace=.42)
    ax = fig.add_subplot(grid[:, 0])
    diversity_axes = [
        fig.add_subplot(grid[0, 1]), fig.add_subplot(grid[0, 2]),
        fig.add_subplot(grid[1, 1]), fig.add_subplot(grid[1, 2]),
    ]
    all_arch_specs = [
        ("deit_tiny_patch16_224", "DeiT-Tiny", BLUE, "o"),
        ("deit_small_patch16_224", "DeiT-Small", TEAL, "s"),
        ("vitb", "ViT-B/16 AugReg", ORANGE, "^"),
        ("dinov2", "DINOv2 ViT-S/14", PURPLE, "D"),
    ]

    # (a) Fixed 50% replacement geometry controls across all four architectures.
    deiT_sources = {
        "deit_tiny_patch16_224": {
            "summary": root / "outputs/fungibility_v0_7/tiny_fraction_summary.csv",
            "permutation": root / "outputs/fungibility_v0_7/tiny_prototype_comparison.csv",
            "sign": root / "outputs/fungibility_v0_7/tiny_sign_flip_sweep.csv",
        },
        "deit_small_patch16_224": {
            "summary": root / "outputs/fungibility_v0_7/small_fraction_summary.csv",
            "permutation": root / "outputs/fungibility_v0_7/small_prototype_comparison.csv",
            "sign": root / "outputs/fungibility_v0_7/small_sign_flip_sweep.csv",
        },
    }
    v1_geometry = {
        "vitb": read_csv(root / "outputs/fungibility_v1/vitb_geometry_results.csv"),
        "dinov2": read_csv(root / "outputs/fungibility_v1/dinov2_geometry_results.csv"),
    }
    v1_depth = {
        "vitb": read_csv(root / "outputs/fungibility_v1/vitb_depth_results.csv"),
        "dinov2": read_csv(root / "outputs/fungibility_v1/dinov2_depth_results.csv"),
    }
    geometry = {}
    for model, _, _, _ in all_arch_specs:
        if model in deiT_sources:
            files = deiT_sources[model]
            summary = next(r for r in read_csv(files["summary"]) if r["fraction"] == "50%")
            permutation_rows = [
                r for r in read_csv(files["permutation"])
                if r["fraction"] == "50%" and r["family"] == "coord_perm"
                and r["control"].startswith("coord_perm_seed_")
            ]
            sign = next(
                r for r in read_csv(files["sign"])
                if r["fraction"] == "50%" and r["flip_condition"] == "sign_flip_100%"
            )
            geometry[model] = {
                "clean": 100 * float(summary["clean_acc"]),
                "centroid": [100 * float(summary["mu8_acc"])],
                "coordinate_shuffle": [100 * float(r["acc_control"]) for r in permutation_rows],
                "sign_inversion": [100 * float(sign["accuracy"])],
            }
        else:
            rows = [r for r in v1_geometry[model] if abs(float(r["fraction"]) - .5) < 1e-9]
            clean = next(float(r["top1_accuracy"]) * 100 for r in v1_depth[model] if r["condition"] == "CLEAN")
            by_condition = {
                "CENTROID": [r for r in rows if r["condition"] == "CENTROID"],
                "COORDINATE_PERMUTED_CENTROID": [r for r in rows if r["condition"] == "COORDINATE_PERMUTED_CENTROID"],
                "SIGN_FLIPPED_CENTROID": [r for r in rows if r["condition"] == "SIGN_FLIPPED_CENTROID"],
            }
            geometry[model] = {
                "clean": clean,
                "centroid": [100 * float(r["top1_accuracy"]) for r in by_condition["CENTROID"]],
                "coordinate_shuffle": [100 * float(r["top1_accuracy"]) for r in by_condition["COORDINATE_PERMUTED_CENTROID"]],
                "sign_inversion": [100 * float(r["top1_accuracy"]) for r in by_condition["SIGN_FLIPPED_CENTROID"]],
            }

    for model, _, _, _ in all_arch_specs:
        ax.axhline(geometry[model]["clean"], color=GRAY, linewidth=.8,
                   linestyle=(0, (3, 2)), alpha=.62, zorder=1)

    condition_keys = ("centroid", "coordinate_shuffle", "sign_inversion")
    condition_labels = ("Centroid", "Coordinate\nshuffle", "Sign\ninversion")
    model_offsets = (-.33, -.11, .11, .33)
    for condition_index, condition in enumerate(condition_keys):
        for model_index, (model, _, color, marker) in enumerate(all_arch_specs):
            values = geometry[model][condition]
            x = condition_index + model_offsets[model_index]
            mean = statistics.mean(values)
            sd = statistics.stdev(values) if len(values) > 1 else 0.0
            ax.bar(x, mean, width=.17, color=color, alpha=.24, edgecolor=color,
                   linewidth=.75, zorder=2)
            if sd:
                ax.errorbar(x, mean, yerr=sd, fmt=marker, markersize=5.2,
                            markerfacecolor=color, markeredgecolor=PAPER, markeredgewidth=.6,
                            ecolor=color, elinewidth=.95, capsize=2.4, zorder=4)
                jitter = [((j / (len(values) - 1)) - .5) * .055 for j in range(len(values))]
                ax.scatter([x + dx for dx in jitter], values, s=15, marker=marker,
                           color=color, alpha=.72, edgecolor=PAPER, linewidth=.45, zorder=5)
            else:
                ax.scatter([x], [mean], s=31, marker=marker, color=color,
                           edgecolor=PAPER, linewidth=.55, zorder=4)

    ax.set_xticks(range(3), condition_labels)
    ax.set_xlim(-.60, 2.60); ax.set_ylim(0, 84)
    ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Geometry at 50% replacement", loc="left", color=INK, pad=10)
    polish_axis(ax)

    # (b) Architecture-specific accuracy facets for the grouped-diversity sweep.
    rows = read_csv(root / "outputs/fungibility_v0_8/grouped_diversity_results.csv")
    v08_clean = read_csv(root / "outputs/fungibility_v0_8/statistical_comparisons.csv")
    extension = read_csv(root / "outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv")
    for index, (model, model_label, color, marker) in enumerate(all_arch_specs):
        ax_b = diversity_axes[index]
        if model.startswith("deit_"):
            model_rows = [r for r in rows if r["model"] == model]
            by_k = grouped(model_rows, ("k",), "accuracy")
            ks = sorted({int(key[0]) for key in by_k})
            means = [100 * sum(by_k[(str(k),)]) / len(by_k[(str(k),)]) for k in ks]
            errs = [100 * ((sum((v - sum(by_k[(str(k),)]) / len(by_k[(str(k),)])) ** 2
                                 for v in by_k[(str(k),)]) / (len(by_k[(str(k),)]) - 1)) ** .5)
                    for k in ks]
            clean = 100 * next(float(r["accuracy"]) for r in v08_clean
                               if r["model"] == model and r["condition"] == "clean")
        else:
            model_rows = [r for r in extension if r["model"] == model]
            ks = [int(r["k"]) for r in model_rows]
            means = [100 * float(r["top1_accuracy_mean"]) for r in model_rows]
            errs = [100 * float(r["top1_accuracy_sd_across_seeds"]) for r in model_rows]
            clean = 100 * next(float(r["top1_accuracy"]) for r in v1_depth[model]
                               if r["condition"] == "CLEAN")
        ax_b.axhline(clean, color=GRAY, linewidth=.9, linestyle=(0, (3, 2)), alpha=.8, zorder=1)
        ax_b.errorbar(ks, means, yerr=errs, marker=marker, markersize=4.4, linewidth=1.55,
                      capsize=2.0, color=color, zorder=3)
        ax_b.set_xscale("log", base=2)
        ax_b.set_xticks(ks, [str(k) for k in ks])
        ax_b.set_ylim(0, 84)
        ax_b.set_title(model_label, loc="left", color=INK, fontsize=9.0, pad=5)
        ax_b.set_xlabel(f"Distinct vectors, K (N={196 if model != 'dinov2' else 256})", fontsize=7.7)
        if index % 2 == 0:
            ax_b.set_ylabel("Top-1 accuracy (%)")
        polish_axis(ax_b)

    # Keep panel labels on the same figure-level baseline despite the unequal panel heights.
    fig.text(.012, .988, "(a)", ha="left", va="top", fontsize=10, weight="bold", color=INK)
    fig.text(.405, .988, "(b)", ha="left", va="top", fontsize=10, weight="bold", color=INK)
    legend_handles = [
        Line2D([0], [0], color=color, marker=marker, linewidth=1.5, label=model_label)
        for _, model_label, color, marker in all_arch_specs
    ] + [Line2D([0], [0], color=GRAY, linestyle="--", linewidth=1.0, label="Clean accuracy")]
    fig.legend(handles=legend_handles, frameon=False, fontsize=7.5, ncol=5,
               loc="lower center", bbox_to_anchor=(.60, .005), handlelength=1.45,
               columnspacing=1.0, handletextpad=.35)
    fig.subplots_adjust(left=.055, right=.99, top=.95, bottom=.14, wspace=.42, hspace=.42)
    save_figure(fig, out, "figure3_geometry_diversity")

def figS10(root: Path, out: Path) -> None:
    rows = [r for r in read_csv(
        root / "outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv"
    ) if r["model"] == "dinov2"]
    rows.sort(key=lambda r: int(r["k"]))
    ks = [int(r["k"]) for r in rows]
    margins = [float(r["mean_true_class_margin"]) for r in rows]
    errors = [float(r["mean_margin_sd_across_seeds"]) for r in rows]
    fig, ax = plt.subplots(figsize=(5.2, 3.5))
    ax.errorbar(ks, margins, yerr=errors, marker="D", markersize=4.6, linewidth=1.7,
                capsize=2.5, color=PURPLE, zorder=3)
    ax.axhline(0, color=GRAY, linewidth=.8, linestyle=(0, (3, 2)), zorder=1)
    ax.set_xscale("log", base=2)
    ax.set_xticks(ks, [str(k) for k in ks])
    ax.set_xlabel("Distinct surrogate vectors (K; N=256 patches)")
    ax.set_ylabel("Mean true-class logit margin")
    ax.set_title("DINOv2: margin under complete replacement", loc="left", color=INK, pad=8)
    ax.set_ylim(min(m - e for m, e in zip(margins, errors)) - .12,
                max(m + e for m, e in zip(margins, errors)) + .12)
    polish_axis(ax)
    fig.tight_layout()
    save_figure(fig, out / "supp", "figureS10_dinov2_margin_diversity")


def fig4(root: Path, out: Path) -> None:
    alignment = read_csv(root/"outputs/fungibility_functional_geometry/covariance_function_alignment.csv")
    dimensions = read_csv(root/"outputs/fungibility_functional_geometry/fungible_dimension.csv")
    depths = [5, 7, 8, 10]
    models = [
        ("deit_small", "DeiT-Small", BLUE, "o"),
        ("vit_base", "ViT-B/16 AugReg", ORANGE, "s"),
    ]

    def value_for(rows, model, depth, key):
        matches = [row for row in rows if row["model_key"] == model and int(row["depth"]) == depth]
        if len(matches) != 1:
            raise ValueError(f"Expected one {model} depth-{depth} row for {key}; found {len(matches)}.")
        return float(matches[0][key])

    ratios = [[value_for(alignment, model, depth, "ratio_PC1_to_PCbot") for depth in depths]
              for model, _, _, _ in models]
    fig = plt.figure(figsize=(11.7, 4.2))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.05, 1.35], wspace=.34)
    axh = fig.add_subplot(grid[0, 0])
    axn = fig.add_subplot(grid[0, 1])

    im = axh.imshow(ratios, cmap="Blues", norm=LogNorm(vmin=.01, vmax=max(max(row) for row in ratios)*1.05), aspect="auto")
    axh.set_box_aspect(.57)
    axh.set_xticks(range(len(depths)), [str(depth) for depth in depths])
    axh.set_yticks(range(len(models)), [model[1] for model in models])
    axh.set_xlabel("Intervention depth")
    axh.set_title("PC1 / lowest-variance PC sensitivity", loc="left", color=INK, fontsize=8.5, pad=8)
    for i, row in enumerate(ratios):
        for j, value in enumerate(row):
            axh.text(j, i, f"{value:.4g}×", ha="center", va="center",
                     color="white" if value > 17 else INK, fontsize=8.1, weight="semibold")
    axh.tick_params(length=0, labelsize=7.5)
    for side in axh.spines.values():
        side.set_visible(False)
    cb = fig.colorbar(im, ax=axh, fraction=.045, pad=.025)
    cb.set_label("Ratio of directional sensitivities", fontsize=7.3)
    cb.ax.tick_params(labelsize=7)

    for (model, name, color, marker) in models:
        y = [100.0*value_for(dimensions, model, depth, "null_subspace_fraction") for depth in depths]
        axn.plot(depths, y, color=color, marker=marker, linewidth=1.9, markersize=4.5,
                 label=name, zorder=3)
    axn.set_xticks(depths)
    axn.set_xlim(4.7, 10.8)
    axn.set_ylim(0, 65)
    axn.set_yticks(range(0, 61, 10))
    axn.set_xlabel("Intervention depth")
    axn.set_ylabel("Threshold-defined near-null fraction (%)")
    axn.set_title("Near-null fraction across depth", loc="left", color=INK, fontsize=8.5, pad=8)
    axn.legend(frameon=False, loc="upper left", fontsize=7.3, handlelength=1.6)
    axn.annotate("57.03%", (10, 57.03125), xytext=(7, 0), textcoords="offset points",
                 ha="left", va="center", fontsize=7.2, color=BLUE)
    axn.annotate("49.61%", (10, 49.609375), xytext=(7, -1), textcoords="offset points",
                 ha="left", va="center", fontsize=7.2, color=ORANGE)
    polish_axis(axn)
    axh.spines["top"].set_visible(False)
    axh.spines["right"].set_visible(False)
    axh.spines["left"].set_visible(False)
    axh.spines["bottom"].set_visible(False)

    fig.subplots_adjust(left=.12, right=.98, bottom=.18, top=.76)
    for ax, label_text in ((axh, "(a)"), (axn, "(b)")):
        ax.text(.5, 1.18, label_text, transform=ax.transAxes, ha="center", va="bottom",
                fontsize=10, weight="bold", color=INK)
    save_figure(fig, out, "figure4_anisotropic_geometry")


def fig5(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_attention_causal_audit/qkv_decomposition.csv")
    models = [("deit_small", 8, "DeiT-Small · Block 8"), ("vit_base", 7, "ViT-B/16 AugReg · Block 7")]
    patterns = [("global_coherent", "Coherent"), ("random_sign", "Random sign"), ("checkerboard", "Checkerboard")]
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 4.4), sharey=True)
    x = list(range(len(patterns))); width = .34
    for ax, (model, depth, title) in zip(axs, models):
        values = {}
        for pathway, name in [("V_only", "V-only"), ("K_plus_V", "K+V")]:
            ys = []
            for pattern, _ in patterns:
                matches = [r for r in rows if r["model_key"] == model and int(r["depth"]) == depth
                           and r["token_pattern"] == pattern and r["feature_dir"] == "jac_top"
                           and float(r["scale_s"]) == 1.0 and r["pathway"] == pathway]
                if len(matches) != 1:
                    raise ValueError(f"Expected one qkv row for {model}/{depth}/{pattern}/{pathway}; got {len(matches)}")
                ys.append(float(matches[0]["dz_readout_l1"]))
            values[pathway] = ys
        ax.bar([v-width/2 for v in x], values["V_only"], width=width, color=BLUE, label="V-only", zorder=3)
        ax.bar([v+width/2 for v in x], values["K_plus_V"], width=width, color=TEAL, label="K+V", zorder=3)
        ax.set_xticks(x, [p[1] for p in patterns])
        ax.set_title(title, loc="left", color=INK, pad=9)
        panel_label(ax, "a" if model == "deit_small" else "b")
        polish_axis(ax)
    axs[0].set_ylabel("Immediate readout disturbance ‖Δz‖₁")
    axs[0].legend(frameon=False, loc="upper right")
    fig.tight_layout(rect=(0, .02, 1, .98), w_pad=2.0)
    save_figure(fig, out, "figure5_value_path_cancellation")

def fig6(root: Path, out: Path) -> None:
    manifest = read_json(root/"outputs/fungibility_multiblock_operator/validation_manifest.json")
    c = manifest["prediction_correlations"]
    single = [c["single_block_pearson_r"], c["single_block_spearman_rho"]]
    multi = [c["multi_block_pearson_r"], c["multi_block_spearman_rho"]]

    # A single full-width plot avoids repeating the method description in a
    # schematic; the caption defines the local and end-to-end operators.
    fig, ax = plt.subplots(figsize=(6.75, 2.75))
    x = [0, 1]
    offset = .15
    for i, val in enumerate(single):
        xpos = x[i] - offset
        ax.scatter([xpos], [val], s=58, color=GRAY, edgecolor=PAPER, linewidth=.8, zorder=4)
        ax.annotate(f"{val:.3f}", (xpos, val), xytext=(0, 7), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.0, color=MUTED)
    for i, val in enumerate(multi):
        xpos = x[i] + offset
        ax.scatter([xpos], [val], s=62, color=TEAL, edgecolor=PAPER, linewidth=.8, zorder=4)
        ax.annotate(f"{val:.3f}", (xpos, val), xytext=(0, 7), textcoords="offset points",
                    ha="center", va="bottom", fontsize=8.0, color=TEAL, weight="semibold")

    ax.set_xlim(-.42, 1.42); ax.set_ylim(.60, 1.06)
    ax.set_xticks(x, ["Pearson r", "Spearman ρ"])
    ax.set_yticks([.60, .70, .80, .90, 1.00])
    ax.set_ylabel("Correlation with held-out damage", fontsize=8.5)
    handles = [
        Line2D([], [], marker="o", linestyle="none", markersize=5.8, color=GRAY, label="Single block"),
        Line2D([], [], marker="o", linestyle="none", markersize=5.8, color=TEAL, label="End-to-end multi-block"),
    ]
    ax.legend(handles=handles, frameon=False, loc="lower right", fontsize=7.3,
              borderaxespad=.35, handletextpad=.45)
    polish_axis(ax)
    ax.tick_params(axis="both", labelsize=8.0)
    fig.subplots_adjust(left=.105, right=.985, bottom=.22, top=.97)
    save_figure(fig, out, "figure6_end_to_end_operator")
def fig7(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_operator_compression_confirmatory/budget_summary.csv")
    rank_rows = read_csv(root/"outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv")
    if not {16, 32}.issubset({int(r["rank"]) for r in rank_rows}):
        raise ValueError("Audited rank-16/rank-32 rows are missing.")
    methods = [
        ("Attention Pruning", "Attention prune", RED),
        ("Group-Mean Merging", "Group mean", GRAY),
        ("ToMe (BSM)", "ToMe", ORANGE),
        ("Operator-Aware (Oracle)", "Operator oracle", BLUE),
        ("Operator-Aware (Rank-32)", "Operator rank 32", TEAL),
    ]
    models = ["DeiT-Tiny", "DeiT-Small", "ViT-B/16", "DINOv2 ViT-S/14"]
    fig, axs = plt.subplots(2, 2, figsize=(10.8, 7.2), sharex=True, sharey=False)
    for ax, model in zip(axs.flat, models):
        subset = [r for r in rows if r["model"] == model]
        clean = float(subset[0]["clean_acc"])*100
        ax.axhline(clean, color="#B6BEC4", linestyle=(0,(3,2)), linewidth=.9)
        plotted_accuracies = [clean]
        for method, name, color in methods:
            pts = sorted((float(r["rem_frac"])*100, float(r["top1_acc"])*100)
                         for r in subset if r["method"] == method)
            if not pts: continue
            xs, ys = zip(*pts)
            plotted_accuracies.extend(ys)
            ax.plot(xs, ys, marker="o", markersize=3.8, linewidth=1.55, color=color, label=name)
        display_model = "ViT-B/16 AugReg" if model == "ViT-B/16" else model
        ax.set_title(display_model, loc="left", color=INK)
        low, high = min(plotted_accuracies), max(plotted_accuracies)
        pad = max(1.0, .08 * (high - low))
        ax.set_xlim(10, 80); ax.set_ylim(low-pad, high+pad)
        polish_axis(ax)
    for ax in axs[-1,:]: ax.set_xlabel("Retained patch tokens (%)")
    axs[0,0].set_ylabel("Top-1 accuracy (%)"); axs[1,0].set_ylabel("Top-1 accuracy (%)")
    handles, labels = axs[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=3,
               bbox_to_anchor=(.5,.09), fontsize=8.0)
    for ax,p in zip(axs.flat,"abcd"): panel_label(ax,p)
    fig.tight_layout(rect=(0, .15, 1, .98), h_pad=1.8, w_pad=1.8)
    save_figure(fig, out, "figure7_operator_compression")


def fig_s1(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv")
    rows = [r for r in rows if int(r["batch_size"]) == 64]
    models = ["DeiT-Tiny", "DeiT-Small", "ViT-B/16 AugReg", "DINOv2 ViT-S/14"]
    plot_labels = {}
    methods = [
        ("Clean", "Clean", GRAY, "o"),
        ("Hybrid Group Mean", "Group mean", TEAL, "o"),
        ("Static Feature-PCA q=16", "Static q16", BLUE, "D"),
        ("Static Feature-PCA q=32", "Static q32", ORANGE, "s"),
        ("Selective Feature-PCA q16 target30", "Selective q16", PURPLE, "^"),
    ]
    fig, axs = plt.subplots(2,2,figsize=(10.5,7.0),sharex=False,sharey=True)
    for ax, model in zip(axs.flat, models):
        subset = [r for r in rows if r["architecture"] == model]
        for method, name, color, marker in methods:
            pts = [r for r in subset if r["method"] == method]
            if not pts: continue
            xs = [float(r["img_per_sec"]) for r in pts]
            ys = [float(r["top1_accuracy"]) for r in pts]
            ax.scatter(xs, ys, s=38, color=color, marker=marker, edgecolor=PAPER, linewidth=.5, label=name, zorder=3)
            label_offsets = {"Clean": (4, 7), "Hybrid Group Mean": (5, 8),
                             "Static Feature-PCA q=16": (5, -13),
                             "Static Feature-PCA q=32": (5, 8),
                             "Selective Feature-PCA q16 target30": (-22, 8)}
            for r,x,y in zip(pts,xs,ys):
                suffix = {"Clean":"clean", "Hybrid Group Mean":"GM", "Static Feature-PCA q=16":"q16",
                          "Static Feature-PCA q=32":"q32", "Selective Feature-PCA q16 target30":"sel"}[method]
                ax.annotate(suffix, (x,y), xytext=label_offsets[method], textcoords="offset points", fontsize=6.8, color=INK)
        ax.set_title(plot_labels.get(model,model),loc="left",color=INK); ax.set_xlabel("Full-model throughput (images/s)")
        ax.set_ylim(64,82); ax.set_yticks([65,70,75,80]); polish_axis(ax)
    axs[0,0].set_ylabel("Top-1 accuracy (%)"); axs[1,0].set_ylabel("Top-1 accuracy (%)")
    handles, labels = axs[0,0].get_legend_handles_labels()
    # union to include only the common five methods
    hmap={}
    for ax in axs.flat:
        h,l=ax.get_legend_handles_labels()
        for hh,ll in zip(h,l): hmap[ll]=hh
    fig.legend([hmap[name] for _,name,_,_ in methods if name in hmap], [name for _,name,_,_ in methods if name in hmap],
               frameon=False,loc="lower center",ncol=5,bbox_to_anchor=(.5,.035))
    for ax,p in zip(axs.flat,"abcd"): panel_label(ax,p)
    fig.tight_layout(rect=(0,.10,1,.98),h_pad=1.7,w_pad=1.8)
    save_figure(fig,out,"figureS1_real_carrier_boundary")


FIGURE_SOURCES = {
    "figure1_overview": ("figures/paper_final_v4/source/figure1_overview_user.png (user-supplied image); no empirical data.", "The supplied overview is reproduced pixel-for-pixel; no numeric result is encoded."),
    "figure2_depthwise": ("outputs/fungibility_v0_6/tiny_depth_fraction_summary.csv; outputs/fungibility_v0_6/tiny_seed_results.csv; outputs/fungibility_v0_6/small_depth_fraction_summary.csv; outputs/fungibility_v0_6/small_seed_results.csv; outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv; outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv", "Depths 5-10 at 25% replacement. DeiT rows filter fraction=25% and use clean_acc, zero_acc, global_mean_acc (calibration-derived centroid), and gaussian_acc; Gaussian seed accuracies are reconstructed from zero_acc plus paired acc_diff and reconciled to the summary means. ViT-B/DINOv2 combine original depths 5, 7-10 with the separate depth-6 follow-up. All cohorts use 1,000 calibration and 1,000 evaluation images per architecture; Gaussian SD is across five DeiT seeds or three ViT-B/DINOv2 seeds."),
    "figure3_geometry_diversity": ("outputs/fungibility_v0_7/tiny_fraction_summary.csv; outputs/fungibility_v0_7/small_fraction_summary.csv; outputs/fungibility_v0_7/tiny_prototype_comparison.csv; outputs/fungibility_v0_7/small_prototype_comparison.csv; outputs/fungibility_v0_7/tiny_sign_flip_sweep.csv; outputs/fungibility_v0_7/small_sign_flip_sweep.csv; outputs/fungibility_v1/vitb_geometry_results.csv; outputs/fungibility_v1/dinov2_geometry_results.csv; outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v0_8/grouped_diversity_results.csv; outputs/fungibility_v0_8/statistical_comparisons.csv; outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv", "Panel (a): 50% replacement geometry controls and clean baselines for all four architectures. DeiT centroid and clean values come from the V0.7 fraction summaries; DeiT coordinate-shuffle error bars summarize three saved seed outcomes; DeiT sign inversion comes from the 100%-flip V0.7 control. ViT-B/DINOv2 use V1 geometry and clean-depth CSVs, with three coordinate-shuffle seeds. Each model uses N=1,000 evaluation and N=1,000 calibration images. Panel (b): grouped-diversity Top-1 curves for DeiT-Tiny/Small (three seeds) and ViT-B/16 AugReg/DINOv2 (five seeds), each with a clean-accuracy reference. The extension reuses the V1 calibration/evaluation splits and statistics."),
    "figure4_anisotropic_geometry": ("outputs/fungibility_functional_geometry/covariance_function_alignment.csv; outputs/fungibility_functional_geometry/fungible_dimension.csv", "Panel (a): PC1-to-lowest-variance-PC directional margin-sensitivity ratios at depths 5, 7, 8, and 10. Panel (b): threshold-defined near-null eigenvalue fraction (λ_k≤10⁻³λ_max) across the same depths. Both panels use the N=100-image functional-geometry pilot for DeiT-Small and ViT-B/16 AugReg."),
    "figure5_value_path_cancellation": ("outputs/fungibility_attention_causal_audit/qkv_decomposition.csv", "model/depth pairs (deit_small,8) and (vit_base,7); token patterns global_coherent/random_sign/checkerboard; feature_dir=jac_top; scale_s=1.0; pathways V_only and K_plus_V; dz_readout_l1."),
    "figure6_end_to_end_operator": ("outputs/fungibility_multiblock_operator/validation_manifest.json", "prediction_correlations single_block/multi_block Pearson and Spearman; primary_findings mean_principal_angle_deg_b8_to_b9."),
    "figure7_operator_compression": ("outputs/fungibility_operator_compression_confirmatory/budget_summary.csv; outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv; docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md", "Filtered budget_summary.csv to Attention Pruning, Group-Mean Merging, ToMe (BSM), Operator-Aware (Oracle), and Operator-Aware (Rank-32), for all budgets and four architectures. Rank-16 and rank-32 outcomes are available in low_rank_ablation.csv and Table II; the figure itself contains only the rank-32 curve."),
    "figureS1_real_carrier_boundary": ("outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv", "batch_size=64; all four architectures and available Clean/Group Mean/q16/q32/Selective q16 rows; fields top1_accuracy and img_per_sec. Output files reside in supp/."),
    "figureS10_dinov2_margin_diversity": ("outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv", "DINOv2 ViT-S/14 true-class logit margin versus K under 100% patch replacement at Block 8; points are five-seed means and error bars are sample SD across seeds. N=1,000 held-out evaluation images per seed. Top-1 remains near its floor and is not represented as recovered accuracy."),
}


def write_manifest(out: Path) -> None:
    titles = {
          "figure1_overview": ("PCF intervention, replacement constraints, and selective transmission", "User-supplied composite overview of (a) fixed-slot late-layer patch-content intervention, (b) geometric and diversity constraints, and (c) anisotropic sensitivity with Value-path cancellation."),
        "figure2_depthwise": ("Depth-dependent replacement tolerance across four architectures", "Four-panel 2×2 depth sweep for DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, and DINOv2 ViT-S/14, comparing Zero, Centroid, Gaussian, and clean accuracy across depths 5-10."),
        "figure3_geometry_diversity": ("Geometry and diversity constraints", "Panel (a) compares 50% replacement geometry controls across all four architectures. Panel (b) uses four architecture-specific, common-scale Top-1 facets for grouped diversity; DINOv2 margin is reported separately in Figure S10."),
        "figure4_anisotropic_geometry": ("Anisotropic functional geometry", "Combines architecture-dependent PC-to-margin-sensitivity alignment with the depth-wise threshold-defined near-null fraction of M_l."),
        "figure5_value_path_cancellation": ("Value-path transmission and cancellation", "Compares coherent and sign-varying token patterns through V-only and K+V pathways."),
        "figure6_end_to_end_operator": ("Local and end-to-end damage prediction", "Single-panel paired-dot comparison of local and end-to-end operator prediction correlations with measured final-logit damage."),
        "figure7_operator_compression": ("Confirmatory operator-aware compression", "Plots N=1,000 accuracy-token curves across four architectures, including the measured rank-32 curve; no recovery percentage is encoded."),
        "figureS1_real_carrier_boundary": ("Real-model carrier boundary", "Shows the measured accuracy-throughput tradeoff as a bounded supplementary result."),
        "figureS10_dinov2_margin_diversity": ("DINOv2 margin across token diversity", "Shows the five-seed mean true-class logit margin across K; DINOv2 Top-1 remains near floor, so this margin change is not accuracy recovery."),
    }
    lines = ["# Figure Manifest v4", "", "Generated by `scripts/build_paper_figures_v4.py`. White background, DejaVu Sans, consistent typography; SVG and 300 dpi PNG saved for every panel. No models were executed.", ""]
    for i, (stem, (purpose, design)) in enumerate(titles.items(), 1):
        filename = f"{stem}.svg / {stem}.png"
        if stem in ("figureS1_real_carrier_boundary", "figureS10_dinov2_margin_diversity"):
            filename = f"supp/{filename}"
        sources, filters = FIGURE_SOURCES[stem]
        design_notes = "user-supplied source image preserved pixel-for-pixel in PNG and embedded in an SVG wrapper; no empirical data."
        if stem != "figure1_overview":
            design_notes = "restrained mechanism blue and compression teal; gray references; explicit units and sample units; concise panel titles only, no figure-level headline or embedded bottom caption; vector SVG plus 300 dpi PNG."
        if stem == "figure4_anisotropic_geometry":
            design_notes = "Panel (a) displays all 8 audited PC1-to-lowest-variance-PC directional margin-sensitivity ratios on a logarithmic color scale, with four significant digits. Panel (b) plots the threshold-defined near-null eigenvalue fraction across depths, with endpoint values labeled. Both panels use N=100 image samples per architecture; standardized PCA score-density maps were removed because they added no independent functional evidence."
        if stem == "figure3_geometry_diversity":
            design_notes = "Panel (a) is widened and uses color-coded bars for the four models; coordinate-shuffle bars show seed means with overlaid individual outcomes and sample-SD error bars, while centroid and sign-inversion bars show single-run estimates. Gray dashed lines mark model-specific clean baselines; model colors/markers match panel (b). Panel (b) uses four common-scale accuracy small multiples with model-specific K endpoints and seed-level SD error bars. DINOv2 margin is separated into Supplementary Figure S10 because its accuracy remains at floor. The figure-level (a)/(b) labels share one horizontal baseline."
        if stem == "figureS10_dinov2_margin_diversity":
            design_notes = "Code-generated line plot of mean true-class logit margin across K; error bars show SD across five seeds. The margin axis is separate from the Top-1 accuracy display and does not imply accuracy recovery."
        if stem == "figure2_depthwise":
            design_notes = "Clean 2×2 architecture layout with common Top-1 scale, consistent Zero/Centroid/Gaussian colors and markers, and gray dashed clean baselines. Error bars show Gaussian seed-level sample SD; DeiT panels use five seeds, while ViT-B/16 AugReg and DINOv2 panels use three seeds. DeiT centroids use the calibration-derived global mean."
        if stem == "figure6_end_to_end_operator":
            design_notes = "A single full-width panel uses paired dots for Pearson r and Spearman rho, with no connecting lines between distinct metrics. Correlations are evaluated on N=100 held-out perturbations; the caption defines the single-block A8 and end-to-end J8→12 operators."
        generator = "`scripts/build_paper_figures_v4.py`"
        lines += [f"## {i}. {purpose}", "", f"- **Final filename:** `{filename}`", f"- **Purpose:** {design}", f"- **Source data:** {sources}", f"- **Generating script:** {generator}", f"- **Rows / filters:** {filters}", f"- **Design notes:** {design_notes}", ""]
    (out/"FIGURE_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


def contact_sheet(out: Path) -> None:
    paths = sorted(out.glob("figure*.png")) + sorted((out/"supp").glob("figure*.png"))
    thumbs = []
    canvas_w = 900; cell_w = 430; cell_h = 300; pad = 20
    for path in paths:
        rgba = Image.open(path).convert("RGBA")
        im = Image.new("RGBA", rgba.size, "white")
        im.alpha_composite(rgba)
        im = im.convert("RGB")
        im.thumbnail((cell_w-2*pad, cell_h-52), Image.Resampling.LANCZOS)
        cell = Image.new("RGB", (cell_w, cell_h), "white")
        x = (cell_w-im.width)//2; y = 35+(cell_h-52-im.height)//2
        cell.paste(im,(x,y))
        draw=ImageDraw.Draw(cell)
        draw.text((pad,10),path.stem,fill="#23313D")
        cell=ImageOps.expand(cell,border=1,fill="#D6DDE2")
        thumbs.append(cell)
    cols=2; rows=(len(thumbs)+cols-1)//cols
    sheet=Image.new("RGB",(cols*cell_w+pad,rows*cell_h+pad),(246,248,249))
    for i,im in enumerate(thumbs): sheet.paste(im,(pad+(i%cols)*cell_w,pad+(i//cols)*cell_h))
    sheet.save(out/"contact_sheet.png",quality=95)


def main() -> None:
    parser=argparse.ArgumentParser()
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    root=parser.parse_args().root.resolve()
    out=root/"figures/paper_final_v4"; (out/"supp").mkdir(parents=True,exist_ok=True)
    setup_style()
    fig1(root,out); fig2(root,out); fig3(root,out); fig4(root,out); fig5(root,out); fig6(root,out); fig7(root,out)
    fig_s1(root,out/"supp")
    figS10(root,out)
    write_manifest(out); contact_sheet(out)
    print(f"Rendered 7 main figures + 2 supplements; contact sheet: {out/'contact_sheet.png'}")


if __name__ == "__main__":
    main()
