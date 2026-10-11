# Mechanism-Gated 2×2 Coarsening Pilot — Results

**Outcome: STOP after M1.** The fixed-cell variance penalty did not reduce the targeted attention–Value covariance or actual CLS attention-branch error by the preregistered practical amounts. M2 and M3 were not run. This is a negative pilot result, not evidence that the mechanism is impossible under every schedule.

The protocol was frozen and committed before execution in [MECHANISM_GATED_2X2_PROTOCOL.md](MECHANISM_GATED_2X2_PROTOCOL.md) (commit `72597a6`). The work ran on the isolated branch `codex/mechanism-gated-2x2-coarsening`.

## Data validation

- Local data: `D:\Study\ResCancel\counterfactual-pcf-mechanism-gated-2x2\local_data\imagenet_train_5k_seed20261011`.
- Source: official HF `ILSVRC/imagenet-1k`, revision `49e2ee26f3810fb5a7536bbf732a7b07389a47b5`, split `train` only, streamed after account authentication and acceptance of dataset access terms.
- 5,000 original image files were retained locally: 4,000 `finetune_train`, 1,000 `dev_train`. All decode, labels fall in `[0,999]`, and encoded-file and decoded-RGB hashes are unique and disjoint across the two partitions. The sample is not balanced: 993 represented classes; min/median/max class counts 0/5/13.
- timm DeiT-Small uses 1,000 outputs with label offset 0. Integer labels are used without remapping; the sole display alias discrepancy is class index 517 (`crane2`/`crane`).
- The 10-image access preflight read 1,108,823 bytes of image payload. The 5,000-image stream read 7,000 rows into its shuffle buffer and exposed 802,567,212 encoded-image payload bytes; local image storage is 577,405,716 bytes. These are payload and file sizes, not measured HTTP wire bytes.
- The independent validator passed after the experiment. It rechecked every file hash and decoded-pixel hash. No official validation images or PCF validation cohorts were read. No credentials or image contents are in Git.
- The tracked [manifest](../artifacts/imagenet_train_5k_seed20261011/examples.csv) SHA-256 is `834a302d9dd24733187676f872fdc2fd13a49f3cd39452b1758af79241e7d5de`. Frozen development identities are in [dev_partitions.json](../artifacts/imagenet_train_5k_seed20261011/dev_partitions.json), SHA-256 `bf9028d67f81e5ae2ff458bae1f09a8f29bac947b85effcb7925126f6e0b2793`.

## M0 — passed

Implementation tests passed for vectorized 2×2 pooling against an independent slice reference, exact CLS preservation, 197→50 tokens, multiplicity mass/bias, clean forward parity, compressed forward parity, and gradients through pooling and Ω. The FP32 clean custom forward matched timm with maximum absolute logit error 0. On the pretrained model, the frozen-attention covariance decomposition had maximum absolute residual `2.31e-7`.

The 1,000-image internal `dev_train` forward smoke gave clean top-1 `90.2%` and untrained fixed-pool top-1 `87.3%` (−2.9 percentage points); mean centered-logit distortion was `0.4291`. These are results on ImageNet training images, not validation accuracy.

The preregistered frozen-weight mechanism screen on 64 `mechanism_dev` images passed its relevance thresholds:

- Median projected covariance / actual CLS attention-branch error: `0.803`; image-bootstrap 95% CI for the mean ratio `[0.759, 0.836]`.
- Median image-wise Spearman correlation between cell Ω and projected covariance magnitude: `0.703`; 95% CI for the mean correlation `[0.671, 0.708]`.

This is an association screen and does not establish causality. Initial checkpoint metrics also showed substantial pooled K/V mismatch and attention-mass rerouting, which remain outside Ω's direct target.

## M1 — failed practical target-engagement thresholds

C (`μ=0`) and D (`μ=0.01`) started from the same pretrained checkpoint and used identical seed `20261021`, 512 `finetune_train` images in manifest order, one epoch, batch size 8, AdamW at `1e-5`, weight decay `0.05`, BF16 autocast, and the frozen teacher with CE+KL (`T=2`, `λ=1`). Each arm took 64 optimizer steps. C/D training took 6.61/6.06 seconds; peak allocated GPU memory was 643,120,640/646,241,792 bytes on an NVIDIA GeForce RTX 5070 Laptop GPU.

Both arms were evaluated on the same 100 frozen `mechanism_dev` images. The paired bootstrap used 10,000 image resamples, seed `20261031`.

| Target | C | D | Paired D−C / reduction | Preregistered threshold | Result |
|---|---:|---:|---:|---:|---|
| Mean Ω | 0.58146 | 0.57372 | −1.33% | Diagnostic only | Ω decreased slightly |
| Median projected covariance norm | 1.67533 | 1.66591 | 0.56% median reduction; mean difference −0.00862, CI `[−0.00976, −0.00750]` | ≥10% median reduction and CI wholly below zero | **Fail** |
| Median actual block-7 CLS attention-branch error | 2.23159 | 2.22749 | 0.18% median reduction; mean difference −0.00289, CI `[−0.00375, −0.00199]` | ≥5% median reduction and CI wholly below zero | **Fail** |
| Compressed top-1 on mechanism_dev | 88% | 88% | 0 pp | No meaningful regression | No regression observed on these 100 images |
| Centered-logit distortion to frozen teacher | 0.40569 | 0.40620 | D slightly higher | Reported diagnostic | No D improvement |

The small paired decreases in covariance and attention-branch error are statistically separated from zero on this 100-image sample, but they miss the frozen 10% and 5% effect thresholds by a wide margin. Ω's mean decreased about 1.3%; full CLS-attention entropy rose only about `0.002` nats (3.9884→3.9904), so the observed result is not an indiscriminate large entropy increase. C and D both had 89% clean-teacher top-1 on this small mechanism subset; their own uncompressed student and compressed student top-1 were both 88%.

**Gate decision:** M1 fails. Following the frozen stop rule, the 4,000-image main paired run (M2), μ tuning on `mu_tune`, and all M3 work were not run. There is no ToMe/MCTF comparison, no measured latency claim, and no claim of a competitive compression algorithm. The initial Ω/covariance association did not translate into a practically meaningful target reduction after this short matched adaptation.

## MAC accounting and limits

For (D=384), (M(N)=12ND^2+2N^2D). Twelve clean blocks at 197 tokens total `4,540,695,552` MACs. Seven full-token blocks plus five 50-token blocks total `3,100,707,072` block MACs, a theoretical 31.71% block-only reduction. Including the common 57,802,752-MAC patch embed gives 31.32%. M3 latency was gated off, so these counts do not establish a speedup on hardware.

This experiment tested the narrow mechanism-specific regularizer, not a new pooling rule or general distillation principle. The outcome supports stopping this specific pilot at M1; a revised μ, a longer run, or a different objective would require a new preregistered GO decision rather than changing this result.

## Reproduction and tracked outputs

- Data acquisition/validation: `scripts/acquire_imagenet_train_pilot.py`, `scripts/validate_imagenet_train_pilot.py`.
- Frozen development partition: `scripts/freeze_dev_train_partitions.py`.
- Mechanism implementation and M0/M1 runners: `patch_fungibility/mechanism_gated_coarsening.py`, `scripts/run_mechanism_gated_m0.py`, `scripts/run_mechanism_gated_m1.py`.
- Unit tests: `tests/test_mechanism_gated_coarsening.py` (4 passed).
- Machine-readable gate outputs: `artifacts/mechanism_gated_pilot/m0.json` and `artifacts/mechanism_gated_pilot/m1.json`.
- Raw images and model checkpoints stay in ignored local storage and are not committed.
