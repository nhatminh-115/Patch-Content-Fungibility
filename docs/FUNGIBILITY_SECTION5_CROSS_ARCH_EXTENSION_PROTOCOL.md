# Frozen Protocol: Section 5 Cross-Architecture Extension

**Date frozen:** 2026-10-09  
**Purpose:** Fill two audited coverage gaps in Section 5 using the current implementation and existing cohorts. This protocol was saved before running either extension.  
**Models:** DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, DINOv2 ViT-S/14.  
**No existing output, result, or checkpoint will be modified.**

## A. Functional-geometry spectrum extension (Section 5.1)

### Question
Do the pilot’s local margin-gradient geometry summaries extend to DeiT-Tiny and DINOv2, and are the reported depth trends robust to numerical treatment and embedding width?

### Frozen design
- Measure all four architectures under the same frozen calculation. DeiT-Tiny and DINOv2 fill the missing coverage; DeiT-Small and ViT-B are recomputed only as double-precision audit controls for cutoff and numerical stability. The existing source outputs remain unchanged, and the previously reported values remain locked unless an auditable discrepancy is found.
- Layers: post-block depths 5, 7, 8, and 10.
- Images: first 100 samples of the existing calibration split returned by get_disjoint_imagenet_splits() with its existing seeds (calibration 9101, evaluation 9201). The same 100 sample IDs are used for covariance and margin-gradient calculations in each model. Ground-truth labels are not used in the metric.
- Checkpoints and preprocessing: the exact current load_model_and_transform() checkpoint and transform for each model, with frozen weights.
- Readout: logits from the existing forward_block_by_block() implementation. For DINOv2 this is the official linear classifier applied to concatenated normalized CLS and mean-normalized-patch readouts.
- Functional metric: for each clean image, hold the clean predicted class and runner-up fixed; differentiate their logit margin with respect to each unperturbed patch activation. Form the double-precision average M_l=(N_img n_p)^(-1) sum_{s,i} g_{s,i} g_{s,i}^T. This is a D×D margin-gradient second moment, not the full downstream readout-Jacobian Gram matrix.
- PCA directions: eigenvectors of the centered covariance of pooled patch activations from those same 100 images. Preserve the absolute values v_PC1^T M_l v_PC1 and v_bottom^T M_l v_bottom, then report their ratio without adding an epsilon. Mark a ratio numerically unstable only if its denominator is at most 10^(-10) lambda_max(M_l); retain all absolute sensitivities regardless.
- Spectral summaries: compute symmetric double-precision eigenvalues of M; save raw eigenvalues before any clipping. Treat a negative eigenvalue as a PSD failure only below -10^(-10) lambda_max; clip round-off negatives to zero only for entropy/effective-rank and cutoff summaries. Report near-null counts at relative cutoffs 10^(-4), 10^(-3) (primary), and 10^(-2), plus effective rank and effective-rank/D.
- No hypotheses or depth-specific tuning will be introduced. No new direction sweep or classification-recovery experiment is included.

### Outputs
Write all new files under outputs/fungibility_section5_cross_arch_extension/functional_geometry/: per-model/depth summaries, raw un-clipped eigenspectra, full M/covariance matrices, sample IDs, validation metadata, and run logs. Existing outputs/fungibility_functional_geometry/ remains unchanged.

## B. Model-specific held-out perturbation prediction extension (Section 5.3)

### Question
Does the reported single-block versus end-to-end prediction correlation reproduce separately for each architecture, rather than only for the existing DeiT-Small cohort?

### Frozen design
- Reuse the existing DeiT-Small Block-8 random_prediction.csv as the reference cohort; do not rerun or replace it.
- New measurements: DeiT-Tiny, ViT-B/16 AugReg, and DINOv2 ViT-S/14, each at post-block 8.
- Use the first 20 calibration-split images and same model preprocessing/checkpoints as the existing multiblock runner. Preserve the existing implementation: J_8_to_L is linearized at the first image in that 20-image batch; the perturbation outcomes are full-model final-logit L2 changes averaged over that same 20-image batch.
- Match the original 100 perturbation vectors, seed 42, scale s=0.4, and four equal perturbation families: 25 top end-to-end modes, 25 middle modes, 25 end-to-end-null modes, and 25 isotropic Gaussian controls. Use each model’s own single-block operator and downstream Jacobian. Do not pool model rows.
- Report model-specific Pearson and Spearman correlations for the full 100-vector mixture. Provide 95% stratified bootstrap intervals by resampling 25 perturbations within each of the four families (2,000 replicates; bootstrap seed 52026). Also report family-specific correlations descriptively; do not treat perturbation vectors as images or tokens as independent observations.
- Correlations quantify association across designed perturbation vectors at one scale and one image batch. They do not establish prediction across new images, across layers, or for deployment.
- No change to model, perturbation, scale, or readout after looking at results.

### Outputs
Write all new files under outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/: raw per-perturbation records, per-model correlations and intervals, model metadata, sample IDs, and validation manifest. Existing multiblock outputs remain unchanged.

## C. Stop rules
- Stop and report a model/depth as not measured if checkpoint, split, or exact implementation cannot be reproduced.
- Stop accepting a measurement if the frozen image count, perturbation count, scale, depth, or required readout differs.
- Do not adjust thresholds, seeds, or sample selection after observing results.
- Do not edit any source data under existing outputs/ directories.

