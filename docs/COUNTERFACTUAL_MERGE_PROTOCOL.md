# Counterfactual merge scoring: frozen pilot protocol

Frozen before executing the Phase I pilot on 2026-10-11. The canonical seed-9201 confirmatory images are excluded from every development step. This is a new, independent algorithm experiment; it does not revise the PCF manuscript.

## Question and estimand

At one intervention depth, can the actual frozen suffix distinguish candidate patch-token merges more effectively than cosine similarity? For state `s`, action `(i,j)` merges source `i` into destination `j` with multiplicity-weighted averaging and removes one patch token. CLS is unchanged. Center logits over classes, and define `D(s) = ||center(z(s))-center(z_clean)||² / (||center(z_clean)||² + 1e-8)`. The observed action cost is `D(s after a)-D(s)`. Negative costs are valid. Selection uses the same 32-action pool for every policy.

## Models, data, and implementation

- Frozen `deit_small_patch16_224` at block 8 and `vit_base_patch16_224.augreg_in1k` at block 7; `timm` pretrained weights and existing PCF transforms. Patch count is 196 in each.
- Use only the canonical calibration draw: one ImageNet-1k validation image per class chosen with seed 9101 using the existing parquet ordering. Do not load or sample seed-9201 images. Partition the 1,000 calibration IDs with NumPy `RandomState(64011)`: first 128 pilot, next 64 disjoint stability check, remainder reserved for possible training. Record global indices, source parquet identities, split seed, model ID, checkpoint identity, library versions, and Git revision.
- Prefix is the original full sequence through blocks `0..depth-1`. Suffix is blocks `depth..11` with additive `log(multiplicity)` key bias; classifier is the original head. Before labels, compare the no-merge compressed path with the standard full forward on each architecture. Require max absolute logit error below `5e-4`, and compare the candidate-batch path with the existing PCF compressed suffix on a single merged example to the same tolerance.
- All computations use inference mode and FP32. The teacher performs actual suffix forwards and never uses labels for its target. CUDA synchronization brackets runtime observations.

## States and candidates

Evaluate each image at 196, 147, and 98 current patch tokens (nominal 100%, 75%, 50%). Generate 147 and 98 states by the *frozen existing ToMe-style bipartite soft matching policy* at the intervention point: even-indexed patch sources, odd-indexed destinations, cosine of current representations, and top `r=49` or `r=98` source-to-best-destination edges. Merge into destinations with multiplicity-weighted averaging. Record weighted mean original patch coordinates for each token. This is one round from the unmerged state, without suffix execution between merges. No candidate teacher signal enters state construction.

At each state, split current patch indices into even sources and odd destinations. Construct exactly 32 distinct admissible edges where possible:

1. The 16 highest-cosine source-to-best-destination edges proposed by the existing ToMe matching rule.
2. The 8 highest-cosine remaining even-to-odd edges, allowing alternate destinations.
3. Eight edges sampled without replacement from the remaining middle/lower-similarity pool, ranks spanning the 25th to 75th similarity percentiles, with NumPy seed `64021 + global_image_index + 1009*state_patch_count + model_offset`.

Ties use source index then destination index. One-action comparisons impose no cross-action destination exclusivity. The candidate record includes cosine, feature distance, norms, CLS cosine, multiplicities, weighted spatial distance, and current patch count. The cosine policy selects the highest cosine edge in this *same* pool; the random control selects one of these 32 using the frozen candidate seed; the teacher chooses the minimum measured next-state distortion. An optional fixed-feature proxy is compared only if defined before looking at outcomes.

Evaluate candidates in batches of at most eight on the actual suffix. For each state store current distortion, all 32 next-state distortions/costs, policy choices, candidate construction metadata, runtime, and peak CUDA allocation. Do not write large hidden-state tensors to Git.

## Analysis and gate G1

For each architecture and state, report mean next-state distortion and absolute paired difference `D_cosine - D_teacher`, the ratio of *mean* distortions `(mean(D_cosine)-mean(D_teacher))/max(mean(D_cosine),1e-8)`, mean teacher cost advantage, candidate cosine/cost Spearman correlation, random-control results, and 95% percentile bootstrap CI for the paired mean difference. Resample images, not actions, 2,000 times with seed 64012. Also report the number of images on which the teacher strictly wins, near-zero distortion frequency, time per candidate, and peak memory. Do not use a mean of unstable per-image percentage ratios.

