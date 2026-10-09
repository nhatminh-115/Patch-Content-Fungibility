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
import numpy as np
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
    fig = plt.figure(figsize=(14.2, 8.6))
    outer = fig.add_gridspec(
        2, 2, width_ratios=[1.05, 1.72], height_ratios=[1.16, .84],
        hspace=.48, wspace=.40,
    )
    ax = fig.add_subplot(outer[0, 0])
    diversity_grid = outer[0, 1].subgridspec(2, 2, wspace=.38, hspace=.48)
    diversity_axes = [
        fig.add_subplot(diversity_grid[0, 0]), fig.add_subplot(diversity_grid[0, 1]),
        fig.add_subplot(diversity_grid[1, 0]), fig.add_subplot(diversity_grid[1, 1]),
    ]
    # A centered, narrower third panel keeps the bottom row visually balanced.
    pca_grid = outer[1, :].subgridspec(1, 3, width_ratios=[.68, 1.64, .68], wspace=.04)
    ax_pc = fig.add_subplot(pca_grid[0, 1])
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
            clean = 100 * next(float(r["top1_accuracy"]) for r in v1_depth[model] if r["condition"] == "CLEAN")
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
    ax.set_title("Geometry at 50% replacement", loc="left", color=INK, pad=9)
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
        ax_b.set_title(model_label, loc="left", color=INK, fontsize=8.7, pad=4)
        patch_count = 256 if model == "dinov2" else 196
        ax_b.set_xlabel(f"Distinct vectors, K ({patch_count} patches)", fontsize=7.3)
        if index % 2 == 0:
            ax_b.set_ylabel("Top-1 accuracy (%)", fontsize=7.8)
        polish_axis(ax_b)

    # (c) Calibration-derived PC1 versus a variance-matched random 1D direction.
    deit_pc1 = read_csv(root / "outputs/fungibility_v0_9/pc_identity_results.csv")
    deit_random = read_csv(root / "outputs/fungibility_v0_9/random_direction_results.csv")
    v1_1d = {
        "vitb": read_csv(root / "outputs/fungibility_v1/vitb_1d_results.csv"),
        "dinov2": read_csv(root / "outputs/fungibility_v1/dinov2_1d_results.csv"),
    }
    pca_rows = {}
    for model, model_label, color, marker in all_arch_specs:
        if model.startswith("deit_"):
            pc1_rows = [r for r in deit_pc1 if r["model"] == model
                        and r["condition_type"] == "natural" and r["pc_index"] == "1"]
            random_rows = [r for r in deit_random if r["model"] == model]
            pc1_seeds = {int(r["seed"]) for r in pc1_rows}
            random_seeds = {int(r["seed"]) for r in random_rows}
            expected_pc1 = set(range(17001, 17006))
            expected_random = set(range(18001, 18006))
            if (len(pc1_rows) != 5 or len(random_rows) != 5
                    or pc1_seeds != expected_pc1 or random_seeds != expected_random):
                raise ValueError(f"Unexpected audited PCA seed rows for {model}: PC1={pc1_seeds}; random={random_seeds}.")
            pc1_values = [100 * float(r["accuracy"]) for r in pc1_rows]
            random_values = [100 * float(r["accuracy"]) for r in random_rows]
        else:
            model_rows = v1_1d[model]
            pc1_rows = [r for r in model_rows if r["condition"] == "NATURAL_PC1"]
            random_rows = [r for r in model_rows if r["condition"] == "RANDOM_1D"]
            pc1_seeds = {int(float(r["seed"])) for r in pc1_rows}
            random_seeds = {int(float(r["seed"])) for r in random_rows}
            expected = {25001, 25002, 25003}
            if (len(pc1_rows) != 3 or len(random_rows) != 3
                    or pc1_seeds != expected or random_seeds != expected):
                raise ValueError(f"Unexpected audited PCA seed rows for {model}: PC1={pc1_seeds}; random={random_seeds}.")
            pc1_values = [100 * float(r["top1_accuracy"]) for r in pc1_rows]
            random_values = [100 * float(r["top1_accuracy"]) for r in random_rows]
        pca_rows[model] = {"pc1": pc1_values, "random": random_values}

        center = all_arch_specs.index((model, model_label, color, marker))
        group_x = float(center)
        for condition, values, offset in (("pc1", pc1_values, -.18), ("random", random_values, .18)):
            x = group_x + offset
            mean = statistics.mean(values)
            bar = ax_pc.bar(
                x, mean, width=.28,
                color=color if condition == "pc1" else "white",
                alpha=.42 if condition == "pc1" else 1.0,
                edgecolor=color, linewidth=.9,
                hatch=None if condition == "pc1" else "///", zorder=2,
            )
            jitter = [((j / (len(values) - 1)) - .5) * .07 for j in range(len(values))]
            if condition == "pc1":
                ax_pc.scatter([x + dx for dx in jitter], values, s=19, marker=marker,
                              color=color, edgecolor=PAPER, linewidth=.5, zorder=4)
            else:
                ax_pc.scatter([x + dx for dx in jitter], values, s=19, marker=marker,
                              facecolors=PAPER, edgecolors=color, linewidth=.95, zorder=4)
            if model == "dinov2":
                # Explicit labels keep the near-floor DINOv2 values interpretable on the shared scale.
                label_y = 2.3 if condition == "pc1" else 4.3
                ax_pc.annotate(f"{mean:.2f}", xy=(x, mean), xytext=(x, label_y),
                               ha="center", va="bottom", fontsize=7.2, color=color,
                               arrowprops={"arrowstyle": "-", "color": color, "lw": .65})
            else:
                label_y = max(values) + 1.0
                ax_pc.text(x, label_y, f"{mean:.1f}", ha="center", va="bottom",
                           fontsize=7.2, color=color)

    ax_pc.set_xlim(-.62, 3.62); ax_pc.set_ylim(0, 46)
    ax_pc.set_xticks(range(4), [spec[1] for spec in all_arch_specs])
    ax_pc.set_ylabel("Top-1 accuracy (%)")
    ax_pc.set_title("Calibration-derived PC1 vs. energy-matched random 1D",
                    loc="left", color=INK, fontsize=9.2, pad=8)
    polish_axis(ax_pc)
    treatment_handles = [
        Rectangle((0, 0), 1, 1, facecolor="#B8C8D2", edgecolor=INK,
                  label="Calibration-derived PC1"),
        Rectangle((0, 0), 1, 1, facecolor="white", edgecolor=INK, hatch="///",
                  label="Energy-matched random 1D"),
    ]
    ax_pc.legend(handles=treatment_handles, frameon=False, fontsize=7.0,
                 loc="upper right", ncol=2, handlelength=1.2,
                 columnspacing=.9, handletextpad=.35, borderaxespad=.25)

    fig.subplots_adjust(left=.06, right=.99, top=.92, bottom=.13, wspace=.40, hspace=.48)
    fig.canvas.draw()
    pos_a = ax.get_position(); pos_b = diversity_axes[0].get_position(); pos_c = ax_pc.get_position()
    fig.text(pos_a.x0, pos_a.y1 + .035, "(a)", ha="left", va="bottom",
             fontsize=10, weight="bold", color=INK)
    fig.text(pos_b.x0, pos_b.y1 + .035, "(b)", ha="left", va="bottom",
             fontsize=10, weight="bold", color=INK)
    fig.text(pos_c.x0, pos_c.y1 + .035, "(c)", ha="left", va="bottom",
             fontsize=10, weight="bold", color=INK)
    legend_handles = [
        Line2D([0], [0], color=color, marker=marker, linewidth=1.5, label=model_label)
        for _, model_label, color, marker in all_arch_specs
    ] + [Line2D([0], [0], color=GRAY, linestyle="--", linewidth=1.0, label="Clean accuracy")]
    fig.legend(handles=legend_handles, frameon=False, fontsize=7.2, ncol=5,
               loc="lower center", bbox_to_anchor=(.50, .005), handlelength=1.35,
               columnspacing=.9, handletextpad=.32)
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
    """Plot four-model PC-direction sensitivity and functional-spectrum depth trends."""
    alignment = read_csv(root/"outputs/fungibility_section5_cross_arch_extension/functional_geometry/pc_directional_sensitivity.csv")
    spectrum = read_csv(root/"outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv")
    depths = [5, 7, 8, 10]
    models = [
        ("deit_tiny", "DeiT-Tiny", BLUE, "o"),
        ("deit_small", "DeiT-Small", ORANGE, "s"),
        ("vit_base", "ViT-B/16 AugReg", TEAL, "^"),
        ("dinov2", "DINOv2 ViT-S/14", PURPLE, "D"),
    ]

    def one(rows, model, depth, key, **filters):
        matches = [r for r in rows if r["model_key"] == model and int(r["depth"]) == depth
                   and all(r[k] == str(v) for k, v in filters.items())]
        if len(matches) != 1:
            raise ValueError(f"Expected one {model} depth-{depth} row for {key}; got {len(matches)}.")
        return float(matches[0][key])

    ratios = [[one(alignment, model, depth, "ratio_PC1_to_PC_bottom_raw") for depth in depths]
              for model, _, _, _ in models]
    log_ratios = [[np.log10(value) for value in row] for row in ratios]

    fig = plt.figure(figsize=(12.0, 4.8))
    grid = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.28], wspace=.34)
    axh = fig.add_subplot(grid[0, 0])
    axn = fig.add_subplot(grid[0, 1])

    im = axh.imshow(log_ratios, cmap="RdBu_r",
                    norm=matplotlib.colors.TwoSlopeNorm(vmin=-2, vcenter=0, vmax=2),
                    aspect="auto")
    axh.set_xticks(range(len(depths)), [str(d) for d in depths])
    axh.set_yticks(range(len(models)), [model[1] for model in models])
    axh.set_xlabel("Intervention depth")
    axh.set_title("PC1 / lowest-variance PC sensitivity", loc="left", color=INK, fontsize=8.5, pad=8)
    for i, row in enumerate(ratios):
        for j, value in enumerate(row):
            axh.text(j, i, f"{value:.3g}×", ha="center", va="center",
                     color="white" if abs(np.log10(value)) > 1.15 else INK,
                     fontsize=7.7, weight="semibold")
    axh.tick_params(length=0, labelsize=7.5)
    for side in axh.spines.values():
        side.set_visible(False)
    cb = fig.colorbar(im, ax=axh, fraction=.045, pad=.025, ticks=[-2, -1, 0, 1, 2])
    cb.ax.set_yticklabels(["0.01×", "0.1×", "1×", "10×", "100×"])
    cb.set_label("PC1-to-PCbottom sensitivity ratio (log scale)", fontsize=7.1)
    cb.ax.tick_params(labelsize=6.8)

    for model, name, color, marker in models:
        y = [100*one(spectrum, model, d, "near_null_fraction", relative_cutoff=0.001) for d in depths]
        axn.plot(depths, y, color=color, marker=marker, linewidth=1.8, markersize=4.4,
                 label=name, zorder=3)
    axn.set_xticks(depths)
    axn.set_xlim(4.7, 10.6)
    axn.set_ylim(0, 70)
    axn.set_yticks(range(0, 71, 10))
    axn.set_xlabel("Intervention depth")
    axn.set_ylabel("Near-null eigenvalues (%)")
    axn.set_title("Threshold-defined near-null fraction", loc="left", color=INK, fontsize=8.5, pad=8)
    axn.legend(frameon=False, loc="upper left", fontsize=7.0, handlelength=1.5, ncol=2)
    polish_axis(axn)

    fig.subplots_adjust(left=.14, right=.98, bottom=.16, top=.78)
    panel_label(axh, "a")
    panel_label(axn, "b")
    save_figure(fig, out, "figure4_anisotropic_geometry")


