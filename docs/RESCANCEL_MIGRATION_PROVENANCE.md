# Migration Provenance: Consolidating Patch Content Fungibility Research

**Date:** 2026-10-06  
**Source Repository:** [`https://github.com/nhatminh-115/ResCancel`](https://github.com/nhatminh-115/ResCancel)  
**Source Commit Head:** `6bc6b6ea9f6b0e95b8f202c13b2bb7ccfef66179`  
**Canonical Target Repository:** [`https://github.com/nhatminh-115/Patch-Content-Fungibility`](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Target Pre-Migration Head:** `4eb557b20654f80028ea08e2a4b00dcf71bc8a67`  

---

## 1. Context and Motivation

The research project *Patch Content Fungibility in Vision Transformers* was originally developed within the legacy `ResCancel` repository. When the repository was split to establish `Patch-Content-Fungibility` as the independent, canonical home of the project, subsequent research accidentally continued on the `main` branch of the legacy `ResCancel` repository.

This migration consolidates all research work conducted post-split back into the canonical `Patch-Content-Fungibility` repository, establishing it as the single, authoritative project repository.

Future research, pull requests, issues, and releases must be committed directly to `Patch-Content-Fungibility`. The legacy `ResCancel` repository remains preserved solely as historical provenance and will receive no further research updates.

---

## 2. Migrated Research Sequence

The following sequential research phases and commits from `ResCancel` have been fully integrated:

1. `4b0cb70` & `d6cb946`: Image-conditioned residual carrier protocol and experiments
2. `6f2250a` & `e2a1210`: Predictive principle protocol and empirical validation
3. `6fdfd1b` & `e416830`: Functional geometry protocol and experiments
4. `fb9fdcd` & `4813d66`: Joint stream geometry protocol and cross-layer experiments
5. `933e8eb`: Attention causal audit across transformer blocks
6. `8a92b32`: Predictive token operator formulation
7. `992eb70`: Full token × feature operator implementation and benchmarks
8. `139e8fe`: Multi-block downstream Jacobian spectrum analysis
9. `5840490`: Joint Value-Key geometry and subspace overlap
10. `7493c28`: Operator-aware token compression framework
11. `77e694a` & `d428515`: Confirmatory token compression protocol and benchmark
12. `11b8a96`, `24367e4` & `0f14635`: Amortized operator predictor, benchmark, and strict audit
13. `2f7b780`: Practical operator compression lower bounds and GPU carrier solvers
14. `6bc6b6e`: Batched operator compression, FlashAttention Route B multiplicity audit, and Hybrid IP-SM grouping

---

## 3. Preserved Canonical Elements

To respect the canonical status of `Patch-Content-Fungibility`, all target-specific cleanup commits were strictly preserved:
- `docs/PAPER_DRAFT.md`: Preserved exactly as canonical (SHA256: `99a3d19da546e740c44aa6a417cf31647e2b9ad8cda81c81f7d7f92461eef672`).
- Self-contained ImageNet dataset loader (`patch_fungibility/dataset.py`).
- Removal of legacy imports from `scripts/run_fungibility_v0.py` and `scripts/run_fungibility_v0_5.py`.
- Polished paper-facing documentation links, related work positioning, and citation metadata (`CITATION.cff`, `README.md`).

---

## 4. Verification and Audit

All migrated modules have been verified via:
- Programmatic Python compilation (`py_compile`) across all migrated modules and scripts.
- Smoke import tests verifying that `patch_fungibility` has zero legacy dependencies.
- Zero active imports or runtime dependencies on `ResCancel`.
- Complete migration inventory documented in [`docs/RESCANCEL_MIGRATION_INVENTORY.md`](file:///d:/Study/Patch-Content-Fungibility/docs/RESCANCEL_MIGRATION_INVENTORY.md).
