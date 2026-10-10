# Regularization Factor Audit

**Scope.** This audit checks the archived evidence for the rationale that the confirmatory regularization factor \(\lambda_{\mathrm{factor}}=10\) was selected by a pilot sweep because it optimally balances linear transmission cancellation and nonlinear manifold distortion. It reads the current source, Git history, protocol/report, run manifest, and existing CSVs. No model runs, new sweeps, or benchmark outputs were generated.

## Verdict

**PARTIALLY SUPPORTED.** The confirmatory implementation and run manifest both record factor 10, and the repository contains older regularization-sensitivity evidence. However, no matching factor sweep, candidate-factor comparison, or nonlinear-distortion measurements for the confirmatory per-image exact-Jacobian objective were found. The claim that factor 10 is optimal or balances linear cancellation against nonlinear distortion is therefore **unverified and withdrawn**. This audit does not recommend changing the factor used in the already-completed confirmatory results.

## What the confirmatory record establishes

- The protocol defines \(\lambda=\lambda_{\mathrm{factor}}\operatorname{Tr}(\Sigma)/D_{\mathrm{readout}}\) and records factor 10 at `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_PROTOCOL.md:30-37`.
- The implementation defaults to `lam_factor=10.0` and computes `lam = lam_factor * trace(Sigma) / D_readout` at `patch_fungibility/operator_compression_confirmatory.py:278-324`. The benchmark calls the solver with `lam_factor=10.0` at `scripts/run_operator_compression_confirmatory.py:260-268`.
- The run manifest records `frozen_lambda_factor: 10.0`, 1,000 evaluation images, four architectures, and their budgets at `outputs/fungibility_operator_compression_confirmatory/validation_manifest.json` (timestamp `2026-10-05 03:06:54`). The per-image CSV stores outcome metrics, operator residual, and correction norm; it does not store \(\operatorname{Tr}(\Sigma)\), \(D_{\mathrm{readout}}\), or the resulting absolute \(\lambda\). The absolute per-image confirmatory \(\lambda\) therefore cannot be reconstructed from the archived run tables.
- The current confirmatory code and stored output use one factor only. The repository contains no archived confirmatory rows or pilot artifact comparing candidate `lambda_factor` values, architectures/budgets for such a sweep, or a criterion combining linear residual with nonlinear distortion.

## Related historical sweep, and why it is not the claimed pilot

The older implicit-carrier audit has `LAM_GRID = [10, 1, 0.1, 0.01, 0.001, 0.0001]` at `scripts/audit_implicit_carrier_operator.py:68-69`. Its saved `stabilized_full_oracle.csv` rows use these as **absolute** Tikhonov parameters, not as candidates for `lambda_factor` in the confirmatory normalization. The script evaluates 100 validation images per architecture, a single fixed token budget (98 for the 196-token models and 128 for DINOv2), and a rank-32 projected operator (`scripts/audit_implicit_carrier_operator.py:61-69, 186-197`). Its recorded criteria are mean projected transmission residual \(\|J E\|\), correction norm, a reported objective, and reduction relative to Group Mean; it does not record high-order manifold distortion.

For the existing absolute-\(\lambda\) sweep, the mean projected residual at \(\lambda=10\) versus \(\lambda=0.001\) was:

| Architecture | Mean residual, \(\lambda=10\) | Mean residual, \(\lambda=0.001\) | Ratio |
|---|---:|---:|---:|
| DeiT-Tiny | 3.9091 | 0.006707 | 582.9× |
| DeiT-Small | 11.7595 | 0.019589 | 600.3× |
| ViT-Base | 17.4246 | 0.027847 | 625.7× |
| DINOv2 | 0.67884 | 0.001157 | 586.7× |

These are descriptive results from `outputs/fungibility_implicit_carrier_operator_audit/stabilized_full_oracle.csv` filtered to `method=Tikhonov_Full_Oracle` and the stated parameter values. They show strong sensitivity to **absolute** regularization in that older setup. They do not show that a dimensionless factor of 10 is optimal for the confirmatory implementation.

## Relationship to the earlier over-damping finding

The earlier audit documents a legacy implicit-carrier solve with \(\lambda=\max(10^{-3},10\operatorname{Tr}(\Sigma)/r)\), typically about 10–100, and reports that this over-damped its rank-32 full-space reference. The saved audit attributes the spurious recovery denominator to that legacy setting and compares it with a stabilized absolute \(\lambda=10^{-3}\) solve (`docs/FUNGIBILITY_IMPLICIT_CARRIER_OPERATOR_AUDIT.md:14-28, 60-62`; `scripts/audit_implicit_carrier_operator.py:113-125, 217-224`).

This is a relevant caution, not a direct validation of the confirmatory factor. Both formulations use a trace-scaled regularizer, but the earlier solve projects through a rank-32 basis \(V_{\mathrm{true}}\) and uses the reduced correction variable; the confirmatory solver uses the per-image exact downstream Jacobian and states the objective as \(\|J\operatorname{vec}(P-SC)\|^2+\lambda\|P-SC\|_F^2\) (`patch_fungibility/operator_compression_confirmatory.py:285-288`). The old audit's regularization grid is absolute, its input/operator and grouping setup differ, and its sweep criteria omit nonlinear distortion. In addition, an absolute \(\lambda=10\) in the old outputs is not numerically interchangeable with \(10\operatorname{Tr}(\Sigma)/D_{\mathrm{readout}}\) in the confirmatory run. Because the confirmatory trace values were not saved, this archive cannot establish whether the confirmatory absolute values match the older 10–100 range. The shared factor value alone is not enough to transfer the old over-damping conclusion.

## Chronology and preregistration limits

The report and confirmatory manifest cite `77e694a96e530ee5c9776d11daab8a426de14117` as the protocol commit. That commit is not present in the current Git object database (`git cat-file -e <hash>^{commit}` fails). In the repository history available here, the protocol first appears in migration commit `0223ca32a1b528fe21d7852073e8d34597c7d7ab`, dated 2026-10-06 23:34:23 +07:00. The manifest timestamp is 2026-10-05 03:06:54, but a stored timestamp and an unresolved hash do not independently prove when the protocol was frozen relative to evaluation. Accordingly, this audit verifies the run setting but does not independently verify preregistration chronology.

## Corrections made

- `docs/PAPER_DRAFT.md` now reports factor 10 as the setting used, removes the unsupported pilot-optimality statement, and states the evidence boundary.
- The matching paragraph in `docs/PAPER_DRAFT_v5.docx` still contains the prior claim. An edit was attempted after Word was closed, but Windows denied replacement of that file (`WinError 5`), so the DOCX was left intact. The source manuscript and protocol corrections are complete; the binary Word copy remains outstanding.
- `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_PROTOCOL.md` preserves an explicit dated correction and withdraws the unsupported rationale. The prior wording remains available in Git history.
- `docs/FUNGIBILITY_OPERATOR_COMPRESSION_CONFIRMATORY_REPORT.md` adds a provenance qualification so the unresolved protocol hash is not presented as independently verified chronology.
- The existing confirmatory outputs and analysis code were not changed. No sweep chart was produced because no matching confirmatory pilot dataset exists.

## Validation

`python scripts/validate_paper_final.py` passed 30/30 checks after the source, protocol, and report edits. The validator's JSON report was emitted to standard output while its normal output-file write was suppressed so archived result files remained unchanged. This validator checks the document's structural and quantitative assertions but does not compare this corrected paragraph against the still-locked Word copy. No experiment or benchmark was rerun.
