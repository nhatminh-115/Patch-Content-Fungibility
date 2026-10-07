# Review workflow and figure checklist

## Venue exemplars

For a full upgrade, study a small, relevant set of primary venue papers (for example DynamicViT at NeurIPS and ToMe at ICLR). Compare their question-to-contribution framing, section progression, baseline definitions, accuracy/efficiency reporting, limitations, and figure legibility. Transfer presentation lessons only; do not treat an exemplar's claims as PCF evidence or use exemplar comparison to inflate novelty.

## Adversarial reviewer lenses

Simulate three independent perspectives:

- **Mechanistic interpretability:** Is the replacement intervention causal and controlled? Are geometry, Value-path attribution, cancellation, and downstream operator claims separated and properly bounded?
- **ViT efficiency:** Are pruning/merging baselines comparable? Are token budgets, accuracy, full-call throughput, and frontier claims measured and clearly scoped? Does operator-space evidence stay distinct from classifier/deployment results?
- **Skeptical general ML:** Is the contribution genuinely connected and clearly differentiated without claiming primitive novelty? Are sample units, dependence, uncertainty, baselines, reproducibility, figures, and practical relevance explicit?

For each comment, record the issue, section/evidence checked, disposition (`VALID`, `ALREADY ADDRESSED`, `OUT OF SCOPE`, `REQUIRES NEW RESEARCH`), and any manuscript-only action. Review novelty, causality, statistics, units, baselines, practical relevance, clarity, figures, and reproducibility. Do not automatically revise a suggestion that changes scientific scope or needs new evidence.

## Figures

For each figure in scope, verify:

1. Source code and source-data provenance are recorded and the displayed values reconcile with validated evidence.
2. The SVG is editable/vector output and a high-resolution raster preview exists.
3. The rendered figure is opened and visually inspected at readable size; inspect labels, units, legends, contrast, whitespace, ordering, and consistency with the manuscript caption.
4. A weak figure is revised in source code and rendered/inspected again. Do not accept screenshots of plots.
5. Scientific content leads: reject generic AI slides, placeholder diagrams, cluttered infographics, unreadable plots, and decoration without information.

Write captions that explain the panel, population/unit, and key denominator or caveat where needed. A conceptual schematic must be labeled conceptual and must not resemble measured results.

## Selective revision and outputs

A full upgrade should leave a concise structure diagnosis, a source-grounded related-work positioning note, an adversarial reviewer report, and a quality assessment only when useful to the requested scope. Record exemplar citations/links if the task requests benchmarking. Keep paragraphs coherent rather than fragmenting them; avoid lengthening for its own sake. Recheck citations, claim traceability, captions, validators, and exported DOCX structure. Visual page-layout QA is a separate check from structural DOCX validation and must be reported accurately.
