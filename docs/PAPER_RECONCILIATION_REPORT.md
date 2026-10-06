# Paper Reconciliation & Source-of-Truth Audit Report

**Repository:** [Patch-Content-Fungibility](https://github.com/nhatminh-115/Patch-Content-Fungibility)  
**Date:** October 7, 2026  
**Status:** Authoritative Post-Audit Release  
**Commit Reference:** `db9f460`  

---

## 1. Executive Summary

This report documents the final source-of-truth reconciliation conducted on `docs/PAPER_DRAFT.md` and supporting documents. The objective was to eliminate all stale, unverified, or contradictory numerical claims and align the paper strictly with the raw consolidated CSV outputs (`outputs/fungibility_final_consolidation/`) and prior mathematical audits (`docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md`).

All numerical values, claims, and bibliographic references have been verified, resulting in a fully auditable manuscript where every number maps directly to an authoritative source file.

---

## 2. Discrepancies Identified & Reconciled

### 2.1 Throughput & Pareto Frontier Reconciliation
- **Discrepancy:** Previous drafts claimed that the Selective Feature-PCA Carrier strictly "Pareto-dominates" the Hybrid Group Mean baseline, citing preliminary throughput figures ($4357.8\text{ vs }4199.9\text{ img/s}$).
- **Authoritative Source:** `outputs/fungibility_final_consolidation/final_pareto_frontier.csv` and `final_throughput_table.csv` ($BS=64$, 50% token budget at Depth 8).
- **Audit Finding:** In the final consolidated benchmark:
  - On **DeiT-Small**: Hybrid Group Mean achieves $7153.5\text{ img/s}$ at $76.67\%$ Top-1. Selective Feature-PCA Carrier achieves $4432.0\text{ img/s}$ at $77.20\%$ Top-1.
  - On **ViT-Base**: Group Mean achieves $3474.6\text{ img/s}$ at $77.15\%$ Top-1. Selective Carrier achieves $2051.3\text{ img/s}$ at $77.60\%$ Top-1.
  - On **DINOv2**: Group Mean achieves $4049.6\text{ img/s}$ at $84.32\%$ Top-1. Selective Carrier achieves $3494.2\text{ img/s}$ at $84.34\%$ Top-1.
  - On **DeiT-Tiny**: Group Mean achieves $14076.3\text{ img/s}$ at $71.16\%$ Top-1. Selective Carrier achieves $11967.2\text{ img/s}$ at $71.28\%$ Top-1.
- **Resolution:** By strict mathematical definition, method $A$ Pareto-dominates $B$ if and only if $\text{acc}_A \ge \text{acc}_B$ AND $\text{throughput}_A \ge \text{throughput}_B$ with at least one strict inequality. Because Selective Carrier has higher accuracy (+0.53 pp on DeiT-Small) but lower throughput due to gating logic, **all claims of strict Pareto dominance over Group Mean have been removed**. The relationship is now accurately characterized as an **accuracy-throughput tradeoff frontier**, where Selective Carrier establishes an accuracy-prioritizing operating point along the frontier.

---

### 2.2 Feature-PCA Random Control Reconciliation
- **Discrepancy:** Previous drafts stated that "Feature-PCA achieves Cohen's $d > 2.0$ across all architectures" and claimed this "proves the true data-generating covariance".
- **Authoritative Source:** `outputs/fungibility_final_consolidation/final_random_basis_control.csv` ($N=100$ held-out evaluation images, 25 seeds per architecture).
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
  - The exact audited $\|JE\|$ values for DeiT-Small are:
    - Group Mean ($q=0$): $12.5234$
    - $q=8$: $8.0663$ (gain: $4.4571$, recovery of full oracle: $35.6\%$)
    - $q=16$: $6.6023$ (gain: $5.9211$, recovery of full oracle: $47.4\%$)
    - $q=32$: $3.5164$ (gain: $9.0070$, recovery of full oracle: $72.0\%$)
    - $q=64$: $0.9937$ (gain: $11.5297$, recovery of full oracle: $92.2\%$)
    - Stabilized Full Oracle ($r=32$): $0.0196$ (gain: $12.5038$, recovery: $100.0\%$)
  - For Static Calibration ($\bar{\alpha}$ at $q=16$): $\|JE\| = 9.2724$, reducing error by $3.2510$. This recovers **$54.91\%$ of the restricted oracle gain** ($3.2510 / 5.9211$) and **$26.00\%$ of the full oracle gain** ($3.2510 / 12.5038$).
- **Resolution:**
  - Updated Table 4 with the exact audited values.
  - Strictly separated Denominator A (low-rank Jacobian SVD benefit $>98\%$), Denominator B (restricted carrier oracle recovery of stabilized full oracle: $47.4\%$, $72.0\%$, $92.2\%$), and Denominator C (static alpha recovery of restricted oracle: $54.91\%$).

---

### 2.4 Sample Size Mapping ($N=1000$ vs $N=100$)
- **Discrepancy:** Earlier summaries conflated the $N=1000$ sample size of initial static replacement experiments with the $N=100$ held-out evaluation set of expensive Jacobian operator benchmarks.
- **Resolution:** An explicit sample size mapping was established and documented across all sections:
  - **$N=1000$ Canonical Validation Set:** Used for static substitution depth curves (§4, Table 1, Figure 2), margin damage recovery (DeiT-T 93.8%, DeiT-S 97.5%, DINOv2 93.4%), geometric coordinate/sign control ablations (§5, Table 2, Figure 3), and token diversity sweeps (§6, Figure 3).
  - **$N=500$ Calibration / $N=100$ Held-Out Evaluation Set:** Used for downstream Jacobian evaluations, carrier-space $q$-ablation (§8, Table 4, Figure 7), matched random basis controls (§8, Table 3, Figure 4), static calibration generalization (§8.4), clean-state risk gating (§9.1), and latency/throughput profiling (§9.2, Table 5, Table 6).

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

## 3. Authoritative Source-of-Truth Hierarchy

For all ongoing and future documentation, numbers must adhere to the following priority hierarchy:
1. **Strict Audit Reports:** `docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md` and `docs/PAPER_FINAL_AUDIT.md`.
2. **Final Consolidation CSVs:** `outputs/fungibility_final_consolidation/` (`final_q_ablation.csv`, `final_random_basis_control.csv`, `final_accuracy_table.csv`, `final_throughput_table.csv`, `final_pareto_frontier.csv`).
3. **Canonical Confirmatory N=1000 Experiments:** `outputs/fungibility_v0_figures/`, `outputs/fungibility_v0_7_figures/`, `outputs/fungibility_v1_figures/`, and `docs/DELTA_V0_5_REPORT.md`.

---

## 4. Verification Verdict

All discrepancies have been resolved. `docs/PAPER_DRAFT.md`, `docs/PAPER_FINAL_CLAIMS_TABLE.md`, `docs/PAPER_FINAL_AUDIT.md`, `docs/PAPER_FINAL_EXPERIMENT_SUMMARY.md`, and `docs/PAPER_NUMBER_TRACEABILITY.md` are now in 100% mutual numerical agreement.
