#!/usr/bin/env python3
"""climate-profile-generator / Phase 4: PDF renderer.

Renders the approved Corporate-Navy brief layout (see
examples/mockup_climate_profile.pdf) from a structured brief JSON:

{
  "country": "Burkina Faso",
  "focus": "Drought & Agriculture",
  "period_label": "40-year trends",
  "cards": [["+0.6 C", "warming since 1985"], ...],        # 3 cards
  "sections": [
     {"heading": "1. Observed trends",
      "paragraphs": ["..."],
      "bullets": ["..."],                                   # optional
      "figure": {"path": "output/charts/chart_temperature.png",
                 "caption": "Figure 1. ..."}}               # optional
  ],
  "sources": ["1. NASA POWER ... power.larc.nasa.gov", ...]
}

Usage:
    python3 scripts/render_pdf.py --brief output/BFA_brief.json \
        -o output/Climate_Profile_BurkinaFaso.pdf

Fonts ship in fonts/ and are embedded. Two-pass build for real
"Page X of Y". No network access, stdlib + reportlab + pillow only.
"""
import argparse
import io
import json
from datetime import datetime
from pathlib import Path

from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image,
                                KeepTogether, NextPageTemplate, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

ROOT = Path(__file__).resolve().parent.parent
FONT_DIR = ROOT / "fonts"

# ━━ Locked palette (Corporate Navy, approved 2 Oct 2026) ━━
NAVY = colors.HexColor("#24356B")
NAVY_DIVIDER = colors.HexColor("#1B2852")
NAVY_DARK = colors.HexColor("#1F3A7A")
CARD_FILL = colors.HexColor("#EEF1F8")
CARD_BORDER = colors.HexColor("#C5CEDF")
TEXT_PRIMARY = colors.HexColor("#20201d")
TEXT_MUTED = colors.HexColor("#8b8982")

PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
CONTENT_W = PAGE_W - 2 * MARGIN
BAND_H = 4.4 * cm
TOP_BAND_LATER = 0.9 * cm
BOTTOM = 1.8 * cm
CREDIT = "Built by Omar Farooq  |  github.com/ahaomar/climate-profile-generator"

pdfmetrics.registerFont(TTFont("Roboto Condensed", str(FONT_DIR / "RobotoCondensed-Regular.ttf")))
pdfmetrics.registerFont(TTFont("Roboto Condensed Bold", str(FONT_DIR / "RobotoCondensed-Bold.ttf")))
pdfmetrics.registerFont(TTFont("Roboto Condensed Italic", str(FONT_DIR / "RobotoCondensed-Italic.ttf")))
registerFontFamily("Roboto Condensed", normal="Roboto Condensed",
                   bold="Roboto Condensed Bold", italic="Roboto Condensed Italic",
                   boldItalic="Roboto Condensed Bold")

F = "Roboto Condensed"
FB = "Roboto Condensed Bold"

h2 = ParagraphStyle("h2", fontName=FB, fontSize=13, leading=17, textColor=NAVY_DARK,
                    spaceBefore=14, spaceAfter=6)
body = ParagraphStyle("body", fontName=F, fontSize=11, leading=16.5, textColor=TEXT_PRIMARY,
                      alignment=TA_JUSTIFY, spaceAfter=6)
bullet = ParagraphStyle("bullet", fontName=F, fontSize=11, leading=16.5,
                        textColor=TEXT_PRIMARY, leftIndent=14, spaceAfter=3)
foot = ParagraphStyle("foot", fontName=F, fontSize=8.5, leading=12, textColor=TEXT_MUTED,
                      leftIndent=24, firstLineIndent=-24, spaceAfter=2)
caption = ParagraphStyle("caption", fontName=F, fontSize=8.5, leading=11,
                         textColor=TEXT_MUTED, alignment=TA_CENTER, spaceBefore=4,
                         spaceAfter=4)
stat_style = ParagraphStyle("stat", fontName=FB, fontSize=17, leading=20,
                            textColor=NAVY_DARK, alignment=TA_CENTER)
label_style = ParagraphStyle("statlabel", fontName=F, fontSize=8.5, leading=11,
                             textColor=TEXT_MUTED, alignment=TA_CENTER)

RUN_STAMP = datetime.now().strftime("%d %b %Y, %H:%M")
TOTAL_PAGES = [1]


def draw_footer(cv, page_num):
    cv.saveState()
    cv.setStrokeColor(CARD_BORDER)
    cv.setLineWidth(0.6)
    cv.line(MARGIN, 1.45 * cm, PAGE_W - MARGIN, 1.45 * cm)
    cv.setFont(F, 7.5)
    cv.setFillColor(TEXT_MUTED)
    cv.drawString(MARGIN, 1.05 * cm, CREDIT)
    cv.drawRightString(PAGE_W - MARGIN, 1.05 * cm,
                       "Generated %s   |   Page %s of %s" % (RUN_STAMP, page_num,
                                                             TOTAL_PAGES[0]))
    cv.restoreState()


