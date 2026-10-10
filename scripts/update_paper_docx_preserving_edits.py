"""Apply the final editorial/table changes while preserving existing Word content."""
from __future__ import annotations

import argparse
import copy
import re
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from lxml import etree

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"
R_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG_REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
W = f"{{{W_NS}}}"
M = f"{{{M_NS}}}"
R_ID = f"{{{R_NS}}}id"
R_EMBED = f"{{{R_NS}}}embed"
R_LINK = f"{{{R_NS}}}link"
NS = {"w": W_NS, "m": M_NS}
TEXT_TAGS = {W + "t", M + "t"}
REFERENCE = re.compile(r"^\[(\d+)\]")
NUMERIC_CITATION = re.compile(r"\[(\d+)\](?:–\[(\d+)\])?")


def paragraph_text(node) -> str:
    return "".join(child.text or "" for child in node.iter() if child.tag in TEXT_TAGS)


def visible_paragraphs(body):
    return [(i, node, paragraph_text(node)) for i, node in enumerate(body) if node.tag == W + "p"]


def find_paragraph(body, *, exact: str | None = None, starts: str | None = None):
    found = []
    for index, node, value in visible_paragraphs(body):
        if (exact is not None and value == exact) or (starts is not None and value.startswith(starts)):
            found.append((index, node, value))
    if len(found) != 1:
        raise ValueError(f"Expected one paragraph exact={exact!r} starts={starts!r}; found {len(found)}")
    return found[0]


def set_existing_run_texts(paragraph, replacements: list[str]) -> None:
    """Change prose in place while leaving its OMML math objects and run styling untouched."""
    runs = [child for child in paragraph if child.tag == W + "r"]
    if len(runs) != len(replacements):
        raise ValueError(f"Expected {len(replacements)} text runs in inline-math paragraph; found {len(runs)}")
    for run, replacement in zip(runs, replacements):
        text_nodes = [child for child in run.iter(W + "t")]
        if len(text_nodes) != 1:
            raise ValueError("Expected one Word text node per existing prose run")
        text_nodes[0].text = replacement


def replace_fragment(body, old: str, new: str) -> None:
    matches = []
    for index, node, value in visible_paragraphs(body):
        if old in value:
            matches.append((index, node))
    if len(matches) != 1:
        raise ValueError(f"Expected one editable occurrence of {old!r}; found {len(matches)}")
    _, node = matches[0]
    text_nodes = [child for child in node.iter() if child.tag == W + "t"]
    matches = [child for child in text_nodes if old in (child.text or "")]
    if len(matches) != 1:
        raise ValueError(f"Replacement must fit inside one existing Word text run: {old!r}")
    matches[0].text = matches[0].text.replace(old, new, 1)


def remap_numeric_citation(match: re.Match) -> str:
    first = int(match.group(1))
    last = int(match.group(2) or first)
    values = [n + 2 if n >= 42 else n for n in range(first, last + 1)]
    groups: list[list[int]] = []
    for value in values:
        if not groups or value != groups[-1][-1] + 1:
            groups.append([value])
        else:
            groups[-1].append(value)
    rendered = []
    for group in groups:
        if len(group) >= 3:
            rendered.append(f"[{group[0]}]–[{group[-1]}]")
        else:
            rendered.extend(f"[{value}]" for value in group)
    return ", ".join(rendered)


def update_existing_citations(body, references_heading) -> None:
    """Renumber body citations only; bibliography labels are handled separately."""
    for child in body:
        if child is references_heading:
            break
        for node in child.iter(W + "t"):
            if node.text and NUMERIC_CITATION.search(node.text):
                node.text = NUMERIC_CITATION.sub(remap_numeric_citation, node.text)


def candidate_block(candidate_body, start_prefix: str, end_prefix: str):
    direct = list(candidate_body)
    starts = [i for i, node in enumerate(direct)
              if node.tag == W + "p" and paragraph_text(node).startswith(start_prefix)]
    ends = [i for i, node in enumerate(direct)
            if node.tag == W + "p" and paragraph_text(node).startswith(end_prefix)]
    if len(starts) != 1 or len(ends) != 1 or starts[0] > ends[0]:
        raise ValueError(f"Candidate block anchors are not unique: {start_prefix!r} / {end_prefix!r}")
    block = [copy.deepcopy(node) for node in direct[starts[0]:ends[0] + 1]]
    for element in block:
        for descendant in element.iter():
            if any(attr in descendant.attrib for attr in (R_ID, R_EMBED, R_LINK)):
                raise ValueError("New editorial/table blocks must not introduce package relationships")
    return block


