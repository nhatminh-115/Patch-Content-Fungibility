# Figure Review v4

**Verdict: accepted after visual iteration.** The seven quantitative figures and supplement were generated from the deterministic code pipeline and inspected at full resolution and in the contact sheet. Figure 1 uses the latest user-supplied overview image, including panel (c) on anisotropic transmission, preserved pixel-for-pixel and embedded in an SVG wrapper. The scientific claims and data were not changed. The v3 files remain preserved.

Scores use a 1–5 scale (5 is strongest).

| Figure | Before / after | Readability | Scientific clarity | Aesthetic quality | Set consistency | Revision needed | Final verdict |
|---|---|---:|---:|---:|---:|---|---|
| 1. Overview | Latest supplied composite overview: (a) intervention, (b) replacement constraints and Value-path cancellation, and (c) anisotropic transmission. | — | — | — | — | Source image reproduced unchanged. | Accepted as requested. |
| 2. Depth-wise replacement | Plots audited V1 CSV rows plus a separately recorded depth-6 follow-up, with clean references and Gaussian seed variability. | 5 | 5 | 4 | 5 | Follow-up added at the user's request. | Accepted; depth 6 is visible and the late-layer failure of zero replacement remains easy to see. |
| 3. Geometry and diversity | Panel (a) shows V1 50% geometry controls for ViT-B/16 and DINOv2; panel (b) shows the V0.8 grouped-diversity K sweep for DeiT-Tiny/Small. The caption marks the distinct cohorts. | 5 | 5 | 4 | 5 | Reduced from three panels to two at the user's request; the panel-(a) legend remains below the plot. | Accepted; K sweep retained and relabeled as (b). |
| 4. Anisotropic geometry | Replaced an unnamed trend line with a direction-sensitivity heatmap and a compact vector explanation. | 4 | 5 | 4 | 5 | Yes: switched the ratio scale to logarithmic and increased precision so sub-unity values did not round to zero. | Accepted; values and direction are legible. |
| 5. Value path | Replaced a crowded combined panel with the measured coherent/random-sign/checkerboard comparison for V-only and K+V. | 5 | 5 | 4 | 5 | Yes: offset paired markers and moved panel labels into the titles to remove overlap. | Accepted; coherent versus cancelling patterns are clear. |
| 6. End-to-end operator | Reframed the mechanism as a local-to-downstream diagram paired with the reported held-out damage correlations and rotation angle. | 4 | 5 | 4 | 5 | No. | Accepted; the evidence distinction is explicit. |
| 7. Confirmatory compression | Replaced isolated low-rank bars with N=1,000 accuracy-token curves across four models. The current panel plots rank-32 and makes no recovery-percentage claim; separate rank-16 Top-1 values are in Table II. | 4 | 5 | 4 | 5 | Yes: increased footer spacing after the initial overlap. | Accepted; pruning, merging, oracle, and rank-32 are distinguishable. |
| S1. Carrier boundary | Replaced dense method annotations with a four-model measured accuracy-throughput view at BS=64. | 4 | 5 | 4 | 4 | Yes: fixed the ViT-B source label and separated nearby q16/selective annotations. | Accepted; mixed practical results are visible without claiming a general win. |

## Visual QA

- Contact sheet: `figures/paper_final_v4/contact_sheet.png`.
- Individual 300 dpi previews: `figures/paper_final_v4/*.png` and `figures/paper_final_v4/supp/*.png`.
- Per-figure zoom previews: `figures/paper_final_v4/previews/` and `figures/paper_final_v4/supp/previews/`.
- Quantitative SVG/PNG panels are generated from deterministic Matplotlib figure objects; Figure 1 is the supplied PNG embedded in an SVG wrapper.
- The first visual passes exposed footer collisions in Figures 1 and 7, model labels colliding with the Figure 3 panel title, a heatmap rounding small ratios to zero, panel-label collision in Figure 5, and a ViT-B facet filter mismatch in S1. The final files were regenerated and re-inspected after those revisions.
- No unresolved label clipping, panel overlap, missing facet, color-meaning conflict, or legend collision was found in the final contact sheet and per-figure previews.

## Style revision requested on 2026-10-07

- Removed figure-level headline titles and embedded bottom caption/footer text from all figures; retained the scientific content and concise panel titles/labels.
- Figure 2 no longer places a `Clean` text annotation across the dashed reference line; the dashed reference is identified in the legend.
- Figure 2 now marks a central crowded region in panel (a) and shows it in a matched zoom box shifted right within the same chart. Two dashed connectors link the selected region to the zoom box, which includes Clean and all three replacement curves across depths 5–8, including the later depth-6 follow-up.
- Figure 5 now uses paired bars for the measured V-only and K+V pathway values in each token-pattern condition, with the same audited values and source rows.
- Figure 7 legend moved below the axes into its own reserved margin after the first updated preview showed overlap with x-axis ticks.
- Figure 7 now uses architecture-specific tight accuracy ranges with margin around every plotted value and clean reference, reducing unused vertical space without clipping data.
- Removed the standalone bottom annotation from Figure 6; the measured 49.0° block-8-to-9 principal angle is retained in the manuscript caption.
- Rebuilt every SVG/300 dpi PNG from the source generator and re-inspected the updated contact sheet and individual figures. No source data or scientific result changed.

## Figure 3 text and cohort clarification requested on 2026-10-07

