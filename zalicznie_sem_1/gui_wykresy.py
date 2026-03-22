from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile
import os


def generuj_raport(fig, opis, tytul="Raport analizy"):

    path = "raport.pdf"

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    story = []

    # Tytuł
    story.append(Paragraph(f"<b>{tytul}</b>", styles["Title"]))
    story.append(Spacer(1, 20))

    # zapis wykresu tymczasowo
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
    fig.savefig(tmp.name)

    # dodanie obrazu
    story.append(Image(tmp.name, width=400, height=250))
    story.append(Spacer(1, 20))

    # opis
    story.append(Paragraph(f"<b>Wnioski:</b><br/>{opis}", styles["Normal"]))

    doc.build(story)

    os.unlink(tmp.name)

    return path