def fig5(root: Path, out: Path) -> None:
    # Matched four-architecture comparison of two common attention conditions.
    primary = read_csv(root / "outputs/fungibility_attention_causal_audit/causal_conditions.csv")
    reduced = read_csv(root / "outputs/fungibility_attention_causal_audit/replication_summary.csv")
    specs = [
        ("deit_small", 8, "DeiT-Small", "a", primary),
        ("vit_base", 7, "ViT-B/16 AugReg", "b", primary),
        ("deit_tiny", 8, "DeiT-Tiny", "c", reduced),
        ("dinov2", 8, "DINOv2 ViT-S/14", "d", reduced),
    ]
    patterns = [
        ("global_coherent", "Coherent"),
        ("random_sign", "Random sign"),
        ("checkerboard", "Checkerboard"),
    ]
    conditions = [
        ("full_perturbation", "Full Q/K/V + residual", BLUE),
        ("frozen_attn_v_only_pert_res", "Frozen A; V + residual", TEAL),
    ]
    verified_rows = 0
    fig, axs = plt.subplots(2, 2, figsize=(10.0, 6.7))
    for ax, (model, depth, title, panel, rows) in zip(axs.flat, specs):
        values = {condition: [] for condition, _, _ in conditions}
        for pattern, _ in patterns:
            for condition, _, _ in conditions:
                matches = [
                    r for r in rows
                    if r["model_key"] == model
                    and int(r["depth"]) == depth
                    and r["token_pattern"] == pattern
                    and r["feature_dir"] == "jac_top"
                    and float(r["scale_s"]) == 1.0
                    and r["condition"] == condition
                ]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected one Figure 5 row for {model}/{depth}/{pattern}/{condition}; "
                        f"got {len(matches)}"
                    )
                value = float(matches[0]["dz_readout_l1"])
                if not np.isfinite(value) or value < 0:
                    raise ValueError(f"Invalid readout norm for {model}/{pattern}/{condition}: {value}")
                values[condition].append(value)
                verified_rows += 1

        x = np.arange(len(patterns))
        width = .34
        for j, (condition, label, color) in enumerate(conditions):
            xpos = x + (j - .5) * width
            ax.bar(xpos, values[condition], width=width, color=color, label=label, zorder=3)
            for xp, value in zip(xpos, values[condition]):
                ax.annotate(
                    f"{value:.3g}", (xp, value), xytext=(0, 3), textcoords="offset points",
                    ha="center", va="bottom", fontsize=6.5, color=INK
                )
        ax.set_xticks(x, [label for _, label in patterns])
        ax.set_ylabel("Mean per-image readout change ‖Δz‖₂")
        ymax = max(max(v) for v in values.values())
        ax.set_ylim(0, ymax * 1.30 if ymax else 1.0)
        ax.set_title(title, loc="center", color=INK, fontsize=9, pad=9)
        ax.text(.5, 1.13, f"({panel})", transform=ax.transAxes, ha="center", va="bottom",
                fontsize=10, weight="bold", color=INK)
        polish_axis(ax)
    if verified_rows != 24:
        raise ValueError(f"Figure 5 expected 24 unique rows, verified {verified_rows}")
    handles, labels = axs[0, 0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2,
               bbox_to_anchor=(.5, .015), fontsize=7.7)
    fig.subplots_adjust(left=.12, right=.98, bottom=.13, top=.92, wspace=.33, hspace=.56)
    save_figure(fig, out, "figure5_value_path_cancellation")


