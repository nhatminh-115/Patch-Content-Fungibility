"""Build the publication figure set v4 from audited local outputs only.

No model execution or new empirical measurement is performed.
"""
from __future__ import annotations

import argparse
import base64
import csv
import json
import re
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
    "vit_base": "ViT-Base",
    "vitb": "ViT-B/16",
    "dinov2": "DINOv2 ViT-S/14",
    "DINOv2 ViT-S/14": "DINOv2 ViT-S/14",
    "DeiT-Small": "DeiT-Small",
    "DeiT-Tiny": "DeiT-Tiny",
    "ViT-B/16": "ViT-B/16",
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
    paths = {
        "ViT-B/16 AugReg": root/"outputs/fungibility_v1/vitb_depth_results.csv",
        "DINOv2 ViT-S/14": root/"outputs/fungibility_v1/dinov2_depth_results.csv",
    }
    followup_paths = {
        "ViT-B/16 AugReg": root/"outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv",
        "DINOv2 ViT-S/14": root/"outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv",
    }
    conditions = [("ZERO", "Zero", RED, "--"), ("CENTROID", "Centroid", BLUE, "-"),
                  ("DIAGONAL_GAUSSIAN", "Gaussian", TEAL, "-")]
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.2), sharey=True)
    plotted_by_model = {}
    clean_by_model = {}
    for ax, (model, path) in zip(axs, paths.items()):
        rows = read_csv(path)
        followup = read_csv(followup_paths[model])
        rows.extend(r for r in followup if r["condition"] != "CLEAN")
        clean = next(float(r["top1_accuracy"])*100 for r in rows if r["condition"] == "CLEAN")
        clean_by_model[model] = clean
        ax.axhline(clean, color=GRAY, linewidth=1.1, linestyle=(0, (3, 2)), label="Clean reference (dashed)")
        plotted = {}
        for cond, name, color, ls in conditions:
            agg = grouped([r for r in rows if r["condition"] == cond], ("depth",), "top1_accuracy")
            depths, means, errs = [], [], []
            for depth in sorted({int(k[0]) for k in agg}):
                vals = agg[(str(depth),)]
                depths.append(depth); means.append(sum(vals)/len(vals)*100)
                if len(vals) > 1:
                    mean = sum(vals)/len(vals); errs.append((sum((v-mean)**2 for v in vals)/(len(vals)-1))**0.5*100)
                else:
                    errs.append(0.0)
            ax.errorbar(depths, means, yerr=errs, marker="o", markersize=4.8, linewidth=1.8,
                        capsize=2.5, color=color, linestyle=ls, label=name)
            plotted[name] = (depths, means, errs, color, ls)
        plotted_by_model[model] = plotted
        ax.set_title(model, loc="left", color=INK, pad=10)
        ax.set_xlabel("Intervention depth")
        ax.set_xticks([5, 6, 7, 8, 9, 10])
        ax.set_xlim(4.6, 10.7); ax.set_ylim(0, 86)
        polish_axis(ax, grid="y")
    # Zoom a central region that contains every replacement curve and the clean reference.
    zoom_x = (4.8, 8.3)
    zoom_y = (69.0, 77.5)
    inset = axs[0].inset_axes([.35, .23, .50, .42])
    inset.set_facecolor(PAPER)
    inset.patch.set_alpha(1.0)
    inset.set_zorder(10)
    inset.axhline(clean_by_model["ViT-B/16 AugReg"], color=GRAY, linewidth=1.0,
                  linestyle=(0, (3, 2)), zorder=1)
    for name, (depths, means, errs, color, ls) in plotted_by_model["ViT-B/16 AugReg"].items():
        inset.errorbar(depths, means, yerr=errs, marker="o", markersize=3.2, linewidth=1.35,
                       capsize=1.8, color=color, linestyle=ls, zorder=3)
    inset.set_xlim(*zoom_x); inset.set_ylim(*zoom_y)
    inset.set_xticks([5, 6, 7, 8]); inset.set_yticks([70, 72, 74, 76])
    inset.yaxis.tick_right()
    inset.tick_params(labelsize=6.8, length=2, pad=1.5)
    inset.grid(axis="y", color=GRID, linewidth=.55)
    for spine in inset.spines.values():
        spine.set_edgecolor(BLUE); spine.set_linewidth(1.1)
    axs[0].add_patch(Rectangle((zoom_x[0], zoom_y[0]), zoom_x[1]-zoom_x[0], zoom_y[1]-zoom_y[0],
                               fill=False, edgecolor=BLUE, linewidth=1.2, zorder=5))
    for source_x, target_x in ((zoom_x[0], 0), (zoom_x[1], 1)):
        fig.add_artist(ConnectionPatch((source_x, zoom_y[0]), (target_x, 1),
                                       coordsA="data", axesA=axs[0],
                                       coordsB="axes fraction", axesB=inset,
                                       color=BLUE, linestyle=(0, (3, 2)),
                                       linewidth=.85, alpha=.8, zorder=8))
    axs[0].set_ylabel("Top-1 accuracy (%)")
    handles, labels = axs[0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, ncol=4, loc="lower center",
               bbox_to_anchor=(.5, .012), fontsize=8.5)
    panel_label(axs[0], "a"); panel_label(axs[1], "b")
    fig.tight_layout(rect=(0, .06, 1, .98), w_pad=2.2)
    save_figure(fig, out, "figure2_depthwise")


