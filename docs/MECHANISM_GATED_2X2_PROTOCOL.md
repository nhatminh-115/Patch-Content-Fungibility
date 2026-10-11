# Mechanism-Gated 2×2 Coarsening Pilot — Frozen Protocol

**Protocol status:** frozen before M0/M1 execution

**Repository branch:** `codex/mechanism-gated-2x2-coarsening`

**Base commit:** `0f9acf9307a47ecaace7a784b15dd0f74ebb7dad` (`origin/main`)

**Frozen:** 2026-10-11 (Asia/Saigon)
**Pilot question:** Does a cellwise CLS-query attention-logit variance penalty make pretrained DeiT-Small more tolerant to a fixed 2×2 spatial mean pool than the identical compression-aware CE+KL fine-tuning control?

This is a bounded representation-adaptation experiment. It does not introduce a learned merge policy, predictor, Jacobian, token assignment, or extra inference module. Every gate is falsifiable; work stops at the first failed gate. Results from the 1,000-image development set are internal `dev_train` results, never ImageNet validation results.

## 1. Data, provenance, and integrity

- Source: Hugging Face [`ILSVRC/imagenet-1k`](https://huggingface.co/datasets/ILSVRC/imagenet-1k), dataset revision `49e2ee26f3810fb5a7536bbf732a7b07389a47b5`, split `train` only, loaded with streaming. The account-authenticated access token was not written to code, logs, manifests, or artifacts.
- Local images: `D:\Study\ResCancel\counterfactual-pcf-mechanism-gated-2x2\local_data\imagenet_train_5k_seed20261011` (ignored by Git). Only original encoded files are stored; no full ImageNet archive was fetched.
- Acquisition: `datasets` streaming shuffle seed `20261011`, buffer 2,000; first 5,000 distinct encoded-image and decoded-RGB hashes retained. The 4,000/1,000 split uses seed `20261012`.
- `finetune_train`: 4,000 images. `dev_train`: 1,000 images, drawn from the same official training split. This is not the official validation split.
- The sample is not class-balanced: 993 classes represented; per-class count across the 5,000 images has min/median/max 0/5/13. There are 974 represented labels in `finetune_train` and 618 in `dev_train`.
- Integrity validation recomputed every encoded-file SHA-256 and decoded RGB pixel hash: 5,000 unique encoded hashes, 5,000 unique pixel hashes, all images decode, all labels are in `[0,999]`, and the two partitions are disjoint. The official validation split and PCF seed-9101/seed-9201 cohorts were not loaded or used.
- The source ClassLabel has 1,000 categories and timm's `imagenet-1k` index has 1,000 sorted unique synsets. DeiT-Small has 1,000 outputs and label offset zero. Integer labels are used without remapping. One displayed alias differs at index 517 (`crane2` versus `crane`); the sorted ILSVRC synset index is the same.
- Reproducibility artifacts (manifest, class counts, metadata, checksums) are in `artifacts/imagenet_train_5k_seed20261011/`. Manifest SHA-256: `834a302d9dd24733187676f872fdc2fd13a49f3cd39452b1758af79241e7d5de`; label-count SHA-256: `fcc7c201c848bf7ab2fdcb06d787048566d2f981837a674be6ef1cb7f4bc2800`.
- The 10-image access/decode preflight read 1,108,823 encoded-image payload bytes. The 5,000-image stream read 7,000 rows into its shuffle buffer and exposed 802,567,212 encoded-image payload bytes to Python; 577,405,716 bytes were retained on disk. These are image payload/storage measurements, not HTTP/Parquet wire-byte measurements.
- Fine-tuning transforms: resize shorter side to 256 with bicubic interpolation, random crop 224, horizontal flip p=0.5, tensor conversion, ImageNet mean/std normalization. Development transforms: resize 256 bicubic, center crop 224, tensor conversion, same normalization. Source bytes remain unchanged.

The acquisition and independent validation commands are documented in the scripts under `scripts/`; rerunning acquisition requires an authenticated HF account with accepted dataset terms. The recorded manifest makes the selected local set auditable without containing image content or credentials.

## 2. Model and exact intervention

- Model/checkpoint: timm `deit_small_patch16_224.fb_in1k`, 224×224 input, patch size 16, width (D=384), 6 attention heads, 12 transformer blocks indexed 0–11, 196 patch tokens plus one CLS token. The existing 1,000-class classifier is retained.
- Full reference: the standard model forward, all 12 blocks at 197 tokens.
- Compressed forward: blocks 0–6 execute at 197 tokens. Reshape the 196 patch outputs from block 6 to a 14×14 grid and use a vectorized non-overlapping 2×2 arithmetic mean to obtain 49 patch tokens in a 7×7 grid. Preserve the CLS tensor bit-for-bit. Blocks 7–11 execute at 50 tokens.
- In every compressed suffix attention block, add key bias 0 to CLS and (log 4) to each pooled patch key. This exactly restores the original total patch-token multiplicity under equal logits; it is not a claim that the compressed attention distribution otherwise matches the full one.
- Each pooled patch represents four original tokens; multiplicities are `(1, 4, ..., 4)`, summing to 197 including CLS. No extra trainable or inference-time module is added.
- Student runs use this same compressed forward for all images. Teacher logits come from the frozen uncompressed pretrained model on the identical augmented input.

### MAC accounting

For a DeiT block with sequence length (N), width (D), and MLP ratio 4, count matrix multiply-accumulate operations as

\[
M(N)=12ND^2+2N^2D,
\]

covering QKV/output projections, the two MLP projections, and QK/AV products. With (D=384):

| Path | Blocks | Tokens | Block MACs |
|---|---:|---:|---:|
| Clean | 12 | 197 | 4,540,695,552 |
| Fixed coarsening | 7 | 197, then 5 | 3,100,707,072 |

The block-only theoretical reduction is 31.71%. The common patch embedding is 57,802,752 MACs, giving totals 4,598,498,304 versus 3,158,509,824 MACs, a 31.32% reduction. These analytic counts omit normalization, softmax, residuals, pooling, memory traffic, and kernel-launch overhead. No latency claim will be based on MAC counts; clean and pooled latency must be measured end-to-end on the same GPU only at M3.

## 3. Regularizer and exact mechanism identity

Let (h_i) be the unpooled block-6 hidden states, and let block 7's first LayerNorm and Q/K projections use the current student parameters. For each head (r) and each fixed 2×2 cell (G), compute the CLS-query logits

\[
t_{ri}=q_{r,\mathrm{CLS}}^\top k_{ri}/\sqrt{d_h},\qquad
\Omega_{\mathrm{cell}}=\frac{1}{6\cdot49\cdot4}\sum_{r,G}\sum_{i\in G}(t_{ri}-\bar t_{rG})^2.
\]

This uses the unpooled block-6 output, before pooling, and the same student weights as the compressed branch. It is an auxiliary training penalty only.

For a *frozen full-sequence attention operation*, let (a_{ri}) be the full attention weights from the CLS query, (v_{ri}) the full Value vectors, (A_{rG}=\sum_{i\in G}a_{ri}), and (\bar v_{rG}=\tfrac14\sum_{i\in G}v_{ri}). The within-cell identity is exact:

\[
\sum_{i\in G}a_{ri}v_{ri}=A_{rG}\bar v_{rG}+C_{rG},\qquad
C_{rG}=\sum_{i\in G}(a_{ri}-\bar a_{rG})(v_{ri}-\bar v_{rG}),
\]

where (\bar a_{rG}=A_{rG}/4). This identity is a decomposition, not evidence that (\Omega_{\mathrm{cell}}) controls the covariance or that it controls the real compressed network.

The actual compressed block recomputes Q/K/V from pooled hidden states after LayerNorm. LayerNorm does not commute with averaging; pooled keys alter cell and CLS masses; multiplicity bias corrects only the equal-logit group-size effect; and pooled Values need not equal (\bar v_{rG}). For each head before output projection, the full-minus-compressed CLS attention output is decomposed exactly as

\[
o_{\mathrm{full}}-o_{\mathrm{comp}}=
\sum_G C_{rG}
+\sum_G(A_{rG}-\hat A_{rG})\bar v_{rG}
+(A_{r,CLS}-\hat A_{r,CLS})v_{r,CLS}
+\sum_G\hat A_{rG}(\bar v_{rG}-v^{pool}_{rG}).
\]

Terms are respectively frozen-attention within-cell covariance, patch-group rerouting, CLS-mass rerouting, and pooled-Value mismatch (which includes LayerNorm noncommutativity). The implementation will numerically verify this decomposition before any training.

## 4. M0 and M1 gates

### M0 — implementation and mechanism validity

Before any training:

1. Unit-check 197→50 tokens, exact CLS preservation, 49 pooled patches, vectorized 2×2 means against an explicit reference, total token mass 197, and suffix bias `(0, log4 × 49)`.
2. Check gradients through the pool and (\Omega_{cell}).
3. Run the custom clean path and pooled path against their exact reference constructions; clean custom forward must match timm's normal forward within max absolute logit error (10^{-5}) in FP32. Verify the compressed suffix matches an independently constructed pooled-input forward within the same tolerance.
4. Run pretrained clean and pooled inference over the 1,000 `dev_train` images, reporting top-1 accuracy and centered-logit distortion. This is a forward smoke, not an official validation result.
5. On the first deterministic 64 `dev_train` images (assigned below to `mechanism_dev`), log A) (\Omega_{cell}), B) covariance contribution, C) full grouped versus compressed CLS attention mass, D) first block-7 CLS attention-output and block-output differences, E) final centered-logit distortion, K/V LayerNorm pooling mismatch, and CLS attention entropy.
6. Verify the covariance decomposition residual has max absolute error ≤ (10^{-5}) in FP32.

