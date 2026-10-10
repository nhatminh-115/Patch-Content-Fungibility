# Reproducibility Guide

This guide maps the current manuscript to the archived evidence and the code paths that validate or regenerate it. The repository preserves existing experimental results; this guide does not claim that every historical study has a one-command rerun.

## 1. Software setup

There is no checked-in `requirements.txt`, `pyproject.toml`, Conda environment, or pinned dependency lock. The research code imports Python's standard library plus PyTorch, torchvision, timm, NumPy, pandas, SciPy, Matplotlib, Seaborn, Pillow, scikit-learn, and a Parquet engine such as PyArrow. Exact software and device details for measured runs are retained in experiment manifests and timing CSVs.

Create an environment, install a PyTorch/torchvision pair compatible with the chosen CPU or CUDA platform, then install the analysis/model packages:

    python -m venv .venv
    python -m pip install --upgrade pip
    python -m pip install numpy pandas scipy matplotlib seaborn pillow pyarrow scikit-learn timm

Install PyTorch and torchvision using the PyTorch distribution that matches the target hardware; do not assume a CPU wheel is suitable for GPU experiments. The commands above are environment setup guidance, not a pinned reconstruction of the historical environment. The repository does not record a single tested cross-platform dependency lock.

## 2. Dataset, checkpoints, and hardware

- The image source is the ImageNet-1k validation set. It is not stored in this repository. `patch_fungibility/v0_6_dataset.py` reads `val-*.parquet` shards below `~/.cache/huggingface/hub/`; it raises an error if no cached shards are available.
- DeiT-Tiny and DeiT-Small use `timm` identifiers `deit_tiny_patch16_224` and `deit_small_patch16_224`; ViT-B/16 AugReg uses `vit_base_patch16_224.augreg_in1k`.
- DINOv2 uses the official Torch Hub model `facebookresearch/dinov2: dinov2_vits14_lc` with `layers=1`. First-time model loading requires access to the corresponding checkpoint source or a populated local cache.
- CSV/manifest validation and review of archived outputs do not require ImageNet or a GPU. Full model evaluations, Jacobian-based compression, and timing runs require the data and model checkpoints and are computationally expensive; use a CUDA GPU for practical runtimes. The archived real-final throughput run reports an NVIDIA GeForce RTX 5070 Laptop GPU. That is the measured setup, not a minimum-hardware guarantee.
- The paper combines protocol-specific experiments. Do not transfer a split or seed from one family to another.

## 3. Existing validated entry points

Run from the repository root:

    python scripts/validate_paper_final.py
    python scripts/validate_real_final_benchmark.py

These inspect the paper structure, citations, referenced figures, numerical claims, and archived benchmark outputs; they do not rerun model inference. They write validation JSON files in `outputs/fungibility_real_final/`, so inspect those generated-file changes before staging. At this cleanup baseline the archived real-final manifest reports PASS, 12/12 checks; the paper validator is recorded separately in the cleanup report after it is rerun.

The figure builders are separate from experiment runners. `python scripts/build_paper_figures_v4.py` rebuilds the v4 manuscript assets from archived data and the source image; `python scripts/plot_regularization_sensitivity_manuscript.py` rebuilds S15 from the corrected sensitivity CSV. `python scripts/render_paper_figures_final.py` rebuilds the separate `figures/paper_final/main/` and S1–S9 PNG/PDF set. These scripts write tracked figure files. They were not run during cleanup so canonical figure outputs would not be overwritten. Use a clean copy if intentionally regenerating them.

Experiment scripts listed below are entry-point files, not a universal command line. Their arguments/defaults and protocol-specific settings are defined in each script and paired protocol. There is no single command that reruns the full paper.

## 4. Split and cohort manifests

