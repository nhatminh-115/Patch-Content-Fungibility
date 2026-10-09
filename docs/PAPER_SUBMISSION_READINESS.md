# Paper Submission Readiness

**Status: REPORTING AUDIT COMPLETE; REQUIRED VALIDATORS PASS; DOCX VISUALLY INSPECTED**

The manuscript-wide scientific-writing and reporting audit covered Sections 3–9, figure/table captions, and the supplementary draft. Cohort definitions, seed construction, aggregation, and statistical procedures are documented in Methods and the supplement; Results lead with findings and retain the evidence needed to interpret them. Existing claims, numerical results, and sample-unit boundaries were preserved. No experiment was rerun and no raw output was modified.

## Completed checks

- [x] `python scripts/validate_real_final_benchmark.py`: PASS, 12/12 checks, 2026-10-09.
- [x] `python scripts/validate_paper_final.py`: PASS, 27/27 checks, 2026-10-09.
- [x] The manuscript retains separate sample units for image audits, held-out perturbations, confirmatory compression, and classifier-carrier evaluation.
- [x] Seed counts, split construction, aggregation rules, and statistical tests are recorded by evidence family in the supplementary reproducibility section.
- [x] The figure review record distinguishes DeiT-Small's 57.6% ± 5.9% coordinate-permutation seed mean from the legacy 58.2% majority-correctness summary.
- [x] AUROC is expanded at first use in the main text.
- [x] `docs/PAPER_DRAFT_v5.docx` was regenerated from the current Markdown. It contains eight reviewed figures, three manuscript data tables, ten numbered equations, and 51 references; the existing formatted table and equation layouts were preserved.
- [x] All 15 rendered DOCX pages were visually inspected. Figures, equations, tables, captions, and references have no visible clipping or overlap.
- [x] Existing local edits were preserved; no raw experimental outputs or generated figure data were changed during this audit.

## Remaining issues

No blocking manuscript or layout issue was identified by this audit or the required validators. The manuscript continues to state the limits of the local functional metrics and the practical classifier-carrier results without treating them as general deployment evidence.

## Validation and review artifacts

- `outputs/fungibility_real_final/validation_manifest.json`
- `outputs/fungibility_real_final/paper_final_validation.json`
- `docs/PAPER_FIGURE_REVIEW_V4.md`
- `docs/PCF_PAPER_SKILL_TEST.md`
- `docs/PCF_PAPER_UPGRADE_REPORT.md`
- Final DOCX render preview: `D:\Study\ResCancel\pcf_reporting_audit_qa_20261009c`