# Functional set-aware token merging: gated feasibility result

**Decision: KILL under the frozen protocol.** Full 1,000-logit action-effect vectors improved offline 16-merge selection (Gate A GO), but no permitted compact random projection met Gate B. Accordingly, no student was trained and no 98/49-patch rollout or throughput claim was made. The protocol was committed as `216406b` before these evaluations; the gates and stopping rule were not changed after viewing results.

## Question and experimental scope

The preceding [pilot](COUNTERFACTUAL_MERGE_PILOT_REPORT.md) and [interaction diagnostic](COUNTERFACTUAL_MERGE_INTERACTION_REPORT.md) found that independent one-action labels left a 19.8% conditional-greedy gap on DeiT-Small after 16 simultaneous merges, while most of the old student's set deficit arose from individual action ranking. This experiment asks whether the *directions* of actual one-action output changes can close part of that gap and whether a small representation preserves the gain. It does not assume that the offline teacher can run at inference.

The frozen [protocol](FUNCTIONAL_SET_AWARE_MERGING_PROTOCOL.md) uses DeiT-Small at Block 8 and ViT-B/16 AugReg at Block 7, one pretrained model seed each, original 196-patch states, the same 32-edge teacher-label candidate pool, source-disjoint selected actions, cached equal-token suffix batches, and normalized centered-logit distortion `D`. Every method selects from the same pool; 16 merges retain exactly 180 patches. The 64-image `stability` cohort had already been used for prior checkpoint selection. The disjoint 128-image `pilot` cohort was also previously used in the research program. Both are **exploratory calibration cohorts**, not fresh held-out confirmation. No seed-9201 benchmark was read or run.

For current output error `e` and one-action centered logit changes `delta_a`, the additive teacher scores a proposed set by `||e + sum(delta_a)||² / (||center(z_clean)||² + 1e-8)`. The exact conditional greedy reference queries the suffix for enlarged sets; the additive selector only sees the 32 individual-action teacher vectors. The destination-load ablation adds `median(single-action D) × number of previously chosen actions with the same destination` to each marginal score. The hard distinct-destination ablation uses maximum-matching lookahead and is evaluated at its feasible merge count.

Paired intervals below are image-bootstrap percentile 95% intervals with 2,000 resamples, seed `76112`. A positive difference means the method named first had *more* actual distortion than the second. Reported differences are absolute `D` units, not percentage points of classification accuracy.

## Gate A: full functional vectors help offline selection

| Cohort/model | Cosine or ToMe | Independent | Independent + load | Additive | Additive + load | Conditional oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 64 DeiT-Small | 3.7433e-4 | 1.4040e-4 | 1.3408e-4 | 1.2089e-4 | **1.1641e-4** | 1.1260e-4 |
| 64 ViT-B | 9.8059e-5 | 4.2020e-5 | 4.1962e-5 | **3.8801e-5** | 3.9570e-5 | 3.6806e-5 |
| 128 DeiT-Small | 5.9409e-4 | 1.7330e-4 | 1.7927e-4 | **1.5848e-4** | 1.6004e-4 | 1.4577e-4 |
| 128 ViT-B | 1.0698e-4 | 4.5822e-5 | 4.4601e-5 | **4.0820e-5** | 4.2008e-5 | 3.6880e-5 |

Means are actual 16-merge suffix distortion, not additive predictions. `Cosine` within this 32-edge pool reproduced the validated ToMe first-round proposal up to numerical noise. The separately executed 180-patch ToMe baseline matched the proposal suffix logits within `3.10e-6` maximum absolute error on the 64 cohort, below the `5e-4` parity tolerance.

The pre-specified stability-cohort choice compares the best functional variant, **additive + load**, with the best cost-only control, **independent + load**. DeiT-Small improvement is `1.768e-5` (95% CI `[8.740e-6, 2.860e-5]`), or 13.2% of the control's mean D. It recovers **63.6%** of the independent-to-conditional `2.781e-5` gap, clearing Gate A's 50% and `1e-5` thresholds. Its remaining mean regret to conditional greedy is `3.811e-6` (CI `[1.071e-6, 6.883e-6]`). The same selected contrast has the required positive sign in the 128-image DeiT cohort: `1.924e-5` (CI `[9.942e-6, 2.975e-5]`). This is replication of a chosen contrast in reused calibration data, with potential selection optimism in the 64-image magnitude.

