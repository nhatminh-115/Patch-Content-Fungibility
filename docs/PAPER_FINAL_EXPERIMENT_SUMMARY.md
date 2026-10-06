# Final Paper Experiment Summary: Patch Content Fungibility & Operator-Aware Carrier Correction

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Date:** October 7, 2026  
**Status:** Authoritative Post-Audit Release (Fully Reconciled)  
**Primary Outputs:** [`outputs/fungibility_final_consolidation/`](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_final_consolidation/)  
**Primary Figures:** [`figures/paper_final_v2/`](file:///d:/Study/Patch-Content-Fungibility/figures/paper_final_v2/)  

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

## 2. Static $q$-Ablation Across Architectures (Authoritative Final Consolidation)

Evaluating carrier correction across subspace dimensions $q \in \{8, 16, 32, 64\}$ against the properly stabilized full oracle reference ($\lambda = 10^{-3}$) on 100 held-out evaluation images (from `final_q_ablation.csv`):

| Architecture | Budget | Baseline Group Mean $\|JE\|$ | Stabilized Full Oracle $\|JE\|$ | Static $\bar{\alpha}$ ($q=8$) | Static $\bar{\alpha}$ ($q=16$) | Static $\bar{\alpha}$ ($q=32$) | Static $\bar{\alpha}$ ($q=64$) | Full Oracle Recovery ($q=16$) | Restricted Oracle Recovery ($q=16$) |
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

From `final_random_basis_control.csv` ($N=100$ held-out images):

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

## 4. End-to-End Accuracy vs. Throughput Frontier (BS=64, 50% Budget)

From `final_pareto_frontier.csv` (Authoritative Final Benchmark):

| Architecture | Method | Throughput (img/sec) | Latency (ms/img) | Speedup vs Clean | Top-1 Accuracy (%) | Top-1 Drop vs Clean | Frontier Characterization |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **DeiT-Tiny** | Clean | 11059.8 | 0.090 | 1.00x | 72.20% | 0.00 pp | Reference |
| | Attention Pruning | 14477.0 | 0.069 | 1.31x | 70.24% | -1.96 pp | High speed / lower acc |
| | ToMe | 14377.8 | 0.070 | 1.30x | 70.86% | -1.34 pp | High speed / moderate acc |
| | Hybrid Group Mean | 14076.3 | 0.071 | 1.27x | 71.16% | -1.04 pp | High speed baseline |
| | **Selective Restricted (30%)** | **11967.2** | **0.084** | **1.08x** | **71.28%** | **-0.92 pp** | **Accuracy Tradeoff (+0.12 pp Top-1)** |
| **DeiT-Small** | Clean | 5194.0 | 0.193 | 1.00x | 79.80% | 0.00 pp | Reference |
| | Attention Pruning | 7289.5 | 0.137 | 1.40x | 73.88% | -5.92 pp | Severe accuracy damage |
| | ToMe | 7273.2 | 0.137 | 1.40x | 75.77% | -4.03 pp | Large accuracy drop |
| | Hybrid Group Mean | 7153.5 | 0.140 | 1.38x | 76.67% | -3.13 pp | High speed baseline |
| | **Selective Restricted (30%)** | **4432.0** | **0.226** | **0.85x** | **77.20%** | **-2.60 pp** | **Accuracy Tradeoff (+0.53 pp vs GM, +1.43 pp vs ToMe)** |
| **ViT-B/16** | Clean | 2538.6 | 0.394 | 1.00x | 81.80% | 0.00 pp | Reference |
| | Attention Pruning | 3563.6 | 0.281 | 1.40x | 73.02% | -8.78 pp | Catastrophic drop |
| | ToMe | 3493.7 | 0.286 | 1.38x | 75.81% | -5.99 pp | Heavy drop |
| | Hybrid Group Mean | 3474.6 | 0.288 | 1.37x | 77.15% | -4.65 pp | High speed baseline |
| | **Selective Restricted (30%)** | **2051.3** | **0.488** | **0.81x** | **77.60%** | **-4.20 pp** | **Accuracy Tradeoff (+0.45 pp vs GM, +1.79 pp vs ToMe)** |
| **DINOv2** | Clean | 3181.5 | 0.314 | 1.00x | 84.50% | 0.00 pp | Reference |
| | Attention Pruning | 4118.0 | 0.243 | 1.29x | 84.16% | -0.34 pp | High speed |
| | ToMe | 4089.0 | 0.245 | 1.29x | 84.27% | -0.23 pp | Moderate accuracy |
| | Hybrid Group Mean | 4049.6 | 0.247 | 1.27x | 84.32% | -0.18 pp | High speed baseline |
| | **Selective Restricted (30%)** | **3494.2** | **0.286** | **1.10x** | **84.34%** | **-0.16 pp** | **Accuracy Tradeoff (+0.02 pp Top-1)** |
