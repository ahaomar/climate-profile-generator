"""MOCKUP PDF: Climate Risk Profile layout preview - illustrative data only."""
import io
from datetime import datetime

import pymupdf
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas as canvas_module
from reportlab.platypus import (BaseDocTemplate, Frame, HRFlowable, Image,
                                KeepTogether, NextPageTemplate, PageTemplate,
                                Paragraph, Spacer, Table, TableStyle)

FONT_DIR = "/System/Library/Fonts/Supplemental/"
FONT_DIR = "../fonts/"
pdfmetrics.registerFont(TTFont("Roboto Condensed", FONT_DIR + "RobotoCondensed-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Roboto Condensed Bold", FONT_DIR + "RobotoCondensed-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Roboto Condensed Italic", FONT_DIR + "RobotoCondensed-Italic.ttf"))
registerFontFamily("Roboto Condensed", normal="Roboto Condensed", bold="Roboto Condensed Bold",
                   italic="Roboto Condensed Italic", boldItalic="Roboto Condensed Bold")
BODY_FONT = "Roboto Condensed"
HEAD_FONT = "Roboto Condensed Bold"

# ━━ Palette: user-specified UN blue + derived tints (single hue family) ━━
UN_BLUE = colors.HexColor("#24356B")     # corporate navy masthead (approved 2 Oct 2026)
UN_DARK = colors.HexColor("#1F3A7A")     # headings / stat emphasis
TABLE_STRIPE = colors.HexColor("#EEF1F8")
BORDER = colors.HexColor("#C5CEDF")
TEXT_PRIMARY = colors.HexColor("#20201d")
TEXT_MUTED = colors.HexColor("#8b8982")

M, P = TEXT_MUTED, TEXT_PRIMARY
PAGE_W, PAGE_H = A4
MARGIN = 2.0 * cm
CONTENT_W = PAGE_W - 2 * MARGIN
BAND_H = 4.4 * cm
TOP_BAND_LATER = 0.9 * cm
BOTTOM = 1.8 * cm
GENERATED = datetime.now().strftime("%d %b %Y, %H:%M")
CREDIT = "Built by Omar Farooq  |  github.com/ahaomar/climate-profile-generator"
TOTAL_PAGES = [1]  # filled by the counting pass

h2 = ParagraphStyle("h2", fontName="Roboto Condensed Bold", fontSize=13, leading=17,
                    textColor=UN_DARK, spaceBefore=14, spaceAfter=6)
body = ParagraphStyle("body", fontName="Roboto Condensed", fontSize=11, leading=16.5,
                      textColor=P, alignment=TA_JUSTIFY, spaceAfter=6)
bullet = ParagraphStyle("bullet", fontName="Roboto Condensed", fontSize=11, leading=16.5,
                        textColor=P, leftIndent=14, spaceAfter=3)
foot = ParagraphStyle("foot", fontName="Roboto Condensed", fontSize=8.5, leading=12,
                      textColor=M, leftIndent=24, firstLineIndent=-24, spaceAfter=2)
caption = ParagraphStyle("caption", fontName="Roboto Condensed", fontSize=8.5, leading=11,
                         textColor=M, alignment=TA_CENTER, spaceBefore=4, spaceAfter=4)
banner_txt = ParagraphStyle("banner", fontName="Roboto Condensed Bold", fontSize=8, leading=10,
                            textColor=colors.white, alignment=TA_CENTER)
stat_style = ParagraphStyle("stat", fontName="Roboto Condensed Bold", fontSize=17, leading=20,
                            textColor=UN_DARK, alignment=TA_CENTER)
label_style = ParagraphStyle("statlabel", fontName="Roboto Condensed", fontSize=8.5,
                             leading=11, textColor=M, alignment=TA_CENTER)


def draw_footer(cv, page_num):
    cv.saveState()
    cv.setStrokeColor(BORDER)
    cv.setLineWidth(0.6)
    cv.line(MARGIN, 1.45 * cm, PAGE_W - MARGIN, 1.45 * cm)
    cv.setFont("Roboto Condensed", 7.5)
    cv.setFillColor(M)
    cv.drawString(MARGIN, 1.05 * cm, CREDIT)
    right = "Generated %s   |   Page %s of %s" % (GENERATED, page_num, TOTAL_PAGES[0])
    cv.drawRightString(PAGE_W - MARGIN, 1.05 * cm, right)
    cv.restoreState()


