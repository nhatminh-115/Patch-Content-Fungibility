# Figure Review v4

**Verdict: accepted after visual iteration.** All eight final SVG/PNG pairs were generated from the deterministic code pipeline and inspected at full resolution and in the contact sheet. The scientific claims and data were not changed. The v3 files remain preserved.

Scores use a 1–5 scale (5 is strongest).

| Figure | Before / after | Readability | Scientific clarity | Aesthetic quality | Set consistency | Revision needed | Final verdict |
|---|---|---:|---:|---:|---:|---|---|
| 1. Overview | Replaced a generic process strip with a fixed-slot intervention schematic, explicit surrogate controls, patch grids, and the measured evidence units. | 4 | 5 | 4 | 5 | Yes: separated the sample-unit footer after the first review. | Accepted; clear conceptual anchor. |
| 2. Depth-wise replacement | Replaced transcribed point curves with the audited V1 CSV rows, clean references, and seed variability. | 5 | 5 | 4 | 5 | No. | Accepted; the late-layer failure of zero replacement is easy to see. |
| 3. Geometry and diversity | Replaced summary bars with raw geometry-control points, shared/independent seed outcomes, and grouped-diversity curves. | 4 | 5 | 4 | 4 | Yes: moved model labels below the categories to avoid a title collision. | Accepted; three evidence components remain distinct. |
| 4. Anisotropic geometry | Replaced an unnamed trend line with a direction-sensitivity heatmap and a compact vector explanation. | 4 | 5 | 4 | 5 | Yes: switched the ratio scale to logarithmic and increased precision so sub-unity values did not round to zero. | Accepted; values and direction are legible. |
| 5. Value path | Replaced a crowded combined panel with the measured coherent/random-sign/checkerboard comparison for V-only and K+V. | 5 | 5 | 4 | 5 | Yes: offset paired markers and moved panel labels into the titles to remove overlap. | Accepted; coherent versus cancelling patterns are clear. |
| 6. End-to-end operator | Reframed the mechanism as a local-to-downstream diagram paired with the reported held-out damage correlations and rotation angle. | 4 | 5 | 4 | 5 | No. | Accepted; the evidence distinction is explicit. |
| 7. Confirmatory compression | Replaced the isolated low-rank bars with N=1,000 accuracy-token curves across four models and the audited >98% benefit statement. | 4 | 5 | 4 | 5 | Yes: increased footer spacing after the initial overlap. | Accepted; pruning, merging, oracle, and rank-32 are distinguishable. |
| S1. Carrier boundary | Replaced dense method annotations with a four-model measured accuracy-throughput view at BS=64. | 4 | 5 | 4 | 4 | Yes: fixed the ViT-B source label and separated nearby q16/selective annotations. | Accepted; mixed practical results are visible without claiming a general win. |

## Visual QA

- Contact sheet: `figures/paper_final_v4/contact_sheet.png`.
- Individual 300 dpi previews: `figures/paper_final_v4/*.png` and `figures/paper_final_v4/supp/*.png`.
- Per-figure zoom previews: `figures/paper_final_v4/previews/` and `figures/paper_final_v4/supp/previews/`.
- Every SVG and PNG is generated from the same deterministic Matplotlib figure object; no raster screenshots or text-to-image assets are used.
- The first visual passes exposed footer collisions in Figures 1 and 7, model labels colliding with the Figure 3 panel title, a heatmap rounding small ratios to zero, panel-label collision in Figure 5, and a ViT-B facet filter mismatch in S1. The final files were regenerated and re-inspected after those revisions.
- No unresolved label clipping, panel overlap, missing facet, color-meaning conflict, or legend collision was found in the final contact sheet and per-figure previews.

## Scope and integration

- No experiment, model execution, or scientific claim was added or altered.
- Quantitative panels use the exact source files and row filters recorded in `figures/paper_final_v4/FIGURE_MANIFEST.md`.
- The main manuscript was updated only after this visual review was accepted; changes are limited to figure paths, captions, and the sentence assigning figure roles.
- No extended DOCX manuscript was present in the repository or searched local project paths. The Word export is therefore generated from the canonical manuscript Markdown and the reviewed v4 PNG figures.
