#!/usr/bin/env python3
"""climate-profile-generator / Phase 5: Word renderer.

Renders the same brief JSON as render_pdf.py into an editable .docx.

Usage:
    python3 scripts/render_docx.py --brief output/BFA_brief.json \
        -o output/Climate_Profile_BurkinaFaso.docx

Font note (documented in docs/TECHNICAL_SPEC.md): .docx files reference
fonts rather than embed them. We declare Roboto Condensed; Word substitutes
a similar font (e.g. Calibri) on devices without it. The PDF is the
canonical share format.

Requires: python-docx (the only non-stdlib dependency in the project).
"""
import argparse
import json
import re
from datetime import datetime
from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Cm, Pt, RGBColor

NAVY = RGBColor(0x24, 0x35, 0x6B)
NAVY_DARK = RGBColor(0x1F, 0x3A, 0x7A)
MUTED = RGBColor(0x8B, 0x89, 0x82)
TEXT = RGBColor(0x20, 0x20, 0x1D)

FONT = "Roboto Condensed"
FALLBACK = "Calibri"  # Word's substitution target when RC is absent
CREDIT = "Built by Omar Farooq | github.com/ahaomar/climate-profile-generator"
SUPER_RE = re.compile(r"<super>(.*?)</super>")


def set_font(run, size=11, bold=False, color=TEXT, italic=False):
    run.font.name = FONT
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.italic = italic
    run.font.color.rgb = color
    # East Asian / complex-script mapping so Word honors the face everywhere
    rpr = run._element.get_or_add_rPr()
    rfonts = rpr.get_or_add_rFonts()
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rfonts.set("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}%s" % attr.split(":")[1], FONT)


def add_rich(par, text, size=11, color=TEXT):
    """Add text to a paragraph, honoring <super> tags."""
    pos = 0
    for m in SUPER_RE.finditer(text):
        if m.start() > pos:
            set_font(par.add_run(text[pos:m.start()]), size=size, color=color)
        sup = par.add_run(m.group(1))
        set_font(sup, size=size, color=color)
        sup.font.superscript = True
        pos = m.end()
    if pos < len(text):
        set_font(par.add_run(text[pos:]), size=size, color=color)


def header_band(doc, brief):
    """Navy title block at the top of the document."""
    t = doc.add_table(rows=1, cols=1)
    t.style = "Table Grid"
    cell = t.rows[0].cells[0]
    cell.paragraphs[0].text = ""
    shading = cell._element.get_or_add_tcPr()
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), "24356B")
    shading.append(shd)
    p1 = cell.paragraphs[0]
    add_rich(p1, "COUNTRY BRIEF", size=9)
    for r in p1.runs:
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.bold = True
    p2 = cell.add_paragraph()
    add_rich(p2, "Climate Risk Profile", size=20)
    for r in p2.runs:
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        r.font.bold = True
    p3 = cell.add_paragraph()
    add_rich(p3, "%s  |  %s Focus  |  %s" % (
        brief["country"], brief.get("focus", "Climate"),
        datetime.now().strftime("%d %b %Y, %H:%M")), size=10)
    for r in p3.runs:
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
    doc.add_paragraph()


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief", required=True)
    ap.add_argument("-o", "--out", required=True)
    args = ap.parse_args()
    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))

    doc = Document()
    # document-level default font with graceful fallback
    style = doc.styles["Normal"]
    style.font.name = FONT
    style.font.size = Pt(11)

    header_band(doc, brief)

    cards = brief.get("cards") or []
    if len(cards) == 3:
        h = doc.add_paragraph()
        set_font(h.add_run("Key Findings"), size=13, bold=True, color=NAVY_DARK)
        t = doc.add_table(rows=2, cols=3)
        t.alignment = WD_TABLE_ALIGNMENT.CENTER
        for i, (v, l) in enumerate(cards):
            cv = t.rows[0].cells[i]
            p = cv.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_font(p.add_run(v), size=16, bold=True, color=NAVY_DARK)
            cl = t.rows[1].cells[i]
            pl = cl.paragraphs[0]
            pl.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_font(pl.add_run(l), size=8.5, color=MUTED)
        doc.add_paragraph()

    for sec in brief.get("sections", []):
        h = doc.add_paragraph()
        set_font(h.add_run(sec["heading"]), size=13, bold=True, color=NAVY_DARK)
        h.paragraph_format.space_before = Pt(12)
        for para in sec.get("paragraphs", []):
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            add_rich(p, para)
        for bul in sec.get("bullets", []):
            p = doc.add_paragraph(style="List Bullet")
            add_rich(p, bul)
        fig = sec.get("figure")
        if fig and Path(fig["path"]).exists():
            doc.add_picture(fig["path"], width=Cm(15.5))
            cap = doc.add_paragraph()
            cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            set_font(cap.add_run(fig["caption"]), size=8.5, color=MUTED)

    if brief.get("sources"):
        h = doc.add_paragraph()
        set_font(h.add_run("Sources (annex)"), size=13, bold=True, color=NAVY_DARK)
        for s in brief["sources"]:
            p = doc.add_paragraph()
            set_font(p.add_run(s), size=8.5, color=MUTED)

    footer = doc.add_paragraph()
    set_font(footer.add_run(CREDIT), size=8, color=MUTED)

    doc.save(args.out)
    print("wrote %s" % args.out)


if __name__ == "__main__":
    main()
