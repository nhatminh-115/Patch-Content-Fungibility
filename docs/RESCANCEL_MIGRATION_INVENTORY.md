# ResCancel to Patch-Content-Fungibility Migration Inventory

**Source Repository:** `https://github.com/nhatminh-115/ResCancel` (HEAD `6bc6b6ea9f6b0e95b8f202c13b2bb7ccfef66179`)
**Target Canonical Repository:** `https://github.com/nhatminh-115/Patch-Content-Fungibility` (Pre-migration HEAD `4eb557b20654f80028ea08e2a4b00dcf71bc8a67`)
**Migration Branch:** `migrate/rescancel-pcf-2026-10-06`
**Total Tracked Items Inspected:** 713

## Summary of Actions

| Action | Count | Description |
|---|---|---|
| `COPY_NEW` | 303 | Newly migrated PCF research artifacts (code, scripts, reports, outputs, figures) |
| `KEEP_TARGET` | 302 | Preserved canonical target files (e.g. `PAPER_DRAFT.md`, cleaned scripts, datasets) |
| `UPDATE_FROM_SOURCE` | 1 | Files updated to incorporate latest generalized scientific logic |
| `MERGE_MANUALLY` | 1 | Manually merged configuration files (e.g. `.gitignore`) |
| `SKIP_LEGACY` | 106 | Legacy ResCancel / Delta files excluded from canonical PCF repository |

## Detailed Inventory Table