def figS12(root: Path, out: Path) -> None:
    # Preserve the primary V-only versus K+V projection-path audit.
    rows = read_csv(root / "outputs/fungibility_attention_causal_audit/qkv_decomposition.csv")
    models = [
        ("deit_small", 8, "DeiT-Small · Block 8", "a"),
        ("vit_base", 7, "ViT-B/16 AugReg · Block 7", "b"),
    ]
    patterns = [
        ("global_coherent", "Coherent"),
        ("random_sign", "Random sign"),
        ("checkerboard", "Checkerboard"),
    ]
    pathways = [
        ("V_only", "V-only (clean residual)", BLUE),
        ("K_plus_V", "K+V (clean residual)", TEAL),
    ]
    fig, axs = plt.subplots(1, 2, figsize=(9.5, 3.7))
    for ax, (model, depth, title, panel) in zip(axs, models):
        values = {pathway: [] for pathway, _, _ in pathways}
        for pattern, _ in patterns:
            for pathway, _, _ in pathways:
                matches = [
                    r for r in rows
                    if r["model_key"] == model and int(r["depth"]) == depth
                    and r["token_pattern"] == pattern and r["feature_dir"] == "jac_top"
                    and float(r["scale_s"]) == 1.0 and r["pathway"] == pathway
                ]
                if len(matches) != 1:
                    raise ValueError(
                        f"Expected one Q/K/V row for {model}/{depth}/{pattern}/{pathway}; "
                        f"got {len(matches)}"
                    )
                values[pathway].append(float(matches[0]["dz_readout_l1"]))
        x = np.arange(len(patterns))
        width = .34
        for j, (pathway, label, color) in enumerate(pathways):
            xpos = x + (j - .5) * width
            ax.bar(xpos, values[pathway], width=width, color=color, label=label, zorder=3)
            for xp, value in zip(xpos, values[pathway]):
                ax.annotate(f"{value:.3g}", (xp, value), xytext=(0, 3), textcoords="offset points",
                            ha="center", va="bottom", fontsize=6.6, color=INK)
        ax.set_xticks(x, [label for _, label in patterns])
        ax.set_ylabel("Mean per-image readout change ‖Δz‖₂")
        ymax = max(max(v) for v in values.values())
        ax.set_ylim(0, ymax * 1.30 if ymax else 1.0)
        ax.set_title(title, loc="center", color=INK, fontsize=9, pad=9)
        ax.text(.5, 1.13, f"({panel})", transform=ax.transAxes, ha="center", va="bottom",
                fontsize=10, weight="bold", color=INK)
        polish_axis(ax)
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=2,
               bbox_to_anchor=(.5, .015), fontsize=7.7)
    fig.subplots_adjust(left=.11, right=.99, bottom=.18, top=.83, wspace=.32)
    save_figure(fig, out, "figureS12_primary_qkv_decomposition")


