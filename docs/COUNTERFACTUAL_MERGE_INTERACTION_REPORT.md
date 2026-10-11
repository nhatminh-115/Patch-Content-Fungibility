# Diagnosing merge-action interactions in Patch-Content Fungibility

**Date:** 2026-10-11. **Branch:** `research/merge-action-interactions`, stacked on PR #4. **Frozen protocol:** [COUNTERFACTUAL_MERGE_INTERACTION_PROTOCOL.md](COUNTERFACTUAL_MERGE_INTERACTION_PROTOCOL.md), committed as `0f074b4` before any new model forwards. **Recommendation:** **Path B — interaction-aware merging**, as a research direction only. No new predictor was trained and neither PR was merged.

## Executive result

The failure has more than one component. In the original 196-patch state, the frozen student selects 16 actions whose **summed individual downstream distortions** are much larger than those selected by the independent oracle. This accounts for 91% of the mean student–oracle completed-set gap for DeiT-Small and 86% for ViT-B on the 64-image internal-validation cohort. A good top-1 action or global rank correlation does not guarantee a good *admissible set of 16*: the student chooses damaging actions farther down its constrained ranking. Conditional greedy selection also beats independent oracle selection, by 19.8% of independent-oracle distortion for DeiT-Small. It selects slightly costlier individual actions but gains from less aligned output error and a smaller non-additive response. The frozen student's regret additionally rises on its own compressed-state distribution, including at matched 147- and 98-patch counts.

Thus H1 (set-relevant single-action ranking error), H2 (joint-action effects), and H3 (state-policy shift) all have support, with different magnitudes. The frozen D2 gate passes for DeiT-Small, so its pre-registered recommendation priority selects Path B. This result does **not** establish that an efficient interaction-aware policy can be learned or that it will speed up inference. The current student remains worse than cosine.

## Design and provenance

We reused PR #4's frozen DeiT-Small Block 8 and ViT-B/16 AugReg Block 7 checkpoints, FP32 transforms/prefix/suffix/classifiers, clean-logit target, multiplicity-aware attention, and 32-candidate even-source/odd-destination pool. The primary pool follows the PR #4 teacher-label seed, including the architecture offset. A separate sensitivity run uses the deployment rollout seed, which omits that offset for ViT-B. Every method sees exactly the same pool within an image. Sources are unique and disjoint from destinations; destinations may receive several sources. All set evaluations apply original-state candidate identities simultaneously to the original 196-patch activation. All 192 images had 16 admissible actions.

The 64-image `stability` cohort previously selected the frozen student checkpoint. The separate 128-image `pilot` cohort also appeared in PR #4. Neither is a new independent confirmatory set. Both consist only of seed-9101 calibration-side ImageNet images partitioned by seed 64011. The canonical seed-9201 held-out set was not accessed. We did not edit the PCF manuscript, supplementary material, historical outputs, model weights, or the validated compression implementation. The runner records global image IDs, source snapshot filenames, model/checkpoint hashes, seeds, software, timing, and GPU memory in [manifests](../outputs/merge_interaction_diagnostic/).

The target `D` is mean squared **centered** compressed-logit difference from centered clean logits, divided by squared centered clean-logit norm plus `1e-8`. Lower is better. The teacher is an actual frozen-suffix forward for every counterfactual set; it is an offline diagnostic, not deployable inference. Paired 95% percentile intervals use 2,000 image-level bootstrap resamples with seed 75012. All reported relative changes divide cohort mean distortions; absolute scales remain primary.

## A/C: first-round ranking and set selection

At 16 merges, the primary 64-image means are:

| Model | Cosine | Frozen student | Independent oracle | Conditional greedy oracle |
|---|---:|---:|---:|---:|
| DeiT-Small | `3.743e-4` | `1.992e-3` | `1.404e-4` | `1.126e-4` |
| ViT-B | `9.806e-5` | `3.369e-4` | `4.202e-5` | `3.681e-5` |

The paired contrasts below are **left minus right**, so positive values favor the right-hand policy:

