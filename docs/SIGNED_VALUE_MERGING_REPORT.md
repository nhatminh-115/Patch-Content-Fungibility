# Signed Value-error balancing for ViT merging: gated result

**Decision: KILL at G1 proxy validity.** The [protocol](SIGNED_VALUE_MERGING_PROTOCOL.md) and [G0 prior-art audit](SIGNED_VALUE_MERGING_NOVELTY_AUDIT.md) were committed as `edb7fba` before any new model forward. A prefix-hook route met the frozen pooled-median acquisition-cost cap, but its signed Value-error norms selected one-merge actions with **more actual output distortion than cosine** on both 64-image model cohorts. No 128-image replication, simultaneous set selection, complete rollout, or throughput benchmark was run.

## Gate decisions

| Gate | Frozen question | Decision |
| --- | --- | --- |
| G0 | Is the exact proposed method already present in the reviewed primary methods? | **GO to a bounded pilot.** Signed vector balancing is prior art in [BalanceKV](https://arxiv.org/pdf/2502.07861), while [MCTF](https://arxiv.org/html/2403.10030v3) warns that previous-block attention may be a weak proxy. The [matrix](SIGNED_VALUE_MERGING_NOVELTY_AUDIT.md) supports only a narrow method distinction, not priority or usefulness. |
| G1 smoke | Can the signal be extracted with ≤20% pooled median prefix overhead and ≤128 MiB extra GPU allocation, preserving fused attention and one QKV call? | **GO.** DeiT +19.21%, ViT-B +12.82%; extra peak ≤2.0 MiB; one QKV hook call and `fused_attn=True`. |
| G1 validity | Does the better DeiT signed norm beat the best cosine/scalar one-action control by ≥1e-6 and ≥10% mean D, with paired 95% lower bound >0, and generalize to ViT-B? | **KILL.** Raw signed norm was worse than cosine by 4.896e-6 mean D on DeiT and 1.522e-7 on ViT-B; both paired lower bounds for *cosine minus signed* were negative. |
| G2 / G3 / practical Phase D | Do signed sets, full 98/49-patch rollouts, and end-to-end inference improve? | **Not entered**, required by the G1 stopping rule. |

The G0 audit compares full methods and, where available, supplements of ToMe, MCTF, DTEM, ATM, HAC, SAD-TM, AdaMerge, statistically calibrated scaling, BalanceKV, and ApET. Neither the error identity nor signed vector cancellation is novel by itself. The proposed training-free ViT merge-set use has no demonstrated advantage in this branch.

## Mechanism and deployed-route boundary

For a fixed CLS query in one head, suppose original attention weights to two tokens are `a_i,a_j`, Values are `v_i,v_j`, and multiplicities are `m_i,m_j`. Replacing the Values by the weighted carrier `v_bar=(m_i v_i+m_j v_j)/(m_i+m_j)` while holding total attention mass at `a_i+a_j` gives the exact frozen-attention identity

`a_i v_i + a_j v_j - (a_i+a_j) v_bar = ((a_i m_j-a_j m_i)/(m_i+m_j)) (v_i-v_j)`.

The code concatenates these signed vectors over heads and separately applies the existing attention output projection. Their norms are one-action selectors; the actual signed sum would be used only in G2 if G1 passed. A hook observes the last ordinary prefix block's existing QKV output and computes CLS attention and Value tensors without a second full QKV projection or an extra block. The two scalar controls are head-mean CLS attention importance and unsigned attention-weighted Value distance. Cosine and every proxy see the same seeded 32-edge PR #4–6 pool and the same actual suffix teacher offline.

The hook sees the **preceding block input**, while a merge intervenes on that block's *output*. The next block's Q/K/Value response, attention rerouting, layer normalization, residual path, MLP, later blocks, and non-CLS readouts are absent from the proxy. Thus the derivation is neither a final-logit estimate nor evidence for DINOv2. The synthetic fixed-attention identity test passes, including unequal carrier masses and a nontrivial output projection.

## G1 acquisition cost and correction record

The smoke used two seed-9101 `stability` calibration images per model, DeiT-Small Block 8 and ViT-B/16 AugReg Block 7 in FP32 on an RTX 5070 Laptop GPU. There were 20 warmups and 50 synchronized measured runs **per arm, image, and model**. The pre-registered statistic is the median of the pooled 100 runs per model. Candidate-pool construction is common to the matching policies and was precomputed outside both timing arms; the captured route includes hook, CLS attention/Value extraction, 32 candidate proxy scores, and selection. Offline teacher suffix calls are excluded. The [raw timing series and gate](../outputs/signed_value_merging/pooled_metering/smoke/gate_smoke.json) permit exact recomputation.

| Model | Uncaptured prefix pooled median | Capture + proxy + selection pooled median | Increment | Max extra allocated GPU peak |
| --- | ---: | ---: | ---: | ---: |
| DeiT-Small | 2.434 ms | 2.902 ms | **19.21%** | 0.866 MiB |
| ViT-B | 4.005 ms | 4.518 ms | **12.82%** | 2.000 MiB |

The [smoke telemetry](../outputs/signed_value_merging/pooled_metering/smoke/telemetry.csv) also separates an ordinary hooked-prefix arm from post-prefix proxy construction. This split is approximate because sequential arms can experience GPU clock variation; the gate uses complete-route timings. No-merge logit parity was exactly zero in all smoke and stability cases. The retained hook saw one QKV call, and the fused attention flag remained true. Candidate-pool construction in direct image evaluation took roughly 45–56 ms after warmup, with a ~335 ms cold first case; this CPU-heavy research pool is a further warning against claiming production speed from the incremental signal result.

**Timing interpretation was corrected before 64-image outcomes were inspected.** The first [smoke](../outputs/signed_value_merging/smoke/gate_smoke.json) accidentally charged shared state construction only to the captured arm. The second [smoke](../outputs/signed_value_merging/revised_metering/smoke/gate_smoke.json) fixed that split, but its code treated the 20% cap as a per-image maximum. That stricter interpretation failed on one DeiT image at 21.26%. The written protocol says *median on the two-image/model smoke*, so the third smoke recorded every timing repetition and used a pooled per-model median. Both earlier result sets are retained. The 20% threshold, candidate policy, and subsequent 64-image outcome criterion were never adjusted. The late clarification of aggregation is a methodological limitation; importantly, the 64-image downstream validity gate fails even under the passing runtime interpretation.

## G1 actual one-action outcomes

The 64-image `stability` cohort was previously used in this research program; it is **calibration data**, not fresh held-out confirmation. For every image and candidate, the frozen suffix produced actual normalized centered-logit distortion `D`. The [manifest](../outputs/signed_value_merging/pooled_metering/stability/manifest.json) records model weight hashes, exact image IDs and parquet snapshot, seeds, software versions, four batched offline teacher calls per image, parity, and wall time. The full stability run took 19.68 wall seconds. The canonical seed-9201 cohort was never read.

| Model, n=64 images | Cosine | CLS attention scalar | Attention × Value distance | Raw signed norm | Output-projected signed norm | Offline one-action oracle |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| DeiT-Small | **6.012e-6** | 7.009e-5 | 2.442e-5 | 1.091e-5 | 1.133e-5 | 1.529e-7 |
| ViT-B | **1.509e-7** | 1.081e-5 | 5.440e-7 | 3.030e-7 | 1.800e-7 | 2.443e-8 |

All numbers are mean **actual** one-merge D, not proxy scores. On DeiT, `raw_norm` is the pre-specified better signed variant. Its paired cosine-minus-signed mean is **−4.896e-6**, 95% image-bootstrap CI **[−1.764e-5, +4.346e-6]** (2,000 resamples, seed 77112). Instead of the required ≥10% reduction, its D is **81.4% higher** than cosine. The same held-fixed raw variant on ViT-B gives cosine-minus-signed **−1.522e-7**, CI **[−4.555e-7, +1.055e-8]**. Even the separately reported, ViT-favored projected variant has higher mean D than cosine: cosine-minus-projected **−2.915e-8**, CI **[−7.879e-8, +1.186e-8]**. No signed variant satisfies the absolute, relative, or paired-interval gate. Therefore the planned 128-image pilot replication is prohibited by the frozen stop rule.

Candidate-level rank correlation did *not* predict minimum-action quality. Mean within-image Spearman of cost against actual D on DeiT was **0.742** for raw norm versus **0.363** for cosine; oracle agreement was **18.8%** versus **3.1%**. Yet the signed policy's mean selected D was worse. It helped 39 DeiT images, harmed 22, and tied 3; one failure at image 5934 alone had cosine-minus-signed D **−3.195e-4**, while image 38428 gained **+1.177e-4**. On ViT-B, projected norm helped 14, harmed 25, and tied 25 against cosine. The [diagnostics](../outputs/signed_value_merging/pooled_metering/stability/diagnostics.json) inspect these positive and negative examples and record selected actions without tuning a new selector.

The raw norm's mean within-image Spearman with unsigned attention-weighted Value distance was **0.861** on DeiT and **0.846** on ViT-B, and with feature distance **0.801/0.691**. Thus much of its ranking follows unsigned local magnitude. Those correlations do not prove the source of the high-distortion tail, but they help explain why an apparently informative rank statistic did not produce a safe selected minimum. The preceding-block mismatch, Q/K rerouting, and nonlinear downstream transmission remain plausible causes; this experiment did not isolate them.

## Reproduction and limits

Implementation: [proxy module](../patch_fungibility/signed_value_merging.py), [runner](../scripts/run_signed_value_merging.py), [tests](../tests/test_signed_value_merging.py), and [gate JSON](../outputs/signed_value_merging/pooled_metering/gate_decisions.json). Six targeted tests pass, covering the synthetic identity, CLS/mass/source invariants, the exact 180-patch 16-action budget, QKV call count and fused state, suffix parity, cohort isolation, and the pooled timing gate. The runner refuses a 128-image replication after this failed 64-image decision.

```text
python -m pytest tests/test_signed_value_merging.py -q
python scripts/run_signed_value_merging.py --phase smoke --output-dir NEW_OUTPUT_DIR
python scripts/run_signed_value_merging.py --phase stability --output-dir NEW_OUTPUT_DIR
python scripts/run_signed_value_merging.py --phase summarize --output-dir NEW_OUTPUT_DIR
```

The pre-registered G1 outcome is negative despite a technically feasible QKV capture. No G2 signed set objective, destination-load correction, 98/49-patch Top-1 result, or throughput point was produced, and none should be inferred from individual-action correlations or the offline oracle. The recommendation is to **stop this algorithm under the frozen protocol**. A future proposal would need a newly frozen mechanism that protects against the selected-action tail and a full end-to-end candidate matcher; this branch provides no practical speedup or novelty claim.