def fig6(root: Path, out: Path) -> None:
    """Compare local and end-to-end prediction across models, plus finite-radius direction ratios."""
    correlations = read_csv(root/"outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/model_specific_correlations.csv")
    damage = read_csv(root/"outputs/fungibility_multiblock_operator/replication_summary.csv")
    models = [
        ("deit_tiny", "Tiny", BLUE),
        ("deit_small", "Small", ORANGE),
        ("vit_base", "ViT-B", TEAL),
        ("dinov2", "DINOv2", PURPLE),
    ]
    predictors = [
        ("single_block", "Single-block A", GRAY, -.13),
        ("end_to_end", "End-to-end J", TEAL, .13),
    ]

    fig = plt.figure(figsize=(10.8, 5.7))
    grid = fig.add_gridspec(2, 4, height_ratios=[1.15, .82], hspace=.54, wspace=.45)
    axes = [fig.add_subplot(grid[0, :2]), fig.add_subplot(grid[0, 2:])]
    metric_specs = [
        ("pearson_r", "pearson_ci95_low", "pearson_ci95_high", "Pearson r"),
        ("spearman_rho", "spearman_ci95_low", "spearman_ci95_high", "Spearman ρ"),
    ]
    x = np.arange(len(models))
    for ax, (value_key, low_key, high_key, title) in zip(axes, metric_specs):
        for predictor, predictor_label, color, offset in predictors:
            ys, lows, highs = [], [], []
            for model, _, _ in models:
                row = next(r for r in correlations if r["model_key"] == model and r["predictor"] == predictor)
                y = float(row[value_key])
                ys.append(y)
                lows.append(y-float(row[low_key]))
                highs.append(float(row[high_key])-y)
            ax.errorbar(x+offset, ys, yerr=[lows, highs], fmt="o", color=color,
                        markersize=4.8, capsize=2.6, linewidth=1.0, zorder=3,
                        label=predictor_label)
        ax.set_xticks(x, [m[1] for m in models])
        ax.set_xlim(-.48, 3.48)
        ax.set_ylim(.62, 1.015)
        ax.set_yticks([.6, .7, .8, .9, 1.0])
        ax.set_ylabel("Correlation with observed damage")
        panel = "a" if title == "Pearson r" else "b"
        ax.set_title(f"({panel}) {title}", loc="left", color=INK, fontsize=8.7, pad=8)
        polish_axis(ax)
        ax.tick_params(axis="both", labelsize=7.5)
    axes[0].legend(frameon=False, loc="lower left", fontsize=7.0, ncol=2,
                   handletextpad=.35, columnspacing=.7)
    axr = fig.add_subplot(grid[1, 1:3])
    ratio_rows = []
    for model, name, color in models:
        row = next(r for r in damage if r["arch"] == model)
        ratio = float(row["multi_top_damage_s04"])/float(row["multi_null_damage_s04"])
        ratio_rows.append((name, color, ratio))
    ypos = np.arange(len(ratio_rows))
    axr.barh(ypos, [row[2] for row in ratio_rows], color=[row[1] for row in ratio_rows],
             height=.58, zorder=3)
    axr.set_yticks(ypos, [row[0] for row in ratio_rows])
    axr.invert_yaxis()
    axr.set_xlim(0, 14.5)
    axr.set_xticks([0, 2, 4, 6, 8, 10, 12, 14])
    axr.set_xlabel("Top-mode / multi-block near-null damage ratio")
    axr.set_title("(c) Finite-radius logit damage at s = 0.4", loc="left", color=INK, fontsize=8.7, pad=8)
    for y, (_, _, value) in enumerate(ratio_rows):
        axr.text(value+.18, y, f"{value:.2f}×", va="center", ha="left",
                 fontsize=7.4, color=INK, weight="semibold")
    polish_axis(axr, grid="x")
    axr.tick_params(axis="both", labelsize=7.3)
    fig.subplots_adjust(left=.10, right=.98, bottom=.11, top=.88)
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
                             "Static Feature-PCA q=16": (8, -17),
                             "Static Feature-PCA q=32": (5, 8),
                             "Selective Feature-PCA q16 target30": (-30, 14)}
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
    save_figure(fig,out,"figureS13_real_carrier_boundary")