def on_first(cv, doc):
    b = doc._brief
    cv.saveState()
    cv.setFillColor(NAVY)
    cv.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
    cv.setFillColor(NAVY_DIVIDER)
    cv.rect(0, PAGE_H - BAND_H, PAGE_W, 0.18 * cm, stroke=0, fill=1)
    cv.setFont(FB, 8.5)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.75))
    cv.drawString(MARGIN, PAGE_H - 1.15 * cm, "C O U N T R Y   B R I E F")
    cv.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.15 * cm, "CLIMATE PROFILE GENERATOR")
    cv.setFillColor(colors.white)
    cv.setFont(FB, 21)
    cv.drawString(MARGIN, PAGE_H - 2.25 * cm, "Climate Risk Profile")
    cv.setFont(F, 13)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.92))
    cv.drawString(MARGIN, PAGE_H - 3.05 * cm,
                  "%s  |  %s Focus" % (b["country"], b.get("focus", "Climate")))
    cv.setFont(F, 9.5)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.8))
    cv.drawString(MARGIN, PAGE_H - 3.75 * cm,
                  "%s  |  %s  |  Country Climate Profile Generator"
                  % (b.get("period_label", ""), RUN_STAMP))
    cv.restoreState()
    draw_footer(cv, 1)


def on_later(cv, doc):
    b = doc._brief
    cv.saveState()
    cv.setFillColor(NAVY)
    cv.rect(0, PAGE_H - TOP_BAND_LATER, PAGE_W, TOP_BAND_LATER, stroke=0, fill=1)
    cv.setFont(FB, 8.5)
    cv.setFillColor(colors.white)
    cv.drawString(MARGIN, PAGE_H - 0.62 * cm,
                  "Climate Risk Profile  |  %s" % b["country"])
    cv.restoreState()
    draw_footer(cv, doc.page)


def stat(v, l):
    t = Table([[Paragraph("<b>%s</b>" % v, stat_style)], [Paragraph(l, label_style)]],
              colWidths=[(CONTENT_W - 24) / 3.0])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), CARD_FILL),
        ("BOX", (0, 0), (-1, -1), 0.8, CARD_BORDER),
        ("LINEABOVE", (0, 0), (-1, 0), 2, NAVY_DARK),
        ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("TOPPADDING", (0, -1), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
    ]))
    return t


def embed(path, max_w=CONTENT_W * 0.86):
    w, h = PILImage.open(path).size
    r = min(max_w / w, 1.0)
    return Image(str(path), width=w * r, height=h * r)


def make_story(b):
    story = [NextPageTemplate("Later")]
    cards = b.get("cards") or []
    if len(cards) == 3:
        story.append(Paragraph("<b>Key Findings</b>", h2))
        row = Table([[stat(v, l) for v, l in cards]],
                    colWidths=[CONTENT_W / 3.0] * 3, hAlign="CENTER")
        row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 4),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
        story.append(row)
        story.append(Spacer(1, 8))

    for sec in b.get("sections", []):
        story.append(Paragraph("<b>%s</b>" % sec["heading"], h2))
        for para in sec.get("paragraphs", []):
            story.append(Paragraph(para, body))
        for bul in sec.get("bullets", []):
            story.append(Paragraph("&bull; %s" % bul, bullet))
        fig = sec.get("figure")
        if fig:
            story.append(Spacer(1, 6))
            story.append(KeepTogether([embed(fig["path"]),
                                       Paragraph(fig["caption"], caption)]))
            story.append(Spacer(1, 4))

    if b.get("sources"):
        story.append(Spacer(1, 10))
        story.append(HRFlowable(width="100%", thickness=0.6, color=CARD_BORDER,
                                spaceAfter=6))
        story.append(Paragraph("<b>Sources (annex)</b>", h2))
        for s in b["sources"]:
            story.append(Paragraph(s, foot))
    return story


def make_doc(target, brief):
    doc = BaseDocTemplate(str(target), pagesize=A4,
                          title="Climate Risk Profile - %s" % brief["country"],
                          author="Z.ai", creator="Z.ai",
                          subject="Country climate risk brief")
    first = Frame(MARGIN, BOTTOM, CONTENT_W, PAGE_H - BAND_H - BOTTOM - 0.5 * cm, id="f1")
    later = Frame(MARGIN, BOTTOM, CONTENT_W, PAGE_H - TOP_BAND_LATER - BOTTOM - 0.5 * cm,
                  id="f2")
    doc._brief = brief
    doc.addPageTemplates([PageTemplate(id="First", frames=[first], onPage=on_first),
                          PageTemplate(id="Later", frames=[later], onPage=on_later)])
    return doc


def count_pages(brief):
    # reportlab writes 0 bytes to file-like targets here, so count via a
    # temporary file (reportlab quirk, harmless: rebuild follows)
    import tempfile, os
    fd, tmp = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    try:
        make_doc(tmp, brief).build(make_story(brief))
        import pymupdf
        return len(pymupdf.open(tmp))
    finally:
        os.remove(tmp)


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--brief", required=True, help="brief JSON path")
    ap.add_argument("-o", "--out", required=True, help="output PDF path")
    args = ap.parse_args()
    brief = json.loads(Path(args.brief).read_text(encoding="utf-8"))
    TOTAL_PAGES[0] = count_pages(brief)
    make_doc(args.out, brief).build(make_story(brief))
    print("wrote %s (%d pages)" % (args.out, TOTAL_PAGES[0]))


if __name__ == "__main__":
    main()
