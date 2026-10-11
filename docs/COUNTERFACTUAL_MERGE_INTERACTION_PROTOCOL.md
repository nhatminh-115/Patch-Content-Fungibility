# Frozen protocol: merge-action interactions

**Frozen before new diagnostic model forwards.** Branch `research/merge-action-interactions` starts at PR #4 commit `9ad8e0f`. This protocol is committed before the correctness/runtime pilot and data collection. No weights are trained or modified.

## Questions and hypotheses

- H1: at 196 patches, the frozen student ranks actual single-action damage poorly enough to explain its first-round failure.
- H2: independently favorable actions compose poorly; true conditional set selection improves completed-round distortion.
- H3: the frozen student's ranking degrades at unseen counts (180, 164) or on its own compressed-state distribution versus ToMe states at matched count.

These explanations can coexist. A positive scalar pair interaction is not by itself evidence of nonlinear transformer response, because squared logit error has a cross term even for additive perturbations.

## Population, intervention, and sampling

Use only PR #4 seed-9101 calibration images and seed-64011 partitions: 64 `stability` images first, then the separate 128 `pilot` images for decisive A–C replication if the measured runtime allows. The 64 images selected the PR #4 student checkpoint; both cohorts have previously been used in research and are exploratory, not independent confirmation. Never read or sample seed 9201. Evaluate frozen DeiT-Small Block 8 and ViT-B/16 AugReg Block 7 in FP32 using the PR #4 transform, prefix, suffix, classifier, candidate-pool seed, and multiplicity bias. Record image IDs, model checkpoint hashes, software, GPU, total runtime, teacher-forward time/count, and peak GPU memory.

For each image/model start at its original 196-patch state. Construct the existing deterministic 32-edge pool once. All policies use this pool, original even-source/odd-destination indices, unique sources, and sources disjoint from destinations; repeated destinations are allowed. Select at most 16; record any lower feasible maximum. `apply_actions` evaluates every set against the original state, retaining CLS and mass-weighted carriers. D is squared centered logit distance from the clean logits divided by squared centered clean-logit norm plus `1e-8`.

## A and C: first-round policies and estimands

Rank candidates by descending cosine, ascending frozen `counterfactual_pair` score, or ascending actual *one-action* D. Choose the first admissible 16 in each ranking. The latter is the **independent oracle**: it sees no multi-action outcomes. The **conditional greedy oracle** starts empty and at each step computes actual D for each admissible set formed by adding one remaining edge; select minimum D, ties by candidate index. Candidate identities remain fixed to the original state. Compare actual D of prefixes k=1,2,4,8,16 for all four methods. Primary paired contrasts at k=16 are cosine minus independent oracle (D1), independent minus conditional (D2), and student minus independent/conditional (D3). Also report cosine/student single-action teacher regret, Spearman rank correlation with teacher costs, top-1 agreement, and selection overlap. No oracle timing is counted as practical inference.

Image is the sampling/bootstrap unit. For each architecture/cohort/contrast use 2,000 paired image-resamples with fixed seed 75012, 95% percentile intervals on the mean absolute D difference. Relative improvement is the difference of cohort mean D divided by the reference mean D and is descriptive. Show absolute scales, particularly near zero.

## B: functional interactions

At 196 choose up to five distinct admissible pairs per image, with deterministic ties: top-two cosine actions; top-two single-action-oracle actions; highest-cosine high-damage action paired with the highest-cosine admissible other action; lowest-damage admissible pair with different destinations; lowest-damage admissible pair with a shared destination. High damage means the action with maximum one-action D among the top cosine half of the pool. A missing stratum is reported. Deduplicate identical action pairs for suffix execution, retain category labels for analysis. Compute `I(a,b)=D(ab)-D(a)-D(b)+D(empty)`. Compute centered perturbations `delta_a`, `delta_b`, alignment cosine, additive squared-error prediction, and residual vector `R(ab)=delta_ab-delta_a-delta_b`. At selected-set prefixes also compute `R(A)` and its norm divided by the norm of summed individual perturbations (with `1e-12` floor), and predicted additive-output D. Report positive/negative I frequencies and the observed contributions of additive output alignment and non-additivity; label the latter a functional residual, not exclusive Value-path causation.

## D: conditional state-distribution diagnosis

Enter D only if A–C show useful oracle headroom: D1 or D2 passes in at least one architecture and the absolute improvement is at least `1e-5` there. If entered, evaluate counts 180, 164, 147, 98 for existing ToMe-generated states and student-generated states at matched counts where feasible. Use the frozen student, cosine, and true one-action oracle on a new pool at each state. Teacher labels are actual suffix outcomes from that state. Report mean one-action regret, Spearman rank correlation, top-1 agreement, and matched paired differences by policy/count. The student state at a target count is produced by the PR #4 greedy scoring rollout with a final partial round; the ToMe state is constructed from the original activation. This comparison is observational with respect to state policy, because action histories differ.

## Gates and stopping

- **D1 GO:** at k=16 independent oracle beats cosine by at least `1e-5` absolute D and 10% relative mean D, with paired bootstrap lower 95% bound above zero, on the 64-image cohort; pilot replication must have the same sign if run. Otherwise D1 KILL.
- **D2 GO:** conditional greedy beats independent oracle by the same absolute, relative, and interval criteria; replication sign must agree if run. Otherwise D2 KILL. Conditional oracle must also beat cosine to be actionable.
- **D3 GO (ranking bottleneck):** D1 passes, student-minus-independent D at k=16 has lower paired bound above zero, and this difference is at least 50% of student-minus-cosine completed-round D. Otherwise D3 KILL or INDETERMINATE when denominator is nonpositive. This gate concerns explanatory magnitude, not successful learning.
- **D4 GO:** after D entry, student regret on self-generated states exceeds matched ToMe states at count 147 or 98 by at least `1e-5` and 20% of ToMe regret, with positive paired lower bound; alternatively at 180 or 164 student regret exceeds count-196 regret by the same criteria. Report the two comparisons separately, rather than inferring state shift from a pooled value. Otherwise D4 KILL; NOT ENTERED if D is skipped.

Recommendation priority: Path B if D2 GO; otherwise Path A if D1 and D3 GO; otherwise Path C if D4 GO; otherwise Path D KILL. The path is only a recommendation. If conditional greedy cannot beat cosine by `1e-5`, 10%, and positive lower bound in any architecture, stop algorithm development and select Path D. These thresholds are operational diagnostics, not proof of generalization.

## Compute and validation

Run unit tests including simultaneous multi-action equivalence, CLS preservation, exact counts, and mass conservation. Then run a 2-image/model correctness/runtime pilot, verifying original-state suffix parity with the clean full model within `5e-4`. Batch equal-length candidate sets (initial maximum batch 8) and cache clean logits, prefix activations, one-action logits, and repeated action sets. Use synchronized CUDA timing. Target at most 4 GPU-hours and 8 GB peak; if projected beyond this, retain the 64-image first-round A–C test and omit replication/D in that order. Any deviation is documented before interpreting outcomes. Write raw per-image measurements, paired summaries, and a reproducibility manifest under `outputs/merge_interaction_diagnostic/`.
