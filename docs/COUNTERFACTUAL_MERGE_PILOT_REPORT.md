# Counterfactual merge scoring: calibration pilot report

- **Date:** 2026-10-11
- **Branch:** `research/counterfactual-merge-scoring`
- **Decision:** G1 GO under its frozen rule; G2 KILL; G3 not entered. No canonical seed-9201 held-out image was used. No manuscript, publication figure, or historical engine was changed.

## Executive finding

Actual frozen-suffix counterfactuals reveal candidate merge actions that cosine similarity misses. The oracle reduces mean next-state normalized output distortion by 8.8% at 147 patches for DeiT-Small and by 16.3% at 147 and 10.3% at 98 patches for ViT-B. A 13k–19k parameter pair scorer trained on these outcomes has some lower one-step regret on disjoint calibration-validation images, yet **makes final predictions substantially worse** when its actions are rolled out to 98 or 49 patches. The local target is informative; this implementation does not turn it into practical token compression.

The G1 pass needs a qualification: DeiT-Small's second qualifying regime is the initially unmerged 196-patch state, whose cosine next-state distortion is only `1.39e-5`. Its 98-patch reduction was 4.85%, just below the frozen 5% criterion. ViT-B's initially unmerged state failed the absolute `1e-6` floor. Thus both architectures have robust headroom at 147 patches, but the two-regime result is not equally strong at nontrivial accumulated distortion.

## Protocol and audit trail

The [frozen protocol](COUNTERFACTUAL_MERGE_PROTOCOL.md) was committed as `fe3067e` before labels. Phase I code was committed as `189a5ca` before the full 128+64-image run; its [manifest](../outputs/counterfactual_merge_pilot/manifest.json) records that revision, the exact source parquet snapshot filenames and sizes, SHA-256 hashes of loaded model state dictionaries, seeds, transforms, library versions, depths, and parity. The training-label generator revision was `6a27097`; student training and rollout ran at `1ccafc3`. Raw candidate labels and token-pair caches remain in local output directories and are ignored by Git; the aggregate CSVs, manifests, model weights, and source-image ID lists are deliverables.

The calibration draw follows PCF seed 9101, one image per class. A new seed 64011 partitioned its 1,000 distinct image IDs into 128 pilot, 64 stability/internal-validation, and 808 student-training images. The seed-9201 confirmatory set was neither read nor sampled. Teacher targets use clean frozen logits, not class labels. Class labels were used only to report internal-validation Top-1 after rollouts.

To reproduce from a fresh checkout with the same cached ImageNet parquet snapshot and pretrained checkpoints, use unique output directories (the runner refuses to overwrite existing experiments):

```text
python scripts/run_counterfactual_merge_pilot.py --output-dir outputs/counterfactual_merge_pilot_repro
python scripts/run_counterfactual_merge_pilot.py --cohort train --output-dir outputs/counterfactual_merge_train_repro
python scripts/train_counterfactual_merge_scorer.py --pilot-dir outputs/counterfactual_merge_pilot_repro --train-dir outputs/counterfactual_merge_train_repro --output-dir outputs/counterfactual_merge_student_repro
python scripts/diagnose_counterfactual_merge_rollout.py --student-dir outputs/counterfactual_merge_student_repro
```

Both frozen backbones used FP32 and the original prefix and head. The candidate suffix preserves CLS, uses group-size weighted carriers, and adds `log(multiplicity)` to attention keys; DINOv2 was implemented in the generic suffix utility but not tested in this pilot. The no-merge and one-merge comparisons against PCF's validated suffix had **zero observed maximum logit discrepancy** for both tested architectures on all pilot images, below the `5e-4` tolerance. The 147/98 intermediate states match PCF's existing ToMe-style matching to floating-point tolerance.

At each state, the same 32 admissible even-source/odd-destination edges were available to cosine, random, and teacher selection: 16 ToMe-proposed edges, eight high-cosine alternatives, and eight sampled middle/lower-similarity edges. The teacher actually ran the frozen suffix for every candidate. Image, not candidate, was the bootstrap unit. The 95% intervals below use 2,000 paired image resamples.

## G1: oracle headroom

The table shows the 128-image pilot. `Δ` is mean cosine-selected next-state distortion minus mean teacher-selected next-state distortion; lower distortion is better. The percentage divides the two *mean* distortions, not near-zero per-image ratios. All choices use exactly the same candidate pool.