def on_first(cv, doc):
    cv.saveState()
    cv.setFillColor(UN_BLUE)
    cv.rect(0, PAGE_H - BAND_H, PAGE_W, BAND_H, stroke=0, fill=1)
    cv.setFillColor(colors.HexColor("#1B2852"))
    cv.rect(0, PAGE_H - BAND_H, PAGE_W, 0.18 * cm, stroke=0, fill=1)
    cv.setFont("Roboto Condensed Bold", 8.5)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.75))
    cv.drawString(MARGIN, PAGE_H - 1.15 * cm, "C O U N T R Y   B R I E F")
    cv.drawRightString(PAGE_W - MARGIN, PAGE_H - 1.15 * cm, "MOCKUP PREVIEW")
    cv.setFillColor(colors.white)
    cv.setFont("Roboto Condensed Bold", 21)
    cv.drawString(MARGIN, PAGE_H - 2.25 * cm, "Climate Risk Profile")
    cv.setFont("Roboto Condensed", 13)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.92))
    cv.drawString(MARGIN, PAGE_H - 3.05 * cm,
                  "Burkina Faso  |  Drought & Agriculture Focus")
    cv.setFont("Roboto Condensed", 9)
    cv.setFillColor(colors.Color(1, 1, 1, alpha=0.8))
    cv.drawString(MARGIN, PAGE_H - 3.75 * cm,
                  "40-year trends  |  October 2026  |  Country Climate Profile Generator")
    cv.restoreState()
    draw_footer(cv, 1)


def on_later(cv, doc):
    cv.saveState()
    cv.setFillColor(UN_BLUE)
    cv.rect(0, PAGE_H - TOP_BAND_LATER, PAGE_W, TOP_BAND_LATER, stroke=0, fill=1)
    cv.setFont("Roboto Condensed Bold", 8.5)
    cv.setFillColor(colors.white)
    cv.drawString(MARGIN, PAGE_H - 0.62 * cm,
                  "Climate Risk Profile  |  Burkina Faso  (MOCKUP)")
    cv.restoreState()
    draw_footer(cv, doc.page)


def stat(v, l):
    t = Table([[Paragraph("<b>%s</b>" % v, stat_style)], [Paragraph(l, label_style)]],
              colWidths=[(CONTENT_W - 24) / 3.0])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), TABLE_STRIPE),
        ("BOX", (0, 0), (-1, -1), 0.8, BORDER),
        ("LINEABOVE", (0, 0), (-1, 0), 2, UN_BLUE),
        ("TOPPADDING", (0, 0), (-1, 0), 8), ("BOTTOMPADDING", (0, -1), (-1, -1), 8),
        ("TOPPADDING", (0, -1), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, 0), 1),
    ]))
    return t


def embed(path, max_w=CONTENT_W * 0.86):
    w, h = PILImage.open(path).size
    r = min(max_w / w, 1.0)
    return Image(path, width=w * r, height=h * r)