| Model / cohort | Cosine − independent oracle | Independent − conditional | Student − independent |
|---|---:|---:|---:|
| DeiT / 64 | `2.339e-4` [`1.629e-4`, `3.124e-4`] | `2.781e-5` [`1.290e-5`, `4.452e-5`] | `1.851e-3` [`1.209e-3`, `2.636e-3`] |
| ViT / 64 | `5.604e-5` [`1.113e-5`, `1.160e-4`] | `5.214e-6` [`1.792e-6`, `9.372e-6`] | `2.949e-4` [`2.030e-4`, `3.880e-4`] |
| DeiT / 128 | `4.210e-4` [`2.900e-4`, `5.620e-4`] | `2.8e-5` [`1.7e-5`, `4.1e-5`] | `2.168e-3` [`1.635e-3`, `2.822e-3`] |
| ViT / 128 | `6.1e-5` [`2.1e-5`, `1.11e-4`] | `9e-6` [`4e-6`, `1.6e-5`] | `5.46e-4` [`2.22e-4`, `1.032e-3`] |

The independent oracle uses **only** true one-action D to rank candidates. It beats cosine after a full 16 merges on both architectures, so single-action labels contain actionable set-level information. Conditional greedy evaluates the actual D of adding each candidate to its selected set. It gains a further 19.8% over independent selection on DeiT, meeting the frozen `1e-5` absolute floor; ViT's 12.4% relative improvement is only `5.21e-6`, so D2 fails there on absolute scale. The 128-image replication has the same signs. [The curve figure](../outputs/merge_interaction_diagnostic/distortion_curves.png) and [all prefix means](../outputs/merge_interaction_diagnostic/curve_summary.csv) show k=1,2,4,8,16; conditional and independent are identical at k=1 by construction, then gradually separate. The [per-image selected indices and outcomes](../outputs/merge_interaction_diagnostic/curve_first_stability.csv) permit paired reanalysis.

One-action **top-1** regret at 196 is a weaker predictor of this result. On the 64-image cohort, mean regret is `5.86e-6` cosine versus `7.29e-6` student for DeiT, and `1.26e-7` versus `2.56e-6` for ViT. The paired student-minus-cosine intervals include zero for both (`[-6.27e-6, 1.08e-5]` and `[-1.42e-8, 5.92e-6]`). On the 128-image cohort, DeiT's student even has lower mean top-1 regret (`5.26e-6` versus `1.36e-5`, interval spanning zero), while its completed 16-action set is still much worse. Mean Spearman rank agreement on the 64 images is `0.400` student versus `0.363` cosine for DeiT, and `0.680` versus `0.662` for ViT. Top-1 agreement with the oracle is `35.9%`/`53.1%` for the student. These broad ranking summaries miss the constrained top-16 damage. The student's selected set overlaps the independent oracle by only `10.3/16` actions for DeiT and `13.1/16` for ViT, versus `12.9/16` and `14.6/16` for cosine. See [rank summaries](../outputs/merge_interaction_diagnostic/rank_summary.csv) and [candidate costs and scores](../outputs/merge_interaction_diagnostic/candidates_first_stability.csv).

### Exact set-error accounting

For each selected set we computed (i) the sum of its true one-action distortions, (ii) the extra squared-error term from adding its centered one-action logit vectors, and (iii) actual set D minus that additive-logit prediction. The three terms sum to actual set D, up to rounding. This accounting is functional, not a causal attribution to a transformer pathway.

| 64-image model and contrast | Difference in summed one-action D | Output-alignment contribution | Non-additive contribution | Actual D difference |
|---|---:|---:|---:|---:|
| DeiT, student − independent | `+1.693e-3` | `−0.003e-3` | `+0.162e-3` | `+1.851e-3` |
| ViT, student − independent | `+0.253e-3` | `+0.026e-3` | `+0.016e-3` | `+0.295e-3` |
| DeiT, independent − conditional | `−1.0e-5` | `+2.2e-5` | `+1.7e-5` | `+2.8e-5` |
| ViT, independent − conditional | `−5e-6` | `+6e-6` | `+3e-6` | `+5e-6` |

For student versus independent, the sum-of-single-action difference has a positive paired interval on both models: DeiT `[1.092e-3, 2.450e-3]`, ViT `[1.76e-4, 3.36e-4]`. For independent versus conditional on DeiT, conditional deliberately gives up about `1.0e-5` in summed individual cost but recovers `2.2e-5` from less aligned output change and `1.7e-5` from less non-additive response; both latter differences have positive paired intervals. This directly separates the dominant student ranking problem from the smaller, real joint-selection headroom. [Per-image decomposition](../outputs/merge_interaction_diagnostic/selection_decomposition.csv) and [paired component intervals](../outputs/merge_interaction_diagnostic/decomposition_paired_contrasts.csv) are available.

