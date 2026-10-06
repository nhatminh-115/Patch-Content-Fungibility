# Patch Content Fungibility in Vision Transformers

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23050375.svg)](https://doi.org/10.5281/zenodo.23050375)

**Canonical Repository:** https://github.com/nhatminh-115/Patch-Content-Fungibility

This repository contains the code, experiment records, analysis artifacts, and paper-development material for:

**Patch Content Fungibility in Vision Transformers: Geometric and Diversity Constraints in Late-Layer Representations**

The central finding is that late Vision Transformer patch representations can become **content-fungible**: after substantial upstream computation, many ordinary spatial patch activations can be replaced by coarse calibration-derived surrogates while downstream classification remains substantially more intact than under destructive zero replacement. This tolerance is structured rather than arbitrary. Valid substitutes must respect learned feature geometry, and complete patch-stream replacement additionally depends on token-to-token diversity.

## Preprint

Canonical public record:

**Nhat Minh Nghiem. _Patch Content Fungibility in Vision Transformers: Geometric and Diversity Constraints in Late-Layer Representations_. Zenodo, 2026.**

DOI: **[10.5281/zenodo.23050375](https://doi.org/10.5281/zenodo.23050375)**

The Zenodo record is the canonical timestamped preprint. The manuscript distributed there is licensed separately from the source code in this repository.

## Repository layout

- `patch_fungibility/` — intervention, model, validation, geometry, diversity, low-rank, dense-sweep, and compression experiment code.
- `scripts/` — experiment entry points and plotting/rendering scripts.
- `docs/` — protocols, reports, evidence tables, paper audits, and manuscript-development notes.
- `outputs/` — machine-readable experiment outputs and manifests.
- `figures/` — experimental figures and paper figure assets.
- `arxiv/` — arXiv export tooling and metadata.
- `paper/` — licensing/citation notes for the manuscript.

## Main empirical stages

The research record includes the initial fungibility screen, held-out calibration experiments, geometry controls, diversity interventions, low-dimensional direction tests, cross-architecture validation, dense replacement-fraction sweeps, and negative compression controls. The paper-level claims should be read together with `docs/PAPER_EVIDENCE_TABLE.md` and `docs/PAPER_CLAIMS_AUDIT.md`.

## Models

Experiments cover pretrained DeiT-Tiny, DeiT-Small, supervised ViT-B/16 AugReg, and self-supervised DINOv2 ViT-S/14 variants. Exact checkpoints, depths, masks, seeds, calibration/evaluation splits, and intervention definitions are recorded in the experiment manifests and protocol documents.

## Reproducibility

Start from the protocol associated with the experiment you want to reproduce, then use the matching `scripts/run_fungibility_*.py` entry point. The repository intentionally retains intermediate reports and validation manifests so that the chain from exploratory experiment to paper claim remains auditable.

## Licenses

Source code is released under the **Apache License 2.0**; see `LICENSE`.

The preprint/manuscript is a separate scholarly work. Its public Zenodo version is distributed under **CC BY-NC-ND 4.0**; see `paper/LICENSE.md` and the Zenodo record for the authoritative metadata.

## Citation

If you use this work, please cite the Zenodo preprint using DOI **10.5281/zenodo.23050375**. A machine-readable citation is provided in `CITATION.cff`.
