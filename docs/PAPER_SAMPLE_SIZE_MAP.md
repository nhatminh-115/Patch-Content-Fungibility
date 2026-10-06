# Paper Sample-Size Map

Sample sizes below come from the named manifests or report, not from draft prose. Mechanistic perturbation counts and image counts are different units.

| Claim / experiment | Architecture | Sample size | Split / sampling unit | Source |
|---|---|---:|---|---|
| Functional geometry pilot: image consistency / anisotropy | DeiT-Small, ViT-B/16 | N=100 images | Pilot/evaluation images; manifest does not identify a canonical N=1,000 split | `outputs/fungibility_functional_geometry/validation_manifest.json` |
| Attention causal audit | DeiT-Small, ViT-B/16; replication includes DeiT-Tiny and DINOv2 | N=100 evaluation images | Evaluation images | `outputs/fungibility_attention_causal_audit/validation_manifest.json` |
| Multi-block operator prediction | DeiT-Small, ViT-B/16, DeiT-Tiny, DINOv2 | N=100 held-out perturbations | Perturbations; do not describe this as 100 or 1,000 held-out images | `outputs/fungibility_multiblock_operator/validation_manifest.json` |
| Strict confirmatory operator compression | DeiT-Tiny, DeiT-Small, ViT-B/16 AugReg, DINOv2 ViT-S/14 | N=1,000 held-out images per architecture | ImageNet-1k validation subset, eval seed 9201; calibration seed 9101; report says disjoint | `outputs/fungibility_operator_compression_confirmatory/validation_manifest.json`; `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md` |
| Historical final-consolidation operator targets | DeiT-Tiny, DeiT-Small, ViT-B/16, DINOv2 | 500 calibration activations and 100 held-out evaluation activations | Target tensors identify train and val cohorts; the consolidation validation manifest says 500/100 | `outputs/fungibility_final_consolidation/validation_manifest.json`; `scripts/run_final_consolidation_benchmark.py` |
| Historical final-consolidation q ablation and random-basis control | Four configured architectures | N=100 evaluation activations; 25 random bases in the control | Operator-space evaluation, not real classification evaluation | `outputs/fungibility_final_consolidation/validation_manifest.json`; `scripts/run_final_consolidation_benchmark.py` |
| Historical confirmatory integer-count extraction | DeiT-Tiny, DeiT-Small, ViT-B/16, DINOv2 | N=1,000 per architecture/method/budget | Reused binary correctness rows; not a new run; logits/predictions are not in this derived summary | `outputs/fungibility_real_final/historical_confirmatory_accuracy_counts.csv`, sourced from confirmatory `per_image_results.csv` |
| New real-final static carrier / selective gate / throughput | Four requested architectures | UNMEASURED | No new validated run or full real-final per-image schema is present | `outputs/fungibility_real_final/validation_manifest.json` |

## Corrections required in scientific writing

- Do not describe the functional-geometry, attention-causal, or multi-block studies above as N=1,000.
- Do not reduce the strict confirmatory operator-compression evaluation to N=100. Its report and validation manifest specify N=1,000.
- The final-consolidation directory's 100 evaluation targets support at most its operator-space analyses. They do not support the synthetic Top-1 rows in its accuracy table.
- When reporting N=1,000 confirmatory accuracy, cite the confirmatory report and raw per-image output, and preserve its checkpoint, preprocessing, intervention depth, token semantics, multiplicity handling, and exact method/budget filters.
