# Pre-Registered Protocol: Lightweight Operator Predictors and Shared Envelope Geometry

**Document:** `docs/FUNGIBILITY_LIGHTWEIGHT_OPERATOR_PREDICTOR_PROTOCOL.md`  
**Repository:** `https://github.com/nhatminh-115/Patch-Content-Fungibility`  
**Author:** Antigravity Autonomous Research Agent  
**Date:** 2026-10-06  
**Status:** PRE-REGISTERED PRIOR TO EXECUTION  

---

## 1. Scientific Context and Bottleneck Identification

Prior research in Patch Content Fungibility established:
1. **Operator-Aware Carrier Compression** preserves accuracy and reduces functional damage ($\|J E\|$, logit $L_2$) relative to unguided token reduction.
2. **Vectorized GPU Carrier Solving** is fast: $\approx 1.4\text{--}1.5\text{ ms}$ for $BS=1$, amortizing to $\approx 0.12\text{ ms/image}$ at large batch sizes ($BS \ge 32$).
3. **Grouping** is lightweight: fixed spatial grouping $<0.05\text{ ms}$, Hybrid IP-SM grouping $<0.1\text{ ms/image}$.
4. **FlashAttention Multiplicity (Route B)** recovers 100.00% numerical parity without explicit attention masks, running at fused kernel speeds.
5. **Suffix Transformer Blocks** achieve dramatic speedups under token reduction ($7.1\times$ faster on ViT-Base at $BS=32$).
6. **The Remaining Bottleneck:** The current `FactorizedModePredictor` outputs:
   $$Z_A(x) \in \mathbb{R}^{N \times r}, \quad Z_B(x) \in \mathbb{R}^{D \times r}$$
   requiring massive projection heads (e.g. $768 \to 24,576$). At batch size 32, evaluating this predictor consumes $72.5\text{ ms}$ on DeiT-Small and $135.2\text{ ms}$ on ViT-Base ($75\text{--}80\%$ of total pipeline time), preventing end-to-end throughput crossover despite suffix block acceleration.

### Central Hypothesis
The downstream-visible operator subspace $V(x) \in \mathbb{R}^{ND \times r}$ does not vary arbitrarily across the full $ND$-dimensional ambient space. Rather, it lies inside a much lower-dimensional **Shared Envelope / Dictionary**:
$$V(x) \approx U_K C(x) \quad \text{or} \quad V(x) \approx \text{orth}\left( V_0 + \sum_{k=1}^K \alpha_k(x) \Delta V_k \right)$$
where $K \ll ND$.  
Instead of predicting thousands of ambient matrix entries, a lightweight neural predictor needs only to output low-dimensional coordinates $\alpha(x) \in \mathbb{R}^K$ or $C(x) \in \mathbb{R}^{K \times r}$, reducing predictor parameter count and GEMM computation by $10\text{--}100\times$.

---

## 2. Experimental Phases & Hypotheses

### Phase 1: Oracle Target Compressibility Audit (1A & 1B)
- **1A. Global Subspace Envelope:**
  Given training oracle bases $V_i \in \mathbb{R}^{ND \times r}$ ($M=500$), construct the stacked matrix $V_{stack} = [V_1, \dots, V_M] \in \mathbb{R}^{ND \times Mr}$ and compute the top-$K$ shared orthonormal basis $U_K \in \mathbb{R}^{ND \times K}$ for $K \in \{16, 32, 48, 64, 96, 128\}$.
  For held-out images $j = 1, \dots, M_{val}$, measure envelope capture:
  $$\text{capture}_K(j) = \frac{\|U_K^\top V_j\|_F^2}{r} \in [0, 1]$$
- **1B. Token-Side vs Feature-Side Variability:**
  Test mode separability variance:
  - Configuration A: Dynamic Token + Static Feature
  - Configuration B: Static Token + Dynamic Feature
  - Configuration C: Both Dynamic (Reference Factorized Mode Predictor)
  - Configuration D: Both Static (Reference Static Subspace)

