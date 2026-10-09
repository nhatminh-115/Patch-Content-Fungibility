# Paper Submission Readiness

**Status: Figure 5 consistency correction complete; both Word deliverables validated and visually inspected (2026-10-09).**

This focused correction used audited experimental outputs only. It did not rerun models, change raw results, or alter unrelated manuscript sections. The main Word document’s hand-formatted tables were preserved while its main-text figures and supplementary cross-reference were updated.

## Completed checks

- [x] Figure 5 uses exactly `full_perturbation` and `frozen_attn_v_only_pert_res` for all four architectures, with `feature_dir=jac_top`, `scale_s=1.0`, and each model’s specified block. All 24 model × pattern × condition rows are unique.
- [x] Figure 5 reports the mean per-image Euclidean (L_2) immediate-readout change for coherent, random-sign, and checkerboard patterns. The caption describes the distinct DINOv2 CLS-plus-mean-patch readout.
- [x] Primary clean-residual V-only/(K+V) decomposition remains in Supplementary Figure S12; reduced Tiny/DINO signed-logit replications remain in Figure S11. The held-out classifier-carrier plot is now Supplementary Figure S13; Figure S1 remains spatial-mask robustness.
- [x] Supplementary Figures S1–S13 have unique object/caption labels. Supplementary Tables S1–S3 and the evidence-map table are present in the editable Word supplement; table notation uses readable subscripts and superscripts.
- [x] `docs/PAPER_DRAFT_v5.docx` contains seven main figures, three manuscript data tables, ten numbered equations, and 51 references. Its formatted table XML matches the saved pre-edit version.
- [x] `docs/PAPER_SUPPLEMENTARY.docx` contains 13 supplementary figures and four tables and was exported without inventing a bibliography.
- [x] All 15 main DOCX pages and 13 supplementary DOCX pages were rendered and visually inspected. Figure 5, Tables S1–S3, and Figures S11–S13 have no visible clipping, duplication, or split caption.
- [x] `python scripts/validate_real_final_benchmark.py`: PASS, 12/12 checks.
- [x] `python scripts/validate_paper_final.py`: PASS, 28/28 checks.

## Validation and review artifacts

- `outputs/fungibility_real_final/validation_manifest.json`
- `outputs/fungibility_real_final/paper_final_validation.json`
- `docs/PAPER_FIGURE_REVIEW_V4.md`
- `docs/PAPER_DRAFT_v5.docx`
- `docs/PAPER_SUPPLEMENTARY.docx`