### Development partition

Using Python `random.Random(20261013)`, sort the 1,000 `dev_train` manifest rows by their stable `image_sha256` identity, shuffle, then assign the first 100 to `mechanism_dev`, the next 100 to `mu_tune`, and the final 800 to locked `dev_gate`. `scripts/freeze_dev_train_partitions.py` saves these IDs before M0 in `artifacts/imagenet_train_5k_seed20261011/dev_partitions.json` (SHA-256 `bf9028d67f81e5ae2ff458bae1f09a8f29bac947b85effcb7925126f6e0b2793`). No image from `dev_gate` may affect tuning or model selection.

The cell covariance vector is projected through the corresponding input slice of block 7's output projection, then through its LayerScale when present. The image-level covariance ratio is the norm of the summed projected covariance vectors divided by the norm of the full-minus-compressed CLS attention-branch output (both before the residual addition). Before M1 training, the 64-image frozen-weight M0 mechanism screen must have median covariance ratio ≥0.10 and a 95% image-bootstrap lower bound >0.05; median image-wise Spearman correlation between per-head/cell \(\Omega\) and projected \(\|C_{rG}\|\) must be ≥0.25 with lower bound >0.10. Bootstrap: 10,000 image resamples, seed `20261031`. These are relevance/screening criteria, not causal evidence. If either criterion fails, stop before any optimizer step.