| Model | Current patches | Cosine D | Teacher D | Δ D (95% paired CI) | Reduction | Frozen threshold |
|---|---:|---:|---:|---:|---:|---|
| DeiT-Small | 196 | 1.390e-5 | 2.515e-7 | 1.365e-5 [4.640e-6, 2.849e-5] | 98.19% | Pass; small absolute scale |
| DeiT-Small | 147 | 0.003268 | 0.002981 | 0.000287 [0.000177, 0.000457] | 8.79% | Pass |
| DeiT-Small | 98 | 0.018216 | 0.017332 | 0.000884 [0.000679, 0.001137] | 4.85% | Fail: below 5% |
| ViT-B | 196 | 2.532e-7 | 5.036e-8 | 2.029e-7 [3.915e-8, 4.595e-7] | 80.12% | Fail: below absolute floor |
| ViT-B | 147 | 0.000747 | 0.000625 | 0.000122 [0.000070, 0.000185] | 16.34% | Pass |
| ViT-B | 98 | 0.007775 | 0.006973 | 0.000802 [0.000514, 0.001238] | 10.32% | Pass |

All qualifying regimes also had positive mean advantages on the disjoint 64-image stability cohort. In the pilot, the teacher strictly improved on cosine for 117/128 DeiT-Small images at 196 patches, 120/128 at 147, and 121/128 at 98; the corresponding ViT-B counts were 52, 123, and 127. Mean within-state Spearman correlations of cosine with actual action cost were negative, as expected, but modest at compressed states (`-0.27` to `-0.42`), leaving room for a better ranker. The 32-candidate suffix evaluation cost averaged 0.79–2.43 ms per candidate, depending on model/state, with observed peak CUDA allocation 118–427 MiB. These are **offline teacher** costs, not deployable student costs. Full values, random controls, uncertainty, and near-zero counts are in [summary.csv](../outputs/counterfactual_merge_pilot/summary.csv).

## Phase II: can a compact scorer predict the ranking?

The student shared a D→16 token projection, formed pair features from projected source/destination, absolute difference, and product, and used a 64/32 MLP plus ten standardized fixed features. It has 13,073 parameters for DeiT-Small and 19,217 for ViT-B. A listwise top-action cross-entropy trained on the 808 images' within-state counterfactual rankings. Epochs were selected only by the 64-image internal-validation regret. Controls were raw cosine; a 897-parameter fixed-feature ranking MLP; a fixed-feature absolute-distortion regressor; and a D→16 embedding trained to reconstruct original cosine without counterfactual labels. No model saw clean logits, suffix outcomes, or labels at inference.

On fixed ToMe-generated internal-validation states, the proposed scorer's mean regret against the teacher was lower than cosine at 147 and 98 patches in both architectures:

| Model | State | Cosine regret | Counterfactual scorer regret | Scorer Spearman with cost | Top-1 teacher action agreement |
|---|---:|---:|---:|---:|---:|
| DeiT-Small | 147 | 1.656e-4 | 1.198e-4 | 0.294 | 3.1% |
| DeiT-Small | 98 | 8.297e-4 | 7.463e-4 | 0.160 | 6.3% |
| ViT-B | 147 | 3.491e-4 | 1.388e-4 | 0.134 | 10.9% |
| ViT-B | 98 | 8.313e-4 | 8.201e-4 | -0.054 | 7.8% |

These are small or inconsistent rank-quality gains: ViT-B at 98 patches has negative score/cost rank correlation, and initially unmerged states show *worse* regret than cosine. The full [ranking summary](../outputs/counterfactual_merge_student/ranking_summary.csv) contains all controls, Spearman values, and Top-5 agreement. This is weak evidence that this small model learned a robust damage ordering beyond cosine.

## G2: complete compression

Rollout merged at most 16 unique even sources per round, permitted multiple sources per odd destination, rebuilt the same 32-action pool at each new state, and stopped at exactly 98 or 49 patches. All same-schedule scorers used this identical construction and weighted-merge rule. ToMe and Hybrid Group Mean used the existing PCF implementations at the same depth and final patch count. The student used neither teacher queries nor clean outputs during rollout. The table reports full frozen-model output distortion and Top-1 on the 64 internal-validation images.

