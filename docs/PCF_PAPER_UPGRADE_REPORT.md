# PCF Manuscript Upgrade Review

**Scope:** Evidence-preserving manuscript revision after the `pcf-paper-upgrade` dry-run passed. No experiments or raw-output changes were made.

## Structure diagnosis

The existing draft already follows the intended causal sequence: fixed-slot patch-content intervention; geometric and diversity boundaries; anisotropic transmission through attention; multi-block downstream geometry; operator-aware compression; and a separate practical carrier boundary. The principal structural risks were not missing sections but (1) a dense introduction that compressed several stages into one findings paragraph, (2) a related-work section that listed methods before making the intervention distinction explicit, and (3) a section-opening sample-size description that called the evidence “four units” before separately mentioning two more carrier units.

The manuscript was revised selectively rather than reordered. The introduction now explains how the controls narrow the replaceability claim and how the mechanism motivates, but does not prove, the later compression result. Related work now distinguishes sequence-changing pruning/merging methods from the fixed-slot content intervention before discussing adjacent mathematical tools. The sample-size paragraph names the mechanism, confirmatory, classifier-carrier, and operator-space units separately. The limitations now state the offline status of the full-J oracle and bound runtime conclusions to measured hardware, batch sizes, and implementations.

## Exemplar benchmarking

Three primary venue papers were reviewed for question framing, baseline role, and evidence presentation:

- [DynamicViT, NeurIPS 2021](https://proceedings.neurips.cc/paper/2021/hash/747d3443e319a22747fbb873e8b2f9f2-Abstract.html) frames token importance, a concrete pruning mechanism, and accuracy/efficiency evidence. Transferable lesson: define the intervention and operational outcome separately.
- [EViT, ICLR 2022](https://openreview.net/forum?id=9ND8fMUzOAr) reorganizes tokens by retaining attentive tokens and fusing others. Transferable lesson: explain exactly how token handling changes so comparisons are interpretable.
- [ToMe, ICLR 2023](https://openreview.net/forum?id=JroZRaRw7Eu) presents a training-free merging mechanism with accuracy/throughput outcomes. Transferable lesson: keep the method baseline's practical objective distinct from a mechanistic intervention.

The PCF paper uses these works as task context and compression baselines, not as evidence for fungibility. Its related-work paragraph now states the fixed-slot distinction directly. No venue-specific template or section order was copied wholesale.

## Related-work and claim verification

Primary venue records were checked for the three token-reduction exemplars above; arXiv records were checked for the recent adjacent works already cited in the draft. The paper keeps these adjacent works scoped to their actual model family or task. Existing citation resolution also passes the repository's manuscript validator (12 bibliography entries, no unresolved, duplicate, or uncited entries).

Numeric and scientific claims were checked against the claims table, traceability map, sample-size map, current real-final validation/report, confirmatory raw outputs and report, and current figure manifest/review. No quantitative result, sample count, metric, denominator, architecture coverage, or uncertainty statement was changed. The >98% sentence retains the Group-Mean-to-full-J-oracle compression-benefit denominator. The manuscript does not inherit broader deployment or universal-dominance language from older report prose: its practical carrier conclusion remains mixed and secondary.

## Adversarial reviewer simulation

| Reviewer concern | Disposition | Manuscript response |
|---|---|---|
| Mechanistic interpretability: a Value-path ratio above 100% may be misread as an impossible attribution. | ALREADY ADDRESSED | The draft explains that a secondary contribution can oppose the Value-path effect and limits the claim to the tested frozen-attention intervention. |
| Mechanistic interpretability: local geometry may not predict later nonlinear damage. | ALREADY ADDRESSED | The draft compares single-block and end-to-end prediction on N=100 held-out perturbations and explicitly avoids claiming nonlinear invariance. |
| ViT efficiency: do improvements over pruning imply general superiority over merging or a deployable speedup? | VALID | Related result language preserves the three-of-four frontier scope and the DeiT-S tie; limitations clarify the oracle and hardware/batch-specific runtime boundary. |
| General ML: are the N=100 mechanism studies conflated with N=1,000 classification evidence or with repeated condition rows? | VALID | The scope paragraph now enumerates each sample unit; confirmatory condition rows remain explicitly dependent on reused images in the existing text. |
| General ML: could Jacobian/SVD/anisotropy or token reduction themselves be the novelty? | ALREADY ADDRESSED | The related-work section explicitly disclaims these primitives and states the connected ViT-specific causal chain. |
| Any reviewer: broader architectures/tasks or practical predictor deployment need new measurements. | REQUIRES NEW RESEARCH | Kept as an explicit limitation/future-work boundary; no experiment was run or added to this paper. |

No OUT OF SCOPE request was accepted as a manuscript change. No new evidence was requested by the dry-run; the broader-coverage item remains a limitation.

## Figure and table audit

The eight current v4 figures were checked against `figures/paper_final_v4/FIGURE_MANIFEST.md`, the deterministic generator/source mappings, the SVG and 300-dpi PNG pairs, and `docs/PAPER_FIGURE_REVIEW_V4.md`. I visually inspected the current contact sheet: the sequence from causal intervention through geometry, Value-path cancellation, end-to-end transmission, confirmatory compression, and the mixed carrier boundary reads coherently; labels and panel hierarchy are legible at contact-sheet scale. The previous per-figure review records detailed 100%/zoom inspection and iterative fixes for label collisions, footers, scale precision, facet selection, and annotations. The figures remain unchanged because the current set is already code-generated, source-traceable, and reviewed.

## Selective revisions and quality assessment

Revised `docs/PAPER_DRAFT.md` in four places: introduction argument flow, related-work positioning, sample-unit wording, and practical limitations. The edits make the causal chain and evidence boundaries easier to audit while leaving scientific results untouched. No section reordering was warranted; the current section architecture already matches the paper's argument. Paragraphs remain developed rather than fragmented, and no filler was added.

Quality assessment: the manuscript now more clearly separates causal mechanism, confirmatory compression, and practical translation. The claim hierarchy is bounded, figure set is accepted, and the existing draft already meets the empirical publication checks. Final validator status and DOCX export status are recorded after the last manuscript edits in the repository readiness record.
