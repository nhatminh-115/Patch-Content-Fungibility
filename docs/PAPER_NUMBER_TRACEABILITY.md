# Paper Number Traceability Matrix

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Date:** October 7, 2026  
**Status:** Source repair in progress; PAPER_DRAFT is intentionally unchanged
**Commit Reference:** `db9f460`  

This matrix records verified sources and flags legacy draft values that must be replaced in the subsequent manuscript-lockdown task. Historical consolidation accuracy/runtime metrics are withdrawn; surviving consolidation measurements are explicitly limited to operator-space evidence.

---

## 1. Abstract & Introduction Numbers

| Paper Location | Claim / Metric | Paper Value | Source File | Filter / Row | Sample Size | Audit Status |
| :--- | :--- | :---: | :--- | :--- | :---: | :---: |
| **Abstract** | Validation image sample size | $N=1000$ | `configs/v0_benchmark_config.json` | `val_samples: 1000` | $N=1000$ | **CONFIRMED** |
| **Abstract** | Depth 8 Centroid Margin Recovery | $>93\%$ (93.8% DeiT-T, 97.5% DeiT-S, 93.4% DINOv2) | `docs/DELTA_V0_5_REPORT.md` | Table 1 (Depth 8, Centroid) | $N=1000$ | **CONFIRMED** |
| **Abstract** | Top-1 Accuracy drop under 25% replacement | 1–2 pp | `docs/DELTA_V0_5_REPORT.md` | Table 1 (Clean vs Centroid) | $N=1000$ | **CONFIRMED** |
| **Abstract** | Coordinate permutation / sign flip damage | 25–74 pp drop | `pca_control_ablation.csv` | DeiT-S (76.2% $\to$ 36.4% / 21.2%), DINOv2 (71.4% $\to$ 0.1%) | $N=1000$ | **CONFIRMED** |
| **Abstract** | Diversity injection threshold | $k \ge 4$ | `outputs/fungibility_v0_7_figures/` | Rank-$k$ diversity sweep | $N=1000$ | **CONFIRMED** |
| **Abstract** | Random basis control $p$-values | All $p < 10^{-25}$ | `final_random_basis_control.csv` | Rows 0, 2, 4, 6 ($q=16$) | $N=100$, 25 seeds | **AUDITED** |
| **Abstract** | Random basis control effect sizes | $d \in [1.46, 2.66]$ | `final_random_basis_control.csv` | DeiT-T (1.46), ViT-B (1.77), DINOv2 (1.59), DeiT-S (2.66) | $N=100$, 25 seeds | **AUDITED** |
| **Abstract** | Stabilized Oracle Recovery ($q=1$) | $17.5\%$ | `docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md` | Section 2 ($q$-scaling summary) | $N=100$ | **AUDITED** |
| **Abstract** | Stabilized Oracle Recovery ($q=16$) | $47.4\%$ | `final_q_ablation.csv` / audit | $(12.5234 - 6.6023)/(12.5038) = 47.35\%$ | $N=100$ | **AUDITED** |
| **Abstract** | Stabilized Oracle Recovery ($q=64$) | $92.2\%$ | `final_q_ablation.csv` / audit | $(12.5234 - 0.9937)/(12.5038) = 92.21\%$ | $N=100$ | **AUDITED** |
| **Abstract** | Static $\bar{\alpha}$ Recovery of Restricted Oracle | $54.91\%$ | `final_q_ablation.csv` | `deit_small, q=16, recovery_vs_restricted_oracle_pct` | $N=100$ | **AUDITED** |
| **Abstract (legacy claim; withdraw)** | Isolated operator overhead | Sub-0.25 ms/image ($0.12–0.23$) | No valid isolated-overhead measurement; real full-call timing is `outputs/fungibility_real_final/real_throughput_summary.csv` | DeiT-Small, BS=64, budget=98: Clean 1.230, Group Mean 1.103, q16 1.329, q32 1.821, selective q16 target30 1.339 ms/image | 50 warmups + 100 measured iterations per timing row | **WITHDRAWN; full-call timings do not isolate operator overhead** |
| **Abstract (legacy value; replace)** | Selective q16 target30 throughput on DeiT-Small | 746.8 img/s | `outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv` | `architecture == "DeiT-Small" & budget_tokens == 98 & batch_size == 64 & method == "Selective Feature-PCA q16 target30"` | Accuracy N=1,000; timing 100 iterations at BS=64 | **CONFIRMED; not Pareto-optimal** |
| **Abstract (legacy value; replace)** | Selective q16 target30 Top-1 on DeiT-Small | 758/1,000 = 75.8% | `outputs/fungibility_real_final/real_accuracy_summary.csv` | `architecture == "DeiT-Small" & budget_tokens == 98 & method == "Selective Feature-PCA q16 target30"`; count is integer sum of per-image `correct` | N=1,000 held-out images | **CONFIRMED; actual-model logits and predictions** |
| **§1 (Intro)** | DeiT-S Rank-$k$ Diversity gain | $+37.08\text{ pp}$ | `outputs/fungibility_v0_7_figures/` | Complete stream replacement sweep | $N=1000$ | **CONFIRMED** |
| **§1 (Intro)** | Local 1-block singular vector rotation | $\ge 68.4^\circ$ | `outputs/fungibility_v1_figures/` | Subspace drift analysis | $N=1000$ | **CONFIRMED** |

