# Final Paper Experiment Summary: Patch Content Fungibility & Operator-Aware Carrier Correction

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Date:** October 7, 2026  
**Status:** Source correction in progress; manuscript draft remains pending lockdown
**Primary Outputs:** `outputs/fungibility_real_final/` (actual carrier accuracy/runtime); `outputs/fungibility_operator_compression_confirmatory/` (strict N=1,000 compression)
**Legacy Figures:** `figures/paper_final_v2/` are not treated as validated accuracy/runtime figures pending figure lockdown

---

## 1. Experimental Overview & Model Architectures

The empirical evaluation covers four diverse Vision Transformer models spanning supervised classification, self-supervised distillation, and self-supervised feature learning:

| Model Architecture | Parameter Count | Patch Grid $N$ | Hidden Dim $D$ | Attention Heads | Compression Depth $L_{\text{split}}$ | Token Budgets Evaluated |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** (`deit_tiny_patch16_224`) | 5.7M | 196 | 192 | 3 | Layer 8 / 12 | 98 (~50%), 49 (~25%), 32 (~16%) |
| **DeiT-Small** (`deit_small_patch16_224`) | 22.1M | 196 | 384 | 6 | Layer 8 / 12 | 98 (~50%), 49 (~25%), 32 (~16%) |
| **ViT-B/16** (`vit_base_patch16_224`) | 86.6M | 196 | 768 | 12 | Layer 7 / 12 | 98 (~50%), 49 (~25%), 32 (~16%) |
| **DINOv2 ViT-S/14** (`dinov2_vits14`) | 22.1M | 256 | 384 | 6 | Layer 8 / 12 | 128 (~50%), 64 (~25%), 42 (~16%) |

---

## 2. Static $q$-Ablation Across Architectures (Operator-Space Evidence Only)

The following audited quantities are $\|JE\|$ operator-space measurements from 100 held-out samples, not Top-1 or runtime evidence. Historical Top-1 fields are omitted. Source: `outputs/fungibility_final_consolidation/final_q_ablation.csv` plus `docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md`.

