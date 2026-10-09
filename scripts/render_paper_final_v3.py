"""Render the publication-locked figure set from audited manuscript sources.

Usage: python scripts/render_paper_final_v3.py [--root REPOSITORY]
Only reads audited reports, manifests, and CSVs named in the traceability map.
It does not run models or create new empirical results.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch


PALETTE = {"blue": "#2D6A9F", "cyan": "#63A6C8", "orange": "#E28E2C",
           "red": "#C65353", "green": "#4B8B63", "gray": "#68737D",
           "light": "#EAF0F4", "dark": "#23313D", "purple": "#8771A7"}


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def save(fig, path: Path) -> None:
    fig.savefig(path, format="svg", bbox_inches="tight")
    plt.close(fig)


def style(ax, title: str, ylabel: str | None = None) -> None:
    ax.set_title(title, loc="left", fontsize=13, weight="bold", color=PALETTE["dark"])
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", alpha=.2)
    ax.set_axisbelow(True)


def figure1(out: Path) -> None:
    fig, ax = plt.subplots(figsize=(11.5, 3.1))
    ax.set_xlim(0, 11.5); ax.set_ylim(0, 3.1); ax.axis("off")
    boxes = [(0.25, 1.15, 1.55, 1.0, "Image + ViT", "prefix forward"),
             (2.2, 1.15, 1.7, 1.0, "Patch stream", "CLS and slots fixed"),
             (4.35, 1.15, 1.8, 1.0, "Intervene", "content replaced"),
             (6.65, 1.15, 1.85, 1.0, "Downstream J", "functional geometry"),
             (8.95, 1.15, 2.0, 1.0, "Readout / result", "damage or compression")]
    for x,y,w,h,title,sub in boxes:
        box = FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.04,rounding_size=.12",
                             fc=PALETTE["light"],ec=PALETTE["blue"],lw=1.5)
        ax.add_patch(box); ax.text(x+w/2,y+.62,title,ha="center",va="center",fontsize=11,weight="bold")
        ax.text(x+w/2,y+.31,sub,ha="center",va="center",fontsize=8.5,color=PALETTE["gray"])
    for a,b in [(1.8,2.2),(3.9,4.35),(6.15,6.65),(8.5,8.95)]:
        ax.add_patch(FancyArrowPatch((a,1.65),(b,1.65),arrowstyle="-|>",mutation_scale=13,color=PALETTE["gray"]))
    ax.text(5.25,2.55,"Geometry + diversity constrain replacement",ha="center",fontsize=10,color=PALETTE["orange"],weight="bold")
    ax.text(7.55,.55,"mechanistic audits: N=100 images / N=100 perturbations",ha="center",fontsize=8.5,color=PALETTE["gray"])
    ax.text(9.95,.55,"confirmatory compression: N=1,000 images/model",ha="center",fontsize=8.5,color=PALETTE["gray"])
    save(fig,out)


def figure2(out: Path) -> None:
    # Transcribed from FUNGIBILITY_V1_REPORT.md §3.2, 25% replacement depth sweep.
    depths=[5,7,8,9,10]
    curves={"ViT-B/16 AugReg":{"Clean":[76.1]*5,"Zero":[73.8,70.4,75.7,73.2,73.6],"Centroid":[74.7,74.5,74.5,74.9,75.4],"Gaussian":[75.4,74.2,74.5,74.1,74.1]},
            "DINOv2 ViT-S/14":{"Clean":[78.8]*5,"Zero":[60.2,66.3,39.4,4.5,1.9],"Centroid":[73.2,73.9,74.6,74.1,76.8],"Gaussian":[75.2,75.8,75.1,75.0,75.1]}}
    fig,axs=plt.subplots(1,2,figsize=(10.8,4.3),sharey=True)
    colors={"Clean":PALETTE["gray"],"Zero":PALETTE["red"],"Centroid":PALETTE["blue"],"Gaussian":PALETTE["green"]}
    for ax,(model,methods) in zip(axs,curves.items()):
        for method,vals in methods.items():
            ax.plot(depths,vals,marker="o",lw=2 if method!="Clean" else 1.5,ls="--" if method=="Clean" else "-",label=method,color=colors[method])
        ax.set_xticks(depths); ax.set_ylim(0,100); ax.set_xlabel("Intervention depth")
        style(ax,model,"Top-1 accuracy (%)")
    axs[0].legend(frameon=False,ncols=2,fontsize=8)
    fig.text(.02,.01,"N=1,000 evaluation images per architecture; 25% spatial-patch replacement. Source: FUNGIBILITY_V1_REPORT.md §3.2.",fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def figure3(root: Path, out: Path) -> None:
    base = root/"outputs/fungibility_v0_8"
    shared = rows(base/"shared_vs_independent_results.csv")
    grouped = rows(base/"grouped_diversity_results.csv")
    fig, axs = plt.subplots(1,2,figsize=(11,4.3))
    models = sorted({r["model"] for r in shared})
    labels = {"deit_tiny_patch16_224":"DeiT-Tiny","deit_small_patch16_224":"DeiT-Small"}
    types = sorted({r["condition_type"] for r in shared})
    x = list(range(len(models))); width=.34
    for ti,typ in enumerate(types[:2]):
        vals=[]
        for model in models:
            v=[float(r["accuracy"])*100 for r in shared if r["model"]==model and r["condition_type"]==typ]
            vals.append(sum(v)/len(v) if v else float("nan"))
        axs[0].bar([i+(ti-.5)*width for i in x],vals,width,label=typ.replace("_"," "),color=[PALETTE["orange"],PALETTE["blue"]][ti])
    axs[0].set_xticks(x,[labels.get(m,m) for m in models]); axs[0].set_ylabel("Top-1 accuracy (%)")
    style(axs[0],"Complete replacement: shared vs independent variation")
    axs[0].legend(frameon=False,fontsize=8)
    for model in models:
        ks=sorted({int(r["k"]) for r in grouped if r["model"]==model})
        means=[]
        for k in ks:
            vals=[100*float(r["accuracy"]) for r in grouped if r["model"]==model and int(r["k"])==k]
            means.append(sum(vals)/len(vals))
        axs[1].plot(ks,means,marker="o",label=labels.get(model,model),lw=2)
    axs[1].set_xscale("log",base=2); axs[1].set_xlabel("Number of distinct carrier groups (K)"); axs[1].set_ylabel("Top-1 accuracy (%)")
    style(axs[1],"Low-dimensional diversity is not sufficient")
    axs[1].legend(frameon=False,fontsize=8)
    fig.text(.02,-.01,"V0.8 complete-stream intervention; N=1,000 evaluation images and 1,000 calibration images per model. High-dimensional structure required.",fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def figure4(root: Path, out: Path) -> None:
    m=read_json(root/"outputs/fungibility_functional_geometry/validation_manifest.json")
    summary=m["anisotropy_summary"]
    fig,ax=plt.subplots(figsize=(8.8,4.4))
    for model,label,color in [("deit_small","DeiT-Small",PALETTE["blue"]),("vit_base","ViT-Base",PALETTE["orange"])]:
        data=sorted((int(k.rsplit("_",1)[1]),v) for k,v in summary.items() if k.startswith(model+"_depth_"))
        ax.plot([x for x,_ in data],[y for _,y in data],marker="o",lw=2,label=label,color=color)
    ax.set_xlabel("Intervention depth"); ax.set_ylabel("Audited anisotropy summary")
    style(ax,"Functional geometry varies with model and depth")
    ax.legend(frameon=False)
    ax.text(.01,-.2,"Pilot: N=100 images. Values summarize the named manifest field; exploratory geometry evidence.",transform=ax.transAxes,fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def figure5(root: Path, out: Path) -> None:
    att=read_json(root/"outputs/fungibility_attention_causal_audit/validation_manifest.json")
    mb=read_json(root/"outputs/fungibility_multiblock_operator/validation_manifest.json")
    qkv=rows(root/"outputs/fungibility_attention_causal_audit/qkv_decomposition.csv")
    labels=["DeiT-S depth 8", "ViT-B depth 7"]
    model_depth=[("deit_small",8),("vit_base",7)]
    vals=[]
    for model,depth in model_depth:
        select=lambda pathway: next(float(r["dz_readout_l1"]) for r in qkv if r["model_key"]==model and int(r["depth"])==depth and r["token_pattern"]=="global_coherent" and r["feature_dir"]=="jac_top" and float(r["scale_s"])==1.0 and r["pathway"]==pathway)
        vals.append(100*select("V_only")/select("K_plus_V"))
    corr=mb["prediction_correlations"]
    fig,axs=plt.subplots(1,2,figsize=(10.5,4.2))
    axs[0].bar(labels,vals,color=[PALETTE["blue"],PALETTE["orange"]]); axs[0].axhline(100,color=PALETTE["gray"],ls="--",lw=1)
    axs[0].set_ylim(0,110); axs[0].set_ylabel("V-only / K+V immediate readout L1 (%)"); style(axs[0],"Value path reproduces the immediate readout disturbance")
    gap=att["attribution_summary"]
    axs[0].text(.03,.90,f"N=100 images; V gap shares: {100*gap['deit_small_depth_8']['v_path_attribution_ratio']:.1f}% / {100*gap['vit_base_depth_7']['v_path_attribution_ratio']:.1f}%.\nQ is zero for the unperturbed CLS query; K rerouting is secondary.",transform=axs[0].transAxes,fontsize=7.5,color=PALETTE["gray"],va="top")
    names=["Single block", "Multi block"]
    p=[corr["single_block_pearson_r"],corr["multi_block_pearson_r"]]
    s=[corr["single_block_spearman_rho"],corr["multi_block_spearman_rho"]]
    x=[0,1]; w=.34
    axs[1].bar([i-w/2 for i in x],p,w,label="Pearson r",color=PALETTE["cyan"])
    axs[1].bar([i+w/2 for i in x],s,w,label="Spearman ρ",color=PALETTE["purple"])
    axs[1].set_xticks(x,names); axs[1].set_ylim(0,1.05); axs[1].set_ylabel("Correlation with held-out damage")
    style(axs[1],"End-to-end operator better predicts damage"); axs[1].legend(frameon=False,fontsize=8)
    axs[1].text(.02,-.22,"N=100 held-out perturbations; mean block-8→9 principal angle = 48.99°",transform=axs[1].transAxes,fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def figure6(root: Path, out: Path) -> None:
    data=rows(root/"outputs/fungibility_operator_compression_confirmatory/architecture_summary.csv")
    models=sorted({r["model"] for r in data})
    methods=["Attention Pruning","Group-Mean Merging","ToMe (BSM)","Operator-Aware (Oracle)","Operator-Aware (Rank-32)"]
    colors=[PALETTE["red"],PALETTE["green"],PALETTE["orange"],PALETTE["blue"],PALETTE["purple"]]
    fig,axs=plt.subplots(2,2,figsize=(11,7),sharey=True)
    for ax,model in zip(axs.flat,models):
        subset=[r for r in data if r["model"]==model]
        for r in subset:
            if r["method"] not in methods: continue
        vals=[]
        for method in methods:
            rr=[r for r in subset if r["method"]==method]
            if rr: vals.append((method,float(rr[0]["auc_frontier"])))
        vals.sort(key=lambda z:methods.index(z[0]))
        ax.bar([v[0] for v in vals],[v[1] for v in vals],color=[colors[methods.index(v[0])] for v in vals])
        ax.tick_params(axis="x",rotation=38,labelsize=7); style(ax,model,"Accuracy-token frontier AUC")
    fig.suptitle("Strict confirmatory operator-aware compression",fontsize=15,weight="bold",x=.06,ha="left")
    fig.text(.02,.01,"N=1,000 held-out images per architecture; AUC over the shared tested retained-token domain. See paired results for inferential comparisons.",fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def figure7(root: Path, out: Path) -> None:
    raise RuntimeError(
        "The former >98% low-rank recovery chart was withdrawn on 2026-10-08 "
        "after matched Top-1 recovery recomputation. Use the current "
        "figures/paper_final_v4/figure7_operator_compression.svg, which shows "
        "measured accuracy-token curves and encodes no recovery percentage."
    )


def figure_s1(root: Path, out: Path) -> None:
    data=rows(root/"outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv")
    subset=[r for r in data if int(r["batch_size"])==64]
    models=sorted({r["architecture"] for r in subset})
    fig,axs=plt.subplots(2,2,figsize=(10.5,7.5))
    colors={"Clean":PALETTE["gray"],"Hybrid Group Mean":PALETTE["green"],"Static Feature-PCA q=16":PALETTE["blue"],"Static Feature-PCA q=32":PALETTE["orange"],"Selective Feature-PCA q16 target30":PALETTE["purple"]}
    for ax,model in zip(axs.flat,models):
        rs=[r for r in subset if r["architecture"]==model]
        for r in rs:
            method=r["method"]
            ax.scatter(float(r["img_per_sec"]),float(r["top1_accuracy"]),s=46,color=colors.get(method,PALETTE["red"]),marker="o" if r["pareto_optimal"].lower()=="true" else "x")
            ax.annotate(method.replace("Static Feature-PCA ","q"), (float(r["img_per_sec"]),float(r["top1_accuracy"])),fontsize=6,xytext=(3,3),textcoords="offset points")
        style(ax,model,"Top-1 (%)"); ax.set_xlabel("Measured full-model throughput (images/s)")
    fig.suptitle("Real carrier benchmark: a narrow measured frontier",fontsize=14,weight="bold",x=.06,ha="left")
    fig.text(.02,.01,"BS=64. Accuracy N=1,000 images/model; throughput from 100 measured full-model calls per timing row. Circles mark the CSV frontier.",fontsize=8,color=PALETTE["gray"])
    save(fig,out)


def main() -> None:
    ap=argparse.ArgumentParser(); ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]); root=ap.parse_args().root.resolve()
    out=root/"figures/paper_final_v3"; supp=out/"supp"; supp.mkdir(parents=True,exist_ok=True)
    figure1(out/"figure1_conceptual.svg")
    figure2(out/"figure2_depthwise.svg")
    figure3(root,out/"figure3_geometry_diversity.svg")
    figure4(root,out/"figure4_anisotropy.svg")
    figure5(root,out/"figure5_value_end_to_end.svg")
    figure6(root,out/"figure6_confirmatory_frontier.svg")
    figure7(root,out/"figure7_low_rank.svg")
    figure_s1(root,supp/"figureS13_real_carrier_boundary.svg")
    print(f"Rendered 7 main figures and one supplement to {out}")


if __name__=="__main__":
    main()