---

## 2. Table 1: Depthwise Emergence of Fungibility (§4.1)

**Source File:** `docs/DELTA_V0_5_REPORT.md` & `outputs/fungibility_v0_figures/`  
**Sample Size:** $N=1000$ validation images, 500 calibration images  
**Protocol:** 25% spatial patch replacement at specified depth, clean weights/CLS frozen.

| Row Architecture | Interv. Depth | Clean Top-1 | Zero Top-1 | Centroid Top-1 | Margin Recovery | Logit $L_2$ (Zero $\to$ Centroid) | Traceability Row |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **DeiT-Tiny** | Depth 8 | 72.2% | 24.6% | 71.0% | 93.8% | 18.4 $\to$ 2.8 | `DELTA_V0_5_REPORT.md` Table 1, Row 1 |
| **DeiT-Small** | Depth 8 | 79.8% | 32.1% | 78.1% | 97.5% | 22.6 $\to$ 3.1 | `DELTA_V0_5_REPORT.md` Table 1, Row 2 |
| **ViT-Base** | Depth 8 | 81.8% | 41.2% | 80.4% | 81.8% | 24.1 $\to$ 4.7 | `FUNGIBILITY_V1_REPORT.md` Table 2, Row 3 |
| **DINOv2** | Depth 9 | 78.8% | 4.5% | 74.1% | 93.4% | 31.2 $\to$ 5.2 | `DELTA_V0_5_REPORT.md` Table 1, Row 4 |

---

## 3. Table 2: Geometric Control Ablations (§5.1)

**Source File:** `outputs/fungibility_implicit_carrier_operator_audit/pca_control_ablation.csv`  
**Sample Size:** $N=1000$ validation images (DeiT-S, ViT-B, DINOv2 at Depth 8, $\rho = 0.50$).

| Surrogate Intervention | DeiT-Small Top-1 | ViT-Base Top-1 | DINOv2 Top-1 | Downstream $\|JE\|$ Norm | Source File / Filter |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Clean Baseline** | 79.8% | 81.8% | 78.8% | 0.00 | Ground Truth Reference |
| **Calibration Centroid ($\mu$)** | 76.2% | 75.8% | 71.4% | 12.52 | `pca_control_ablation.csv`, `method == "centroid"` |
| **Coordinate Permutation ($\Pi \mu$)** | 36.4% | 38.0% | 31.8% | 28.64 | `pca_control_ablation.csv`, `method == "coord_perm"` |
| **Sign Inversion ($-\mu$)** | 21.2% | 27.9% | 0.1% | 34.18 | `pca_control_ablation.csv`, `method == "sign_inv"` |
| **Matched Random Unit Vector** | 18.5% | 22.4% | 0.2% | 36.90 | `pca_control_ablation.csv`, `method == "rand_unit"` |
| **Zero Replacement ($\mathbf{0}$)** | 14.2% | 12.8% | 1.8% | 42.15 | `pca_control_ablation.csv`, `method == "zero"` |

---

## 4. Table 3: Controlled Random Basis Interventions (§8.2)

**Source File:** `outputs/fungibility_final_consolidation/final_random_basis_control.csv`  
**Sample Size:** $N=100$ held-out evaluation images, 25 random orthonormal seeds per architecture, $q=16$.

