# Section 5 Cross-Architecture Evidence Audit

Scope: functional geometry, attention-mediated Value-path transmission, end-to-end operator prediction, and joint token–feature geometry. Evidence cutoff: current repository outputs plus the targeted extension in outputs/fungibility_section5_cross_arch_extension/. Legacy raw-output directories remain unchanged.

## Status definitions

- A — Not evaluated for this scientific claim or condition.
- B — Evaluated but omitted from the manuscript.
- C — Partial replication with a narrower intervention or depth set than the primary audit.
- D — Matched evidence under the same frozen condition and metric for the cross-model comparison.

## Evidence matrix

| Claim / metric | DeiT-Tiny | DeiT-Small | ViT-B/16 AugReg | DINOv2 ViT-S/14 | Figure coverage before → after | Depth / protocol | Sampling unit | Direct comparability | Missing or bounded evidence |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| M_l PC-direction sensitivity and spectrum | D, extension | D, original pilot plus matched reanalysis | D, original pilot plus matched reanalysis | D, extension with official CLS+mean-patch classifier | Figure 4: Small/ViT-B → all four | Depths 5,7,8,10; centered activation covariance for PC directions; M_l from per-patch clean predicted-margin gradients | 100 calibration images/model; patch observations aggregated | Matched cohort/sampling within extension; widths differ, so fraction/effective-rank normalization is needed | Lowest-variance PC is weakly separated in ViT-B, especially at depth 8; pilot is exploratory and has no image-level CIs. |
| Threshold near-null and entropy effective rank | D, extension | D, pilot plus matched reanalysis | D, pilot plus matched reanalysis | D, extension | Figure 4: two models → all four | Depths 5,7,8,10; relative cutoffs 1e-4,1e-3,1e-2 lambda_max | 100 images/model | Same cutoff definition; DINO’s result changes markedly at 1e-2 | DINOv2 near-null fraction is nearly flat at the primary 1e-3 cutoff; do not claim universal near-null expansion. |
| Frozen-attention Value-only immediate readout | C, Block 8 | D, primary Block 8 | D, primary Block 7 | C, Block 8 | Figure 5: primary Small/ViT-B → primary pair plus Supplementary Figure S11 replication | Coherent J-top direction, scale 1; V-only with perturbed residual/full coherent; full Q/K/V pathways in primary pair | 100 outcome images/model; selected direction estimated from 4 images | Same coherent readout ratio concept, but Tiny/DINO only reduced rows and Block 8 | Tiny/DINO do not have full matched Q-only/K-only/V-only decomposition, coherent-gap attribution, or all-pattern rerouting audit. |
| Value-path coherence-gap attribution | A | D, Block 8 | D, Block 7 | A | Figure 5 primary pair only | Signed full coherent-minus-random-sign margin gap and frozen-attention V-only gap | 100 outcomes/model | Two primary models use same metric but different depths | Not evaluated as a matched gap-attribution measure for Tiny/DINO. Ratios above one reflect opposing secondary effects, not additive causal percentages. |
| Multi-block top-mode / near-null finite-radius damage contrast | D, existing | D, existing | D, existing | D, existing | Figure 7(c), previously absent as cross-model panel | Block 8; scale s=0.4; multi-block modes | Per-model final-logit L2 damage on fixed reference setup | Same ratio definition and scale across architectures | Directional outcome contrast, not a prediction correlation or independent image-level test. |
| Single-block versus end-to-end held-out damage prediction | D, extension | D, reused original 100 perturbations and re-summarized | D, extension | D, extension | Figure 7: pooled Small-only → model-specific four-model panels | Block 8, s=0.4, same family mixture (25 top modes, 25 middle modes, 25 end-to-end near-null modes, 25 isotropic Gaussian); local A_8 and end-to-end J_8_to_L | 100 perturbation vectors/model, each scored on 20 reference images; vector is the correlation unit | Matched designed distribution and outcome; A is averaged across 20 images while J is linearized at the first image | Aggregate correlations favor J for this mixture; within-family correlations are variable and sometimes negative. Distinct reference point prevents a strict matched-linearization interpretation. |
| Joint token–feature geometry | C, Block 8 | D, multiple-depth grid | D, multiple-depth grid | C, Block 8 | Figure 6 and Supplementary Figure S14 | Small/ViT-B depth grid; Tiny/DINO Block-8 replication | N=100 images/model; distinct cohort from M_l and operator perturbations; same cohort estimates directions and outcomes | Same finite-radius construction at Block 8; depth coverage is incomplete in Tiny/DINO | Direction-by-pattern grid is saturated with no residual degrees of freedom; report condition values descriptively without inferential interaction claims. |

## Section 5.1: corrected PCA-direction result

The old patch_fungibility/functional_geometry.py sorted descending eigenvalues but applied that order to eigenvectors after flipping only the eigenvalue array. Because torch.linalg.eigh returns eigenvalues and eigenvectors in ascending order, the index order was identity after the flip; the vector columns therefore remained ascending. The code then called column 0 PC1 and the last column PCbottom, reversing those labels. It also propagated that reversed ordering into covariance subspace slices. The implementation has been corrected so the same descending index is applied to both eigenvalues and eigenvectors.