The rollout-pool sensitivity reproduces the PR #4 first-round trace: DeiT student/cosine `1.992e-3`/`3.743e-4`; ViT student/cosine `4.51e-4`/`9.81e-5`. Independent and conditional oracles still beat cosine on this pool ([paired sensitivity contrasts](../outputs/merge_interaction_diagnostic/rollout_pool_paired_contrasts.csv)). This guards against attributing the result solely to the teacher-label pool used in the primary comparison.

## B: pair interactions and logit mechanism

Five deterministic, admissible pair categories were selected per image: high cosine; high independent-oracle rank; high-cosine/high-damage; low-damage with distinct destinations; and low-damage with a shared destination. All categories were available for all 64 images/model. Categories can overlap and are deliberately selected, so their frequencies do not estimate the frequency among all possible pairs. [The interaction distribution figure](../outputs/merge_interaction_diagnostic/pair_interaction_distribution.png), [category summary](../outputs/merge_interaction_diagnostic/pair_summary.csv), and [per-pair values](../outputs/merge_interaction_diagnostic/pairs_first_stability.csv) provide the full distribution.

| Pair category, 64 images | DeiT mean `I`; positive fraction | ViT mean `I`; positive fraction |
|---|---:|---:|
| High cosine | `2.28e-6`; `70.3%` | `1.05e-8`; `64.1%` |
| High oracle | `1.05e-7`; `89.1%` | `6.74e-9`; `56.3%` |
| Low damage, distinct destination | `8.84e-8`; `85.9%` | `−2.40e-9`; `54.7%` |
| Low damage, shared destination | `3.03e-5`; `96.9%` | `1.27e-6`; `84.4%` |

The shared-minus-distinct low-damage pair difference is `3.02e-5` [`2.80e-6`, `6.56e-5`] for DeiT and `1.27e-6` [`3.61e-7`, `2.73e-6`] for ViT. Shared-carrier competition is therefore a strong functional interaction in this controlled sample. Its mean non-additive scalar remainder is `2.79e-5` DeiT and `1.15e-6` ViT; the corresponding simple additive-vector cross terms are `2.39e-6` and `1.15e-7`. By contrast, low-damage distinct-destination pairs have nearly zero mean non-additive remainder, while their centered perturbations still have mean cosine alignment `0.255` DeiT and `0.055` ViT. Positive scalar `I` alone would have conflated these mechanisms. At k=16 the median vector residual `||R(A)||/||Σ delta_a||` is `0.228`/`0.233` for independent selection on DeiT/ViT; the residual is measurable but does not by itself identify any exclusive Value path. The results are consistent with PCF's broader coherent accumulation/cancellation theme, without establishing the pathway responsible here.

## D: matched-count state-policy diagnosis

Because D1/D2 established oracle headroom, D was entered. The table reports mean frozen-student one-action teacher regret on 64 matched images; the final column is student-state minus ToMe-state with paired 95% interval:

| Model | Count | ToMe state | Student-generated state | Difference [95% CI] |
|---|---:|---:|---:|---:|
| DeiT | 180 | `4.1e-5` | `8.9e-5` | `4.8e-5` [`1.1e-5`, `9.1e-5`] |
| DeiT | 164 | `3.7e-5` | `1.95e-4` | `1.58e-4` [`9.0e-5`, `2.36e-4`] |
| DeiT | 147 | `1.20e-4` | `5.81e-4` | `4.61e-4` [`2.05e-4`, `8.12e-4`] |
| DeiT | 98 | `7.46e-4` | `1.913e-3` | `1.167e-3` [`5.94e-4`, `1.865e-3`] |
| ViT | 180 | `5.5e-5` | `9.8e-5` | `4.2e-5` [`0.6e-5`, `8.6e-5`] |
| ViT | 164 | `1.89e-4` | `2.42e-4` | `5.3e-5` [`−8.4e-5`, `1.93e-4`] |
| ViT | 147 | `1.39e-4` | `5.45e-4` | `4.06e-4` [`2.10e-4`, `7.01e-4`] |
| ViT | 98 | `8.20e-4` | `2.152e-3` | `1.332e-3` [`3.78e-4`, `2.441e-3`] |

