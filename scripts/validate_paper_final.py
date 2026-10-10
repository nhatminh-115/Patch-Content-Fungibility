"""Fail-closed publication gate for the final manuscript and figure set."""
from __future__ import annotations

import csv
import json
import math
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
DRAFT = DOCS / "PAPER_DRAFT.md"
TRACE = DOCS / "PAPER_NUMBER_TRACEABILITY.md"
CLAIMS = DOCS / "PAPER_FINAL_CLAIMS_TABLE.md"
SAMPLES = DOCS / "PAPER_SAMPLE_SIZE_MAP.md"
FIGS = ROOT / "figures" / "paper_final_v4"
DOCX_PATH = DOCS / "PAPER_DRAFT_v5.docx"
SUPPLEMENTARY_DRAFT = DOCS / "PAPER_SUPPLEMENTARY_DRAFT.md"
SUPPLEMENTARY_DOCX = DOCS / "PAPER_SUPPLEMENTARY.docx"
if not DOCX_PATH.is_file():
    DOCX_PATH = DOCS / "PAPER_DRAFT_v4.docx"
sys.path.insert(0, str(ROOT / "scripts"))
import export_paper_markdown_to_docx as exporter


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def markdown_table(text: str, roman: str) -> list[list[str]]:
    lines = text.splitlines()
    title = f"**TABLE {roman}**"
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == title)
        start = next(i for i in range(start + 1, len(lines)) if lines[i].strip().startswith("|"))
    except StopIteration:
        return []
    block = []
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break
        block.append([cell.strip() for cell in line.strip().strip("|").split("|")])
    return [row for row in block if not row or not all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in row)]


def supplementary_markdown_table(text: str, label: str) -> list[list[str]]:
    lines = text.splitlines()
    try:
        caption = next(i for i, line in enumerate(lines)
                       if re.match(rf"^\*\*Table\s+{re.escape(label)}\.", line.strip()))
        start = next(i for i in range(caption + 1, len(lines))
                     if lines[i].strip().startswith("|"))
    except StopIteration:
        return []
    block = []
    for line in lines[start:]:
        if not line.strip().startswith("|"):
            break
        row = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not all(re.fullmatch(r":?-{2,}:?", cell.replace(" ", "")) for cell in row):
            block.append(row)
    return block


def source_value(rows_: list[dict[str, str]], **filters) -> dict[str, str] | None:
    return next((r for r in rows_ if all(r.get(k) == str(v) for k, v in filters.items())), None)


def average_ranks(values: list[float]) -> list[float]:
    ordered = sorted(enumerate(values), key=lambda item: item[1])
    ranks = [0.0] * len(values)
    start = 0
    while start < len(ordered):
        end = start + 1
        while end < len(ordered) and ordered[end][1] == ordered[start][1]:
            end += 1
        rank = ((start + 1) + end) / 2.0
        for index, _ in ordered[start:end]:
            ranks[index] = rank
        start = end
    return ranks


def pearson(x: list[float], y: list[float]) -> float:
    if len(x) != len(y) or len(x) < 2:
        raise ValueError("Pearson inputs must have equal lengths >= 2")
    mx, my = sum(x) / len(x), sum(y) / len(y)
    dx, dy = [v - mx for v in x], [v - my for v in y]
    denom = math.sqrt(sum(v * v for v in dx) * sum(v * v for v in dy))
    return sum(a * b for a, b in zip(dx, dy)) / denom