Historical outputs/fungibility_functional_geometry CSV files were not rewritten. The revised Figure 4 and Section 5.1 use the double-precision reanalysis in the isolated extension directory. At depth 8, corrected PC1/PCbottom ratios are 0.0891 (Tiny), 0.0409 (Small), 65.2 (ViT-B), and 0.199 (DINOv2). Previous values 24.4553 (Small) and 0.0241773 (ViT-B) were based on reversed labels and must not be retained as PC1/PCbottom results.

The new ViT-B ratio is not exactly the reciprocal of the historical stored ratio. Its selected lowest-variance covariance eigenvector has a relative eigengap of 1.53e-5 at depth 8, and the original raw covariance matrix/eigenvectors were not archived. The historical covariance was also cast to float32 before eigendecomposition, whereas the reanalysis accumulates/eigendecomposes in float64. The exact source of this discrepancy cannot be isolated from saved files. Thus the corrected number is tied to the new matched-cohort reanalysis and should not be generalized to a stable low-variance subspace.

All 16 new M_l matrices pass the PSD check at tolerance 1e-10 lambda_max; no material negative eigenvalues are present. Raw eigenvalues and directional sensitivities are retained. At the 1e-3 cutoff, near-null fraction rises strongly in Tiny, Small, and ViT-B, but only from 0.26% to 1.56% in DINOv2. At the 1e-2 cutoff, DINOv2 depth 10 reaches 64.84%, demonstrating cutoff dependence. Entropy effective rank divided by D declines in all four.

## Section 5.2: Value-path evidence levels

Primary immediate-readout mean Euclidean norm ratios V-only/(K+V) under a coherent pattern are 1.1636996/1.1950681 = 0.97375 (DeiT-Small, Block 8) and 2.8756475/2.8943245 = 0.99355 (ViT-B, Block 7). Corresponding signed true-class logit-drop coherence-gap ratios are 0.707999 and 1.022240. The ViT-B ratio exceeds one because the secondary term opposes the measured Value-path contribution; it is not a fraction in an additive decomposition.

In the reduced Block-8 replication, frozen-attention V-only immediate-readout ratio to full perturbation is 100.107% for Tiny and 100.775% for DINOv2. This specific ratio is not evidence that all Q/K/V paths or all coherence-gap contrasts were audited in those models. Supplementary Figure S11 shows signed true-class logit drops for full and frozen-attention V-only conditions under coherent and random-sign patterns; the feature direction was estimated on four images and outcomes use 100 images.

## Section 5.3: prediction and directional outcomes

At s=0.4, existing four-model finite-radius multi-block top-mode / multi-block near-null-mode logit-L2 ratios are 4.62037, 8.35137, 12.55126, and 10.86577 (Tiny, Small, ViT-B, DINOv2). Separately, the new model-specific correlation extension uses 100 vectors/model in a fixed four-family mixture; each model uses a 20-image reference batch. Single-block/end-to-end Pearson estimates are 0.806/0.964 (Tiny), 0.753/0.975 (Small), 0.757/0.954 (ViT-B), and 0.883/0.946 (DINOv2); Spearman estimates are 0.720/0.964, 0.735/0.945, 0.725/0.934, and 0.829/0.944. CIs and raw outcomes are in extension CSVs. Within-family checks are descriptive and show heterogeneity; they are not pooled as independent perturbation families.

The original N=100 multi-block study's reported correlation values (multi-block Pearson r=0.974717 and Spearman rho=0.944554) were computed from `df_pred_deit`: DeiT-Small at Block 8 only, using 100 held-out perturbations with seed 42. They were not pooled across the four architectures. The extension reuses Small perturbation vectors and measures other models with the same fixed seed, scale, family counts, and calibration split. Its A estimates average a single-block operator over the reference batch while J uses one image as the linearization point, so conclusions are scoped to predictive association on the tested mixture.

## New and reused measurements

- Reused without rewriting: original Small perturbation-vector CSV; original two-model Q/K/V decomposition; Tiny/DINO reduced attention replication; four-model finite-radius top-versus-null ratios; joint-stream condition CSVs.
- Newly measured: margin-gradient spectra and covariance-PC directional sensitivities for all four architectures at four depths; model-specific A_8/J_8_to_L held-out prediction correlations for all four (Small raw vectors reused, re-summarized).
- Frozen execution protocol: docs/FUNGIBILITY_SECTION5_CROSS_ARCH_EXTENSION_PROTOCOL.md.
- Output location: outputs/fungibility_section5_cross_arch_extension/; per-perturbation rows, image IDs, family labels, bootstrap replicates, spectra, matrices, and validation manifests are stored there.
- Validation: extension manifests report PASS; manuscript validators are reported separately after export.

## Remaining limitations

1. M_l is a local margin-gradient second moment, not a Gram matrix of the full readout Jacobian; threshold-defined near-null directions do not prove nonlinear invariance.
2. DINOv2 has a small near-null fraction at the primary 1e-3 threshold; the metric changes substantially under a looser cutoff.
3. ViT-B’s lowest-variance covariance eigenvector is weakly separated; the PC1/PCbottom scalar ratio is sample-direction specific.
4. Tiny and DINOv2 attention results do not include full primary Q/K/V and gap-attribution controls.
5. Multi-block correlations are across designed perturbation vectors for one reference-image batch/model. They are not correlations over 100 independent images; within-family ranking is not uniformly improved by J.
6. Joint-stream depth-wide evidence is limited to Small and ViT-B. Tiny/DINO measurements are Block-8 replications, and the interaction regression is saturated.
