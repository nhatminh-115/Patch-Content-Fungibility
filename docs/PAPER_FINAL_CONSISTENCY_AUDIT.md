# Final manuscript consistency audit

**Audit date:** 2026-10-10

**Source:** current `main` worktree; no experiment or raw-output modification was performed.

## Citations and references

- The manuscript has **53 in-text citation keys and 53 bibliography records**. All keys resolve one-to-one, every entry is cited, citation numbering follows first appearance, and the standalone BibTeX file matches the embedded manuscript source.
- Title, author list, year, venue, and a DOI or official proceedings/publisher record are present for every item. Normalized titles and DOI values have no duplicates.
- The editable Word reference list is IEEE-numbered `[1]` through `[53]`; DOI is printed where present, with the official record link used when a DOI is not listed.
- All 22 in-text citation clusters are strictly ascending and unique; the seven rendered numeric ranges and remaining individual citations match the source exactly in the DOCX.
- PatchDropout is cited as the published WACV 2023 paper with DOI `10.1109/WACV56688.2023.00394`. The official CVF proceedings record lists pp. 3953–3962; a DOI-derived secondary catalog lists pp. 3942–3951. The manuscript follows the official CVF proceedings record and records the conflict in `PAPER_CITATION_AUDIT.md`.

## Tables, figures, and cross-references

- The paper contains **3 tables** and **8 figures** (Figures 1–8 and Supplementary Figures S1–S14).
- Every figure/table number resolves to one object and matching caption. Every object follows its first textual callout.
- Table I groups analyses into six primary result families while retaining separate sample units and endpoints. Table II gives exact strict-confirmatory accuracy at each architecture's most aggressive tested budget. Table III gives correct counts and percentage-point changes for the separate classifier-carrier study.
- Figures use the existing reviewed SVG source set; the exporter embeds their high-resolution PNG previews in the DOCX.

## Numeric consistency

Table II was recomputed from `budget_summary.csv`; the strongest pruning method at each listed budget is:

| Architecture | Budget | Strongest pruning baseline | Group Mean | ToMe | Full-J oracle | Rank-16 | Rank-32 |
|---|---:|---:|---:|---:|---:|---:|---:|
| DeiT-Tiny | 32 | Random, 58.6% | 66.5% | 65.8% | 67.1% | 67.1% | 67.9% |
| DeiT-Small | 32 | Attention, 71.6% | 76.4% | 76.4% | 75.8% | 76.5% | 76.5% |
| ViT-B/16 | 32 | Random, 69.2% | 73.2% | 73.0% | 74.4% | 73.7% | 74.2% |
| DINOv2 ViT-S/14 | 42 | Random, 61.5% | 72.2% | 69.4% | 73.5% | 73.2% | 73.0% |

At these architecture-specific budgets, the operator-aware oracle and low-rank variants exceed the strongest pruning baseline by **4.2–12.0 percentage points**. Comparisons against each individual Random, Norm, and Attention baseline span **4.2–17.4 points**. The Abstract now states the stronger-baseline range; the traceability and claims tables preserve both comparator definitions.

Table III was recomputed from `real_accuracy_summary.csv`. Its four architecture/budget rows contain the matching integer counts, `N=1,000` accuracy, and percentage-point differences. These results remain separate from the strict confirmatory compression table and the `N=100` operator-space carrier evidence.

## Evidence boundaries and mathematical definitions

- Attention causal audit: `N=100` images; functional geometry: `N=100` images; joint-stream geometry: `N=100` images per model, reused for direction estimation and response measurement (within-cohort descriptive); multi-block operator: `N=100` held-out perturbations.
- Strict confirmatory compression and real classifier-carrier benchmark: `N=1,000` held-out images per architecture. Operator-space carrier experiments remain separate `N=100` evidence.
- The functional-geometry matrix `M_l` is the uncentered second moment of scalar class-margin gradients pooled over patch tokens. It is not the Gram matrix of the full downstream pre-classifier readout Jacobian `J^T J`. The separate joint-stream direction metric averages patch-margin gradients per image; it is also not the compression Jacobian.
- PCA uses the centered covariance of calibration patch-feature rows and denominator `M_cal - 1`, where `M_cal` counts calibration patch observations. The solver matrix `H_J` is instead a readout-space Gram matrix. The confirmatory Jacobian maps the row-major flattened patch matrix to the pre-classifier readout `u`, with `rvec(X)=vec(X^T)`: `d_u=D` for normalized CLS readouts and `d_u=2D` for DINOv2 normalized CLS concatenated with mean normalized patch features. The linear classification head is excluded; classifier outcomes are measured through the actual downstream model.
- The 10 displayed equations now cover fixed-slot replacement, the margin-gradient metric, head-wise attention weighting and measured Value-context change, joint token-by-feature perturbation, the full downstream Jacobian, Group Mean, the Tikhonov objective, its trace-scaled solver Gram and regularizer, the closed-form carrier update, and multiplicity-aware attention. Each equation is explained in nearby prose. The carrier update is exact for the stated local quadratic objective because the Group Mean residual sums to zero within each group; this does not make it an exact nonlinear classifier optimum.
- The attention scalar `Gamma_h(a)` summarizes alignment with clean attention weights. It does not replace token-specific `Delta v[h,i]`; the displayed context change retains the measured post-normalization Value differences. The `log(m_j)` multiplicity correction is identified as prior ToMe machinery, not a novelty claim.