- Main replacement studies: protocol-specific manifests and calibration/evaluation CSVs live in their experiment folders under `outputs/fungibility_v0_6/`, `outputs/fungibility_v0_7/`, `outputs/fungibility_v0_8/`, `outputs/fungibility_v0_9/`, and `outputs/fungibility_v1/`. `docs/PAPER_SAMPLE_SIZE_MAP.md` records the unit and sample size for each evidence family.
- Strict confirmatory operator compression: the frozen calibration/evaluation design and validation state are in `outputs/fungibility_operator_compression_confirmatory/validation_manifest.json`; the per-image outcomes and paired summaries are in that directory. The reported design uses calibration split seed 9101 and evaluation split seed 9201.
- Practical carrier evaluation: `outputs/fungibility_real_final/sample_manifest.csv` and `measurement_manifest.json` record the 7101 calibration and 9201 evaluation cohorts; `validation_manifest.json` records the audited state.
- Corrected regularization sensitivity: `outputs/fungibility_regularization_sensitivity_v2_class_randomized/manifest_full.json` and `selected_cohort.csv` record the class-randomized 200-image calibration cohort (selection seed 61327, from canonical calibration seed 9101). The original first-200-classes study is preserved separately under `outputs/fungibility_regularization_sensitivity/` and is historical exploratory evidence.
- Mechanistic analyses have their own N=100 image or perturbation cohorts and manifests. See the relevant protocol and output folder; those cohorts are not interchangeable with the confirmatory N=1,000 evaluation cohort.

## 5. Main manuscript figures

For exact row filters and design notes, use the linked sections of [FIGURE_MANIFEST.md](../figures/paper_final_v4/FIGURE_MANIFEST.md). The manuscript's Markdown calls out `figures/paper_final_v4/*.svg`; the current DOCX embeds the corresponding v4 PNGs.

| Figure | Archived source results | Figure script |
|---|---|---|
| 1 | `figures/paper_final_v4/source/figure1_overview_user.png` (user-supplied conceptual image; no empirical values) | `scripts/build_paper_figures_v4.py` |
| 2 | `outputs/fungibility_v0_6/` depth summaries and seed rows; `outputs/fungibility_v1/` depth results; `outputs/fungibility_v1_depth6_followup/` depth-6 rows. Exact eight input CSVs and filters are in manifest section 2. | `scripts/build_paper_figures_v4.py` |
| 3 | `outputs/fungibility_v0_7/`, `outputs/fungibility_v0_8/`, `outputs/fungibility_v0_9/`, `outputs/fungibility_v1/`, and `outputs/fungibility_v1_grouped_diversity_extension/`. Exact input files and seed/filter rules are in manifest section 3. | `scripts/build_paper_figures_v4.py` |
| 4 | `outputs/fungibility_section5_cross_arch_extension/functional_geometry/pc_directional_sensitivity.csv` and `functional_spectrum_robustness.csv` | `scripts/build_paper_figures_v4.py` |
| 5 | `outputs/fungibility_attention_causal_audit/causal_conditions.csv`, `replication_summary.csv`, and the validation manifest | `scripts/build_paper_figures_v4.py` |
| 6 | `outputs/fungibility_joint_stream_geometry/directional_curves.csv` and its validation manifest | `scripts/build_paper_figures_v4.py` |
| 7 | `outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/model_specific_correlations.csv` and `outputs/fungibility_multiblock_operator/replication_summary.csv` | `scripts/build_paper_figures_v4.py` |
| 8 | `outputs/fungibility_operator_compression_confirmatory/budget_summary.csv`, `low_rank_ablation.csv`, and the confirmatory report | `scripts/build_paper_figures_v4.py` |

## 6. Main manuscript tables

Tables are maintained in the manuscript source rather than produced by a single table-generation command. Source paths and quantitative traceability are recorded in [PAPER_NUMBER_TRACEABILITY.md](PAPER_NUMBER_TRACEABILITY.md), [PAPER_FINAL_CLAIMS_TABLE.md](PAPER_FINAL_CLAIMS_TABLE.md), and the listed validation scripts.

| Table | Source evidence | Check / derivation |
|---|---|---|
| I | `docs/PAPER_SAMPLE_SIZE_MAP.md`, each cited protocol, and the run-specific manifests under `outputs/` | `scripts/validate_paper_final.py` checks table structure and sample-unit scope. |
| II | V0.7 geometry outputs; V0.8 grouped-diversity outputs; V0.9 PC1/random outputs; V1 geometry and grouped-diversity outputs. Exact contrasts and cohort/seed definitions are in traceability row for Table II. | `scripts/validate_paper_final.py` recomputes the reported percentage-point contrasts from archived CSVs. |
| III | `outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv` and `pc_directional_sensitivity.csv` | `scripts/validate_paper_final.py` recomputes the spectrum and directional summaries. |
| IV | `outputs/fungibility_operator_compression_confirmatory/budget_summary.csv`, `per_image_results.csv`, and `low_rank_ablation.csv` | `scripts/validate_paper_final.py` checks values; `scripts/validate_real_final_benchmark.py` checks benchmark provenance and archived outputs. |

