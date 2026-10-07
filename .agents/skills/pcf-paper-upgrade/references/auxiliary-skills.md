# Optional auxiliary skill routing

Check the installed-skill catalog or project skill files for these named workflows when the corresponding phase is requested. Invoke an auxiliary skill only if available and relevant; it is nonessential. If a skill is missing, continue with this PCF skill's evidence rules and available tools, and do not claim that the missing skill was used.

## Research-paper lifecycle

- `research-paper-lifecycle-skills`: `paper-profile`, `study-exemplars`, `benchmark-paper`, `refactor-structure`, `verify-claims`, `verify-citations`, `draft-related-work`, `polish-prose`, `polish-tables-figures`, `simulate-reviewers`, `reflect-paper`, `reflect-and-improve`, `assess-paper`, `fit-page-limit`.
- `scicomp-research-skills`: `research-paper-writing`, `literature-survey`, `human-facing-doc-authoring`.
- `scientific-writer-skill`: `REVIEW`, `DIAGNOSE`.
- `lulab-research-skills`: `find-redflag`, `roast-figure`, `check-facts`, `manage-refs`, `review-landscape`, `visualize-blackbox`.

## Route by task

- Profile, exemplar study, structure, claims, citations, related work, prose, review simulation, reflection, assessment, or page fit: use the corresponding lifecycle/research/writer workflow if installed.
- Figure or table polish: prefer `polish-tables-figures`; for figure-specific critique use `roast-figure`; use `visualize-blackbox` for visual explanation where useful.
- Citation or fact audit: use `verify-citations`, `check-facts`, and `manage-refs` if installed.
- Landscape scan: use `review-landscape` only when literature positioning is in scope.

Auxiliary tools and skills must not weaken the PCF claim boundaries, authorize new experiments, or substitute suggestions for validated evidence. Record unavailable dependencies only when they materially limit a requested deliverable.