def fig3(root: Path, out: Path) -> None:
    fig, axs = plt.subplots(1, 2, figsize=(11.8, 5.0), gridspec_kw={"width_ratios": [1.0, 1.12]})
    model_specs = [
        ("ViT-B/16", "ViT-B/16", BLUE, "o"),
        ("DINOv2 ViT-S/14", "DINOv2", TEAL, "s"),
    ]
    legend_handles = [
        Line2D([0], [0], marker="o", linestyle="none", markerfacecolor=BLUE,
               markeredgecolor="white", label="ViT-B/16"),
        Line2D([0], [0], marker="s", linestyle="none", markerfacecolor=TEAL,
               markeredgecolor="white", label="DINOv2"),
        Line2D([0], [0], color=GRAY, linestyle="--", linewidth=1.2, label="Clean reference"),
    ]

    def draw_seed_bar(ax, x: float, values: list[float], color: str, marker: str, width: float = .32):
        mean = sum(values) / len(values)
        sd = (sum((v - mean) ** 2 for v in values) / (len(values) - 1)) ** .5 if len(values) > 1 else 0.0
        ax.bar(x, mean, width=width, color=color, alpha=.24, edgecolor=color, linewidth=.8, zorder=2)
        if sd:
            ax.errorbar(x, mean, yerr=sd, color=color, linewidth=.9, capsize=2.2, zorder=3)
        jitter = [0.0] if len(values) == 1 else [((j / (len(values) - 1)) - .5) * width * .58 for j in range(len(values))]
        ax.scatter([x + dx for dx in jitter], values, s=25, marker=marker, color=color,
                   edgecolor=PAPER, linewidth=.55, zorder=4)

    # (a) Change the geometry of the replacement while keeping a 50% replacement rate.
    ax = axs[0]
    geometry_files = {
        "ViT-B/16": root / "outputs/fungibility_v1/vitb_geometry_results.csv",
        "DINOv2 ViT-S/14": root / "outputs/fungibility_v1/dinov2_geometry_results.csv",
    }
    geometry_conditions = [
        ("CENTROID", "Centroid\n(mean)"),
        ("COORDINATE_PERMUTED_CENTROID", "Shuffled\ncoordinates"),
        ("SIGN_FLIPPED_CENTROID", "Sign-flipped\nvector"),
    ]
    clean_sources = {
        "ViT-B/16": root / "outputs/fungibility_v1/vitb_depth_results.csv",
        "DINOv2 ViT-S/14": root / "outputs/fungibility_v1/dinov2_depth_results.csv",
    }
    for model, path in clean_sources.items():
        clean = next(float(row["top1_accuracy"]) * 100 for row in read_csv(path) if row["condition"] == "CLEAN")
        ax.axhline(clean, color=GRAY, linewidth=.9, linestyle=(0, (3, 2)), alpha=.75, zorder=1)
    for i, (condition, _) in enumerate(geometry_conditions):
        for mi, (model, _, color, marker) in enumerate(model_specs):
            path = geometry_files[model]
            rows = [r for r in read_csv(path) if abs(float(r["fraction"]) - .5) < 1e-9 and r["condition"] == condition]
            values = [float(row["top1_accuracy"]) * 100 for row in rows]
            draw_seed_bar(ax, i + (-.19 if mi == 0 else .19), values, color, marker, width=.32)
    ax.set_xticks(range(3), [title for _, title in geometry_conditions])
    ax.set_xlim(-.58, 2.58); ax.set_ylim(0, 84)
    ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Geometry at 50% replacement", loc="left", color=INK, pad=10)
    polish_axis(ax)

    # (b) Show accuracy as the number K of unique replacement vectors increases.
    ax = axs[1]
    rows = read_csv(root / "outputs/fungibility_v0_8/grouped_diversity_results.csv")
    v08_clean = read_csv(root / "outputs/fungibility_v0_8/statistical_comparisons.csv")
    model_order = ["deit_tiny_patch16_224", "deit_small_patch16_224"]
    model_style = {
        "deit_tiny_patch16_224": (BLUE, "o", "Tiny"),
        "deit_small_patch16_224": (TEAL, "s", "Small"),
    }
    for model in model_order:
        clean = next(100 * float(r["accuracy"]) for r in v08_clean
                     if r["model"] == model and r["condition"] == "clean")
        ax.axhline(clean, color=GRAY, linewidth=.9, linestyle=(0, (3, 2)), alpha=.75, zorder=1)
    for model in model_order:
        color, marker, short_name = model_style[model]
        by_k = grouped([r for r in rows if r["model"] == model], ("k",), "accuracy")
        ks, means, errs = [], [], []
        for k in sorted({int(key[0]) for key in by_k}):
            vals = by_k[(str(k),)]
            mean = sum(vals) / len(vals)
            ks.append(k); means.append(mean * 100)
            errs.append(((sum((v - mean) ** 2 for v in vals) / (len(vals) - 1)) ** .5 * 100)
                        if len(vals) > 1 else 0.0)
        ax.errorbar(ks, means, yerr=errs, marker=marker, markersize=4.8, linewidth=1.7,
                    capsize=2.2, color=color, label=f"DeiT-{short_name}", zorder=3)
    ax.set_xscale("log", base=2)
    ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 196],
                  ["1\nall same", "2", "4", "8", "16", "32", "64", "196\nall distinct"])
    ax.set_ylim(0, 84); ax.set_xlabel("Unique replacement vectors (K)"); ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Accuracy vs. K", loc="left", color=INK, pad=10)
    ax.legend(handles=[
        Line2D([0], [0], color=BLUE, marker="o", linewidth=1.7, label="DeiT-Tiny"),
        Line2D([0], [0], color=TEAL, marker="s", linewidth=1.7, label="DeiT-Small"),
        Line2D([0], [0], color=GRAY, linestyle="--", linewidth=1.2, label="Clean reference"),
    ], frameon=False, fontsize=7.0, loc="lower left", bbox_to_anchor=(.02, .52), handlelength=1.6)
    polish_axis(ax)
    for ax, p in zip(axs, "ab"):
        panel_label(ax, p)
    fig.tight_layout(rect=(0, .10, 1, .97), w_pad=2.0)
    # Keep the panel-(a) model key out of the plotted data region.
    fig.legend(handles=legend_handles, frameon=False, fontsize=7.0, ncol=3,
               loc="lower center", bbox_to_anchor=(.25, .015), handlelength=1.5,
               columnspacing=1.15, handletextpad=.4)
    save_figure(fig, out, "figure3_geometry_diversity")


