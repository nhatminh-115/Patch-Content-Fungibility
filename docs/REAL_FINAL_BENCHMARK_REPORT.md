# Real Final Benchmark Report

**Measurement status:** actual-model accuracy and throughput runs complete; publication validator **FAIL (11/12)** because the existing paper-facing documents still cite historical proxy-consolidation tables. The six gated paper files and empirical figures were left untouched. No benchmark result below is inferred from operator error.

## Protocol and provenance

Four pretrained checkpoints were evaluated on the same 1,000 held-out ImageNet images per architecture (evaluation seed 9201), with 500 separate calibration images per architecture (calibration seed 7101). No calibration/evaluation image overlap was found. Accuracy runs used FP32 actual prefix/suffix forwards, actual classifier readout, and multiplicity-aware carrier collapse. Clean parity against each model's normal `forward` was 0 maximum absolute logit error on the parity input. The reusable carrier path also passed the runner's identity/forward parity check before measurement.

Static q=16/q=32 PCA bases and alpha parameters were derived from calibration-only actual-model targets. Selective thresholds were frozen from calibration clean-prefix residual-risk scores; evaluation labels and evaluation-set ranking were not used. The accuracy run covered Clean, Hybrid Group Mean, static q=16/q=32, and selective q16 target rates 20/30/50 across every requested architecture and budget. `real_accuracy_per_image.csv` carries prediction, integer correctness, flips, real-logit L2, and true-class margins. Compressed logits are saved per architecture in NPZ files. Top-1 is always `100 * correct_count / 1000`.

Exact image hashes, split IDs, labels, seeds, and preprocessing by architecture are in `outputs/fungibility_real_final/sample_manifest.csv`. DeiT Tiny/Small and DINOv2 use Resize 256 bicubic, CenterCrop 224, ImageNet normalization; ViT-B/16 AugReg uses Resize 248 bicubic, CenterCrop 224, normalization mean/std 0.5. Model state hashes and run details are in `measurement_manifest.json`.

## Real static carrier classification

Correct counts out of 1,000; parenthesized values are Top-1 percent.

| Architecture | Budget | Hybrid Group Mean | Static q=16 | Static q=32 |
|---|---:|---:|---:|---:|
| DeiT-Tiny | 98 | 679 (67.9) | 664 (66.4) | 665 (66.5) |
| DeiT-Tiny | 49 | 639 (63.9) | 637 (63.7) | 644 (64.4) |
| DeiT-Tiny | 32 | 618 (61.8) | 616 (61.6) | 619 (61.9) |
| DeiT-Small | 98 | 764 (76.4) | 763 (76.3) | 760 (76.0) |
| DeiT-Small | 49 | 755 (75.5) | 740 (74.0) | 740 (74.0) |
| DeiT-Small | 32 | 731 (73.1) | 722 (72.2) | 718 (71.8) |
| ViT-B/16 AugReg | 98 | 736 (73.6) | 737 (73.7) | 735 (73.5) |
| ViT-B/16 AugReg | 49 | 712 (71.2) | 719 (71.9) | 716 (71.6) |
| ViT-B/16 AugReg | 32 | 682 (68.2) | 684 (68.4) | 683 (68.3) |
| DINOv2 ViT-S/14 | 128 | 754 (75.4) | 749 (74.9) | 759 (75.9) |
| DINOv2 ViT-S/14 | 64 | 691 (69.1) | 684 (68.4) | 693 (69.3) |
| DINOv2 ViT-S/14 | 42 | 613 (61.3) | 568 (56.8) | 570 (57.0) |

Neither static carrier consistently improves real classification over Group Mean. At the most aggressive DINOv2 budget, q16 loses 45 correct images and q32 loses 43. Across other settings, differences are small and mixed in sign.

## Functional-to-behavioral translation

Operator-space improvements do not reliably translate into better classifier behavior. Paired q16-versus-Group-Mean changes range from small gains/losses on DeiT and ViT-B to a clear DINOv2 failure at budget 42: q16 changes Top-1 by -4.5 percentage points, increases mean logit L2 by 4.336, increases mean margin damage by 0.384, rescues 67 Group-Mean errors but introduces 108 new errors (paired McNemar p=0.000447). q32 at the same setting is -4.3 pp, +3.180 logit L2, +0.284 margin damage, with 64 rescued and 113 introduced (p=0.000811).

There are isolated positive cases, such as ViT-B budget 32 where q16 is +0.2 pp and reduces mean logit L2 by 0.304 and mean margin damage by 0.079. Those do not establish a general benefit. Full paired q16/q32 comparisons against Group Mean and each other, including tests and rescued/introduced flips, are in `real_static_carrier_ablation.csv`.

## Selective gate

Thresholds were fixed using calibration data. For target-30 q16, the threshold / held-out activation rate / correct count were:

| Architecture | Budget | Threshold | Activation | Correct / 1,000 |
|---|---:|---:|---:|---:|
| DeiT-Tiny | 98 / 49 / 32 | .474573 / .550454 / .587435 | 30.8% / 33.1% / 33.2% | 665 / 640 / 626 |
| DeiT-Small | 98 / 49 / 32 | .519415 / .598428 / .632308 | 27.0% / 29.1% / 31.0% | 758 / 746 / 728 |
| ViT-B/16 AugReg | 98 / 49 / 32 | .575423 / .660380 / .689265 | 31.4% / 31.7% / 27.2% | 735 / 716 / 682 |
| DINOv2 ViT-S/14 | 128 / 64 / 42 | .470309 / .542653 / .578412 | 43.1% / 47.4% / 43.6% | 756 / 687 / 585 |

The calibration target rate is approximate; realized rates vary by held-out architecture/budget. At budget 42, target-30 selective DINOv2 is 28 images worse than Group Mean (585 vs 613). The gate is not a consistent accuracy improvement. All 20/30/50 targets are reported in `real_selective_gate_summary.csv`.

## Actual throughput and Pareto frontier

Throughput used actual pretrained-model and compression forwards, FP32, CUDA events, 50 warmups, 100 measured iterations, synchronization, and batch sizes 1/8/16/32/64. GPU: NVIDIA GeForce RTX 5070 Laptop GPU. Full quartile dispersion, memory, callable/checkpoint IDs, software versions, and attention settings are in `real_throughput_raw.csv`.

Selected batch-1 and batch-64 results (batch latency; images/s):

| Architecture | Method | BS=1 | BS=64 |
|---|---|---:|---:|
| DeiT-Tiny | Clean | 7.58 ms; 131.9 | 26.69 ms; 2397.7 |
| DeiT-Tiny | Group Mean | 13.83 ms; 72.3 | 27.76 ms; 2305.5 |
| DeiT-Tiny | q16 / q32 | 15.12 / 15.71 ms; 66.1 / 63.7 | 34.66 / 47.61 ms; 1846.6 / 1344.4 |
| DeiT-Small | Clean | 7.48 ms; 133.6 | 78.74 ms; 812.8 |
| DeiT-Small | Group Mean | 14.01 ms; 71.4 | 70.60 ms; 906.5 |
| ViT-B/16 AugReg | Clean | 7.30 ms; 137.0 | 267.66 ms; 239.1 |
| ViT-B/16 AugReg | Group Mean | 14.26 ms; 70.1 | 215.39 ms; 297.1 |
| DINOv2 ViT-S/14 | Clean | 8.40 ms; 119.1 | 112.89 ms; 566.9 |
| DINOv2 ViT-S/14 | Group Mean | 16.92 ms; 59.1 | 100.09 ms; 639.4 |

At batch 1, Clean is fastest for all architectures. At batch 64, Group Mean is faster than Clean for DeiT-Small, ViT-B, and DINOv2, while Clean is faster for DeiT-Tiny. The full accuracy-throughput Pareto computation uses the measured target-50% budget accuracy and each measured batch size. The frontier is: DINOv2 Clean at batch 1/8/16, Clean and Group Mean at 32/64; DeiT-Small Clean and Group Mean at 1/8/16, Group Mean at 32/64; DeiT-Tiny Clean at every batch; ViT-B Clean at 1 and Clean/Group Mean/q16 at 8/16/32/64. q32 and selective q16 are not on any measured frontier.

## Validation and paper status

The strict validator passes 11 of 12 assertions. Checks for generator integrity, real integer-count provenance, timing metadata, disjoint splits, known sample sizes, confirmatory N=1,000, no deployable eval-top-k gate, and the draft-edit gate pass. Check 10 fails because six existing paper-facing files still cite proxy CSVs under `fungibility_final_consolidation/`:

- `docs/PAPER_DRAFT.md`
- `docs/PAPER_FINAL_CLAIMS_TABLE.md`
- `docs/PAPER_FINAL_AUDIT.md`
- `docs/PAPER_FINAL_EXPERIMENT_SUMMARY.md`
- `docs/PAPER_NUMBER_TRACEABILITY.md`
- `docs/PAPER_RECONCILIATION_REPORT.md`

Those files and `figures/paper_final_v3/` were left untouched. The repository's strict gate requires all 12 checks to pass before paper edits, while check 10 can only be cleared by repairing the cited paper files; an earlier attempt to weaken that gate was rejected by automatic review. The validation manifest records the exact failing assertion. The empirical benchmark is complete; publication validation and paper repair remain gated.

## Historical evidence kept separate

`historical_confirmatory_accuracy_counts.csv` preserves the existing N=1,000 confirmatory counts for Random, Norm, Attention Pruning, ToMe, Group Mean, Operator Oracle, and Rank-16/32 Oracle. It is not mixed with the new static carrier or selective inference results. Historical proxy consolidation accuracy/timing remains excluded from the measurements above.

## Unmeasured

- No requested carrier accuracy, held-out activation-rate, or throughput row remains unmeasured.
- Paper repair and regenerated `figures/paper_final_v3/` remain incomplete because validation check 10 has not passed under the enforced all-checks paper-edit gate.
