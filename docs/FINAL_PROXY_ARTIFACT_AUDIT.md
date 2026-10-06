# Final Proxy Artifact Audit

**Audited repository:** `nhatminh-115/Patch-Content-Fungibility`  
**Audited commit:** `14cf343cb0b72a21c68c642142d0adaf2346b717`  
**Generator:** `scripts/run_final_consolidation_benchmark.py`  
**Decision:** the historical consolidation is mixed evidence. Its accuracy, latency, throughput, and Pareto claims are **not publication evidence**. Existing operator-space values are potentially reusable with their original scope and provenance.

## Classification by artifact and column

| Artifact / columns | Classification | Publication use |
|---|---|---|
| `final_accuracy_table.csv`: `top1_accuracy`, `top1_drop`, `logit_l2`, `prediction_flips_pct` | `PROXY_INVALID_FOR_PAPER` | Exclude all rows. No integer correct count or per-image classification outputs are saved. |
| `final_accuracy_table.csv`: architecture, method, token budget, budget percent | `DERIVED_EXACT` (configuration only) | May describe configured settings, not evidence of measured performance. |
| `final_functional_table.csv`: `mean_je_norm` | `OPERATOR_SPACE_MEASUREMENT` | Potentially reusable as functional/operator-space data from saved activations and Jacobians. It is not Top-1 or a downstream logit measurement. |
| `final_functional_table.csv`: `error_reduction_vs_group_mean`, `stabilized_oracle_recovery_pct` | `DERIVED_EXACT` from operator-space measurements | Reusable only after checking source rows, denominators, and matching definitions. It remains an operator-space result. |
| `final_q_ablation.csv`: JE columns (`group_mean_je`, `stabilized_full_oracle_je`, `restricted_oracle_je`, `static_alpha_je`) | `OPERATOR_SPACE_MEASUREMENT` | Potentially reusable after source-target and split provenance verification. |
| `final_q_ablation.csv`: gain and recovery columns | `DERIVED_EXACT` from JE values | Operator-space only. Retain the denominator explicitly; do not imply classification benefit. |
| `final_q_ablation.csv`: `top1_accuracy`, `top1_drop` | `PROXY_INVALID_FOR_PAPER` | Exclude. These are computed from a hard-coded clean accuracy and a JE coefficient. |
| `final_random_basis_control.csv`: PCA/random JE distribution and tests | `OPERATOR_SPACE_MEASUREMENT` / `DERIVED_EXACT` | Potentially reusable as an operator-space control after provenance verification; not classification evidence. |
| `final_random_basis_control.csv`: `causal_superiority_confirmed` | `DERIVED_EXACT` boolean based on operator-space tests | Limit interpretation to the tested operator-space outcome and seeds. |
| `final_throughput_table.csv`: batch latency, per-image latency, throughput | `PROXY_INVALID_FOR_PAPER` | Exclude every value. Random activations and a hand-written toy loop are timed, not a pretrained ViT. |
| `final_pareto_frontier.csv`: throughput, latency, speedup | `PROXY_INVALID_FOR_PAPER` | Exclude; values inherit the toy benchmark. |
| `final_pareto_frontier.csv`: Top-1, Top-1 drop | `PROXY_INVALID_FOR_PAPER` | Exclude; values inherit hard-coded/heuristic accuracy. |
| `final_pareto_frontier.csv`: method and batch metadata | `DERIVED_EXACT` (configuration only) | Not evidence of a measured frontier. |
| `final_claim_manifest.json`: claims about accuracy, static generalization, and Pareto dominance | `PROXY_INVALID_FOR_PAPER` where based on proxy tables; otherwise unverified claim text | Do not cite as empirical evidence. |
| `validation_manifest.json`: 500 calibration / 100 held-out targets and figure list | `DERIVED_EXACT` provenance metadata | Establishes the target-data sample counts, not real classification evaluation. |

## Generator defects

1. **Hard-coded clean accuracy.** `ARCH_CONFIGS` assigns `clean_acc` constants (72.2, 79.8, 81.8, 84.5). These are then used as the clean Top-1 rows and as the baseline for all synthetic Top-1 rows. They are not computed from this run's labels and predictions.
2. **Heuristic Top-1.** The q-ablation computes `top1_drop = min(6.0, je_q_stat * 0.22)` and subtracts that from `clean_acc`. The method table similarly maps JE values to Top-1 using method-specific constants and caps. No classifier suffix is run for these metrics.
3. **Heuristic logit L2 and flips.** The method table multiplies heuristic JE values by fixed coefficients to produce `logit_l2` and `prediction_flips_pct`; these are not logits, predictions, or per-image comparisons.
4. **Heuristic pruning and ToMe estimates.** `je_rand_prune = je_gm * 1.55`, `je_norm_prune = je_gm * 1.42`, `je_attn_prune = je_gm * 1.35`, and `je_tome = je_gm * 1.15`. These baseline values are not measurements of those interventions.
5. **Toy latency.** `benchmark_pipeline_latency` creates random hidden states and runs a simplified repeated matrix-multiplication update. It does not load model weights, execute the registered transformer blocks, use real input preprocessing, or execute the actual compression implementations.
6. **Invalid frontier.** The Pareto table combines the synthetic classification values with the toy loop timing values; no publication frontier claim can use it.
7. **Actual operator-space work is distinct.** The script also loads saved calibration/evaluation activations and Jacobian targets. Its JE and matched random-basis calculations can be retained only as operator-space/function-transmission measurements. They do not validate Top-1, logits, flips, or latency.

## Historical outputs and figures

Preserve `outputs/fungibility_final_consolidation/` unchanged. Label it as **mixed proxy/operator-space historical consolidation artifacts; NOT authoritative for empirical accuracy or latency**. Do not silently overwrite it.

Figures in `figures/paper_final_v2/` that visualize Top-1, throughput, latency, or a Pareto frontier inherit the invalid inputs and must not be used as empirical figures. Operator-space plots may be retained only after their exact source columns and target-data provenance are checked.

## Replacement gate

The new `outputs/fungibility_real_final/` directory currently records an incomplete benchmark state. It contains no accuracy, functional, timing, or frontier result tables. No paper repair is claimed. The historical strict confirmatory result remains a separate N=1,000 actual-model benchmark; see `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md` and its raw outputs.
