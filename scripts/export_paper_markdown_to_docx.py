"""Create a readable Word export of the canonical manuscript Markdown."""
from __future__ import annotations

import re
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def bibliography(markdown: str):
    block = re.search(r"```bibtex\s*\n(.*?)\n```", markdown, re.S)
    if not block:
        raise ValueError("BibTeX block is missing")
    source = block.group(1)
    entries=[]; pos=0
    while True:
        start=source.find("@",pos)
        if start<0: break
        brace=source.find("{",start)
        if brace<0: break
        depth=0; end=None
        for i in range(brace,len(source)):
            if source[i]=="{": depth+=1
            elif source[i]=="}":
                depth-=1
                if depth==0: end=i+1; break
        if end is None: raise ValueError("Unbalanced BibTeX entry")
        comma=source.find(",",brace)
        head=re.match(r"@(\w+)\s*\{\s*([^,]+),",source[start:comma+1]) if comma>=0 else None
        if not head: raise ValueError("Could not parse BibTeX entry")
        key=head.group(2).strip()
        body=source[brace+1:end-1]
        fields={}; i=0
        while i<len(body):
            m=re.search(r"([A-Za-z]+)\s*=\s*",body[i:])
            if not m: break
            name=m.group(1).lower(); j=i+m.end()
            while j<len(body) and body[j].isspace(): j+=1
            if j>=len(body): break
            if body[j]=="{":
                d=1; k=j+1
                while k<len(body) and d:
                    if body[k]=="{": d+=1
                    elif body[k]=="}": d-=1
                    k+=1
                val=body[j+1:k-1]
            elif body[j]=='"':
                k=j+1
                while k<len(body) and not(body[k]=='"' and body[k-1]!='\\'): k+=1
                val=body[j+1:k]
            else:
                k=j
                while k<len(body) and body[k] not in ",\n": k+=1
                val=body[j:k]
            fields[name]=val.strip()
            i=max(k,j)+1
        entries.append((key,fields))
        pos=end
    if not entries: raise ValueError("No BibTeX entries parsed")
    return block,entries


def clean_tex(text: str) -> str:
    text=text.replace("{\\'e}","é").replace("{\\'E}","É").replace("{\\'o}","ó").replace("{\\'a}","á")
    text=re.sub(r"\\textit\{([^{}]*)\}",r"\1",text)
    return text.replace("{","").replace("}","").replace("~"," ").strip()


def reference_text(fields: dict[str,str]) -> str:
    author=clean_tex(fields.get("author",""))
    year=clean_tex(fields.get("year","n.d."))
    title=clean_tex(fields.get("title",""))
    venue=clean_tex(fields.get("journal",fields.get("booktitle","")))
    volume=clean_tex(fields.get("volume",""))
    pages=clean_tex(fields.get("pages",""))
    url=clean_tex(fields.get("url",""))
    tail=", ".join(x for x in (volume,pages) if x)
    result=f"{author} ({year}). {title}."
    if venue: result+=f" {venue}"
    if tail: result+=f", {tail}"
    result+="."
    if url: result+=f" {url}"
    return result


def set_font(run, *, size=10.5, bold=None, italic=None, color="202A32", name="Times New Roman"):
    run.font.name=name
    run._element.get_or_add_rPr().rFonts.set(qn("w:ascii"),name)
    run._element.get_or_add_rPr().rFonts.set(qn("w:hAnsi"),name)
    run.font.size=Pt(size); run.font.color.rgb=RGBColor.from_string(color)
    if bold is not None: run.bold=bold
    if italic is not None: run.italic=italic


def citation_replace(text: str, key_to_num: dict[str,int]) -> str:
    def sub(m):
        keys=[k.strip() for k in m.group(1).split(",")]
        nums=[str(key_to_num[k]) for k in keys if k in key_to_num]
        return "["+", ".join(nums)+"]" if nums else m.group(0)
    return re.sub(r"\\citep\{([^}]+)\}",sub,text)


INLINE=re.compile(r"(\*\*(.+?)\*\*|\*(.+?)\*|`(.+?)`|\\citep\{([^}]+)\})")


def add_inline_paragraph(doc, text: str, key_to_num, *, caption=False):
    p=doc.add_paragraph()
    if caption: p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    cursor=0
    for m in INLINE.finditer(text):
        if m.start()>cursor:
            run=p.add_run(citation_replace(text[cursor:m.start()],key_to_num))
            set_font(run,size=9.2 if caption else 10.5,italic=caption,color="4C5963" if caption else "202A32")
        if m.group(2) is not None:
            run=p.add_run(m.group(2)); set_font(run,size=10.5,bold=True,color="202A32")
        elif m.group(4) is not None:
            run=p.add_run(m.group(4)); set_font(run,size=10.5,italic=True,color="202A32")
        elif m.group(6) is not None:
            run=p.add_run(m.group(6)); set_font(run,size=9.5,name="Consolas",color="34495E")
        else:
            run=p.add_run(citation_replace("\\citep{"+m.group(8)+"}",key_to_num))
            set_font(run,size=9.2 if caption else 10.5,italic=caption,color="4C5963" if caption else "202A32")
        cursor=m.end()
    if cursor<len(text):
        run=p.add_run(citation_replace(text[cursor:],key_to_num))
        set_font(run,size=9.2 if caption else 10.5,italic=caption,color="4C5963" if caption else "202A32")
    p.paragraph_format.space_after=Pt(5 if caption else 6)
    if not caption:
        p.paragraph_format.line_spacing=1.12
    return p


