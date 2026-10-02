"""One-page palette preview: current UN blue vs proposed Corporate Navy."""
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import registerFontFamily
from PIL import Image as PILImage

FONT_DIR = "../fonts/"
pdfmetrics.registerFont(TTFont("Roboto Condensed", FONT_DIR + "RobotoCondensed-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Roboto Condensed Bold", FONT_DIR + "RobotoCondensed-Bold.ttf"))
pdfmetrics.registerFont(TTFont("Roboto Condensed Italic", FONT_DIR + "RobotoCondensed-Italic.ttf"))
registerFontFamily("Roboto Condensed", normal="Roboto Condensed",
                   bold="Roboto Condensed Bold", italic="Roboto Condensed Italic",
                   boldItalic="Roboto Condensed Bold")

W, H = A4
M = 1.6 * cm
CW = W - 2 * M

label = ParagraphStyle("label", fontName="Roboto Condensed Bold", fontSize=10,
                       leading=13, textColor=colors.HexColor("#20201d"), spaceBefore=8,
                       spaceAfter=4)
hexnote = ParagraphStyle("hex", fontName="Roboto Condensed", fontSize=8.5, leading=11,
                         textColor=colors.HexColor("#8b8982"), spaceAfter=8)

# masthead band sample: 1.9cm tall, drawn via Table background
def band(bg, divider):
    t = Table([[Paragraph('<font color="white"><b>COUNTRY BRIEF</b></font>',
                          ParagraphStyle("k", fontName="Roboto Condensed Bold", fontSize=8,
                                         leading=10, textColor=colors.white))],
               [Paragraph('<font color="white"><b>Climate Risk Profile</b></font>',
                          ParagraphStyle("h", fontName="Roboto Condensed Bold", fontSize=17,
                                         leading=21, textColor=colors.white))],
               [Paragraph('<font color="white">Burkina Faso  |  Drought & '
                          'Agriculture Focus</font>',
                          ParagraphStyle("s", fontName="Roboto Condensed", fontSize=10,
                                         leading=13, textColor=colors.white))]],
              colWidths=[CW])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("LINEBELOW", (0, -1), (-1, -1), 2.5, divider),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, 0), (-1, 0), 2),
        ("TOPPADDING", (0, 1), (-1, 1), 0), ("BOTTOMPADDING", (0, 1), (-1, 1), 0),
        ("TOPPADDING", (0, 2), (-1, 2), 1), ("BOTTOMPADDING", (0, 2), (-1, 2), 8),
    ]))
    return t

def stat(v, l, head, fill, border):
    st = ParagraphStyle("sv", fontName="Roboto Condensed Bold", fontSize=14, leading=17,
                        textColor=colors.HexColor(head), alignment=TA_CENTER)
    lb = ParagraphStyle("sl", fontName="Roboto Condensed", fontSize=8, leading=10,
                        textColor=colors.HexColor("#8b8982"), alignment=TA_CENTER)
    t = Table([[Paragraph("<b>%s</b>" % v, st)], [Paragraph(l, lb)]],
              colWidths=[(CW - 40) / 3.0])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(fill)),
        ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor(border)),
        ("LINEABOVE", (0, 0), (-1, 0), 2, colors.HexColor(head)),
        ("TOPPADDING", (0, 0), (-1, 0), 6), ("BOTTOMPADDING", (0, -1), (-1, -1), 6),
    ]))
    return t

def statrow(head, fill, border):
    r = Table([[stat("+1.2 °C", "warming since 1985", head, fill, border),
                stat("-8%", "rainfall vs baseline", head, fill, border),
                stat("27 / 185", "vulnerability rank", head, fill, border)]],
              colWidths=[CW / 3.0] * 3, hAlign="CENTER")
    r.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 5),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 5)]))
    return r

def img(path):
    w, h = PILImage.open(path).size
    return Image(path, width=CW * 0.8, height=h * (CW * 0.8) / w)

doc = SimpleDocTemplate("palette_preview.pdf", pagesize=A4,
                        leftMargin=M, rightMargin=M, topMargin=M, bottomMargin=M,
                        title="Palette preview - Corporate Navy vs UN blue",
                        author="Z.ai", creator="Z.ai")
story = []
story.append(Paragraph("<b>Palette preview — choose the document look</b>",
                       ParagraphStyle("t", fontName="Roboto Condensed Bold", fontSize=14,
                                      leading=18, spaceAfter=10)))

story.append(Paragraph("A. CURRENT — UN blue (reads as a UN document)", label))
story.append(band(colors.HexColor("#009EDB"), colors.HexColor("#0077B0")))
story.append(Paragraph("#009EDB band · #03679B headings", hexnote))

story.append(Spacer(1, 8))
story.append(Paragraph("B. PROPOSED — Corporate Navy (international-corporate, not UN)",
                       label))
story.append(band(colors.HexColor("#24356B"), colors.HexColor("#1B2852")))
story.append(Spacer(1, 6))
story.append(statrow("#1F3A7A", "#EEF1F8", "#C5CEDF"))
story.append(Paragraph("#24356B band · #1F3A7A headings · #3D5A99 charts · "
                       "#EEF1F8 card fills", hexnote))
story.append(Spacer(1, 8))
story.append(img("chart_navy_sample.png"))
story.append(Paragraph("Sample chart in the navy family (bars #3D5A99, baseline warm grey).",
                       hexnote))
doc.build(story)
print("preview done")