## 7. Supplementary figures and tables

S1–S9 are generated by `scripts/render_paper_figures_final.py` from the following archived CSVs. The source manuscript links the PNGs under `figures/paper_final/supp/`.

| Figure | Source results |
|---|---|
| S1 | `outputs/fungibility_dense_fraction/summary_by_mask_seed.csv`, `summary_across_masks.csv` |
| S2 | `outputs/fungibility_dense_fraction/threshold_crossings.csv` |
| S3 | `outputs/fungibility_v0_9/natural_vs_energy_matched_rank.csv` |
| S4 | `outputs/fungibility_v0_9/pc1_scale_sweep.csv` |
| S5 | `outputs/fungibility_v0_9/rank_propagation.csv` |
| S6 | `outputs/fungibility_compression_poc/equivalence_results.csv` |
| S7 | `outputs/fungibility_compression_poc/baseline_comparison.csv` |
| S8 | `outputs/fungibility_compression_poc/latency_summary.csv`, `baseline_comparison.csv` |
| S9 | `outputs/fungibility_geometry_bank/delta_vs_pruning.csv` |

S10–S14 are generated by `scripts/build_paper_figures_v4.py`; their complete sources and filters are in manifest sections 10–14. Key output files are: S10 `outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv`; S11 `outputs/fungibility_attention_causal_audit/replication_summary.csv`; S12 `outputs/fungibility_attention_causal_audit/qkv_decomposition.csv`; S13 `outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv`; S14 `outputs/fungibility_joint_stream_geometry/directional_curves.csv`.

S15 is generated by `scripts/plot_regularization_sensitivity_manuscript.py` from `outputs/fungibility_regularization_sensitivity_v2_class_randomized/aggregated_by_architecture_budget_factor.csv`. Paired comparisons and cohort provenance are in that output folder; the corrected report is `docs/REGULARIZATION_SENSITIVITY_REPORT_CORRECTED.md`.

| Supplementary table | Source evidence |
|---|---|
| S1 | Seed and cohort details in `docs/PAPER_SAMPLE_SIZE_MAP.md` and study manifests. |
| S2 | `outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv`, `pc_directional_sensitivity.csv`, `raw_eigenspectrum.csv`. |
| S3 | `outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/model_specific_correlations.csv`, `stratified_bootstrap_correlations.csv`, and companion validation manifest. |
| S4 | `outputs/fungibility_attention_causal_audit/causal_conditions.csv`, `qkv_decomposition.csv`, `replication_summary.csv`. |
| S5 | `outputs/fungibility_real_final/real_accuracy_summary.csv`, `real_accuracy_per_image.csv`, `real_accuracy_throughput_frontier.csv`. |
| S6 | `outputs/fungibility_regularization_sensitivity_v2_class_randomized/aggregated_by_architecture_budget_factor.csv`; calibration cohort and paired comparisons are in `selected_cohort.csv` and `paired_factor10_vs_3_30.csv`. |

## 8. Direct checks versus expensive reruns

Archived aggregate and per-image CSVs allow reviewers to check image-level counts, paired contrasts, and figure/table inputs without downloading ImageNet or loading a model. Both publication validators operate on repository files rather than running experiment models. Full claim regeneration is more demanding: it requires the protocol's image cohort, matching pretrained model, and experiment runner, and can involve large batched inference or downstream Jacobians. Read the paired protocol before invoking a runner; do not infer that the two validators reproduce the experiments.

The repository preserves failed and superseded approaches as research history. The final paper's source paths are defined by `PAPER_DRAFT.md`, `PAPER_SUPPLEMENTARY_DRAFT.md`, and the v4 figure manifest, not by similar filenames in alternate figure directories.

## 9. Citation and licenses

For the archived preprint, cite the historical Zenodo record and DOI in `CITATION.cff`: *Patch Content Fungibility in Vision Transformers: Geometric and Diversity Constraints in Late-Layer Representations*, DOI `10.5281/zenodo.23050375`. The current under-review journal title is different and is shown in the root README. Code uses Apache-2.0 (`LICENSE`); the preprint is separately licensed CC BY-NC-ND 4.0 (`paper/LICENSE.md`).