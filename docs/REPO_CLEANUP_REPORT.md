# PCF Repository Cleanup Report

**Date:** 2026-10-10

**Cleanup branch:** `chore/pre-submission-repo-cleanup`

**Base:** `origin/main` at `8e7e464309373083df63db164ea9f47600fab20c`

## Scope and safety record

This batch improves repository navigation and reproducibility documentation. It does not alter manuscript scientific content, experimental data, equations, methods, figure files, validation code, or Word documents. No tracked file was deleted, moved, ignored, or rewritten outside the five documentation paths listed below. `.gitignore` is unchanged.

The cleanup started from the latest fetched `origin/main`. Before branching, the local checkout was at `0f9acf9307a47ecaace7a784b15dd0f74ebb7dad`; the fetched remote contained one later figure-render commit. An annotated local-only tag, `pcf-pre-cleanup-2026-10-10`, preserves the exact former local HEAD. The cleanup branch is based on the fetched remote commit; neither `main` nor the tag is part of the push.

| Change | Purpose |
|---|---|
| [`README.md`](../README.md) | Makes the current journal draft, preprint record, canonical figure locations, evidence, reproduction steps, and license distinction clear. |
| [`REPRODUCIBILITY_GUIDE.md`](REPRODUCIBILITY_GUIDE.md) | Documents environment prerequisites and maps manuscript figures, tables, cohorts, validators, and evidence to source files. |
| [`REPOSITORY_STRUCTURE.md`](REPOSITORY_STRUCTURE.md) | Distinguishes current publication assets from alternate and historical material. |
| [`REPO_CLEANUP_INVENTORY.md`](REPO_CLEANUP_INVENTORY.md) | Records all tracked paths, file roles, canonical figure resolution, exact archive/storage candidates, sizes, hashes, and unresolved cases. |
| [`REPO_CLEANUP_REPORT.md`](REPO_CLEANUP_REPORT.md) | This decision record and validation summary. |

The fetched base had 897 tracked files; the cleanup branch has 901 after adding four documentation files. The final tracked tree is 549,431,796 bytes. The two pre-existing untracked Word backups, `outputs/PAPER_DRAFT_v5_before_section7_reframing.docx` and `outputs/PAPER_DRAFT_v5_before_sensitivity.docx`, remain untouched and are excluded from the tracked-file inventory and cleanup commit.

## Manuscript and Word preservation

Neither Word package was written. Their current SHA-256 hashes match the values recorded before cleanup:

- Main manuscript, [`docs/PAPER_DRAFT_v5.docx`](PAPER_DRAFT_v5.docx): `8c143da1c05d80d057cdb80d3cb603d843db20ff576949a15fe9c22c13aa2460`.
- Supplement, [`docs/PAPER_SUPPLEMENTARY.docx`](PAPER_SUPPLEMENTARY.docx): `c0fd553d76f893b7d768a8f526c30f9a82f0cc8bbc117d7ac280555c4ebfdef0`.

This preserves the user's manual Word formatting and edits. Only the README and four cleanup Markdown files are included in the change set; the complete inventory identifies all 901 paths.

## Figure and evidence resolution

The current main manuscript cites Figures 1–8 from `figures/paper_final_v4/`. The main DOCX's eight embedded images match the corresponding v4 PNGs by SHA-256. Supplementary Markdown cites S1–S9 from `figures/paper_final/supp/` and S10–S15 from `figures/paper_final_v4/supp/`; S10–S15 embedded images match the corresponding v4 PNGs.

There is one pre-existing package inconsistency requiring editorial review: the fetched CI-render commit `8e7e464` refreshed the source PNGs for S1–S9, while the Supplementary DOCX still embeds the earlier S1–S9 images. Those images therefore do not hash-match. Both source PNGs and the Word package are preserved; this cleanup does not regenerate the DOCX or choose which version should be authoritative. The inventory lists each exact path.

The manuscript references resolve to 23 figure source files (8 main and 15 supplementary). PNG decoding and SVG XML parsing succeeded for the referenced assets; the publication validators also confirmed the expected figure counts. This is a file/reference integrity check, not a new figure redesign or an assertion that the S1–S9 package mismatch is resolved.

## Retained cleanup candidates

The complete file-by-file register is in [`REPO_CLEANUP_INVENTORY.md`](REPO_CLEANUP_INVENTORY.md). Nothing listed below was removed or externalized.