| Path | Source Status | Target Status | Source SHA256 | Target Pre-Migration SHA256 | Action | Notes |
|---|---|---|---|---|---|---|
| `.github/workflows/arxiv-export.yml` | EXISTS | ABSENT | `2388af10e216` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `.github/workflows/paper-figures.yml` | EXISTS | ABSENT | `d8500377cd32` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `.gitignore` | EXISTS | EXISTS | `472f0552608f` | `6fd71ccf0550` | `MERGE_MANUALLY` | Preserve target gitignore and add *.pt and scratch/ ignore rules |
| `CITATION.cff` | ABSENT | EXISTS | `N/A` | `e10b23f96fd5` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `LICENSE` | EXISTS | EXISTS | `1eb85fc97224` | `1eb85fc97224` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `README.md` | EXISTS | EXISTS | `6f4189337fc5` | `e872f574c544` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `arxiv/README.md` | EXISTS | EXISTS | `2eb6fcb39031` | `2eb6fcb39031` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `arxiv/build_arxiv_package.py` | EXISTS | EXISTS | `21c8c8ca1557` | `21c8c8ca1557` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `arxiv/metadata.yaml` | EXISTS | EXISTS | `504237b9c6f1` | `504237b9c6f1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `arxiv/submission_metadata.txt` | EXISTS | EXISTS | `ffb7be1ed579` | `ffb7be1ed579` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `delta_transport/__init__.py` | EXISTS | ABSENT | `83cc678f3f0c` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/metrics.py` | EXISTS | ABSENT | `ba2dc9b493b2` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/models.py` | EXISTS | ABSENT | `97136ac2fe57` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/oracle.py` | EXISTS | ABSENT | `edcbc84b38cf` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/pipeline.py` | EXISTS | ABSENT | `c0deeaa99f49` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/v0_5_controls.py` | EXISTS | ABSENT | `ee6cb129c068` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/v0_5_decision.py` | EXISTS | ABSENT | `0d3982e6523d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/v0_5_pipeline.py` | EXISTS | ABSENT | `1b2b2958370d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/v0_5_validation.py` | EXISTS | ABSENT | `340d7ea881ac` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `delta_transport/validation.py` | EXISTS | ABSENT | `cb6e196b1baa` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/DELTA_V0_5_PROTOCOL.md` | EXISTS | ABSENT | `9d4c0680bc35` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/DELTA_V0_5_REPORT.md` | EXISTS | ABSENT | `4396b71dbf82` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/DELTA_V0_PRIOR_ART.md` | EXISTS | ABSENT | `3c2ac3b5f0b3` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/DELTA_V0_PROTOCOL.md` | EXISTS | ABSENT | `be4b6bc72920` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/DELTA_V0_REPORT.md` | EXISTS | ABSENT | `aa2181fe5c84` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/FUNGIBILITY_AMORTIZED_OPERATOR_AUDIT.md` | EXISTS | ABSENT | `197e6386b631` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_AMORTIZED_OPERATOR_PROTOCOL.md` | EXISTS | ABSENT | `a3ad9f67569b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_AMORTIZED_OPERATOR_REPORT.md` | EXISTS | ABSENT | `ad1f51314e51` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_ATTENTION_CAUSAL_AUDIT_PROTOCOL.md` | EXISTS | ABSENT | `d239a03d1c45` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_ATTENTION_CAUSAL_AUDIT_REPORT.md` | EXISTS | ABSENT | `219a2ff926d5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_BATCHED_OPERATOR_PROTOCOL.md` | EXISTS | ABSENT | `ddba5aecd376` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_BATCHED_OPERATOR_REPORT.md` | EXISTS | ABSENT | `a50abf1e9b52` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_COMPRESSION_POC_PROTOCOL.md` | EXISTS | EXISTS | `ba1d17e09a3e` | `814f4893cbbb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_COMPRESSION_POC_REPORT.md` | EXISTS | EXISTS | `326867a8be35` | `fdee9e355ffc` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_DENSE_FRACTION_PROTOCOL.md` | EXISTS | EXISTS | `e81826df6d37` | `e81826df6d37` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_DENSE_FRACTION_REPORT.md` | EXISTS | EXISTS | `b901054f97a6` | `b901054f97a6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_FULL_OPERATOR_PROTOCOL.md` | EXISTS | ABSENT | `e46e1c04c8dd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_FULL_OPERATOR_REPORT.md` | EXISTS | ABSENT | `e833ad732c39` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_FUNCTIONAL_GEOMETRY_PROTOCOL.md` | EXISTS | ABSENT | `86857c2b08e7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_FUNCTIONAL_GEOMETRY_REPORT.md` | EXISTS | ABSENT | `5c0eb1c9d8c9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_GEOMETRY_BANK_PROTOCOL.md` | EXISTS | EXISTS | `44d4444cfd60` | `31813006acfa` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_GEOMETRY_BANK_REPORT.md` | EXISTS | EXISTS | `4eb61430e37e` | `e846ad8aeb02` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_JOINT_STREAM_GEOMETRY_PROTOCOL.md` | EXISTS | ABSENT | `99e022e431e0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_JOINT_STREAM_GEOMETRY_REPORT.md` | EXISTS | ABSENT | `80e997ed5168` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_JOINT_VALUE_KEY_PROTOCOL.md` | EXISTS | ABSENT | `d1f38f829a11` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_JOINT_VALUE_KEY_REPORT.md` | EXISTS | ABSENT | `e354a81e7ff7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_MULTIBLOCK_OPERATOR_PROTOCOL.md` | EXISTS | ABSENT | `947ef206cb9f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_MULTIBLOCK_OPERATOR_REPORT.md` | EXISTS | ABSENT | `d8a7d1ee2b84` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_PROTOCOL.md` | EXISTS | ABSENT | `6cad412dff67` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md` | EXISTS | ABSENT | `e900a6298891` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_OPERATOR_COMPRESSION_PROTOCOL.md` | EXISTS | ABSENT | `caab13ee310d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_OPERATOR_COMPRESSION_REPORT.md` | EXISTS | ABSENT | `d90dfc6b4975` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PRACTICAL_OPERATOR_COMPRESSION_PROTOCOL.md` | EXISTS | ABSENT | `096df19320de` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PRACTICAL_OPERATOR_COMPRESSION_REPORT.md` | EXISTS | ABSENT | `5c6a24304bfb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PREDICTIVE_OPERATOR_PROTOCOL.md` | EXISTS | ABSENT | `13ea662fc211` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PREDICTIVE_OPERATOR_REPORT.md` | EXISTS | ABSENT | `517b5fca0a62` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PREDICTIVE_PRINCIPLE_PROTOCOL.md` | EXISTS | ABSENT | `07b3bcfdb336` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_PREDICTIVE_PRINCIPLE_REPORT.md` | EXISTS | ABSENT | `50cb983f4780` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/FUNGIBILITY_V0_5_PROTOCOL.md` | EXISTS | EXISTS | `d3a55598f439` | `f89fc3dfe39b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_5_REPORT.md` | EXISTS | EXISTS | `f6db6943c8c0` | `dfb6b067ff6a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_6_AUDIT.md` | EXISTS | EXISTS | `f32b1c7ed2c9` | `a6db51f138e3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_6_PROTOCOL.md` | EXISTS | EXISTS | `b6c232507821` | `56f17114057a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_6_REPORT.md` | EXISTS | EXISTS | `b4b1538b9ba8` | `cc1d47cdb50f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_7_PROTOCOL.md` | EXISTS | EXISTS | `96f077e4a354` | `8397ccaa7323` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_7_REPORT.md` | EXISTS | EXISTS | `3426ee2bd673` | `89de789c13e6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_8_PROTOCOL.md` | EXISTS | EXISTS | `84094cf28535` | `70d22d82887d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_8_REPORT.md` | EXISTS | EXISTS | `e903ec6597bf` | `cf61d8578b04` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_9_PROTOCOL.md` | EXISTS | EXISTS | `a2f79dd4eb0f` | `aabf34e00153` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_9_REPORT.md` | EXISTS | EXISTS | `ecbe95100a92` | `a9aba1500e02` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_PRIOR_ART.md` | EXISTS | EXISTS | `73293ed8e717` | `e48464960dcf` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_PROTOCOL.md` | EXISTS | EXISTS | `6fb5a1e7f8cd` | `bac71ac0ca25` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V0_REPORT.md` | EXISTS | EXISTS | `7dd0507669e5` | `9ba3ad9586bf` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V1_PROTOCOL.md` | EXISTS | EXISTS | `725089f22a27` | `ad63ed3d63c1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V1_REPORT.md` | EXISTS | EXISTS | `0d508d79c834` | `6686270db37a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/FUNGIBILITY_V1_SYNTHESIS_AUDIT.md` | EXISTS | EXISTS | `da36a270468c` | `b95e3e143c67` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/IMAGE_CONDITIONED_RESIDUAL_CARRIER_PROTOCOL.md` | EXISTS | ABSENT | `a54ebb0bef4d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/IMAGE_CONDITIONED_RESIDUAL_CARRIER_REPORT.md` | EXISTS | ABSENT | `cfbf2df94461` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `docs/PAPER_CLAIMS_AUDIT.md` | EXISTS | EXISTS | `bd1b00b2be0e` | `88fc7d421d99` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_DRAFT.md` | EXISTS | EXISTS | `6fb17d51f099` | `99a3d19da546` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_EVIDENCE_TABLE.md` | EXISTS | EXISTS | `4991709810fc` | `5d95c3aeb673` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_FIGURE_PLAN.md` | EXISTS | EXISTS | `404c8a1c1b16` | `5975a73dfb3d` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_FIGURE_STYLE.md` | EXISTS | EXISTS | `f6b8350191dd` | `f6b8350191dd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/PAPER_OUTLINE.md` | EXISTS | EXISTS | `6c0659768d66` | `f8d1f174b142` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_REFERENCES_DRAFT.bib` | EXISTS | EXISTS | `12aa91834845` | `84fb77c678e5` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_RELATED_WORK_POSITIONING.md` | EXISTS | EXISTS | `8912d16e9294` | `7387ac6b50c6` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `docs/PAPER_REVIEWER_AUDIT.md` | EXISTS | EXISTS | `30a0b6eec432` | `30a0b6eec432` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/PAPER_SUBMISSION_ASSETS.md` | EXISTS | EXISTS | `5b92efb587e9` | `5b92efb587e9` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/PAPER_SUPPLEMENTARY_DRAFT.md` | EXISTS | EXISTS | `b5d48352c561` | `b5d48352c561` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `docs/V0_1_AUDIT.md` | EXISTS | ABSENT | `7706508bbf1f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/V0_1_REPORT.md` | EXISTS | ABSENT | `6399b110cb26` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/V0_PROTOCOL.md` | EXISTS | ABSENT | `3083b7c37e19` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `docs/V0_REPORT.md` | EXISTS | ABSENT | `635fc058da41` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_small_patch16_224_cancellation_landscape.png` | EXISTS | ABSENT | `8072fefea8de` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_small_patch16_224_causal_intervention.png` | EXISTS | ABSENT | `d63e2fe01270` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_small_patch16_224_confound_matching.png` | EXISTS | ABSENT | `abbd9569e6ed` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_small_patch16_224_geometry_joint_distribution.png` | EXISTS | ABSENT | `0ddd3660852f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_tiny_patch16_224_cancellation_landscape.png` | EXISTS | ABSENT | `8207485bd7ac` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_tiny_patch16_224_causal_intervention.png` | EXISTS | ABSENT | `aadbd1031222` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_tiny_patch16_224_confound_matching.png` | EXISTS | ABSENT | `105b329dcc69` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/deit_tiny_patch16_224_geometry_joint_distribution.png` | EXISTS | ABSENT | `3c6682a5e746` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_small_patch16_224_oracle_margin_comparison.png` | EXISTS | ABSENT | `1fd750f49cb1` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_small_patch16_224_source_layer_histogram.png` | EXISTS | ABSENT | `65f2df533641` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_small_patch16_224_tokenwise_source_maps.png` | EXISTS | ABSENT | `0403e81c6563` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_tiny_patch16_224_oracle_margin_comparison.png` | EXISTS | ABSENT | `d95fbd2d3b99` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_tiny_patch16_224_source_layer_histogram.png` | EXISTS | ABSENT | `8c31f4a02992` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0/deit_tiny_patch16_224_tokenwise_source_maps.png` | EXISTS | ABSENT | `70a47448a135` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_small_patch16_224_historical_vs_cross_image.png` | EXISTS | ABSENT | `9d70e6f4243d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_small_patch16_224_historical_vs_random_oracle.png` | EXISTS | ABSENT | `cad340b4fc8f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_small_patch16_224_historical_vs_spatial_shuffle.png` | EXISTS | ABSENT | `32e7bc17735e` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_small_patch16_224_oracle_capacity_comparison.png` | EXISTS | ABSENT | `32cb93ec40dc` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_tiny_patch16_224_historical_vs_cross_image.png` | EXISTS | ABSENT | `864baa3f597f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_tiny_patch16_224_historical_vs_random_oracle.png` | EXISTS | ABSENT | `ed3ff3b38546` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_tiny_patch16_224_historical_vs_spatial_shuffle.png` | EXISTS | ABSENT | `5bc762069e68` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/delta_v0_5/deit_tiny_patch16_224_oracle_capacity_comparison.png` | EXISTS | ABSENT | `a54dadc0017b` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/fungibility_amortized_operator/figure_a_target_subspace_variability.png` | EXISTS | ABSENT | `533d47f36005` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_b_predicted_vs_oracle_subspace.png` | EXISTS | ABSENT | `2e02a6be3cf3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_c_oracle_recovery.png` | EXISTS | ABSENT | `c5d0e7a8b101` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_d_accuracy_token_frontier.png` | EXISTS | ABSENT | `50095acad7cf` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_e_static_vs_dynamic.png` | EXISTS | ABSENT | `26cbe42337fd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_f_rank_latency_tradeoff.png` | EXISTS | ABSENT | `7a7308964bd7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_g_accuracy_latency_frontier.png` | EXISTS | ABSENT | `3cc9f0e2d3ea` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_amortized_operator/figure_h_cross_architecture_summary.png` | EXISTS | ABSENT | `29199b45ce03` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_a_causal_path_decomposition.png` | EXISTS | ABSENT | `5cfd788cf3cb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_b_headwise_gamma_prediction.png` | EXISTS | ABSENT | `11fbbccb71b2` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_c_blockwise_propagation.png` | EXISTS | ABSENT | `32cc982df38c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_d_attention_shift.png` | EXISTS | ABSENT | `f1d54ee86b5d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_e_replication.png` | EXISTS | ABSENT | `36bc7cd756a7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_attention_causal_audit/figure_f_spatial_frequency_response.png` | EXISTS | ABSENT | `12107f3c11a6` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_a_batch_crossover.png` | EXISTS | ABSENT | `f30939e7835f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_b_throughput_vs_batch.png` | EXISTS | ABSENT | `ca0a7c991560` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_c_accuracy_throughput_frontier.png` | EXISTS | ABSENT | `f6299f86cf02` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_d_flashattention_multiplicity.png` | EXISTS | ABSENT | `fc9ae46c74fa` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_e_hybrid_grouping.png` | EXISTS | ABSENT | `ab0898088b74` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_f_depth_batch_interaction.png` | EXISTS | ABSENT | `c7bc5e4c1cef` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_g_predictor_batch_scaling.png` | EXISTS | ABSENT | `15fe31b3fcd0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_batched_operator/figure_h_cross_architecture_pareto.png` | EXISTS | ABSENT | `3086e2f1e34b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_compression_poc/accuracy_vs_latency.png` | EXISTS | EXISTS | `a932686d9d40` | `a932686d9d40` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_compression_poc/accuracy_vs_tail_tokens.png` | EXISTS | EXISTS | `57a558ec849c` | `57a558ec849c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_compression_poc/accuracy_vs_total_flops.png` | EXISTS | EXISTS | `9c09ae6833dd` | `9c09ae6833dd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_compression_poc/equivalence_error.png` | EXISTS | EXISTS | `da7a9385f4c1` | `da7a9385f4c1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_dense_fraction/dense_fraction_accuracy.png` | EXISTS | EXISTS | `04c5f51d6603` | `04c5f51d6603` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_dense_fraction/dense_fraction_margin.png` | EXISTS | EXISTS | `53fe6d97abd0` | `53fe6d97abd0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_dense_fraction/dense_fraction_recovery.png` | EXISTS | EXISTS | `6b84a8732a10` | `6b84a8732a10` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_dense_fraction/mask_seed_robustness.png` | EXISTS | EXISTS | `544793efae0a` | `544793efae0a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_dense_fraction/threshold_summary.png` | EXISTS | EXISTS | `7acfd99e66f0` | `7acfd99e66f0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_full_operator/figure_a_full_operator_spectrum.png` | EXISTS | ABSENT | `be414f54c732` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_b_top_vs_null_modes.png` | EXISTS | ABSENT | `db20f1cea109` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_c_predicted_vs_observed.png` | EXISTS | ABSENT | `84790c0e0e8b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_d_mode_factorization.png` | EXISTS | ABSENT | `be6b33913366` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_e_depth_evolution.png` | EXISTS | ABSENT | `b3758d742014` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_f_intervention_projection.png` | EXISTS | ABSENT | `f6a2876b7fd0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_g_null_mode_scaling.png` | EXISTS | ABSENT | `7bc3a58dee35` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_full_operator/figure_h_cross_architecture_replication.png` | EXISTS | ABSENT | `19276d4a14a5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_1_directional_tolerance_curves.png` | EXISTS | ABSENT | `eff0a8adf5c8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_2_fungibility_spectrum_depth.png` | EXISTS | ABSENT | `085c8c50cdf3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_3_functional_metric_eigenspectrum.png` | EXISTS | ABSENT | `e9ffb79f6314` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_4_covariance_functional_alignment.png` | EXISTS | ABSENT | `0a6b4da0ef1d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_5_intervention_projections.png` | EXISTS | ABSENT | `49c1efc9809d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_functional_geometry/figure_6_constructive_surrogate_test.png` | EXISTS | ABSENT | `adc91b67b3e0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_geometry_bank/accuracy_vs_token_budget.png` | EXISTS | EXISTS | `a3dadf90e721` | `a3dadf90e721` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_geometry_bank/delta_vs_pruning.png` | EXISTS | EXISTS | `73f12e8c499a` | `73f12e8c499a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_geometry_bank/pca_vs_kmeans.png` | EXISTS | EXISTS | `77acd38c433c` | `77acd38c433c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_joint_stream_geometry/figure_a_token_feature_heatmap.png` | EXISTS | ABSENT | `e243b50ed420` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_stream_geometry/figure_b_fraction_sweep.png` | EXISTS | ABSENT | `a2a5451e8d80` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_stream_geometry/figure_c_key_combination_curves.png` | EXISTS | ABSENT | `86547f7c57a7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_stream_geometry/figure_d_spatial_pattern_comparison.png` | EXISTS | ABSENT | `f92e5677f370` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_stream_geometry/figure_e_replication_summary.png` | EXISTS | ABSENT | `a3797e8f0ff7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_a_value_vs_key_spectrum.png` | EXISTS | ABSENT | `8785ca82112e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_b_subspace_overlap.png` | EXISTS | ABSENT | `37b068c35039` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_c_value_null_vs_joint_vk.png` | EXISTS | ABSENT | `caf2ae54ec4b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_d_finite_radius_curves.png` | EXISTS | ABSENT | `a02e17e0bf93` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_e_attention_shift.png` | EXISTS | ABSENT | `256e3e6c3768` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_f_scaling_exponents.png` | EXISTS | ABSENT | `7ecbc6316cf9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_g_blockwise_rerouting.png` | EXISTS | ABSENT | `b7304febf110` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_joint_value_key/figure_h_cross_architecture_replication.png` | EXISTS | ABSENT | `06abca77c484` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_a_single_vs_multiblock_spectrum.png` | EXISTS | ABSENT | `08c06dba8fde` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_b_single_null_vs_multi_null.png` | EXISTS | ABSENT | `b5bcbb877834` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_c_predicted_vs_observed.png` | EXISTS | ABSENT | `98ca73ba165a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_d_nullspace_rotation.png` | EXISTS | ABSENT | `591710b96b82` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_e_leakage_trace.png` | EXISTS | ABSENT | `a1f1b5c9a6ae` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_f_finite_radius_curves.png` | EXISTS | ABSENT | `e36a24983fbb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_g_depth_comparison.png` | EXISTS | ABSENT | `b3de5e9957bf` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_multiblock_operator/figure_h_cross_architecture_replication.png` | EXISTS | ABSENT | `7a453c321ce9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_a_reconstruction_objective.png` | EXISTS | ABSENT | `9153dd422529` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_b_matched_budget_accuracy.png` | EXISTS | ABSENT | `b7f85068b7af` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_c_accuracy_token_frontier.png` | EXISTS | ABSENT | `d7e3a66f8d24` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_d_operator_residual_vs_damage.png` | EXISTS | ABSENT | `64ba08034508` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_e_grouping_ablation.png` | EXISTS | ABSENT | `e897f59cb3c0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_f_operator_ablation.png` | EXISTS | ABSENT | `3c333e5b29db` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_g_low_rank_tradeoff.png` | EXISTS | ABSENT | `8378dfb94381` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression/figure_h_cross_architecture_replication.png` | EXISTS | ABSENT | `14df1358ebe8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_a_accuracy_token_frontier.png` | EXISTS | ABSENT | `2f5da6b6a6d3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_b_accuracy_retention.png` | EXISTS | ABSENT | `e2b3551f5ae4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_c_operator_vs_best_baseline.png` | EXISTS | ABSENT | `4aa79d84be7a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_d_same_group_carrier_effect.png` | EXISTS | ABSENT | `be916a253002` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_e_operator_residual_vs_damage.png` | EXISTS | ABSENT | `42b0a9275045` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_f_low_rank_ablation.png` | EXISTS | ABSENT | `d81fe56f0b27` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_g_cross_architecture_summary.png` | EXISTS | ABSENT | `a8a930554b90` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_operator_compression_confirmatory/figure_h_runtime_breakdown.png` | EXISTS | ABSENT | `9d09647d6bfb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_a_runtime_breakdown.png` | EXISTS | ABSENT | `7b2b8a3c2f53` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_b_depth_latency_lower_bound.png` | EXISTS | ABSENT | `fed112531ea4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_c_accuracy_vs_depth.png` | EXISTS | ABSENT | `9c53e571e967` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_d_operator_advantage_vs_depth.png` | EXISTS | ABSENT | `008a73eeb0f1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_e_fast_solver_tradeoff.png` | EXISTS | ABSENT | `7a53eb8e5da3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_f_accuracy_token_frontier.png` | EXISTS | ABSENT | `1c8fb087b997` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_g_accuracy_latency_frontier.png` | EXISTS | ABSENT | `a53113fcd7e8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_practical_operator_compression/figure_h_pareto_summary.png` | EXISTS | ABSENT | `f220e6fed3b7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_a_operator_spectrum.png` | EXISTS | ABSENT | `27b913a0a97e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_b_predicted_vs_observed_damage.png` | EXISTS | ABSENT | `75fc15a178e8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_c_top_vs_null_modes.png` | EXISTS | ABSENT | `95f4a801eb81` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_d_finite_radius_validation.png` | EXISTS | ABSENT | `b754e7c37589` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_e_depth_evolution.png` | EXISTS | ABSENT | `881c10bcbb14` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_f_cross_architecture_replication.png` | EXISTS | ABSENT | `3f6d921c75ac` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_operator/figure_g_token_mode_spatial_structure.png` | EXISTS | ABSENT | `13672f6f67bd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_principle/figure_a_depth_alignment.png` | EXISTS | ABSENT | `b844f100887c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_principle/figure_b_predictor_scatter.png` | EXISTS | ABSENT | `f15c3c90a498` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_principle/figure_c_loao_predicted_vs_observed.png` | EXISTS | ABSENT | `f2c2b9b38469` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_predictive_principle/figure_d_spectral_sensitivity_decomposition.png` | EXISTS | ABSENT | `7dfc82258005` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_residual_carrier/accuracy_vs_method.png` | EXISTS | ABSENT | `d93fb700bdeb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_residual_carrier/delta_accuracy_heatmap.png` | EXISTS | ABSENT | `f827e02a505e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `figures/fungibility_v0/accuracy_by_condition_depth.png` | EXISTS | EXISTS | `fe13136e92cd` | `fe13136e92cd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0/condition_difference_heatmap.png` | EXISTS | EXISTS | `0f75197ec961` | `0f75197ec961` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0/fungibility_gap_by_depth.png` | EXISTS | EXISTS | `605fffba46eb` | `605fffba46eb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0/margin_damage_by_condition.png` | EXISTS | EXISTS | `17e5ee7079f1` | `17e5ee7079f1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0/replacement_norm_distribution.png` | EXISTS | EXISTS | `a1cf1f4f27cc` | `a1cf1f4f27cc` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_5/condition_accuracy.png` | EXISTS | EXISTS | `c942621aec20` | `c942621aec20` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_5/condition_margin_damage.png` | EXISTS | EXISTS | `d06d70ac1c69` | `d06d70ac1c69` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_5/distribution_distance_vs_damage.png` | EXISTS | EXISTS | `ff1f298ce289` | `ff1f298ce289` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_5/norm_vs_performance.png` | EXISTS | EXISTS | `e19ca8752f76` | `e19ca8752f76` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/accuracy_by_depth_fraction.png` | EXISTS | EXISTS | `fb439f10c095` | `fb439f10c095` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/correct_vs_wrong_depth_gaussian.png` | EXISTS | EXISTS | `eb6ea4d9f4d4` | `eb6ea4d9f4d4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/damage_by_depth_fraction.png` | EXISTS | EXISTS | `7ef9774a5536` | `7ef9774a5536` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/depth_transition_heatmap.png` | EXISTS | EXISTS | `523c4f767103` | `523c4f767103` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/gaussian_recovery_by_depth.png` | EXISTS | EXISTS | `fc57a37bbbf7` | `fc57a37bbbf7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/gaussian_vs_random_sphere.png` | EXISTS | EXISTS | `48cc8cfaf0cc` | `48cc8cfaf0cc` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_6/global_mean_vs_gaussian.png` | EXISTS | EXISTS | `7a7a37ac4e11` | `7a7a37ac4e11` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/cls_vs_patch_replacement.png` | EXISTS | EXISTS | `81abc2f55abb` | `81abc2f55abb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/full_patch_replacement.png` | EXISTS | EXISTS | `5f8c2075b914` | `5f8c2075b914` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/prototype_cosine_sweep.png` | EXISTS | EXISTS | `eeeeb9fd89db` | `eeeeb9fd89db` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/prototype_performance_by_fraction.png` | EXISTS | EXISTS | `cde7a5621a34` | `cde7a5621a34` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/prototype_scale_sweep.png` | EXISTS | EXISTS | `51b90378c9bd` | `51b90378c9bd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/prototype_sign_flip_sweep.png` | EXISTS | EXISTS | `e67375f98d28` | `e67375f98d28` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_7/wrong_depth_mean_comparison.png` | EXISTS | EXISTS | `fc6a397f9b4a` | `fc6a397f9b4a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/accuracy_vs_designed_rank.png` | EXISTS | EXISTS | `984678d61155` | `984678d61155` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/accuracy_vs_unique_token_count.png` | EXISTS | EXISTS | `442a186ec975` | `442a186ec975` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/attention_rank_through_blocks.png` | EXISTS | EXISTS | `c63907ad0471` | `c63907ad0471` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/effective_rank_through_blocks.png` | EXISTS | EXISTS | `68229e4cbf8f` | `68229e4cbf8f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/margin_vs_effective_rank.png` | EXISTS | EXISTS | `e51d9b66c1b1` | `e51d9b66c1b1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/pca_vs_random_subspace.png` | EXISTS | EXISTS | `851cbdab5d07` | `851cbdab5d07` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_8/shared_vs_independent_noise.png` | EXISTS | EXISTS | `f76a0664fa0f` | `f76a0664fa0f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/accuracy_vs_natural_rank.png` | EXISTS | EXISTS | `0d57fa163db0` | `0d57fa163db0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/attention_recovery_through_blocks.png` | EXISTS | EXISTS | `9bdfe73db25b` | `9bdfe73db25b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/eigenvalue_spectrum.png` | EXISTS | EXISTS | `bc319db3f044` | `bc319db3f044` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/natural_vs_energy_matched_rank.png` | EXISTS | EXISTS | `b530041f954c` | `b530041f954c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/pc1_amplitude_sweep.png` | EXISTS | EXISTS | `98f32dc81a4f` | `98f32dc81a4f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/pc_identity_comparison.png` | EXISTS | EXISTS | `e76e0ffae33c` | `e76e0ffae33c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v0_9/rank_expansion_through_blocks.png` | EXISTS | EXISTS | `df310770d806` | `df310770d806` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/content_fungibility_across_models.png` | EXISTS | EXISTS | `0fe8145d2a27` | `0fe8145d2a27` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/depth_generalization.png` | EXISTS | EXISTS | `ac421ccb6561` | `ac421ccb6561` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/geometry_controls_across_models.png` | EXISTS | EXISTS | `2637abda21b1` | `2637abda21b1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/learned_vs_random_1d.png` | EXISTS | EXISTS | `4370e3be965e` | `4370e3be965e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/replacement_fraction_generalization.png` | EXISTS | EXISTS | `2eb422fd3ca4` | `2eb422fd3ca4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/fungibility_v1/shared_vs_independent_across_models.png` | EXISTS | EXISTS | `ba304d8fde58` | `ba304d8fde58` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig01_conceptual_overview.pdf` | EXISTS | EXISTS | `453ed43a87a6` | `453ed43a87a6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig01_conceptual_overview.png` | EXISTS | EXISTS | `a3c2cc0a00be` | `a3c2cc0a00be` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig02_depth_emergence.pdf` | EXISTS | EXISTS | `b88b4515fa65` | `b88b4515fa65` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig02_depth_emergence.png` | EXISTS | EXISTS | `2c16821700bd` | `2c16821700bd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig03_dense_fraction.pdf` | EXISTS | EXISTS | `ebcb86f26101` | `ebcb86f26101` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig03_dense_fraction.png` | EXISTS | EXISTS | `09482b6c73be` | `09482b6c73be` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig04_geometry_constraint.pdf` | EXISTS | EXISTS | `39202c195672` | `39202c195672` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig04_geometry_constraint.png` | EXISTS | EXISTS | `2e3a7b3744bf` | `2e3a7b3744bf` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig05_diversity_constraint.pdf` | EXISTS | EXISTS | `029803764648` | `029803764648` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig05_diversity_constraint.png` | EXISTS | EXISTS | `755ae660a5b4` | `755ae660a5b4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig06_lowdim_direction.pdf` | EXISTS | EXISTS | `71f0eabc8f28` | `71f0eabc8f28` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/main/fig06_lowdim_direction.png` | EXISTS | EXISTS | `77e3830be397` | `77e3830be397` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS01_mask_robustness.pdf` | EXISTS | EXISTS | `84e83bcc3b91` | `84e83bcc3b91` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS01_mask_robustness.png` | EXISTS | EXISTS | `53cc01c52997` | `53cc01c52997` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS02_retention_thresholds.pdf` | EXISTS | EXISTS | `6f165155d051` | `6f165155d051` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS02_retention_thresholds.png` | EXISTS | EXISTS | `1aa4e4e0a677` | `1aa4e4e0a677` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS03_pca_rank.pdf` | EXISTS | EXISTS | `20a69378398f` | `20a69378398f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS03_pca_rank.png` | EXISTS | EXISTS | `6696e6b294aa` | `6696e6b294aa` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS04_pc1_amplitude.pdf` | EXISTS | EXISTS | `42489f591ad6` | `42489f591ad6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS04_pc1_amplitude.png` | EXISTS | EXISTS | `ce4fdadcee14` | `ce4fdadcee14` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS05_rank_propagation.pdf` | EXISTS | EXISTS | `86dceb18fecd` | `86dceb18fecd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS05_rank_propagation.png` | EXISTS | EXISTS | `4b8df04861ad` | `4b8df04861ad` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS06_carrier_equivalence.pdf` | EXISTS | EXISTS | `b5fd023a8575` | `b5fd023a8575` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS06_carrier_equivalence.png` | EXISTS | EXISTS | `4642d6fd39d6` | `4642d6fd39d6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS07_accuracy_vs_tokens.pdf` | EXISTS | EXISTS | `03cfb8e25e65` | `03cfb8e25e65` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS07_accuracy_vs_tokens.png` | EXISTS | EXISTS | `25fc7e8702b5` | `25fc7e8702b5` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS08_accuracy_vs_latency.pdf` | EXISTS | EXISTS | `9743e2c2a83b` | `9743e2c2a83b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS08_accuracy_vs_latency.png` | EXISTS | EXISTS | `7ebd57e2df4d` | `7ebd57e2df4d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS09_geometry_bank_vs_pruning.pdf` | EXISTS | EXISTS | `a7b649adde5d` | `a7b649adde5d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/paper_final/supp/figS09_geometry_bank_vs_pruning.png` | EXISTS | EXISTS | `8af9db5e68f2` | `8af9db5e68f2` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `figures/v0_1/deit_small_patch16_224_cancellation_landscape.png` | EXISTS | ABSENT | `a78efdecf3ec` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_small_patch16_224_causal_intervention.png` | EXISTS | ABSENT | `81b7e8310a3a` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_small_patch16_224_confound_matching.png` | EXISTS | ABSENT | `47687455820a` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_small_patch16_224_geometry_joint_distribution.png` | EXISTS | ABSENT | `0ddd3660852f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_small_patch16_224_patch_causal_intervention.png` | EXISTS | ABSENT | `c40ef48c5ae8` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_tiny_patch16_224_cancellation_landscape.png` | EXISTS | ABSENT | `f0bcb92500ec` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_tiny_patch16_224_causal_intervention.png` | EXISTS | ABSENT | `ec98a4e1833c` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_tiny_patch16_224_confound_matching.png` | EXISTS | ABSENT | `027085e2731e` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_tiny_patch16_224_geometry_joint_distribution.png` | EXISTS | ABSENT | `3c6682a5e746` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `figures/v0_1/deit_tiny_patch16_224_patch_causal_intervention.png` | EXISTS | ABSENT | `eaa380f216d7` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_small_patch16_224_image_predictions.csv` | EXISTS | ABSENT | `84b409e6b4dc` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_small_patch16_224_intervention_sweep.csv` | EXISTS | ABSENT | `b14656781e25` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_small_patch16_224_matched_controls.csv` | EXISTS | ABSENT | `7e77460cad6c` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_small_patch16_224_residual_events.csv` | EXISTS | ABSENT | `1110c6169380` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_tiny_patch16_224_image_predictions.csv` | EXISTS | ABSENT | `ac3cff26efea` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_tiny_patch16_224_intervention_sweep.csv` | EXISTS | ABSENT | `3bd2550988da` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_tiny_patch16_224_matched_controls.csv` | EXISTS | ABSENT | `e5a366198345` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/deit_tiny_patch16_224_residual_events.csv` | EXISTS | ABSENT | `edaa1e9acf20` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_small_patch16_224_image_results.csv` | EXISTS | ABSENT | `9770dca77b1f` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_small_patch16_224_policy_comparison.csv` | EXISTS | ABSENT | `249ccefdbbb9` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_small_patch16_224_source_selection.csv` | EXISTS | ABSENT | `f92f2a7a9f08` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_tiny_patch16_224_image_results.csv` | EXISTS | ABSENT | `9034841f6651` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_tiny_patch16_224_policy_comparison.csv` | EXISTS | ABSENT | `46230f58ce0e` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/deit_tiny_patch16_224_source_selection.csv` | EXISTS | ABSENT | `2d3012d3bb49` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0/experiment_manifest.json` | EXISTS | ABSENT | `57fcda3618cb` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_small_patch16_224_image_results.csv` | EXISTS | ABSENT | `79340b1d742b` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_small_patch16_224_matched_oracle_comparison.csv` | EXISTS | ABSENT | `2ba82c57fc4b` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_small_patch16_224_seed_results.csv` | EXISTS | ABSENT | `38242ebc6014` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_small_patch16_224_selection_diversity.csv` | EXISTS | ABSENT | `857fdc655138` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_tiny_patch16_224_image_results.csv` | EXISTS | ABSENT | `7aead0f87914` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_tiny_patch16_224_matched_oracle_comparison.csv` | EXISTS | ABSENT | `deff98d302cb` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_tiny_patch16_224_seed_results.csv` | EXISTS | ABSENT | `5921e3546334` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/deit_tiny_patch16_224_selection_diversity.csv` | EXISTS | ABSENT | `4267f0d52157` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/delta_v0_5/experiment_manifest.json` | EXISTS | ABSENT | `eef312068126` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/experiment_manifest.json` | EXISTS | ABSENT | `511eeb4a3ee3` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/fungibility_amortized_operator/budget_results.csv` | EXISTS | ABSENT | `ddf756568936` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/direct_carrier_baseline.csv` | EXISTS | ABSENT | `7c89100afc55` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/mode_error_tolerance.csv` | EXISTS | ABSENT | `40e285f252ed` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/mode_separability.csv` | EXISTS | ABSENT | `fa0464de0cd1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/oracle_recovery.csv` | EXISTS | ABSENT | `b8effb211b97` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/principal_angles.csv` | EXISTS | ABSENT | `06de4f5a5d62` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/rank_ablation.csv` | EXISTS | ABSENT | `28d301bbcfaa` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/replication_summary.csv` | EXISTS | ABSENT | `1fb3868711ed` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/runtime_breakdown.csv` | EXISTS | ABSENT | `a418071076f0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/static_vs_dynamic.csv` | EXISTS | ABSENT | `46e72fa9073e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/subspace_prediction.csv` | EXISTS | ABSENT | `142fe81358b4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/target_statistics.csv` | EXISTS | ABSENT | `f886d36be2f9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator/validation_manifest.json` | EXISTS | ABSENT | `fcf97f14995d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/clean_flip_analysis.csv` | EXISTS | ABSENT | `e93de7388bd9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/dataset_alignment_audit.csv` | EXISTS | ABSENT | `6486ef2d3917` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/oracle_recovery_audit.csv` | EXISTS | ABSENT | `0a31c907b6c4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/overlap_vs_compression.csv` | EXISTS | ABSENT | `2257fd802842` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/recomputed_accuracy.csv` | EXISTS | ABSENT | `3eb722a6b281` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/runtime_audit.csv` | EXISTS | ABSENT | `abd02bd4809e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_amortized_operator_audit/validation_manifest.json` | EXISTS | ABSENT | `e373ff94ed02` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/attention_shift.csv` | EXISTS | ABSENT | `1d899318ab97` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/blockwise_propagation.csv` | EXISTS | ABSENT | `2a421ef7b88d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/causal_conditions.csv` | EXISTS | ABSENT | `14d8c93922bc` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/headwise_gamma.csv` | EXISTS | ABSENT | `782111b15400` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/headwise_prediction.csv` | EXISTS | ABSENT | `b5f7175a6148` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/qkv_decomposition.csv` | EXISTS | ABSENT | `2e1591d2bf90` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/replication_summary.csv` | EXISTS | ABSENT | `158259267d29` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/residual_path.csv` | EXISTS | ABSENT | `0b487824d751` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_attention_causal_audit/validation_manifest.json` | EXISTS | ABSENT | `793d76936fbd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/batch_crossover.csv` | EXISTS | ABSENT | `0d7ba95fdf8c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/batch_runtime_breakdown.csv` | EXISTS | ABSENT | `d8bcbfc042ae` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/batch_throughput.csv` | EXISTS | ABSENT | `0d55cdd76fd1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/depth_batch_ablation.csv` | EXISTS | ABSENT | `5a8f38605618` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/hybrid_grouping_results.csv` | EXISTS | ABSENT | `19ca8bf340dd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/matched_budget_results.csv` | EXISTS | ABSENT | `45b2f6f3c30b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/multiplicity_kernel_audit.csv` | EXISTS | ABSENT | `90c86a4a7565` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/pareto_frontier.csv` | EXISTS | ABSENT | `4acd36f2c912` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/predictor_batch_ablation.csv` | EXISTS | ABSENT | `c71296d496aa` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/solver_batch_ablation.csv` | EXISTS | ABSENT | `5168b61209b4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/throughput_frontier.csv` | EXISTS | ABSENT | `4eec55358ddd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_batched_operator/validation_manifest.json` | EXISTS | ABSENT | `52e58863c51e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_compression_poc/baseline_comparison.csv` | EXISTS | EXISTS | `ab771b24bf2f` | `ab771b24bf2f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/compute_summary.csv` | EXISTS | EXISTS | `e33353bc4d4d` | `e33353bc4d4d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/equivalence_results.csv` | EXISTS | EXISTS | `0f69c6343a00` | `0f69c6343a00` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/experiment_manifest.json` | EXISTS | EXISTS | `3ff30a8ea405` | `3ff30a8ea405` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/full_eval_results.csv` | EXISTS | EXISTS | `5ea154f8744b` | `5ea154f8744b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/latency_summary.csv` | EXISTS | EXISTS | `c95810fbc69f` | `c95810fbc69f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_compression_poc/validation_results.json` | EXISTS | EXISTS | `a5f25cb8cc20` | `a5f25cb8cc20` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/all_results.parquet` | EXISTS | EXISTS | `ed8cf42e8326` | `ed8cf42e8326` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/auc_summary.csv` | EXISTS | EXISTS | `2b777455a557` | `2b777455a557` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/cliff_summary.csv` | EXISTS | EXISTS | `bad1a4cb57c7` | `bad1a4cb57c7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/experiment_manifest.json` | EXISTS | EXISTS | `eef14dc7e955` | `eef14dc7e955` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/fraction_grid.json` | EXISTS | EXISTS | `29355df45024` | `29355df45024` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/mask_permutations.json` | EXISTS | EXISTS | `74225b52bc19` | `74225b52bc19` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/summary_across_masks.csv` | EXISTS | EXISTS | `71998fc6ffeb` | `71998fc6ffeb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/summary_by_mask_seed.csv` | EXISTS | EXISTS | `d68416242362` | `d68416242362` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/threshold_crossings.csv` | EXISTS | EXISTS | `aa1daf074423` | `aa1daf074423` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_dense_fraction/validation_results.json` | EXISTS | EXISTS | `8473f5b12eb5` | `8473f5b12eb5` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_full_operator/depth_evolution.csv` | EXISTS | ABSENT | `567cc6fd142a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/finite_radius_curves.csv` | EXISTS | ABSENT | `f4b7931bcfa1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/intervention_projection.csv` | EXISTS | ABSENT | `178c91973799` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/mode_factorization.csv` | EXISTS | ABSENT | `4c765e76661f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/null_scaling.csv` | EXISTS | ABSENT | `54acf5dec840` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/operator_spectrum.csv` | EXISTS | ABSENT | `bfc56f639e70` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/random_perturbation_prediction.csv` | EXISTS | ABSENT | `b96e2bfcab68` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/replication_summary.csv` | EXISTS | ABSENT | `855db0a206b0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/residual_damage.csv` | EXISTS | ABSENT | `52cdea2ebc61` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/singular_mode_validation.csv` | EXISTS | ABSENT | `c2da52d787c9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_full_operator/validation_manifest.json` | EXISTS | ABSENT | `419d842655be` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/constructive_surrogates.csv` | EXISTS | ABSENT | `38ae4312866c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/covariance_function_alignment.csv` | EXISTS | ABSENT | `3358a94c9382` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/directional_tolerance.csv` | EXISTS | ABSENT | `1ec3b3255912` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/functional_spectrum.csv` | EXISTS | ABSENT | `440fe6d94a11` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/fungible_dimension.csv` | EXISTS | ABSENT | `14c96fb1b7d5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/imagewise_consistency.csv` | EXISTS | ABSENT | `988080afe1b2` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/intervention_projection.csv` | EXISTS | ABSENT | `b97e7f8ffae3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_functional_geometry/validation_manifest.json` | EXISTS | ABSENT | `c98b1df7dbaa` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_geometry_bank/all_results.csv` | EXISTS | EXISTS | `b9383077fd33` | `b9383077fd33` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_geometry_bank/delta_vs_pruning.csv` | EXISTS | EXISTS | `c2d936e0dead` | `c2d936e0dead` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_geometry_bank/experiment_manifest.json` | EXISTS | EXISTS | `7fae234b646a` | `7fae234b646a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_geometry_bank/matched_budget_summary.csv` | EXISTS | EXISTS | `d3f209718e5d` | `d3f209718e5d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_geometry_bank/validation_results.json` | EXISTS | EXISTS | `e8550638f467` | `e8550638f467` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_joint_stream_geometry/condition_results.csv` | EXISTS | ABSENT | `c744a54c56c2` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_stream_geometry/directional_curves.csv` | EXISTS | ABSENT | `4deef5bd3007` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_stream_geometry/fraction_sweep.csv` | EXISTS | ABSENT | `31d01c07a2e9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_stream_geometry/replication_summary.csv` | EXISTS | ABSENT | `d88431000bcd` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_stream_geometry/token_feature_interaction.csv` | EXISTS | ABSENT | `f86144e84098` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_stream_geometry/validation_manifest.json` | EXISTS | ABSENT | `491e5a8323ad` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/attention_shift.csv` | EXISTS | ABSENT | `3498975b975c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/blockwise_rerouting.csv` | EXISTS | ABSENT | `6b31c3b69e7e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/depth_comparison.csv` | EXISTS | ABSENT | `57c10c69d06d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/finite_radius_curves.csv` | EXISTS | ABSENT | `c7c0ace5e817` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/joint_operator_spectrum.csv` | EXISTS | ABSENT | `e0eeaf0600ff` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/key_operator_spectrum.csv` | EXISTS | ABSENT | `a7b84dd72b6a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/random_prediction.csv` | EXISTS | ABSENT | `b13a3c5815b8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/replication_summary.csv` | EXISTS | ABSENT | `3d873716ace4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/scaling_exponents.csv` | EXISTS | ABSENT | `1a369746e891` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/validation_manifest.json` | EXISTS | ABSENT | `09dc6460bdc1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/value_operator_spectrum.csv` | EXISTS | ABSENT | `a58950ab2189` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_joint_value_key/vk_subspace_overlap.csv` | EXISTS | ABSENT | `47d1d9ec4387` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/depth_comparison.csv` | EXISTS | ABSENT | `7775c06a991d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/finite_radius_curves.csv` | EXISTS | ABSENT | `a26d1af87489` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/historical_intervention_projection.csv` | EXISTS | ABSENT | `de4026b6252e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/leakage_trace.csv` | EXISTS | ABSENT | `578ceb33c75f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/multiblock_spectrum.csv` | EXISTS | ABSENT | `ef8913466799` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/nullspace_rotation.csv` | EXISTS | ABSENT | `2990514c2b4d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/random_prediction.csv` | EXISTS | ABSENT | `ceceb7fefbdf` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/replication_summary.csv` | EXISTS | ABSENT | `691c1e8b61c7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/scaling_exponents.csv` | EXISTS | ABSENT | `5138c5a99304` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/single_vs_multi_null.csv` | EXISTS | ABSENT | `a2146ff8d33c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_multiblock_operator/validation_manifest.json` | EXISTS | ABSENT | `fc2d67dbb454` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/budget_frontier.csv` | EXISTS | ABSENT | `8234d7cd8c64` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/calibration_operator_results.csv` | EXISTS | ABSENT | `4ab644ef412a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/collapse_parity.csv` | EXISTS | ABSENT | `177bba6724f1` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/full_length_surrogate_results.csv` | EXISTS | ABSENT | `eaafb0257afb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/grouping_ablation.csv` | EXISTS | ABSENT | `df63d2fd5126` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/low_rank_ablation.csv` | EXISTS | ABSENT | `df5952ed766a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/matched_budget_results.csv` | EXISTS | ABSENT | `500b8193307e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/operator_ablation.csv` | EXISTS | ABSENT | `7b4aa92eb629` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/reconstruction_objectives.csv` | EXISTS | ABSENT | `8c4f75aab64b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/replication_summary.csv` | EXISTS | ABSENT | `fcaad0ce36e2` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/residual_vs_damage.csv` | EXISTS | ABSENT | `b1fa394b9302` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression/validation_manifest.json` | EXISTS | ABSENT | `0dce8142e55a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/architecture_summary.csv` | EXISTS | ABSENT | `a48a8e1be43b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/baseline_comparison.csv` | EXISTS | ABSENT | `57201c8660cf` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/budget_summary.csv` | EXISTS | ABSENT | `0d08b7c2e9d7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/collapse_parity.csv` | EXISTS | ABSENT | `5eb43f71f470` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv` | EXISTS | ABSENT | `500e6a92b1f6` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/operator_residual_analysis.csv` | EXISTS | ABSENT | `92e1375599ad` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/paired_statistics.csv` | EXISTS | ABSENT | `9b653fcf74f9` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/per_image_results.csv` | EXISTS | ABSENT | `c5df9974277b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/runtime_breakdown.csv` | EXISTS | ABSENT | `b2293b284b24` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/same_group_ablation.csv` | EXISTS | ABSENT | `7c0011debc87` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/seed_summary.csv` | EXISTS | ABSENT | `461708792643` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_operator_compression_confirmatory/validation_manifest.json` | EXISTS | ABSENT | `7709588de1f8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/accuracy_latency_frontier.csv` | EXISTS | ABSENT | `c8a2d264768f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/depth_latency_lower_bound.csv` | EXISTS | ABSENT | `8b791c48adf3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/depth_sweep.csv` | EXISTS | ABSENT | `2ac1e24a4287` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/detailed_solver_profile.csv` | EXISTS | ABSENT | `b31a1a77f711` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/fast_solver_ablation.csv` | EXISTS | ABSENT | `f87cb59af24f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/grouping_profile.csv` | EXISTS | ABSENT | `cfb6b996011b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/latency_results.csv` | EXISTS | ABSENT | `45dd28711c80` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/matched_budget_results.csv` | EXISTS | ABSENT | `2e270f60846e` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/pareto_frontier.csv` | EXISTS | ABSENT | `71cae2ad47cc` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/predictor_depth_ablation.csv` | EXISTS | ABSENT | `2f291911c250` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_practical_operator_compression/validation_manifest.json` | EXISTS | ABSENT | `d858b0bd2527` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/depth_spectrum.csv` | EXISTS | ABSENT | `ec43dfb47246` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/feature_token_matrix.csv` | EXISTS | ABSENT | `27c3398b1087` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/finite_radius_curves.csv` | EXISTS | ABSENT | `ca67a6f76718` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/operator_spectrum.csv` | EXISTS | ABSENT | `4512a6fac99d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/random_pattern_prediction.csv` | EXISTS | ABSENT | `c1f708ba7b72` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/replication_summary.csv` | EXISTS | ABSENT | `a02fded86eb5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/singular_mode_validation.csv` | EXISTS | ABSENT | `8eb68afea29c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/spatial_mode_analysis.csv` | EXISTS | ABSENT | `abe5e2019cf2` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_operator/validation_manifest.json` | EXISTS | ABSENT | `2c69664b7bd0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_principle/layer_metrics.csv` | EXISTS | ABSENT | `8a54a6e5df88` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_principle/leave_one_architecture_out.csv` | EXISTS | ABSENT | `8c34a9311c58` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_principle/predictor_vs_fungibility.csv` | EXISTS | ABSENT | `d3b6c8912720` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_principle/transition_predictions.csv` | EXISTS | ABSENT | `0a29a538d7a8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_predictive_principle/validation_manifest.json` | EXISTS | ABSENT | `21363a2973fb` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_residual_carrier/heatmap_grid.csv` | EXISTS | ABSENT | `21ecc7c72aa5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_residual_carrier/summary_by_condition.csv` | EXISTS | ABSENT | `eb07adb3099a` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_residual_carrier/trial_results.csv` | EXISTS | ABSENT | `87e514b68c80` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_residual_carrier/validation_manifest.json` | EXISTS | ABSENT | `bba8c39b82a3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `outputs/fungibility_v0/decision_summary.json` | EXISTS | EXISTS | `e966e1fca4b9` | `e966e1fca4b9` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0/image_records_small.parquet` | EXISTS | EXISTS | `a75512d68b10` | `a75512d68b10` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0/image_records_tiny.parquet` | EXISTS | EXISTS | `efde6be619a4` | `efde6be619a4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0/results_manifest.json` | EXISTS | EXISTS | `493b628096d2` | `493b628096d2` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/experiment_manifest.json` | EXISTS | EXISTS | `a9ec1f4b7c28` | `a9ec1f4b7c28` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/small_activation_diagnostics.csv` | EXISTS | EXISTS | `a20f13b90c42` | `a20f13b90c42` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/small_condition_comparison.csv` | EXISTS | EXISTS | `e612cbffbdab` | `e612cbffbdab` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/small_image_results.parquet` | EXISTS | EXISTS | `896a5d03a019` | `896a5d03a019` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/small_seed_results.csv` | EXISTS | EXISTS | `cd09e06bd760` | `cd09e06bd760` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/tiny_activation_diagnostics.csv` | EXISTS | EXISTS | `0da5dac36134` | `0da5dac36134` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/tiny_condition_comparison.csv` | EXISTS | EXISTS | `705bb6be4d30` | `705bb6be4d30` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/tiny_image_results.parquet` | EXISTS | EXISTS | `4b6ec6a1e809` | `4b6ec6a1e809` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_5/tiny_seed_results.csv` | EXISTS | EXISTS | `64ccb07bfd12` | `64ccb07bfd12` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/calibration_split.csv` | EXISTS | EXISTS | `32df41c745ed` | `32df41c745ed` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/calibration_statistics.npz` | EXISTS | EXISTS | `3f39e33c53af` | `3f39e33c53af` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/evaluation_split.csv` | EXISTS | EXISTS | `829cb109c008` | `829cb109c008` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/experiment_manifest.json` | EXISTS | EXISTS | `06f4fbe0624f` | `06f4fbe0624f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/small_condition_comparisons.csv` | EXISTS | EXISTS | `8182c56227cb` | `8182c56227cb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/small_depth_fraction_summary.csv` | EXISTS | EXISTS | `52ab7c3775b4` | `52ab7c3775b4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/small_seed_results.csv` | EXISTS | EXISTS | `15de74d7333c` | `15de74d7333c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/summary_all_models.csv` | EXISTS | EXISTS | `01e22532c725` | `01e22532c725` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/tiny_condition_comparisons.csv` | EXISTS | EXISTS | `6b2ec8cbf9ea` | `6b2ec8cbf9ea` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/tiny_depth_fraction_summary.csv` | EXISTS | EXISTS | `de7cd386fa24` | `de7cd386fa24` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_6/tiny_seed_results.csv` | EXISTS | EXISTS | `8d305884cf06` | `8d305884cf06` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/experiment_manifest.json` | EXISTS | EXISTS | `5a0e74436093` | `5a0e74436093` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/prototype_vectors.npz` | EXISTS | EXISTS | `fa47ddf8d883` | `fa47ddf8d883` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/prototype_vectors_metadata.csv` | EXISTS | EXISTS | `e984bcf962be` | `e984bcf962be` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_cls_comparison.csv` | EXISTS | EXISTS | `1c99c6413f85` | `1c99c6413f85` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_cosine_sweep.csv` | EXISTS | EXISTS | `1871157cdd72` | `1871157cdd72` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_fraction_summary.csv` | EXISTS | EXISTS | `3f81cc2133a5` | `3f81cc2133a5` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_image_results.parquet` | EXISTS | EXISTS | `1ce3e7f9113d` | `1ce3e7f9113d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_prototype_comparison.csv` | EXISTS | EXISTS | `1bbca4783d7b` | `1bbca4783d7b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_scale_sweep.csv` | EXISTS | EXISTS | `faabb1f01070` | `faabb1f01070` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/small_sign_flip_sweep.csv` | EXISTS | EXISTS | `acfe5ab38996` | `acfe5ab38996` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_cls_comparison.csv` | EXISTS | EXISTS | `831096da9e90` | `831096da9e90` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_cosine_sweep.csv` | EXISTS | EXISTS | `7c76b031a3e1` | `7c76b031a3e1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_fraction_summary.csv` | EXISTS | EXISTS | `106ec1cc32e4` | `106ec1cc32e4` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_image_results.parquet` | EXISTS | EXISTS | `c97b85d2519d` | `c97b85d2519d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_prototype_comparison.csv` | EXISTS | EXISTS | `2c30bcd373e7` | `2c30bcd373e7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_scale_sweep.csv` | EXISTS | EXISTS | `0e70c3c6d4ae` | `0e70c3c6d4ae` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_7/tiny_sign_flip_sweep.csv` | EXISTS | EXISTS | `92053d5ea662` | `92053d5ea662` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/attention_rank_diagnostics.csv` | EXISTS | EXISTS | `4726fea556e6` | `4726fea556e6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/decision_summary.json` | EXISTS | EXISTS | `8fe9c01bec3d` | `8fe9c01bec3d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/energy_verification.csv` | EXISTS | EXISTS | `8f810b90e338` | `8f810b90e338` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/experiment_manifest.json` | EXISTS | EXISTS | `50d6a5b7dbf7` | `50d6a5b7dbf7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/grouped_diversity_results.csv` | EXISTS | EXISTS | `0c914a74ee51` | `0c914a74ee51` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/pca_basis_metadata.json` | EXISTS | EXISTS | `52f1b2380a72` | `52f1b2380a72` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/rank_condition_results.csv` | EXISTS | EXISTS | `600c9cdb1215` | `600c9cdb1215` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/representation_rank_diagnostics.csv` | EXISTS | EXISTS | `06d4c2aa0d74` | `06d4c2aa0d74` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/secondary_75_results.csv` | EXISTS | EXISTS | `8cfe03c8fe15` | `8cfe03c8fe15` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/shared_vs_independent_results.csv` | EXISTS | EXISTS | `1275ffda411f` | `1275ffda411f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/small_image_results.parquet` | EXISTS | EXISTS | `ad801c201334` | `ad801c201334` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/statistical_comparisons.csv` | EXISTS | EXISTS | `647868d92918` | `647868d92918` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_8/tiny_image_results.parquet` | EXISTS | EXISTS | `3d5e10c1ac3b` | `3d5e10c1ac3b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/attention_diagnostics.csv` | EXISTS | EXISTS | `3314e47b0f35` | `3314e47b0f35` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/decision_summary.json` | EXISTS | EXISTS | `bc9f9e1e3610` | `bc9f9e1e3610` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/eigenvalue_spectrum.csv` | EXISTS | EXISTS | `36a612b11409` | `36a612b11409` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/experiment_manifest.json` | EXISTS | EXISTS | `aa2baf956f9c` | `aa2baf956f9c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/natural_vs_energy_matched_rank.csv` | EXISTS | EXISTS | `7fbff8cd999a` | `7fbff8cd999a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/pc1_scale_sweep.csv` | EXISTS | EXISTS | `ec514a226465` | `ec514a226465` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/pc_identity_results.csv` | EXISTS | EXISTS | `333e7f466de2` | `333e7f466de2` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/pca_cache_deit_small_patch16_224.npz` | EXISTS | EXISTS | `73efdd6780f0` | `73efdd6780f0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/pca_cache_deit_tiny_patch16_224.npz` | EXISTS | EXISTS | `49f57734af25` | `49f57734af25` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/random_direction_results.csv` | EXISTS | EXISTS | `4e10fab23499` | `4e10fab23499` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/rank_propagation.csv` | EXISTS | EXISTS | `732fee40528a` | `732fee40528a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/small_image_results.parquet` | EXISTS | EXISTS | `105a97338b32` | `105a97338b32` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v0_9/tiny_image_results.parquet` | EXISTS | EXISTS | `2ccb5f22c73e` | `2ccb5f22c73e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/calibration_statistics.npz` | EXISTS | EXISTS | `43e817b90cdf` | `43e817b90cdf` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/decision_summary.json` | EXISTS | EXISTS | `93660385b760` | `93660385b760` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_1d_results.csv` | EXISTS | EXISTS | `1736700e3768` | `1736700e3768` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_depth_results.csv` | EXISTS | EXISTS | `e0d0e0a3f19a` | `e0d0e0a3f19a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_diversity_results.csv` | EXISTS | EXISTS | `44c2a00272ed` | `44c2a00272ed` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_fraction_results.csv` | EXISTS | EXISTS | `4595c0e9d7f9` | `4595c0e9d7f9` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_geometry_results.csv` | EXISTS | EXISTS | `6a6b0be5c3a0` | `6a6b0be5c3a0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/dinov2_image_results.parquet` | EXISTS | EXISTS | `aefb80fe47a3` | `aefb80fe47a3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/experiment_manifest.json` | EXISTS | EXISTS | `c12535a868c5` | `c12535a868c5` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/manual_forward_validation.json` | EXISTS | EXISTS | `7c40fccfc04a` | `7c40fccfc04a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/model_metadata.json` | EXISTS | EXISTS | `d5025f2e95c3` | `d5025f2e95c3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/validation_results.json` | EXISTS | EXISTS | `46a9b7090114` | `46a9b7090114` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_1d_results.csv` | EXISTS | EXISTS | `3775b3ec78d5` | `3775b3ec78d5` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_depth_results.csv` | EXISTS | EXISTS | `9c3b0be0c2a3` | `9c3b0be0c2a3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_diversity_results.csv` | EXISTS | EXISTS | `6501cc0286e0` | `6501cc0286e0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_fraction_results.csv` | EXISTS | EXISTS | `03de1113cb10` | `03de1113cb10` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_geometry_results.csv` | EXISTS | EXISTS | `bba9f3fcc682` | `bba9f3fcc682` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/fungibility_v1/vitb_image_results.parquet` | EXISTS | EXISTS | `8ebbb18720c9` | `8ebbb18720c9` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `outputs/v0_1/deit_small_patch16_224_cls_intervention_sweep.csv` | EXISTS | ABSENT | `ba6c84e8b4af` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_cls_residual_events.csv` | EXISTS | ABSENT | `f4a4ae7575ba` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_image_predictions.csv` | EXISTS | ABSENT | `84b409e6b4dc` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_intervention_sweep.csv` | EXISTS | ABSENT | `ba6c84e8b4af` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_matched_controls.csv` | EXISTS | ABSENT | `7eb70257593d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_patch_intervention_sweep.csv` | EXISTS | ABSENT | `3985765c7443` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_small_patch16_224_patch_summary.csv` | EXISTS | ABSENT | `2ab5fb4fd874` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_cls_intervention_sweep.csv` | EXISTS | ABSENT | `51b7db438984` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_cls_residual_events.csv` | EXISTS | ABSENT | `efb09553580c` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_image_predictions.csv` | EXISTS | ABSENT | `ac3cff26efea` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_intervention_sweep.csv` | EXISTS | ABSENT | `51b7db438984` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_matched_controls.csv` | EXISTS | ABSENT | `7eb70257593d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_patch_intervention_sweep.csv` | EXISTS | ABSENT | `439dbbf10e6a` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/deit_tiny_patch16_224_patch_summary.csv` | EXISTS | ABSENT | `21c0173377d0` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `outputs/v0_1/experiment_manifest.json` | EXISTS | ABSENT | `ea212b0b0cf3` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `paper/LICENSE.md` | ABSENT | EXISTS | `N/A` | `80e38c1af8b3` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `paper/README.md` | ABSENT | EXISTS | `N/A` | `0da2ba860b77` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `patch_fungibility/__init__.py` | EXISTS | EXISTS | `9b6adbc20a1f` | `a60f301bdbdc` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/amortized_operator.py` | EXISTS | ABSENT | `836459afb205` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/attention_causal_audit.py` | EXISTS | ABSENT | `0cecb09ac672` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/batched_operator_compression.py` | EXISTS | ABSENT | `5e26a9db9ac8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/compression_models.py` | EXISTS | EXISTS | `186f797a4258` | `23135ac3b2f2` | `UPDATE_FROM_SOURCE` | Source contains generalized multiplicity partition handling for operator compression |
| `patch_fungibility/compression_pipeline.py` | EXISTS | EXISTS | `7470733683b4` | `c1bb9338a57d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/dataset.py` | ABSENT | EXISTS | `N/A` | `5acca9ba4ab5` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `patch_fungibility/decision.py` | EXISTS | EXISTS | `a5ff303b7bb1` | `bf66d80f71fa` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/dense_fraction_analysis.py` | EXISTS | EXISTS | `c1ebd195e8e8` | `c1ebd195e8e8` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/dense_fraction_masks.py` | EXISTS | EXISTS | `59ceadedc390` | `59ceadedc390` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/dense_fraction_models.py` | EXISTS | EXISTS | `1777f6b29b6c` | `1777f6b29b6c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/dense_fraction_pipeline.py` | EXISTS | EXISTS | `415978e526a1` | `415978e526a1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/full_fungibility_operator.py` | EXISTS | ABSENT | `464917afbf37` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/functional_geometry.py` | EXISTS | ABSENT | `8bd08372c3cf` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/geometry_bank_pipeline.py` | EXISTS | EXISTS | `078731e517c9` | `c654b8a0eb0f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/interventions.py` | EXISTS | EXISTS | `044e8b97f1d6` | `6794e13fb4e0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/joint_stream_geometry.py` | EXISTS | ABSENT | `bf6de32f04e4` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/joint_value_key.py` | EXISTS | ABSENT | `7e7683155eb7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/masks.py` | EXISTS | EXISTS | `7e24c227a528` | `7e3dd6ca06e1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/metrics.py` | EXISTS | EXISTS | `52025eff778a` | `5dbff57f4675` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/models.py` | EXISTS | EXISTS | `97136ac2fe57` | `3281b070fdde` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/multiblock_operator.py` | EXISTS | ABSENT | `5b12abee6391` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/operator_compression.py` | EXISTS | ABSENT | `b2d02130eb00` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/operator_compression_confirmatory.py` | EXISTS | ABSENT | `9eac83fbeb8d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/pipeline.py` | EXISTS | EXISTS | `21910ad83e3e` | `a48b1e46d66a` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/practical_operator_compression.py` | EXISTS | ABSENT | `6ebe6ec3393f` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/predictive_operator.py` | EXISTS | ABSENT | `b46488d022a7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/predictive_principle.py` | EXISTS | ABSENT | `319c54e1d8d5` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/residual_carrier_pipeline.py` | EXISTS | ABSENT | `13f34aec92f8` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `patch_fungibility/v0_5_decision.py` | EXISTS | EXISTS | `b4fba5493cda` | `03c0e268d30e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_5_interventions.py` | EXISTS | EXISTS | `3f08bf24c74f` | `761fe040d9f7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_5_pipeline.py` | EXISTS | EXISTS | `742c9bd074ab` | `7462bde5b0f3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_5_validation.py` | EXISTS | EXISTS | `72fc3110a749` | `d7a0bab6485c` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_calibration.py` | EXISTS | EXISTS | `d7eb7f113a01` | `8609291cd361` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_dataset.py` | EXISTS | EXISTS | `c8fbe54312e0` | `87947553a352` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_decision.py` | EXISTS | EXISTS | `9f7293f62e0a` | `05ea3c324708` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_masks.py` | EXISTS | EXISTS | `fbd129373ae7` | `4ee2ef694339` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_pipeline.py` | EXISTS | EXISTS | `8eafc871e967` | `6555a2d9e8d6` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_6_validation.py` | EXISTS | EXISTS | `82275ebe4ed4` | `514fe6b5d0fe` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_7_decision.py` | EXISTS | EXISTS | `4ebec4ebc6de` | `be01f2b5e47b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_7_masks.py` | EXISTS | EXISTS | `632ae0b56bc6` | `0f135246d33d` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_7_pipeline.py` | EXISTS | EXISTS | `d7ea8706ffe7` | `70cf7e09d8db` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_7_prototypes.py` | EXISTS | EXISTS | `96b7eec0c415` | `570038813868` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_7_validation.py` | EXISTS | EXISTS | `b71e2d909f05` | `d4a2f94b1f56` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_decision.py` | EXISTS | EXISTS | `7226f2642432` | `e9c75e3340fa` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_diagnostics.py` | EXISTS | EXISTS | `7bdc9cf8c6f6` | `09e93d83156f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_interventions.py` | EXISTS | EXISTS | `0d1028bca23e` | `dbbd1dd8dac1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_pca.py` | EXISTS | EXISTS | `e39eab7f334e` | `3643322c707e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_pipeline.py` | EXISTS | EXISTS | `f509fc99b0c9` | `9f45bf423b52` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_8_validation.py` | EXISTS | EXISTS | `b0fdf47340a4` | `0b08729208dd` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_9_decision.py` | EXISTS | EXISTS | `dbb2b42352aa` | `fd6daffec61e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_9_diagnostics.py` | EXISTS | EXISTS | `2dc437206146` | `730703ec80bb` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_9_interventions.py` | EXISTS | EXISTS | `202f5c1aa956` | `631c53ecf6c7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_9_pipeline.py` | EXISTS | EXISTS | `36fddccd8c76` | `e1d1016393e2` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v0_9_validation.py` | EXISTS | EXISTS | `bc1c366dd576` | `be81f1babe22` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v1_decision.py` | EXISTS | EXISTS | `1aaffa6522f0` | `391e4ee2ba66` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v1_interventions.py` | EXISTS | EXISTS | `234647672a8e` | `611a4d0998df` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v1_models.py` | EXISTS | EXISTS | `6a7acd3d5c1b` | `a84d5c6eb3a0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v1_pipeline.py` | EXISTS | EXISTS | `b7681226d17d` | `6f15d7608d3e` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/v1_validation.py` | EXISTS | EXISTS | `e5393c3637bf` | `2d25ae84530f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `patch_fungibility/validation.py` | EXISTS | EXISTS | `6b84e4752d75` | `0f6fc27ccc26` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `rescancel/__init__.py` | EXISTS | ABSENT | `360629487e84` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/audit_validation.py` | EXISTS | ABSENT | `e9b5c4a53ea9` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/confound_matching.py` | EXISTS | ABSENT | `da557fb3fac5` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/corruptions.py` | EXISTS | ABSENT | `8ff04e1acd34` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/dataset.py` | EXISTS | ABSENT | `02fc294e2a44` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/instrumentation.py` | EXISTS | ABSENT | `0f4805cf780e` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/intervention.py` | EXISTS | ABSENT | `8384c1951187` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/metrics.py` | EXISTS | ABSENT | `30860071e1a9` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `rescancel/pipeline.py` | EXISTS | ABSENT | `7d5783a9f434` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/audit_amortized_operator.py` | EXISTS | ABSENT | `26d5ecab3f9b` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/audit_multiplicity_flashattention.py` | EXISTS | ABSENT | `53ea20ec20e0` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/eval_amortized_operator.py` | EXISTS | ABSENT | `6663c2956809` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/eval_batched_operator.py` | EXISTS | ABSENT | `f9392adc92ec` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/eval_hybrid_grouping.py` | EXISTS | ABSENT | `f9e4fcf27c4d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/generate_operator_targets.py` | EXISTS | ABSENT | `fdf50c2b7054` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/plot_delta_figures.py` | EXISTS | ABSENT | `61682ce50b60` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/plot_delta_v0_5_figures.py` | EXISTS | ABSENT | `1e01e7db05ba` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/plot_figures.py` | EXISTS | ABSENT | `2c1a5d6de2fd` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/plot_fungibility_compression.py` | EXISTS | EXISTS | `3b302f5c3937` | `d5da43a644ac` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_dense_fraction.py` | EXISTS | EXISTS | `de62d31d79d0` | `de62d31d79d0` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_geometry_bank.py` | EXISTS | EXISTS | `4a279445c744` | `e9d61089b2b3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_5_figures.py` | EXISTS | EXISTS | `e94bd92a2097` | `429ef0e64e16` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_6_figures.py` | EXISTS | EXISTS | `e41ea537c347` | `e32a5dec3445` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_7_figures.py` | EXISTS | EXISTS | `f2ac3904119f` | `e77c77450e1b` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_8_figures.py` | EXISTS | EXISTS | `faf1313c4d4c` | `e1aad9137a80` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_9_figures.py` | EXISTS | EXISTS | `1d2528c9dc83` | `bcf463770035` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v0_figures.py` | EXISTS | EXISTS | `85c645d95e55` | `0c1a90b85db7` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_fungibility_v1_figures.py` | EXISTS | EXISTS | `9dec42165880` | `42dc96a71593` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/plot_residual_carrier_figures.py` | EXISTS | ABSENT | `0cbba0975ebe` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/profile_batched_operator.py` | EXISTS | ABSENT | `1c5ccb5e1100` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/profile_operator_compression.py` | EXISTS | ABSENT | `77d0a2fefa5c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/render_paper_figures_final.py` | EXISTS | EXISTS | `43fe06355c1f` | `43fe06355c1f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_attention_causal_audit.py` | EXISTS | ABSENT | `e3df2f1cc948` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_delta_v0.py` | EXISTS | ABSENT | `928bbab8179d` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/run_delta_v0_5.py` | EXISTS | ABSENT | `6562f22ea5b8` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/run_full_fungibility_operator.py` | EXISTS | ABSENT | `d376001964e6` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_functional_geometry.py` | EXISTS | ABSENT | `b56ab5c61573` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_fungibility_compression.py` | EXISTS | EXISTS | `4b2b3be6d10a` | `597cc5ad8e24` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_dense_fraction.py` | EXISTS | EXISTS | `73450ddad8f8` | `73450ddad8f8` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_geometry_bank.py` | EXISTS | EXISTS | `3ee16f893f54` | `4535c313f22f` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_v0.py` | EXISTS | EXISTS | `afbb8f9483ed` | `be0639c8c685` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `scripts/run_fungibility_v0_5.py` | EXISTS | EXISTS | `c6c73c12abc9` | `10fec47e923b` | `KEEP_TARGET` | Target-specific polished file or safety rule preserved |
| `scripts/run_fungibility_v0_6.py` | EXISTS | EXISTS | `7600ae5e9fe1` | `bbd9c9993a89` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_v0_7.py` | EXISTS | EXISTS | `8f61ea4ab76a` | `e4b3c9be1e98` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_v0_8.py` | EXISTS | EXISTS | `c6e034d0c447` | `b1d5a295c4b1` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_v0_9.py` | EXISTS | EXISTS | `3f4b65a09ab9` | `969ba6cc25e9` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_fungibility_v1.py` | EXISTS | EXISTS | `0d8e0312f82d` | `453aa7bb2ef3` | `KEEP_TARGET` | Identical or already synchronized PCF research artifact |
| `scripts/run_joint_stream_geometry.py` | EXISTS | ABSENT | `882f6ae6d522` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_joint_value_key.py` | EXISTS | ABSENT | `91e7722e4984` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_multiblock_operator.py` | EXISTS | ABSENT | `6810a265f1c7` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_operator_compression.py` | EXISTS | ABSENT | `5b891e6db657` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_operator_compression_confirmatory.py` | EXISTS | ABSENT | `ccc0bba02699` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_practical_operator_compression.py` | EXISTS | ABSENT | `e5b512f647c3` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_predictive_operator.py` | EXISTS | ABSENT | `e7e5320e0068` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_predictive_principle.py` | EXISTS | ABSENT | `869ce9974b6c` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_residual_carrier_experiment.py` | EXISTS | ABSENT | `551254485e29` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
| `scripts/run_v0_pipeline.py` | EXISTS | ABSENT | `9cdc75a0e411` | `N/A` | `SKIP_LEGACY` | Legacy ResCancel / Delta artifact not part of Patch Content Fungibility |
| `scripts/train_amortized_operator.py` | EXISTS | ABSENT | `4f8a4b067a2d` | `N/A` | `COPY_NEW` | New PCF research artifact migrated from ResCancel |
