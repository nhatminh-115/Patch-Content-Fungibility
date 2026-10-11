# Final Supplementary Streamlining

**Date:** 2026-10-11
**Branch:** `fix/supp-legend-placement`

## Figure numbering

The final display order follows the actual appearance order in the Supplementary document. Source/generator IDs and filenames remain unchanged.

| Appearance | Original source figure | Final display figure | Result |
|---:|---:|---:|---|
| 1 | S1 | S1 | Kept: spatial-mask robustness |
| 2 | S2 | S2 | Kept: accuracy-retention thresholds |
| 3 | S10 | S3 | Kept: DINOv2 margin diversity |
| 4 | S4 | S4 | Kept: PC1 amplitude sensitivity |
| 5 | S9 | S5 | Kept: synthetic geometry banks versus pruning |
| 6 | S11 | S6 | Kept: reduced Value-path replication |
| 7 | S14 | S7 | Kept: joint token–feature geometry |
| 8 | S12 | S8 | Kept: primary Q/K/V comparison |
| 9 | S13 | S9 | Kept: measured classifier-carrier boundary |
| 10 | S15 | S10 | Kept: regularization sensitivity |

Five figures were removed from the Supplementary display. Their image, code, and experimental outputs remain in the repository:

- **Source S3, PCA-rank comparison:** its five-seed rank-1 and rank-64 Top-1 values are summarized in Supplementary Section S6.
- **Source S5, effective-rank propagation:** the Block-8-to-11 natural rank-1 result and near-zero static-centroid result are summarized in Section S6, identified as a separate single-seed run.
- **Source S6, exact carrier equivalence:** Section S8 retains 100% prediction agreement and maximum absolute logit discrepancy (4.49\times10^{-5}).
- **Source S7, accuracy versus downstream token count:** the negative matched-budget carrier results remain in Section S8, including the ViT-B and DINOv2 comparisons.
- **Source S8, legacy accuracy-versus-latency plot:** measured latency changes and the Tiny overhead result remain in Section S8 prose.

Supplementary tables S1–S6, all sections, equations, main Figures 1–8, and main Tables 1–4 retain their numbering.

## Embedded-image comparison

All 15 pre-edit Supplementary DOCX images were extracted and compared with their corresponding repository PNG source. Nine pairs were byte-identical. Six differed at the pixel level because the embedded/source renders have small antialiasing or canvas differences; full-size side-by-side review found the plotted results, axes, labels, legends, and panel contents visually equivalent. Retained embedded image bytes were left unchanged.

| Original source figure | DOCX media part | Final display | Comparison |
|---:|---|---:|---|
| S1 | `image1.png` | S1 | Byte-identical |
| S2 | `image2.png` | S2 | Raster/canvas difference; visually equivalent |
| S3 | `image4.png` | Removed | Raster/canvas difference; visually equivalent |
| S4 | `image5.png` | S4 | Raster/canvas difference; visually equivalent |
| S5 | `image6.png` | Removed | Raster/canvas difference; visually equivalent |
| S6 | `image7.png` | Removed | Byte-identical |
| S7 | `image8.png` | Removed | Byte-identical |
| S8 | `image9.png` | Removed | Raster/canvas difference; visually equivalent |
| S9 | `image10.png` | S5 | Rasterization difference at matching dimensions; visually equivalent |
| S10 | `image3.png` | S3 | Byte-identical |
| S11 | `image11.png` | S6 | Byte-identical |
| S12 | `image13.png` | S8 | Byte-identical |
| S13 | `image14.png` | S9 | Byte-identical |
| S14 | `image12.png` | S7 | Byte-identical |
| S15 | `image15.png` | S10 | Byte-identical |

No canonical source image was replaced, and no chart data or figure source file was changed.

## DOCX package and formatting preservation

- `PAPER_DRAFT_v5.docx`: only `word/document.xml` changed, to update supplementary figure callouts. All 23 package parts and all eight embedded main figures remain present; image bytes, styles, equations, tables, hyperlinks, and page settings are unchanged.
- `PAPER_SUPPLEMENTARY.docx`: `word/document.xml` and `word/_rels/document.xml.rels` changed; media parts `word/media/image4.png` and `image6.png`–`image9.png` were removed with their figure/caption paragraphs. No other package parts changed. All ten retained image bytes and their placements/extents are unchanged. Two evidence paragraphs were added using the existing body-paragraph style.
- Both DOCX ZIP packages pass integrity checks. Image relationships resolve; the Supplementary has exactly ten drawings, ten image parts, and captions S1–S10 in order. All eight Supplementary table elements remain present, including six numbered tables and the evidence-map/equation layouts.

The removed PCA figures' prose values were checked against `outputs/fungibility_v0_9/natural_vs_energy_matched_rank.csv` and `outputs/fungibility_v0_9/rank_propagation.csv`. No experimental output, model, or scientific conclusion was changed.

## Validation and rendering status

- `scripts/validate_paper_final.py`: **PASS, 42/42**.
- `scripts/validate_real_final_benchmark.py`: **PASS, 12/12**.
- `git diff --check`: **PASS**.
- The validators confirm eight main figures, ten supplementary figures, 58 references, four numbered main tables, and six numbered Supplementary tables.
- **Page-layout review is blocked.** The bundled `render_docx.py` was attempted for both documents but could not find `soffice.exe`; its cleanup also hit a sandbox permission error. Word was kept closed to preserve the user's current editing session. Therefore, DOCX pagination, page breaks, and all-page clipping/placement could not be re-rendered and visually verified in this pass.

No figure redesign, new experiment, source-data edit, or manuscript-wide DOCX regeneration was performed.