- Removed the explanatory note from panel (b) and placed the shared-versus-independent definition in the Word manuscript caption.
- Moved panel (a)'s legend below its plotting area so it no longer covers the low-accuracy bars or points.
- Made the two model cohorts explicit in the caption: panel (a) uses V1 ViT-B/16 and DINOv2 geometry controls; panels (b,c) use V0.8 DeiT-Tiny and DeiT-Small diversity controls. The caption warns that the studies are separate cohorts and cross-panel absolute accuracies are not matched-model contrasts.
- Kept the cohorts separate because the existing V0.7 report and CSV disagree on some DeiT-Tiny/Small geometry values; substituting those data into panel (a) without resolving the discrepancy would be unsupported. No experiment or source output was changed.
- Shortened all three panel titles for consistent scanning: geometry at 50% replacement; token diversity at K=1 versus K=196; and accuracy versus K.
- Regenerated and visually inspected Figure 3 and the contact sheet after the edits.

## Figure 1 replacement requested on 2026-10-07

- Replaced Figure 1 with `figures/paper_final_v4/source/figure1_overview_user.png`, exactly as supplied by the user. The generated PNG and preview preserve the source bytes; the SVG embeds the same PNG so the manuscript's existing SVG reference remains valid.
- The manifest records this user-provided image provenance. No empirical data or scientific result changed.

## Figure 2 depth-6 follow-up on 2026-10-07

- Added the separately recorded depth-6 measurements for ViT-B/16 AugReg and DINOv2 ViT-S/14 to the Figure 2 plot and zoom inset. Original V1 measurements at depths 5, 7, 8, 9, and 10 remain sourced from their original CSVs.
- The follow-up ran the same 25% replacement controls on N=1,000 calibration and N=1,000 held-out evaluation images per architecture, with the original split and mask seeds and three Gaussian seeds. It completed in 44.29 seconds on an NVIDIA GeForce RTX 5070 Laptop GPU.
- Original V1 output files were not modified. The follow-up provenance and per-image records are kept in `outputs/fungibility_v1_depth6_followup/` and summarized in `docs/FUNGIBILITY_V1_DEPTH6_FOLLOWUP.md`.
- Regenerated and visually reviewed Figure 2, its central zoom, contact sheet, and the replacement image points. The depth-6 extension is labeled as a post hoc follow-up in the caption and traceability records.

## Figure 3 clarity redraw requested on 2026-10-07

- Reorganized the chart as three explicit questions: whether replacement-vector geometry matters at 50% replacement; whether shared versus per-patch vectors matter when all 196 patch tokens are replaced; and how accuracy changes with the number `K` of distinct vectors.
- Replaced unexplained horizontal mean ticks with mean bars, overlaid individual runs, seed-spread error bars, and gray dashed clean-accuracy references. The `K=1` and `K=196` endpoints are labeled in plain language.
- Updated the caption to define centroid, coordinate shuffling, sign flipping, shared/independent surrogates, `K`, and the N=1,000 evaluation unit. Source outputs and numerical values are unchanged.
- Regenerated and visually inspected the full-resolution figure and contact sheet. The three panels remain readable without overlapping labels or obscuring observations.

## Figure 3 panel reduction requested on 2026-10-07

- Removed the former panel (b), which compared shared and independent endpoint conditions, as requested; retained the grouped-diversity K sweep and relabeled the former panel (c) as (b).
- Reflowed Figure 3 as a two-panel layout. Updated the manuscript caption, sample-size map, number traceability, generator, and figure manifest to reflect the retained panels.
- The V0.8 shared-versus-independent source outputs remain unchanged; only their display in Figure 3 was removed.
- Regenerated and visually reviewed the two-panel figure and contact sheet.

## Scope and integration

- No experiment, model execution, or scientific claim was added or altered.
- Quantitative panels use the exact source files and row filters recorded in `figures/paper_final_v4/FIGURE_MANIFEST.md`.
- The main manuscript was updated only after this visual review was accepted; changes are limited to figure paths, captions, and the sentence assigning figure roles.
- The editable Word export is generated from the canonical manuscript Markdown and the reviewed v4 PNG figures. Its eight embedded images and updated Figure 1 caption were structurally verified; page layout was not visually verified because this host lacks a DOCX renderer.


## Figure 1 overview update requested on 2026-10-07

- Replaced the supplied overview source with the latest `D:/Download/Figure1_overview.png`, which adds panel (c), “Anisotropic Transmission.” The PNG and preview preserve the supplied source bytes, and the SVG embeds the same image.
- Updated the manuscript alt text and caption, and the figure manifest, to describe all three panels.
- Updated contact-sheet rendering to composite transparent pixels over white, avoiding a false black edge while preserving the supplied source and standalone PNG bytes exactly. No empirical data or scientific result changed.


## Figure 1, Figure 4, and manuscript notation update requested on 2026-10-08

- Replaced the Figure 1 source with the latest user-supplied `D:/Download/Figure1_overview.png`; its panels show the fixed-slot intervention, geometric/diversity constraints, and selective transmission through anisotropic sensitivity and Value-path cancellation.
- Tightened the spacing between the two density maps in Figure 4(b) using a nested grid; the plotted observations, axes, and source data are unchanged.
- Updated the Figure 1 in-text description, alt text, caption, and manifest to match the supplied panels. Removed the non-publication disclaimer from the caption.
- Updated the DOCX exporter to encode subscripts and superscripts throughout equations and inline prose as Word math/script structures; figure captions use semantic subscript/superscript markup where needed.
- Replaced defensive novelty wording with a concise statement that the underlying analytical tools are established, removed an internal CSV path from the Results prose, and simplified the reproducibility statement. Substantive evidence boundaries remain in place.
- Rebuilt figures from the existing source data and visually inspected the changed assets. No experiment, raw output, or quantitative result was changed.
