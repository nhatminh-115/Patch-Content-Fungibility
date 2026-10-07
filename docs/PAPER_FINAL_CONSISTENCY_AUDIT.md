# Final manuscript consistency audit

**Audit date:** 2026-10-07

**Source:** current `main` worktree; no experiment or raw-output modification was performed.

## Citations and references

- The manuscript has **50 in-text citation keys and 50 bibliography records**. All keys resolve one-to-one, every entry is cited, citation numbering follows first appearance, and the standalone BibTeX file matches the embedded manuscript source.
- Title, author list, year, venue, and a DOI or official proceedings/publisher record are present for every item. Normalized titles and DOI values have no duplicates.
- The editable Word reference list is IEEE-numbered `[1]` through `[50]`; DOI is printed where present, with the official record link used when a DOI is not listed.
- All 25 in-text citation clusters are strictly ascending and unique; the seven rendered numeric ranges and remaining individual citations match the source exactly in the DOCX.
- PatchDropout is cited as the published WACV 2023 paper with DOI `10.1109/WACV56688.2023.00394`. The official CVF proceedings record lists pp. 3953–3962; a DOI-derived secondary catalog lists pp. 3942–3951. The manuscript follows the official CVF proceedings record and records the conflict in `PAPER_CITATION_AUDIT.md`.

## Tables, figures, and cross-references

- The paper contains **3 tables** and **8 figures** (Figures 1–7 and Supplementary Figure S1).
- Every figure/table number resolves to one object and matching caption. Every object follows its first textual callout.
- Table I separates evidence cohorts and sampling units. Table II gives exact strict-confirmatory accuracy at each architecture's most aggressive tested budget. Table III gives correct counts and percentage-point changes for the separate classifier-carrier study.
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

## Evidence boundaries and formulas

- Attention causal audit: `N=100` images; functional geometry: `N=100` images; joint-stream geometry: `N=100` images per model; multi-block operator: `N=100` held-out perturbations.
- Strict confirmatory compression and real classifier-carrier benchmark: `N=1,000` held-out images per architecture. Operator-space carrier experiments remain separate `N=100` evidence.
- The `>98%` wording means rank-16/32 retain more than 98% of the **Group-Mean-to-full-J-oracle compression benefit**.
- The Abstract contains no defined abbreviations. Main-text abbreviations are defined at their first use.
- Six displayed equations cover the fixed-slot intervention, frozen Value path, end-to-end Jacobian, Group Mean, operator-aware objective, and trace-scaled regularization. The prose explains their variables and empirical scope.

## Validation and layout

- `python scripts/validate_real_final_benchmark.py`: **PASS, 12/12 checks**.
- `python scripts/validate_paper_final.py`: **PASS, 27/27 checks**, including IEEE citation order/range equality between Markdown and DOCX.
- The DOCX package has 3 native Word tables, 8 embedded figures, 6 Word math objects, and 50 ordered references. Page-by-page DOCX rendering was unavailable on this host, so the Word pagination itself was not visually inspected; figures were already reviewed in the existing figure review record.