def fig4(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_functional_geometry/covariance_function_alignment.csv")
    depths = [5, 7, 8, 10]
    models = ["deit_small", "vit_base"]
    values = [[next(float(r["ratio_PC1_to_PCbot"]) for r in rows if r["model_key"] == model and int(r["depth"]) == d)
               for d in depths] for model in models]
    fig, (axh, axd) = plt.subplots(1, 2, figsize=(10.6, 4.6), gridspec_kw={"width_ratios": [1.2, 1]})
    im = axh.imshow(values, cmap="Blues", norm=LogNorm(vmin=0.01, vmax=max(max(row) for row in values)*1.05), aspect="auto")
    axh.set_xticks(range(len(depths)), [str(d) for d in depths]); axh.set_yticks(range(2), ["DeiT-Small", "ViT-Base"])
    axh.set_xlabel("Intervention depth"); axh.set_title("PC1 / bottom PC", loc="left", color=INK)
    for i in range(2):
        for j in range(len(depths)):
            value = values[i][j]
            axh.text(j, i, f"{value:.2f}×" if value < 1 else f"{value:.1f}×", ha="center", va="center",
                     color="white" if value > 17 else INK, fontsize=9, weight="semibold")
    axh.tick_params(length=0)
    for side in axh.spines.values(): side.set_visible(False)
    cb = fig.colorbar(im, ax=axh, fraction=.05, pad=.04); cb.set_label("Sensitivity ratio", fontsize=8); cb.ax.tick_params(labelsize=7)
    panel_label(axh, "a")
    # Vector explanation of feature direction and token-pattern interaction.
    axd.set_xlim(0, 1); axd.set_ylim(0, 1); axd.axis("off"); panel_label(axd, "b")
    axd.set_title("Feature direction", loc="left", color=INK, pad=10)
    axd.text(.07, .82, "token displacement", fontsize=8, color=MUTED)
    # axes / two directions
    axd.add_patch(FancyArrowPatch((.20,.35),(.86,.35),arrowstyle="-|>",mutation_scale=12,color="#AAB3BA",lw=1))
    axd.add_patch(FancyArrowPatch((.24,.24),(.52,.71),arrowstyle="-|>",mutation_scale=12,color=BLUE,lw=2))
    axd.add_patch(FancyArrowPatch((.24,.24),(.75,.52),arrowstyle="-|>",mutation_scale=12,color=TEAL,lw=2))
    axd.text(.49,.74,"PC1",color=BLUE,fontsize=9,weight="semibold")
    axd.text(.76,.55,"bottom PC",color=TEAL,fontsize=9,weight="semibold")
    axd.text(.56,.20,"feature space",color=MUTED,fontsize=8,ha="center")
    fig.tight_layout(rect=(0, .02, 1, .98), w_pad=2.0)
    save_figure(fig, out, "figure4_anisotropic_geometry")


def fig5(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_attention_causal_audit/qkv_decomposition.csv")
    models = [("deit_small", 8, "DeiT-S · Block 8"), ("vit_base", 7, "ViT-B · Block 7")]
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
    metrics = ["Pearson r", "Spearman ρ"]
    single = [c["single_block_pearson_r"], c["single_block_spearman_rho"]]
    multi = [c["multi_block_pearson_r"], c["multi_block_spearman_rho"]]
    fig, (axd, axc) = plt.subplots(1, 2, figsize=(10.8, 4.4), gridspec_kw={"width_ratios": [1, 1.2]})
    axd.set_xlim(0, 1); axd.set_ylim(0, 1); axd.axis("off")
    axd.set_title("Across blocks", loc="left", color=INK, pad=10); panel_label(axd, "a")
    # Local operator vs composition through downstream blocks.
    for i, y in enumerate([.69, .46, .23]):
        box = FancyBboxPatch((.09,y),.32,.13,boxstyle="round,pad=.02,rounding_size=.03",
                             facecolor=LIGHT,edgecolor="#AAB3BA",linewidth=1)
        axd.add_patch(box); axd.text(.25,y+.065,f"Block {8+i}",ha="center",va="center",color=INK,fontsize=8.5)
        if i<2:
            axd.add_patch(FancyArrowPatch((.25,y-.02),(.25,y-.09),arrowstyle="-|>",mutation_scale=9,color=GRAY,lw=1))
    axd.text(.60,.73,"one-block map",color=BLUE,fontsize=8.5,weight="semibold")
    axd.text(.60,.63,"Jₗ",color=BLUE,fontsize=11)
    axd.text(.60,.46,"downstream composition",color=TEAL,fontsize=8.5,weight="semibold")
    axd.text(.60,.34,"Jₗ₊₁ · … · Jᴸ",color=TEAL,fontsize=11)
    # Correlation comparison with directly reported values.
    x = [0, 1]
    axc.plot(x, single, marker="o", color=GRAY, lw=1.8, markersize=6, label="Single block")
    axc.plot(x, multi, marker="o", color=TEAL, lw=2.2, markersize=6, label="End-to-end multi-block")
    for xi, val in zip(x, single): axc.text(xi, val-.045, f"{val:.3f}", color=MUTED, fontsize=8, ha="center")
    for xi, val in zip(x, multi): axc.text(xi, val+.025, f"{val:.3f}", color=TEAL, fontsize=8, ha="center", weight="semibold")
    axc.set_xticks(x, metrics); axc.set_ylim(.6,1.02); axc.set_ylabel("Correlation with held-out damage")
    axc.set_title("Damage prediction", loc="left", color=INK)
    axc.legend(frameon=False, loc="lower right"); polish_axis(axc); panel_label(axc, "b")
    fig.tight_layout(rect=(0, .02, 1, .98), w_pad=2.0)
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
        ax.set_title(model, loc="left", color=INK)
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
    plot_labels = {"ViT-B/16 AugReg": "ViT-B/16"}
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
        ax.set_ylim(49,84); polish_axis(ax)
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
    "figure2_depthwise": ("outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv; outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv", "Original V1 depths 5, 7, 8, 9, 10 plus isolated depth-6 follow-up; CLEAN/ZERO/CENTROID/DIAGONAL_GAUSSIAN; Top-1 accuracy; Gaussian seed-level SD; all under 25% replacement."),
    "figure3_geometry_diversity": ("outputs/fungibility_v1/vitb_geometry_results.csv; outputs/fungibility_v1/dinov2_geometry_results.csv; outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv; outputs/fungibility_v0_8/grouped_diversity_results.csv; outputs/fungibility_v0_8/statistical_comparisons.csv", "Panel (a): V1 rows fraction=0.50 and conditions CENTROID/COORDINATE_PERMUTED_CENTROID/SIGN_FLIPPED_CENTROID for ViT-B/16 AugReg and DINOv2 ViT-S/14, with CLEAN references; panel (b): V0.8 grouped-diversity results across all K values for DeiT-Tiny/Small with model-specific CLEAN references. These are separate study cohorts."),
    "figure4_anisotropic_geometry": ("outputs/fungibility_functional_geometry/covariance_function_alignment.csv", "All 8 model/depth rows; heatmap displays ratio_PC1_to_PCbot. Vector panel is explanatory only."),
    "figure5_value_path_cancellation": ("outputs/fungibility_attention_causal_audit/qkv_decomposition.csv", "model/depth pairs (deit_small,8) and (vit_base,7); token patterns global_coherent/random_sign/checkerboard; feature_dir=jac_top; scale_s=1.0; pathways V_only and K_plus_V; dz_readout_l1."),
    "figure6_end_to_end_operator": ("outputs/fungibility_multiblock_operator/validation_manifest.json", "prediction_correlations single_block/multi_block Pearson and Spearman; primary_findings mean_principal_angle_deg_b8_to_b9."),
    "figure7_operator_compression": ("outputs/fungibility_operator_compression_confirmatory/budget_summary.csv; outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv; docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md", "Filtered budget_summary.csv to Attention Pruning, Group-Mean Merging, ToMe (BSM), Operator-Aware (Oracle), and Operator-Aware (Rank-32), for all budgets and four architectures; rank-16/rank-32 rows are checked in low_rank_ablation.csv. The >98% benefit denominator remains stated in the manuscript caption and confirmatory report."),
    "figureS1_real_carrier_boundary": ("outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv", "batch_size=64; all four architectures and available Clean/Group Mean/q16/q32/Selective q16 rows; fields top1_accuracy and img_per_sec. Output files reside in supp/."),
}


def write_manifest(out: Path) -> None:
    titles = {
          "figure1_overview": ("PCF intervention, replacement constraints, and anisotropic transmission", "User-supplied composite overview of (a) fixed-slot late-layer patch-content intervention, (b) geometry/diversity constraints and Value-path cancellation, and (c) anisotropic transmission."),
        "figure2_depthwise": ("Depth-wise replacement controls", "Replots original V1 results and an isolated depth-6 follow-up, exposes Gaussian seed variation, and zooms the boxed panel-(a) region with Clean, Zero, Centroid, and Gaussian curves."),
        "figure3_geometry_diversity": ("Geometry and diversity constraints", "Two-panel figure: V1 geometry controls at 50% replacement for ViT-B/16 and DINOv2, and V0.8 accuracy versus K for DeiT-Tiny/Small. The cohorts are distinct; interpret contrasts within panels."),
        "figure4_anisotropic_geometry": ("Anisotropic functional geometry", "Shows audited feature-direction sensitivity ratio with a concise geometric explanation."),
        "figure5_value_path_cancellation": ("Value-path transmission and cancellation", "Compares coherent and sign-varying token patterns through V-only and K+V pathways."),
        "figure6_end_to_end_operator": ("Local versus end-to-end operator", "Connects downstream block composition to the audited damage-prediction correlations."),
        "figure7_operator_compression": ("Confirmatory operator-aware compression", "Plots the N=1,000 accuracy-token curves across four architectures; the audited >98% benefit denominator is stated in the manuscript caption and report."),
        "figureS1_real_carrier_boundary": ("Real-model carrier boundary", "Shows the measured accuracy-throughput tradeoff as a bounded supplementary result."),
    }
    lines = ["# Figure Manifest v4", "", "Generated by `scripts/build_paper_figures_v4.py`. White background, DejaVu Sans, consistent typography; SVG and 300 dpi PNG saved for every panel. No models were executed.", ""]
    for i, (stem, (purpose, design)) in enumerate(titles.items(), 1):
        filename = f"{stem}.svg / {stem}.png"
        if stem == "figureS1_real_carrier_boundary":
            filename = f"supp/{filename}"
        sources, filters = FIGURE_SOURCES[stem]
        design_notes = "user-supplied source image preserved pixel-for-pixel in PNG and embedded in an SVG wrapper; no empirical data."
        if stem != "figure1_overview":
            design_notes = "restrained mechanism blue and compression teal; gray references; explicit units and sample units; concise panel titles only, no figure-level headline or embedded bottom caption; vector SVG plus 300 dpi PNG."
        if stem == "figure3_geometry_diversity":
            design_notes = "Two panels only: (a) geometry controls at 50% replacement and (b) the grouped-diversity sweep across K; the former shared-versus-independent panel is omitted; clean accuracy is shown as gray dashed references."
        lines += [f"## {i}. {purpose}", "", f"- **Final filename:** `{filename}`", f"- **Purpose:** {design}", f"- **Source data:** {sources}", "- **Generating script:** `scripts/build_paper_figures_v4.py`", f"- **Rows / filters:** {filters}", f"- **Design notes:** {design_notes}", ""]
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
    write_manifest(out); contact_sheet(out)
    print(f"Rendered 7 main figures + 1 supplement; contact sheet: {out/'contact_sheet.png'}")


if __name__ == "__main__":
    main()
