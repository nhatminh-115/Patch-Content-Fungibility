# Repository Cleanup Inventory

Generated 2026-10-10 from git ls-files on the cleanup branch. This inventory covers every tracked path, including this file, and excludes two pre-existing untracked DOCX backups.

## Snapshot and disposition

- Cleanup branch: chore/pre-submission-repo-cleanup, based on fetched origin/main commit 8e7e464309373083df63db164ea9f47600fab20c.
- Pre-cleanup tag: pcf-pre-cleanup-2026-10-10 points to the exact local pre-cleanup HEAD 0f9acf9307a47ecaace7a784b15dd0f74ebb7dad. The fetched remote had advanced one commit before branching.
- Initial fetched tree: 897 tracked files. Cleanup tree index: 901 tracked files.
- No tracked file is deleted or moved. Archive and external-storage candidates remain present; these labels are review proposals only.
- .gitignore is unchanged and does not broadly ignore CSV, NPZ, Parquet, PDF, or DOCX evidence. Its existing *.pt rule does not untrack already committed calibration files.

### Primary classification counts

| Classification | Files |
|---|---:|
| KEEP — Essential | 366 |
| KEEP — Research History | 482 |
| ARCHIVE CANDIDATE — retain in place | 17 |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | 23 |
| UNRESOLVED — retain | 13 |
| GENERATED TEMPORARY | 0 |

Counts are mutually exclusive. External-storage rows are retained in the checkout and detailed separately. No tracked file met the generated-temporary definition.

## Canonical publication assets

Canonical status comes from the manuscript references and DOCX package, not directory names or render dates.

| Figure | Current manuscript source | DOCX comparison / note |
|---|---|---|
| Figure 1 | figures/paper_final_v4/figure1_overview.svg | figures/paper_final_v4/figure1_overview.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 2 | figures/paper_final_v4/figure2_depthwise.svg | figures/paper_final_v4/figure2_depthwise.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 3 | figures/paper_final_v4/figure3_geometry_diversity.svg | figures/paper_final_v4/figure3_geometry_diversity.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 4 | figures/paper_final_v4/figure4_anisotropic_geometry.svg | figures/paper_final_v4/figure4_anisotropic_geometry.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 5 | figures/paper_final_v4/figure5_value_path_cancellation.svg | figures/paper_final_v4/figure5_value_path_cancellation.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 6 | figures/paper_final_v4/figure6_joint_stream_geometry.svg | figures/paper_final_v4/figure6_joint_stream_geometry.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 7 | figures/paper_final_v4/figure7_end_to_end_operator.svg | figures/paper_final_v4/figure7_end_to_end_operator.png; all eight embedded main-DOCX images match by SHA-256. |
| Figure 8 | figures/paper_final_v4/figure8_operator_compression.svg | figures/paper_final_v4/figure8_operator_compression.png; all eight embedded main-DOCX images match by SHA-256. |
| Supplementary Figure S1 | figures/paper_final/supp/figS01_mask_robustness.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S2 | figures/paper_final/supp/figS02_retention_thresholds.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S3 | figures/paper_final/supp/figS03_pca_rank.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S4 | figures/paper_final/supp/figS04_pc1_amplitude.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S5 | figures/paper_final/supp/figS05_rank_propagation.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S6 | figures/paper_final/supp/figS06_carrier_equivalence.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S7 | figures/paper_final/supp/figS07_accuracy_vs_tokens.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S8 | figures/paper_final/supp/figS08_accuracy_vs_latency.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S9 | figures/paper_final/supp/figS09_geometry_bank_vs_pruning.png | The Supplementary DOCX contains 15 images; embedded S1–S9 pixels do not hash-match these freshly rendered PNGs after upstream commit 8e7e464. Keep both sides unchanged pending review. |
| Supplementary Figure S10 | figures/paper_final_v4/supp/figureS10_dinov2_margin_diversity.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |
| Supplementary Figure S11 | figures/paper_final_v4/supp/figureS11_value_path_replication.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |
| Supplementary Figure S12 | figures/paper_final_v4/supp/figureS12_primary_qkv_decomposition.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |
| Supplementary Figure S13 | figures/paper_final_v4/supp/figureS13_real_carrier_boundary.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |
| Supplementary Figure S14 | figures/paper_final_v4/supp/figureS14_joint_stream_geometry.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |
| Supplementary Figure S15 | figures/paper_final_v4/supp/figureS15_regularization_sensitivity.svg | Corresponding v4 PNG is embedded; S10–S15 images match by SHA-256. |

All 23 current Markdown figure references exist; PNG files decode and SVG files parse as XML. The publication validator confirms eight main and fifteen supplementary DOCX figures. The CI-generated figures/paper_final/main set is not linked by the current main manuscript and is not interchangeable with v4.

The cleanup did not write either DOCX. SHA-256 before and after is identical: main docs/PAPER_DRAFT_v5.docx = 8c143da1c05d80d057cdb80d3cb603d843db20ff576949a15fe9c22c13aa2460; supplementary docs/PAPER_SUPPLEMENTARY.docx = c0fd553d76f893b7d768a8f526c30f9a82f0cc8bbc117d7ac280555c4ebfdef0.

## Large-output audit

There are 23 tracked outputs files at or above 1 MiB, totaling 451,595,391 bytes (430.67 MiB). The tracked outputs tree totals 465,649,788 bytes. Eight files exceed 5 MiB and total 419,772,035 bytes. None was moved, deleted, ignored, or rewritten.

Two retained calibration-statistics files are byte-identical by SHA-256 (`43e817b90cdf5997df2f4b992499fd4d1893bb570db8219bfe05e5fde745e6ef`): `outputs/fungibility_v1/calibration_statistics.npz` and `outputs/fungibility_v1_grouped_diversity_extension/calibration_statistics_used.npz`. Their matching hash does not establish that either path is redundant: each has a distinct run/provenance role, so both remain tracked unless a future evidence audit verifies equivalence and approves a change.

No independent durable external archive copy was verified. The real-final measurement manifest has checksums for files within this repository; that is not evidence of a separate archive. Before any later transfer, make and independently verify a full archive copy and checksum manifest.