The corresponding ViT-B improvement is smaller: `2.392e-6` on 64 (CI `[-0.553e-6, 5.767e-6]`) and `2.593e-6` on 128 (CI `[-6.053e-6, 9.141e-6]`). Neither interval excludes zero. The unpenalized additive variant is better than the penalized variant in the 128-image DeiT cohort and in both ViT cohorts; the penalty is not consistently helpful.

The 16-merge prefix curves are in [phase_a_curves.png](../outputs/functional_set_merge/phase_a_curves.png). On 64 DeiT images, the cost-only control has mean summed selected single-action D `8.725e-5`, alignment term `3.894e-5`, and nonadditive residual `7.890e-6`. Additive + load has a *slightly higher* summed single-action D `9.416e-5`, but a much smaller alignment term `1.586e-5` and residual `6.378e-6`. Thus the gain over an already competent individual-action oracle is mainly from **less harmful output-effect alignment**, with a smaller reduction in nonadditive response; it is not a reduction in individual action cost. By contrast, cosine's selected individual costs are already much larger (`2.692e-4`), confirming that individual ranking remains the dominant gap to a deployable method. These accounting terms are exact scalar identities for the measured set and do not establish a Value-path mechanism.

Shared destinations cannot be banned blindly. On the 64-image cohort, two images per architecture admit only 15 distinct destinations; on the 128-image cohort, two DeiT images admit only 14 and two ViT images only 15. Every hard-restriction result was compared with each unrestricted policy at **the same image-specific cardinality**. Against unrestricted additive selection, the hard restriction increased mean D by `2.968e-4` on 64 DeiT (paired unrestricted-minus-hard CI `[-5.838e-4, -1.276e-4]`) and `2.358e-4` on 64 ViT (CI `[-3.232e-4, -1.575e-4]`). The hard policy has zero collisions, but it often has to choose damaging edges. Soft load correction reduces average DeiT collisions from `2.91` to `2.53` at 16 while keeping the candidate set intact. Individual images have both signs of residual interaction; the averages alone do not imply every shared destination is harmful.

## Gate B: compact random projections lose too much

Each image uses fixed Gaussian projections of the exact one-action changes and clean-error vector, with dimension-specific seeds recorded in the manifest. These projections isolate representation loss: they are still computed from *teacher* logits. The selected set at each dimension is evaluated by a real suffix forward.

| Projection dimension | DeiT actual D | Improvement vs cost-only | Retained full-effect improvement | Median pair inner-product Spearman | Greedy score time/image |
| ---: | ---: | ---: | ---: | ---: | ---: |
| 16 | 1.4750e-4 | -1.341e-5 | -75.9% | 0.371 | 0.844 ms |
| 32 | 1.3407e-4 | 0.009e-6 | 0.05% | 0.487 | 1.002 ms |
| 64 | 1.2252e-4 | 1.156e-5 | **65.4%** | **0.606** | 0.957 ms |
| 128, diagnostic only | 1.2171e-4 | 1.238e-5 | 70.0% | 0.714 | 0.967 ms |
| Full 1,000-logit vectors | 1.1641e-4 | 1.768e-5 | 100% | 1.000 | — |

For 64 dimensions, the paired improvement over the cost-only control is positive, `1.156e-5` (CI `[2.683e-6, 2.233e-5]`), and 16-merge set overlap with the full-effect selector averages `15.06/16`. Yet it misses **both** required representation thresholds: at least 80% retained improvement and median pair Spearman at least 0.70. It also has `6.116e-6` more actual D than the full-effect selector (full-minus-projected CI `[-1.021e-5, -2.298e-6]`). Dimension 128 clears the pair-correlation threshold but is outside the deployable limit and still retains only about 70% of the gain. ViT-B at 64 dimensions reaches median pair Spearman `0.779` and mean D `3.890e-5`; it does not alter the pre-registered DeiT-based decision. Mean set-score rank Spearman is high (`0.970` for DeiT at d=64), which shows that a high global rank correlation can coexist with a consequential error among the best admissible 16 actions. The [projection sensitivity figure](../outputs/functional_set_merge/phase_b_projection_sensitivity.png) shows both metrics.

The d=64 representation stores `32 × 64 = 2,048` action-effect scalars versus `32 × 1,000 = 32,000` in full vectors. Its fixed `1,000 × 64` projection matrix adds 64,000 scalars; applying it to one image's vectors took `0.557 ms` mean on DeiT, separately from `0.957 ms` greedy scoring, and one-time matrix construction took `0.957 ms` for DeiT. At d=16/32/64, measured greedy scoring stayed under the 5 ms limit. No compact student exists, so these offline times do **not** represent inference latency or net acceleration.

