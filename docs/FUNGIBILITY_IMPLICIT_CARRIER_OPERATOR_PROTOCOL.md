# Pre-Registered Research Protocol: Implicit Carrier-Space Operator Solving and Selective Operator Activation

**Investigation:** Implicit / Carrier-Space Operator Solving and Selective Operator Activation  
**Repository:** `https://github.com/nhatminh-115/Patch-Content-Fungibility`  
**Branch:** `main`  
**Date:** 2026-10-07  
**Hardware Target:** NVIDIA GeForce RTX 5070 Laptop GPU (8.15 GB VRAM, sm_120)  
**Deliverables Root:** `outputs/fungibility_implicit_carrier_operator/`  
**Figures Root:** `figures/fungibility_implicit_carrier_operator/`  

---

## 1. Problem Statement & Motivation

Prior investigations established that:
1. The downstream-visible operator subspace $V(x) \in \mathbb{R}^{ND \times r}$ contains useful functional geometry, and low-rank Jacobian projection captures $\approx 95\%$ of functional transmission.
2. However, predicting and materializing $V(x) \in \mathbb{R}^{ND \times r}$ in ambient token $\times$ feature space requires:
   - High-dimensional output projections ($Z_A \in \mathbb{R}^{N \times r}, Z_B \in \mathbb{R}^{D \times r}$)
   - Ambient basis materialization and orthonormalization via Householder QR ($150,528 \times 32$ per image), consuming $\approx 72\text{ ms}$ at $BS=32$.
3. Attempts to compress $V(x)$ into a global shared linear envelope ($U_K \in \mathbb{R}^{ND \times K}$) failed because natural image operator subspaces are non-linear and high-dimensional ($K \le 64$ captures $< 9\%$ energy).
4. Non-neural Hybrid Group Mean achieves immediate $BS^* = 1$ crossover and up to $1.57\times$ clean throughput, but sacrifices functional fidelity at aggressive budgets.

### Central Research Question
> **Can we obtain operator-aware carrier corrections WITHOUT ever predicting or materializing the ambient basis $V(x) \in \mathbb{R}^{ND \times r}$?**

---

## 2. Mathematical Formulation: Minimal Carrier-Space Objective

Let:
- $p = \text{vec}(P) \in \mathbb{R}^{ND}$ be the uncompressed patch activations.
- $c = \text{vec}(C) \in \mathbb{R}^{BD}$ be the carrier token vector ($B \ll N$).
- $A_S = S \otimes I_D \in \mathbb{R}^{ND \times BD}$ be the Kronecker grouping operator such that $A_S c = \text{vec}(S C)$.
- $c_0 = \text{vec}(C_{\text{mean}})$ be the baseline Group Mean carrier.
- $e_0 = p - A_S c_0 \in \mathbb{R}^{ND}$ be the baseline reconstruction error.

The operator-aware carrier correction objective is:
$$\min_c \| J (p - A_S c) \|_2^2 + \lambda \| c - c_0 \|_2^2$$

Defining $M = J^\top J \in \mathbb{R}^{ND \times ND}$ (approximated offline by $V_{\text{true}} V_{\text{true}}^\top$), setting $c = c_0 + \delta c$ yields:
$$\mathcal{L}(\delta c) = (e_0 - A_S \delta c)^\top M (e_0 - A_S \delta c) + \lambda \| \delta c \|_2^2$$

The unconstrained optimal correction satisfies:
$$(A_S^\top M A_S + \lambda I) \delta c = A_S^\top M e_0$$

### Low-Dimensional Restricted Carrier Space
Instead of solving for full $\delta c \in \mathbb{R}^{BD}$, we restrict corrections to a low-dimensional subspace spanned by an analytic basis:
$$R(x, S) \in \mathbb{R}^{BD \times q}, \quad q \in \{4, 8, 16, 32, 64\}$$
$$\delta c = R(x, S) \alpha, \quad \alpha \in \mathbb{R}^q$$

The restricted objective becomes:
$$\min_{\alpha \in \mathbb{R}^q} \| J (e_0 - A_S R \alpha) \|_2^2 + \lambda \| \alpha \|_2^2$$

This yields the exact $q \times q$ linear system:
$$(H_q + \lambda I_q) \alpha^* = g_q$$
where:
$$H_q = R^\top A_S^\top M A_S R \in \mathbb{R}^{q \times q}$$
$$g_q = R^\top A_S^\top M e_0 \in \mathbb{R}^q$$