**Pre-registered pass:** for **each** of DeiT-Small and ViT-B, at least two of the three states must show (i) at least 5% reduction in mean next-state distortion versus cosine, (ii) a strictly positive paired 95% image-bootstrap lower bound, and (iii) absolute mean reduction above `1e-6`. On the disjoint 64-image calibration stability set, the same qualifying regimes must retain a positive mean absolute advantage; this check is descriptive, not a second threshold search. The pool is held identical for oracle and cosine. If G1 fails, stop before training.

## Subsequent gates, only if unlocked

G2: Train the smallest shared token projection (D→16) plus pair MLP using within-state ranking on the remaining calibration-training images; compare cosine, fixed-feature linear/MLP, a fair learned-embedding control without counterfactual targets, and random. Evaluate ranking and complete same-schedule rollouts on disjoint calibration-validation images at 98 and 49 patch tokens. Require lower completed-state distortion than the strongest same-protocol matching baseline on both architectures, with no material Top-1 regression. Single-step rank correlation alone does not pass.

G3: Only after G2, implement batched student scoring without suffix calls. Benchmark synchronized end-to-end throughput and peak memory at batch sizes 1, 8, 32, 64 where feasible against clean, ToMe, and Hybrid Group Mean. Require a meaningful acceleration over clean on an accuracy–throughput frontier; otherwise report the tradeoff and stop.

No final canonical N=1,000 evaluation, extra architecture replication, or manuscript changes are authorized by this protocol.

### Phase II/III operational details, fixed before student results

The reserved 808 calibration images provide training counterfactuals; the 64-image stability cohort is the only internal validation cohort. Train a D→16 shared pair projection and 64/32 hidden-unit score MLP with a within-state top-action listwise cross-entropy. Controls are cosine, a fixed-feature MLP trained on the same teacher rank target, a fixed-feature MLP regressing absolute distortion, and a D→16 projection trained to reconstruct the input cosine without teacher costs. Select epochs by internal-validation regret; no seed-9201 data is used. Rollout selects at most 16 unique even-source edges per round from the same deterministic 32-edge construction, permits shared odd destinations, and repeats until 98 or 49 patch tokens remain. Evaluate the existing ToMe and Hybrid Group Mean implementations alongside these same-schedule methods.

For G2, compare the proposed model with the lowest-distortion same-schedule control in each architecture–budget cell. Require a positive 95% paired image-bootstrap lower bound (2,000 resamples, seed 64051) on the control-minus-proposed completed-state distortion in all four cells and no more than a 1 percentage point Top-1 regression in any cell. This makes “reproducible improvement” operational before observing student outcomes.

## Prior-art audit (scope of claim)

- [ToMe](https://arxiv.org/abs/2210.09461) uses fast bipartite similarity matching and size-weighted merging, without per-action suffix counterfactual labels.
- [DTEM](https://arxiv.org/abs/2412.10569) learns a decoupled embedding through differentiable relaxed merging and downstream task training. It establishes that a learned merge metric alone is not novel. Our narrower distinction is the frozen-model, per-action *finite counterfactual suffix* target and within-state ranking; head-to-head controls are required to establish value.
- [PiToMe](https://arxiv.org/abs/2405.16148) uses an energy/spectrum criterion to protect informative tokens; [AdaMerge](https://arxiv.org/abs/2605.27465) uses salience-weighted similarity and adaptive rate; [ALGM](https://arxiv.org/abs/2406.09936) uses local then global similarity for segmentation. None of these cited methods supplies the particular finite-action target above.
- [Learned Thresholds Token Merging and Pruning](https://arxiv.org/abs/2307.10780), [Efficient Visual Transformer by Learnable Token Merging](https://arxiv.org/abs/2407.15219), and [Lossless Token Merging Even Without Fine-Tuning](https://arxiv.org/abs/2505.15160) overlap on trainable decision rules, task/reconstruction losses, or single-merge loss proxies. The audit supports a *testable mechanistic distinction*, not a priority claim that no related method exists.

The prior PCF operator reports show real per-image oracle benefit but poor amortization and practical throughput; they motivate this narrower action-ranking test. In particular, do not infer final-budget accuracy from one-step distortion.
