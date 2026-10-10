# Repository Structure

This map describes the tracked repository without relocating scientific data. For the exact file-by-file classification and preservation decisions, see [REPO_CLEANUP_INVENTORY.md](REPO_CLEANUP_INVENTORY.md).

## Current publication files

- `docs/PAPER_DRAFT.md` and `docs/PAPER_DRAFT_v5.docx` — current main manuscript source and editable Word export.
- `docs/PAPER_SUPPLEMENTARY_DRAFT.md` and `docs/PAPER_SUPPLEMENTARY.docx` — current supplementary source and editable Word export.
- `docs/PAPER_FINAL_CLAIMS_TABLE.md`, `PAPER_NUMBER_TRACEABILITY.md`, and `PAPER_SAMPLE_SIZE_MAP.md` — claim, number, and sample-unit maps.
- `docs/PAPER_REFERENCES.bib`, root `CITATION.cff`, `LICENSE`, and `paper/LICENSE.md` — citation and license records. `arxiv/` retains preprint export metadata; the Zenodo title and DOI are historical and remain intact.

## Canonical figure paths

The current Markdown manuscript references main Figures 1–8 in `figures/paper_final_v4/`. Its actual DOCX media hashes match the same-named PNGs there. The current supplementary Markdown references S1–S9 in `figures/paper_final/supp/` and S10–S15 in `figures/paper_final_v4/supp/`. Exact data sources and row filters are in `figures/paper_final_v4/FIGURE_MANIFEST.md` and the reproducibility guide.

`figures/paper_final/main/` is a separate generated render set referenced by historical review/migration records; it is not the main manuscript's linked figure set and must not be substituted by filename similarity. `figures/paper_final_v2/` and `figures/paper_final_v3/` are earlier figure iterations retained as archive candidates. Other `figures/fungibility_*` folders preserve study-specific plots.

## Scientific evidence and results

- `outputs/` contains raw per-image CSV/Parquet results, aggregate tables, run manifests, split/cohort records, calibration statistics, validation JSON, and historical exploratory outputs.
- Claim-supporting sources for the current paper are identified in `docs/PAPER_NUMBER_TRACEABILITY.md`, `docs/PAPER_FINAL_CLAIMS_TABLE.md`, the figure manifest, and `docs/REPRODUCIBILITY_GUIDE.md`.
- Earlier, negative, failed, and superseded experiments remain part of the record. Large files are not automatically temporary; the inventory identifies external-storage candidates but keeps them in place.

## Implementations, protocols, and validation

- `patch_fungibility/` contains the model, intervention, data-loading, geometry, and compression implementations.
- `scripts/` contains experiment runners, figure builders, audits, and validators. Current publication gates are `validate_paper_final.py` and `validate_real_final_benchmark.py`.
- `docs/` contains current protocols, historical protocols, reports, audits, and publication-development records. A report's age or filename is not by itself evidence that it can be removed.
- `.github/workflows/` contains automated figure/export workflows; their generated outputs are not automatically the files used by the current manuscript.

## Generated figures and previews

Figure SVG, PNG, and PDF assets are tracked publication or research records. Within v4 figure folders, `previews/` and `contact_sheet.png` are review outputs, while `source/` retains upstream artwork and source data. The separate `figures/paper_final/main/` workflow output is preserved but not treated as interchangeable with v4.

## Archived preprint and licenses

`arxiv/` contains export tooling/metadata; `paper/` records manuscript licensing. `README.md` distinguishes the current journal draft from the archived Zenodo preprint and preserves its original title and DOI.