def percentile(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    return ordered[lower] + (ordered[upper] - ordered[lower]) * (position - lower)


def main() -> int:
    checks: dict[str, dict[str, str]] = {}

    def record(name: str, ok: bool, detail: str) -> None:
        checks[name] = {"status": "PASS" if ok else "FAIL", "detail": detail}

    required = [DRAFT, TRACE, CLAIMS, SAMPLES, ROOT / "docs/PAPER_SUBMISSION_READINESS.md", DOCS / "PAPER_REFERENCES.bib", DOCS / "PAPER_CITATION_AUDIT.md", DOCS / "PAPER_FINAL_CONSISTENCY_AUDIT.md"]
    record("required_manuscript_and_audit_docs", all(p.is_file() for p in required),
           "Draft, claims, traceability, sample-size map, readiness, citation, bibliography, and final consistency records must exist.")
    text = DRAFT.read_text(encoding="utf-8-sig") if DRAFT.exists() else ""
    all_paper = "\n".join(p.read_text(encoding="utf-8-sig") for p in (DRAFT, TRACE, CLAIMS, SAMPLES) if p.exists())

    # Historical consolidation accuracy/timing tables were proxy-backed and are prohibited.
    proxy = re.search(r"fungibility_final_consolidation/(?:final_accuracy_table|final_throughput_table|final_pareto_frontier)\.csv", all_paper, re.I)
    record("no_proxy_accuracy_timing_or_frontier_sources", proxy is None,
           "No historical proxy accuracy, toy timing, or frontier CSV may be cited as empirical support.")
    stale = ["4432.0", "77.20", "sub-0.25 ms", "sub-0.25ms"]
    found = [s for s in stale if s.lower() in text.lower()]
    record("no_stale_practical_headline_values", not found,
           "Removed stale throughput, accuracy, and isolated-overhead headline claims." if not found else f"Found: {found}")

    # Sample units must be explicit and correctly separated.
    sample_ok = all(s in text for s in ("N=100 images", "N=100 held-out perturbations", "N=1,000 held-out images per architecture"))
    sample_ok = sample_ok and "N=1000" not in text
    record("mechanistic_sample_units_correct", sample_ok,
           "Attention/geometry image audits use N=100, multi-block uses perturbations, and confirmatory/carrier accuracy uses N=1,000 per model.")
    record("sample_map_and_claims_correct", all(s in SAMPLES.read_text(encoding="utf-8-sig") for s in ("N=100 evaluation images", "N=100 held-out perturbations", "N=1,000 held-out images per architecture"))
           and "N=100 held-out operator-space images" in CLAIMS.read_text(encoding="utf-8-sig"),
           "C2, C4/C5, confirmatory, and real-final counts are separately stated.")

    # Recompute the original Top-1 recovery ratio from same-image confirmatory rows.
    image_path = ROOT / "outputs/fungibility_operator_compression_confirmatory/per_image_results.csv"
    rank_path = ROOT / "outputs/fungibility_operator_compression_confirmatory/low_rank_ablation.csv"
    per_image_rows = rows(image_path) if image_path.exists() else []
    low_rank_rows = rows(rank_path) if rank_path.exists() else []
    method_names = {"Group-Mean Merging", "Operator-Aware (Oracle)",
                    "Operator-Aware (Rank-16)", "Operator-Aware (Rank-32)"}
    condition_images: dict[tuple[str, str, str], dict[str, tuple[float, str]]] = {}
    duplicate_images = False
    for item in per_image_rows:
        if item.get("method") not in method_names:
            continue
        key = (item["model"], item["budget"], item["method"])
        image_idx = item["image_idx"]
        condition_images.setdefault(key, {})
        if image_idx in condition_images[key]:
            duplicate_images = True
        condition_images[key][image_idx] = (float(item["top1_acc"]), item.get("seed", ""))

    recovery_rows = []
    positive_denominators = negative_denominators = zero_denominators = 0
    matched_cohorts_ok = not duplicate_images
    rank_summary_matches = True
    for rank_row in low_rank_rows:
        if rank_row.get("rank") not in ("16", "32"):
            continue
        model, budget = rank_row["model"], rank_row["budget"]
        rank_method = f"Operator-Aware (Rank-{rank_row['rank']})"
        groups = [condition_images.get((model, budget, method), {}) for method in
                  ("Group-Mean Merging", "Operator-Aware (Oracle)", rank_method)]
        if any(len(group) != 1000 for group in groups):
            matched_cohorts_ok = False
            continue
        image_ids = set(groups[0])
        if any(set(group) != image_ids for group in groups[1:]):
            matched_cohorts_ok = False
            continue
        if any({seed for _, seed in group.values()} != {"0"} for group in groups):
            matched_cohorts_ok = False
            continue
        gm_acc, full_acc, rank_acc = [sum(value for value, _ in group.values()) / 1000
                                      for group in groups]
        rank_summary_matches = rank_summary_matches and abs(rank_acc - float(rank_row["top1_acc"])) < 0.0005
        denominator = full_acc - gm_acc
        if abs(denominator) < 1e-12:
            zero_denominators += 1
            continue
        recovery = 100.0 * (rank_acc - gm_acc) / denominator
        if denominator > 0:
            positive_denominators += 1
        else:
            negative_denominators += 1
        recovery_rows.append((recovery, denominator > 0))

    above_98_positive = sum(1 for recovery, positive in recovery_rows if positive and recovery > 98.0)
    low_rank_audit_ok = (len(low_rank_rows) == 60 and len(recovery_rows) == 38
                         and positive_denominators == 22 and negative_denominators == 16
                         and zero_denominators == 2 and above_98_positive == 4
                         and matched_cohorts_ok and rank_summary_matches
                         and not re.search(r">\s*98\s*%", text, re.I)
                         and "do not support a universal recovery fraction" in text.lower())
    record("universal_low_rank_top1_recovery_claim_removed",
           low_rank_audit_ok,
           f"Matched rank-16/32 settings=40; positive/negative/zero Group-Mean-to-full-J Top-1 denominators={positive_denominators}/{negative_denominators}/{zero_denominators}; >98% among positive denominators={above_98_positive}/22; same N=1,000 image IDs and seed 0; rank summary matches per-image rows={rank_summary_matches}.")
    pareto_overclaim = re.search(r"\b(?:strictly|universally|always)\s+(?:Pareto\s+)?(?:dominates?|dominant|frontier improvement)\b|general Pareto (?:dominance|improvement)", text, re.I)
    record("no_unsupported_pareto_dominance", pareto_overclaim is None,
           "Frontier language is limited to measured non-dominated points and bounded regimes.")
    unresolved = re.search(r"\b(?:TODO|FIXME|PLACEHOLDER|TBD|xxxxx|yyyyy)\b", text, re.I)
    record("no_unresolved_placeholders", unresolved is None,
           "No unresolved editorial or bibliography placeholders remain in the manuscript.")
    record("no_local_file_urls", "file:///" not in text.lower(),
           "Manuscript contains no machine-local file URL.")
    record("canonical_repo_name_correct", "ResCancel" not in text and "github.com/nhatminh-115/Patch-Content-Fungibility" in text,
           "Canonical repository is Patch-Content-Fungibility; workspace folder name is not presented as canonical.")
    record("no_invalid_figure_paths", "paper_final_v2" not in text and "../figures/paper_final_v4/" in text,
           "Manuscript points only to visually reviewed v4 figures.")

    # BibTeX citation/reference consistency, including duplicate entries.
    cite_keys = set()
    for match in re.finditer(r"\\cite\w*\{([^}]+)\}", text):
        cite_keys.update(k.strip() for k in match.group(1).split(","))
    bib = text.split("```bibtex", 1)[1].split("```", 1)[0] if "```bibtex" in text else ""
    bib_keys = re.findall(r"@\w+\s*\{\s*([^,\s]+)", bib)
    duplicates = len(bib_keys) != len(set(bib_keys))
    unresolved_keys = cite_keys - set(bib_keys)
    uncited = set(bib_keys) - cite_keys
    record("bibliography_resolves_without_duplicates", not duplicates and not unresolved_keys and not uncited,
           f"{len(bib_keys)} entries; unresolved citations={sorted(unresolved_keys)}; uncited entries={sorted(uncited)}; duplicates={duplicates}.")

    paths = re.findall(r"\]\((\.\./figures/[^)]+)\)", text)
    missing = [p for p in paths if not (DOCS / p).resolve().is_file()]
    invalid = [p for p in paths if "paper_final_v2" in p or not p.endswith(".svg")]
    record("all_manuscript_figures_exist_and_are_v4_svg", bool(paths) and not missing and not invalid
           and all("paper_final_v4" in p for p in paths),
           f"Referenced figures={len(paths)}; missing={missing}; invalid={invalid}.")

    # The plotted joint-stream cells must map one-to-one to the existing audited CSV rows.
    joint_rows = rows(ROOT / "outputs/fungibility_joint_stream_geometry/directional_curves.csv")
    joint_pairs = {("deit_small", 5), ("deit_small", 8), ("deit_small", 10),
                   ("vit_base", 5), ("vit_base", 7), ("vit_base", 10)}
    joint_patterns = {"single_central", "single_corner", "global_coherent", "random_sign",
                      "random_gaussian", "spatial_cluster_25%", "checkerboard", "smooth_spatial"}
    joint_directions = {"jac_top", "jac_null", "pc1", "centroid_dir", "rand_dir"}
    joint_filtered = [r for r in joint_rows if abs(float(r["scale_s"]) - 1.0) <= 1e-12
                      and (r["model_key"], int(r["depth"])) in joint_pairs]
    joint_keys = [(r["model_key"], int(r["depth"]), r["token_pattern"], r["feature_dir"])
                  for r in joint_filtered]
    joint_expected = {(model, depth, pattern, direction)
                      for model, depth in joint_pairs
                      for pattern in joint_patterns for direction in joint_directions}
    joint_grid_ok = (len(joint_filtered) == 240 and len(set(joint_keys)) == 240
                     and set(joint_keys) == joint_expected
                     and all(float(r["logit_l2"]) > 0 for r in joint_filtered))
    record("joint_stream_figures_match_all_240_audited_cells", joint_grid_ok,
           f"At scale_s=1.0: rows={len(joint_filtered)}, unique={len(set(joint_keys))}, expected=240; model-depth pairs={sorted(joint_pairs)}; all logit_l2 values positive for shared LogNorm={all(float(r['logit_l2']) > 0 for r in joint_filtered)}.")

    # Figure generation must be reproducible from the declared audited sources.
    main_figure_names = ["figure1_overview.svg", "figure2_depthwise.svg", "figure3_geometry_diversity.svg",
                         "figure4_anisotropic_geometry.svg", "figure5_value_path_cancellation.svg",
                         "figure6_joint_stream_geometry.svg", "figure7_end_to_end_operator.svg", "figure8_operator_compression.svg"]
    supplementary_figure_names = ["supp/figureS11_value_path_replication.svg",
                                  "supp/figureS12_primary_qkv_decomposition.svg",
                                  "supp/figureS13_real_carrier_boundary.svg", "supp/figureS14_joint_stream_geometry.svg",
                                  "supp/figureS15_regularization_sensitivity.svg"]
    figure_names = main_figure_names + supplementary_figure_names
    absent = [n for n in figure_names if not (FIGS/n).is_file()]
    absent_png = [n[:-4]+".png" for n in figure_names if not (FIGS/(n[:-4]+".png")).is_file()]
    stale_carrier_assets = [str(p.relative_to(FIGS)) for p in FIGS.rglob("figureS1_real_carrier_boundary.*")]
    script = ROOT/"scripts/build_paper_figures_v4.py"
    script_text = script.read_text(encoding="utf-8") if script.exists() else ""
    script_ok = ("fungibility_real_final/real_accuracy_throughput_frontier.csv" in script_text
                 and "figureS13_real_carrier_boundary" in script_text
                 and "figureS12_primary_qkv_decomposition" in script_text
                 and "figure6_joint_stream_geometry" in script_text
                 and "figure7_end_to_end_operator" in script_text
                 and "figure8_operator_compression" in script_text
                 and "figureS14_joint_stream_geometry" in script_text)
    sensitivity_figure_script = ROOT / "scripts/plot_regularization_sensitivity_manuscript.py"
    sensitivity_script_text = sensitivity_figure_script.read_text(encoding="utf-8") if sensitivity_figure_script.exists() else ""
    script_ok = script_ok and "aggregated_by_architecture_budget_factor.csv" in sensitivity_script_text and "figureS15_regularization_sensitivity.svg" in sensitivity_script_text
    sidecars = [FIGS/"FIGURE_MANIFEST.md", FIGS/"contact_sheet.png", DOCS/"PAPER_FIGURE_REVIEW_V4.md"]
    record("publication_figures_present_source_scoped_and_reviewed",
           not absent and not absent_png and not stale_carrier_assets and script_ok and all(p.is_file() for p in sidecars),
           f"Missing SVGs={absent}; missing PNGs={absent_png}; stale S1 carrier assets={stale_carrier_assets}; generator source checks={script_ok}; manifest/contact/review={[p.is_file() for p in sidecars]}.")

    docx_path = DOCX_PATH
    docx_ok = False
    if docx_path.is_file():
        try:
            with zipfile.ZipFile(docx_path) as archive:
                media = [name for name in archive.namelist() if name.startswith("word/media/")]
                document_xml = ET.fromstring(archive.read("word/document.xml"))
            drawings = sum(1 for node in document_xml.iter() if node.tag.endswith("}drawing"))
            docx_ok = len(media) == 8 and drawings == 8
        except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError):
            docx_ok = False
    record("main_docx_embeds_eight_reviewed_figures", docx_ok,
           "Main DOCX package contains exactly eight main-text figure drawings and eight embedded PNG assets; supplementary figures are kept in the separate supplement DOCX.")

    supplementary_docx_ok = False
    supp_drawings = supp_media = supp_tables = 0
    s4_present = s5_present = s6_present = False
    if SUPPLEMENTARY_DOCX.is_file():
        try:
            with zipfile.ZipFile(SUPPLEMENTARY_DOCX) as archive:
                supp_media = sum(1 for name in archive.namelist() if name.startswith("word/media/"))
                supp_xml = ET.fromstring(archive.read("word/document.xml"))
            supp_drawings = sum(1 for node in supp_xml.iter() if node.tag.endswith("}drawing"))
            supp_tables = sum(1 for node in supp_xml.iter() if node.tag.endswith("}tbl"))
            supp_doc_text = "".join(node.text or "" for node in supp_xml.iter() if node.tag.endswith("}t"))
            required_s4_values = ["Table S4.", "+0.006282993", "+0.004448350", "−0.247199488", "−0.252697120", "102.2%"]
            s4_present = all(value in supp_doc_text for value in required_s4_values)
            s5_present = all(value in supp_doc_text for value in
                             ["Table S5.", "764/1,000", "568/1,000", "76.4%", "56.8%"])
            s6_present = all(value in supp_doc_text for value in
                             ["Table S6.", "71.5", "61327", "within 0.5"])
            supplementary_docx_ok = (supp_media == 15 and supp_drawings == 15 and supp_tables == 8
                                     and s4_present and s5_present and s6_present)
        except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError):
            supplementary_docx_ok = False
    record("supplementary_docx_embeds_all_figures_and_tables", supplementary_docx_ok,
           f"Supplementary DOCX contains {supp_drawings} figure drawings/{supp_media} image assets and {supp_tables} table elements; required 15 figures and eight tables (evidence map, Tables S1–S6, and one display-equation layout), including verified S4/S5/S6 values={s4_present}/{s5_present}/{s6_present}.")

    # Confirm that the delivered Word files carry the post-hoc wording and table.
    main_doc_text = supp_doc_text = ""
    try:
        with zipfile.ZipFile(DOCX_PATH) as archive:
            main_xml = ET.fromstring(archive.read("word/document.xml"))
        with zipfile.ZipFile(SUPPLEMENTARY_DOCX) as archive:
            supplementary_xml = ET.fromstring(archive.read("word/document.xml"))
        main_w = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}t"
        main_doc_text = "".join(node.text or "" for node in main_xml.iter(main_w))
        supp_doc_text = "".join(node.text or "" for node in supplementary_xml.iter(main_w))
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError):
        pass
    main_docx_headings_ok = ("7. Limitations" in main_doc_text
                             and "8. Conclusion" in main_doc_text
                             and "7. From Operator-Aware Optimization to Practical Compression" not in main_doc_text
                             and "9. Conclusion" not in main_doc_text
                             and all(f"TABLE {label}" in main_doc_text for label in ("I", "II", "III", "IV"))
                             and "Practical carrier evaluation" not in main_doc_text)
    record("main_docx_has_separate_correct_limitations_and_conclusion_headings",
           main_docx_headings_ok,
           "Main Word export contains Sections 7 and 8 and all four current main-table labels, without the former practical-carrier section.")
    docx_sensitivity_ok = ("post-hoc sensitivity analysis" in main_doc_text.lower()
                           and "not as a demonstrated global optimum" in main_doc_text.lower()
                           and "fixed after a pilot sweep" not in main_doc_text.lower()
                           and "Regularization Sensitivity of Operator-Aware Carriers" in supp_doc_text
                           and all(value in supp_doc_text for value in ["Table S6.", "71.5", "61327"])
                           and all(value in supp_doc_text for value in ["Table S5.", "764/1,000", "568/1,000"]))
    record("sensitivity_word_exports_match_scientific_wording", docx_sensitivity_ok,
           f"Main DOCX contains corrected post-hoc wording and no unsupported historical pilot sentence; Supplementary DOCX contains S15/Table S6 and practical Table S5={docx_sensitivity_ok}.")

    # Reconcile the new post-hoc sensitivity claims to the corrected archived CSVs.
    sensitivity_root = ROOT / "outputs/fungibility_regularization_sensitivity_v2_class_randomized"
    aggregate_path = sensitivity_root / "aggregated_by_architecture_budget_factor.csv"
    sensitivity_rows = rows(aggregate_path) if aggregate_path.is_file() else []
    factor_rows = [r for r in sensitivity_rows if r.get("method") == "operator_aware"]
    gm_rows = {(r.get("model"), r.get("budget")): r for r in sensitivity_rows if r.get("method") == "group_mean"}
    cells: dict[tuple[str, str], dict[float, dict[str, str]]] = {}
    for row in factor_rows:
        cells.setdefault((row["model"], row["budget"]), {})[float(row["lambda_factor"])] = row
    within_half_pp = logit_better_than_gm = True
    for key, factors in cells.items():
        rates = {factor: float(row["top1_rate"]) for factor, row in factors.items()}
        maximum = max(rates.values())
        within_half_pp &= maximum - rates[10.0] <= 0.005 + 1e-12
        logit_better_than_gm &= float(factors[10.0]["mean_logit_l2_damage"]) < float(gm_rows[key]["mean_logit_l2_damage"])
    paired_path = sensitivity_root / "paired_factor10_vs_3_30.csv"
    paired_rows = rows(paired_path) if paired_path.is_file() else []
    top1_paired = [r for r in paired_rows if r.get("metric") == "compressed_correct"]
    no_significant_mcnemar = len(top1_paired) == 16 and all(float(r["top1_mcnemar_exact_p_unadjusted"]) >= 0.05 for r in top1_paired)
    sensitivity_texts = "\n".join(p.read_text(encoding="utf-8-sig") for p in
                                  (DRAFT, SUPPLEMENTARY_DRAFT, CLAIMS, TRACE) if p.is_file())
    max_count = sum(abs(float(values[10.0]["top1_rate"]) - max(float(r["top1_rate"]) for r in values.values())) < 1e-12
                    for values in cells.values())
    sensitivity_claims_ok = (len(cells) == 8 and len(factor_rows) == 56
                             and max_count == 5 and within_half_pp
                             and logit_better_than_gm and no_significant_mcnemar
                             and "post-hoc" in sensitivity_texts.lower()
                             and "not a demonstrated global optimum" in sensitivity_texts.lower()
                             and "Table S6" in sensitivity_texts and "Figure S15" in sensitivity_texts)
    record("corrected_sensitivity_manuscript_claims_match_v2_csvs", sensitivity_claims_ok,
           f"Corrected cells={len(cells)}; factor rows={len(factor_rows)}; factor 10 at/tied max={max_count}/8; within 0.5 pp all cells={within_half_pp}; logit damage below Group Mean all cells={logit_better_than_gm}; 16 paired McNemar contrasts p>=.05={no_significant_mcnemar}.")

    # Traceability matrix covers every numeric claim family carried into the draft.
    tr = TRACE.read_text(encoding="utf-8-sig") if TRACE.exists() else ""
    claim_families = ["+4.2 to +12.0", "+4.2 to +17.4", "4 exceed 98% and 18 do not", "54.91%", "0.7079985", ".974717", "1.473962", "76.4/76.3/76.0", "0.784"]
    absent_families = [v for v in claim_families if v not in tr]
    record("quantitative_claims_traceable", not absent_families,
           f"Numeric evidence families absent from traceability map: {absent_families}.")

    # Reconcile the added same-group operator-space claim against image-level source rows.
    same_group_rows = rows(ROOT / "outputs/fungibility_operator_compression_confirmatory/same_group_ablation.csv")
    expected_delta = {"DeiT-Tiny": 1.2734326491, "DeiT-Small": 1.4813734684,
                      "ViT-B/16": 2.5278027144, "DINOv2 ViT-S/14": 7.2039423407}
    same_group_primary = [r for r in same_group_rows if r["grouping"] == "feature_similarity"]
    same_group_ok = len(same_group_primary) == 20000 and all(float(r["delta_op_residual"]) > 0 for r in same_group_primary)
    same_group_details = {}
    for model, expected in expected_delta.items():
        model_rows = [r for r in same_group_primary if r["model"] == model]
        budgets = sorted({int(r["budget"]) for r in model_rows})
        budget_counts = [sum(int(r["budget"]) == b for r in model_rows) for b in budgets]
        mean_delta = sum(float(r["delta_op_residual"]) for r in model_rows) / len(model_rows) if model_rows else float("nan")
        same_group_details[model] = {"rows": len(model_rows), "budgets": budgets, "n_per_budget": budget_counts, "mean_delta": mean_delta}
        same_group_ok = same_group_ok and len(model_rows) == 5000 and len(budgets) == 5 and budget_counts == [1000] * 5 and abs(mean_delta - expected) < 1e-8
    record("same_group_operator_residual_claim_matches_csv", same_group_ok,
           f"Primary feature-similarity rows={len(same_group_primary)}; per-architecture counts and five-budget means={same_group_details}; all deltas positive={all(float(r['delta_op_residual']) > 0 for r in same_group_primary)}.")


    # Complete bibliography, acronym, callout, equation, and numeric consistency gates.
    try:
        bib_block, bib_entries = exporter.bibliography(text)
        first_cite_order = exporter.cited_order(text, bib_entries)
        bib_order = [key for key, _ in bib_entries]
        bib_fields = dict(bib_entries)
        external_bib_path = DOCS / "PAPER_REFERENCES.bib"
        external_bib = external_bib_path.read_text(encoding="utf-8-sig") if external_bib_path.exists() else ""
        complete = all(v.get("author") and v.get("title") and v.get("year") and
                       (v.get("booktitle") or v.get("journal") or
                        (v.get("archiveprefix", "").lower() == "arxiv" and v.get("eprint")))
                       and (v.get("doi") or v.get("url"))
                       for _, v in bib_entries)
        norm_titles = [re.sub(r"[^a-z0-9]+", "", exporter.clean_tex(v.get("title", "")).lower())
                       for _, v in bib_entries]
        dois = [v.get("doi", "").strip().lower() for _, v in bib_entries if v.get("doi", "").strip()]
        record("bibliography_has_55_complete_unique_records",
               len(bib_entries) == 55 and complete and len(set(norm_titles)) == len(norm_titles) and len(set(dois)) == len(dois),
               f"Entries={len(bib_entries)}; complete fields={complete}; duplicate normalized titles={len(norm_titles)-len(set(norm_titles))}; duplicate DOIs={len(dois)-len(set(dois))}.")
        related_work = text.split("## 2. Related Work", 1)[1].split("## 3. Experimental Setup", 1)[0] if "## 2. Related Work" in text and "## 3. Experimental Setup" in text else ""
        new_prior_art_ok = (
            "\\citep{bond2026taskinduced}" in related_work
            and "\\citep{liu2025approxnullspace}" in related_work
            and "preprint" not in " ".join((bib_fields.get("bond2026taskinduced", {}).get("booktitle", ""), bib_fields.get("bond2026taskinduced", {}).get("journal", ""))).lower()
            and bib_fields.get("bond2026taskinduced", {}).get("eprint") == "2609.27988"
            and bib_fields.get("bond2026taskinduced", {}).get("archiveprefix", "").lower() == "arxiv"
            and bib_fields.get("liu2025approxnullspace", {}).get("booktitle") == "Conference on Parsimony and Learning"
            and bib_fields.get("liu2025approxnullspace", {}).get("volume") == "280"
            and bib_fields.get("liu2025approxnullspace", {}).get("pages") == "1--23"
            and all(key in related_work for key in ("fixed-slot interventions", "task-aware token compression", "approximate-nullspace analysis")))
        record("bond_and_liu_prior_art_are_cited_with_verified_types_and_distinctions",
               new_prior_art_ok,
               f"Related Work citations, Bond arXiv metadata and Liu PMLR 280:1–23 metadata/distinctions valid={new_prior_art_ok}.")
        record("bibliography_numbering_matches_first_citation_and_sidecar",
               bib_order == first_cite_order and bib_block.group(1).strip() == external_bib.strip(),
               f"First-citation ordering={bib_order == first_cite_order}; external BibTeX synchronized={bib_block.group(1).strip() == external_bib.strip()}.")
    except (ValueError, OSError, IndexError) as exc:
        bib_entries, bib_fields, first_cite_order = [], {}, []
        record("bibliography_has_55_complete_unique_records", False, f"Could not parse or validate bibliography: {exc}")
        record("bond_and_liu_prior_art_are_cited_with_verified_types_and_distinctions", False,
               "Could not parse or validate the Bond/Liu bibliography records and Related Work citations.")
        record("bibliography_numbering_matches_first_citation_and_sidecar", False, "Bibliography parser or sidecar check failed.")


    # Check IEEE citation clusters and confirm their numbering/ranges in the exported DOCX.
    try:
        key_to_num = {key: i for i, key in enumerate(first_cite_order, start=1)}
        source_tokens = []
        cluster_issues = []
        cite_matches = list(re.finditer(r"\\citep\{([^}]+)\}", text))
        for match in cite_matches:
            keys = [part.strip() for part in match.group(1).split(",")]
            unknown = [key for key in keys if key not in key_to_num]
            if unknown:
                cluster_issues.append((keys, f"unknown keys {unknown}"))
                continue
            numbers = [key_to_num[key] for key in keys]
            if numbers != sorted(set(numbers)):
                cluster_issues.append((keys, f"numbers {numbers} are not strictly ascending and unique"))
            if len(numbers) >= 3 and numbers == list(range(numbers[0], numbers[0] + len(numbers))):
                source_tokens.append((numbers[0], numbers[-1]))
            else:
                source_tokens.extend((number, None) for number in numbers)

        actual_tokens = []
        found_reference_heading = False
        if docx_path.is_file():
            with zipfile.ZipFile(docx_path) as archive:
                citation_xml = ET.fromstring(archive.read("word/document.xml"))
            word_ns = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
            body_paragraphs = []
            for paragraph in citation_xml.iter(word_ns + "p"):
                paragraph_text = "".join(node.text or "" for node in paragraph.iter(word_ns + "t"))
                if paragraph_text.strip().casefold() == "references":
                    found_reference_heading = True
                    break
                body_paragraphs.append(paragraph_text)
            rendered_body = "\n".join(body_paragraphs)
            actual_tokens = [(int(start), int(end) if end else None)
                             for start, end in re.findall(r"\[(\d+)\](?:–\[(\d+)\])?", rendered_body)]
        ieee_citations_ok = bool(cite_matches) and not cluster_issues and found_reference_heading and source_tokens == actual_tokens
        range_count = sum(end is not None for _, end in actual_tokens)
        record("ieee_citation_order_and_ranges_match_docx",
               ieee_citations_ok,
               f"Citation clusters={len(cite_matches)}; ordering issues={cluster_issues}; reference heading found={found_reference_heading}; source/rendered tokens={len(source_tokens)}/{len(actual_tokens)}; ranges={range_count}; exact match={source_tokens == actual_tokens}.")
    except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError, ValueError) as exc:
        record("ieee_citation_order_and_ranges_match_docx", False, f"Could not validate IEEE citation sequence and ranges: {exc}")

    abstract = text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0] if "## Abstract" in text and "## 1. Introduction" in text else ""
    abstract_acronyms = re.findall(r"\b(?:ViTs?|LLMs?|PCF|SVD|PCA|AUROC)\b", abstract)
    record("abstract_uses_no_defined_abbreviations", not abstract_acronyms,
           f"Acronym tokens in Abstract: {sorted(set(abstract_acronyms))}.")
    body = text.split("## 1. Introduction", 1)[1].split("## References", 1)[0] if "## 1. Introduction" in text else text
    definitions = [("ViTs", r"vision transformers?\s+\(ViTs\)"),
                   ("PCF", r"Patch-Content Fungibility\s+\(PCF\)"),
                   ("LLMs", r"large language models\s+\(LLMs\)"),
                   ("PCA", r"principal component analysis\s+\(PCA\)"),
                   ("SVD", r"singular value decomposition\s+\(SVD\)")]
    acronym_issues = []
    for acronym, definition in definitions:
        d = re.search(definition, body, re.I)
        a = re.search(rf"\b{acronym}\b", body)
        if not d or not a or d.start() > a.start():
            acronym_issues.append(acronym)
    record("main_text_defines_abbreviations_at_first_use", not acronym_issues,
           f"Missing or late definitions: {acronym_issues}.")

    # Every figure/table callout must resolve to the numbered object and precede its placement.
    lines = text.splitlines()
    main_sections = [(int(m.group(1)), m.group(2))
                     for line in lines
                     if (m := re.match(r"^##\s+(\d+)\.\s+(.+)$", line.strip()))]
    section_structure_ok = ([number for number, _ in main_sections] == list(range(1, 9))
                            and main_sections[-2:] == [(7, "Limitations"), (8, "Conclusion")]
                            and "From Operator-Aware Optimization to Practical Compression" not in text)
    record("main_sections_run_from_operator_compression_to_limitations_and_conclusion",
           section_structure_ok,
           f"Numbered headings={main_sections}; expected Sections 1–8 ending in Limitations and Conclusion, with no standalone practical-carrier section.")
    fig_objects = [(i, m.group(1)) for i, line in enumerate(lines) if (m := re.match(r"!\[Figure\s+(S?\d+)", line.strip()))]
    fig_captions = [(i, m.group(1)) for i, line in enumerate(lines) if (m := re.match(r"\*Figure\s*(S?\d+)\.", line.strip()))]
    table_headings = [(i, m.group(1)) for i, line in enumerate(lines) if (m := re.match(r"\*\*TABLE\s+([IVX]+)\*\*", line.strip()))]
    # This manuscript uses IEEE-style uppercase table labels followed by a bold uppercase title.
    table_captions = []
    for i, line in enumerate(lines):
        heading = re.match(r"\*\*TABLE\s+([IVX]+)\*\*", line.strip())
        if not heading:
            continue
        title_i = next((j for j in range(i + 1, len(lines)) if lines[j].strip()), None)
        if title_i is not None and re.fullmatch(r"\*\*[^*].*[^*]\*\*", lines[title_i].strip()):
            table_captions.append((title_i, heading.group(1)))
    figure_callouts = {}
    table_callouts = {}
    for i, line in enumerate(lines):
        if line.strip().startswith(("![", "*Figure", "**TABLE", "*Table ")):
            continue
        for m in re.finditer(r"\bFigure\s+(S?\d+)\b", line):
            figure_callouts.setdefault(m.group(1), i)
        for m in re.finditer(r"\bTable\s+([IVX]+)\b", line, re.I):
            table_callouts.setdefault(m.group(1).upper(), i)
    fig_labels = [label for _, label in fig_objects]
    cap_labels = [label for _, label in fig_captions]
    fig_order_ok = fig_labels == cap_labels and len(fig_labels) == 8 and len(set(fig_labels)) == 8
    fig_placement_ok = all(label in figure_callouts and figure_callouts[label] < pos for pos, label in fig_objects)
    table_labels = [label for _, label in table_headings]
    table_cap_labels = [label for _, label in table_captions]
    table_order_ok = table_labels == table_cap_labels == ["I", "II", "III", "IV"]
    table_placement_ok = all(label in table_callouts and table_callouts[label] < pos for pos, label in table_headings)
    resolved_figs = set(re.findall(r"\bFigure\s+(S?\d+)\b", text))
    resolved_tables = set(m.group(1).upper() for m in re.finditer(r"\bTable\s+([IVX]+)\b", text, re.I))

    # Supplementary callouts resolve against the separate supplementary manuscript and DOCX.
    supplementary_path = SUPPLEMENTARY_DRAFT
    supplementary_text = supplementary_path.read_text(encoding="utf-8-sig") if supplementary_path.is_file() else ""
    auroc_definition = re.search(
        r"area under the receiver operating characteristic curve\s+\(AUROC\)",
        supplementary_text,
        re.I,
    )
    auroc_first_use = re.search(r"\bAUROC\b", supplementary_text)
    record("supplementary_AUROC_defined_at_first_use",
           bool(auroc_definition and auroc_first_use and auroc_definition.start() <= auroc_first_use.start()),
           "AUROC is expanded at or before its first use in the supplementary manuscript, where the operator-space result now appears.")
    supplementary_lines = supplementary_text.splitlines()
    supplementary_table_captions = [
        (i, m.group(1).upper())
        for i, line in enumerate(supplementary_lines)
        if (m := re.match(r"^\*\*Table\s+(S\d+)\.", line.strip()))
    ]
    supplementary_table_labels = [label for _, label in supplementary_table_captions]
    expected_supplementary_tables = [f"S{i}" for i in range(1, 7)]
    supplementary_table_callouts = {}
    caption_lines = {i for i, _ in supplementary_table_captions}
    for i, line in enumerate(supplementary_lines):
        if i in caption_lines:
            continue
        for match in re.finditer(r"\bTable\s+(S\d+)\b", line):
            supplementary_table_callouts.setdefault(match.group(1).upper(), i)
    supplementary_table_numbering_ok = (
        supplementary_table_labels == expected_supplementary_tables
        and len(set(supplementary_table_labels)) == 6
        and all(label in supplementary_table_callouts
                and supplementary_table_callouts[label] < next(pos for pos, value in supplementary_table_captions
                                                                 if value == label)
                for label in ("S5", "S6"))
    )
    record("supplementary_table_numbering_unique_first_appearance_and_callouts_resolve",
           supplementary_table_numbering_ok,
           f"Caption order={supplementary_table_labels}; expected S1–S6 once each; Table S5/S6 callouts precede their captions.")
    supplementary_objects = {}
    for i, line in enumerate(supplementary_lines):
        match = re.match(r"!\[Supplementary Figure\s+(S?\d+)[^]]*\]\(([^)]+)\)", line.strip())
        if match:
            supplementary_objects.setdefault(match.group(1), []).append((i, match.group(2)))
    supplementary_captions = {}
    for i, line in enumerate(supplementary_lines):
        match = re.match(r"\*\*Supplementary Figure\s+(S?\d+)\.", line.strip())
        if match:
            supplementary_captions.setdefault(match.group(1), []).append(i)
    supplementary_refs = resolved_figs - set(fig_labels)
    supplementary_refs_ok = True
    for label in supplementary_refs:
        objects = supplementary_objects.get(label, [])
        captions = supplementary_captions.get(label, [])
        if len(objects) != 1 or len(captions) != 1 or objects[0][0] >= captions[0]:
            supplementary_refs_ok = False
            continue
        target = (DOCS / objects[0][1]).resolve()
        if not target.is_file():
            supplementary_refs_ok = False
    supplementary_labels = sorted(supplementary_objects, key=lambda value: int(value.lstrip("S")))
    expected_supplementary_labels = [f"S{i}" for i in range(1, 16)]
    supplementary_numbering_ok = (supplementary_labels == expected_supplementary_labels
                                  and all(len(supplementary_objects[label]) == 1
                                          and len(supplementary_captions.get(label, [])) == 1
                                          for label in expected_supplementary_labels)
                                  and "figureS1_real_carrier_boundary" not in supplementary_text
                                  and "figureS13_real_carrier_boundary.svg" in supplementary_text
                                  and "figureS14_joint_stream_geometry.svg" in supplementary_text
                                  and "figureS15_regularization_sensitivity.svg" in supplementary_text)
    resolved_figures_ok = resolved_figs == set(fig_labels) | supplementary_refs and supplementary_refs_ok
    record("figure_cross_references_resolve_and_precede_objects", fig_order_ok and fig_placement_ok and resolved_figures_ok and supplementary_numbering_ok,
           f"Main figure objects={fig_labels}; captions={cap_labels}; callouts={sorted(resolved_figs)}; supplementary callouts={sorted(supplementary_refs)}; supplement labels={supplementary_labels}; object/caption/path resolution={supplementary_refs_ok}; placement={fig_placement_ok}; unique S1–S15 numbering={supplementary_numbering_ok}.")
    record("table_cross_references_resolve_and_precede_objects", table_order_ok and table_placement_ok and resolved_tables == set(table_labels),
           f"Table headings={table_labels}; captions={table_cap_labels}; callouts={sorted(resolved_tables)}; placement={table_placement_ok}.")
    table_i = markdown_table(text, "I")
    table_i_ok = len(table_i) == 6 and all(len(row) == 4 for row in table_i) and "Practical carrier evaluation" not in text
    record("main_table_I_excludes_relocated_practical_carrier_row",
           table_i_ok,
           f"Table I rows including header={len(table_i)}; expected six rows and no practical-carrier row.")

    # Recompute the controlled-replacement effect sizes in Table II from the archived runs.
    table2_effects = markdown_table(text, "II")
    expected_table2_headers = ["Architecture", "Centroid − coordinate-permuted (50%)", "Centroid − sign-inverted (50%)",
                               "Grouped Kmax − K1", "PC1 − random 1D (100%)"]
    geometry_effects: dict[str, tuple[float, float]] = {}
    grouped_effects: dict[str, float] = {}
    direction_effects: dict[str, float] = {}
    seed_design_ok = True

    for model_key, arch in (("deit_tiny_patch16_224", "DeiT-Tiny"),
                            ("deit_small_patch16_224", "DeiT-Small")):
        stem = "tiny" if arch == "DeiT-Tiny" else "small"
        summary_rows = rows(ROOT / f"outputs/fungibility_v0_7/{stem}_fraction_summary.csv")
        prototype_rows = rows(ROOT / f"outputs/fungibility_v0_7/{stem}_prototype_comparison.csv")
        sign_rows = rows(ROOT / f"outputs/fungibility_v0_7/{stem}_sign_flip_sweep.csv")
        summary_row = source_value(summary_rows, model=model_key, fraction="50%")
        perm_rows = [r for r in prototype_rows if r.get("model") == model_key and r.get("fraction") == "50%"
                     and r.get("family") == "coord_perm" and r.get("control", "").startswith("coord_perm_seed_")]
        sign_row = source_value(sign_rows, model=model_key, fraction="50%", flip_condition="sign_flip_100%")
        if summary_row and len(perm_rows) == 3 and sign_row and len({r["control"] for r in perm_rows}) == 3:
            centroid = float(summary_row["mu8_acc"])
            permuted = sum(float(r["acc_control"]) for r in perm_rows) / len(perm_rows)
            inverted = float(sign_row["accuracy"])
            geometry_effects[arch] = (100 * (centroid - permuted), 100 * (centroid - inverted))
        else:
            seed_design_ok = False

        grouped_rows = rows(ROOT / "outputs/fungibility_v0_8/grouped_diversity_results.csv")
        low = [r for r in grouped_rows if r.get("model") == model_key and r.get("k") == "1"]
        high = [r for r in grouped_rows if r.get("model") == model_key and r.get("k") == "196"]
        if len(low) == len(high) == 3 and len({r["seed"] for r in low}) == len({r["seed"] for r in high}) == 3:
            grouped_effects[arch] = 100 * (sum(float(r["accuracy"]) for r in high) / 3
                                           - sum(float(r["accuracy"]) for r in low) / 3)
        else:
            seed_design_ok = False

        pc_rows = rows(ROOT / "outputs/fungibility_v0_9/pc_identity_results.csv")
        random_rows = rows(ROOT / "outputs/fungibility_v0_9/random_direction_results.csv")
        natural = [r for r in pc_rows if r.get("model") == model_key and r.get("condition_type") == "natural" and r.get("pc_index") == "1"]
        random = [r for r in random_rows if r.get("model") == model_key and r.get("condition", "").startswith("random_1d_seed_")]
        if len(natural) == len(random) == 5 and len({r["seed"] for r in natural}) == len({r["seed"] for r in random}) == 5:
            direction_effects[arch] = 100 * (sum(float(r["accuracy"]) for r in natural) / 5
                                              - sum(float(r["accuracy"]) for r in random) / 5)
        else:
            seed_design_ok = False

    v1_geometry: dict[str, list[dict[str, str]]] = {}
    for arch, stem in (("ViT-B/16 AugReg", "vitb"), ("DINOv2 ViT-S/14", "dinov2")):
        source_rows = rows(ROOT / f"outputs/fungibility_v1/{stem}_geometry_results.csv")
        selected = [r for r in source_rows if abs(float(r.get("fraction", "-1")) - 0.5) < 1e-12]
        centroid_rows = [r for r in selected if r.get("condition") == "CENTROID"]
        perm_rows = [r for r in selected if r.get("condition") == "COORDINATE_PERMUTED_CENTROID"]
        sign_rows = [r for r in selected if r.get("condition") == "SIGN_FLIPPED_CENTROID"]
        if len(centroid_rows) == len(sign_rows) == 1 and len(perm_rows) == 3 and len({r["seed"] for r in perm_rows}) == 3:
            centroid = float(centroid_rows[0]["top1_accuracy"])
            permuted = sum(float(r["top1_accuracy"]) for r in perm_rows) / 3
            inverted = float(sign_rows[0]["top1_accuracy"])
            geometry_effects[arch] = (100 * (centroid - permuted), 100 * (centroid - inverted))
        else:
            seed_design_ok = False
        grouped_source = rows(ROOT / "outputs/fungibility_v1_grouped_diversity_extension/aggregate_results.csv")
        model = "vitb" if stem == "vitb" else "dinov2"
        kmax = "196" if stem == "vitb" else "256"
        low = source_value(grouped_source, model=model, k="1")
        high = source_value(grouped_source, model=model, k=kmax)
        if low and high and low.get("n_seeds") == high.get("n_seeds") == "5" and low.get("n_eval_images_per_seed") == high.get("n_eval_images_per_seed") == "1000":
            grouped_effects[arch] = 100 * (float(high["top1_accuracy_mean"]) - float(low["top1_accuracy_mean"]))
        else:
            seed_design_ok = False
        direction_source = rows(ROOT / f"outputs/fungibility_v1/{stem}_1d_results.csv")
        natural = [r for r in direction_source if r.get("condition") == "NATURAL_PC1"]
        random = [r for r in direction_source if r.get("condition") == "RANDOM_1D"]
        if len(natural) == len(random) == 3 and len({r["seed"] for r in natural}) == len({r["seed"] for r in random}) == 3:
            direction_effects[arch] = 100 * (sum(float(r["top1_accuracy"]) for r in natural) / 3
                                              - sum(float(r["top1_accuracy"]) for r in random) / 3)
        else:
            seed_design_ok = False

    effect_values = {}
    effect_tolerances = {}
    parsed_table2 = (len(table2_effects) == 5 and table2_effects[0] == expected_table2_headers
                     and [r[0] for r in table2_effects[1:]] == ["DeiT-Tiny", "DeiT-Small", "ViT-B/16 AugReg", "DINOv2 ViT-S/14"])
    if parsed_table2:
        for row in table2_effects[1:]:
            try:
                raw_values = [re.search(r"[+−-]?\d+(?:\.\d+)?", cell).group(0) for cell in row[1:]]
                values = [float(value.replace("−", "-")) for value in raw_values]
                tolerances = [0.5 * 10 ** (-len(value.partition(".")[2])) + 1e-6
                              for value in raw_values]
            except (AttributeError, ValueError):
                parsed_table2 = False
                break
            effect_values[row[0]] = values
            effect_tolerances[row[0]] = tolerances
    table2_match = parsed_table2 and seed_design_ok and set(geometry_effects) == set(grouped_effects) == set(direction_effects) == {
        "DeiT-Tiny", "DeiT-Small", "ViT-B/16 AugReg", "DINOv2 ViT-S/14"}
    if table2_match:
        for arch, values in effect_values.items():
            sourced = [*geometry_effects[arch], grouped_effects[arch], direction_effects[arch]]
            signs_match = all(reported == 0 or source == 0 or math.copysign(1, reported) == math.copysign(1, source)
                              for reported, source in zip(values, sourced))
            rounding_matches = all(abs(reported - source) <= tolerance
                                   for reported, source, tolerance in zip(values, sourced, effect_tolerances[arch]))
            table2_match = table2_match and signs_match and rounding_matches
    table2_note = text.split("**CONTROLLED PATCH-CONTENT REPLACEMENT EFFECTS ACROSS ARCHITECTURES**", 1)[1].split("**TABLE III**", 1)[0] if "**CONTROLLED PATCH-CONTENT REPLACEMENT EFFECTS ACROSS ARCHITECTURES**" in text and "**TABLE III**" in text else ""
    table2_note_ok = all(token in table2_note for token in ("percentage points", "Note (Table II)", "50%", "all spatial patches", "N=1,000 held-out images",
                                                             "disjoint", "three-seed means", "five seeds", "not meaningful accuracy recovery"))
    record("table_II_controlled_replacement_effects_recompute_from_archived_runs",
           bool(table2_match and table2_note_ok),
           f"Table II source effects in pp={effect_values}; geometry/grouped-K/PC-direction seed designs valid={seed_design_ok}; protocol/cohort/floor notes valid={table2_note_ok}.")

    # Recompute depth-5/depth-10 functional spectra and depth-8 directional ratios for Table III.
    table3 = markdown_table(text, "III")
    spectrum_rows = rows(ROOT / "outputs/fungibility_section5_cross_arch_extension/functional_geometry/functional_spectrum_robustness.csv")
    direction_rows = rows(ROOT / "outputs/fungibility_section5_cross_arch_extension/functional_geometry/pc_directional_sensitivity.csv")
    expected_architectures = ["DeiT-Tiny", "DeiT-Small", "ViT-B/16 AugReg", "DINOv2 ViT-S/14"]
    table3_headers = ["Architecture", "Normalized effective rank, d5 → d10", "Near-null fraction, d5 → d10", "PC1 / PCbottom sensitivity ratio, d8"]
    table3_ok = (len(table3) == 5 and table3[0] == table3_headers
                 and [r[0] for r in table3[1:]] == expected_architectures)
    spectrum_summary = {}
    for arch in expected_architectures:
        selected = [r for r in spectrum_rows if r.get("architecture") == arch
                    and abs(float(r.get("relative_cutoff", "-1")) - 1e-3) < 1e-12
                    and int(r.get("depth", -1)) in (5, 10)]
        d5 = [r for r in selected if int(r["depth"]) == 5]
        d10 = [r for r in selected if int(r["depth"]) == 10]
        ratio_rows = [r for r in direction_rows if r.get("architecture") == arch and int(r.get("depth", -1)) == 8]
        if len(d5) == len(d10) == len(ratio_rows) == 1:
            spectrum_summary[arch] = (float(d5[0]["effective_rank_over_D"]), float(d10[0]["effective_rank_over_D"]),
                                      100 * float(d5[0]["near_null_fraction"]), 100 * float(d10[0]["near_null_fraction"]),
                                      float(ratio_rows[0]["ratio_PC1_to_PC_bottom_raw"]))
            table3_ok = table3_ok and d5[0]["N_img"] == d10[0]["N_img"] == "100"
            table3_ok = table3_ok and ratio_rows[0]["ratio_numerically_stable"].lower() == "true"
        else:
            table3_ok = False
    if table3_ok:
        for row in table3[1:]:
            values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", row[1])]
            near = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", row[2])]
            ratio_text = row[3].replace("†", "").strip()
            actual = spectrum_summary[row[0]]
            table3_ok = table3_ok and len(values) == len(near) == 2
            if len(values) == len(near) == 2:
                table3_ok = table3_ok and abs(values[0] - actual[0]) <= 0.00051 and abs(values[1] - actual[1]) <= 0.00051
                table3_ok = table3_ok and abs(near[0] - actual[2]) <= 0.0051 and abs(near[1] - actual[3]) <= 0.0051
            table3_ok = table3_ok and abs(float(ratio_text) - actual[4]) <= (0.051 if row[0] == "ViT-B/16 AugReg" else 0.00051)
    table3_note = text.split("**DEPTH EVOLUTION OF FUNCTIONAL SENSITIVITY ACROSS ARCHITECTURES**", 1)[1].split("### 5.2", 1)[0] if "**DEPTH EVOLUTION OF FUNCTIONAL SENSITIVITY ACROSS ARCHITECTURES**" in text and "### 5.2" in text else ""
    table3_note_ok = all(token.lower() in table3_note.lower() for token in (
        "uncentered second moment", "N=100 calibration images/model", "aggregated within images",
        "distinct from the full token-by-feature", "operational cutoff", "small at the primary threshold",
        "feature dimension D", "sensitive to a small depth-8 activation-covariance eigengap",
        "not a universal ranking", "Supplementary Table S2"))
    record("table_III_functional_geometry_recompute_from_corrected_outputs",
           bool(table3_ok and table3_note_ok),
           f"Table III source metrics={spectrum_summary}; corrected rows use N=100 and stable directional diagnostics; scope note valid={table3_note_ok}.")

    # Independently recompute Figure 7 correlations and bootstrap intervals from the fixed perturbation cohort.
    multi_root = ROOT / "outputs/fungibility_section5_cross_arch_extension/multiblock_prediction"
    perturbation_rows = rows(multi_root / "per_perturbation_results.csv")
    correlation_rows = rows(multi_root / "model_specific_correlations.csv")
    bootstrap_rows = rows(multi_root / "stratified_bootstrap_correlations.csv")
    within_rows = rows(multi_root / "within_family_correlations.csv")
    manifest_path = multi_root / "validation_manifest.json"
    multi_manifest = json.loads(manifest_path.read_text(encoding="utf-8-sig")) if manifest_path.exists() else {}
    family_names = {"top_end_to_end_modes", "middle_end_to_end_modes", "end_to_end_null_modes", "isotropic_gaussian_controls"}
    figure7_ok = len(correlation_rows) == 8 and len(within_rows) == 32 and len(bootstrap_rows) == 16000
    figure7_details = []
    for model in ("deit_tiny", "deit_small", "vit_base", "dinov2"):
        model_rows = [r for r in perturbation_rows if r.get("model_key") == model]
        families = {name: sum(r.get("perturbation_family") == name for r in model_rows) for name in family_names}
        ids = {r.get("pert_id") for r in model_rows}
        figure7_ok = figure7_ok and len(model_rows) == 100 and len(ids) == 100 and set(families.values()) == {25}
        figure7_ok = figure7_ok and all(r.get("depth") == "8" and r.get("n_reference_images") == "20"
                                        and abs(float(r.get("scale_factor", "nan")) - 0.4) < 1e-12
                                        and r.get("linearization_image_global_index") == "29" for r in model_rows)
        for predictor, xfield in (("single_block", "predicted_tau_single"), ("end_to_end", "predicted_tau_multi")):
            xs = [float(r[xfield]) for r in model_rows]
            ys = [float(r["logit_l2"]) for r in model_rows]
            recalc_r = pearson(xs, ys)
            recalc_rho = pearson(average_ranks(xs), average_ranks(ys))
            saved = source_value(correlation_rows, model_key=model, predictor=predictor)
            boots = [r for r in bootstrap_rows if r.get("model_key") == model and r.get("predictor") == predictor]
            if not saved or len(boots) != 2000:
                figure7_ok = False
                continue
            pearson_ci = (percentile([float(r["pearson_r"]) for r in boots], 0.025),
                          percentile([float(r["pearson_r"]) for r in boots], 0.975))
            spearman_ci = (percentile([float(r["spearman_rho"]) for r in boots], 0.025),
                           percentile([float(r["spearman_rho"]) for r in boots], 0.975))
            figure7_ok = figure7_ok and abs(recalc_r - float(saved["pearson_r"])) < 1e-10
            figure7_ok = figure7_ok and abs(recalc_rho - float(saved["spearman_rho"])) < 1e-10
            figure7_ok = figure7_ok and max(abs(a - float(b)) for a, b in zip(pearson_ci, (saved["pearson_ci95_low"], saved["pearson_ci95_high"]))) < 1e-10
            figure7_ok = figure7_ok and max(abs(a - float(b)) for a, b in zip(spearman_ci, (saved["spearman_ci95_low"], saved["spearman_ci95_high"]))) < 1e-10
            figure7_details.append((model, predictor, recalc_r, recalc_rho, pearson_ci, spearman_ci))
    s3_rows = supplementary_markdown_table(supplementary_text, "S3")
    s3_ok = len(s3_rows) == 9
    model_labels = {"DeiT-Tiny":"deit_tiny", "DeiT-Small":"deit_small",
                    "ViT-B/16 AugReg":"vit_base", "DINOv2 ViT-S/14":"dinov2"}
    for row in s3_rows[1:]:
        if len(row) != 4:
            s3_ok = False
            continue
        model = model_labels.get(row[0])
        predictor = "single_block" if row[1].startswith("Single-block") else "end_to_end" if row[1].startswith("End-to-end") else None
        saved = source_value(correlation_rows, model_key=model, predictor=predictor) if model and predictor else None
        values = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", row[2])]
        ranks = [float(x) for x in re.findall(r"\d+(?:\.\d+)?", row[3])]
        if not saved or len(values) != 3 or len(ranks) != 3:
            s3_ok = False
            continue
        expected = [float(saved["pearson_r"]), float(saved["pearson_ci95_low"]), float(saved["pearson_ci95_high"])]
        expected_ranks = [float(saved["spearman_rho"]), float(saved["spearman_ci95_low"]), float(saved["spearman_ci95_high"])]
        s3_ok = s3_ok and all(abs(a - b) <= 0.00051 for a, b in zip(values, expected))
        s3_ok = s3_ok and all(abs(a - b) <= 0.00051 for a, b in zip(ranks, expected_ranks))
    scope_text = text.split("**Predictive validation.**", 1)[1].split("**Directional transmission contrast.**", 1)[0] if "**Predictive validation.**" in text and "**Directional transmission contrast.**" in text else ""
    scope_ok = all(phrase.lower() in scope_text.lower() for phrase in (
        "100 designed perturbation vectors per architecture", "25 vectors from each of four families",
        "fixed 20-image reference batch", "perturbation vector—not an image or token",
        "averages over the 20-image reference batch", "is linearized at its first image",
        "not general superiority over arbitrary perturbations or independent image batches"))
    manifest_ok = (multi_manifest.get("status") == "PASS"
                   and all(info.get("N_perturbations") == 100 and info.get("N_reference_images") == 20
                           and info.get("scale_s") == 0.4 and info.get("linearization_image_global_index") == 29
                           for info in multi_manifest.get("models", {}).values())
                   and multi_manifest.get("bootstrap", {}).get("replicates") == 2000
                   and multi_manifest.get("bootstrap", {}).get("seed") == 52026)
    record("figure_7_correlations_bootstrap_and_scope_match_prescribed_mixture",
           bool(figure7_ok and s3_ok and scope_ok and manifest_ok),
           f"Recomputed 8 model/operator correlations and 2,000-stratified-bootstrap intervals match source; Table S3 rounded values={s3_ok}; 4×25 perturbation families, 20-image reference, first-image J linearization, and bounded wording valid={scope_ok and manifest_ok}; within-family rows={len(within_rows)}; results={figure7_details}.")

    equation_blocks = text.count("$$") // 2
    equation_tags = re.findall(r"\\tag\{(\d+)\}", text)
    equation_explanation_text = re.sub(r"<sub>(.*?)</sub>", r"_\1", text, flags=re.IGNORECASE)
    equation_explanations = all(s.lower() in equation_explanation_text.lower() for s in (
        "n_img denotes the number of image samples", "uncentered second moment of scalar margin gradients",
        "pre-output-projection head context", "row-major order", "pre-classifier readout vector",
        "d_u=2D", "excluding the linear classification head",
        "positive-semidefinite gram matrix of grouped jacobian blocks",
        "exact minimizer of the stated quadratic objective", "proportional-attention correction is used in token merging (tome)"))
    record("ten_display_equations_match_implementation_and_are_explained",
           equation_blocks == 10 and equation_tags == [str(i) for i in range(1, 11)] and equation_explanations,
           f"Display equations={equation_blocks}; tags={equation_tags}; key implementation/notation explanations present={equation_explanations}.")

    # Recompute the unchanged compression entries now published as Table IV.
    table4 = markdown_table(text, "IV")
    budget_path = ROOT / "outputs/fungibility_operator_compression_confirmatory/budget_summary.csv"
    budget_rows = rows(budget_path) if budget_path.exists() else []
    model_map = {"DeiT-Tiny":"DeiT-Tiny", "DeiT-Small":"DeiT-Small", "ViT-B/16":"ViT-B/16", "ViT-B/16 AugReg":"ViT-B/16", "DINOv2 ViT-S/14":"DINOv2 ViT-S/14"}
    method_map = ["Group-Mean Merging", "ToMe (BSM)", "Operator-Aware (Oracle)", "Operator-Aware (Rank-16)", "Operator-Aware (Rank-32)"]
    table4_ok = bool(budget_rows) and len(table4) == 5 and len(table4[0]) == 8
    gain_values = []
    if table4_ok:
        for row in table4[1:]:
            if len(row) != 8:
                table4_ok = False
                break
            architecture, budget_s, baseline_cell = row[0], row[1], row[2]
            model = model_map.get(architecture)
            budget = int(budget_s) if budget_s.isdigit() else -1
            baselines = [r for r in budget_rows if r.get("model") == model and int(float(r.get("budget", -1))) == budget and r.get("method") in ("Random Pruning", "Norm Pruning", "Attention Pruning")]
            if not model or not baselines:
                table4_ok = False
                break
            best = max(baselines, key=lambda r: float(r["top1_acc"]))
            match = re.match(r"(Random|Norm|Attention),\s*([0-9.]+)%", baseline_cell)
            expected_name = {"Random Pruning":"Random", "Norm Pruning":"Norm", "Attention Pruning":"Attention"}[best["method"]]
            if not match or match.group(1) != expected_name or abs(float(match.group(2))/100-float(best["top1_acc"])) > 0.0005:
                table4_ok = False
                break
            for index, method in enumerate(method_map, start=3):
                source_row = source_value(budget_rows, model=model, budget=budget, method=method)
                accuracy_match = re.search(r"([0-9.]+)%", row[index])
                if not source_row or not accuracy_match or abs(float(accuracy_match.group(1))/100-float(source_row["top1_acc"])) > 0.0005:
                    table4_ok = False
                    break
                if index >= 5:
                    gain_values.append(100*(float(source_row["top1_acc"])-float(best["top1_acc"])))
            if not table4_ok:
                break
    range_in_abstract = bool(re.search(r"4\.2\s*[–-]\s*12\.0", abstract))
    table4_ok = table4_ok and gain_values and abs(min(gain_values)-4.2) < 0.051 and abs(max(gain_values)-12.0) < 0.051 and range_in_abstract
    record("table_IV_and_abstract_match_confirmatory_csv", bool(table4_ok),
           f"Parsed rows={max(0,len(table4)-1)}; best-pruning row and all five compression columns checked; oracle/low-rank gain range={min(gain_values) if gain_values else 'n/a'}–{max(gain_values) if gain_values else 'n/a'} pp.")

    # Recompute the relocated Table S5 counts and percentage-point differences
    # from the real classifier output, and Table S6 from the corrected v2 CSVs.
    table5 = supplementary_markdown_table(supplementary_text, "S5")
    real_path = ROOT / "outputs/fungibility_real_final/real_accuracy_summary.csv"
    real_rows = rows(real_path) if real_path.exists() else []
    arch_map = {"DeiT-Small":"DeiT-Small", "DINOv2 ViT-S/14":"DINOv2 ViT-S/14", "ViT-B/16 AugReg":"ViT-B/16 AugReg"}
    method5 = ["Hybrid Group Mean", "Static Feature-PCA q=16", "Static Feature-PCA q=32"]
    table5_ok = bool(real_rows) and len(table5) == 5 and all(len(row) == 5 for row in table5)
    if table5_ok:
        for row in table5[1:]:
            if len(row) != 5:
                table5_ok = False
                break
            model = arch_map.get(row[0])
            budget = int(row[1]) if row[1].isdigit() else -1
            baseline_acc = None
            for index, method in enumerate(method5, start=2):
                source_row = source_value(real_rows, architecture=model, budget_tokens=budget, method=method)
                if not source_row or int(source_row["n"]) != 1000:
                    table5_ok = False
                    break
                value = re.match(r"([0-9,]+)/1,000\s+\(([0-9.]+)%", row[index])
                count = int(value.group(1).replace(",", "")) if value else -1
                pct = float(value.group(2)) if value else -1.0
                if count != int(source_row["correct_count"]) or abs(pct-float(source_row["top1_accuracy"])) > 0.0005:
                    table5_ok = False
                    break
                if index == 2:
                    baseline_acc = float(source_row["top1_accuracy"])
                else:
                    diff = re.search(r"([+−-][0-9.]+)\s*pp", row[index])
                    expected_diff = float(source_row["top1_accuracy"])-baseline_acc
                    reported_diff = float(diff.group(1).replace("−", "-")) if diff else 999.0
                    if not diff or abs(reported_diff-expected_diff) > 0.051:
                        table5_ok = False
                        break
            if not table5_ok:
                break
    record("table_S5_counts_and_differences_match_real_classifier_csv", bool(table5_ok),
           f"Parsed rows={max(0,len(table5)-1)}; integer correct counts, N=1,000 percentages, and percentage-point changes checked against real_accuracy_summary.csv.")

    table6 = supplementary_markdown_table(supplementary_text, "S6")
    sensitivity_root = ROOT / "outputs/fungibility_regularization_sensitivity_v2_class_randomized"
    aggregate_path = sensitivity_root / "aggregated_by_architecture_budget_factor.csv"
    sens_rows = rows(aggregate_path) if aggregate_path.exists() else []
    factor_by_cell: dict[tuple[str, str], dict[float, dict[str, str]]] = {}
    group_mean_by_cell = {}
    for item in sens_rows:
        key = (item.get("model", ""), item.get("budget", ""))
        if item.get("method") == "operator_aware":
            factor_by_cell.setdefault(key, {})[float(item["lambda_factor"])] = item
        elif item.get("method") == "group_mean":
            group_mean_by_cell[key] = item

    def factor_label(value: float) -> str:
        return str(int(round(value))) if abs(value - round(value)) < 1e-12 else f"{value:g}"

    table6_ok = len(table6) == 9 and all(len(row) == 6 for row in table6)
    seen_cells = set()
    if table6_ok:
        for row in table6[1:]:
            model = row[0]
            budget = row[1]
            key = (model, budget)
            factors = factor_by_cell.get(key, {})
            gm = group_mean_by_cell.get(key)
            if key in seen_cells or len(factors) != 7 or gm is None:
                table6_ok = False
                break
            seen_cells.add(key)
            rates = {factor: float(value["top1_rate"]) for factor, value in factors.items()}
            maximum = max(rates.values())
            best = [factor for factor, rate in rates.items() if abs(rate - maximum) < 1e-12]
            best_text = "all seven factors" if len(best) == 7 else ", ".join(
                factor_label(value) for value in sorted(best))
            values = [float(row[2]), float(row[3]), float(row[5])]
            expected = [rates[10.0] * 100.0, maximum * 100.0, float(gm["top1_rate"]) * 100.0]
            if (any(abs(a-b) > 0.051 for a, b in zip(values, expected))
                    or row[4] != best_text):
                table6_ok = False
                break
    table6_ok = table6_ok and len(seen_cells) == 8
    record("table_S6_matches_corrected_sensitivity_csv",
           bool(table6_ok),
           f"Parsed eight model-budget cells with seven factors each; factor-10, cell maximum, maximizing factor set, and Group Mean checked against the corrected v2 aggregate CSV.")

    # Inspect the actual editable DOCX package: real tables, drawings, equations, and reference sequence.
    docx_path = DOCX_PATH
    docx_structure_ok = False
    if docx_path.is_file():
        try:
            with zipfile.ZipFile(docx_path) as archive:
                names = archive.namelist()
                xml = ET.fromstring(archive.read("word/document.xml"))
                W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
                M = "{http://schemas.openxmlformats.org/officeDocument/2006/math}"
                all_tables = [node for node in xml.iter() if node.tag == W+"tbl"]
                # The exporter uses unstyled 1x3 tables solely to right-align equation numbers.
                manuscript_tables = sum(1 for table in all_tables
                                        if (style := table.find(".//" + W + "tblStyle")) is not None
                                        and style.get(W + "val") == "TableGrid")
                equation_layout_tables = len(all_tables) - manuscript_tables
                drawings_in_docx = sum(1 for node in xml.iter() if node.tag.endswith("}drawing"))
                equations_in_docx = sum(1 for node in xml.iter() if node.tag == M+"oMath")
                display_math_lines = sum(
                    1 for table in all_tables for node in table.iter() if node.tag == M+"oMath")
                inline_math_objects = equations_in_docx - display_math_lines
                para_text = []
                for para in xml.iter(W+"p"):
                    para_text.append("".join(n.text or "" for n in para.iter(W+"t")))
                ref_nums = [int(m.group(1)) for value in para_text if (m := re.match(r"\[(\d+)\]\s", value))]
                docx_valid = [n for n in names if n.startswith("word/media/")]
                docx_table_labels = [value for value in para_text if value in {"TABLE I", "TABLE II", "TABLE III", "TABLE IV"}]
                main_docx_headings_ok = ("7. Limitations" in para_text
                                         and "8. Conclusion" in para_text
                                         and not any("7. From Operator-Aware Optimization to Practical Compression" in value
                                                     or "9. Conclusion" in value
                                                     or "Practical carrier evaluation" in value
                                                     for value in para_text)
                                         and docx_table_labels == ["TABLE I", "TABLE II", "TABLE III", "TABLE IV"])
                docx_structure_ok = (manuscript_tables == 4 and equation_layout_tables == 10
                                     and drawings_in_docx == 8 and len(docx_valid) == 8
                                     and display_math_lines >= 10 and ref_nums == list(range(1,56))
                                     and main_docx_headings_ok)
        except (OSError, zipfile.BadZipFile, KeyError, ET.ParseError):
            docx_structure_ok = False
    record("editable_main_docx_contains_four_native_tables_eight_figures_ten_equations_and_55_ieee_refs",
           docx_structure_ok,
           f"DOCX package {docx_path.name}: manuscript tables={manuscript_tables if docx_path.is_file() else 0}, numbered equation layout tables={equation_layout_tables if docx_path.is_file() else 0}, figures={drawings_in_docx if docx_path.is_file() else 0}, display math lines={display_math_lines if docx_path.is_file() else 0}, inline math objects={inline_math_objects if docx_path.is_file() else 0}, references={len(ref_nums) if docx_path.is_file() else 0}; table labels={docx_table_labels if docx_path.is_file() else []}.")

    passed = all(v["status"] == "PASS" for v in checks.values())
    manifest = {"status":"PASS" if passed else "FAIL", "checks":checks,
                "passed_count":sum(v["status"]=="PASS" for v in checks.values()), "assertion_count":len(checks)}
    out=ROOT/"outputs/fungibility_real_final/paper_final_validation.json"
    out.parent.mkdir(parents=True,exist_ok=True)
    out.write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(manifest,indent=2))
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