### M1 — target-engagement screen before the main paired run

Only if M0 passes, perform one bounded paired target-engagement run using the first 512 `finetune_train` examples in manifest order, one epoch, seed `20261021`, and fixed (\mu=0.01). Compare C (\(\mu=0\)) and D (\(\mu=0.01\)); all other settings and minibatch order are identical. Evaluate both checkpoints on `mechanism_dev` only. The M1 question is whether D reduces the intended attention–Value aggregation error beyond C, rather than only reducing attention logits.

M1 covariance vectors are summed after output projection and LayerScale; actual branch error is the norm of the full-minus-compressed block-7 CLS attention-branch outputs before the residual addition. M1 passes only if all conditions hold:

- D reduces median per-image block-7 projected covariance norm by at least 10% relative to C and the 95% paired image-bootstrap interval for mean(D−C) is below zero.
- D reduces median per-image actual block-7 CLS attention-branch output error by at least 5% relative to C and the 95% paired bootstrap interval for mean(D−C) is below zero.
- The covariance decomposition remains numerically valid (max absolute residual ≤ (10^{-5})).

Use 10,000 paired image bootstrap resamples, seed `20261031`. Report (\Omega_{cell}), attention-logit standard deviation, attention entropy, covariance norm, actual attention error, group-mass total variation, pooled K/V mismatch, and output distortion for both arms. A drop in (\Omega_{cell}) or logits alone is not a pass. If either required error fails its threshold, stop before the 4,000-image main run.

## 5. M2 matched training and locked evaluation

Only if M1 passes, train C and D from the same pretrained checkpoint, with identical 4,000 `finetune_train` images, epoch count, sample order, augmentation RNG, optimizer, seeds, and all trained parameters. Full student fine-tuning is allowed. Use the same frozen pretrained teacher for KL.

