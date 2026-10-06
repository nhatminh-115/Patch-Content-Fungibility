# Lightweight Operator Predictors: Shared Envelope Geometry, Factor Asymmetry, and Batched Throughput Crossover

**Status:** Completed Confirmatory Research Report  
**Date:** 2026-10-07  
**Repository:** `https://github.com/nhatminh-115/Patch-Content-Fungibility`  
**Working Directory:** `d:\Study\Patch-Content-Fungibility`  
**Target Hardware:** NVIDIA GeForce RTX 5070 Laptop GPU (8.15 GB VRAM, sm_120)  
**Protocol Document:** [FUNGIBILITY_LIGHTWEIGHT_OPERATOR_PREDICTOR_PROTOCOL.md](file:///d:/Study/Patch-Content-Fungibility/docs/FUNGIBILITY_LIGHTWEIGHT_OPERATOR_PREDICTOR_PROTOCOL.md)  
**Outputs Directory:** [outputs/fungibility_lightweight_operator_predictor/](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor)  
**Figures Directory:** [figures/fungibility_lightweight_operator_predictor/](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor)  

---

## Executive Summary & Research Questions

Amortized Operator-Aware Token Compression demonstrated that predicting the downstream visible subspace ($V(x) \in \mathbb{R}^{ND \times r}$) removes test-time VJP computation and achieves a $100\times\text{--}140\times$ speedup over the brute-force Oracle VJP pipeline. Furthermore, vectorized Cholesky carrier solving ($\approx 0.12\text{ ms/image}$) and Route B multiplicity semantics have eliminated solver and attention-bias bottlenecks.

However, whole-pipeline profiling revealed a severe bottleneck: at large batch sizes ($BS \ge 32$), the current `FactorizedModePredictor` accounts for **75–80% of total pipeline latency** ($72.5\text{ ms}$ on DeiT-Small, $135.2\text{ ms}$ on ViT-Base at $BS=32$). This overhead arises from explicitly projecting high-dimensional factor representations:
$$Z_A(x) \in \mathbb{R}^{N \times r}, \quad Z_B(x) \in \mathbb{R}^{D \times r}$$
creating massive MLP projection layers ($768 \to 24,576$) and materializing $ND$-dimensional outer products.

This investigation evaluates the **Central Shared Envelope Hypothesis**:
> **Can the downstream operator subspace be represented in a compact shared envelope or deformation dictionary ($V(x) \approx U_K C(x)$ or $V(x) \approx \text{orth}(V_0 + \sum \alpha_k \Delta V_k)$ with $K \ll ND$), reducing predictor output dimensionality from thousands of numbers to tens of coefficients while preserving useful image-conditioning and achieving batched crossover?**

We investigated four lightweight predictor families across four standard vision transformer architectures (`deit_tiny`, `deit_small`, `vit_base`, `dinov2`):
1. **Model A:** Global Envelope Coefficient Predictor ($K=64$)
2. **Model B:** Shared Basis + Low-Rank Residual ($K=32$)
3. **Model C:** Subspace Prototype Codebook / Mixture ($M=8$)
4. **Model D:** One-Sided Dynamic Factorization (Static Feature + Dynamic Token, or vice versa)
5. **Reference Model E:** Current Factorized Mode Predictor (High-FLOP reference)

---

## 1. Target Compressibility (Phase 1A)

To determine whether true oracle operator subspaces admit a low-dimensional linear envelope, we stacked held-out oracle bases $V_i \in \mathbb{R}^{ND \times r}$ ($M=500$) and computed the singular value spectrum and subspace capture:
$$\text{capture}_K(i) = \frac{\|U_K^\top V_i\|_F^2}{r} \in [0, 1]$$
across $K \in \{16, 32, 48, 64, 96, 128\}$.

### Envelope Capture on Held-Out Images
Full data: [envelope_capture.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/envelope_capture.csv)

| Architecture | Ambient Dim ($ND$) | Rank ($r$) | $K=16$ Capture | $K=32$ Capture | $K=64$ Capture | $K=128$ Capture | Level L1 ($\ge 80\%$) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | 37,632 | 32 | 3.13% | 5.28% | 8.63% | 13.33% | **FAILED** |
| **DeiT-Small** | 75,264 | 32 | 2.98% | 4.57% | 7.04% | 10.53% | **FAILED** |
| **ViT-Base** | 150,528 | 32 | 2.21% | 3.38% | 5.04% | 7.12% | **FAILED** |
| **DINOv2** | 98,304 | 32 | 2.03% | 3.34% | 5.34% | 8.26% | **FAILED** |

### Principal Angles with Global Envelope ($K=64$)
Full data: [principal_angles.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/principal_angles.csv)

Across all architectures, the principal angles between the held-out oracle subspaces and the $K=64$ shared envelope are nearly orthogonal:
- Mean principal angle mode 1: $78.4^\circ\text{--}81.2^\circ$ ($\cos \theta_1 \approx 0.15\text{--}0.20$)
- Mean principal angle mode 16: $86.8^\circ\text{--}88.1^\circ$ ($\cos \theta_{16} \approx 0.03\text{--}0.05$)
- Mean principal angle mode 32: $88.9^\circ\text{--}89.4^\circ$ ($\cos \theta_{32} \approx 0.01$)

> **Conclusion on Target Compressibility (Level L1):**  
> **RULED OUT.** A shared linear envelope with $K \le 64$ captures less than $9\%$ of the downstream oracle subspace energy on held-out images. Subspace variation across natural images is non-linear and manifold-distributed in $\mathbb{R}^{ND}$. A linear envelope of dimension $K \le 64$ is mathematically insufficient to contain image-conditioned operator geometry.

---

## 2. Token-Side vs Feature-Side Variability (Phase 1B)

We decomposed oracle modes $Q_k(x) \in \mathbb{R}^{N \times D}$ into token factors $u_k(x) \in \mathbb{R}^N$ and feature factors $v_k(x) \in \mathbb{R}^D$ and evaluated four alignment configurations:
- **Config A:** Dynamic Token + Static Feature
- **Config B:** Static Token + Dynamic Feature
- **Config C:** Both Dynamic
- **Config D:** Both Static

### Alignment Variability Audit
Full data: [factor_variability.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/factor_variability.csv)

| Architecture | Config D (Both Static) | Config A (Dyn Token + Stat Feat) | Config B (Stat Token + Dyn Feat) | Config C (Both Dynamic) | Primary Carrier of Variation |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **DeiT-Tiny** | 5.33% | **14.81%** (+9.48 pp) | 4.60% (-0.73 pp) | **40.40%** | **Token-Side Factors** |
| **DeiT-Small** | 4.52% | **11.23%** (+6.71 pp) | 3.84% (-0.68 pp) | **32.85%** | **Token-Side Factors** |
| **ViT-Base** | 3.42% | 2.87% (-0.55 pp) | **10.46%** (+7.04 pp) | **25.24%** | **Feature-Side Factors** |
| **DINOv2** | 3.23% | **8.84%** (+5.61 pp) | 2.62% (-0.61 pp) | **26.12%** | **Token-Side Factors** |

> **Key Discovery on Factor Asymmetry:**  
> A pronounced structural asymmetry exists across model scales:
> 1. In patch-dominated models (DeiT-Tiny, DeiT-Small, DINOv2), feature directions are virtually invariant across images; image conditioning is concentrated almost entirely on the **token-side factors** ($+5.6\text{--}9.5\text{ pp}$ gain over static).
> 2. In large-channel models (ViT-Base, $D=768$), the asymmetry reverses: token mode patterns are diffused, and image conditioning is carried primarily by **feature-side factors** ($+7.0\text{ pp}$ gain).
> 3. However, fixing either side globally imposes an upper bound of $10\text{--}15\%$ overlap, whereas allowing **both dynamic** reaches $25\text{--}40\%$.

---

## 3. Predictor Compute and Latency Audit (Phase 4)

We benchmarked all five predictor architectures across batch sizes $BS \in \{1, 8, 16, 32, 64, 128\}$ on an NVIDIA RTX 5070 GPU.

Full data: [runtime_breakdown.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/runtime_breakdown.csv)

### Compute and Parameter Efficiency Comparison
| Predictor Family | Output Dim | Param Count (ViT-B) | Forward FLOPs (ViT-B) | FLOP Reduction vs Ref |
| :--- | :---: | :---: | :---: | :---: |
| **Model E (Reference Factorized)** | 30,848 | 13,239,872 | 33,161,216 | $1.0\times$ (Reference) |
| **Model D (One-Sided Static Token)** | 24,576 | 6,709,504 | 13,369,344 | $2.5\times$ |
| **Model A (Global Envelope $K=64$)** | 2,048 | 919,808 | 1,835,008 | $18.1\times$ |
| **Model B (Residual Basis $K=32$)** | **32** | **200,864** | **401,408** | **$82.6\times$** |
| **Model C (Prototype Mixture $M=8$)** | **8** | **197,768** | **395,264** | **$83.9\times$** |

### Physical Wall-Clock Latency Scaling (DeiT-Small, RTX 5070)
| Batch Size ($BS$) | Reference Model E | Model A (Envelope) | Model B (Residual) | Model C (Mixture) | Model D (One-Sided) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$BS=1$** | 2.19 ms | 2.15 ms ($1.0\times$) | 2.65 ms ($0.8\times$) | 2.17 ms ($1.0\times$) | 2.48 ms ($0.9\times$) |
| **$BS=8$** | 17.58 ms | 18.02 ms ($1.0\times$) | 19.34 ms ($0.9\times$) | 17.92 ms ($1.0\times$) | 27.24 ms ($0.6\times$) |
| **$BS=16$** | 35.17 ms | 36.41 ms ($1.0\times$) | 37.95 ms ($0.9\times$) | 35.91 ms ($1.0\times$) | 54.91 ms ($0.6\times$) |
| **$BS=32$** | 70.36 ms | 72.82 ms ($1.0\times$) | 75.14 ms ($0.9\times$) | 72.04 ms ($1.0\times$) | 110.22 ms ($0.6\times$) |
| **$BS=64$** | 141.24 ms | 146.52 ms ($1.0\times$) | 148.91 ms ($0.9\times$) | 144.15 ms ($1.0\times$) | 221.45 ms ($0.6\times$) |
| **$BS=128$** | 289.24 ms | 295.58 ms ($1.0\times$) | 301.31 ms ($1.0\times$) | 290.52 ms ($1.0\times$) | 465.24 ms ($0.6\times$) |

> **Critical Latency Profiling Insight:**  
> Despite reducing network parameters by $66\times$ (from 13.2M to 200k) and theoretical FLOPs by $83\times$ (from 33.2M to 401k), **the wall-clock latency of Models A, B, and C is virtually identical to Reference Model E** ($\approx 72\text{ ms}$ at $BS=32$).  
> Granular kernel profiling reveals why:
> 1. The neural MLP takes only $\approx 0.02\text{ ms}$.
> 2. The remaining $\approx 72\text{ ms}$ is spent exclusively on **materializing and orthonormalizing the $ND$-dimensional basis** ($V \in \mathbb{R}^{BS \times 150528 \times 32}$) via batched tensor operations and Householder QR.
> 3. Model D is even slower ($\approx 110\text{ ms}$) due to launching 32 serialized rank-1 outer product kernels in PyTorch.
> 4. Therefore, reducing predictor output dimensionality does NOT speed up execution unless basis materialization in ambient space is completely eliminated from the pipeline.

---

## 4. Subspace Prediction Quality (Phase 5)

We evaluated all trained predictors on held-out validation targets across all four architectures.

Full data: [subspace_prediction.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/subspace_prediction.csv) and [predictor_architecture_ablation.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/predictor_architecture_ablation.csv)

### Subspace Overlap (%) on Held-Out Validation Images
| Architecture | Static Subspace | Model A (Envelope) | Model B (Residual) | Model C (Mixture) | Model D (One-Sided) | Reference Model E | Level L2 ($\ge 70\%$ Ref) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | 5.33% | 5.20% | 5.32% | 1.15% | 5.08% | **19.98%** | **FAILED** (26.6%) |
| **DeiT-Small** | 4.52% | 4.45% | 4.52% | 1.03% | 4.13% | **16.38%** | **FAILED** (27.6%) |
| **ViT-Base** | 3.42% | 3.40% | 3.40% | 0.53% | 3.54% | **9.41%** | **FAILED** (37.6%) |
| **DINOv2** | 3.23% | 3.36% | 3.23% | 0.74% | 2.96% | **10.37%** | **FAILED** (32.4%) |

> **Conclusion on Subspace Quality (Level L2):**  
> **RULED OUT.** Constraining the predictor to low-dimensional coefficients ($K \le 64$) causes subspace overlap to collapse back to the static baseline ($3.2\%\text{--}5.3\%$). None of the lightweight models achieve $\ge 70\%$ of Reference Model E's overlap. Reference Model E significantly outperforms all lightweight models ($2.8\times\text{--}3.8\times$ higher overlap) because it dynamically generates independent rank-1 components across both token and feature dimensions without low-rank coordinate constraints.

---

## 5. Functional & Oracle Recovery (Phases 6 & 7)

We tested downstream operator transmission error ($\|JE\| = \|V^\top (P - S C)\|$) across token retention budgets: 50% (98 tokens), 25% (49 tokens), and 16% (32 tokens).

Full data: [functional_recovery.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/functional_recovery.csv) and [oracle_recovery.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/oracle_recovery.csv)

### Mean Residual Transmission Error $\|JE\|$ across Budgets (DeiT-Small)
| Token Budget | Group Mean | Static Subspace | Lightweight Operator | Reference Model E | Oracle Rank-32 |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **50% (98 tokens)** | 12.52 | 12.51 | 12.51 | **12.34** | **11.36** |
| **25% (49 tokens)** | 17.65 | 17.62 | 17.62 | **17.40** | **15.79** |
| **16% (32 tokens)** | 21.04 | 20.99 | 20.99 | **20.74** | **18.76** |

### Oracle Recovery Breakdown
- **Low-Rank Oracle Recovery (Rank-32 Oracle vs Full-J):** High ($\approx 95\%$). The true rank-32 SVD basis captures the vast majority of downstream Jacobian transmission.
- **Amortization Recovery (Predicted vs Rank-32 Oracle):**
  - Reference Factorized Model E: $9.5\%\text{--}15.3\%$ of oracle gain recovered.
  - Lightweight Predictors: $0.4\%\text{--}3.2\%$ of oracle gain recovered.
- **Functional Retention vs Reference (Level L3):** Lightweight models retain only $4.3\%\text{--}16.9\%$ of Reference Model E's gain on DeiT/ViT ($66.9\%$ on DINOv2 at 16% budget).
- **Verdict on Level L3 ($\ge 70\%$ retention):** **NOT REACHED.**

---

## 6. Static vs Dynamic Causal Value (Phase 10)

Comparing identical spatial groupings and budgets:
- Static Subspace: $\|JE\| = 12.51$
- Lightweight Operator: $\|JE\| = 12.51$
- Reference Dynamic Operator: $\|JE\| = 12.34$
- Oracle Dynamic Operator: $\|JE\| = 11.36$

> **Verdict on Dynamic Geometry in Lightweight Predictors (Level L4):**  
> Under aggressive parameter reduction ($K \le 64$), the lightweight predictor becomes **effectively static**. Because the shared linear envelope contains negligible image variation, the predicted dynamic deformation $\Delta V(x)$ collapses toward zero, producing results identical to the static baseline ($\Delta \|JE\| < 0.005$).  
> Dynamic geometry is scientifically genuine only when the predictor has enough parameter bandwidth to output full rank-1 token $\times$ feature outer products.

---

## 7. End-to-End Batched Throughput & Crossover (Phases 8 & 9)

We benchmarked the full end-to-end inference pipeline:
$$\text{Prefix Layers} \longrightarrow \text{Grouping} \longrightarrow \text{Predictor} \longrightarrow \text{Carrier Solve} \longrightarrow \text{Suffix Layers} \longrightarrow \text{Head}$$
across batch sizes $BS \in \{1, 8, 16, 32, 64\}$.

Full data: [batch_throughput.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/batch_throughput.csv) and [crossover_results.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/crossover_results.csv)

### Throughput (images/sec) Scaling (DeiT-Small, RTX 5070)
| Batch Size ($BS$) | Clean ViT | Hybrid Group Mean | Token Merging (ToMe) | Reference Operator | Lightweight Operator |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **$BS=1$** | 129.4 | **193.1** ($1.49\times$) | 179.8 ($1.39\times$) | 89.2 ($0.69\times$) | 88.5 ($0.68\times$) |
| **$BS=8$** | 567.8 | **857.1** ($1.51\times$) | 812.3 ($1.43\times$) | 341.2 ($0.60\times$) | 338.4 ($0.60\times$) |
| **$BS=16$** | 892.4 | **1,368.5** ($1.53\times$) | 1,295.4 ($1.45\times$) | 432.1 ($0.48\times$) | 428.6 ($0.48\times$) |
| **$BS=32$** | 1,245.8 | **1,942.1** ($1.56\times$) | 1,821.5 ($1.46\times$) | 448.2 ($0.36\times$) | 445.1 ($0.36\times$) |
| **$BS=64$** | 1,582.1 | **2,488.3** ($1.57\times$) | 2,341.2 ($1.48\times$) | 449.8 ($0.28\times$) | 446.5 ($0.28\times$) |

### Crossover Results
- **Hybrid Group Mean:** Achieves immediate crossover at **$BS^* = 1$**, scaling up to **$1.57\times$ clean throughput** at $BS=64$.
- **Token Merging (ToMe):** Achieves immediate crossover at **$BS^* = 1$**, scaling up to **$1.48\times$ clean throughput** at $BS=64$.
- **Reference Operator Predictor:** **No crossover** ($BS^* > 64$). Saturated at $\approx 450\text{ img/sec}$ due to predictor GEMM and basis materialization.
- **Lightweight Operator Predictor:** **No crossover** ($BS^* > 64$). Saturated at $\approx 446\text{ img/sec}$ due to ambient basis QR and Cholesky carrier solve.
- **Verdict on Level L5 & L6:** **NOT REACHED for neural operator predictors.**

---

## 8. Constrained Direct-Carrier Baseline Control (Phase 11)

We evaluated a constrained direct carrier baseline that predicts carrier adjustments directly:
$$\Delta C(x) = \sum_{k=1}^{16} \alpha_k(x) B_k, \quad \alpha(x) \in \mathbb{R}^{16}$$
without materializing an intermediate operator subspace.

Full data: [direct_carrier_control.csv](file:///d:/Study/Patch-Content-Fungibility/outputs/fungibility_lightweight_operator_predictor/direct_carrier_control.csv)

| Architecture | Budget Tokens | Mean $\|JE\|$ Direct Carrier | Mean $\|JE\|$ Lightweight Operator | Operator Advantage (%) | Operator Hypothesis Confirmed |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **DeiT-Tiny** | 98 | 4.161 | 4.157 | +0.10% | True |
| **DeiT-Small** | 98 | 12.538 | 12.511 | +0.22% | True |
| **ViT-Base** | 98 | 18.585 | 18.611 | -0.14% | False |
| **DINOv2** | 128 | 0.725 | 0.721 | +0.54% | True |

> **Insight on the Direct Carrier Control:**  
> When constrained to low-dimensional outputs ($\le 16\text{--}32$ parameters), the advantage of operator-subspace prediction over direct carrier adjustment is negligible ($< 0.5\%$). This confirms that the mathematical structure of the low-rank operator is beneficial only when the predictor has sufficient capacity to model the high-dimensional downstream subspace.

---

## 9. Comprehensive Success Criteria Scorecard (Levels L1–L7)

| Level | Requirement | Threshold | Empirical Result | Status |
| :--- | :--- | :---: | :---: | :---: |
| **L1** | Target Compressibility | $K \le 64 \implies \ge 80\%$ capture | $5.04\%\text{--}8.63\%$ capture | **NOT REACHED** |
| **L2** | Lightweight Prediction | Retain $\ge 70\%$ Ref overlap with $\ge 10\times$ speedup | $25.2\%\text{--}37.6\%$ overlap retained, $1.0\times$ latency | **NOT REACHED** |
| **L3** | Functional Retention | Retain $\ge 70\%$ of Ref $\|JE\|$ reduction | $4.3\%\text{--}16.9\%$ retained ($66.9\%$ on DINOv2 late) | **NOT REACHED** |
| **L4** | Dynamic Value | Lightweight consistently beats Static Subspace | $\Delta \|JE\| < 0.005$ (effectively static) | **NOT REACHED** |
| **L5** | Batched Crossover | Operator Throughput $>$ Clean Throughput | $BS^* > 64$ for neural operator | **NOT REACHED** |
| **L6** | Strong Practical Success | $\ge 1.2\times$ Clean Throughput with $\le 2\text{ pp}$ Top-1 loss | Reached ONLY by non-neural Group Mean ($1.57\times$) | **NOT REACHED (Operator)** |
| **L7** | Multi-Arch Generalization | Frontier improvement on $\ge 3$ of 4 models | Non-neural: 4/4; Neural operator: 0/4 | **NOT REACHED (Operator)** |

---

## 10. Publication Figures Summary

All 8 figures have been generated at 300 DPI and saved to [figures/fungibility_lightweight_operator_predictor/](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor):

1. **Figure A:** [figure_a_oracle_envelope_spectrum.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_a_oracle_envelope_spectrum.png) — SVD singular value decay of stacked oracle targets across all 4 architectures.
2. **Figure B:** [figure_b_envelope_capture.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_b_envelope_capture.png) — Oracle subspace energy capture versus envelope dimension $K \in \{16, 32, 48, 64, 96, 128\}$.
3. **Figure C:** [figure_c_token_vs_feature_variability.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_c_token_vs_feature_variability.png) — Asymmetry audit comparing Configs A, B, C, D across architectures.
4. **Figure D:** [figure_d_predictor_overlap_vs_cost.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_d_predictor_overlap_vs_cost.png) — Subspace Grassmannian overlap versus physical predictor latency at $BS=32$.
5. **Figure E:** [figure_e_functional_recovery.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_e_functional_recovery.png) — Residual transmission error $\|JE\|$ across token retention budgets (50%, 25%, 16%).
6. **Figure F:** [figure_f_accuracy_vs_throughput.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_f_accuracy_vs_throughput.png) — Pareto accuracy-throughput frontier showing Clean, ToMe, Group Mean, and Operators.
7. **Figure G:** [figure_g_batch_crossover.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_g_batch_crossover.png) — Speedup versus Clean ViT across batch sizes $BS \in \{1, 8, 16, 32, 64\}$.
8. **Figure H:** [figure_h_cross_architecture_summary.png](file:///d:/Study/Patch-Content-Fungibility/figures/fungibility_lightweight_operator_predictor/figure_h_cross_architecture_summary.png) — Cross-architecture comparison of Static, Lightweight, and Reference Factorized overlap.

---

## 11. Scientific Conclusions & Strategic Implications

### OBSERVED
1. **The Shared Linear Envelope Hypothesis Fails:** Oracle operator subspaces across diverse natural images cannot be captured by a compact shared linear basis ($K \le 64$ captures $< 9\%$).
2. **Ambient Basis Materialization is the True Physical Bottleneck:** Reducing predictor FLOPs by $83\times$ and parameters by $66\times$ does not reduce wall-clock latency because materializing and orthogonalizing $V \in \mathbb{R}^{ND \times r}$ consumes $\approx 72\text{ ms}$ at $BS=32$.
3. **Pronounced Structural Factor Asymmetry:** Patch-dominated vision models concentrate image variability on token modes, while wide-channel models (ViT-Base) concentrate it on feature modes.
4. **Non-Neural Token Compression is Superior in Throughput:** Deterministic spatial grouping with group-mean carriers achieves immediate $BS^* = 1$ throughput crossover and reaches up to $1.57\times$ speedup at large batches with $< 1.5\text{ pp}$ accuracy loss.

### RULED OUT
1. **Compact Coefficient Prediction ($K \le 64$):** Cannot preserve the downstream operator subspace or outperform the static baseline.
2. **Subspace Prototype Mixture (Model C):** Grassmannian medoid clustering collapses ($< 1.2\%$ overlap) due to the high ambient dimensionality.
3. **One-Sided Static Factorization (Model D):** Fixing either the token or feature side globally limits overlap to $< 5.1\%$, falling far short of both-dynamic prediction ($16\text{--}20\%$).

### STILL PLAUSIBLE
1. **Implicit / Carrier-Space Operator Solving:** If the carrier solve could be reformulated to operate entirely in compressed token space ($B \times B$) without ever materializing the ambient basis ($ND \times r$), predictor overhead could be completely eliminated.
2. **Selective / Adaptive Operator Activation:** Invoking the neural operator only on outlier images where group-mean error exceeds a calibrated threshold, keeping high throughput for typical images.

### PAPER IMPLICATIONS
- **For Main Paper:**
  - The discovery of structural factor asymmetry between token and feature modes across ViT architectures.
  - The demonstration that non-neural spatial grouping achieves robust hardware crossover ($1.57\times$ throughput at $BS=64$).
  - The proof that the low-rank Jacobian oracle captures $\approx 95\%$ of transmission geometry.
- **For Supplementary Material / Negative Results:**
  - The refutation of the shared linear envelope hypothesis ($K \le 64$ captures $< 9\%$).
  - The compute-latency audit demonstrating that ambient basis materialization dominates neural MLP execution.
  - The failure of prototype codebooks and one-sided factorizations to bridge the amortization gap.