Using the low-rank factorization $M = V_{\text{true}} V_{\text{true}}^\top$, let:
$$K_R = V_{\text{true}}^\top (A_S R) \in \mathbb{R}^{r \times q}$$
Then:
$$H_q = K_R^\top K_R, \quad g_q = K_R^\top (V_{\text{true}}^\top e_0)$$

**Computational Complexity:**
- $H_q$ is a small $q \times q$ symmetric positive semi-definite matrix ($16 \times 16$ or $32 \times 32$).
- Solving $(H_q + \lambda I) \alpha = g_q$ takes **$< 0.005\text{ ms}$**.
- No $ND \times r$ tensor is ever materialized or orthogonalized at test time!

---

## 3. Analytic Correction Bases $R(x, S)$

The basis $R$ is constructed analytically from information readily available during compression:
1. **Basis A (Group-Residual SVD Directions):** Computes the top 1–2 principal feature directions of within-group patch residuals $(P_i - C_{0, g(i)})$.
2. **Basis B (Calibration Feature PCA):** Uses fixed global feature PCA directions derived from offline calibration activations.
3. **Basis C (Group-Wise Statistical Directions):** Combines group mean directions, residual variance directions, and normalized residual directions.
4. **Basis D (Hybrid Semantic Residual Directions):** Combines spatial-semantic grouping eigenvectors with local residual norms.
5. **Basis E (Random Matched Control):** Random orthogonal directions with matched dimension $q$ and Frobenius norm.

Target construction overhead: **$< 0.05\text{ ms/image}$**.

---

## 4. Sufficient Statistics Distillation Options

If the restricted carrier oracle recovers significant functional fidelity, we train lightweight predictors mapping pooled activations $x \in \mathbb{R}^{2D}$ to carrier statistics:
- **Option A ($g_q$ only):** Predicts only $g_q \in \mathbb{R}^q$, using a calibrated static Hessian $\bar{H}_q$ or diagonal Hessian. Output dim: $q$ numbers (e.g. 16 or 32).
- **Option B ($\text{diag}(H_q) + g_q$):** Predicts diagonal entries and gradient vector. Output dim: $2q$ numbers.
- **Option C (Cholesky $L_q + g_q$):** Predicts lower-triangular Cholesky factor of $H_q$ and $g_q$. Output dim: $q(q+1)/2 + q$ numbers.
- **Option D (Direct $\alpha^*$ Prediction):** Directly predicts $\alpha^* \in \mathbb{R}^q$ inside the analytically defined basis $R$.

---

## 5. Selective Operator Activation (Adaptive Gating)

Because Hybrid Group Mean is fast and accurate for standard images, operator correction should only be invoked for "hard" images where compression error is high.

We define a cheap risk estimator $risk(x) \in [0, 1]$ computed from clean prefix representations:
1. **Classifier Margin:** $1 - (p_{(1)} - p_{(2)})$ from prefix proxy logits.
2. **Within-Group Residual Norm:** $\| P - S C_0 \|_F / \| P \|_F$.
3. **Patch Feature Variance:** Trace of patch covariance.
4. **Composite Risk Score:** Normalized weighted combination.

Operator correction is triggered only when $risk(x) > \tau$.
We sweep activation budgets: $5\%, 10\%, 20\%, 30\%, 50\%, 100\%$.

---

## 6. Pre-Registered Success Criteria (Levels C1–C7)

- **Level C1 — Restricted Oracle Viability:** $q \le 32$ restricted carrier oracle recovers $\ge 50\%$ of full-operator functional improvement ($\|JE\|$ reduction).
- **Level C2 — Sufficient-Statistic Distillation:** Predicted small $H_q/g_q$ or direct $\alpha$ recovers $\ge 50\%$ of restricted-oracle benefit.
- **Level C3 — Representation Breakthrough:** Zero ambient $ND \times r$ tensors are materialized during test-time inference.
- **Level C4 — Low Overhead:** Total operator overhead (gate + predictor + solve) is $< 0.25\text{ ms/image}$ at practical batch sizes ($BS \ge 16$).
- **Level C5 — Selective Value:** Selective activation retains $\ge 70\%$ of always-on operator accuracy improvement while invoking operator correction on $\le 30\%$ of images.
- **Level C6 — Practical Frontier:** Selective/restricted operator strictly dominates Hybrid Group Mean on the accuracy-throughput Pareto frontier.
- **Level C7 — Strong Practical Success:** At least one major architecture achieves $\ge 1.2\times$ clean throughput with $\le 2\text{ pp}$ Top-1 loss and measurable accuracy gain over matched Group Mean.
