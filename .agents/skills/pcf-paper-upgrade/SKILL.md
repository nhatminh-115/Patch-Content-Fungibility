---
name: pcf-paper-upgrade
description: Upgrade, audit, restructure, polish, reviewer-test, and visually inspect the Patch-Content Fungibility manuscript while preserving audited claims and experimental evidence.
---

# PCF paper upgrade

Use this project skill for manuscript audits, substantial paper upgrades, reviewer-style evaluation, figure review, or requested export of the Patch-Content Fungibility paper. Operate on the current checkout and current HEAD; never pin work to a commit SHA. Read `references/evidence-boundaries.md` before substantive work, `references/review-and-figures.md` when reviewing figures or running a full upgrade, and `references/auxiliary-skills.md` when routing work to optional installed skills.

## Hard limits

- Treat the authoritative files and evidence hierarchy in `references/evidence-boundaries.md` as gates. Read all six named manuscript/evidence files, current validated real-final reports, manifests/raw sources needed for the requested claims, and current paper figures before editing.
- Preserve scientific results, denominators, model/budget scope, sample units, and caveats. Do not convert operator-space evidence into Top-1 or deployment evidence. The carrier/predictor branch is secondary and must retain its limited real-classifier/deployment translation.
- Do not run new experiments, invent hypotheses, create research branches, edit raw outputs, manufacture evidence, or resurrect proxy metrics. If a requested claim needs new evidence, mark it `FUTURE WORK` or `REQUIRES NEW EXPERIMENT` and continue manuscript-level work.
- Do not claim novelty for Jacobians, SVD, anisotropy generally, token redundancy/pruning/merging, low-rank operators, or generic output-aware compression. Keep novelty on the connected ViT-specific causal chain in the reference.
- Avoid fragmented, filler-heavy prose. Build substantial paragraphs around claim/question, setup, evidence, interpretation, and limitation/implication. Change text only when it materially improves logic, accuracy, clarity, or venue fit; revert edits that do not.

## Workflow

1. **Inspect evidence and draft.** Read the authoritative files and current figure set. Establish claim-to-source and sample-unit mappings before proposing prose changes.
2. **Benchmark structure.** Study a small number of strong, relevant venue exemplars (especially ViT efficiency papers); use them for organization, evidence presentation, and figure conventions, never as evidence for PCF claims. Record source links and transferable observations when the task calls for a full upgrade.
3. **Diagnose and refactor.** State the paper's central question, argument chain, section roles, missing transitions, repetition, and scope. Reorder or rewrite only to strengthen that argument.
4. **Position related work.** Distinguish the intervention and causal question from token-sequence reduction methods and from established mathematical tools. Do not imply a literature claim beyond sources actually checked.
5. **Verify claims.** Check each quantitative and causal sentence against the claim table, traceability, sample map, validated reports/manifests, and raw source where necessary. Preserve exact units and uncertainty.
6. **Polish prose and tables/figures.** Keep methods, results, limitations, and claims aligned. Apply the figure rules in `references/review-and-figures.md` to every changed or requested figure.
7. **Adversarial review.** Simulate a mechanistic-interpretability reviewer, a ViT-efficiency reviewer, and a skeptical general-ML reviewer. Classify comments `VALID`, `ALREADY ADDRESSED`, `OUT OF SCOPE`, or `REQUIRES NEW RESEARCH`; only automatically resolve manuscript-level issues.
8. **Reflect and revise selectively.** Recheck argument flow, sample units, novelty boundary, practical limitations, and figure readability. Keep only changes that materially improve the paper.
9. **Assess and export.** Produce only deliverables implied by the request. For a manuscript-ready request, run `python scripts/validate_real_final_benchmark.py` and `python scripts/validate_paper_final.py`; both must pass before calling the manuscript ready. If either fails, inspect the assertion and repair manuscript-level causes without changing evidence, then rerun both.

## Figure and artifact rules

Figures must be generated from code and traceable source data, saved as SVG plus a high-resolution raster preview, and inspected in rendered form. If weak, revise and inspect again. Use installed `polish-tables-figures`, `visualize-blackbox`, or `roast-figure` skills when available and relevant; absence of an auxiliary skill is not a blocker. Reject generic AI-slide styling, placeholders, cluttered infographics, unreadable scientific plots, plot screenshots, and decorative figures without information. Use `references/review-and-figures.md` for the review checklist.

When requested, update `docs/PAPER_DRAFT.md` and produce an editable DOCX; PDF, figure-review records, mock reviews, structure diagnosis, and quality assessment are scope-dependent. Do not create every optional artifact on every invocation. Before committing/pushing, inspect the diff and status; do so only when the user requests it or has authorized it in the current task.