def figS11(root: Path, out: Path) -> None:
    """Show the reduced Block-8 margin replication for DeiT-Tiny and DINOv2."""
    rows = read_csv(root/"outputs/fungibility_attention_causal_audit/replication_summary.csv")
    models = [
        ("deit_tiny", "DeiT-Tiny"),
        ("dinov2", "DINOv2 ViT-S/14"),
    ]
    patterns = [
        ("global_coherent", "Coherent"),
        ("random_sign", "Random sign"),
        ("checkerboard", "Checkerboard"),
    ]
    conditions = [
        ("full_perturbation", "Full perturbation", BLUE),
        ("frozen_attn_v_only_pert_res", "Frozen-attention V-only", TEAL),
    ]
    fig, axs = plt.subplots(1, 2, figsize=(8.8, 3.45))
    x = np.arange(len(patterns))
    width = .34
    for ax, (model, title) in zip(axs, models):
        for j, (condition, condition_label, color) in enumerate(conditions):
            values = []
            for pattern, _ in patterns:
                match = [r for r in rows if r["model_key"] == model and r["depth"] == "8"
                         and r["token_pattern"] == pattern and r["feature_dir"] == "jac_top"
                         and float(r["scale_s"]) == 1.0 and r["condition"] == condition]
                if len(match) != 1:
                    raise ValueError(f"Expected one replication row for {model}/{pattern}/{condition}; got {len(match)}")
                values.append(float(match[0]["logit_margin_drop"]))
            xpos = x + (j-.5)*width
            ax.bar(xpos, values, width=width, color=color, label=condition_label, zorder=3)
            for xp, value in zip(xpos, values):
                dx = -5 if j == 0 else 5
                ax.annotate(f"{value:.3g}", (xp, value),
                            xytext=(dx, 3 if value >= 0 else -3), textcoords="offset points",
                            ha="right" if j == 0 else "left",
                            va="bottom" if value >= 0 else "top", fontsize=6.8, color=INK)
        ax.axhline(0, color=GRAY, linewidth=.8, zorder=2)
        ax.set_xticks(x, [p[1] for p in patterns])
        ax.set_ylabel("Signed true-class logit drop")
        ax.set_title(title, loc="left", color=INK, fontsize=9, pad=8)
        polish_axis(ax)
        ax.tick_params(axis="both", labelsize=7.2)
    axs[0].legend(frameon=False, fontsize=7.0, loc="upper right")
    for ax, label_text in zip(axs, ("a", "b")):
        panel_label(ax, label_text)
    fig.tight_layout(rect=(0, .02, 1, .98), w_pad=1.6)
    save_figure(fig, out, "figureS11_value_path_replication")


