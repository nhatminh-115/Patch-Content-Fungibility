# PCF Paper Skill Dry-Run Test

**Date:** 2026-10-07
**Mode:** audit-only; manuscript editing disabled
**Skill:** `.agents/skills/pcf-paper-upgrade/SKILL.md`

## Checks

| Check | Result | Evidence |
|---|---|---|
| Project-local discovery | PASS | Skill is at the repository Agent Skills location `.agents/skills/pcf-paper-upgrade/SKILL.md`; it has the required `name` and discriminating `description` front matter. The bundled `quick_validate.py` reports `Skill is valid!`. |
| Authoritative files found | PASS | All six required paths exist: draft, claims table, number traceability, sample-size map, submission readiness, and strict confirmatory report. Current `docs/REAL_FINAL_BENCHMARK_REPORT.md`, validation outputs, v4 figure manifest, previews, and figure review were also inspected. |
| Canonical scientific story | PASS | Audit recovers the ordered chain: fixed-slot patch-content replacement → geometry/diversity limits → anisotropic transmission and coherent Value-path accumulation/cancellation → downstream rotation and `J_{l→L}` → operator-aware compression → N=1,000-per-architecture confirmatory test. |
| Sample units kept distinct | PASS | N=100 attention images; N=100 functional-geometry images; N=100 held-out perturbations for multi-block prediction; N=1,000 held-out images per architecture for confirmatory compression and real classifier-carrier results; separate N=100 operator-space carrier evidence. |
| >98% claim and novelty boundary | CORRECTED 2026-10-08 | The earlier dry-run row treated >98% as an active claim. The mathematical audit recovered the stated Top-1 ratio and found only 4 of 22 positive-denominator settings above 98%; the universal claim is withdrawn. Novelty remains on the connected ViT-specific causal chain. |
| Carrier branch is secondary | PASS | The draft and current real-final report bound operator-space gains against mixed/non-general classifier accuracy and deployment results. The carrier/predictor branch is not the headline contribution. |
| Research lock honored | PASS | No experiment, new hypothesis, branch, raw-output edit, or proxy metric was proposed or run. Unsupported extensions remain future-work questions. |
| Correct final validators | PASS | `python scripts/validate_real_final_benchmark.py`: PASS 12/12. `python scripts/validate_paper_final.py`: PASS 16/16 on the existing manuscript. |
| No manuscript rewrite during dry-run | PASS | `docs/PAPER_DRAFT.md` remained unchanged during the audit-only pass; its baseline SHA-256 was `3E7FDE687DDC97B24CB22E4410329EECCC7BCFE000E9CB303C36E67534FCF23F`. |

**Dry-run verdict: PASS.** The skill identifies the expected files, scientific argument, sampling units, claim boundaries, secondary carrier status, and validators without changing manuscript text or requesting new research. The full workflow may now run under the skill's research lock.
