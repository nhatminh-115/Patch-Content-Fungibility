# Frozen protocol: signed Value-error balancing for ViT merging

**Freeze point:** commit this file and the [G0 audit](SIGNED_VALUE_MERGING_NOVELTY_AUDIT.md) before any new model forward. Start at PR #6 head `cb57fd4`, in an independent branch stacked on `research/functional-set-aware-merging`. A failed gate stops dependent phases. No neural training, Jacobian/VJP, deployed suffix/clean-logit query, seed-9201 held-out access, manuscript edit, or change to historical outputs.

## G0: exact methodological overlap

The primary-method matrix in the audit reviewed ToMe, MCTF including supplement, DTEM, ATM, HAC including supplement, SAD-TM including supplement, AdaMerge, ICML 2026 calibrated scaling, and close BalanceKV/ApET work. **G0 GO only for an empirical pilot:** vector balancing is prior art, but no reviewed method uses this specific per-merge, head-resolved signed Value-replacement proxy to choose a simultaneous ViT merge set. Neither priority nor practical usefulness is inferred. If an effectively identical method is found later, mark G0 KILL and stop.

## Models, data, and estimator

Use the PR #4–6 frozen DeiT-Small Block 8 and ViT-B/16 AugReg Block 7 model/transform/suffix, FP32, clean classifier, and 32-edge candidate pool seeded `64021+global_index+1009*196+model_offset` (`model_offset=0` or `1000003`). The `stability` 64 and `pilot` 128 are disjoint seed-9101 calibration images already used by prior PRs. Phase A starts with a two-image/model smoke and then 64 `stability` images. Replicate a passing gate on 128 `pilot` images; these are not new held-out confirmation. The canonical seed-9201 cohort is excluded.

For each image, run the original optimized prefix **once** while a forward hook retains the last executed block's *existing* QKV projection output. It must not call QKV again or disable PyTorch/timm fused scaled-dot-product attention. From that captured tensor, compute each head's CLS-query attention weights to all original tokens and retain the corresponding Value vectors. The captured block is `depth-1`; these signals describe the *preceding block input*, not the next block's actual attention/Values after merging. This mismatch is a central falsification target. The output-projected variant may multiply a candidate's concatenated head vector by the already existing attention output-projection weight, a small per-candidate operation. No second full QKV or extra transformer block is allowed in the deployed route.

For action `(i,j)` with multiplicities `(m_i,m_j)`, define in each head

`u_ij^h = ((a_i^h*m_j - a_j^h*m_i)/(m_i+m_j)) * (v_i^h-v_j^h)`.

This is the original-minus-merged frozen-attention Value aggregate for a fixed query, assuming the merged attention mass equals `a_i+a_j` and the merged Value is the multiplicity-weighted average. It is algebraically exact only under those assumptions and a linear Value projection. In the original 196-patch state `m_i=m_j=1`, so it becomes `(a_i-a_j)(v_i-v_j)/2`. It excludes Q/K rerouting, layer normalization on the merged carrier, residual/MLP nonlinearities, following blocks, and any non-CLS readout. Do not extend a CLS-only conclusion to DINOv2.

Use exactly matched candidate access and 16 source-disjoint simultaneous actions; repeated destinations are permitted. Preserve CLS, multiplicity mass, weighted carriers, and the same multiplicity-biased frozen suffix. Demand no-merge maximum logit parity `<5e-4`. Paired 95% percentile bootstrap intervals use 2,000 image resamples, fixed seed `77112`. Count images, never candidate actions, as independent units. All gate thresholds below refer to actual suffix distortion `D`, not proxy objective values.

## A: proxy validity and acquisition cost

Offline teacher: cache actual one-action suffix D for each of the 32 actions. At inference, selectors use only prefix activations and retained QKV data. Evaluate these pre-specified one-action selectors:

1. Highest original cosine similarity.
2. Lowest scalar CLS attention importance `a_i+a_j` (head mean).
3. Lowest scalar attention-weighted Value distance `(a_i+a_j)*||v_i-v_j||` (head concatenation).
4. Lowest raw signed-vector norm `||u_ij||`.
5. Lowest attention-output-projected norm `||W_o u_ij||`.
6. Actual independent one-action oracle as an offline upper reference only.

Report within-image Spearman rank agreement of each cost with actual D, chosen-action D and regret to oracle, top-1 oracle agreement, candidate-feature correlations, and both architectures' absolute distortion scale. Keep the two signed-norm variants visible even if one wins the gate. Inspect positive and negative individual examples without using them to tune a selector.