| Exact path | Bytes | Baseline SHA-256 | Purpose, claim support, dependencies, and proposal |
|---|---:|---|---|
| outputs/fungibility_dense_fraction/summary_by_mask_seed.csv | 1,769,089 | d68416242362b80e5ee126510aa94faf42949d83d21bd5d1bbe055d6cb3dc0c3 | Dense-fraction per-mask-seed outcome summaries. Direct input to Supplementary Figure S1. Re-run dense-fraction evaluation; multiple GPU inference conditions. Keep in Git pending explicit approval. |
| outputs/fungibility_operator_compression_confirmatory/per_image_results.csv | 27,927,030 | c5df9974277b671d8a8d97155bc3e1e50bd7f4d92f39a8643a02942105f4b139 | Per-image, method, and budget outcomes for strict exact-Jacobian confirmatory compression. Primary Table IV and paired claim source; read by scripts/validate_paper_final.py. Re-run scripts/run_operator_compression_confirmatory.py; costly per-image downstream-Jacobian and model evaluation. Keep in Git pending explicit approval. |
| outputs/fungibility_operator_compression_confirmatory/same_group_ablation.csv | 2,708,288 | 7c0011debc874d99e0150c3f40926f1a960ab4fbabdb4e2bcc9ed96c8c0adb1a | Confirmatory same-assignment Group Mean versus Operator-Aware residual ablation. Supports Section 6 same-image/same-budget residual comparisons. Re-run exact-Jacobian confirmatory analysis; GPU intensive. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/real_accuracy_logits_deit_small.npz | 78,022,056 | 51f640c6dea1e2c668c2bf96f10c11a622513d84ccdc6b930536f839470d43e6 | Actual-model logits by architecture for the real-final carrier benchmark. Validation requires all four logits files; paired per-image/summary CSVs support S5 and the carrier audit. Re-run scripts/run_real_final_accuracy.py with cached ImageNet and checkpoints; GPU inference. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/real_accuracy_logits_deit_tiny.npz | 77,966,760 | 3d0ab084e7ed784a9f85116011027dbca6875d5b441dc0ab70774a5be01258d8 | Actual-model logits by architecture for the real-final carrier benchmark. Validation requires all four logits files; paired per-image/summary CSVs support S5 and the carrier audit. Re-run scripts/run_real_final_accuracy.py with cached ImageNet and checkpoints; GPU inference. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/real_accuracy_logits_dinov2.npz | 77,960,243 | 92a305fa9923b6de17879d342055117670801bf7350910c9ecceaafd9619e339 | Actual-model logits by architecture for the real-final carrier benchmark. Validation requires all four logits files; paired per-image/summary CSVs support S5 and the carrier audit. Re-run scripts/run_real_final_accuracy.py with cached ImageNet and checkpoints; GPU inference. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/real_accuracy_logits_vit_base.npz | 77,818,643 | dd015ff1761672af2ca91dd5ac835f72f05ae94bad283621c77b1bfebe9d289f | Actual-model logits by architecture for the real-final carrier benchmark. Validation requires all four logits files; paired per-image/summary CSVs support S5 and the carrier audit. Re-run scripts/run_real_final_accuracy.py with cached ImageNet and checkpoints; GPU inference. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/real_accuracy_per_image.csv | 17,910,526 | 9b0d1c62b5838248c6553e04f141ab2088c8115292bfa04465057378a600e08d | Actual classifier predictions, correctness, flips, logit damage, and margin per held-out image. Direct evidence for Supplementary Table S5 and real-carrier claims; checked by real-final validation. Re-run scripts/run_real_final_accuracy.py with ImageNet and four checkpoints; GPU inference. Keep in Git pending explicit approval. |
| outputs/fungibility_real_final/sample_manifest.csv | 1,231,373 | d901108bc5dddd6dba1bf0d65290c5e6363b4f7f4613733dd60672aeaed58358 | Real-final calibration/evaluation image IDs and labels. Provenance for S5/S13 and split-overlap checks. Regenerate only with the same ImageNet parquet shards/seeds; preserve exact IDs. Keep in Git pending explicit approval. |
| outputs/fungibility_regularization_sensitivity/per_image_results.csv | 2,611,662 | 53ca04392bdcd66062dbd3bb00188ed337bc2a5ab9272b5633ab14d8d28fcd0b | Original first-200-classes exploratory per-image sensitivity results. Historical comparison to the corrected randomized cohort; not the canonical corrected study. Preserve historical result; do not overwrite or rerun as substitute. Keep in Git pending explicit approval. |
| outputs/fungibility_regularization_sensitivity_v2_class_randomized/per_image_results.csv | 2,634,591 | 5f6263a571a360081aa5628fa905008e2209ce17b881683c8234e8463b7d1617 | Corrected class-randomized per-image sensitivity results across factors/budgets. Supports S15, Table S6, paired comparisons, and corrected sensitivity interpretation. Exact-Jacobian sensitivity rerun is expensive; preserve original outcomes. Keep in Git pending explicit approval. |
| outputs/fungibility_section5_cross_arch_extension/functional_geometry/metric_and_covariance_matrices.npz | 56,127,494 | c6c60e9a71b095bc932dd3a272bb47ba89f8b178d3c534672d34ed9c9bfbe0f8 | Float64 functional metric and activation-covariance matrices from the cross-architecture extension. Supports reanalysis of Figure 4/Table III/S2 spectra and directional measures; CSV summaries are direct publication inputs. Re-run scripts/run_section5_cross_arch_extension.py; calibration and gradient/Jacobian work is GPU intensive. Keep in Git pending explicit approval. |
| outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/stratified_bootstrap_correlations.csv | 1,243,289 | 012139ac1f03def874b14ccb5c68d5c4f1ddb6673041e37ac7810be1b814665a | Bootstrap replicates for cross-architecture operator-prediction correlations. Uncertainty source for Figure 7 and Supplementary Table S3. Recalculate from archived perturbation rows; CPU analysis, no model rerun. Keep in Git pending explicit approval. |
| outputs/fungibility_v0_5/experiment_manifest.json | 1,651,607 | a9ec1f4b7c28bebce5914141bff52d939d00ad474b63c9aa781bc1d0975f295e | Large historical V0.5 run manifest and configuration record. Research-history provenance, not a direct current figure/table input. Keep the record; replay requires the V0.5 protocol and model runs. Keep in Git pending explicit approval. |
| outputs/fungibility_v0_8/small_image_results.parquet | 1,142,202 | ad801c201334586dc728354d1785000486a132def100dc24cd5a130a43f1760a | V0.8 image-level grouped-diversity outcomes. Supports grouped-diversity source rows for Figure 3/Table II. Re-run V0.8 multi-seed model evaluation; retain current result. Keep in Git pending explicit approval. |
| outputs/fungibility_v0_8/tiny_image_results.parquet | 1,069,318 | 3d5e10c1ac3bc3ab9107c2717ca50c9c471c863934f05b2c2996eb7f72521045 | V0.8 image-level grouped-diversity outcomes. Supports grouped-diversity source rows for Figure 3/Table II. Re-run V0.8 multi-seed model evaluation; retain current result. Keep in Git pending explicit approval. |
| outputs/fungibility_v0_9/small_image_results.parquet | 2,154,618 | 105a97338b32aa5a54b5026dcf1db65f8a38a15291ca5971000fc7ea934ec881 | V0.9 image-level low-rank/PCA outcomes. Historical/exploratory source supporting Supplementary Figures S3–S5. Re-run V0.9 protocol and model evaluation; retain current result. Keep in Git pending explicit approval. |
| outputs/fungibility_v0_9/tiny_image_results.parquet | 2,018,726 | 2ccb5f22c73ee3e0e64513fa1247d2a67a1464776759fb030b4e68c610ab7a57 | V0.9 image-level low-rank/PCA outcomes. Historical/exploratory source supporting Supplementary Figures S3–S5. Re-run V0.9 protocol and model evaluation; retain current result. Keep in Git pending explicit approval. |
| outputs/fungibility_v1/calibration_statistics.npz | 2,787,884 | 43e817b90cdf5997df2f4b992499fd4d1893bb570db8219bfe05e5fde745e6ef | V1 calibration statistics for cross-architecture interventions. Preserves calibration-derived representations used by V1 outcomes. Recompute on calibration images; requires activation extraction. Keep in Git pending explicit approval. |
| outputs/fungibility_v1/dinov2_image_results.parquet | 3,007,636 | aefb80fe47a34667bf52d1c1821ec98de9428066c5390924ab11a3049f630d53 | DINOv2 V1 per-image geometry/diversity outcomes. Supports V1 geometry/grouped-diversity evidence used by Figure 3/Table II. Re-run scripts/run_fungibility_v1.py; DINOv2/ImageNet inference. Keep in Git pending explicit approval. |
| outputs/fungibility_v1/vitb_image_results.parquet | 3,005,189 | 8ebbb18720c96808b00ba51c0159b518efba02a46d852132033539fa2b021705 | ViT-B V1 per-image geometry/diversity outcomes. Supports V1 geometry evidence used by Figure 3/Table II. Re-run scripts/run_fungibility_v1.py; ViT-B/ImageNet inference. Keep in Git pending explicit approval. |
| outputs/fungibility_v1_grouped_diversity_extension/calibration_statistics_used.npz | 2,787,884 | 43e817b90cdf5997df2f4b992499fd4d1893bb570db8219bfe05e5fde745e6ef | Calibration-derived statistics consumed by the grouped-diversity extension. Preserves inputs to cross-architecture group-diversity results. Recompute on the calibration cohort; requires model activation extraction. Keep in Git pending explicit approval. |
| outputs/fungibility_v1_grouped_diversity_extension/per_image_results.csv | 6,039,283 | 5e2b466020dc49bbaa6f0eb716a0b744f33d7b0270de2fb9073781b0dd7191e0 | Image-level V1 grouped-diversity outcomes over models and seeds. Supports Figure 3 grouped-diversity and Figure S10 source aggregates. Re-run scripts/run_grouped_diversity_extension.py; repeated GPU evaluation. Keep in Git pending explicit approval. |

Externalizing every listed file could reduce the working-tree checkout by at most 451,595,391 bytes only if later approved and independently archived. It would not erase the existing Git-history blobs. No history rewrite or LFS migration is proposed.

## Archive candidates — preserve in place

These are candidates for a separately reviewed historical archive; none is approved for movement or deletion.

