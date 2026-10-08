# PCF evidence and claim boundaries

## Read before editing

Read these files first:

- `docs/PAPER_DRAFT.md`
- `docs/PAPER_FINAL_CLAIMS_TABLE.md`
- `docs/PAPER_NUMBER_TRACEABILITY.md`
- `docs/PAPER_SAMPLE_SIZE_MAP.md`
- `docs/PAPER_SUBMISSION_READINESS.md`
- `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md`

Then inspect current validated real-final reports (including `docs/REAL_FINAL_BENCHMARK_REPORT.md` and its current validation status), relevant validation manifests and raw evidence, and the current manuscript figure sources/previews. Use current HEAD only; do not hardcode a commit.

## Evidence priority

For current empirical claims, prefer validated raw outputs/manifests and the explicit claim/number/sample maps. Use `outputs/fungibility_real_final/` for real classifier-carrier accuracy and complete-call runtime; use `outputs/fungibility_operator_compression_confirmatory/` plus its report for strict confirmatory compression; use mechanism-specific validated outputs for the N=100 audits. Historical reports provide context only. The withdrawn `fungibility_final_consolidation` accuracy/timing/frontier tables are proxy-derived and cannot support empirical claims. Operator-space audit CSVs support only explicitly labeled linearized operator-space results.

## Canonical paper argument

Keep this causal and evidentiary chain visible:

1. Causal replacement of image-specific late patch content while preserving token slots and sequence structure.
2. Geometry and token-diversity constraints on replacement.
3. Anisotropic functional transmission.
4. Coherent accumulation versus cancellation, including the tested Value-path contribution.
5. Downstream Value-mediated mechanism and subspace rotation across blocks.
6. End-to-end `J_{l→L}` as a predictor/objective for downstream functional damage.
7. Operator-aware token compression.
8. Strict confirmatory validation at N=1,000 held-out images per architecture.

The practical predictor/carrier branch is secondary: operator-space correction can succeed while translation to nonlinear classification and deployment remains limited. It must not become the headline contribution.

## Novelty and claim guardrails

Do not claim novelty for Jacobians, SVD, anisotropy in general, token redundancy, pruning, merging, low-rank operators, or generic output-aware compression. The novelty boundary is the connected ViT-specific causal chain, especially content substitution that preserves slots/sequence structure, then geometry/diversity constraints, Value-mediated coherence/cancellation, downstream functional transmission, and operator-aware compression.

Keep sample units distinct everywhere:

| Study | Unit |
|---|---|
| Attention causal audit | N=100 images |
| Functional geometry | N=100 images |
| Multi-block operator study | N=100 held-out perturbations |
| Strict confirmatory compression | N=1,000 held-out images per architecture |
| Real classifier carrier benchmark | N=1,000 held-out images per architecture |
| Operator-space carrier experiments | Separate N=100 operator-space evidence |

The 30,000 method/budget/seed rows per architecture in confirmatory residual analysis reuse those 1,000 images; do not describe rows as independent images.

The former universal rank-16/32 `>98%` claim is withdrawn. Its original stated metric is the Top-1 accuracy ratio `100 × (A_rank − A_GroupMean)/(A_fullJ − A_GroupMean)`. Recomputed from matched per-image outcomes, 22 of 40 settings have a positive denominator; only 4 of those 22 exceed 98%, while 18 are below. Sixteen denominators are negative and two are zero, so those settings do not represent recovery of a positive full-J benefit. Never state a universal `>98%` result. Keep the bounded recomputation in the audit/traceability record, not as a manuscript headline. Do not reinterpret it as retained spectral energy, operator-residual recovery, practical-predictor recovery, restricted-carrier-oracle recovery, or static-alpha recovery.

## Research lock

Do not launch new experiments, create hypotheses, make research branches, edit raw outputs, fill evidence gaps with synthetic values, or restore invalid proxies. A manuscript question that needs more evidence becomes `FUTURE WORK` or `REQUIRES NEW EXPERIMENT`; continue edits that are supported by existing audited evidence.