## Same-group operator-residual comparison

- The confirmatory CSV contains 20,000 primary feature-similarity image-by-budget rows: four architectures × five budgets × 1,000 held-out images. Every row has positive `delta_op_residual`, defined as `||J E_mean||_2 - ||J E_operator||_2` under identical image, budget, and assignment matrix `S`.
- Equal-weighted means over five budgets are 1.27343 (DeiT-Tiny), 1.48137 (DeiT-Small), 2.52780 (ViT-B/16 AugReg), and 7.20394 (DINOv2 ViT-S/14). Images recur across budgets, so the manuscript reports descriptive operator-residual contrasts, not a significance test or guaranteed improvement in nonlinear logits or Top-1 accuracy.
- Joint-stream analyses reuse the same N=100 images for direction estimation and response scoring; their reported evidence is within-cohort descriptive.

## Rank-16/32 recovery audit

The audited recovery metric is **Top-1 condition accuracy**, not operator residual or spectral energy:

`100 * (A_rank - A_GroupMean) / (A_fullJ - A_GroupMean)`.

The recomputation uses `per_image_results.csv`, the same 1,000 held-out image IDs and seed 0 within each model/budget/method condition, and reconciles to the low-rank and budget summaries. Across the 40 selected rank-16/rank-32 rows, the Group-Mean-to-full-J denominator is positive in 22, negative in 16, and zero in 2. Only **4 of the 22 positive-denominator settings exceed 98%**; the other 18 do not. Negative-denominator settings do not measure recovery of a positive full-J benefit, and a zero denominator makes the ratio undefined.

At the most aggressive tested budgets, rank-16/rank-32 recovery is 100%/233.3% for DeiT-Tiny, 41.7%/83.3% for ViT-B/16 AugReg, and 76.9%/61.5% for DINOv2 ViT-S/14. For DeiT-Small, full-J is 0.6 percentage points below Group Mean at budget 32, so there is no positive Group-Mean-to-full-J benefit to recover. The four >98% cases are the two DeiT-Tiny rank settings at budget 32 and the two ViT-B/16 settings at budget 147; the latter ratios are 400% because the Top-1 denominator is only 0.1 percentage point. The manuscript therefore does not state a universal >98% recovery result and says recovery varies by architecture and budget.

Long et al. (CVPR 2023) is included as prior diversity-aware token-reduction work. Thrash et al. (arXiv:2609.35579, 2026) is identified as a preprint precedent for output-aware residual-stream pruning in LLMs. FishBack was reviewed but not cited because its LLM activation-steering focus does not directly support the manuscript’s compression argument.

- The Abstract contains no defined abbreviations. Main-text abbreviations are defined at their first use.

## Validation and layout

- `python scripts/validate_real_final_benchmark.py`: **PASS, 12/12 checks**.
- `python scripts/validate_paper_final.py`: **PASS, 30/30 checks**, including the Top-1 recovery recomputation and IEEE citation order/range equality between Markdown and DOCX.
- The editable DOCX has 3 native manuscript tables, 8 embedded figures, 10 numbered equation layout blocks containing editable Word math lines, and 53 ordered references. The title rule was removed, and figure-caption pairs are kept together.
- The main Word document was exported from the current Markdown source and visually inspected as a 16-page PDF rendered by Microsoft Word; the supplementary Word document was rendered and inspected as a 14-page PDF. The built-in `render_docx.py` route could not run because LibreOffice `soffice.exe` is unavailable, so Word PDF export was used for page-level review. The updated main page containing the Section 6 residual contrast was re-rendered and checked after the formula typography change.
- No experiments or raw outputs were changed.