The new 180/164 counts show deterioration already at unseen levels, although ViT's matched 164 contrast is uncertain. The 147/98 matched-state differences are robust on both models. Student score–teacher cost Spearman correlation at 147 drops from `0.294` on ToMe states to `0.017` on student-generated states for DeiT, and from `0.134` to `−0.053` for ViT; at 98 the corresponding values are `0.160` to `−0.028` and `−0.054` to `−0.099`. [State summary](../outputs/merge_interaction_diagnostic/state_summary.csv) and [paired state contrasts](../outputs/merge_interaction_diagnostic/state_paired_contrasts.csv) include all methods/counts. The self-generated states differ in both selected actions and accumulated distortion; this observational contrast supports a state-distribution contribution but does not identify which state feature causes it.

## Frozen decisions and recommendation

| Gate | DeiT-Small | ViT-B | Interpretation |
|---|---|---|---|
| D1: independent oracle beats cosine at 16 | **GO** | **GO** | True one-action labels provide actionable headroom. |
| D2: conditional beats independent at 16 | **GO** | **KILL** | DeiT passes absolute, relative, interval, and replication-sign rules; ViT misses the `1e-5` absolute floor. |
| D3: student gap explains rollout failure | **GO** | **GO** | Student–oracle completed-set gaps are large; the per-action-sum audit locates most of the gap in selected individual damage. |
| D4: state-shift contribution | **GO** | **GO** | Matched 147/98 student-generated states have materially higher regret. |

The [machine-readable gate record](../outputs/merge_interaction_diagnostic/gates.json) applies the pre-committed thresholds. **Path B — interaction-aware merging** is the single recommendation because D2 passes for DeiT. The smallest sensible follow-up would test whether a cheap approximation to conditional set cost can retain that modest oracle gain **while fixing the much larger selected-action cost problem**; that is a future protocol and requires review. The present study does not authorize training or deployment. If a practical approximation cannot beat independent oracle selection on a new calibration-side split, the interaction-aware path should be abandoned.

## Validity, compute, and reproducibility

The 2-image/model correctness/runtime pilot preceded full evaluation. Tests include simultaneous multi-action carrier equivalence, repeated-destination mass conservation, original CLS preservation, source constraints, batched multi-action suffix parity against the validated legacy suffix, evaluator caching, and a synthetic additive-logit case where positive pair `I` occurs with zero response residual. **15 tests passed.** Across the full first-round runs, no-merge parity had zero observed maximum logit discrepancy against the full pretrained model. Exact 196→180 counts and total mass 196 were checked. FP32 frozen pretrained suffixes and classifiers were used throughout.

The final four full passes (64 primary, 128 replication, 64 state, 64 rollout-pool sensitivity) took `494.5 s` wall time, approximately `0.137 GPU-hours` on the RTX 5070 Laptop GPU. They performed `200,187` distinct cached teacher set evaluations, with `208.9 s` spent in synchronized batched teacher suffix calls; PyTorch-reported peak allocated GPU memory was `432.2 MiB` (CUDA context excluded). The initial smoke runs and a repeated 64+128 audit pass bring all diagnostic execution to about `0.21 GPU-hours`, below the frozen four-hour budget. Oracle teacher time is kept separate from practical student inference; no G3 latency/speedup claim is made. Per-phase [runtime manifests](../outputs/merge_interaction_diagnostic/) include exact times and memory. The score-state study's reported teacher count excludes student rollout/scoring work, while its wall time includes it.

Reproduce from the PR #4 branch plus this branch, with the same public ImageNet parquet snapshot cached and the PR #4 frozen checkpoints present:

```text
python -m pytest -q tests/test_merge_interaction_diagnostic.py tests/test_counterfactual_merge.py
python scripts/run_merge_interaction_diagnostic.py --phase first --cohort stability
python scripts/run_merge_interaction_diagnostic.py --phase first --cohort pilot
python scripts/run_merge_interaction_diagnostic.py --phase state --cohort stability
python scripts/run_merge_interaction_diagnostic.py --phase first --cohort stability --candidate-schedule rollout
python scripts/summarize_merge_interaction_diagnostic.py
```

The source scripts explicitly request the seed-9101 calibration partition. They do not refer to seed 9201. Per-image and aggregate artifacts are under [`outputs/merge_interaction_diagnostic/`](../outputs/merge_interaction_diagnostic/). The restricted 32-edge pool is an upper bound only inside that candidate space, and the two architectures use one pretrained checkpoint each. The tests and image cohorts support a mechanistic diagnostic within that scope, not a new benchmark or a practical compression claim.
