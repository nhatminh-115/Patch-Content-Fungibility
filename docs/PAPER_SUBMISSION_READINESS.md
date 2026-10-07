# Paper Submission Readiness

**Status: READY — evidence-first publication lockdown complete**

The manuscript, claim tables, traceability map, sample-size map, and v3 figures are aligned to the audited repository evidence. No new experiments or research were added during this rewrite.

## Lockdown checks

- [x] `python scripts/validate_real_final_benchmark.py` passes: 12/12 checks; authoritative real-final evidence is present.
- [x] `python scripts/validate_paper_final.py` passes: 15/15 publication checks.
- [x] Main-text claims distinguish the constrained carrier's negative boundary result from the mechanism and confirmatory evidence; no unsupported practical deployment win remains.
- [x] Quantitative claims are mapped in `docs/PAPER_NUMBER_TRACEABILITY.md` with source, filters, sample unit, denominator, and audit scope.
- [x] Seven main figures and the real-carrier boundary supplement are generated under `figures/paper_final_v3/` from the scoped renderer. All eight SVG files parse as XML.
- [x] Bibliography contains 12 unique, resolved, cited entries with no placeholder metadata.
- [x] Sample units are explicit and separate: N=100 attention/geometry evidence, N=100 held-out operator perturbations, and N=1000 per model for confirmatory and real-final classifier outcomes.
- [x] The activation-space C2 result and operator-space C2 control remain distinct claims with distinct sources and sample units.

## Open blockers

None identified by the final validators or the evidence-scope review.

## Validation artifacts

- `outputs/fungibility_real_final/validation_manifest.json` — authoritative real-final benchmark validation.
- `outputs/fungibility_real_final/paper_final_validation.json` — manuscript and figure publication gate.