**Gate B is KILL.** Because no d≤64 passes the 64-image criteria, the protocol does not permit a 128-image Phase B replication, Phase C student training, or Phase D complete compression rollouts. No alternative projection, penalty tuning, larger neural student, or revised gate was tried after seeing the failure.

## Relation to baselines and literature

The strongest measured first-round result against the actual 180-patch ToMe control is the offline full-effect teacher. For DeiT-Small, ToMe minus additive + load mean D is `2.579e-4` (CI `[1.809e-4, 3.400e-4]`) on 64 and `4.341e-4` (CI `[3.102e-4, 5.842e-4]`) on 128. For ViT-B, the corresponding differences are `5.849e-5` (CI `[1.392e-5, 1.173e-4]`) and `6.498e-5` (CI `[2.231e-5, 1.184e-4]`). Those large gaps require downstream teacher queries and are **headroom**, not deployable compression performance. No 98/49-patch result, Top-1 comparison, Hybrid Group Mean comparison, or throughput Pareto point exists for this method.

[ToMe](https://arxiv.org/abs/2210.09461) uses lightweight token matching without retraining. [DTEM](https://arxiv.org/abs/2412.10569) learns a decoupled embedding for merging through a differentiable relaxation and reports classification, captioning, and segmentation experiments. [PiToMe](https://arxiv.org/abs/2405.16148) prioritizes informative-token preservation using an energy score and studies spectral preservation. Related adaptive reduction such as [A-ViT](https://arxiv.org/abs/2112.07658) learns token halting for task efficiency. Our narrower experimental distinction is **offline** selection of a simultaneous merge set from measured, centered, action-induced downstream logit changes, with explicit accounting for alignment and nonadditive response. A learned score or projected output features alone would not establish algorithmic novelty; no head-to-head deployed comparison with these other papers was performed.

## Reproduction, resource use, and limits

The implementation is in [`functional_set_merge.py`](../patch_fungibility/functional_set_merge.py), the runner in [`run_functional_set_merge.py`](../scripts/run_functional_set_merge.py), the deterministic summary and bootstrap in [`summarize_functional_set_merge.py`](../scripts/summarize_functional_set_merge.py), and tests in [`test_functional_set_merge.py`](../tests/test_functional_set_merge.py). The output directory contains manifests with image IDs, model-weight hashes, candidate/projection seeds, device and software versions, parity, teacher call counts, wall times, and memory; compact per-image CSVs retain k=1,2,4,8,16 plus cardinalities required for the hard-restriction comparison.

Run from the repository root, with the same model/data dependencies as the prior PRs:

```text
python scripts/run_functional_set_merge.py --phase a --cohort stability --limit 2
python scripts/run_functional_set_merge.py --phase a --cohort stability
python scripts/run_functional_set_merge.py --phase a --cohort pilot
python scripts/summarize_functional_set_merge.py
python scripts/run_functional_set_merge.py --phase b --cohort stability --limit 2
python scripts/run_functional_set_merge.py --phase b --cohort stability
python scripts/run_functional_set_merge.py --phase tome --cohort stability
python scripts/run_functional_set_merge.py --phase tome --cohort pilot
python scripts/summarize_functional_set_merge.py
```

Two-image/model smokes preceded each full phase. The final full Phase A 64/128 passes took `99.35/199.70 s`; Phase B 64 took `29.28 s`; matched ToMe controls took `11.40/20.71 s`. These final passes total about **0.10 GPU-hours**, with peak allocated GPU memory **423 MiB**. Teacher suffix calls total 45,625 + 91,815 + 5,548 + 128 + 256 across those passes; Phase A/Phase B teacher suffix time is also recorded separately. No-merge parity was zero in A/B runs; the ToMe action/baseline parity was at most `3.10e-6` on the stability cohort. These measurements describe this exploratory pilot on one RTX 5070 Laptop GPU, not a production runtime study.

The key limitation is decisive: the exact teacher vectors contain useful set-selection information, but the pre-specified compact representation does not retain enough of it. A student would add prediction error, and the earlier student already had substantial individual-ranking regret. With Gate B failed, the supported next step for this branch is **KILL**: preserve the offline finding as diagnostic evidence and do not promote this method to a practical compression algorithm.
