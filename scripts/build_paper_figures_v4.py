"""Build the publication figure set v4 from audited local outputs only.

No model execution or new empirical measurement is performed.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Circle
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


def note(fig, text: str, y: float = 0.025) -> None:
    fig.text(0.04, y, text, ha="left", va="bottom", fontsize=7.6, color=MUTED)


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


def fig1(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.2, 4.5))
    ax.set_xlim(0, 11.2); ax.set_ylim(0, 4.5); ax.axis("off")
    # Four precise stages; patch grids are vector primitives, not generic icons.
    stages = [(0.35, 2.72, 1.65, 0.9, "Image", "patchify"),
              (2.55, 2.72, 1.85, 0.9, "Patch stream at ℓ", "CLS and positions fixed"),
              (5.05, 2.72, 1.90, 0.9, "Replace content", "slots and weights fixed"),
              (7.62, 2.72, 1.60, 0.9, "Downstream J", "functional map"),
              (9.72, 2.72, 1.18, 0.9, "Readout", "measure Δz")]
    for i, (x, y, w, h, title, sub) in enumerate(stages):
        edge = BLUE if i in (1, 3) else TEAL if i == 2 else "#9AA5AD"
        box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04,rounding_size=0.08",
                             facecolor=LIGHT, edgecolor=edge, linewidth=1.25)
        ax.add_patch(box)
        ax.text(x + w/2, y + 0.57, title, ha="center", va="center", color=INK, fontsize=9.5, weight="semibold")
        ax.text(x + w/2, y + 0.27, sub, ha="center", va="center", color=MUTED, fontsize=7.4)
    for a, b in [(2.0, 2.55), (4.4, 5.05), (6.95, 7.62), (9.22, 9.72)]:
        ax.add_patch(FancyArrowPatch((a, 3.17), (b, 3.17), arrowstyle="-|>", mutation_scale=10,
                                     color="#6F7C85", linewidth=1.15))
    # Image/patch stream tile swatches.
    for r in range(3):
        for c in range(4):
            color = ["#B9CCD6", "#DAE3E8", "#9DBBC8", "#E8EEF1"][(r*3+c) % 4]
            ax.add_patch(plt.Rectangle((0.66+c*0.24, 1.94-r*0.24), 0.19, 0.19,
                                      facecolor=color, edgecolor=PAPER, linewidth=0.4))
            ax.add_patch(plt.Rectangle((3.02+c*0.25, 1.94-r*0.24), 0.19, 0.19,
                                      facecolor=[BLUE, "#A9C6D1", TEAL, "#D6E2E7"][(r+c) % 4],
                                      edgecolor=PAPER, linewidth=0.4))
    ax.text(0.95, 1.13, "pixels → patch tokens", ha="center", color=MUTED, fontsize=8)
    ax.text(3.48, 1.13, "class token + slots held fixed", ha="center", color=MUTED, fontsize=8)
    # Three candidate replacement rules.
    ax.text(5.97, 2.10, "candidate content", ha="center", color=INK, fontsize=8, weight="semibold")
    swatches = [("zero", RED), ("centroid", BLUE), ("Gaussian", ORANGE)]
    for j, (name, color) in enumerate(swatches):
        yy = 1.70-j*0.36
        ax.add_patch(Circle((5.34, yy), 0.075, facecolor=color, edgecolor="none"))
        ax.text(5.52, yy, name, ha="left", va="center", color=INK, fontsize=8)
    ax.text(8.42, 2.06, "geometry + diversity", ha="center", color=BLUE, fontsize=8.5, weight="semibold")
    ax.text(8.42, 1.70, "constrain transmission", ha="center", color=MUTED, fontsize=8)
    ax.text(10.28, 2.06, "damage /", ha="center", color=INK, fontsize=8.5, weight="semibold")
    ax.text(10.28, 1.70, "compression", ha="center", color=INK, fontsize=8.5, weight="semibold")
    ax.add_patch(FancyArrowPatch((6.98, 1.48), (7.63, 1.48), arrowstyle="-|>", mutation_scale=10,
                                 color=TEAL, linewidth=1.2))
    ax.text(5.6, 0.48, "Mechanism: N=100 images · Multi-block: N=100 perturbations · Confirmatory: N=1,000 images/model",
            color=MUTED, fontsize=8, ha="center")
    fig.suptitle("Patch-content replacement is a controlled intervention", x=0.04, y=0.98,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    save_figure(fig, out, "figure1_overview")


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
    conditions = [("ZERO", "Zero", RED, "--"), ("CENTROID", "Centroid", BLUE, "-"),
                  ("DIAGONAL_GAUSSIAN", "Gaussian", TEAL, "-")]
    fig, axs = plt.subplots(1, 2, figsize=(10.6, 4.2), sharey=True)
    for ax, (model, path) in zip(axs, paths.items()):
        rows = read_csv(path)
        clean = next(float(r["top1_accuracy"])*100 for r in rows if r["condition"] == "CLEAN")
        xclean = [5, 10]
        ax.axhline(clean, color=GRAY, linewidth=1.1, linestyle=(0, (3, 2)), label="Clean reference")
        ax.text(10.12, clean, f"clean {clean:.1f}", color=MUTED, fontsize=7.5, va="center")
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
        ax.set_title(model, loc="left", color=INK, pad=10)
        ax.set_xlabel("Intervention depth")
        ax.set_xticks([5, 7, 8, 9, 10])
        ax.set_xlim(4.6, 10.7); ax.set_ylim(0, 86)
        polish_axis(ax, grid="y")
    axs[0].set_ylabel("Top-1 accuracy (%)")
    axs[0].legend(frameon=False, ncol=2, loc="lower left", bbox_to_anchor=(0, 0.01))
    panel_label(axs[0], "a"); panel_label(axs[1], "b")
    note(fig, "25% spatial-patch replacement; N=1,000 images/model. Error bars show SD across logged seeds; clean reference is the raw CLEAN row.")
    fig.suptitle("Late-layer replacement depends on the surrogate", x=0.04, y=1.02,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    fig.tight_layout(rect=(0, 0.09, 1, 0.95), w_pad=2.2)
    save_figure(fig, out, "figure2_depthwise")


def fig3(root: Path, out: Path) -> None:
    files = [("ViT-B/16", root/"outputs/fungibility_v1/vitb_geometry_results.csv"),
             ("DINOv2 ViT-S/14", root/"outputs/fungibility_v1/dinov2_geometry_results.csv")]
    fig, axs = plt.subplots(1, 3, figsize=(13.0, 4.7), gridspec_kw={"width_ratios": [1.15, 1.1, 1.15]})
    # (a) Feature-coordinate geometry control; individual randomized permutation seeds remain visible.
    ax = axs[0]
    conditions = [("CENTROID", "Centroid"), ("COORDINATE_PERMUTED_CENTROID", "Permuted"),
                  ("SIGN_FLIPPED_CENTROID", "Sign-flipped")]
    offsets = {"ViT-B/16": -0.10, "DINOv2 ViT-S/14": 0.10}
    for model, path in files:
        rows = [r for r in read_csv(path) if abs(float(r["fraction"])-0.5) < 1e-9]
        for i, (condition, _) in enumerate(conditions):
            vals = [float(r["top1_accuracy"])*100 for r in rows if r["condition"] == condition]
            xs = [i+offsets[model]+(j-(len(vals)-1)/2)*0.035 for j in range(len(vals))]
            color = BLUE if model == "ViT-B/16" else TEAL
            ax.scatter(xs, vals, s=28, color=color, edgecolor=PAPER, linewidth=0.5, zorder=3,
                       marker="o" if model == "ViT-B/16" else "s")
            if vals:
                mean = sum(vals)/len(vals)
                ax.plot([i+offsets[model]-0.07, i+offsets[model]+0.07], [mean, mean], color=INK, lw=1.5)
    ax.set_xticks(range(3), [x[1] for x in conditions], rotation=15, ha="right")
    ax.set_ylabel("Top-1 accuracy (%)"); ax.set_ylim(0, 82)
    ax.set_title("Coordinate geometry · 50% replacement", loc="left", color=INK)
    ax.scatter([], [], color=BLUE, marker="o", label="ViT-B/16")
    ax.scatter([], [], color=TEAL, marker="s", label="DINOv2")
    ax.legend(frameon=False, loc="lower left", ncol=1)
    polish_axis(ax)

    # (b) Shared versus independently sampled surrogates; each seed is shown.
    ax = axs[1]
    rows = read_csv(root/"outputs/fungibility_v0_8/shared_vs_independent_results.csv")
    model_order = ["deit_tiny_patch16_224", "deit_small_patch16_224"]
    types = [("shared_noise", "Shared"), ("independent_noise", "Independent")]
    for mi, model in enumerate(model_order):
        for ti, (cond, _) in enumerate(types):
            vals = [100*float(r["accuracy"]) for r in rows if r["model"] == model and r["condition_type"] == cond]
            x = mi*3+ti
            color = BLUE if mi == 0 else TEAL
            ax.scatter([x+(j-(len(vals)-1)/2)*0.045 for j in range(len(vals))], vals,
                       s=25, color=color, alpha=.9, edgecolor=PAPER, linewidth=.4)
            if vals:
                mean = sum(vals)/len(vals)
                ax.plot([x-.22, x+.22], [mean, mean], color=INK, lw=1.2)
    ax.set_xticks([0, 1, 3, 4], ["Shared\nTiny", "Independent\nTiny", "Shared\nSmall", "Independent\nSmall"], rotation=0, ha="center")
    ax.set_xlim(-.6, 4.6); ax.set_ylim(0, 82); ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Complete-stream surrogates", loc="left", color=INK)
    polish_axis(ax)

    # (c) More carrier groups help but do not imply full recovery.
    ax = axs[2]
    rows = read_csv(root/"outputs/fungibility_v0_8/grouped_diversity_results.csv")
    for model, color, marker in [("deit_tiny_patch16_224", BLUE, "o"), ("deit_small_patch16_224", TEAL, "s")]:
        by_k = grouped([r for r in rows if r["model"] == model], ("k",), "accuracy")
        ks, means, errs = [], [], []
        for k in sorted({int(key[0]) for key in by_k}):
            vals = by_k[(str(k),)]; mean = sum(vals)/len(vals)
            ks.append(k); means.append(mean*100)
            errs.append(((sum((v-mean)**2 for v in vals)/(len(vals)-1))**0.5*100) if len(vals)>1 else 0)
        ax.errorbar(ks, means, yerr=errs, marker=marker, markersize=4.5, linewidth=1.6,
                    capsize=2, color=color, label=label(model))
    ax.set_xscale("log", base=2); ax.set_xticks([1, 2, 4, 8, 16, 32, 64, 196], ["1", "2", "4", "8", "16", "32", "64", "196"])
    ax.set_ylim(0, 82); ax.set_xlabel("Distinct carrier groups (K)"); ax.set_ylabel("Top-1 accuracy (%)")
    ax.set_title("Grouped-stream diversity", loc="left", color=INK); ax.legend(frameon=False, loc="lower right")
    polish_axis(ax)
    for ax, p in zip(axs, "abc"): panel_label(ax, p)
    fig.suptitle("Replacement depends on feature geometry and token diversity", x=0.04, y=1.02,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    note(fig, "(a) V1 geometry CSVs, fraction=0.50; points are logged rows/seeds. (b,c) V0.8 complete-stream studies; N=1,000 evaluation images/model, with calibration disjoint.")
    fig.tight_layout(rect=(0, 0.12, 1, 0.94), w_pad=1.7)
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
    axh.set_xlabel("Intervention depth"); axh.set_title("PC1 / bottom-PC sensitivity", loc="left", color=INK)
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
    axd.set_title("Same token pattern, different feature direction", loc="left", color=INK, pad=10)
    axd.text(.07, .82, "token displacement", fontsize=8, color=MUTED)
    # axes / two directions
    axd.add_patch(FancyArrowPatch((.20,.35),(.86,.35),arrowstyle="-|>",mutation_scale=12,color="#AAB3BA",lw=1))
    axd.add_patch(FancyArrowPatch((.24,.24),(.52,.71),arrowstyle="-|>",mutation_scale=12,color=BLUE,lw=2))
    axd.add_patch(FancyArrowPatch((.24,.24),(.75,.52),arrowstyle="-|>",mutation_scale=12,color=TEAL,lw=2))
    axd.text(.49,.74,"PC1",color=BLUE,fontsize=9,weight="semibold")
    axd.text(.76,.55,"bottom PC",color=TEAL,fontsize=9,weight="semibold")
    axd.text(.56,.20,"feature space",color=MUTED,fontsize=8,ha="center")
    axd.text(.50,.04,"Functional sensitivity is anisotropic",color=INK,fontsize=9,ha="center",weight="semibold")
    fig.suptitle("Functional geometry is direction-dependent", x=0.04, y=1.02,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    note(fig, "Heatmap values are the audited ratio_PC1_to_PCbot field from the N=100 functional-geometry pilot; right panel is an explanatory vector schematic.")
    fig.tight_layout(rect=(0, .11, 1, .94), w_pad=2.0)
    save_figure(fig, out, "figure4_anisotropic_geometry")


def fig5(root: Path, out: Path) -> None:
    rows = read_csv(root/"outputs/fungibility_attention_causal_audit/qkv_decomposition.csv")
    models = [("deit_small", 8, "DeiT-Small · depth 8"), ("vit_base", 7, "ViT-Base · depth 7")]
    patterns = [("global_coherent", "Coherent"), ("random_sign", "Random sign"), ("checkerboard", "Checkerboard")]
    fig, axs = plt.subplots(1, 2, figsize=(9.8, 4.4), sharey=True)
    for ax, (model, depth, title) in zip(axs, models):
        for pathway, name, color, marker, offset in [("V_only", "V-only", BLUE, "o", -0.12),
                                                       ("K_plus_V", "K+V", TEAL, "s", 0.12)]:
            xs, ys = [], []
            for i, (pattern, _) in enumerate(patterns):
                matches = [r for r in rows if r["model_key"] == model and int(r["depth"]) == depth
                           and r["token_pattern"] == pattern and r["feature_dir"] == "jac_top"
                           and float(r["scale_s"]) == 1.0 and r["pathway"] == pathway]
                if len(matches) != 1:
                    raise ValueError(f"Expected one qkv row for {model}/{depth}/{pattern}/{pathway}; got {len(matches)}")
                xs.append(i+offset); ys.append(float(matches[0]["dz_readout_l1"]))
            ax.scatter(xs, ys, marker=marker, color=color, s=45, label=name, zorder=3)
        panel = "a" if model == "deit_small" else "b"
        ax.set_xticks(range(3), [p[1] for p in patterns]); ax.set_title(f"({panel})  {title}", loc="left", color=INK, pad=11)
        ax.set_ylabel("Immediate readout disturbance ‖Δz‖₁" if model == "deit_small" else "")
        polish_axis(ax)
    axs[0].legend(frameon=False, loc="upper right")
    # Compact vector explanation, no added quantitative claims.
    fig.text(.12, .18, "coherent", color=BLUE, fontsize=8, weight="semibold")
    fig.text(.53, .18, "random signs", color=MUTED, fontsize=8, weight="semibold")
    for i in range(5):
        x=.21+i*.045; fig.add_artist(FancyArrowPatch((x,.155),(x+.025,.155),transform=fig.transFigure,
                          arrowstyle="-|>",mutation_scale=7,color=BLUE,lw=1.2))
    for i, direction in enumerate([1,-1,1,-1,1]):
        x=.64+i*.045; y=.155
        fig.add_artist(FancyArrowPatch((x,y),(x+.025,y+direction*.025),transform=fig.transFigure,
                          arrowstyle="-|>",mutation_scale=7,color=GRAY,lw=1.2))
    fig.suptitle("The Value path carries coherent patch perturbations to the readout", x=0.04, y=1.02,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    note(fig, "N=100 attention-audit images; jac_top, scale s=1.0; raw QKV-decomposition dz_readout_l1. Schematic arrows explain coherence only.")
    fig.tight_layout(rect=(0, .25, 1, .94), w_pad=2.0)
    save_figure(fig, out, "figure5_value_path_cancellation")


def fig6(root: Path, out: Path) -> None:
    manifest = read_json(root/"outputs/fungibility_multiblock_operator/validation_manifest.json")
    c = manifest["prediction_correlations"]
    metrics = ["Pearson r", "Spearman ρ"]
    single = [c["single_block_pearson_r"], c["single_block_spearman_rho"]]
    multi = [c["multi_block_pearson_r"], c["multi_block_spearman_rho"]]
    angle = manifest["primary_findings"]["mean_principal_angle_deg_b8_to_b9"]
    fig, (axd, axc) = plt.subplots(1, 2, figsize=(10.8, 4.4), gridspec_kw={"width_ratios": [1, 1.2]})
    axd.set_xlim(0, 1); axd.set_ylim(0, 1); axd.axis("off")
    axd.set_title("Functional map across depth", loc="left", color=INK, pad=10); panel_label(axd, "a")
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
    axd.text(.50,.06,f"Mean principal angle, block 8→9: {angle:.1f}°",ha="center",color=MUTED,fontsize=8)
    # Correlation comparison with directly reported values.
    x = [0, 1]
    axc.plot(x, single, marker="o", color=GRAY, lw=1.8, markersize=6, label="Single block")
    axc.plot(x, multi, marker="o", color=TEAL, lw=2.2, markersize=6, label="End-to-end multi-block")
    for xi, val in zip(x, single): axc.text(xi, val-.045, f"{val:.3f}", color=MUTED, fontsize=8, ha="center")
    for xi, val in zip(x, multi): axc.text(xi, val+.025, f"{val:.3f}", color=TEAL, fontsize=8, ha="center", weight="semibold")
    axc.set_xticks(x, metrics); axc.set_ylim(.6,1.02); axc.set_ylabel("Correlation with held-out damage")
    axc.set_title("Damage prediction improves with downstream context", loc="left", color=INK)
    axc.legend(frameon=False, loc="lower right"); polish_axis(axc); panel_label(axc, "b")
    fig.suptitle("Local geometry misses downstream rotation and transmission", x=0.04, y=1.02,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    note(fig, "N=100 held-out perturbations. Correlations and principal angle are read from the audited multi-block validation manifest; diagram is conceptual.")
    fig.tight_layout(rect=(0, .10, 1, .94), w_pad=2.0)
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
        for method, name, color in methods:
            pts = sorted((float(r["rem_frac"])*100, float(r["top1_acc"])*100)
                         for r in subset if r["method"] == method)
            if not pts: continue
            xs, ys = zip(*pts)
            ax.plot(xs, ys, marker="o", markersize=3.8, linewidth=1.55, color=color, label=name)
        ax.set_title(model, loc="left", color=INK)
        ax.set_xlim(10, 80); ax.set_ylim(max(0, clean-32), clean+3)
        polish_axis(ax)
    for ax in axs[-1,:]: ax.set_xlabel("Retained patch tokens (%)")
    axs[0,0].set_ylabel("Top-1 accuracy (%)"); axs[1,0].set_ylabel("Top-1 accuracy (%)")
    handles, labels = axs[0,0].get_legend_handles_labels()
    fig.legend(handles, labels, frameon=False, loc="lower center", ncol=5, bbox_to_anchor=(.5,.12))
    for ax,p in zip(axs.flat,"abcd"): panel_label(ax,p)
    # Low-rank result is shown exactly as the audited claim, not recomputed from Top-1 rows.
    fig.text(.5,.066,"Rank-16 / Rank-32 retain >98% of the full-J oracle compression benefit*",
             ha="center", color=INK, fontsize=9, weight="semibold")
    note(fig, "N=1,000 held-out images/model; all tested budgets. *Denominator: Group-Mean-to-full-J-oracle compression benefit, as audited; not an accuracy ratio or spectral energy.", y=.018)
    fig.suptitle("Operator-aware compression improves selected confirmatory frontiers", x=0.04, y=.99,
                 ha="left", fontsize=13, weight="semibold", color=INK)
    fig.tight_layout(rect=(0, .22, 1, .93), h_pad=1.8, w_pad=1.8)
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
    fig.suptitle("Measured carrier results are mixed and model-dependent",x=.04,y=.99,ha="left",fontsize=13,weight="semibold",color=INK)
    note(fig,"BS=64 rows from the real-final accuracy-throughput frontier; 1,000 held-out images/model; throughput uses 100 full-model calls per timing row. Markers show measured methods; no proxy timing.",y=.005)
    fig.tight_layout(rect=(0,.12,1,.93),h_pad=1.7,w_pad=1.8)
    save_figure(fig,out,"figureS1_real_carrier_boundary")


FIGURE_SOURCES = {
    "figure1_overview": ("Conceptual vector schematic; no empirical data.", "Intervention logic is shown without numeric encoding."),
    "figure2_depthwise": ("outputs/fungibility_v1/vitb_depth_results.csv; outputs/fungibility_v1/dinov2_depth_results.csv", "Rows condition in CLEAN/ZERO/CENTROID/DIAGONAL_GAUSSIAN; all depths; Top-1 accuracy; seed-level SD; 25% replacement documented in audited V1 report."),
    "figure3_geometry_diversity": ("outputs/fungibility_v1/vitb_geometry_results.csv; outputs/fungibility_v1/dinov2_geometry_results.csv; outputs/fungibility_v0_8/shared_vs_independent_results.csv; outputs/fungibility_v0_8/grouped_diversity_results.csv", "V1 rows fraction=0.50 and conditions CENTROID/COORDINATE_PERMUTED_CENTROID/SIGN_FLIPPED_CENTROID, all recorded seeds; V0.8 all shared/independent seeds and all K values."),
    "figure4_anisotropic_geometry": ("outputs/fungibility_functional_geometry/covariance_function_alignment.csv", "All 8 model/depth rows; heatmap displays ratio_PC1_to_PCbot. Vector panel is explanatory only."),
    "figure5_value_path_cancellation": ("outputs/fungibility_attention_causal_audit/qkv_decomposition.csv", "model/depth pairs (deit_small,8) and (vit_base,7); token patterns global_coherent/random_sign/checkerboard; feature_dir=jac_top; scale_s=1.0; pathways V_only and K_plus_V; dz_readout_l1."),
    "figure6_end_to_end_operator": ("outputs/fungibility_multiblock_operator/validation_manifest.json", "prediction_correlations single_block/multi_block Pearson and Spearman; primary_findings mean_principal_angle_deg_b8_to_b9."),
    "figure7_operator_compression": ("outputs/fungibility_operator_compression_confirmatory/budget_summary.csv; outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv; docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md", "Filtered budget_summary.csv to Attention Pruning, Group-Mean Merging, ToMe (BSM), Operator-Aware (Oracle), and Operator-Aware (Rank-32), for all budgets and four architectures. Low-rank >98% statement is reproduced from the audited benefit denominator in report §5, not recomputed from Top-1; rank conditions checked in low_rank_ablation.csv."),
    "figureS1_real_carrier_boundary": ("outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv", "batch_size=64; all four architectures and available Clean/Group Mean/q16/q32/Selective q16 rows; fields top1_accuracy and img_per_sec. Output files reside in supp/."),
}


def write_manifest(out: Path) -> None:
    titles = {
        "figure1_overview": ("Controlled patch-content intervention", "Mechanism schematic with fixed slots, surrogate controls, downstream operator, and readout."),
        "figure2_depthwise": ("Depth-wise replacement controls", "Replots accuracy directly from V1 result CSVs and exposes seed variation."),
        "figure3_geometry_diversity": ("Geometry and diversity constraints", "Combines coordinate-geometry controls with shared/independent and grouped-stream diversity evidence."),
        "figure4_anisotropic_geometry": ("Anisotropic functional geometry", "Shows audited feature-direction sensitivity ratio with a concise geometric explanation."),
        "figure5_value_path_cancellation": ("Value-path transmission and cancellation", "Compares coherent and sign-varying token patterns through V-only and K+V pathways."),
        "figure6_end_to_end_operator": ("Local versus end-to-end operator", "Connects downstream block composition to the audited damage-prediction correlations."),
        "figure7_operator_compression": ("Confirmatory operator-aware compression", "Plots the N=1,000 accuracy-token curves and states the audited low-rank benefit denominator."),
        "figureS1_real_carrier_boundary": ("Real-model carrier boundary", "Shows the measured accuracy-throughput tradeoff as a bounded supplementary result."),
    }
    lines = ["# Figure Manifest v4", "", "Generated by `scripts/build_paper_figures_v4.py`. White background, DejaVu Sans, consistent typography; SVG and 300 dpi PNG saved for every panel. No models were executed.", ""]
    for i, (stem, (purpose, design)) in enumerate(titles.items(), 1):
        filename = f"{stem}.svg / {stem}.png"
        if stem == "figureS1_real_carrier_boundary":
            filename = f"supp/{filename}"
        sources, filters = FIGURE_SOURCES[stem]
        lines += [f"## {i}. {purpose}", "", f"- **Final filename:** `{filename}`", f"- **Purpose:** {design}", f"- **Source data:** {sources}", "- **Generating script:** `scripts/build_paper_figures_v4.py`", f"- **Rows / filters:** {filters}", "- **Design notes:** restrained mechanism blue and compression teal; gray references; explicit units and sample units; vector SVG plus 300 dpi PNG.", ""]
    (out/"FIGURE_MANIFEST.md").write_text("\n".join(lines), encoding="utf-8")


def contact_sheet(out: Path) -> None:
    paths = sorted(out.glob("figure*.png")) + sorted((out/"supp").glob("figure*.png"))
    thumbs = []
    canvas_w = 900; cell_w = 430; cell_h = 300; pad = 20
    for path in paths:
        im = Image.open(path).convert("RGB")
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
    fig1(out); fig2(root,out); fig3(root,out); fig4(root,out); fig5(root,out); fig6(root,out); fig7(root,out)
    fig_s1(root,out/"supp")
    write_manifest(out); contact_sheet(out)
    print(f"Rendered 7 main figures + 1 supplement; contact sheet: {out/'contact_sheet.png'}")


if __name__ == "__main__":
    main()