| Architecture | Budget | Baseline Group Mean $\|JE\|$ | Stabilized Full Oracle $\|JE\|$ | Static $\bar{\alpha}$ ($q=8$) | Static $\bar{\alpha}$ ($q=16$) | Static $\bar{\alpha}$ ($q=32$) | Static $\bar{\alpha}$ ($q=64$) | Full-Oracle $\|JE\|$ Gain Recovery ($q=16$) | Restricted-Oracle Gain Recovery ($q=16$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | 50% (98) | 4.1586 | 0.0067 | 3.7791 | 3.7532 | 3.6512 | 3.6192 | 9.76% | 26.06% |
| **DeiT-Small** | 50% (98) | 12.5234 | 0.0196 | 9.4336 | **9.2724** | 9.0642 | 9.0594 | **26.00%** | **54.91%** |
| **ViT-B/16** | 50% (98) | 18.5889 | 0.0278 | 17.2455 | **17.1633** | 17.1788 | 17.2940 | 7.68% | 21.03% |
| **DINOv2** | 50% (128) | 0.7220 | 0.0012 | 0.6481 | **0.6452** | 0.6342 | 0.6284 | 10.66% | 29.92% |

### Key Insights:
- $q=16$ provides the optimal Pareto point between error reduction and parameter/computation cost.
- Moving from $q=16$ to $q=64$ with static calibration yields only marginal additional gain ($9.27 \rightarrow 9.06$ on DeiT-Small) while increasing basis dimensions $4\text{x}$.
- Static $\bar{\alpha}$ captures **$54.91\%$** of the restricted oracle gain ($26.00\%$ of full oracle gain) on DeiT-Small with zero learned predictor FLOPs.

---

## 3. Matched Random Control Distribution (25 Seeds per Architecture)

Operator-space comparison only; these values do not establish real classification or runtime gains. Source: `outputs/fungibility_final_consolidation/final_random_basis_control.csv` ($N=100$ held-out operator-space images):

| Architecture | Subspace Dim ($q$) | Feature-PCA $\|JE\|$ | Random Bases Mean $\|JE\|$ | Random Bases Std | Paired $t$-stat | $p$-value | Cohen's $d$ Effect Size |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | $q=16$ | **2.6029** | 3.2107 | 0.0202 | -14.55 | $2.45 \times 10^{-26}$ | 1.46 |
| | $q=32$ | **1.2878** | 2.3586 | 0.0209 | -24.03 | $4.20 \times 10^{-43}$ | 2.42 |
| **DeiT-Small** | $q=16$ | **6.6023** | 10.1829 | 0.0671 | -26.49 | **$9.96 \times 10^{-47}$** | **2.66** |
| | $q=32$ | **3.5164** | 8.1902 | 0.0670 | -30.00 | **$1.72 \times 10^{-51}$** | **3.01** |
| **ViT-B/16** | $q=16$ | **11.8086** | 16.0150 | 0.0737 | -17.56 | $3.51 \times 10^{-32}$ | 1.77 |
| | $q=32$ | **6.5166** | 13.8614 | 0.1087 | -25.91 | $6.78 \times 10^{-46}$ | 2.60 |
| **DINOv2** | $q=16$ | **0.4651** | 0.6042 | 0.0039 | -15.82 | $7.29 \times 10^{-29}$ | 1.59 |
| | $q=32$ | **0.3003** | 0.5035 | 0.0042 | -17.93 | $7.36 \times 10^{-33}$ | 1.80 |

**Conclusion:** Across all models and tested dimensions ($q=16, 32$), Feature-PCA decisively outperforms matched random bases ($p < 10^{-25}$, Cohen's $d \in [1.46, 2.66]$ at $q=16$), supporting the functional relevance of learned feature covariance directions for token compression error correction.

---

## 4. Real End-to-End Accuracy and Throughput (BS=64, 50% Budget)

Actual held-out classification counts (N=1,000 per architecture) are joined to actual full-model timing. Timing uses FP32, 50 warmups, 100 measured CUDA-event iterations and synchronization on an NVIDIA GeForce RTX 5070 Laptop GPU. Per-image latency is the measured batch latency divided by 64. Outputs: `outputs/fungibility_real_final/real_accuracy_summary.csv`, `real_throughput_raw.csv`, `real_throughput_summary.csv`, and `real_accuracy_throughput_frontier.csv`; generation: `scripts/run_real_final_accuracy.py`, `scripts/run_real_final_throughput.py`, `scripts/build_real_final_frontier.py`.

| Architecture | Method | Budget | Correct / N (Top-1) | Latency (ms/image) | Throughput (img/s) | Pareto-optimal at BS=64 |
| :--- | :--- | ---: | :---: | ---: | ---: | :---: |
| DeiT-Tiny | Clean | 98 | 679/1,000 (67.9%) | 0.417 | 2397.7 | Yes |
| DeiT-Tiny | Hybrid Group Mean | 98 | 664/1,000 (66.4%) | 0.434 | 2305.5 | No |
| DeiT-Tiny | Static Feature-PCA q=16 | 98 | 662/1,000 (66.2%) | 0.542 | 1846.6 | No |
| DeiT-Tiny | Static Feature-PCA q=32 | 98 | 665/1,000 (66.5%) | 0.744 | 1344.4 | No |
| DeiT-Tiny | Selective Feature-PCA q16 target30 | 98 | 665/1,000 (66.5%) | 0.546 | 1831.3 | No |
| DeiT-Small | Clean | 98 | 761/1,000 (76.1%) | 1.230 | 812.8 | No |
| DeiT-Small | Hybrid Group Mean | 98 | 764/1,000 (76.4%) | 1.103 | 906.5 | Yes |
| DeiT-Small | Static Feature-PCA q=16 | 98 | 763/1,000 (76.3%) | 1.329 | 752.3 | No |
| DeiT-Small | Static Feature-PCA q=32 | 98 | 760/1,000 (76.0%) | 1.821 | 549.3 | No |
| DeiT-Small | Selective Feature-PCA q16 target30 | 98 | 758/1,000 (75.8%) | 1.339 | 746.8 | No |
| ViT-B/16 AugReg | Clean | 98 | 761/1,000 (76.1%) | 4.182 | 239.1 | Yes |
| ViT-B/16 AugReg | Hybrid Group Mean | 98 | 736/1,000 (73.6%) | 3.365 | 297.1 | Yes |
| ViT-B/16 AugReg | Static Feature-PCA q=16 | 98 | 737/1,000 (73.7%) | 3.798 | 263.3 | Yes |
| ViT-B/16 AugReg | Static Feature-PCA q=32 | 98 | 735/1,000 (73.5%) | 4.722 | 211.8 | No |
| ViT-B/16 AugReg | Selective Feature-PCA q16 target30 | 98 | 735/1,000 (73.5%) | 3.793 | 263.6 | No |
| DINOv2 ViT-S/14 | Clean | 128 | 788/1,000 (78.8%) | 1.764 | 566.9 | Yes |
| DINOv2 ViT-S/14 | Hybrid Group Mean | 128 | 754/1,000 (75.4%) | 1.564 | 639.4 | Yes |
| DINOv2 ViT-S/14 | Static Feature-PCA q=16 | 128 | 749/1,000 (74.9%) | 1.869 | 535.1 | No |
| DINOv2 ViT-S/14 | Static Feature-PCA q=32 | 128 | 759/1,000 (75.9%) | 2.391 | 418.2 | No |
| DINOv2 ViT-S/14 | Selective Feature-PCA q16 target30 | 128 | 756/1,000 (75.6%) | 1.878 | 532.4 | No |

The practical carrier result is mixed and mostly negative. At BS=64, static q16 adds one narrow non-dominated point for ViT-B/16 AugReg (budget 98): 737/1,000 (73.7%) at 263.3 img/s, between Clean (761/1,000; 76.1%; 239.1 img/s) and Group Mean (736/1,000; 73.6%; 297.1 img/s). Clean dominates all tested methods on DeiT-Tiny; Group Mean is the only carrier frontier method on DeiT-Small; Clean and Group Mean are frontier methods on DINOv2. Static q32 and selective q16 are not on this frontier. No proxy accuracy, toy timing, or unmeasured pruning/ToMe timing is included here.
