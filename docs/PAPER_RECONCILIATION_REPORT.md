# Paper Reconciliation & Source-of-Truth Audit Report

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Date:** October 7, 2026  
**Status:** Empirical source correction recorded; manuscript draft remains pending lockdown
**Commit Reference:** `db9f460`  

---

## 1. Executive Summary

This report preserves the audit history and corrects the empirical source hierarchy. The historical consolidation accuracy, throughput, and Pareto outputs were later invalidated as proxy-derived: accuracy was hard-coded or heuristically inferred, and timing exercised a toy loop rather than the complete pretrained model. Those artifacts remain in the repository for historical inspection but are not empirical classification or runtime evidence. The real-final measurements and the strict N=1,000 confirmatory outputs supersede them for their respective claims. The manuscript draft is intentionally unchanged in this check-10 repair.

---

## 2. Discrepancies Identified & Reconciled

### 2.1 Proxy Runtime and Frontier Claims Withdrawn; Real-Final Results Supersede Them

- **Discrepancy:** The earlier consolidation reported Top-1, latency, throughput, and accuracy-throughput values derived from proxy accuracy and toy timing. These values are invalid as empirical evidence and are withdrawn; the original files are preserved, not deleted.
- **Replacement evidence:** `outputs/fungibility_real_final/real_accuracy_summary.csv`, `real_throughput_raw.csv`, `real_throughput_summary.csv`, and `real_accuracy_throughput_frontier.csv` contain actual pretrained-model outputs and complete-call timing. Accuracy uses integer correct counts over N=1,000 held-out images per architecture. Timing uses actual model/compression callables on the NVIDIA GeForce RTX 5070 Laptop GPU, FP32, 50 warmups and 100 measured CUDA-event iterations.
- **Measured result:** At DeiT-Small, budget 98 and BS=64, Group Mean is 764/1,000 (76.4%) at 906.5 img/s; static q16 is 763/1,000 (76.3%) at 752.3 img/s; static q32 is 760/1,000 (76.0%) at 549.3 img/s; selective q16 target30 is 758/1,000 (75.8%) at 746.8 img/s. Group Mean is the only carrier method on that architecture's BS=64 frontier.
- **Frontier correction:** Static q16 adds a narrow measured frontier point on ViT-B/16 AugReg at BS=16/32/64. At BS=64 it has 737/1,000 correct (73.7%) and 263.3 img/s, alongside Clean at 761/1,000 (76.1%) and 239.1 img/s, and Group Mean at 736/1,000 (73.6%) and 297.1 img/s. q32 and selective q16 are not on any measured frontier. No broad practical-carrier advantage is claimed.
- **Runtime correction:** The former 0.12–0.23 ms/image operator-only claim is not reproduced by the real-final complete-call timing and is withdrawn. The new timing includes the full model call and must not be described as isolated operator overhead.

### Historical Artifact Treatment

The earlier consolidation reports and generated figures are retained as historical records. Their accuracy, logit, latency, throughput, and Pareto values are explicitly invalid for publication claims. The separate consolidation q-ablation and random-basis CSVs may only support audited operator-space quantities such as $\|JE\|$; they are not classification or deployment evidence. Real-final empirical outputs supersede all proxy-derived practical accuracy/runtime conclusions.

---

### 2.2 Feature-PCA Random Control Reconciliation
- **Discrepancy:** Previous drafts stated that "Feature-PCA achieves Cohen's $d > 2.0$ across all architectures" and claimed this "proves the true data-generating covariance".
- **Operator-space source only:** `outputs/fungibility_final_consolidation/final_random_basis_control.csv` ($N=100$ held-out operator-space images, 25 seeds per architecture); it is not Top-1 or runtime evidence.
- **Audit Finding:** The exact Cohen's $d$ effect sizes at $q=16$ are:
  - **DeiT-Tiny:** $d = 1.46$ ($t = -14.55, p = 2.45 \times 10^{-26}$)
  - **DeiT-Small:** $d = 2.66$ ($t = -26.49, p = 9.96 \times 10^{-47}$)
  - **ViT-Base:** $d = 1.77$ ($t = -17.56, p = 3.51 \times 10^{-32}$)
  - **DINOv2:** $d = 1.59$ ($t = -15.82, p = 7.29 \times 10^{-29}$)
- **Resolution:**
  - Removed "Cohen's $d > 2.0$ across all architectures".
  - Replaced with exact range: $d \in [1.46, 2.66]$ (all $p < 10^{-25}$).
  - Replaced causal over-claims ("proves the true data-generating covariance") with rigorous phrasing: *"controlled basis interventions show that Feature-PCA directions produce significantly lower downstream functional error than matched random orthonormal subspaces across all four architectures (all $p < 10^{-25}$), supporting the functional relevance of learned feature covariance directions."*

---

### 2.3 Stabilized Oracle Error & Denominator Hygiene in Table 4
- **Discrepancy:** Table 4 in earlier drafts reported "Full Oracle $\|JE\| = 1.82$" and "$q=16$ $\|JE\| = 7.45$".
- **Authoritative Source:** `docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md` and `outputs/fungibility_final_consolidation/final_q_ablation.csv`.
- **Audit Finding:**
  - The true stabilized full unconstrained oracle ($\lambda = 10^{-3}$) achieves $\|JE\| = 0.0196 \approx 0.020$ on DeiT-Small (not 1.82). The number 1.82 was an approximate residue from an older unregularized run.
  - The exact audited operator-space $\|JE\|$ values for DeiT-Small are Group Mean ($q=0$): $12.5234$; restricted oracle $q=8$: $8.0663$; $q=16$: $6.6023$; $q=32$: $3.5164$; $q=64$: $0.9937$; and stabilized full oracle ($r=32$): $0.0196$. Gains and recoveries use their explicitly stated operator-space denominators. No Top-1 values from this historical CSV are treated as measured classification results.
  - For Static Calibration ($\bar{\alpha}$ at $q=16$): $\|JE\| = 9.2724$, reducing error by $3.2510$. This recovers **$54.91\%$ of the restricted oracle gain** ($3.2510 / 5.9211$) and **$26.00\%$ of the full oracle gain** ($3.2510 / 12.5038$).