| Architecture | Feature-PCA $\|JE\|$ | Random Mean $\|JE\|$ | Random Std | Advantage | $t$-stat | $p$-value | Cohen's $d$ | CSV Row Index |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | **2.6029** | 3.2107 | 0.0202 | 0.6078 | -14.55 | $2.45 \times 10^{-26}$ | 1.46 | Row 0 (`architecture == "deit_tiny" & q == 16`) |
| **DeiT-Small** | **6.6023** | 10.1829 | 0.0671 | 3.5806 | -26.49 | $9.96 \times 10^{-47}$ | 2.66 | Row 2 (`architecture == "deit_small" & q == 16`) |
| **ViT-Base** | **11.8086** | 16.0150 | 0.0737 | 4.2064 | -17.56 | $3.51 \times 10^{-32}$ | 1.77 | Row 4 (`architecture == "vit_base" & q == 16`) |
| **DINOv2** | **0.4651** | 0.6042 | 0.0039 | 0.1391 | -15.82 | $7.29 \times 10^{-29}$ | 1.59 | Row 6 (`architecture == "dinov2" & q == 16`) |

---

## 5. Table 4: Audited q-Scaling of the Stabilized Carrier Oracle (§8.3) — Operator-Space Evidence Only

**Source:** `outputs/fungibility_final_consolidation/final_q_ablation.csv` and `docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md`. These audited fields are operator-space $\|JE\|$ measurements; no Top-1 or runtime claim is taken from this historical consolidation file. **Architecture:** DeiT-Small, depth 8, 50% budget, N=100 held-out operator-space images.

Recovery denominator: $(\|JE\|_{GM}-\|JE\|_{q})/(\|JE\|_{GM}-\|JE\|_{stabilized\ full\ oracle})$. This is not the distinct full-J compression-benefit denominator used for the >98% low-rank claim, nor the restricted-oracle denominator used for static-alpha recovery.

| Method / dimension | $\|JE\|$ | Gain vs. Group Mean | Recovery | Source filter |
| :--- | :---: | :---: | :---: | :--- |
| Group Mean ($q=0$) | 12.5234 | 0.0000 | 0.0% | DeiT-Small, depth 8, 50% budget |
| Restricted Oracle ($q=8$) | 8.0663 | 4.4571 | 35.6% | `q == 8` |
| Restricted Oracle ($q=16$) | 6.6023 | 5.9211 | 47.4% | `q == 16` |
| Restricted Oracle ($q=32$) | 3.5164 | 9.0070 | 72.0% | `q == 32` |
| Restricted Oracle ($q=64$) | 0.9937 | 11.5297 | 92.2% | `q == 64` |
| Stabilized Full Oracle ($r=32$) | 0.0196 | 12.5038 | 100.0% | `stabilized_full_oracle_je` |

---

## 6. Table 5: Real Full-Model Runtime (Replaces Withdrawn Isolated-Overhead Claim)

The old 0.12–0.23 ms/image statement was an operator-only figure from a proxy timing artifact and is withdrawn. The real-final timing measures complete model calls, including the actual prefix, carrier transformation, suffix, and readout. It does **not** separately time operator overhead. Timing protocol: FP32, 50 warmups, 100 measured CUDA-event iterations with synchronization, NVIDIA GeForce RTX 5070 Laptop GPU; exact device/software/callable metadata is in `outputs/fungibility_real_final/real_throughput_raw.csv`. Values below are BS=64, target-50% budget; latency is per image.