- **Archive candidates:** 17 files remain in place: `docs/PAPER_DRAFT_v4.docx` and the eight assets in each of `figures/paper_final_v2/` and `figures/paper_final_v3/`. The current manuscript uses v4 paths, but older figures and document versions may preserve provenance or review history. No independently verified archive copy was available, so no move is proposed as part of this batch.
- **External-storage candidates:** 23 tracked output files at least 1 MiB, totaling 451,595,391 bytes (430.67 MiB); 8 exceed 5 MiB and total 419,772,035 bytes (400.33 MiB). Externalizing all of them could reduce a checkout by at most the listed 430.67 MiB, but it would not remove Git-history blobs. The inventory records each path, byte count, SHA-256, scientific role, dependencies, and a retention proposal. No storage destination, retrieval workflow, or independently verified archive was established; all files stay in Git.
- **Same-content calibration files:** `outputs/fungibility_v1/calibration_statistics.npz` and `outputs/fungibility_v1_grouped_diversity_extension/calibration_statistics_used.npz` share a SHA-256 hash, but remain at both paths because their run provenance differs. The inventory records the pair and hash; content identity alone is not treated as proof of redundancy.
- **Unresolved files:** 13 paths stay untouched pending source/provenance review, including the separate `figures/paper_final/main/` set and `outputs/fungibility_real_final/README.md`.

The inventory classifies all 901 tracked paths: 366 essential, 482 research-history, 17 archive candidates, 23 external-storage candidates, 13 unresolved, and zero generated temporaries. These classes are mutually exclusive. The `.gitignore` rules were not broadened, and tracked evidence files were not hidden from version control.

## Reproduction and validation

The README points readers to the reproducibility guide, which explains that no complete cross-platform dependency lock is recorded, ImageNet validation Parquet shards and pretrained weights are external prerequisites, and model reruns can be computationally expensive. It distinguishes archived-data validators from full model-inference experiments and warns that figure builders can overwrite tracked assets.

The existing validators were run on this branch:

| Command | Result |
|---|---|
| `python scripts/validate_paper_final.py` | **PASS, 42/42 checks.** Current paper structure, citations, figure references, numeric traceability, and existing DOCX/supplement structure pass. |
| `python scripts/validate_real_final_benchmark.py` | **PASS, 12/12 checks.** Existing real-final benchmark artifacts pass the strict data validator. |
| `git diff --check` | **PASS.** No whitespace errors in the cleanup changes. |

Additional read-only checks confirmed all documented internal paths and listed script entry points exist, all 23 current manuscript figure references resolve, and the three previously reviewed supplementary wording corrections remain present in the Markdown source. Both DOCX hashes remain unchanged. No experiments or figure builders were run.

## Issues surfaced, not altered

These inconsistencies should be reconciled in a separately reviewed evidence/documentation pass; changing their historical content was outside this cleanup:

1. `outputs/fungibility_real_final/README.md` says no complete per-image classification output or actual-model throughput run has passed validation, while the current benchmark artifacts and `validation_manifest.json` report a completed state and the strict validator passes 12/12.
2. The “Figure Sources” section of `docs/PAPER_NUMBER_TRACEABILITY.md` still says the current assets are all in `figures/paper_final_v3/`; the current manuscript references the v4 main set and a split S1–S9/S10–S15 supplementary set.
3. `docs/REAL_FINAL_BENCHMARK_REPORT.md` retains old statements that the paper-validation gate and paper repair remain incomplete, which conflict with the current 12/12 benchmark validator result and current manuscript validator result. The historical narrative was not rewritten.
4. `docs/PAPER_REVIEWER_AUDIT.md` references older `figures/paper_final/main/` assets in its historical audit. The new README and structure guide identify those as a separate set rather than the current paper's canonical sources.
5. The S1–S9 source PNGs and embedded supplementary-DOCX images differ after the upstream render commit, as described above.

## Follow-up proposals

This cleanup makes no destructive or scientific changes. A later, separately reviewed archival step could select a destination for the 23 large output files, copy and verify them by the recorded SHA-256 hashes, test retrieval, and only then consider removing duplicates from the working-tree version. The 17 older manuscript/figure files and the 13 unresolved paths need provenance and citation review before any relocation or deletion. No Git LFS conversion, history rewrite, data upload, tracked-file deletion, manuscript edit, DOCX regeneration, or merge to `main` is included here.