def add_image(doc, src: str, image_root: Path):
    local=(image_root/src).resolve()
    if local.suffix.lower()==".svg": local=local.with_suffix(".png")
    if not local.is_file(): raise FileNotFoundError(local)
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.keep_together=True; p.paragraph_format.space_after=Pt(2)
    p.add_run().add_picture(str(local),width=Inches(6.45))


def add_formatted_reference(doc, index: int, fields: dict[str,str]):
    p=doc.add_paragraph()
    p.paragraph_format.left_indent=Inches(.24)
    p.paragraph_format.first_line_indent=Inches(-.24)
    p.paragraph_format.space_after=Pt(5)
    r=p.add_run(f"[{index}] {reference_text(fields)}")
    set_font(r,size=9.4,color="34414A")


def build(source: Path, output: Path):
    markdown=source.read_text(encoding="utf-8")
    bib_block,entries=bibliography(markdown)
    key_to_num={key:i+1 for i,(key,_) in enumerate(entries)}
    body=markdown.replace(bib_block.group(0),"")
    doc=Document()
    sec=doc.sections[0]
    sec.top_margin=Inches(.72); sec.bottom_margin=Inches(.72)
    sec.left_margin=Inches(.78); sec.right_margin=Inches(.78)
    styles=doc.styles
    for nm,size,col in [("Normal",10.5,"202A32"),("Title",18,"17232D"),("Heading 1",14,"173D52"),("Heading 2",11.5,"246B8E")]:
        st=styles[nm]; st.font.name="Times New Roman"; st.font.size=Pt(size); st.font.color.rgb=RGBColor.from_string(col)
        st._element.rPr.rFonts.set(qn("w:ascii"),"Times New Roman"); st._element.rPr.rFonts.set(qn("w:hAnsi"),"Times New Roman")
    styles["Heading 1"].paragraph_format.space_before=Pt(14); styles["Heading 1"].paragraph_format.space_after=Pt(5)
    styles["Heading 2"].paragraph_format.space_before=Pt(10); styles["Heading 2"].paragraph_format.space_after=Pt(4)
    # Numbered citations match the formatted references at the end.
    lines=body.splitlines(); i=0; references_inserted=False; image_count=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:
            i+=1; continue
        if line.startswith("```"):
            while i<len(lines) and not lines[i].strip().startswith("```"): i+=1
            i+=1; continue
        heading=re.match(r"^(#{1,3})\s+(.*)$",line)
        if heading:
            level=len(heading.group(1)); text=heading.group(2).strip()
            if text=="References":
                doc.add_heading("References",level=1)
                for n,(_,fields) in enumerate(entries,1): add_formatted_reference(doc,n,fields)
                references_inserted=True
            elif level==1:
                p=doc.add_paragraph(style="Title"); r=p.add_run(text); set_font(r,size=18,bold=True,color="17232D")
                p.paragraph_format.space_after=Pt(8)
            else:
                p=doc.add_paragraph(style="Heading 1" if level==2 else "Heading 2")
                r=p.add_run(text); set_font(r,size=14 if level==2 else 11.5,bold=True,color="173D52" if level==2 else "246B8E")
                p.paragraph_format.keep_with_next=True
            i+=1; continue
        if line.startswith("![") and "](" in line and line.endswith(")"):
            source_path=line[2:].split("](",1)[1][:-1]
            add_image(doc,source_path,source.parent); image_count+=1; i+=1; continue
        if line.startswith("*") and line.endswith("*") and line.count("*")>=2:
            text=line.strip("*")
            add_inline_paragraph(doc,text,key_to_num,caption=text.startswith(("Figure ","Figure S")))
            i+=1; continue
        if line.startswith("**") and line.endswith("**"):
            p=doc.add_paragraph(); r=p.add_run(line[2:-2]); set_font(r,size=10.5,bold=True,color="202A32")
            i+=1; continue
        if line.startswith("---"):
            i+=1; continue
        # Join wrapped source lines into the same manuscript paragraph.
        paragraph=[line]
        i+=1
        while i<len(lines) and lines[i].strip() and not re.match(r"^#{1,3}\s",lines[i].strip()) and not lines[i].strip().startswith("```") and not lines[i].strip().startswith("!["):
            paragraph.append(lines[i].strip()); i+=1
        joined=" ".join(paragraph).replace("\\ ","").replace("\\"," ").strip()
        add_inline_paragraph(doc,joined,key_to_num)
    if not references_inserted:
        doc.add_heading("References",level=1)
        for n,(_,fields) in enumerate(entries,1): add_formatted_reference(doc,n,fields)
    doc.core_properties.title="Patch-Content Fungibility: Geometry, Functional Transmission, and Operator-Aware Token Compression"
    doc.core_properties.subject="Manuscript export with reviewed v4 figures"
    output.parent.mkdir(parents=True,exist_ok=True)
    doc.save(output)
    print(f"Created {output}; references={len(entries)}; figures={image_count}")


if __name__=="__main__":
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("source",type=Path); ap.add_argument("output",type=Path)
    args=ap.parse_args(); build(args.source.resolve(),args.output.resolve())