| Exact path | Bytes | Purpose / origin | References and current-claim support | Restoration / proposal |
|---|---:|---|---|---|
| docs/PAPER_DRAFT_v4.docx | 2,629,821 | Superseded editable manuscript export preceding v5. | The current source is PAPER_DRAFT.md and v5 DOCX. validate_paper_final.py has a fallback to v4 only if v5 is absent; no current claim selects v4 as canonical. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain untouched; review manual-formatting needs before any historical packaging. |
| figures/paper_final_v2/figure1_conceptual_overview.png | 180,601 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure1_conceptual_overview.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure2_depthwise_fungibility.png | 180,601 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure2_depthwise_fungibility.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure3_geometry_diversity_constraints.png | 180,601 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure3_geometry_diversity_constraints.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure4_functional_geometry.png | 111,645 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure4_functional_geometry.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure5_local_vs_end_to_end_jacobian.png | 111,645 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure5_local_vs_end_to_end_jacobian.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure6_operator_aware_compression_frontier.png | 192,543 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure6_operator_aware_compression_frontier.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure7_carrier_space_formulation.png | 146,006 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure7_carrier_space_formulation.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v2/figure8_accuracy_throughput_frontier.png | 147,057 | Earlier v2 figure from run_final_consolidation_benchmark.py: figure8_accuracy_throughput_frontier.png. | Referenced by the runner, PAPER_FINAL_EXPERIMENT_SUMMARY.md, and FINAL_PROXY_ARTIFACT_AUDIT.md. Audit disallows proxy-derived Top-1/throughput/frontier panels as current evidence; no current manuscript figure path points here. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each asset in place; assess its exact visual/data role before any archival action. |
| figures/paper_final_v3/README.md | 1,784 | Earlier v3 SVG figure iteration or README: README.md. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure1_conceptual.svg | 50,611 | Earlier v3 SVG figure iteration or README: figure1_conceptual.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure2_depthwise.svg | 70,909 | Earlier v3 SVG figure iteration or README: figure2_depthwise.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure3_geometry_diversity.svg | 74,800 | Earlier v3 SVG figure iteration or README: figure3_geometry_diversity.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure4_anisotropy.svg | 51,492 | Earlier v3 SVG figure iteration or README: figure4_anisotropy.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure5_value_end_to_end.svg | 76,489 | Earlier v3 SVG figure iteration or README: figure5_value_end_to_end.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/figure6_confirmatory_frontier.svg | 108,191 | Earlier v3 SVG figure iteration or README: figure6_confirmatory_frontier.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |
| figures/paper_final_v3/supp/figureS1_real_carrier_boundary.svg | 138,234 | Earlier v3 SVG figure iteration or README: figureS1_real_carrier_boundary.svg. | Directory-level links remain in PAPER_NUMBER_TRACEABILITY.md and REAL_FINAL_BENCHMARK_REPORT.md. Current manuscript paths use v4; these references are historical/stale. | Current tracked copy and GitHub remote are available; no independent non-Git archive was verified. Retain each file in place; review dependent historical documentation before any archival action. |

No removal is approved. The files can currently be restored from the checkout/remote and Git objects; no independent non-Git preservation copy is verified.

## Unresolved items kept intact

