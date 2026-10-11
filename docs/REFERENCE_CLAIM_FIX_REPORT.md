# Reference–Claim Fix Report

Date: 11 October 2026
Scope: targeted citation, reference metadata, and effective-rank clarification in `PAPER_DRAFT_v5.docx`; citation synchronization only in `PAPER_SUPPLEMENTARY.docx`.

## Summary

The two DOCX files were edited in place at the OOXML package level. The edits correct the audited attribution of Optimal Brain Damage / Optimal Brain Surgeon, cite the official DINOv2 readout documentation, add the directly relevant CAAP prior work, correct the Optimal Brain Surgeon metadata, and cite and accurately describe the entropy-based effective-rank measure. Experimental results, equations, figures, tables, and scientific conclusions were not changed.

## Changes made

### A. Optimal Brain Damage and Optimal Brain Surgeon

**Main manuscript, Section 2 (Related Work).** Before, the paragraph said: “Sensitivity-weighted objectives and Jacobian-based measures provide established foundations for analyzing downstream functional effects [45], [46].” Those two references are the curvature-based pruning papers OBD and OBS; that sentence attached an unsupported Jacobian claim to them.

It now says: “Second-order curvature-based pruning criteria have a long history [46], [47].” The neighboring text separately describes Bond et al. and Liu et al. as direct precedents for ViT task-induced/Jacobian geometry and approximate-nullspace analysis, with citations [42] and [43] unchanged. The paper therefore no longer uses OBD/OBS as evidence for Jacobian geometry.

### B. DINOv2 classifier readout