Measure uncaptured optimized prefix time, hooked prefix time, post-prefix signal construction time, total incremental memory, and suffix teacher time separately on a warm GPU. The capture must preserve `fused_attn`, and a hook/call-count test must demonstrate one QKV invocation in each prefix block during the captured forward. The measured deployed increment is hook/capture plus proxy construction and selection; do not charge offline teacher to it. Use an initial two-image/model smoke, including 20 warmup and 50 measured prefix runs/image/model for overhead, before the 64-image pass.

**G1 GO:** on DeiT's 64 images, the better pre-specified signed-norm variant must improve mean chosen one-action D over the best of cosine, scalar-attention importance, and scalar attention-weighted Value-distance by `≥1e-6` absolute and `≥10%` relative to that baseline, with paired bootstrap lower bound `>0`. The same selected variant must have a positive mean contrast on the 128-image pilot replication. On ViT-B's smaller absolute scale, require the same variant to have a positive paired lower bound on 64 and positive pilot mean. The hooked route must keep fused attention, avoid any redundant full QKV, add no more than `20%` to median prefix-plus-signal time relative to uncaptured prefix on the two-image/model smoke, and use at most `128 MiB` additional allocated GPU memory. The overhead condition is assessed on the complete capture/proxy route, not the hook alone. If any condition fails, G1 KILL and stop before set selection.

## B: signed set selection, only after G1 GO

At original 196-patch states, choose 16 admissible actions by constrained greedy with a frozen, untuned objective

`score(S) = sum_a ||u_a||² + ||sum_a u_a||²`.

Thus `lambda=1`; use both raw and output-projected vectors, selecting the better G1 variant as primary. A destination-load correction is separately pre-specified as marginal `median(||u_a||²)*existing_destination_load`; no tuning on suffix outcomes. Controls use the same 32 edges: cosine/ToMe, scalar attention importance, scalar attention-weighted Value distance, raw norm-only ranking, projected norm-only ranking, signed balancing, signed balancing plus load, and actual independent/conditional offline oracles. `Scalar Value-error ranking` denotes the attention-weighted Value-distance score; `norm-only` denotes the exact signed-vector norm without cross-action alignment, avoiding a duplicate control. Report actual suffix D after k=1,4,8,16, selected single-action D sum, additive-output alignment and actual-minus-additive residual using offline individual logits, source/destination validity, cardinality, collisions, and scoring overhead. Hard distinct-destination restriction is omitted because PR #6 found it damaging; any later restriction requires count-matched analysis.

**G2 GO:** on 64 DeiT images, the signed primary policy must beat both cosine and the best lightweight scalar/norm-only policy at 16 merges by `≥1e-5` absolute and `≥10%` relative to that scalar control, with paired lower 95% bound `>0` for both contrasts. On ViT-B, require positive means and paired lower bounds for both contrasts; on the 128-image pilot replication, require the DeiT signs to remain positive. Failure stops before full rollouts. A lower proxy objective or better rank correlation alone cannot pass.

## C: complete compression, only after G2 GO

On 64 calibration images, run matched schedules to 98 and 49 retained patches with original ToMe, Hybrid Group Mean, cosine same-schedule, scalar Value-distance same-schedule, and signed balancing. At each new state, repeat the same one-prefix capture strategy; no teacher query and no silent on-policy fitting. If needed, compare a single first-round-only signed/then-cosine hybrid, predeclared as one bounded ablation. Report exact token counts, Top-1, clean-prediction preservation, full-model normalized D, and round-wise divergence.

**G3 GO:** signed method must lower mean D against the strongest same-schedule control at both budgets in both architectures, with paired lower bound `>0`, and make no more than one additional Top-1 error among 64 images per cell. If only the single-stage hybrid passes, label the full signed rollout failed and limit any claim to that hybrid. A failed G3 stops throughput claims.

## D: practical performance, only after G3 GO

Benchmark actual end-to-end prefix + capture + proxy + matching + merging + suffix + head against optimized clean ViT, ToMe, and Hybrid Group Mean at batch sizes 1,8,32,64 where memory allows. Report latency, throughput, allocated memory, and FLOPs; include signal materialization and host matching costs. A useful route must improve accuracy–throughput tradeoff in a measured operating regime. No theoretical FLOP estimate counts as demonstrated speedup.

## Execution and artifacts

Before every entered full phase, run two images per model through correctness and runtime smoke checks. Cap total new experiment work at 4 GPU-hours and peak 8 GiB; stop if observed cost predicts exceeding either. Store image IDs, model hashes, data snapshot names, seeds, architecture, timing, QKV hook counts, fused-attention status, CUDA memory, teacher calls, and parity in manifests. Tests cover the synthetic fixed-attention identity, source constraints, CLS/mass preservation, multi-action count, forward parity, no redundant QKV, dataset isolation, and instrumentation. Commit reproducible code, compact per-image/aggregate outputs, report, tests, and this protocol on a new stacked PR without merging predecessors.
