from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

import tempfile
import os


def raport_pdf(fig=None, opis="", tytul="Raport analizy"):

    path = "raport.pdf"

    # =================
    # FONT (polskie znaki)
    # =================
    try:
        pdfmetrics.registerFont(TTFont("DejaVu", "DejaVuSans.ttf"))
        font = "DejaVu"
    except:
        font = "Helvetica"

    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="TitleCustom",
        fontName=font,
        fontSize=18,
        spaceAfter=15
    ))

    styles.add(ParagraphStyle(
        name="NormalCustom",
        fontName=font,
        fontSize=11,
        leading=14
    ))

    doc = SimpleDocTemplate(path, pagesize=A4)

    story = []

    # =================
    # TYTUŁ
    # =================
    story.append(Paragraph(tytul, styles["TitleCustom"]))
    story.append(Spacer(1, 10))

    tmp_path = None

    try:
        # =================
        # WYKRES
        # =================
        if fig is not None:
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
            tmp_path = tmp.name
            tmp.close()

            fig.savefig(tmp_path, dpi=150, bbox_inches="tight")

            img = Image(tmp_path)
            img.drawWidth = 450
            img.drawHeight = 280

            story.append(img)
            story.append(Spacer(1, 20))

        # =================
        # OPIS / WNIOSKI
        # =================
        if opis:
            story.append(Paragraph("<b>Wnioski:</b>", styles["NormalCustom"]))
            story.append(Spacer(1, 8))
            story.append(Paragraph(opis, styles["NormalCustom"]))

        doc.build(story)

    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)

    return path