| Architecture | Method | Budget | Accuracy count / Top-1 (N=1,000) | ms/image | img/s | Frontier at BS=64 | Exact source filter |
| :--- | :--- | ---: | :---: | ---: | ---: | :---: | :--- |
| DeiT-Tiny | Clean | 98 | 679/1,000 (67.9%) | 0.417 | 2397.7 | True | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| DeiT-Tiny | Hybrid Group Mean | 98 | 664/1,000 (66.4%) | 0.434 | 2305.5 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DeiT-Tiny | Static Feature-PCA q=16 | 98 | 662/1,000 (66.2%) | 0.542 | 1846.6 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DeiT-Tiny | Static Feature-PCA q=32 | 98 | 665/1,000 (66.5%) | 0.744 | 1344.4 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DeiT-Tiny | Selective Feature-PCA q16 target30 | 98 | 665/1,000 (66.5%) | 0.546 | 1831.3 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| DeiT-Small | Clean | 98 | 761/1,000 (76.1%) | 1.230 | 812.8 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| DeiT-Small | Hybrid Group Mean | 98 | 764/1,000 (76.4%) | 1.103 | 906.5 | True | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DeiT-Small | Static Feature-PCA q=16 | 98 | 763/1,000 (76.3%) | 1.329 | 752.3 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DeiT-Small | Static Feature-PCA q=32 | 98 | 760/1,000 (76.0%) | 1.821 | 549.3 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DeiT-Small | Selective Feature-PCA q16 target30 | 98 | 758/1,000 (75.8%) | 1.339 | 746.8 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| ViT-B/16 AugReg | Clean | 98 | 761/1,000 (76.1%) | 4.182 | 239.1 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| ViT-B/16 AugReg | Hybrid Group Mean | 98 | 736/1,000 (73.6%) | 3.365 | 297.1 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| ViT-B/16 AugReg | Static Feature-PCA q=16 | 98 | 737/1,000 (73.7%) | 3.798 | 263.3 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| ViT-B/16 AugReg | Static Feature-PCA q=32 | 98 | 735/1,000 (73.5%) | 4.722 | 211.8 | False | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| ViT-B/16 AugReg | Selective Feature-PCA q16 target30 | 98 | 735/1,000 (73.5%) | 3.793 | 263.6 | False | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| DINOv2 ViT-S/14 | Clean | 128 | 788/1,000 (78.8%) | 1.764 | 566.9 | True | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Clean' & batch_size == 64` |
| DINOv2 ViT-S/14 | Hybrid Group Mean | 128 | 754/1,000 (75.4%) | 1.564 | 639.4 | True | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DINOv2 ViT-S/14 | Static Feature-PCA q=16 | 128 | 749/1,000 (74.9%) | 1.869 | 535.1 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DINOv2 ViT-S/14 | Static Feature-PCA q=32 | 128 | 759/1,000 (75.9%) | 2.391 | 418.2 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DINOv2 ViT-S/14 | Selective Feature-PCA q16 target30 | 128 | 756/1,000 (75.6%) | 1.878 | 532.4 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |

**Raw and generating sources:** `outputs/fungibility_real_final/real_accuracy_summary.csv` (accuracy filter by architecture, budget, method); `outputs/fungibility_real_final/real_throughput_raw.csv` and `real_throughput_summary.csv` (timing filter by architecture, method, batch_size=64); `outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv` (formal frontier flag); scripts `scripts/run_real_final_accuracy.py`, `scripts/run_real_final_throughput.py`, and `scripts/build_real_final_frontier.py`. Accuracy provenance is 1,000 held-out images per architecture; timing provenance is 100 measured iterations per method/batch.

---

## 7. Table 6: Real Accuracy-Throughput Frontier at BS=64

The formal comparison is within architecture and batch size, at each model's 50% token budget. `pareto_optimal` uses measured N=1,000 Top-1 and measured images/s; no proxy results are included.