| Path | Finding | Action |
|---|---|---|
| figures/paper_final/main/* (all tracked PDF/PNG files) | Separate workflow output cited by historical reviewer/migration records; current manuscript references v4. Name similarity does not make them interchangeable. | Preserve; root README and guides identify v4 as canonical. |
| outputs/fungibility_real_final/README.md | Says no complete real-final result passed validation, while current measurement outputs and validation_manifest.json report COMPLETE/PASS and the validator passes 12/12. | Preserve verbatim pending chronology/content review. |

## Complete tracked-file inventory

Every path below is classified. Role text identifies its document or experiment; candidate-specific references and support decisions are expanded above. Historical version labels do not imply permission to remove.

| Classification | Purpose / role | Exact tracked path |
|---|---|---|
| KEEP — Research History | Repository-local research workflow guidance. | .agents/skills/pcf-paper-upgrade/SKILL.md |
| KEEP — Research History | Repository-local research workflow guidance. | .agents/skills/pcf-paper-upgrade/agents/openai.yaml |
| KEEP — Research History | Repository-local research workflow guidance. | .agents/skills/pcf-paper-upgrade/references/auxiliary-skills.md |
| KEEP — Research History | Repository-local research workflow guidance. | .agents/skills/pcf-paper-upgrade/references/evidence-boundaries.md |
| KEEP — Research History | Repository-local research workflow guidance. | .agents/skills/pcf-paper-upgrade/references/review-and-figures.md |
| KEEP — Essential | Repository automation workflow. | .github/workflows/arxiv-export.yml |
| KEEP — Essential | Repository automation workflow. | .github/workflows/paper-figures.yml |
| KEEP — Essential | Targeted cache/development ignore rules. | .gitignore |
| KEEP — Essential | Machine-readable citation metadata. | CITATION.cff |
| KEEP — Essential | Source-code license. | LICENSE |
| KEEP — Essential | Repository entry point. | README.md |
| KEEP — Research History | Archived preprint tooling or historical metadata. | arxiv/README.md |
| KEEP — Research History | Archived preprint tooling or historical metadata. | arxiv/build_arxiv_package.py |
| KEEP — Research History | Archived preprint tooling or historical metadata. | arxiv/metadata.yaml |
| KEEP — Research History | Archived preprint tooling or historical metadata. | arxiv/submission_metadata.txt |
| KEEP — Research History | Documentation: Final Proxy Artifact Audit | docs/FINAL_PROXY_ARTIFACT_AUDIT.md |
| KEEP — Research History | Documentation: Strict Sanity & Validation Audit: Amortized Operator-Aware Token Compression | docs/FUNGIBILITY_AMORTIZED_OPERATOR_AUDIT.md |
| KEEP — Research History | Documentation: Research Protocol: Amortized Operator-Aware Token Compression | docs/FUNGIBILITY_AMORTIZED_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Comprehensive Benchmark Report: Amortized Operator-Aware Token Compression | docs/FUNGIBILITY_AMORTIZED_OPERATOR_REPORT.md |
| KEEP — Research History | Documentation: Experimental Protocol: Causal Audit of the Attention Aggregation Cancellation Mechani | docs/FUNGIBILITY_ATTENTION_CAUSAL_AUDIT_PROTOCOL.md |
| KEEP — Research History | Documentation: Causal Decomposition of the Coherence Effect: Attention Aggregation Cancellation as a | docs/FUNGIBILITY_ATTENTION_CAUSAL_AUDIT_REPORT.md |
| KEEP — Research History | Documentation: Protocol: Batched Operator Compression | docs/FUNGIBILITY_BATCHED_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Batched Operator Compression: Throughput Acceleration, FlashAttention Multiplicity, a | docs/FUNGIBILITY_BATCHED_OPERATOR_REPORT.md |
| KEEP — Research History | Documentation: Protocol: Fungibility-to-Compression Proof-of-Concept (Weighted Centroid Carrier) | docs/FUNGIBILITY_COMPRESSION_POC_PROTOCOL.md |
| KEEP — Research History | Documentation: Report: Fungibility-to-Compression Proof-of-Concept (Weighted Centroid Carrier) | docs/FUNGIBILITY_COMPRESSION_POC_REPORT.md |
| KEEP — Research History | Documentation: Patch Fungibility: Dense Fraction & Spatial-Mask Robustness Sweep Protocol | docs/FUNGIBILITY_DENSE_FRACTION_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Fungibility — Dense Fraction / Mask Robustness Sweep Report | docs/FUNGIBILITY_DENSE_FRACTION_REPORT.md |
| KEEP — Research History | Documentation: Fungibility Full Operator Protocol: Unified Token × Feature Transmission Spectrum | docs/FUNGIBILITY_FULL_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Full Fungibility Operator Report: Unified Token × Feature Transmission Spectrum | docs/FUNGIBILITY_FULL_OPERATOR_REPORT.md |
| KEEP — Research History | Documentation: Functional Equivalence Geometry Protocol | docs/FUNGIBILITY_FUNCTIONAL_GEOMETRY_PROTOCOL.md |
| KEEP — Research History | Documentation: Functional Equivalence Geometry of Patch-Content Fungibility: Empirical Mapping Repor | docs/FUNGIBILITY_FUNCTIONAL_GEOMETRY_REPORT.md |
| KEEP — Research History | Documentation: Protocol: Geometry-Diversity Bank Proof-of-Concept (POC) | docs/FUNGIBILITY_GEOMETRY_BANK_PROTOCOL.md |
| KEEP — Research History | Documentation: Report: Geometry-Diversity Bank Proof-of-Concept (POC) | docs/FUNGIBILITY_GEOMETRY_BANK_REPORT.md |
| KEEP — Research History | Documentation: Strict Sanity & Validation Audit: Implicit Carrier-Space Operator | docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md |
| KEEP — Research History | Documentation: Pre-Registered Research Protocol: Implicit Carrier-Space Operator Solving and Selecti | docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Research Report: Implicit Carrier-Space Operator Solving and Selective Operator Activ | docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_REPORT.md |
| KEEP — Research History | Documentation: Protocol: Fungibility Joint Stream Geometry (Feature Direction × Token-Space Pattern) | docs/FUNGIBILITY_JOINT_STREAM_GEOMETRY_PROTOCOL.md |
| KEEP — Research History | Documentation: Empirical Joint Geometry of Patch-Content Fungibility: Feature Direction × Token-Spac | docs/FUNGIBILITY_JOINT_STREAM_GEOMETRY_REPORT.md |
| KEEP — Research History | Documentation: Joint Value-Key Downstream Low-Transmission Protocol | docs/FUNGIBILITY_JOINT_VALUE_KEY_PROTOCOL.md |
| KEEP — Research History | Documentation: Joint Value-Key Downstream Low-Transmission Report | docs/FUNGIBILITY_JOINT_VALUE_KEY_REPORT.md |
| KEEP — Research History | Documentation: Pre-Registered Protocol: Lightweight Operator Predictors and Shared Envelope Geometry | docs/FUNGIBILITY_LIGHTWEIGHT_OPERATOR_PREDICTOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Lightweight Operator Predictors: Shared Envelope Geometry, Factor Asymmetry, and Batc | docs/FUNGIBILITY_LIGHTWEIGHT_OPERATOR_PREDICTOR_REPORT.md |
| KEEP — Research History | Documentation: Fungibility Multi-Block Operator Protocol: Downstream-Persistent Low-Transmission Geo | docs/FUNGIBILITY_MULTIBLOCK_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: Multi-Block Operator Report: Downstream-Persistent Low-Transmission Geometry | docs/FUNGIBILITY_MULTIBLOCK_OPERATOR_REPORT.md |
| KEEP — Essential | Documentation: Confirmatory Benchmark Protocol: Operator-Aware Token Compression | docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_PROTOCOL.md |
| KEEP — Essential | Documentation: Strict Confirmatory Benchmark Report: Operator-Aware Token Compression | docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md |
| KEEP — Research History | Documentation: Fungibility Operator Compression Protocol | docs/FUNGIBILITY_OPERATOR_COMPRESSION_PROTOCOL.md |
| KEEP — Research History | Documentation: Fungibility Operator Compression Report | docs/FUNGIBILITY_OPERATOR_COMPRESSION_REPORT.md |
| KEEP — Research History | Documentation: Protocol: Practical Operator Compression | docs/FUNGIBILITY_PRACTICAL_OPERATOR_COMPRESSION_PROTOCOL.md |
| KEEP — Research History | Documentation: Practical Operator Compression: Early Intervention, Fast Solvers, and the Accuracy-La | docs/FUNGIBILITY_PRACTICAL_OPERATOR_COMPRESSION_REPORT.md |
| KEEP — Research History | Documentation: Experimental Protocol: Token-Transmission Predictive Operator of Patch-Content Fungib | docs/FUNGIBILITY_PREDICTIVE_OPERATOR_PROTOCOL.md |
| KEEP — Research History | Documentation: From Empirical Discovery to a Predictive Operator: Mapping Patch-Content Fungibility  | docs/FUNGIBILITY_PREDICTIVE_OPERATOR_REPORT.md |
| KEEP — Research History | Documentation: Fungibility Predictive Principle Protocol | docs/FUNGIBILITY_PREDICTIVE_PRINCIPLE_PROTOCOL.md |
| KEEP — Research History | Documentation: Mechanistic Follow-Up Report: Evaluating Clean-State Representation Geometry & Downst | docs/FUNGIBILITY_PREDICTIVE_PRINCIPLE_REPORT.md |
| KEEP — Research History | Documentation: Frozen Protocol: Section 5 Cross-Architecture Extension | docs/FUNGIBILITY_SECTION5_CROSS_ARCH_EXTENSION_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.5: Protocol Specification | docs/FUNGIBILITY_V0_5_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.5: Scientific Report | docs/FUNGIBILITY_V0_5_REPORT.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.6: Recovery Fraction Calculation Audit | docs/FUNGIBILITY_V0_6_AUDIT.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.6: Protocol Specification | docs/FUNGIBILITY_V0_6_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.6: Scientific Report | docs/FUNGIBILITY_V0_6_REPORT.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.7: Protocol Specification | docs/FUNGIBILITY_V0_7_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.7: Scientific Report | docs/FUNGIBILITY_V0_7_REPORT.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0.8: Protocol Specification | docs/FUNGIBILITY_V0_8_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Fungibility V0.8: Token-Diversity / Effective-Rank Sufficiency Report | docs/FUNGIBILITY_V0_8_REPORT.md |
| KEEP — Research History | Documentation: Patch Fungibility V0.9 Protocol: Natural Low-Rank Variance & Downstream Rank-Expansio | docs/FUNGIBILITY_V0_9_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Fungibility V0.9: Natural Low-Rank Variance & Downstream Rank-Expansion Report | docs/FUNGIBILITY_V0_9_REPORT.md |
| KEEP — Research History | Documentation: PATCH CONTENT FUNGIBILITY V0: Prior-Art Audit and Novelty Boundary | docs/FUNGIBILITY_V0_PRIOR_ART.md |
| KEEP — Research History | Documentation: PATCH CONTENT FUNGIBILITY V0: Frozen Experimental Protocol | docs/FUNGIBILITY_V0_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Content Fungibility V0: Mechanistic Falsification Report | docs/FUNGIBILITY_V0_REPORT.md |
| KEEP — Research History | Documentation: V1 Depth-6 Follow-Up | docs/FUNGIBILITY_V1_DEPTH6_FOLLOWUP.md |
| KEEP — Research History | Documentation: Confirmatory Grouped-Diversity Extension Protocol | docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_PROTOCOL.md |
| KEEP — Research History | Documentation: Grouped-Diversity Extension Report | docs/FUNGIBILITY_V1_GROUPED_DIVERSITY_EXTENSION_REPORT.md |
| KEEP — Research History | Documentation: Patch Fungibility V1 Protocol: Cross-Model & Training-Regime Generalization | docs/FUNGIBILITY_V1_PROTOCOL.md |
| KEEP — Research History | Documentation: Patch Fungibility V1: Cross-Model and Training-Regime Generalization Report | docs/FUNGIBILITY_V1_REPORT.md |
| KEEP — Research History | Documentation: Patch Fungibility V1: Cross-Version Synthesis Audit & Discrepancy Log | docs/FUNGIBILITY_V1_SYNTHESIS_AUDIT.md |
| KEEP — Research History | Documentation: Protocol: Image-Conditioned Geometry-Compatible Residual Carrier POC | docs/IMAGE_CONDITIONED_RESIDUAL_CARRIER_PROTOCOL.md |
| KEEP — Research History | Documentation: Report: Image-Conditioned Geometry-Compatible Residual Carrier POC | docs/IMAGE_CONDITIONED_RESIDUAL_CARRIER_REPORT.md |
| KEEP — Research History | Documentation: Citation and bibliography audit | docs/PAPER_CITATION_AUDIT.md |
| KEEP — Research History | Documentation: Paper Claims Audit: Patch Content Fungibility in Vision Transformers | docs/PAPER_CLAIMS_AUDIT.md |
| KEEP — Essential | Documentation: Patch-Content Fungibility: Geometry, Functional Transmission, and Operator-Aware Toke | docs/PAPER_DRAFT.md |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | docs/PAPER_DRAFT_v4.docx |
| KEEP — Essential | Publication, protocol, validation, or research-history record. | docs/PAPER_DRAFT_v5.docx |
| KEEP — Essential | Documentation: Canonical Paper Evidence Table: Patch Content Fungibility | docs/PAPER_EVIDENCE_TABLE.md |
| KEEP — Research History | Documentation: Publication Figure & Table Plan: Patch Content Fungibility | docs/PAPER_FIGURE_PLAN.md |
| KEEP — Research History | Documentation: Figure Review v4 | docs/PAPER_FIGURE_REVIEW_V4.md |
| KEEP — Research History | Documentation: Paper Figure Style Guide | docs/PAPER_FIGURE_STYLE.md |
| KEEP — Research History | Documentation: Paper Final Audit: Methodological Verification & Claim Hygiene | docs/PAPER_FINAL_AUDIT.md |
| KEEP — Essential | Documentation: Final Paper Claims Table | docs/PAPER_FINAL_CLAIMS_TABLE.md |
| KEEP — Essential | Documentation: Final manuscript consistency audit — pre-restructure snapshot | docs/PAPER_FINAL_CONSISTENCY_AUDIT.md |
| KEEP — Research History | Documentation: Final Paper Experiment Summary: Patch Content Fungibility & Operator-Aware Carrier Co | docs/PAPER_FINAL_EXPERIMENT_SUMMARY.md |
| KEEP — Essential | Documentation: Paper Number Traceability | docs/PAPER_NUMBER_TRACEABILITY.md |
| KEEP — Research History | Documentation: Manuscript Structure & Section Outline: Patch Content Fungibility in Vision Transform | docs/PAPER_OUTLINE.md |
| KEEP — Research History | Documentation: Paper Reconciliation & Source-of-Truth Audit Report | docs/PAPER_RECONCILIATION_REPORT.md |
| KEEP — Essential | Publication, protocol, validation, or research-history record. | docs/PAPER_REFERENCES.bib |
| KEEP — Research History | Documentation: Related Work & Conceptual Positioning: Patch Content Fungibility | docs/PAPER_RELATED_WORK_POSITIONING.md |
| KEEP — Research History | Documentation: Reviewer-Facing Manuscript Audit | docs/PAPER_REVIEWER_AUDIT.md |
| KEEP — Essential | Documentation: Paper Sample-Size Map | docs/PAPER_SAMPLE_SIZE_MAP.md |
| KEEP — Research History | Documentation: Section 5 Cross-Architecture Evidence Audit | docs/PAPER_SECTION5_CROSS_ARCHITECTURE_AUDIT.md |
| KEEP — Essential | Documentation: Paper Submission Assets | docs/PAPER_SUBMISSION_ASSETS.md |
| KEEP — Essential | Documentation: Paper Submission Readiness | docs/PAPER_SUBMISSION_READINESS.md |
| KEEP — Essential | Publication, protocol, validation, or research-history record. | docs/PAPER_SUPPLEMENTARY.docx |
| KEEP — Essential | Documentation: Supplementary Material | docs/PAPER_SUPPLEMENTARY_DRAFT.md |
| KEEP — Research History | Documentation: PCF Paper Skill Dry-Run Test | docs/PCF_PAPER_SKILL_TEST.md |
| KEEP — Research History | Documentation: PCF Manuscript Upgrade Review | docs/PCF_PAPER_UPGRADE_REPORT.md |
| KEEP — Research History | Documentation: Real Final Benchmark Report | docs/REAL_FINAL_BENCHMARK_REPORT.md |
| KEEP — Research History | Documentation: Regularization Factor Audit | docs/REGULARIZATION_FACTOR_AUDIT.md |
| KEEP — Research History | Documentation: Exact-Jacobian Regularization Sensitivity (Post-Hoc) | docs/REGULARIZATION_SENSITIVITY_REPORT.md |
| KEEP — Essential | Documentation: Corrected Regularization Sensitivity: Class-Randomized Calibration Cohort | docs/REGULARIZATION_SENSITIVITY_REPORT_CORRECTED.md |
| KEEP — Essential | Documentation: Repository Structure | docs/REPOSITORY_STRUCTURE.md |
| KEEP — Essential | Documentation: Repository Cleanup Inventory | docs/REPO_CLEANUP_INVENTORY.md |
| KEEP — Essential | Documentation: Repository Cleanup Report | docs/REPO_CLEANUP_REPORT.md |
| KEEP — Essential | Documentation: Reproducibility Guide | docs/REPRODUCIBILITY_GUIDE.md |
| KEEP — Research History | Documentation: ResCancel to Patch-Content-Fungibility Migration Inventory | docs/RESCANCEL_MIGRATION_INVENTORY.md |
| KEEP — Research History | Documentation: Migration Provenance: Consolidating Patch Content Fungibility Research | docs/RESCANCEL_MIGRATION_PROVENANCE.md |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_a_target_subspace_variability.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_b_predicted_vs_oracle_subspace.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_c_oracle_recovery.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_d_accuracy_token_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_e_static_vs_dynamic.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_f_rank_latency_tradeoff.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_g_accuracy_latency_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_amortized_operator/figure_h_cross_architecture_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_a_causal_path_decomposition.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_b_headwise_gamma_prediction.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_c_blockwise_propagation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_d_attention_shift.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_e_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_attention_causal_audit/figure_f_spatial_frequency_response.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_a_batch_crossover.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_b_throughput_vs_batch.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_c_accuracy_throughput_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_d_flashattention_multiplicity.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_e_hybrid_grouping.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_f_depth_batch_interaction.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_g_predictor_batch_scaling.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_batched_operator/figure_h_cross_architecture_pareto.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_compression_poc/accuracy_vs_latency.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_compression_poc/accuracy_vs_tail_tokens.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_compression_poc/accuracy_vs_total_flops.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_compression_poc/equivalence_error.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_dense_fraction/dense_fraction_accuracy.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_dense_fraction/dense_fraction_margin.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_dense_fraction/dense_fraction_recovery.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_dense_fraction/mask_seed_robustness.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_dense_fraction/threshold_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_a_full_operator_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_b_top_vs_null_modes.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_c_predicted_vs_observed.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_d_mode_factorization.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_e_depth_evolution.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_f_intervention_projection.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_g_null_mode_scaling.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_full_operator/figure_h_cross_architecture_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_1_directional_tolerance_curves.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_2_fungibility_spectrum_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_3_functional_metric_eigenspectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_4_covariance_functional_alignment.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_5_intervention_projections.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_functional_geometry/figure_6_constructive_surrogate_test.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_geometry_bank/accuracy_vs_token_budget.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_geometry_bank/delta_vs_pruning.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_geometry_bank/pca_vs_kmeans.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_a_restricted_oracle_recovery.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_b_correction_basis_ablation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_c_hg_prediction_quality.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_d_operator_information_vs_output_dim.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_e_gate_quality.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_f_selective_activation_curve.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_g_accuracy_throughput_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_implicit_carrier_operator/figure_h_cross_architecture_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_stream_geometry/figure_a_token_feature_heatmap.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_stream_geometry/figure_b_fraction_sweep.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_stream_geometry/figure_c_key_combination_curves.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_stream_geometry/figure_d_spatial_pattern_comparison.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_stream_geometry/figure_e_replication_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_a_value_vs_key_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_b_subspace_overlap.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_c_value_null_vs_joint_vk.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_d_finite_radius_curves.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_e_attention_shift.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_f_scaling_exponents.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_g_blockwise_rerouting.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_joint_value_key/figure_h_cross_architecture_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_a_oracle_envelope_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_b_envelope_capture.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_c_token_vs_feature_variability.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_d_predictor_overlap_vs_cost.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_e_functional_recovery.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_f_accuracy_vs_throughput.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_g_batch_crossover.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_lightweight_operator_predictor/figure_h_cross_architecture_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_a_single_vs_multiblock_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_b_single_null_vs_multi_null.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_c_predicted_vs_observed.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_d_nullspace_rotation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_e_leakage_trace.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_f_finite_radius_curves.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_g_depth_comparison.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_multiblock_operator/figure_h_cross_architecture_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_a_reconstruction_objective.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_b_matched_budget_accuracy.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_c_accuracy_token_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_d_operator_residual_vs_damage.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_e_grouping_ablation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_f_operator_ablation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_g_low_rank_tradeoff.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression/figure_h_cross_architecture_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_a_accuracy_token_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_b_accuracy_retention.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_c_operator_vs_best_baseline.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_d_same_group_carrier_effect.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_e_operator_residual_vs_damage.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_f_low_rank_ablation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_g_cross_architecture_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_operator_compression_confirmatory/figure_h_runtime_breakdown.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_a_runtime_breakdown.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_b_depth_latency_lower_bound.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_c_accuracy_vs_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_d_operator_advantage_vs_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_e_fast_solver_tradeoff.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_f_accuracy_token_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_g_accuracy_latency_frontier.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_practical_operator_compression/figure_h_pareto_summary.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_a_operator_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_b_predicted_vs_observed_damage.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_c_top_vs_null_modes.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_d_finite_radius_validation.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_e_depth_evolution.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_f_cross_architecture_replication.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_operator/figure_g_token_mode_spatial_structure.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_principle/figure_a_depth_alignment.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_principle/figure_b_predictor_scatter.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_principle/figure_c_loao_predicted_vs_observed.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_predictive_principle/figure_d_spectral_sensitivity_decomposition.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_residual_carrier/accuracy_vs_method.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_residual_carrier/delta_accuracy_heatmap.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0/accuracy_by_condition_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0/condition_difference_heatmap.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0/fungibility_gap_by_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0/margin_damage_by_condition.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0/replacement_norm_distribution.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_5/condition_accuracy.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_5/condition_margin_damage.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_5/distribution_distance_vs_damage.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_5/norm_vs_performance.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/accuracy_by_depth_fraction.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/correct_vs_wrong_depth_gaussian.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/damage_by_depth_fraction.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/depth_transition_heatmap.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/gaussian_recovery_by_depth.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/gaussian_vs_random_sphere.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_6/global_mean_vs_gaussian.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/cls_vs_patch_replacement.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/full_patch_replacement.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/prototype_cosine_sweep.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/prototype_performance_by_fraction.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/prototype_scale_sweep.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/prototype_sign_flip_sweep.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_7/wrong_depth_mean_comparison.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/accuracy_vs_designed_rank.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/accuracy_vs_unique_token_count.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/attention_rank_through_blocks.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/effective_rank_through_blocks.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/margin_vs_effective_rank.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/pca_vs_random_subspace.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_8/shared_vs_independent_noise.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/accuracy_vs_natural_rank.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/attention_recovery_through_blocks.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/eigenvalue_spectrum.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/natural_vs_energy_matched_rank.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/pc1_amplitude_sweep.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/pc_identity_comparison.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v0_9/rank_expansion_through_blocks.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/content_fungibility_across_models.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/depth_generalization.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/geometry_controls_across_models.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/learned_vs_random_1d.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/replacement_fraction_generalization.png |
| KEEP — Research History | Study-specific or historical figure/preview; preserve with its study. | figures/fungibility_v1/shared_vs_independent_across_models.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig01_conceptual_overview.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig01_conceptual_overview.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig02_depth_emergence.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig02_depth_emergence.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig03_dense_fraction.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig03_dense_fraction.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig04_geometry_constraint.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig04_geometry_constraint.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig05_diversity_constraint.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig05_diversity_constraint.png |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig06_lowdim_direction.pdf |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | figures/paper_final/main/fig06_lowdim_direction.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS01_mask_robustness.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS01_mask_robustness.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS02_retention_thresholds.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS02_retention_thresholds.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS03_pca_rank.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS03_pca_rank.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS04_pc1_amplitude.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS04_pc1_amplitude.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS05_rank_propagation.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS05_rank_propagation.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS06_carrier_equivalence.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS06_carrier_equivalence.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS07_accuracy_vs_tokens.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS07_accuracy_vs_tokens.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS08_accuracy_vs_latency.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS08_accuracy_vs_latency.png |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS09_geometry_bank_vs_pruning.pdf |
| KEEP — Essential | Current supplementary S1–S9 PNG or PDF companion. | figures/paper_final/supp/figS09_geometry_bank_vs_pruning.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure1_conceptual_overview.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure2_depthwise_fungibility.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure3_geometry_diversity_constraints.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure4_functional_geometry.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure5_local_vs_end_to_end_jacobian.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure6_operator_aware_compression_frontier.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure7_carrier_space_formulation.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v2/figure8_accuracy_throughput_frontier.png |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/README.md |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure1_conceptual.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure2_depthwise.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure3_geometry_diversity.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure4_anisotropy.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure5_value_end_to_end.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/figure6_confirmatory_frontier.svg |
| ARCHIVE CANDIDATE — retain in place | Superseded manuscript export or earlier figure iteration; details in archive-candidate register. | figures/paper_final_v3/supp/figureS1_real_carrier_boundary.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/FIGURE_MANIFEST.md |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/contact_sheet.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure1_overview.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure1_overview.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure2_depthwise.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure2_depthwise.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure3_geometry_diversity.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure3_geometry_diversity.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure4_anisotropic_geometry.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure4_anisotropic_geometry.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure5_value_path_cancellation.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure5_value_path_cancellation.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure6_joint_stream_geometry.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure6_joint_stream_geometry.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure7_end_to_end_operator.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure7_end_to_end_operator.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure8_operator_compression.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figure8_operator_compression.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figureS11_value_path_replication.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/figureS11_value_path_replication.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure1_overview.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure2_depthwise.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure3_geometry_diversity.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure4_anisotropic_geometry.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure5_value_path_cancellation.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure6_joint_stream_geometry.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure7_end_to_end_operator.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figure8_operator_compression.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/previews/figureS11_value_path_replication.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/source/figure1_overview_user.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/source/figure4_pca_scores.csv |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS10_dinov2_margin_diversity.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS10_dinov2_margin_diversity.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS11_value_path_replication.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS11_value_path_replication.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS12_primary_qkv_decomposition.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS12_primary_qkv_decomposition.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS13_real_carrier_boundary.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS13_real_carrier_boundary.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS14_joint_stream_geometry.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS14_joint_stream_geometry.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS15_regularization_sensitivity.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/figureS15_regularization_sensitivity.svg |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/previews/figureS10_dinov2_margin_diversity.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/previews/figureS11_value_path_replication.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/previews/figureS12_primary_qkv_decomposition.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/previews/figureS13_real_carrier_boundary.png |
| KEEP — Essential | Current v4 publication figure, source artwork, manifest, or preview. | figures/paper_final_v4/supp/previews/figureS14_joint_stream_geometry.png |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/budget_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/direct_carrier_baseline.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/mode_error_tolerance.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/mode_separability.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/oracle_recovery.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/principal_angles.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/rank_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/replication_summary.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/runtime_breakdown.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/static_vs_dynamic.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/subspace_prediction.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/target_statistics.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_amortized_operator. | outputs/fungibility_amortized_operator/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/clean_flip_analysis.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/dataset_alignment_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/oracle_recovery_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/overlap_vs_compression.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/recomputed_accuracy.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/runtime_audit.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_amortized_operator_audit. | outputs/fungibility_amortized_operator_audit/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/attention_shift.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/blockwise_propagation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/causal_conditions.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/headwise_gamma.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/headwise_prediction.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/qkv_decomposition.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/replication_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/residual_path.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_attention_causal_audit. | outputs/fungibility_attention_causal_audit/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/batch_crossover.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/batch_runtime_breakdown.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/batch_throughput.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/depth_batch_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/hybrid_grouping_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/matched_budget_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/multiplicity_kernel_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/pareto_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/predictor_batch_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/solver_batch_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/throughput_frontier.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_batched_operator. | outputs/fungibility_batched_operator/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/baseline_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/compute_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/equivalence_results.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/experiment_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/full_eval_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/latency_summary.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_compression_poc. | outputs/fungibility_compression_poc/validation_results.json |
| KEEP — Essential | image-level outcomes for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/all_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/auc_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/cliff_summary.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/experiment_manifest.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/fraction_grid.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/mask_permutations.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/summary_across_masks.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_dense_fraction/summary_by_mask_seed.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/threshold_crossings.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_dense_fraction. | outputs/fungibility_dense_fraction/validation_results.json |
| KEEP — Research History | experiment artifact for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/README.md |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_accuracy_table.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_claim_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_functional_table.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_pareto_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_q_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_random_basis_control.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/final_throughput_table.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_final_consolidation. | outputs/fungibility_final_consolidation/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/depth_evolution.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/finite_radius_curves.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/intervention_projection.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/mode_factorization.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/null_scaling.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/operator_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/random_perturbation_prediction.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/replication_summary.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/residual_damage.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/singular_mode_validation.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_full_operator. | outputs/fungibility_full_operator/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/constructive_surrogates.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/covariance_function_alignment.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/directional_tolerance.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/functional_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/fungible_dimension.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/imagewise_consistency.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/intervention_projection.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_functional_geometry. | outputs/fungibility_functional_geometry/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_geometry_bank. | outputs/fungibility_geometry_bank/all_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_geometry_bank. | outputs/fungibility_geometry_bank/delta_vs_pruning.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_geometry_bank. | outputs/fungibility_geometry_bank/experiment_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_geometry_bank. | outputs/fungibility_geometry_bank/matched_budget_summary.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_geometry_bank. | outputs/fungibility_geometry_bank/validation_results.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/accuracy_throughput_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/batch_throughput.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/correction_basis_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/functional_recovery.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/gate_quality.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/predictor_accuracy.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/restricted_oracle_recovery.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/runtime_breakdown.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/selective_activation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/sufficient_statistics_ablation.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_implicit_carrier_operator. | outputs/fungibility_implicit_carrier_operator/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/claim_classification.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/conditioning_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/frontier_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/gate_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/paired_sample_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/pca_control_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/predicted_alpha_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/q_scaling_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/random_basis_distribution.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/recovery_denominator_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/runtime_audit.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/stabilized_full_oracle.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/static_alpha_audit.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_implicit_carrier_operator_audit. | outputs/fungibility_implicit_carrier_operator_audit/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/condition_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/directional_curves.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/fraction_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/replication_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/token_feature_interaction.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_joint_stream_geometry. | outputs/fungibility_joint_stream_geometry/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/attention_shift.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/blockwise_rerouting.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/depth_comparison.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/finite_radius_curves.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/joint_operator_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/key_operator_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/random_prediction.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/replication_summary.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/scaling_exponents.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/value_operator_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_joint_value_key. | outputs/fungibility_joint_value_key/vk_subspace_overlap.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/accuracy_throughput_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/batch_throughput.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/crossover_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/direct_carrier_control.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/envelope_capture.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/factor_variability.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/functional_recovery.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/oracle_recovery.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/predictor_architecture_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/principal_angles.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/runtime_breakdown.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/subspace_prediction.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_lightweight_operator_predictor. | outputs/fungibility_lightweight_operator_predictor/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/depth_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/finite_radius_curves.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/historical_intervention_projection.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/leakage_trace.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/multiblock_spectrum.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/nullspace_rotation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/random_prediction.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/replication_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/scaling_exponents.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/single_vs_multi_null.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_multiblock_operator. | outputs/fungibility_multiblock_operator/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/budget_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/calibration_operator_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/collapse_parity.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/full_length_surrogate_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/grouping_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/low_rank_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/matched_budget_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/operator_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/reconstruction_objectives.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/replication_summary.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/residual_vs_damage.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_operator_compression. | outputs/fungibility_operator_compression/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/architecture_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/baseline_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/budget_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/collapse_parity.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/operator_residual_analysis.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/paired_statistics.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_operator_compression_confirmatory/per_image_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/runtime_breakdown.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_operator_compression_confirmatory/same_group_ablation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/seed_summary.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_operator_compression_confirmatory. | outputs/fungibility_operator_compression_confirmatory/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/accuracy_latency_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/depth_latency_lower_bound.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/depth_sweep.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/detailed_solver_profile.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/fast_solver_ablation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/grouping_profile.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/latency_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/matched_budget_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/pareto_frontier.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/predictor_depth_ablation.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_practical_operator_compression. | outputs/fungibility_practical_operator_compression/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/depth_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/feature_token_matrix.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/finite_radius_curves.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/operator_spectrum.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/random_pattern_prediction.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/replication_summary.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/singular_mode_validation.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/spatial_mode_analysis.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_predictive_operator. | outputs/fungibility_predictive_operator/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_principle. | outputs/fungibility_predictive_principle/layer_metrics.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_principle. | outputs/fungibility_predictive_principle/leave_one_architecture_out.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_principle. | outputs/fungibility_predictive_principle/predictor_vs_fungibility.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_predictive_principle. | outputs/fungibility_predictive_principle/transition_predictions.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_predictive_principle. | outputs/fungibility_predictive_principle/validation_manifest.json |
| UNRESOLVED — retain | Alternate main-figure render or conflicting benchmark directory note; preserve pending reconciliation. | outputs/fungibility_real_final/README.md |
| KEEP — Essential | calibration state for experiment folder fungibility_real_final. | outputs/fungibility_real_final/calibration_deit_small.pt |
| KEEP — Essential | calibration state for experiment folder fungibility_real_final. | outputs/fungibility_real_final/calibration_deit_tiny.pt |
| KEEP — Essential | calibration state for experiment folder fungibility_real_final. | outputs/fungibility_real_final/calibration_dinov2.pt |
| KEEP — Essential | calibration state for experiment folder fungibility_real_final. | outputs/fungibility_real_final/calibration_vit_base.pt |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/historical_confirmatory_accuracy_counts.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_real_final. | outputs/fungibility_real_final/measurement_manifest.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_real_final. | outputs/fungibility_real_final/paper_final_validation.json |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/real_accuracy_logits_deit_small.npz |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/real_accuracy_logits_deit_tiny.npz |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/real_accuracy_logits_dinov2.npz |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/real_accuracy_logits_vit_base.npz |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/real_accuracy_per_image.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_accuracy_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_accuracy_throughput_frontier.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_selective_gate_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_static_carrier_ablation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_throughput_raw.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_real_final. | outputs/fungibility_real_final/real_throughput_summary.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_real_final/sample_manifest.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_real_final. | outputs/fungibility_real_final/validation_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/aggregated_by_architecture_budget_factor.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/cross_cell_robustness_descriptive.csv |
| KEEP — Research History | figure/preview for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_carrier_displacement.png |
| KEEP — Research History | experiment artifact for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_carrier_displacement.svg |
| KEEP — Research History | figure/preview for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_logit_damage.png |
| KEEP — Research History | experiment artifact for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_logit_damage.svg |
| KEEP — Research History | figure/preview for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_operator_residual.png |
| KEEP — Research History | experiment artifact for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_operator_residual.svg |
| KEEP — Research History | figure/preview for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_top1.png |
| KEEP — Research History | experiment artifact for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/figures/factor_vs_top1.svg |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/manifest_benchmark8.json |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/manifest_full.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/paired_factor10_vs_3_30.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_regularization_sensitivity/per_image_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/per_image_results_benchmark8.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/runtime_benchmark8.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity. | outputs/fungibility_regularization_sensitivity/runtime_by_architecture.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/aggregated_by_architecture_budget_factor.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/cohort_comparison_vs_v1.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/cross_cell_robustness_descriptive.csv |
| KEEP — Essential | figure/preview for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_carrier_displacement.png |
| KEEP — Essential | experiment artifact for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_carrier_displacement.svg |
| KEEP — Essential | figure/preview for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_logit_damage.png |
| KEEP — Essential | experiment artifact for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_logit_damage.svg |
| KEEP — Essential | figure/preview for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_operator_residual.png |
| KEEP — Essential | experiment artifact for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_operator_residual.svg |
| KEEP — Essential | figure/preview for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_top1.png |
| KEEP — Essential | experiment artifact for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/figures/factor_vs_top1.svg |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/manifest_benchmark8.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/manifest_full.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/paired_factor10_vs_3_30.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/per_image_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/per_image_results_benchmark8.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/runtime_benchmark8.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/runtime_by_architecture.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/selected_cohort.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_regularization_sensitivity_v2_class_randomized. | outputs/fungibility_regularization_sensitivity_v2_class_randomized/selected_cohort_benchmark8.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_residual_carrier. | outputs/fungibility_residual_carrier/heatmap_grid.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_residual_carrier. | outputs/fungibility_residual_carrier/summary_by_condition.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_residual_carrier. | outputs/fungibility_residual_carrier/trial_results.csv |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_residual_carrier. | outputs/fungibility_residual_carrier/validation_manifest.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/calibration_split_seed_metadata.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/checkpoint_provenance.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/calibration_sample_ids.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/metric_and_covariance_matrices.npz |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/pc_directional_sensitivity.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/raw_eigenspectrum.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/functional_geometry/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/calibration_reference_image_ids.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/model_specific_correlations.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/per_perturbation_results.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/stratified_bootstrap_correlations.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/validation_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/multiblock_prediction/within_family_correlations.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_section5_cross_arch_extension. | outputs/fungibility_section5_cross_arch_extension/validation_manifest.json |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_v0. | outputs/fungibility_v0/decision_summary.json |
| KEEP — Research History | image-level outcomes for experiment folder fungibility_v0. | outputs/fungibility_v0/image_records_small.parquet |
| KEEP — Research History | image-level outcomes for experiment folder fungibility_v0. | outputs/fungibility_v0/image_records_tiny.parquet |
| KEEP — Research History | run/validation manifest for experiment folder fungibility_v0. | outputs/fungibility_v0/results_manifest.json |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v0_5/experiment_manifest.json |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/small_activation_diagnostics.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/small_condition_comparison.csv |
| KEEP — Research History | image-level outcomes for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/small_image_results.parquet |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/small_seed_results.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/tiny_activation_diagnostics.csv |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/tiny_condition_comparison.csv |
| KEEP — Research History | image-level outcomes for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/tiny_image_results.parquet |
| KEEP — Research History | tabular outcome/summary for experiment folder fungibility_v0_5. | outputs/fungibility_v0_5/tiny_seed_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/calibration_split.csv |
| KEEP — Essential | array or calibration statistics for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/calibration_statistics.npz |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/evaluation_split.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/experiment_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/small_condition_comparisons.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/small_depth_fraction_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/small_seed_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/summary_all_models.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/tiny_condition_comparisons.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/tiny_depth_fraction_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_6. | outputs/fungibility_v0_6/tiny_seed_results.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/experiment_manifest.json |
| KEEP — Essential | array or calibration statistics for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/prototype_vectors.npz |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/prototype_vectors_metadata.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_cls_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_cosine_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_fraction_summary.csv |
| KEEP — Essential | image-level outcomes for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_image_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_prototype_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_scale_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/small_sign_flip_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_cls_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_cosine_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_fraction_summary.csv |
| KEEP — Essential | image-level outcomes for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_image_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_prototype_comparison.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_scale_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_7. | outputs/fungibility_v0_7/tiny_sign_flip_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/attention_rank_diagnostics.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/decision_summary.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/energy_verification.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/experiment_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/grouped_diversity_results.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/pca_basis_metadata.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/rank_condition_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/representation_rank_diagnostics.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/secondary_75_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/shared_vs_independent_results.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v0_8/small_image_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_8. | outputs/fungibility_v0_8/statistical_comparisons.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v0_8/tiny_image_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/attention_diagnostics.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/decision_summary.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/eigenvalue_spectrum.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/experiment_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/natural_vs_energy_matched_rank.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/pc1_scale_sweep.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/pc_identity_results.csv |
| KEEP — Essential | array or calibration statistics for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/pca_cache_deit_small_patch16_224.npz |
| KEEP — Essential | array or calibration statistics for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/pca_cache_deit_tiny_patch16_224.npz |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/random_direction_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v0_9. | outputs/fungibility_v0_9/rank_propagation.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v0_9/small_image_results.parquet |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v0_9/tiny_image_results.parquet |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v1/calibration_statistics.npz |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1. | outputs/fungibility_v1/decision_summary.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/dinov2_1d_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/dinov2_depth_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/dinov2_diversity_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/dinov2_fraction_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/dinov2_geometry_results.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v1/dinov2_image_results.parquet |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1. | outputs/fungibility_v1/experiment_manifest.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1. | outputs/fungibility_v1/manual_forward_validation.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1. | outputs/fungibility_v1/model_metadata.json |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1. | outputs/fungibility_v1/validation_results.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/vitb_1d_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/vitb_depth_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/vitb_diversity_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/vitb_fraction_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1. | outputs/fungibility_v1/vitb_geometry_results.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v1/vitb_image_results.parquet |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/calibration_split.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/dinov2_depth6_per_image.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/dinov2_depth6_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/evaluation_split.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/followup_manifest.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/vitb_depth6_per_image.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_depth6_followup. | outputs/fungibility_v1_depth6_followup/vitb_depth6_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/calibration_split_used.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v1_grouped_diversity_extension/calibration_statistics_used.npz |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/endpoint_validation.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/evaluation_split_used.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/experiment_metadata.json |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/monotonicity_summary.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/paired_image_comparisons.csv |
| EXTERNAL STORAGE CANDIDATE — retain pending approval | Large experiment output; experiment purpose and claim role are detailed in storage-candidate register. | outputs/fungibility_v1_grouped_diversity_extension/per_image_results.csv |
| KEEP — Essential | tabular outcome/summary for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/seed_level_results.csv |
| KEEP — Essential | run/validation manifest for experiment folder fungibility_v1_grouped_diversity_extension. | outputs/fungibility_v1_grouped_diversity_extension/validation_results.json |
| KEEP — Research History | tabular outcome/summary for experiment folder migration_validation. | outputs/migration_validation/file_hash_comparison.csv |
| KEEP — Research History | experiment artifact for experiment folder migration_validation. | outputs/migration_validation/legacy_reference_audit.txt |
| KEEP — Research History | run/validation manifest for experiment folder migration_validation. | outputs/migration_validation/migration_manifest.json |
| KEEP — Research History | experiment artifact for experiment folder migration_validation. | outputs/migration_validation/validation_summary.txt |
| KEEP — Essential | Manuscript license/publication information. | paper/LICENSE.md |
| KEEP — Research History | Manuscript license/publication information. | paper/README.md |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/__init__.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/amortized_operator.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/attention_causal_audit.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/batched_operator_compression.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/compression_models.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/compression_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/dataset.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/dense_fraction_analysis.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/dense_fraction_masks.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/dense_fraction_models.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/dense_fraction_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/full_fungibility_operator.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/functional_geometry.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/geometry_bank_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/implicit_carrier_operator.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/interventions.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/joint_stream_geometry.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/joint_value_key.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/lightweight_operator_predictor.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/masks.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/metrics.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/models.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/multiblock_operator.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/operator_compression.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/operator_compression_confirmatory.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/practical_operator_compression.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/predictive_operator.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/predictive_principle.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/real_final_carriers.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/residual_carrier_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_5_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_5_interventions.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_5_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_5_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_calibration.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_dataset.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_masks.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_6_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_7_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_7_masks.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_7_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_7_prototypes.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_7_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_diagnostics.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_interventions.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_pca.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_8_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_9_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_9_diagnostics.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_9_interventions.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_9_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v0_9_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v1_decision.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v1_interventions.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v1_models.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v1_pipeline.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/v1_validation.py |
| KEEP — Essential | Reusable model, data, intervention, geometry, or compression implementation. | patch_fungibility/validation.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/analyze_operator_target_compressibility.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/analyze_restricted_carrier_oracle.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/audit_amortized_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/audit_implicit_carrier_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/audit_multiplicity_flashattention.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/build_paper_figures_v4.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/build_real_final_frontier.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/compare_regularization_sensitivity_cohorts.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_amortized_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_batched_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_hybrid_grouping.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_implicit_carrier_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_lightweight_operator_predictor.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/eval_selective_operator_gate.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/export_figure4_pca_scores.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/export_paper_markdown_to_docx.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/generate_operator_targets.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_compression.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_dense_fraction.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_geometry_bank.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_5_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_6_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_7_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_8_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_9_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v0_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_fungibility_v1_figures.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_regularization_sensitivity_manuscript.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/plot_residual_carrier_figures.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/profile_batched_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/profile_implicit_carrier_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/profile_lightweight_operator_predictor.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/profile_operator_compression.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/render_paper_figures_final.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/render_paper_final_v3.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_attention_causal_audit.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_final_consolidation_benchmark.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_full_fungibility_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_functional_geometry.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_compression.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_dense_fraction.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_geometry_bank.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0_5.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0_6.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0_7.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0_8.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v0_9.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v1.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_fungibility_v1_depth6_followup.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_grouped_diversity_extension.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_joint_stream_geometry.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_joint_value_key.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_multiblock_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_operator_compression.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_operator_compression_confirmatory.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_practical_operator_compression.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_predictive_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_predictive_principle.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_real_final_accuracy.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_real_final_throughput.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_regularization_sensitivity.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_regularization_sensitivity_v1_first200_classes.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_residual_carrier_experiment.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/run_section5_cross_arch_extension.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/train_amortized_operator.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/train_carrier_statistics_predictor.py |
| KEEP — Research History | Experiment, figure-generation, validation, audit, or analysis code. | scripts/train_lightweight_operator_predictor.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/update_paper_docx_preserving_edits.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/validate_paper_final.py |
| KEEP — Essential | Experiment, figure-generation, validation, audit, or analysis code. | scripts/validate_real_final_benchmark.py |

## Preservation decisions

- Keep current publication files, all current-claim source data, scripts, protocols, manifests, validators, historical experiments, failed/negative results, and prior file iterations.
- Do not move archive candidates in this first pass.
- Do not migrate to Git LFS or upload externally without explicit approval and an independently checked archive.
- The two pre-existing untracked DOCX backups under outputs/ are not part of git ls-files and are not included in the inventory or cleanup commit.
