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

The complete requested real-final per-image schema (including predictions, logits, margins, and flips) has not been generated. However, the already-audited strict confirmatory raw output contains binary per-image correctness for the actual model methods. I reused those N=1,000 rows without rerunning them and wrote integer-count summaries to `outputs/fungibility_real_final/historical_confirmatory_accuracy_counts.csv`. The values below are **historical confirmatory Top-1 correct counts out of 1,000**, not a completed `real_accuracy_summary.csv` for the new benchmark.

| Architecture | Budget | Clean | Rand | Norm | Attention | ToMe | Group Mean | Oracle | Rank-16 | Rank-32 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| DeiT-Tiny | 98 | 679 | 638 | 653 | 665 | 676 | 673 | 679 | 678 | 678 |
| DeiT-Tiny | 49 | 679 | 611 | 593 | 625 | 665 | 682 | 680 | 682 | 682 |
| DeiT-Tiny | 32 | 679 | 586 | 505 | 575 | 658 | 665 | 671 | 671 | 679 |
| DeiT-Small | 98 | 761 | 739 | 751 | 759 | 765 | 765 | 761 | 763 | 761 |
| DeiT-Small | 49 | 761 | 716 | 717 | 738 | 768 | 763 | 760 | 758 | 760 |
| DeiT-Small | 32 | 761 | 711 | 642 | 716 | 764 | 764 | 758 | 765 | 765 |
| ViT-B/16 | 98 | 761 | 733 | 728 | 737 | 744 | 751 | 758 | 756 | 756 |
| ViT-B/16 | 49 | 761 | 705 | 678 | 688 | 729 | 746 | 752 | 748 | 751 |
| ViT-B/16 | 32 | 761 | 692 | 583 | 628 | 730 | 732 | 744 | 737 | 742 |
| DINOv2 ViT-S/14 | 128 | 788 | 760 | 743 | 771 | 762 | 782 | 790 | 786 | 784 |
| DINOv2 ViT-S/14 | 64 | 788 | 696 | 640 | 678 | 737 | 752 | 771 | 756 | 753 |
| DINOv2 ViT-S/14 | 42 | 788 | 615 | 562 | 603 | 694 | 722 | 735 | 732 | 730 |

Columns abbreviate Random Pruning, Norm Pruning, Attention Pruning, ToMe (BSM), Group-Mean Merging, Operator-Aware (Oracle), Operator-Aware (Rank-16), and Operator-Aware (Rank-32), respectively. Values are direct sums of the raw binary `top1_acc` field, with one row per image/method/budget; Clean sums one distinct `clean_correct` row per image. The source manifest records N=1,000, eval seed 9201, and the strict confirmatory report identifies the real-model execution protocol.

**UNMEASURED:** new real-final Clean, Random/Norm/Attention Pruning, tested ToMe, Hybrid Group Mean, Static Feature-PCA q=16/q=32, and Selective Feature-PCA classification metrics across the requested budgets. Historical Hybrid Group Mean, static carrier, and selective-gate metrics are not present in the confirmatory raw output.

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

**FAIL (4/12 assertions PASS).** Required real-final outputs and raw traceability are absent, so the 12 publication assertions do not pass. The recorded results are in `outputs/fungibility_real_final/validation_manifest.json`; no overall PASS is claimed. See `outputs/fungibility_real_final/validation_manifest.json`.

## UNMEASURED

- New per-image logits, predictions, margins, flips, and integer-count Top-1 for all requested real-final methods, architectures, and budgets.
- New static carrier and calibration-derived selective-gate downstream classification evaluation.
- Actual pretrained-model end-to-end throughput and latency with required batch sizes and timing metadata.
- Accuracy-throughput and accuracy-latency frontiers from those new real measurements.
- Regenerated `figures/paper_final_v3/` empirical accuracy/runtime figures.
- Full 12-assertion final publication validation.

## FINAL COMMIT SHA

Audit deliverables committed on canonical `main`; final commit SHA is in the delivery response.

## PUSH STATUS

Push status is reported in the delivery response after remote verification.
