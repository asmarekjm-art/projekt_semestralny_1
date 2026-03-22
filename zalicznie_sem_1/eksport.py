# =================
# IMPORTY
# =================
from tkinter import filedialog
from datetime import datetime
import os

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from dane import get_dane

import matplotlib.pyplot as plt


# =================
# FONT (polskie znaki)
# =================
try:
    pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
except:
    pass


# =================
# LOG
# =================
def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# 🔥 UNIWERSALNY ZAPIS WYKRESU
# =================
def zapisz_figure(fig, log):

    if fig is None:
        log("Brak wykresu!", "WARNING")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[
            ("PNG", "*.png"),
            ("PDF", "*.pdf")
        ]
    )

    if not path:
        return

    try:
        fig.savefig(path, dpi=300)
        log(f"Zapisano: {path}")
    except Exception as e:
        log(f"Błąd zapisu: {e}", "ERROR")


# =================
# EKSPORT CSV
# =================
def eksport_csv():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Eksport CSV przerwany – brak danych", "ERROR")
        return

    path = filedialog.asksaveasfilename(
        initialfile=f"dane_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )

    if not path:
        log("Eksport CSV anulowany")
        return

    try:
        dane.to_csv(path, index=False)
        log(f"CSV zapisany: {path}")

    except Exception as e:
        log(f"Błąd eksportu CSV: {e}", "ERROR")


# =================
# RAPORT PDF
# =================
def raport_pdf():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Raport PDF przerwany – brak danych", "ERROR")
        return

    path = filedialog.asksaveasfilename(
        initialfile=f"raport_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not path:
        log("Zapis raportu anulowany")
        return

    styles = getSampleStyleSheet()

    for style in ["Normal", "Title", "Heading2"]:
        styles[style].fontName = "DejaVu"

    elements = []

    # =================
    # TYTUŁ
    # =================
    elements.append(
        Paragraph("Raport analizy danych pacjentów", styles["Title"])
    )

    elements.append(
        Paragraph(
            f"Data wygenerowania raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # =================
    # WNIOSKI
    # =================
    wnioski = []

    if "bmi" in dane.columns:
        bmi_mean = round(dane["bmi"].mean(), 2)
        wnioski.append(f"Średnie BMI: {bmi_mean}")

        if bmi_mean > 25:
            wnioski.append("Pacjenci mają tendencję do nadwagi.")

    if "wiek" in dane.columns:
        wiek_mean = round(dane["wiek"].mean(), 1)
        wnioski.append(f"Średni wiek: {wiek_mean}")

    elements.append(Paragraph("Wnioski:", styles["Heading2"]))

    for w in wnioski:
        elements.append(Paragraph(f"- {w}", styles["Normal"]))

    elements.append(Spacer(1, 20))

    # =================
    # STATYSTYKI
    # =================
    elements.append(
        Paragraph(f"Liczba pacjentów: {len(dane)}", styles["Normal"])
    )

    if "wiek" in dane.columns:
        elements.append(
            Paragraph(f"Średni wiek: {dane['wiek'].mean():.1f}", styles["Normal"])
        )

    if "bmi" in dane.columns:
        elements.append(
            Paragraph(f"Średnie BMI: {dane['bmi'].mean():.2f}", styles["Normal"])
        )

    elements.append(Spacer(1, 20))

    # =================
    # WYKRES
    # =================
    try:
        fig = plt.gcf()

        if fig and fig.get_axes():
            temp_path = "temp_plot.png"
            fig.savefig(temp_path, dpi=300)

            elements.append(Paragraph("Wykres:", styles["Heading2"]))
            elements.append(Image(temp_path, width=400, height=300))
            elements.append(Spacer(1, 20))

    except Exception as e:
        log(f"Nie udało się dodać wykresu: {e}", "ERROR")

    # =================
    # KOMENTARZ
    # =================
    elements.append(
        Paragraph("Komentarz analityczny", styles["Heading2"])
    )

    komentarz = generuj_komentarz(dane)

    elements.append(
        Paragraph(komentarz, styles["Normal"])
    )

    # =================
    # ZAPIS
    # =================
    try:
        doc = SimpleDocTemplate(path, pagesize=A4)
        doc.build(elements)

        if os.path.exists("temp_plot.png"):
            os.remove("temp_plot.png")

        log(f"Raport PDF zapisany: {path}")

    except Exception as e:
        log(f"Błąd zapisu raportu PDF: {e}", "ERROR")


# =================
# KOMENTARZ
# =================
def generuj_komentarz(dane):

    komentarz = []

    if "bmi" in dane.columns:
        bmi = dane["bmi"].mean()

        if bmi > 30:
            komentarz.append("BMI wskazuje na otyłość.")
        elif bmi > 25:
            komentarz.append("BMI wskazuje na nadwagę.")
        else:
            komentarz.append("BMI w normie.")

    if "nadcisnienie" in dane.columns:
        proc = (dane["nadcisnienie"].fillna("nie") == "tak").mean() * 100
        if proc > 30:
            komentarz.append("Wysoki poziom nadciśnienia.")

    if "cukrzyca" in dane.columns:
        proc = (dane["cukrzyca"].fillna("nie") == "tak").mean() * 100
        if proc > 15:
            komentarz.append("Podwyższony poziom cukrzycy.")

    if "wiek" in dane.columns and "bmi" in dane.columns:
        try:
            korelacja = dane["wiek"].corr(dane["bmi"])
            komentarz.append(f"Korelacja wiek-BMI: {korelacja:.2f}")
        except:
            pass

    if not komentarz:
        komentarz.append("Brak istotnych odchyleń.")

    # =================
    # 🔥 ZAPIS (CSV lub PDF)
    # =================
def zapisz_dane_lub_raport(log):

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[
            ("CSV (dane)", "*.csv"),
            ("PDF (raport)", "*.pdf")
        ]
    )

    if not path:
        return

    if path.endswith(".csv"):
        eksport_csv()
    elif path.endswith(".pdf"):
        raport_pdf()

    return " ".join(komentarz)