| Architecture | Method | Budget | Correct / N (Top-1) | ms/image | img/s | Pareto-optimal | Exact source filter |
| :--- | :--- | ---: | :---: | ---: | ---: | :---: | :--- |
| DeiT-Tiny | Clean | 98 | 679/1,000 (67.9%) | 0.417 | 2397.7 | True | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| DeiT-Tiny | Hybrid Group Mean | 98 | 664/1,000 (66.4%) | 0.434 | 2305.5 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DeiT-Tiny | Static Feature-PCA q=16 | 98 | 662/1,000 (66.2%) | 0.542 | 1846.6 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DeiT-Tiny | Static Feature-PCA q=32 | 98 | 665/1,000 (66.5%) | 0.744 | 1344.4 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DeiT-Tiny | Selective Feature-PCA q16 target30 | 98 | 665/1,000 (66.5%) | 0.546 | 1831.3 | False | `architecture == 'DeiT-Tiny' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| DeiT-Small | Clean | 98 | 761/1,000 (76.1%) | 1.230 | 812.8 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| DeiT-Small | Hybrid Group Mean | 98 | 764/1,000 (76.4%) | 1.103 | 906.5 | True | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DeiT-Small | Static Feature-PCA q=16 | 98 | 763/1,000 (76.3%) | 1.329 | 752.3 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DeiT-Small | Static Feature-PCA q=32 | 98 | 760/1,000 (76.0%) | 1.821 | 549.3 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DeiT-Small | Selective Feature-PCA q16 target30 | 98 | 758/1,000 (75.8%) | 1.339 | 746.8 | False | `architecture == 'DeiT-Small' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| ViT-B/16 AugReg | Clean | 98 | 761/1,000 (76.1%) | 4.182 | 239.1 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Clean' & batch_size == 64` |
| ViT-B/16 AugReg | Hybrid Group Mean | 98 | 736/1,000 (73.6%) | 3.365 | 297.1 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Hybrid Group Mean' & batch_size == 64` |
| ViT-B/16 AugReg | Static Feature-PCA q=16 | 98 | 737/1,000 (73.7%) | 3.798 | 263.3 | True | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| ViT-B/16 AugReg | Static Feature-PCA q=32 | 98 | 735/1,000 (73.5%) | 4.722 | 211.8 | False | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| ViT-B/16 AugReg | Selective Feature-PCA q16 target30 | 98 | 735/1,000 (73.5%) | 3.793 | 263.6 | False | `architecture == 'ViT-B/16 AugReg' & budget_tokens == 98 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |
| DINOv2 ViT-S/14 | Clean | 128 | 788/1,000 (78.8%) | 1.764 | 566.9 | True | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Clean' & batch_size == 64` |
| DINOv2 ViT-S/14 | Hybrid Group Mean | 128 | 754/1,000 (75.4%) | 1.564 | 639.4 | True | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Hybrid Group Mean' & batch_size == 64` |
| DINOv2 ViT-S/14 | Static Feature-PCA q=16 | 128 | 749/1,000 (74.9%) | 1.869 | 535.1 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Static Feature-PCA q=16' & batch_size == 64` |
| DINOv2 ViT-S/14 | Static Feature-PCA q=32 | 128 | 759/1,000 (75.9%) | 2.391 | 418.2 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Static Feature-PCA q=32' & batch_size == 64` |
| DINOv2 ViT-S/14 | Selective Feature-PCA q16 target30 | 128 | 756/1,000 (75.6%) | 1.878 | 532.4 | False | `architecture == 'DINOv2 ViT-S/14' & budget_tokens == 128 & method == 'Selective Feature-PCA q16 target30' & batch_size == 64` |

The measured frontier contains a narrow added static q16 point on ViT-B/16 AugReg at BS=16/32/64. At BS=64, q16 obtains 737/1,000 (73.7%) at 263.3 img/s, between Clean (761/1,000; 76.1%; 239.1 img/s) and Group Mean (736/1,000; 73.6%; 297.1 img/s). q32 and selective q16 are not on the measured frontier. Clean dominates all tested methods on DeiT-Tiny at BS=64; Group Mean is the frontier method on DeiT-Small, and Clean plus Group Mean are frontier methods on DINOv2. The full batch-size result is in `outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv`.

---

## 8. Figure Traceability Mapping

| Figure Asset | Caption / Concept | Underlying Data Source | Scripts Generating Asset | Audit Status |
| :--- | :--- | :--- | :--- | :---: |
| `figures/paper_final_v2/figure1_conceptual_overview.png` | Causal substitution framework | Conceptual diagram & benchmark metrics | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure2_depthwise_fungibility.png` | Depthwise emergence of fungibility | `outputs/fungibility_v0_figures/` | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure3_geometry_diversity_constraints.png` | Geometric controls and diversity collapse | `pca_control_ablation.csv`, $N=1000$ | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure4_functional_geometry.png` | Functional geometry and attention cancellation | `outputs/fungibility_v1_figures/` | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure5_local_vs_end_to_end_jacobian.png` | Failure of local 1-block geometry | Local vs downstream singular angle drift | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure6_operator_aware_compression_frontier.png` | Legacy compression accuracy frontier | Withdrawn: based on invalidated proxy accuracy | — | **NOT VALID FOR PUBLICATION** |
| `figures/paper_final_v2/figure7_carrier_space_formulation.png` | $q$-scaling and static calibration $\bar{\alpha}$ | `final_q_ablation.csv` | `scripts/run_final_consolidation_benchmark.py` | **VERIFIED** |
| `figures/paper_final_v2/figure8_accuracy_throughput_frontier.png` | Legacy accuracy-throughput frontier | Withdrawn: proxy accuracy and toy timing; see real-final frontier CSV for valid measurements | — | **NOT VALID FOR PUBLICATION** |
