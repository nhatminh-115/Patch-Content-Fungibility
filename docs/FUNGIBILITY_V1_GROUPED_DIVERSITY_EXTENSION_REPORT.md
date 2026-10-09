# Grouped-Diversity Extension Report

## Protocol and validation

The extension followed the frozen protocol in \`FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md\`. It uses the official frozen ViT-B/16 AugReg and DINOv2 ViT-S/14 checkpoints and preprocessing, the exact V0.6 calibration/evaluation split order (1,000 images each; seeds 9101/9201), calibration statistics archived by V1, and complete spatial-patch replacement at Block 8. Five new sampling seeds (26001–26005) were evaluated at K={1,2,4,8,16,32,64,N_patches}; N_patches is 196 for ViT-B and 256 for DINOv2. The grouped vectors use the original cyclic assignment across token positions.

Validation passed before interpreting the results: split identities matched exactly with zero overlap; recomputed Block-8 calibration means and standard deviations matched the archived values exactly; clean predictions and margins matched archived V1 per-image values exactly; all weights remained frozen; and the 80,000 per-image rows have unique image/seed/K keys. The K=1 and full-diversity endpoints were compared with the archived V1 shared- and independent-Gaussian controls. All eight architecture × endpoint × metric checks were within the pre-specified two combined standard errors; the largest discrepancy was 1.43 combined SE.

## Results

Top-1 accuracy means by K, in percent:

| Architecture | K sequence | Mean Top-1 accuracy (%) |
|---|---|---|
| DeiT-Tiny | 1, 2, 4, 8, 16, 32, 64, 196 | 1.20, 2.37, 4.57, 8.37, 13.27, 16.70, 21.83, 26.40 |
| DeiT-Small | 1, 2, 4, 8, 16, 32, 64, 196 | 10.40, 13.43, 21.00, 29.23, 34.17, 38.73, 43.37, 46.47 |
| ViT-B/16 AugReg | 1, 2, 4, 8, 16, 32, 64, 196 | 3.24, 5.46, 6.82, 9.52, 11.58, 13.10, 13.78, 14.58 |
| DINOv2 ViT-S/14 | 1, 2, 4, 8, 16, 32, 64, 256 | 0.12, 0.10, 0.18, 0.12, 0.08, 0.06, 0.18, 0.10 |

The grouped Top-1 means increase at every tested step in both DeiT models and ViT-B. ViT-B rises by 11.34 percentage points from K=1 to K=196 (paired 95% image-level CI: 9.55–13.13; Wilcoxon BH-adjusted q=4.60×10⁻²⁴). It remains well below its 76.1% clean accuracy.

DINOv2 Top-1 has no monotonic trend and stays near floor (0.06–0.18%); the paired K=1-to-256 difference is −0.02 percentage points (95% CI −0.16 to 0.12; Wilcoxon BH-adjusted q=0.828, N=1,000 images). Its mean true-class logit margin increases at every tested K from −9.233 to −7.982, a paired change of +1.250 (95% image-level CI: 1.091–1.410; Wilcoxon BH-adjusted q=2.00×10⁻⁴³). Because the official DINOv2 linear readout includes the mean normalized patch representation, this is a margin change and does not constitute accuracy recovery.

For each model and metric, paired comparisons cover all 28 K pairs. Each seed outcome is averaged within each evaluation image before tests; the inferential sample is the same N=1,000 images. Seeds and patch positions are not treated as additional independent observations. Seed-level means and SDs are in \`aggregate_results.csv\`; all pairwise tests and confidence intervals are in \`paired_image_comparisons.csv\`.

## Interpretation

The graded Top-1 relationship generalizes from DeiT-Tiny/Small to ViT-B/16 AugReg, but not to DINOv2 classification under this readout and complete-replacement condition. DINOv2 shows ordered margin improvement without Top-1 recovery. The overall conclusion is **partial generalization with an architecture/readout-dependent boundary**, not a universal accuracy-recovery law. Token-position diversity K remains distinct from feature-space dimensionality.

## Artifacts

- \`scripts/run_grouped_diversity_extension.py\`: experiment runner.
- \`docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md\`: frozen design and validation rules.
- \`outputs/fungibility_v1_grouped_diversity_extension/per_image_results.csv\`: 80,000 image-level outcomes, including margins and predictions.
- \`outputs/fungibility_v1_grouped_diversity_extension/seed_level_results.csv\`, \`aggregate_results.csv\`, \`paired_image_comparisons.csv\`, \`monotonicity_summary.csv\`, and \`endpoint_validation.csv\`.
- \`outputs/fungibility_v1_grouped_diversity_extension/experiment_metadata.json\` and \`validation_results.json\`, plus copied split manifests and calibration-statistics archive.
- \`figures/paper_final_v4/figure3_geometry_diversity.svg/.png\` and \`figures/paper_final_v4/supp/figureS10_dinov2_margin_diversity.svg/.png\`.

No DeiT models were rerun and no prior raw results were modified.
