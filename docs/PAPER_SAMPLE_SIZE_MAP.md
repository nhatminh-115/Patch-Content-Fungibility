# Paper Sample-Size Map

Counts below are taken from experiment manifests and named source outputs. A perturbation count is not an image count.

| Experiment / claim | Architecture | Sample size | Sampling unit / split | Authoritative source |
|---|---|---:|---|---|
| Depthwise late replacement (C1, Fig. 2) | DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, DINOv2 ViT-S/14 | N=1,000 evaluation images per architecture in original V0.6/V1 studies; separate depth-6 follow-up uses N=1,000 calibration and N=1,000 evaluation images per ViT-B/DINOv2 architecture | Held-out images; replacement depth and fraction are method filters; depth 6 is explicitly a post hoc follow-up | `outputs/fungibility_v0_6/experiment_manifest.json`; `outputs/fungibility_v1/validation_results.json`; `outputs/fungibility_v1_depth6_followup/followup_manifest.json`; `docs/FUNGIBILITY_V0_6_REPORT.md`; `docs/FUNGIBILITY_V1_REPORT.md`; `docs/FUNGIBILITY_V1_DEPTH6_FOLLOWUP.md` |
| Activation geometry control (C2a) | DeiT-Tiny, DeiT-Small | N=1,000 evaluation + N=1,000 calibration images per model | Depth 8, 50% activation replacement; Top-1 classifier outcome | `outputs/fungibility_v0_7/experiment_manifest.json`; `docs/FUNGIBILITY_V0_7_REPORT.md` |
| PCA-basis coordinate-shuffle control (C2b; +1.474) | DeiT-Small, q=16 | N=100 held-out operator-space images | Mean `||J E||` norm difference, standard PCA vs shuffled PCA basis; not Top-1 | `outputs/fungibility_implicit_carrier_operator_audit/validation_manifest.json`; `pca_control_ablation.csv` |
| Complete-stream diversity (C3; grouped-K sweep shown in Fig. 3b) | DeiT-Tiny, DeiT-Small | N=1,000 evaluation images and N=1,000 calibration images per model | Image samples; 196 spatial patches replaced; multiple fixed seed/control rows | `outputs/fungibility_v0_8/experiment_manifest.json`; CSV outputs in same directory |
| Figure 3 panel (a) geometry display | ViT-B/16 AugReg, DINOv2 ViT-S/14 | N=1,000 evaluation images and N=1,000 calibration images per model | V1 50% replacement; separate display cohort from Fig. 3(b) | `outputs/fungibility_v1/validation_results.json`; `outputs/fungibility_v1/{vitb,dinov2}_geometry_results.csv` |
| Attention causal audit (C4, Fig. 5) | DeiT-Small depth 8, ViT-Base depth 7; replication rows per manifest | N=100 evaluation images | Image samples | `outputs/fungibility_attention_causal_audit/validation_manifest.json` (`num_eval_images`) |
| Functional-geometry pilot (C5 support, Fig. 4) | DeiT-Small, ViT-Base | N=100 images | Pilot evaluation images | `outputs/fungibility_functional_geometry/validation_manifest.json` (`num_images_pilot`) |
| Multi-block operator prediction (C5 primary) | DeiT-Small, ViT-Base, DeiT-Tiny, DINOv2 | N=100 held-out perturbations | Perturbation samples; must never be labeled held-out images | `outputs/fungibility_multiblock_operator/validation_manifest.json` (`num_heldout_perturbations`) |
| Strict operator-compression confirmatory (C6–C8, Figs. 6–7) | DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, DINOv2 ViT-S/14 | N=1,000 held-out images per architecture | Integer-count accuracy and per-image paired records; calibration split is separately manifested | `outputs/fungibility_operator_compression_confirmatory/validation_manifest.json`; `per_image_results.csv` |
| Static-alpha and PCA basis operator-space evidence (C2, C9a) | Four configured models for basis controls; DeiT-Small q16 static-alpha headline | N=100 held-out operator-space images; calibration N=500 activations where applicable | Linearized operator targets; report as operator-space only | `outputs/fungibility_implicit_carrier_operator_audit/validation_manifest.json` and source CSVs |
| Operator-space risk gate (C12a) | Rows as listed in gate audit | N=100 held-out operator-space examples | Risk-score/JE outcomes; exploratory | Same manifest and `gate_audit.csv` |
| Real-final carrier accuracy and gate (C9b, C12b, C14, Fig. S1) | DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, DINOv2 ViT-S/14 | N=1,000 held-out images per architecture | Actual model predictions and integer counts; disjoint calibration/evaluation IDs | `outputs/fungibility_real_final/validation_manifest.json`; `real_accuracy_per_image.csv`; `sample_manifest.csv` |
| Real-final throughput (C13, Fig. S1) | Four real-final models | 50 warmups + 100 measured iterations for each timing row | Actual full-model calls, not an image accuracy subset; hardware and callable details in raw rows | `outputs/fungibility_real_final/real_throughput_raw.csv` and `measurement_manifest.json` |

## Required Wording

- C2a activation-control Top-1 is N=1,000 per DeiT architecture; C2b's +1.474 PCA-basis result is N=100 operator-space evidence, not classification evidence.
- C4 attention causal audit: N=100 images.
- Functional geometry pilot: N=100 images.
- C5 multi-block operator study: N=100 held-out perturbations.
- C6–C8 strict confirmatory: N=1,000 held-out images per architecture.
- C9b/C12b/C14 real-final classification: N=1,000 held-out images per architecture.
- Never combine counts from distinct experiments into one sample-size claim.