| Model | Budget | Proposed D / Top-1 | Cosine D / Top-1 | ToMe D / Top-1 | Hybrid Group Mean D / Top-1 | Best other same-schedule D |
|---|---:|---:|---:|---:|---:|---:|
| DeiT-Small | 98 | 0.03725 / 73.4% | 0.01714 / 75.0% | 0.01759 / 75.0% | 0.05659 / 75.0% | 0.01681 (no-teacher embedding) |
| DeiT-Small | 49 | 0.11409 / 71.9% | 0.05148 / 76.6% | 0.04986 / 75.0% | 0.13668 / 71.9% | 0.05094 (no-teacher embedding) |
| ViT-B | 98 | 0.02164 / 73.4% | 0.01674 / 73.4% | 0.00549 / 73.4% | 0.03030 / 70.3% | 0.01589 (fixed regression) |
| ViT-B | 49 | 0.06585 / 70.3% | 0.03904 / 76.6% | 0.01928 / 71.9% | 0.07469 / 67.2% | 0.03763 (fixed regression) |

The paired 95% bootstrap intervals for **best same-schedule control minus proposed** distortion were entirely negative in all cells: DeiT-Small 98 `[-0.02721, -0.01325]`, DeiT-Small 49 `[-0.07860, -0.05035]`, ViT-B 98 `[-0.01113, -0.00045]`, and ViT-B 49 `[-0.04035, -0.01584]`. Top-1 differences against those controls were `-1.56`, `-4.69`, `-1.56`, and `-3.13` percentage points, respectively. **G2 fails decisively.** Full controls and image-level results are in [rollout_summary.csv](../outputs/counterfactual_merge_student/rollout_summary.csv) and [rollout_per_image.csv](../outputs/counterfactual_merge_student/rollout_per_image.csv).

### Where the damage begins

A post-G2 trace on all 64 validation images reran the same rollout and checked exact final-distortion agreement with the recorded results. Mean distortion was already higher after the **first 16 simultaneous merges**: DeiT-Small `0.001992` versus cosine `0.000374`, and ViT-B `0.000451` versus `0.000098`. By 148 patches, it was `0.010829` versus `0.003454` on DeiT-Small and `0.003789` versus `0.003429` on ViT-B. The gap then widened through 100 and 49 patches. [Trajectory summary](../outputs/counterfactual_merge_student/rollout_diagnostic_summary.csv) contains each round.

This directly shows that single-action cost ranking did not compose into a good *set* of 16 concurrent merges; harm appears before long-horizon state drift alone could explain it. The later divergence is also consistent with distribution shift: training states were produced by fixed ToMe, while the deployed scorer consumes states generated by its own earlier actions. The trace does not isolate nonadditive interactions from ranking errors among the first 16 choices. A future study would need joint-action or on-policy counterfactual targets, with a new frozen protocol; this failed gate does not justify further optimization in the present run.

## Prior art and novelty boundary

[ToMe](https://arxiv.org/abs/2210.09461) established fast similarity-based bipartite matching and multiplicity-weighted merging. [DTEM](https://arxiv.org/abs/2412.10569) already learns a decoupled merge embedding through differentiable relaxed merging and downstream task training, so a trainable merge score is not novel. [PiToMe](https://arxiv.org/abs/2405.16148), [AdaMerge](https://arxiv.org/abs/2605.27465), and [ALGM](https://arxiv.org/abs/2406.09936) use spectrum/energy, salience/adaptive rate, and local/global similarity criteria. Related learned-threshold and token-merger methods also train merge decisions or use reconstruction/task losses. The specific tested distinction here is **offline finite-action supervision from actual frozen-model suffix evaluations**, used for within-state ranking. The cited primary works and targeted search did not establish an effectively identical method, but this is a bounded audit rather than a priority claim. Even if that target is distinct, the failed rollout means the present method makes no practical improvement claim.

## Gate decisions and limits

| Gate | Pre-set question | Result | Decision |
|---|---|---|---|
| G1 | Does a same-pool teacher beat cosine in at least two regimes per architecture by ≥5%, positive paired CI, absolute gain >1e-6, and positive stability mean? | Yes under the frozen rule, with the near-clean DeiT-Small caveat above. | **GO** to training |
| G2 | Does the deployed scorer beat the strongest same-schedule control at completed budgets, with positive paired CI and no >1 pp accuracy loss? | No; all four distortion intervals favor controls, with accuracy losses in several cells. | **KILL** |
| G3 | Does scoring preserve meaningful end-to-end acceleration? | Not tested because G2 failed. Offline teacher timing is not inference throughput. | **NOT ENTERED** |

This is one model seed per architecture, one 64-image internal-validation cohort, and a deliberately limited 32-candidate pool. The candidate oracle is an upper bound *within that pool* and does not imply globally optimal merging. The same internal-validation cohort guided epoch selection and reports G2; any positive student result would have needed new independent confirmation. The canonical N=1,000 seed-9201 set remains untouched. No extensive student latency engineering was performed after G2 failed.
