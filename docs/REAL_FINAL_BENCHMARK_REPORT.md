# Real Final Benchmark Report

**Status: INCOMPLETE — real-final validation has not passed.**  
**Repository commit at audit start:** `14cf343cb0b72a21c68c642142d0adaf2346b717`.

## PROXY AUDIT

The historical consolidation accuracy table is invalid for paper accuracy claims. It uses hard-coded clean accuracy and derives Top-1, logit L2, and prediction flips from JE using fixed coefficients. Its pruning and ToMe JE values are also fixed multiples of Group Mean JE. The throughput table times random hidden states in a toy matrix loop, not a pretrained architecture. Consequently the historical Pareto table and figures based on these metrics are invalid for paper use.

Genuine saved-activation/Jacobian calculations in the same historical run are operator-space measurements only. The detailed per-column classification is in `docs/FINAL_PROXY_ARTIFACT_AUDIT.md`.

## SAMPLE-SIZE AUDIT

- Functional Geometry: N=100 images.
- Attention Causal Audit: N=100 evaluation images.
- Multi-block Operator: N=100 held-out perturbations.
- Strict Confirmatory Operator Compression: N=1,000 held-out ImageNet validation images per architecture, eval seed 9201; preserve this result at N=1,000.

The source-backed map is `docs/PAPER_SAMPLE_SIZE_MAP.md`.

## REAL ACCURACY

No new `outputs/fungibility_real_final/real_accuracy_per_image.csv` or summary exists, so no new real-final Top-1/correct-count results are reported. Historical strict confirmatory outputs remain separate and report actual model execution at N=1,000; they are not repackaged here because their raw schema does not include the requested saved logits and full per-image fields.

**UNMEASURED:** new real-final Clean, Random/Norm/Attention Pruning, tested ToMe, Hybrid Group Mean, Static Feature-PCA q=16/q=32, and Selective Feature-PCA classification metrics across the requested budgets.

## STATIC CARRIER

Whether q=16/q=32 static Feature-PCA improves actual downstream model outputs over Group Mean is **UNMEASURED** in the required real-model evaluation. Historical `||JE||` values are not a substitute for that test.

## SELECTIVE GATE

A calibration-derived fixed threshold has not been evaluated on held-out real-model outputs. Activation rate, AUROC/AUPRC, classification effect, and throughput are **UNMEASURED**. Any historical evaluation-batch top-rate analysis is not evidence for a deployable fixed-threshold gate.

## REAL THROUGHPUT

No real-final timing run was completed. End-to-end model latency, throughput, dispersion, memory, compile mode, precision, and callable metadata are **UNMEASURED**. The historical toy timing values are excluded.

## PARETO

No new real accuracy-throughput or accuracy-latency frontier exists. Therefore no real-final frontier or dominance claim is made. Historical frontier claims based on the proxy consolidation do not survive this audit. Claims from the separately audited confirmatory report concern accuracy-token frontiers, not measured runtime Pareto dominance.

## OPERATOR-SPACE RESULTS

Historical `||JE||`, Feature-PCA versus matched random-basis comparisons, restricted carrier q-scaling, and stabilized oracle recovery are operator-space/functional-transmission results. They may be retained after exact source-row and target-manifest verification. None is empirical Top-1 unless an actual downstream classifier forward was executed. The (>98\%) claim in the confirmatory report refers to low-rank approximation of the full-J oracle compression benefit; keep that denominator explicit.

## PAPER REPAIR

`docs/PAPER_DRAFT.md` and the requested paper tables/reports were not edited because the real-final outputs and validation have not passed. Existing proxy-backed claims and figure references are flagged for repair; the draft is not certified final. The proxy historical directory was preserved.

## FINAL VALIDATION

**FAIL / NOT RUN TO PASS.** Required real-final outputs and raw traceability are absent, so the 12 publication assertions cannot pass. No PASS is claimed. See `outputs/fungibility_real_final/validation_manifest.json`.

## UNMEASURED

- New per-image logits, predictions, margins, flips, and integer-count Top-1 for all requested real-final methods, architectures, and budgets.
- New static carrier and calibration-derived selective-gate downstream classification evaluation.
- Actual pretrained-model end-to-end throughput and latency with required batch sizes and timing metadata.
- Accuracy-throughput and accuracy-latency frontiers from those new real measurements.
- Regenerated `figures/paper_final_v3/` empirical accuracy/runtime figures.
- Full 12-assertion final publication validation.

## FINAL COMMIT SHA

Pending commit.

## PUSH STATUS

Pending push to canonical `origin/main`.
