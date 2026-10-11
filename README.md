# Patch-Content Fungibility: Geometry, Functional Transmission, and Operator-Aware Token Compression

This repository contains the current journal-submission draft and the complete research record for Patch-Content Fungibility (PCF). The paper tests whether ordinary late-layer spatial patch activations in vision transformers can be replaced with class-agnostic calibration surrogates while the patch slots, sequence length, model weights, and downstream computation remain fixed. The evidence identifies constraints from feature geometry and token diversity; the compression study is a bounded oracle-level application and does not establish a general deployment advantage.

## Current journal manuscript

**Current title:** *Patch-Content Fungibility: Geometry, Functional Transmission, and Operator-Aware Token Compression*.

- [Manuscript source (Markdown)](docs/PAPER_DRAFT.md)
- [Editable manuscript (Word)](docs/PAPER_DRAFT_v5.docx)
- [Supplementary source (Markdown)](docs/PAPER_SUPPLEMENTARY_DRAFT.md)
- [Supplementary material (Word)](docs/PAPER_SUPPLEMENTARY.docx)

The experiments cover four pretrained architectures: DeiT-Tiny, DeiT-Small, supervised ViT-B/16 AugReg, and DINOv2 ViT-S/14.

## Publication figures and numerical evidence

The current manuscript references main Figure 1–8 SVGs under `figures/paper_final_v4/`; the editable manuscript embeds the corresponding PNGs. The Supplementary Markdown references Figures S1–S9 under `figures/paper_final/supp/` and Figures S10–S15 under `figures/paper_final_v4/supp/`.

- [Main-figure manifest, data sources, filters, and generator](figures/paper_final_v4/FIGURE_MANIFEST.md)
- [Supplementary Figures S1–S9](figures/paper_final/supp/)
- [Supplementary Figures S10–S15](figures/paper_final_v4/supp/)
- [Final claims table](docs/PAPER_FINAL_CLAIMS_TABLE.md)
- [Evidence table](docs/PAPER_EVIDENCE_TABLE.md)
- [Number traceability](docs/PAPER_NUMBER_TRACEABILITY.md)
- [Sample-size map](docs/PAPER_SAMPLE_SIZE_MAP.md)
- [Confirmatory compression report](docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md)
- [Corrected regularization-sensitivity report](docs/REGULARIZATION_SENSITIVITY_REPORT_CORRECTED.md)

`figures/paper_final/main/` is a separate generated figure set; it is not a substitute for the assets named by the current manuscript. See the [repository structure](docs/REPOSITORY_STRUCTURE.md) for the distinctions among current, historical, and alternate figure files.

## Reproduce and inspect

Start with the [reproducibility guide](docs/REPRODUCIBILITY_GUIDE.md). It maps each manuscript figure and table to its archived results and generating or validating code. The archived CSVs, manifests, and reports support data-level review without rerunning the model experiments. Full experiment reruns require ImageNet validation data and pretrained checkpoints; there is no single command that reproduces the entire paper.

The two checked publication validators are:

    python scripts/validate_paper_final.py
    python scripts/validate_real_final_benchmark.py

## Data and code availability

Experiment implementations are in `patch_fungibility/` and entry-point scripts are in `scripts/`. Machine-readable outcomes, per-image evidence, calibration/evaluation manifests, and validation records are preserved in `outputs/`. ImageNet-1k validation images and pretrained model weights are not redistributed here. The dataset loader expects ImageNet validation Parquet shards in the local Hugging Face cache; model loaders use the named `timm` checkpoints or the official DINOv2 Torch Hub model. See the reproducibility guide for prerequisites and experiment-specific cohort manifests.

## Archived preprint and citation

The public Zenodo record remains the timestamped **preprint**, with its original title and DOI:

*Nhat Minh Nghiem. “Patch Content Fungibility in Vision Transformers: Geometric and Diversity Constraints in Late-Layer Representations.” Zenodo, 2026.* [https://doi.org/10.5281/zenodo.23050375](https://doi.org/10.5281/zenodo.23050375)

This historical preprint record is distinct from the current journal-submission draft above. Use [CITATION.cff](CITATION.cff) for machine-readable citation metadata. Source code is licensed under [Apache-2.0](LICENSE); the public preprint is separately licensed under [CC BY-NC-ND 4.0](paper/LICENSE.md), subject to the version-specific Zenodo metadata.

## Repository map

See [REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md) for a concise map and [REPO_CLEANUP_INVENTORY.md](docs/REPO_CLEANUP_INVENTORY.md) for the complete tracked-file inventory and preservation decisions.