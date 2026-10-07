# V1 Depth-6 Follow-Up

## Scope

The original V1 depth sweep measured intervention depths `{5, 7, 8, 9, 10}`. This follow-up adds the previously unsampled depth 6 to answer the specific question raised about the gap between depths 5 and 7. It is a post hoc extension, not part of the original V1 depth set, and does not replace or modify any original V1 raw output.

The follow-up reuses the V1 calibration/evaluation split seeds (9101/9201), official model preprocessing, deterministic 25% patch mask (seed 21001), replacement controls, and Gaussian seeds (22001, 22002, 22003). Both models use N=1,000 calibration images and N=1,000 held-out evaluation images. The calibration and evaluation sets are disjoint. The evaluation unit is the image.

## Results

Top-1 accuracy on the 1,000 held-out evaluation images:

| Architecture | Clean | Zero | Centroid | Gaussian seed 22001 | Gaussian seed 22002 | Gaussian seed 22003 | Gaussian mean |
|---|---:|---:|---:|---:|---:|---:|---:|
| ViT-B/16 AugReg | 76.1% | 71.5% | 73.9% | 75.0% | 74.9% | 74.8% | 74.9% |
| DINOv2 ViT-S/14 | 78.8% | 28.8% | 70.6% | 74.1% | 75.0% | 74.8% | 74.6% |

The plot's Gaussian error bars show the sample standard deviation across the three fixed seeds. These results fill one depth point; they do not establish a general trend between all neighboring layers or change the paper's stated scope.

## Reproduction and provenance

- Runner: `scripts/run_fungibility_v1_depth6_followup.py`
- Machine-readable run manifest: `outputs/fungibility_v1_depth6_followup/followup_manifest.json`
- Summary rows: `outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv` and `dinov2_depth6_results.csv`
- Per-image records and split manifests are stored in the same output directory.
- Run device: NVIDIA GeForce RTX 5070 Laptop GPU; elapsed time: 44.29 seconds.
- Original files under `outputs/fungibility_v1/` were not modified.
