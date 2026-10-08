# Paper Final Audit: Methodological Verification & Claim Hygiene

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)
**Date:** October 7, 2026
**Status:** Historical claim-hygiene audit; practical runtime claims superseded by real-final measurements
**Commit Reference:** `ef15f365ee59234356062d30a1ba0a457a07e4a9`

---

## 1. Audit Scope & Mandate

This document establishes the methodological hygiene and empirical verification standards governing all claims, numbers, and figures in the final manuscript. During the progression of the research program from initial exploratory token replacement to operator-aware compression and carrier-space solving, multiple formulations and benchmarks were evaluated. This audit reconciles historical findings, identifies and corrects metric artifacts, and enforces strict pre-publication claim hygiene.

---

## 2. The Denominator Inflation Artifact & Its Resolution

### The Issue in Early Exploratory Drafts:
Early exploratory reports recorded "oracle recovery" values exceeding $100\%$ (ranging from $367\%$ to $849\%$). These values prompted an immediate confirmatory audit to determine whether they represented genuine regularized denoising or an evaluation artifact.

### The Mathematical Cause:
In the legacy implementation of `batched_solve_amortized_carrier`, the reference full-space solve used an adaptive Tikhonov regularizer:
$$\lambda = \max\left(10^{-3}, 10.0 \times \frac{\text{trace}(\Sigma)}{r}\right) \approx 10\text{--}100.$$
This damping parameter was over-regularized by a factor of $\approx 10^4$ compared to standard minimum-norm solves ($\lambda = 10^{-3}$), severely arresting carrier updates and suppressing the reference full oracle's error reduction by an exact factor of **$10.78\text{x}\text{--}11.10\text{x}$** across all architectures:
- On DeiT-Small: Legacy reference gain $= 1.16$ (Group Mean $12.52 \rightarrow 11.36$).
- Stabilized reference gain $= 12.51$ (Group Mean $12.52 \rightarrow 0.0135$).

Because the restricted carrier oracle solve in `compute_restricted_carrier_oracle_quantities` used $\lambda = 10^{-3}$, it achieved an error reduction of $5.92$. Dividing this unconstrained numerator by the shrunken legacy denominator ($1.16$) produced the spurious $510.7\%$ recovery figure.

### The Corrected Stabilized Formulation:
When both solves are evaluated under matched numerical regularization ($\lambda = 10^{-3}$):
$$\text{Recovery}(q) = \frac{\|J e_0\| - \|J e_q\|}{\|J e_0\| - \|J e_{\text{stab\_oracle}}\|}$$
The resulting recovery values are strictly monotonic, well-behaved, and bounded within $[0\%, 100\%]$:
- $q=1$: **$17.5\%$**
- $q=2$: **$26.0\%$**
- $q=4$: **$29.9\%$**
- $q=8$: **$35.6\%$**
- $q=16$: **$47.4\%$**
- $q=32$: **$72.0\%$**
- $q=64$: **$92.2\%$**

### Editorial Rule:
**Under no circumstances may any $>100\%$ recovery value appear in the main text or supplement.** All references to oracle recovery must report the stabilized values above and explicitly state the denominator.

---

## 3. Disambiguating the Two Historical "Oracle" Results

To prevent reader confusion, the manuscript maintains a strict conceptual separation between two distinct historical findings:

1. **Former low-rank full-J oracle recovery claim (§6; withdrawn 2026-10-08):**
   The earlier audit defined the former >98% claim as a Top-1 recovery ratio, `100 × (A_rank − A_GroupMean)/(A_fullJ − A_GroupMean)`. Recomputed from the matched per-image Top-1 outcomes in the strict confirmatory CSVs, 22 of 40 settings have a positive denominator, and only 4 of those 22 exceed 98%; 16 denominators are negative and 2 are zero. At the most aggressive budget, DINOv2 and ViT-B/16 are below 98%, while DeiT-Small has a negative denominator. The universal claim and inference of universal low-rank concentration are withdrawn (see confirmatory report §4.5).

2. **The Restricted Carrier Subspace Recovery Finding (§7):**
   Restricting the carrier update to a $q=16$ dimensional analytic Feature-PCA basis ($\delta C = R \alpha$, $\alpha \in \mathbb{R}^{16}$) recovers **$47.4\%$** of the theoretical error reduction of the stabilized full ambient oracle on DeiT-Small ($72.0\%$ at $q=32$).
   *Context:* This measures the functional fidelity of a highly compressed, computationally efficient carrier parameterization that completely eliminates ambient tensor materialization.

---

## 4. Verification of Causal Geometry Controls

### Feature-PCA vs. Matched Random Orthogonal Bases:
To confirm that the Feature-PCA basis captures genuine visual feature covariance rather than generic low-dimensional projection benefits:
- Evaluated against 25 independent random orthonormal bases per image with matched dimension, norm, and regularization.
- Paired statistical tests:
  - DeiT-Tiny: $t = -14.62, p = 1.83 \times 10^{-26}$
  - DeiT-Small: $t = -25.98, p = 5.23 \times 10^{-46}$ (Cohen's $d = 2.45$)
  - ViT-B/16: $t = -17.66, p = 2.30 \times 10^{-32}$
  - DINOv2: $t = -16.14, p = 1.76 \times 10^{-29}$
- Structural Ablations: Permuting feature coordinates damages $\|JE\|$ by $+1.47$ on DeiT-Small. Sign-flipping preserves the spanned subspace exactly (damage $= 0.00$), confirming algebraic correctness.

---

## 5. Strict Data Partitioning for Calibration

To ensure zero information leakage:
1. **Calibration Split:** 500 images per architecture used exclusively for computing the PCA basis $W_{\text{pca}} \in \mathbb{R}^{D \times 64}$ and the static calibration vector $\bar{\alpha} = \mathbb{E}[\alpha^*]$.
2. **Evaluation Split:** 100 strictly held-out images. Zero statistics, covariance matrices, or hyperparameters from the evaluation set enter basis derivation.
3. **Generalization:** On held-out DeiT-Small images, static $\bar{\alpha}$ reduces $\|JE\|$ from $12.52$ (Group Mean) to $9.27$ (a $+3.25$ gain, capturing $54.91\%$ of restricted oracle gain), whereas random vectors of matched norm degrade error to $14.54$ (gain $-2.02$).

---

## 6. Throughput and Latency Reporting Standards

1. **Hardware & Timing Methodology:** All wall-clock latencies measured using CUDA events (`torch.cuda.Event(enable_timing=True)`) with explicit `torch.cuda.synchronize()`, warmup iterations, and repeated benchmark trials.
2. **Latency vs. Throughput Regimes:**
   - At $BS=1$ (latency-bound), token reduction savings in suffix layers are offset by prefix execution overhead; compression yields minimal wall-clock speedup.
   - At $BS \ge 16$ (compute-bound), token reduction yields significant speedups ($1.3\text{--}1.5\text{x}$ suffix acceleration).
   - Claims of acceleration must explicitly specify the **batched throughput regime ($BS \ge 16$)** and avoid asserting universal latency reduction at $BS=1$.
3. **Operator Overhead:** The prior isolated-overhead claim of $0.12$–$0.22$ ms/image is withdrawn. The real-final benchmark measures complete model-call latency, not isolated operator cost; cite `outputs/fungibility_real_final/real_throughput_raw.csv` and `real_throughput_summary.csv` for end-to-end timings.