FIGURE_SOURCES = {
    "figure1_overview": ("figures/paper_final_v4/source/figure1_overview_user.png (user-supplied image); no empirical data.", "The supplied overview is reproduced pixel-for-pixel; no numeric result is encoded."),
    "figure2_depthwise": ("outputs/fungibility_v0_6/tiny_depth_fraction_summary.csv; outputs/fungibility_v0_6/tiny_seed_results.csv; outputs/fungibility_v0_6/small_depth_fraction_summary.csv; outputs/fungibility_v0_6/small_seed_results.csv; outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv; outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv", "Depths 5-10 at 25% replacement. DeiT rows filter fraction=25% and use clean_acc, zero_acc, global_mean_acc (calibration-derived centroid), and gaussian_acc; Gaussian seed accuracies are reconstructed from zero_acc plus paired acc_diff and reconciled to the summary means. ViT-B/DINOv2 combine original depths 5, 7-10 with the separate depth-6 follow-up. All cohorts use 1,000 calibration and 1,000 evaluation images per architecture; Gaussian SD is across five DeiT seeds or three ViT-B/DINOv2 seeds."),
    "figure3_geometry_diversity": ("outputs/fungibility_v0_7/tiny_fraction_summary.csv; outputs/fungibility_v0_7/small_fraction_summary.csv; outputs/fungibility_v0_7/tiny_prototype_comparison.csv; outputs/fungibility_v0_7/small_prototype_comparison.csv; outputs/fungibility_v0_7/tiny_sign_flip_sweep.csv; outputs/fungibility_v0_7/small_sign_flip_sweep.csv; outputs/fungibility_v1/vitb_geometry_results.csv; outputs/fungibility_v1/dinov2_geometry_results.csv; outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v0_8/grouped_diversity_results.csv; outputs/fungibility_v0_8/statistical_comparisons.csv; outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv; outputs/fungibility_v0_9/pc_identity_results.csv; outputs/fungibility_v0_9/random_direction_results.csv; outputs/fungibility_v1/vitb_1d_results.csv; outputs/fungibility_v1/dinov2_1d_results.csv", "Panel (a): 50% replacement geometry controls and clean baselines for all four architectures. DeiT centroid and clean values come from the V0.7 fraction summaries; DeiT coordinate-shuffle error bars summarize three saved seed outcomes; DeiT sign inversion comes from the 100%-flip V0.7 control. ViT-B/DINOv2 use V1 geometry and clean-depth CSVs, with three coordinate-shuffle seeds. Each model uses N=1,000 evaluation and N=1,000 calibration images. Panel (b): grouped-diversity Top-1 curves for DeiT-Tiny/Small (three seeds) and ViT-B/16 AugReg/DINOv2 (five seeds), each with a clean-accuracy reference. Panel (c): complete replacement at Block 8 comparing calibration-derived natural PC1 with an energy-matched random 1D direction; per-seed outcomes are shown for all four architectures, with five seeds for DeiT and three for ViT-B/DINOv2. All PCA comparisons use the audited disjoint calibration/evaluation cohorts."),
    "figure4_anisotropic_geometry": ("outputs/fungibility_section5_cross_arch_extension/functional_geometry/pc_directional_sensitivity.csv; outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv", "Panel (a): raw PC1-to-lowest-variance-PC directional margin-sensitivity ratios at depths 5, 7, 8, and 10, plotted as log10(ratio). Panel (b): threshold-defined near-null fraction at λ_k≤10⁻³λ_max. All four models use a matched N=100-image calibration cohort; the updated extension reports raw sensitivities, covariance eigengaps, metric spectra, and cutoff robustness separately."),
    "figure5_value_path_cancellation": ("outputs/fungibility_attention_causal_audit/causal_conditions.csv; outputs/fungibility_attention_causal_audit/replication_summary.csv; outputs/fungibility_attention_causal_audit/validation_manifest.json; patch_fungibility/attention_causal_audit.py", "All panels filter full_perturbation and frozen_attn_v_only_pert_res at feature_dir=jac_top and scale_s=1.0, depths 8/7/8/8 for DeiT-Small/ViT-B/DeiT-Tiny/DINOv2; patterns coherent, random-sign, checkerboard. dz_readout_l1 is the mean of per-image Euclidean norms (torch.norm(dim=-1)), not L1. N=100 images/model; Tiny/DINOv2 are reduced replications. DINOv2 readout concatenates CLS and mean patch representations."),
    "figure6_end_to_end_operator": ("outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/model_specific_correlations.csv; outputs/fungibility_multiblock_operator/replication_summary.csv", "Panels (a,b): model-specific Pearson and Spearman correlations for the prescribed 100-perturbation mixture with stratified-bootstrap 95% intervals. Panel (c): multi-block top-mode / multi-block near-null finite-radius final-logit-L2 damage ratios at s=0.4 for four architectures."),
    "figure7_operator_compression": ("outputs/fungibility_operator_compression_confirmatory/budget_summary.csv; outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv; docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md", "Filtered budget_summary.csv to Attention Pruning, Group-Mean Merging, ToMe (BSM), Operator-Aware (Oracle), and Operator-Aware (Rank-32), for all budgets and four architectures. Rank-16 and rank-32 outcomes are available in low_rank_ablation.csv and Table II; the figure itself contains only the rank-32 curve."),
    "figureS12_primary_qkv_decomposition": ("outputs/fungibility_attention_causal_audit/qkv_decomposition.csv; outputs/fungibility_attention_causal_audit/validation_manifest.json", "DeiT-Small Block 8 and ViT-B/16 AugReg Block 7; feature_dir=jac_top; scale_s=1.0; V_only and K_plus_V; coherent, random-sign, checkerboard; N=100 images. Mean per-image immediate-readout Euclidean L2."),
    "figureS13_real_carrier_boundary": ("outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv", "batch_size=64; all four architectures and available Clean/Group Mean/q16/q32/Selective q16 rows; fields top1_accuracy and img_per_sec. Output files reside in supp/."),
    "figureS10_dinov2_margin_diversity": ("outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv", "DINOv2 ViT-S/14 true-class logit margin versus K under 100% patch replacement at Block 8; points are five-seed means and error bars are sample SD across seeds. N=1,000 held-out evaluation images per seed. Top-1 remains near its floor and is not represented as recovered accuracy."),
    "figureS11_value_path_replication": ("outputs/fungibility_attention_causal_audit/replication_summary.csv; outputs/fungibility_attention_causal_audit/validation_manifest.json", "Block-8 reduced replication in DeiT-Tiny and DINOv2. Signed true-class logit drops under full perturbation versus frozen-attention V-only with perturbed residual for coherent, random-sign, checkerboard. N=100 outcome images/model; direction estimated from first four images; not a full Q/K/V decomposition."),
}