def make_story():
    story = [NextPageTemplate('Later')]
    banner = Table([[Paragraph("MOCKUP  -  LAYOUT PREVIEW  -  ALL DATA ILLUSTRATIVE",
                               banner_txt)]], colWidths=[CONTENT_W])
    banner.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), UN_DARK),
                                ("TOPPADDING", (0, 0), (-1, -1), 4),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(banner)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Key Findings</b>", h2))
    row = Table([[stat("+1.2 °C", "warming since 1985"),
                  stat("-8%", "Sahel-zone rainfall vs baseline"),
                  stat("27 / 185", "ND-GAIN vulnerability rank")]],
                colWidths=[CONTENT_W / 3.0] * 3, hAlign="CENTER")
    row.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                             ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                             ("LEFTPADDING", (0, 0), (-1, -1), 4),
                             ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
    story.append(row)
    story.append(Spacer(1, 6))
    story.append(Paragraph("Every figure in this brief is footnoted with its source and URL. "
                           "In a real run all numbers are fetched live from the cited open "
                           "databases.", body))

    story.append(Paragraph("<b>1. Observed trends</b>", h2))
    story.append(Paragraph(
        "Mean annual temperature has risen steadily over the observation period, with the most "
        "recent decade the warmest on record (Figure 1). Rainfall shows growing year-to-year "
        "variability: the Sudanian zone receives a comparable annual total but concentrated in "
        "fewer, more intense events, extending the dry season at both ends (Figure 2).", body))
    story.append(Spacer(1, 6))
    story.append(KeepTogether([embed("chart_temperature.png"),
        Paragraph("Figure 1. Mean annual temperature, 1985-2024. Dashed line: linear trend.",
                  caption)]))
    story.append(Spacer(1, 8))
    story.append(KeepTogether([embed("chart_rainfall.png"),
        Paragraph("Figure 2. Monthly rainfall averages, recent decade vs 1985-2005 baseline.",
                  caption)]))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>2. Projections</b>", h2))
    story.append(Paragraph(
        "Under CMIP6 medium-emission scenarios, temperatures are projected to rise a further "
        "1.8-2.6 °C by 2060, with heavy-rainfall event intensity increasing while total annual "
        "rainfall remains uncertain. Heat-extreme days are projected to more than double by "
        "mid-century.", body))
    story.append(Paragraph("<b>3. Hazard exposure</b>", h2))
    story.append(Paragraph("• Drought: recurrent, affecting the Sahelian provinces most severely",
                           bullet))
    story.append(Paragraph("• Heat: extreme-heat days above 40 °C increasingly frequent", bullet))
    story.append(Paragraph("• Floods: flash flooding in urban areas during peak rainy season",
                           bullet))
    story.append(Paragraph("<b>4. Sector impacts</b>", h2))
    story.append(Paragraph(
        "Rain-fed agriculture, which engages the large majority of the workforce, is highly "
        "exposed to the growing rainfall variability; water resources and health (heat and "
        "vector-borne disease range) are secondary concern sectors.", body))
    story.append(Paragraph("<b>5. National response</b>", h2))
    story.append(Paragraph(
        "The updated NDC commits to conditional and unconditional mitigation and adaptation "
        "targets; the National Adaptation Plan prioritizes agriculture, water and livestock. "
        "Links to the registry submissions are cited in the annex.", body))

    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=0.6, color=BORDER, spaceAfter=6))
    story.append(Paragraph("<b>Sources (annex)</b>", h2))
    for s in [
        "1. NASA POWER agroclimatology API, monthly point data (Ouagadougou). "
        "power.larc.nasa.gov",
        "2. World Bank Climate Change Knowledge Portal, country climate data. "
        "climateknowledgeportal.worldbank.org",
        "3. ND-GAIN Country Index, vulnerability and readiness rankings. gain.nd.edu",
        "4. UNFCCC NDC Registry, Burkina Faso updated submission. unfccc.int/NDCREG",
    ]:
        story.append(Paragraph(s, foot))
    return story


def make_doc(target):
    doc = BaseDocTemplate(
        target, pagesize=A4,
        title="Climate Risk Profile - Burkina Faso (Mockup)", author="Z.ai", creator="Z.ai",
        subject="Layout mockup with illustrative data",
    )
    first_frame = Frame(MARGIN, BOTTOM, CONTENT_W,
                        PAGE_H - BAND_H - BOTTOM - 0.5 * cm, id="first")
    later_frame = Frame(MARGIN, BOTTOM, CONTENT_W,
                        PAGE_H - TOP_BAND_LATER - BOTTOM - 0.5 * cm, id="later")
    doc.addPageTemplates([
        PageTemplate(id="First", frames=[first_frame], onPage=on_first),
        PageTemplate(id="Later", frames=[later_frame], onPage=on_later),
    ])
    return doc


def count_pages():
    buf = io.BytesIO()
    make_doc(buf).build(make_story())
    return len(pymupdf.open(stream=buf.getvalue(), filetype="pdf"))


if __name__ == "__main__":
    TOTAL_PAGES[0] = count_pages()
    make_doc("mockup_climate_profile.pdf").build(make_story())
    print("pdf done, pages:", TOTAL_PAGES[0])