- Objective: \(L=CE(y,z_s)+\lambda T^2 KL(softmax(z_t/T)\|softmax(z_s/T))+\mu\Omega_{cell}\), with temperature (T=2), KL coefficient (\lambda=1), and CE/KL computed on the 1,000 logits.
- C has (\mu=0). D uses the (\mu\) selected only on `mu_tune` from the preregistered grid `{0.001, 0.01, 0.1}`. Each candidate uses the first 512 fine-tuning images for one epoch, seed `20261041`; select the value with the lowest mean centered-logit distortion on `mu_tune`, ties to the smaller (\mu). No other hyperparameter tuning.
- Main schedule: one epoch, AdamW, learning rate (10^{-5}), weight decay 0.05, batch size 8, no gradient accumulation, AMP BF16 when supported (otherwise FP32); gradient clipping at 1.0. Two paired seeds `20261051` and `20261052` are preferred and are run only if the first seed fits the available resource envelope without OOM or thermal interruption. If only one seed is feasible, label all inference as single-seed pilot evidence.
- Teacher and student see the identical transformed minibatch. C/D use common per-seed initialization, data order, and augmentation randomness. Save checkpoints and RNG/config metadata locally; keep raw data and checkpoints out of Git.
- `mu_tune` is used only for selecting (\mu). The locked primary comparison uses only the 800 `dev_gate` images, deterministic center-crop transforms, and the matching seed-specific models.
- Per image, centered-logit distortion is (D=\|P(z_c-z_f)\|_2/(\|Pz_f\|_2+10^{-12})), where (P=I-\mathbf1\mathbf1^\top/1000), (z_c) is compressed-student output, and (z_f) is the same seed's frozen clean teacher output.
- M2 passes only if (i) D's mean (D) is at least 20% lower than C's, with a 95% paired image-bootstrap CI for mean(D−C) strictly below zero, and (ii) D's top-1 accuracy difference versus C has 95% paired image-bootstrap lower bound greater than −1.0 percentage point. Bootstrap resamples images, pairing predictions and averaging the two seeds when both are available. Bootstrap seed `20261061`.
- Report the original clean teacher, untrained pooled B, C and D. If C and D are similar or D misses either threshold, stop; do not proceed to M3.

## 6. M3 practical comparison (conditional)

Only after M2 passes, measure clean, untrained fixed pooling, C, D, and compatible public ToMe/MCTF implementations on the same GPU and `dev_gate` inputs. Report method/checkpoint provenance, token budget, training data/compute, analytic MACs, measured end-to-end batch-1 and batch-8 latency (warmup and repeated timing protocol), peak allocated GPU memory, top-1 accuracy, and centered-logit distortion. Clearly distinguish published recipe compute from this one-epoch pilot. If compatible MCTF code/checkpoints are unavailable, report that limitation; do not substitute a non-equivalent implementation silently. This pilot alone cannot authorize a longer training run or support a claim of competitive ImageNet compression.

## 7. Runtime, reporting, and stop conditions

- Available device at freeze time: NVIDIA GeForce RTX 5070 Laptop GPU, 8,151 MiB total VRAM. Available local disk on D: was 296,109,346,816 bytes before dataset acquisition.
- Record actual GPU, driver/runtime, peak allocated/reserved VRAM, epoch wall time, image payload bytes, and local storage after each executed gate. Use deterministic seeds and save source commit, exact IDs, software versions, and commands.
- Never access the canonical PCF seed-9201 held-out benchmark. Do not use official ImageNet validation or existing PCF validation parquet shards. Do not modify manuscript files or historical experiment outputs.
- Stop at the first failed gate. No gate threshold, sample, split, seed, or baseline may be changed after its results are inspected. Results are pilot evidence; no confirmatory claim is implied.
- New work remains on this isolated branch. Open a review PR only after the authorized pilot has produced its results; never merge automatically.

## 8. Prior-art boundary

This experiment does not claim a new pooling or token-merging algorithm, new general distillation objective, or generic attention-consistency method. The narrow tested contribution is whether the particular within-fixed-cell variance of CLS-query logits is a useful training-time control for the exact attention–Value covariance term under a fixed 2×2 mean pool, beyond identical CE+KL compression-aware fine-tuning. Related methods to contextualize results include MCTF, Token Pooling, ToMe fine-tuning, CLS attention distillation, CubistMerge, and Statistically Calibrated Scaling for Token Merging (ICML 2026). Any future novelty claim requires a separate primary-source and implementation audit.