- **Resolution:**
  - Updated Table 4 with the exact audited values.
  - The earlier Denominator A (>98% low-rank Jacobian benefit) statement was withdrawn after recomputing its stated Top-1 ratio from the strict confirmatory CSVs. Only 4 of 22 positive-denominator rank/budget settings exceed 98%; 16 settings have negative denominators and 2 have zero denominators, so no universal recovery fraction is supported. Denominator B (restricted carrier oracle recovery of stabilized full oracle: $47.4\%$, $72.0\%$, $92.2\%$) and Denominator C (static alpha recovery of restricted oracle: $54.91\%$) remain distinct operator-space claims.

---

### 2.4 Sample Size Mapping ($N=1000$ vs $N=100$)
- **Discrepancy:** Earlier summaries conflated the $N=1000$ sample size of initial static replacement experiments with the $N=100$ held-out evaluation set of expensive Jacobian operator benchmarks.
- **Resolution:** An explicit sample size mapping was established and documented across all sections:
  - **$N=1000$ Canonical Validation Set:** Used for static substitution depth curves (§4, Table 1, Figure 2), margin damage recovery (DeiT-T 93.8%, DeiT-S 97.5%, DINOv2 93.4%), geometric coordinate/sign control ablations (§5, Table 2, Figure 3), and token diversity sweeps (§6, Figure 3).
  - **$N=500$ Calibration / $N=100$ Held-Out Evaluation Set:** Used for the historical downstream Jacobian evaluations, carrier-space $q$-ablation (§8, Table 4, Figure 7), matched random-basis operator-space controls (§8, Table 3, Figure 4), static calibration generalization (§8.4), and clean-state risk-gating audit (§9.1). These are not the new practical carrier accuracy or end-to-end timing sample sizes. Real-final classification uses N=1,000 per architecture; real-final timing uses 50 warmups and 100 measured iterations per batch/method on synthetic image tensors passed through actual models.

---

### 2.5 Static Alpha Language
- **Discrepancy:** The claim "zero runtime FLOPs" for static calibration was imprecise.
- **Resolution:** Replaced with "zero learned predictor FLOPs" and "no image-conditioned prediction network is required". Clarified that the static correction $\delta C = \mathbf{1}_M (R \bar{\alpha})^\top$ is precomputed offline during calibration, requiring only an elementwise vector addition to surviving tokens during inference.

---

### 2.6 Restoration of Close Prior Art
- **Discrepancy:** Key close prior works identified during project research were absent from Related Work (§2).
- **Resolution:** Restored and positioned:
  - **Output-Aware Residual Stream Pruning \citep{outputaware2026}:** Models output distribution sensitivity in LLMs via second-order Taylor approximation.
  - **FishBack \citep{fishback2026}:** Pullback Fisher geometry for activation steering.
  - **UniTAC \citep{unitac2026}:** Universal task-aware compression for ViTs using token-level conditioning.
  - **J-BI (Jacobian-Lens Weighting) \citep{jbi2026}:** Depth pruning accounting for downstream impact via Jacobian Lens.
  - **SVD-Prune & SliceGPT \citep{ashkboos2024slicegpt}:** SVD-based low-rank projection in transformer streams.
  - **DINOv2 \citep{oquab2024dinov2}:** Updated citation to peer-reviewed publication in *Transactions on Machine Learning Research (TMLR)*, 2024.
  - Narrowed our novelty claim: not generic Jacobians, not generic SVD, but the specific discovery of late patch content fungibility, attention cancellation mechanics, and constructive implicit carrier-space optimization.

---

### 2.7 Reproducibility Statement
- **Discrepancy:** Claimed repository open-sources all "pretrained model weights".
- **Resolution:** Corrected to state that the repository provides "code, model checkpoint identifiers (accessible via `timm` and official release repositories), evaluation scripts, calibration protocols, and consolidation manifests."

---

## 3. Corrected Source-of-Truth Hierarchy

For empirical claims, use this priority: (1) strict audited raw empirical outputs; (2) `outputs/fungibility_real_final/` for practical carrier classification and runtime; (3) `outputs/fungibility_operator_compression_confirmatory/` and `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md` for strict N=1,000 operator-aware compression; and (4) mechanistic raw outputs with their validation manifests. Historical reports are secondary. The earlier consolidated accuracy, throughput, and Pareto tables are excluded as proxy-derived. The separately audited q-ablation and random-basis files may be cited only for verified operator-space measurements, explicitly labeled as such.

---

## 4. Verification Verdict

The check-10 publication-source repair removes proxy accuracy/runtime/frontier values from the claims table, traceability, experiment summary, and this report. `docs/PAPER_DRAFT.md` was intentionally not edited in this task and still requires the subsequent publication-lockdown pass. Therefore this report does not certify that all manuscript documents are mutually reconciled.