### Phase 2: Lightweight Predictor Families
1. **Model A (Global Envelope Coefficient Predictor):**
   $\hat{V}(x) = \text{orth}(U_K C(x))$ where $U_K$ is fixed and $C(x) \in \mathbb{R}^{K \times r}$ is predicted from $[cls; mean(patches)]$. Output dimension: $K \cdot r$.
2. **Model B (Shared Basis + Low-Rank Residual / Deformation):**
   $\hat{V}(x) = \text{orth}(V_0 + \sum_{k=1}^K \alpha_k(x) \Delta V_k)$ where $\alpha(x) \in \mathbb{R}^K$ is predicted from pooled activations. Output dimension: $K$ scalars ($K \in \{8, 16, 32, 64\}$).
3. **Model C (Subspace Codebook / Mixture):**
   $M$ prototype subspaces $\{P_1, \dots, P_M\}$, $M \in \{4, 8, 16, 32\}$. Predicts $M$ routing logits $w(x) = \text{softmax}(W z(x))$.
4. **Model D (One-Sided Dynamic Factorization):**
   Static feature basis + dynamic token coefficients, or static token basis + dynamic feature coefficients.
5. **Model E (Reference Bottleneck):**
   Existing `FactorizedModePredictor` with dense linear head ($768 \to 24,576$).

### Phase 3: Training Objective
Use rotationally invariant Grassmannian projection loss:
$$\mathcal{L}_{subspace} = 1 - \frac{1}{r} \|V_{true}^\top V_{pred}\|_F^2$$
avoiding arbitrary gauge/sign ambiguity.

### Phase 4: Predictor Compute & Latency Audit
Benchmark parameter count, FLOPs, and latency across $BS \in \{1, 8, 16, 32, 64, 128\}$.
Target: $\ge 10\times$ speedup over current predictor. Strong target: $\ge 30\times$.

### Phase 5–11: Quality, Compression, and Batched Throughput Crossover
- Subspace quality: Grassmannian overlap and principal angles.
- Compression value: $\|J E\|$, logit $L_2$, Top-1 accuracy at $K \in \{98, 49, 32\}$.
- End-to-end batched throughput: Clean ViT vs Attention Pruning vs Hybrid Group Mean vs Current Factorized Operator vs Lightweight Operator.
- Crossover Test: Does operator throughput exceed clean ViT ($BS^* \le 32$)?

---

## 3. Success Levels Pre-Registration (Levels L1–L7)

- **LEVEL L1 — Target Compressibility:** A shared envelope with $K \le 64$ captures $\ge 80\%$ of held-out oracle subspace energy.
- **LEVEL L2 — Lightweight Prediction:** A lightweight predictor preserves $\ge 70\%$ of current predictor overlap while achieving $\ge 10\times$ faster predictor execution.
- **LEVEL L3 — Functional Retention:** Lightweight predictor retains $\ge 70\%$ of current predictor's reduction in $\|J E\|$ or logit damage.
- **LEVEL L4 — Dynamic Value:** Lightweight image-conditioned prediction consistently outperforms static subspace at matched budget.
- **LEVEL L5 — Batched Crossover:** At least one architecture achieves $\text{throughput}_{operator} > \text{throughput}_{clean}$ with the lightweight predictor.
- **LEVEL L6 — Strong Practical Success:** At least one major architecture achieves $\ge 1.2\times$ clean throughput with $\le 2\text{ pp}$ Top-1 loss and measurable improvement over static/mean baseline.
- **LEVEL L7 — Multi-Architecture Generalization:** Lightweight dynamic predictor improves accuracy-throughput frontier on $\ge 3$ of 4 evaluated architectures.

---

## 4. Strict Protocol Constraints
- Do NOT touch `docs/PAPER_DRAFT.md`.
- Preserve all existing files and reports.
- Do NOT work in `ResCancel`. All work must be conducted in `Patch-Content-Fungibility` on `main`.
- Honest scientific reporting: report whatever empirical data reveals without forcing outcomes.