def write_manifest(out: Path) -> None:
    titles = {
          "figure1_overview": ("PCF intervention, replacement constraints, and selective transmission", "User-supplied composite overview of (a) fixed-slot late-layer patch-content intervention, (b) geometric and diversity constraints, and (c) anisotropic sensitivity with Value-path cancellation."),
        "figure2_depthwise": ("Depth-dependent replacement tolerance across four architectures", "Four-panel 2×2 depth sweep for DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, and DINOv2 ViT-S/14, comparing Zero, Centroid, Gaussian, and clean accuracy across depths 5-10."),
        "figure3_geometry_diversity": ("Geometry, token diversity, and feature-space direction", "Panel (a) compares 50% replacement geometry controls across four architectures. Panel (b) shows four common-scale Top-1 facets for token-position diversity under complete grouped-Gaussian replacement; DINOv2 margin remains separately reported in Figure S10. Panel (c) compares calibration-derived PC1 with an energy-matched random 1D direction under complete replacement at Block 8, with per-seed outcomes and the near-floor DINOv2 values explicitly labeled."),
        "figure4_anisotropic_geometry": ("Anisotropic functional geometry", "Shows architecture-dependent covariance-PC directional margin sensitivity and the depth-wise threshold-defined near-null fraction of M_l across four models."),
        "figureS11_value_path_replication": ("Reduced Value-path replication", "Shows coherent, random-sign, and checkerboard signed true-class logit drops for full and frozen-attention V-only perturbations in DeiT-Tiny and DINOv2."),
        "figure5_value_path_cancellation": ("Matched Value-path transmission comparison", "All panels use the same full-perturbation and frozen-attention V-only-with-perturbed-residual conditions, patterns, and mean per-image readout L2. Small/ViT-B are primary audit models; Tiny/DINOv2 are reduced replications. Y-scales are architecture-specific; DINOv2 uses concatenated CLS and mean-patch readout."),
        "figure6_end_to_end_operator": ("Local and end-to-end damage prediction", "Model-specific prediction correlations and finite-radius directional damage contrasts across four architectures."),
        "figure7_operator_compression": ("Confirmatory operator-aware compression", "Plots N=1,000 accuracy-token curves across four architectures, including the measured rank-32 curve; no recovery percentage is encoded."),
        "figureS12_primary_qkv_decomposition": ("Primary Q/K/V projection-path comparison", "Compares V-only with K+V in the primary DeiT-Small and ViT-B audits, with clean residuals and mean per-image immediate-readout L2."),
        "figureS13_real_carrier_boundary": ("Real-model carrier boundary", "Shows the measured accuracy-throughput tradeoff as a bounded supplementary result."),
        "figureS10_dinov2_margin_diversity": ("DINOv2 margin across token diversity", "Shows the five-seed mean true-class logit margin across K; DINOv2 Top-1 remains near floor, so this margin change is not accuracy recovery."),
    }
    lines = ["# Figure Manifest v4", "", "Generated by `scripts/build_paper_figures_v4.py`. White background, DejaVu Sans, consistent typography; SVG and 300 dpi PNG saved for every panel. No models were executed.", ""]
    for i, (stem, (purpose, design)) in enumerate(titles.items(), 1):
        filename = f"{stem}.svg / {stem}.png"
        if stem in ("figureS10_dinov2_margin_diversity", "figureS11_value_path_replication",
                    "figureS12_primary_qkv_decomposition", "figureS13_real_carrier_boundary"):
            filename = f"supp/{filename}"
        sources, filters = FIGURE_SOURCES[stem]
        design_notes = "user-supplied source image preserved pixel-for-pixel in PNG and embedded in an SVG wrapper; no empirical data."
        if stem != "figure1_overview":
            design_notes = "restrained mechanism blue and compression teal; gray references; explicit units and sample units; concise panel titles only, no figure-level headline or embedded bottom caption; vector SVG plus 300 dpi PNG."
        if stem == "figure4_anisotropic_geometry":
            design_notes = "Panel (a) displays all 16 four-model PC1-to-lowest-variance-PC ratios, with color encoding log10(ratio) so values below and above one are visible; raw sensitivities and bottom-PC eigengaps remain available in the source CSV. Panel (b) plots the λ≤10⁻³λmax near-null fraction across depths for all four models. Each model uses N=100 calibration images; cutoff sensitivity and normalized effective ranks are recorded in the supplementary table."
        if stem == "figure3_geometry_diversity":
            design_notes = "Three-panel layout: geometry controls at upper left, four common-scale token-diversity facets at upper right, and a narrower centered PC1-versus-random comparison below. Panel (a) uses model-colored bars; coordinate-shuffle bars show seed means with overlaid individual outcomes and sample-SD error bars, while centroid and sign-inversion bars show single-run estimates. Panel (b) uses seed-level SD error bars and model-specific patch-count endpoints. Panel (c) retains model colors, distinguishes the random direction with hatching and hollow seed markers, and overlays individual seed outcomes on mean bars; DINOv2 means are labeled because both accuracies remain near zero on the shared scale. DINOv2's diversity margin remains in Supplementary Figure S10. No experimental data were changed."
        if stem == "figureS10_dinov2_margin_diversity":
            design_notes = "Code-generated line plot of mean true-class logit margin across K; error bars show SD across five seeds. The margin axis is separate from the Top-1 accuracy display and does not imply accuracy recovery."
        if stem == "figure2_depthwise":
            design_notes = "Clean 2×2 architecture layout with common Top-1 scale, consistent Zero/Centroid/Gaussian colors and markers, and gray dashed clean baselines. Error bars show Gaussian seed-level sample SD; DeiT panels use five seeds, while ViT-B/16 AugReg and DINOv2 panels use three seeds. DeiT centroids use the calibration-derived global mean."
        if stem == "figure6_end_to_end_operator":
            design_notes = "Panels (a,b) show model-specific Pearson and Spearman estimates for single-block A and end-to-end J with stratified-bootstrap 95% intervals. Panel (c) separately plots finite-radius multi-block top-mode / near-null damage ratios. Perturbation vectors, not images or tokens, are the correlation unit."
        if stem == "figureS11_value_path_replication":
            design_notes = "Two independent axes preserve architecture-specific signed true-class logit-drop scales. The outcome is clean target logit minus perturbed target logit; signed bars include negative values and no seed uncertainty is implied. This supplement shows the reduced coherent/random-sign replication, not a complete Q/K/V decomposition."
        if stem == "figure5_value_path_cancellation":
            design_notes = "Every panel filters full_perturbation and frozen_attn_v_only_pert_res at feature_dir=jac_top and scale_s=1.0 and uses mean per-image Euclidean readout L2. Coherent, random-sign, checkerboard patterns appear in order. Panel scales vary by architecture. Tiny/DINOv2 are reduced replications; DINOv2 uses concatenated CLS and mean-patch readout."
        if stem == "figureS12_primary_qkv_decomposition":
            design_notes = "Primary projection-path evidence is limited to DeiT-Small Block 8 and ViT-B/16 AugReg Block 7. V-only perturbs V with clean Q/K and residual; K+V perturbs K/V with clean Q and residual and recomputes attention. Bars use mean per-image Euclidean L2."
        if stem == "figureS13_real_carrier_boundary":
            design_notes = "Bounded classifier-carrier result with measured accuracy and full-model throughput; q=16 has a narrow ViT-B/16 AugReg frontier contribution."
        if stem == "figureS11_value_path_replication":
            design_notes = "Two independent axes preserve architecture-specific signed true-class logit-drop scales; bars include negative values and no seed uncertainty is implied. This reduced replication shows coherent, random-sign, and checkerboard patterns, not a complete Q/K/V decomposition."
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
    parser.add_argument("--only", nargs="+",
                        choices=("figure5", "figureS11", "figureS12", "figureS13"),
                        help="Regenerate only selected assets; the default rebuilds the complete figure set.")
    args = parser.parse_args()
    root=args.root.resolve()
    out=root/"figures/paper_final_v4"; (out/"supp").mkdir(parents=True,exist_ok=True)
    setup_style()
    if args.only is None:
        fig1(root,out); fig2(root,out); fig3(root,out); fig4(root,out); fig5(root,out); fig6(root,out); fig7(root,out)
        fig_s1(root,out/"supp")
        figS10(root,out)
        figS11(root,out/"supp")
        figS12(root,out/"supp")
    else:
        for asset in args.only:
            if asset == "figure5":
                fig5(root,out)
            elif asset == "figureS11":
                figS11(root,out/"supp")
            elif asset == "figureS12":
                figS12(root,out/"supp")
            elif asset == "figureS13":
                fig_s1(root,out/"supp")
    write_manifest(out); contact_sheet(out)
    print(f"Rendered requested figure assets; contact sheet: {out/'contact_sheet.png'}")


if __name__ == "__main__":
    main()