def insert_after(body, anchor_node, elements) -> None:
    index = body.index(anchor_node)
    for offset, element in enumerate(elements, 1):
        body.insert(index + offset, copy.deepcopy(element))


def table_counts(root):
    tables = list(root.iter(W + "tbl"))
    main_tables = 0
    for table in tables:
        style = table.find(".//" + W + "tblStyle")
        if style is not None and style.get(W + "val") == "TableGrid":
            main_tables += 1
    drawings = sum(1 for node in root.iter() if node.tag.endswith("}drawing"))
    equations = sum(1 for node in root.iter() if node.tag == M + "oMath")
    return main_tables, len(tables) - main_tables, drawings, equations


def update(existing: Path, candidate: Path, output: Path) -> None:
    if existing.resolve() == output.resolve():
        raise ValueError("Output must be staged separately; do not edit the source DOCX in place")
    with ZipFile(existing) as original, ZipFile(candidate) as generated:
        old_doc = etree.fromstring(original.read("word/document.xml"))
        new_doc = etree.fromstring(generated.read("word/document.xml"))
        old_body = old_doc.find("w:body", NS)
        new_body = new_doc.find("w:body", NS)
        if old_body is None or new_body is None:
            raise ValueError("DOCX body is missing")
        original_counts = table_counts(old_doc)
        if original_counts[0] != 2 or original_counts[2] != 8 or original_counts[1] != 10:
            raise ValueError(f"Source DOCX is not the expected two-table manuscript: {original_counts}")

        for old, new in (
            ("as a mechanistic account and an oracle-level compression opportunity",
             "as a mechanistic account of the tested interventions and an oracle-level compression opportunity"),
            ("jointly bound replacement tolerance", "shape observed replacement tolerance"),
            ("it groups patches into B carriers and shortens the sequence for subsequent computation.",
             "it optimizes grouped carrier content under a fixed assignment S and shortens the sequence for subsequent computation."),
        ):
            replace_fragment(old_body, old, new)

        # Renumber the existing compression table before adding the new Table II.
        for node in old_body.iter(W + "t"):
            if node.text:
                node.text = node.text.replace("TABLE II", "TABLE IV").replace("Table II", "Table IV")

        reference_heading = find_paragraph(old_body, exact="References")[1]
        update_existing_citations(old_body, reference_heading)

        # Update the one nearby paragraph that would otherwise repeat all Table III values.
        _, ratio_paragraph, _ = find_paragraph(old_body, starts="At depth 8, the corrected PC1-to-lowest-variance-PC sensitivity ratios")
        candidate_ratio = find_paragraph(new_body, starts="At depth 8, the ViT-B PCbottom direction is especially uncertain")[1]
        ratio_index = old_body.index(ratio_paragraph)
        old_body.remove(ratio_paragraph)
        old_body.insert(ratio_index, copy.deepcopy(candidate_ratio))

        related_index, related_paragraph, _ = find_paragraph(old_body, starts="Token-reduction methods such as DynamicViT")
        candidate_related = find_paragraph(new_body, starts="Jacobian-sensitive geometry and task-aware token compression")[1]
        insert_after(old_body, related_paragraph, [candidate_related])

        table2_block = candidate_block(new_body,
                                       "The controlled endpoint differences are summarized in Table II.",
                                       "Note (Table II). All interventions are at Block 8.")
        _, geometry_paragraph, _ = find_paragraph(old_body, starts="PCA-aligned variation.")
        insert_after(old_body, geometry_paragraph, table2_block)

        table3_block = candidate_block(new_body,
                                       "Near-null expansion at the primary cutoff is architecture-dependent",
                                       "Mℓ is the empirical uncentered second moment")
        _, old_spectrum_paragraph, _ = find_paragraph(old_body, starts="The entropy-based effective rank of Ml,")
        _, old_supplementary_s2_paragraph, _ = find_paragraph(old_body, starts="The spectra, cutoff sensitivity, directional sensitivities,")
        if old_body.index(old_supplementary_s2_paragraph) != old_body.index(old_spectrum_paragraph) + 1:
            raise ValueError("Unexpected intervening content in the old functional-spectrum text block")
        set_existing_run_texts(old_spectrum_paragraph, [
            "The entropy-based effective rank of ",
            ", normalized by feature dimension ",
            ", is compared across depths 5–10 in Table III. At the operational near-null cutoff ",
            ", the primary-threshold fractions are summarized there; DINOv2 reaches 64.84% at the looser ",
            " cutoff, illustrating threshold sensitivity.",
        ])
        insert_after(old_body, old_spectrum_paragraph, table3_block)

        # Insert the two new reference paragraphs, then shift the old reference labels 42–53.
        candidate_refs = []
        for node in new_body:
            if node.tag == W + "p" and (match := REFERENCE.match(paragraph_text(node))):
                if int(match.group(1)) in (42, 43):
                    candidate_refs.append(node)
        if len(candidate_refs) != 2:
            raise ValueError(f"Candidate DOCX must contain new reference entries 42–43; found {len(candidate_refs)}")
        old_reference_paragraphs = [(i, node, paragraph_text(node)) for i, node in enumerate(old_body)
                                    if node.tag == W + "p" and REFERENCE.match(paragraph_text(node))]
        old_numbers = [int(REFERENCE.match(value).group(1)) for _, _, value in old_reference_paragraphs]
        if old_numbers != list(range(1, 54)):
            raise ValueError("Source DOCX reference list is not the expected sequence 1–53")
        reference_41 = next(node for _, node, value in old_reference_paragraphs if value.startswith("[41]"))
        insert_after(old_body, reference_41, candidate_refs)
        for _, node, _ in old_reference_paragraphs:
            first_text = next((child for child in node.iter(W + "t") if child.text), None)
            if first_text is None:
                raise ValueError("Reference paragraph is missing its number text")
            match = REFERENCE.match(first_text.text)
            if match and int(match.group(1)) >= 42:
                first_text.text = f"[{int(match.group(1)) + 2}]" + first_text.text[match.end():]

        main_labels = [paragraph_text(node) for node in old_body
                       if node.tag == W + "p" and paragraph_text(node) in {"TABLE I", "TABLE II", "TABLE III", "TABLE IV"}]
        counts = table_counts(old_doc)
        final_references = [int(REFERENCE.match(paragraph_text(node)).group(1))
                            for node in old_body if node.tag == W + "p" and REFERENCE.match(paragraph_text(node))]
        if main_labels != ["TABLE I", "TABLE II", "TABLE III", "TABLE IV"]:
            raise ValueError(f"Main table labels are out of order: {main_labels}")
        if counts[0] != 4 or counts[1] != 10 or counts[2] != 8 or counts[3] < 10:
            raise ValueError(f"Final DOCX structure is invalid: main tables/equations/figures/math={counts}")
        if final_references != list(range(1, 56)):
            raise ValueError(f"Final DOCX references are invalid: {final_references[:3]}…{final_references[-3:]}")

        # Existing section properties, package relationships, style/theme/custom XML remain intact.
        output.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(prefix="pcf_docx_stage_", suffix=".docx", dir=output.parent, delete=False) as temp:
            temp_path = Path(temp.name)
        try:
            xml_bytes = etree.tostring(old_doc, encoding="UTF-8", xml_declaration=True, standalone=True)
            with ZipFile(temp_path, "w", compression=ZIP_DEFLATED) as staged:
                for info in original.infolist():
                    payload = xml_bytes if info.filename == "word/document.xml" else original.read(info.filename)
                    staged.writestr(info, payload)
            temp_path.replace(output)
        finally:
            if temp_path.exists():
                temp_path.unlink()
    print(f"Staged {output}; source package parts preserved except word/document.xml; main tables I–IV, 8 figures, 10 equation layout blocks, 55 references.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("existing", type=Path, help="Existing Word file containing formatting and author edits to preserve")
    parser.add_argument("candidate", type=Path, help="Fresh exporter output with current Markdown additions")
    parser.add_argument("output", type=Path, help="Separate staged DOCX output")
    args = parser.parse_args()
    update(args.existing.resolve(), args.candidate.resolve(), args.output.resolve())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
