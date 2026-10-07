# Paper Submission Readiness

**Status: MANUSCRIPT REVISED; FIGURES APPROVED; DOCX STRUCTURE VALIDATED — PAGE-RENDER QA UNAVAILABLE**

The manuscript prose was selectively upgraded after the PCF skill's audit-only test passed. Scientific results, quantitative claims, evidence units, and figure data remain unchanged. The current draft keeps the carrier branch bounded and secondary.

## Completed checks

- [x] Real-final benchmark gate passes: 12/12 checks; authoritative real-final evidence is present.
- [x] Manuscript and v4 figure publication gate passes: 16/16 checks.
- [x] Structure, related-work positioning, claim boundaries, sample units, and practical limitations were reviewed during the initial manuscript revision; original V1 raw outputs remain unchanged.
- [x] Visual review accepted seven main figures and one supplement; all have SVG and 300 dpi PNG outputs.
- [x] 2026-10-07 figure-style pass removed embedded headline/footer text, fixed Figure 2's Clean-reference collision and added an in-panel zoom showing all replacement curves with two dashed connectors, changed Figure 5 to paired bars, removed Figure 6's bottom note, and tightened Figure 7's per-architecture accuracy ranges without clipping data; all eight figures were rebuilt and visually inspected.
- [x] Figure 1 replaced with the user-supplied overview image; its source is retained and the manuscript-compatible SVG embeds the supplied image unchanged.
- [x] Figure 2 includes an isolated post hoc depth-6 follow-up (N=1,000 calibration and N=1,000 evaluation images per architecture); original V1 raw outputs remain unchanged, and the manuscript labels the extension explicitly.
- [x] Figure 3 uses two explicit panels with model/replacement conditions, clean references, and seed-level summaries; the shared-versus-independent panel was removed at the user's request, with empirical source values unchanged.
- [x] Figure sources, row filters, and design decisions are recorded in `figures/paper_final_v4/FIGURE_MANIFEST.md`.
- [x] `docs/PAPER_DRAFT_v4.docx` was regenerated from the revised Markdown after the figure pass; structural check confirms eight inline figures, eight embedded PNGs, and 12 formatted references.
- [x] The practical carrier remains a bounded, mixed result; the full-J oracle is described as offline.

## Remaining verification limit

DOCX page rendering could not be completed on this Windows host: the packaged renderer requires `soffice.exe`, which is absent, and `WINWORD` is not available on PATH. The refreshed DOCX package and its eight embedded images were checked structurally, but page layout has not been visually verified.

## Validation and review artifacts

- `outputs/fungibility_real_final/validation_manifest.json`
- `outputs/fungibility_real_final/paper_final_validation.json`
- `docs/PAPER_FIGURE_REVIEW_V4.md`
- `docs/PCF_PAPER_SKILL_TEST.md`
- `docs/PCF_PAPER_UPGRADE_REPORT.md`