**Main manuscript, Section 5.3.** Before, the first detailed DINOv2 readout description said it “concatenates normalized CLS and mean normalized patch features” with no citation at that point. It now cites both the DINOv2 paper [5] and official implementation/model-card source [58]: “concatenates normalized CLS and mean normalized patch features [5], [58]”. The official model card describes the class token plus average patch-token linear readout; the implementation uses normalized CLS and patch-token features and concatenates CLS with the mean patch representation ([official model card](https://github.com/facebookresearch/dinov2/blob/main/MODEL_CARD.md); [official classifier implementation](https://github.com/facebookresearch/dinov2/blob/main/dinov2/hub/classifiers.py)). These sources document the readout topology; they do not establish a causal explanation for the manuscript’s empirical findings.

The Supplementary adds [58] to the corresponding readout descriptions in S5, S7, and S11. No supplementary result or mechanistic conclusion was changed. The supplementary document has no independent reference list; its citations use the manuscript’s shared numbering.

### C. Corrected Optimal Brain Surgeon metadata

Old reference [46] is now [47] and reads:

> B. Hassibi, D. G. Stork, and G. J. Wolff, “Optimal Brain Surgeon and general network pruning,” in Proceedings of the 1993 IEEE International Conference on Neural Networks, vol. 1, pp. 293–299, 1993. DOI: 10.1109/ICNN.1993.298572.

This restores Gregory J. Wolff, corrects the duplicated/malformed venue name, and retains the DOI and page range. The author-hosted Caltech record and DOI record identify the same paper and metadata ([Caltech record](https://authors.library.caltech.edu/records/tzehb-vz706); [DOI](https://doi.org/10.1109/ICNN.1993.298572)).

### D. CAAP and the scope of PCF’s prior-art distinction

**Main manuscript, Section 2 (Related Work).** A sentence was added distinguishing *Causal Attribution via Activation Patching* (CAAP): it inserts source-image spatial-patch activations into a blank target context to perform attribution. The following sentence specifies PCF’s different question: whether ordinary late-layer patch content can be replaced by class-agnostic calibration-derived surrogates across depths and replacement fractions while retaining the spatial slots, sequence length, model weights, and downstream computation.

The added text reads: “Causal Attribution via Activation Patching (CAAP) intervenes on internal ViT spatial-patch activations by inserting source-image patch activations into a blank target context for attribution [45]. PCF instead tests whether ordinary late-layer patch content can be replaced by class-agnostic calibration-derived surrogates across depths and replacement fractions, while preserving spatial slots, sequence length, model weights, and downstream computation.” This recognizes prior spatial-patch activation intervention and does not claim that PCF is the first such intervention. The new reference is [45], A. Izadi et al., “Causal Attribution via Activation Patching,” arXiv:2603.13652v2, 2026, DOI 10.48550/arXiv.2603.13652. The arXiv record identifies it as a preprint and supplies the listed authors, title, version, and DOI; it does not list a peer-reviewed publication venue ([arXiv record](https://arxiv.org/abs/2603.13652); [full text](https://arxiv.org/html/2603.13652)). Its publication status is therefore described separately from the relevance of its method.

### E. Effective-rank source and formula

**Main manuscript, Section 5.1.** Before, Section 5.1 referred to “the entropy-based effective rank of M, normalized by feature dimension D” without a source. It now cites Roy and Vetterli [57] at the first definition and says the measure is “divided by feature dimension D as a PCF normalization.” This makes clear that `1/D` is the manuscript’s dimensionless reporting convention, not part of the cited base definition.

Roy and Vetterli define effective rank as the exponential of Shannon entropy over singular values normalized to sum to one (Definition 1, p. 606 of the [EUSIPCO paper](https://www.eurasip.org/Proceedings/Eusipco/Eusipco2007/Papers/a5p-h05.pdf)). PCF applies the same entropy formula to the normalized positive eigenvalues of its symmetric positive-semidefinite empirical matrix `M`. For a positive-semidefinite matrix, singular values equal eigenvalues, so this is the same base measure; numerically nonpositive eigenvalues are clipped after the manuscript’s PSD checks. Dividing that measure by `D` is an additional PCF normalization. The source is the 2007 EUSIPCO conference paper; `10.5281/zenodo.40328` is identified as its archival DOI, not represented as a publisher DOI ([conference record](https://ieeexplore.ieee.org/document/7098875); [Zenodo archive record](https://doi.org/10.5281/zenodo.40328)).

## Final reference numbering

Three references were added; citations in the main manuscript were synchronized accordingly. References [1]–[44] retain their numbering. The affected and new entries are:

| Final number | Reference | Numbering / status |
|---:|---|---|
| [45] | Izadi et al., *Causal Attribution via Activation Patching* | New; arXiv preprint, v2, 2026 |
| [46] | LeCun et al., *Optimal Brain Damage* | Former [45]; metadata retained |
| [47] | Hassibi, Stork, and Wolff, *Optimal Brain Surgeon and general network pruning* | Former [46]; author/venue corrected, DOI retained |
| [48] | Thrash et al., *Output-aware Residual Stream Pruning for Large Language Models* | Former [47] |
| [49]–[56] | Former references [48]–[55] | Renumbered +1 |
| [57] | Roy and Vetterli, *The Effective Rank: A Measure of Effective Dimensionality* | New; EUSIPCO 2007 conference paper; archive DOI identified |
| [58] | Meta AI DINOv2 model card and linear-classifier implementation | New; official software documentation, no DOI |

The OBD source remains its existing NeurIPS record ([1989 proceedings entry](https://proceedings.neurips.cc/paper/1989/hash/6c9882bbac1c7093bd25041881277658-Abstract.html)). The DINOv2 citation is intentionally identified as software documentation with an access date; no DOI or peer-reviewed publication status is implied.

## Citation and package validation

- Main-manuscript reference list: 58 entries, sequentially numbered; all 58 are cited and no cited number is missing.
- Supplementary citations to the shared bibliography are consistent, including the three new [58] citations.
- DOCX package integrity: each file retains the same ZIP member set; only `word/document.xml` changed. Media, relationships, styles, numbering, settings, and embedded image bytes were preserved.
- Structural counts after editing: the main DOCX contains 14 tables (four manuscript tables and ten equation-layout tables), 118 OMML math objects, and 8 figure drawings; the Supplementary contains 8 tables, 89 OMML math objects, and 15 figure drawings. Existing paragraph properties and run formatting were preserved; three formatted reference paragraphs were added to the main document.
- Both files opened and rendered through LibreOffice: 18 manuscript pages and 19 Supplementary pages. Every page was visually inspected at readable resolution. The [45] citation spacing was corrected before the final render. Pagination remained unchanged; no clipping or new layout issue was found.

## Final validation results

- `validate_real_final_benchmark.py`: **PASS**, 12/12 checks.
- `validate_paper_final.py`: **FAIL**, 39/42 checks passed. The three failed checks are: (1) its heading/table-label check does not recognize the existing table-label text in the DOCX; the same check also failed on the pre-edit backup; (2) its IEEE citation-sequence check compares the unchanged Markdown/BibTeX source (26 citation tokens) with the corrected DOCX (30 tokens), which diverge because this task requested DOCX-only changes; and (3) its editable-DOCX structure check is hard-coded to exactly 55 references and the same table-label parser, while the corrected DOCX now correctly contains 58 references. The validator was not changed or weakened.
- Independent DOCX check: both packages pass ZIP CRC and XML parsing; each has the same package members as its pre-edit copy and `word/document.xml` is the only changed package part. References are sequential [1]–[58], all 58 are cited, and every citation resolves. Corrected OBS metadata and all three new reference records are present.
- `git diff --check`: **PASS**. A separate whitespace scan of this report is also included in the final check.

## Remaining limitations

CAAP is cited as the arXiv preprint listed by its source record; no journal or conference venue is shown there. The DINOv2 model card and implementation are software documentation and have no DOI. Roy and Vetterli’s measure matches PCF’s entropy formula for the PSD matrix described above, while division by `D` remains a PCF-specific normalization. `PAPER_DRAFT.md` and `PAPER_REFERENCES.bib` remain unchanged because the requested edit scope was the two DOCX files; as a result, their citation numbering is not synchronized with the corrected Word manuscript. If those files are the canonical sources for a future DOCX export, they will need a separate synchronization pass.
