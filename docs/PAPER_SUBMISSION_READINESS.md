# Paper Submission Readiness

**Status:** Structural validation passes; final page-layout review is blocked because the bundled DOCX renderer cannot find LibreOffice.

The manuscript contains eight main figures, four numbered main tables (Table 1–4), 58 references, and ten numbered equations. The Supplementary displays ten figures (S1–S10) and retains Supplementary Tables S1–S6, the evidence map, and methods/data/negative findings in prose where figures were removed. Generator/source IDs remain unchanged in filenames and map to the final display labels in `figures/paper_final_v4/FIGURE_MANIFEST.md`.

## Verified checks

- [x] The main DOCX retains eight figure drawings, four numbered table captions, ten equation blocks, and 58 references.
- [x] The Supplementary DOCX contains ten figures with captions S1–S10 in order and retains Supplementary Tables S1–S6.
- [x] Figure/table labels, caption order, Markdown paths, and main-to-supplementary callouts resolve.
- [x] `outputs/fungibility_real_final/validation_manifest.json` records PASS, 12/12 benchmark checks.
- [x] `scripts/validate_paper_final.py` passes 42/42 checks for the current publication package.
- [x] `git diff --check` passes.
- [ ] Render and visually inspect all pages; `render_docx.py` cannot run because bundled `soffice.exe` is unavailable.

## Validation artifacts

- `outputs/fungibility_real_final/validation_manifest.json`
- `outputs/fungibility_real_final/paper_final_validation.json`
- `docs/FINAL_SUPPLEMENTARY_STREAMLINING.md`
- `docs/PAPER_DRAFT_v5.docx`
- `docs/PAPER_SUPPLEMENTARY.docx`
