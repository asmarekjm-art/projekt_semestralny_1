# =================
# IMPORTY
# =================

from tkinter import filedialog
from datetime import datetime

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from dane import get_dane

import matplotlib.pyplot as plt


# =================
# LOG (nadpisywany w gui)
# =================

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# EKSPORT CSV
# =================

def eksport_csv():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Eksport CSV przerwany – brak danych", "ERROR")
        return

    path = filedialog.asksaveasfilename(
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
# ZAPIS WYKRESU
# =================

def zapisz_wykres(ext):

    fig = plt.gcf()

    if fig is None or not fig.get_axes():
        log("Brak wykresu do zapisania", "ERROR")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=ext,
        filetypes=[(ext.upper(), f"*{ext}")]
    )

    if not path:
        log("Zapis wykresu anulowany")
        return

    try:

        fig.savefig(path, dpi=300)

        log(f"Wykres zapisany: {path}")

    except Exception as e:

        log(f"Błąd zapisu wykresu: {e}", "ERROR")


def eksport_wykres_png():
    zapisz_wykres(".png")


def eksport_wykres_pdf():
    zapisz_wykres(".pdf")


# =================
# RAPORT PDF
# =================

def raport_pdf():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Raport PDF przerwany – brak danych", "ERROR")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not path:
        log("Zapis raportu anulowany")
        return

    styles = getSampleStyleSheet()
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

    elements.append(Spacer(1,20))

    # =================
    # PODSTAWOWE STATYSTYKI
    # =================

    elements.append(
        Paragraph(f"Liczba pacjentów: {len(dane)}", styles["Normal"])
    )

    if "wiek" in dane.columns:
        elements.append(
            Paragraph(
                f"Średni wiek: {dane['wiek'].mean():.1f}",
                styles["Normal"]
            )
        )

    if "BMI" in dane.columns:
        elements.append(
            Paragraph(
                f"Średnie BMI: {dane['BMI'].mean():.2f}",
                styles["Normal"]
            )
        )

    if "cukrzyca" in dane.columns:

        proc = (dane["cukrzyca"] == "tak").mean() * 100

        elements.append(
            Paragraph(
                f"Cukrzyca w populacji: {proc:.1f}%",
                styles["Normal"]
            )
        )

    if "nadcisnienie" in dane.columns:

        proc = (dane["nadcisnienie"] == "tak").mean() * 100

        elements.append(
            Paragraph(
                f"Nadciśnienie w populacji: {proc:.1f}%",
                styles["Normal"]
            )
        )

    elements.append(Spacer(1,20))

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

    try:

        doc = SimpleDocTemplate(
            path,
            pagesize=A4
        )

        doc.build(elements)

        log(f"Raport PDF zapisany: {path}")

    except Exception as e:

        log(f"Błąd zapisu raportu PDF: {e}", "ERROR")


# =================
# GENEROWANIE KOMENTARZA
# =================

def generuj_komentarz(dane):

    komentarz = []

    if "BMI" in dane.columns:

        bmi = dane["BMI"].mean()

        if bmi > 30:

            komentarz.append(
                "Średnie BMI wskazuje na otyłość w analizowanej populacji."
            )

        elif bmi > 25:

            komentarz.append(
                "Średnie BMI wskazuje na nadwagę w analizowanej populacji."
            )

        else:

            komentarz.append(
                "Średnie BMI znajduje się w zakresie normy."
            )

    if "nadcisnienie" in dane.columns:

        proc = (dane["nadcisnienie"] == "tak").mean() * 100

        if proc > 30:

            komentarz.append(
                "Wysoki odsetek nadciśnienia może wskazywać na zwiększone ryzyko chorób sercowo-naczyniowych."
            )

    if "cukrzyca" in dane.columns:

        proc = (dane["cukrzyca"] == "tak").mean() * 100

        if proc > 15:

            komentarz.append(
                "Odsetek cukrzycy jest stosunkowo wysoki i może wymagać dalszej analizy populacji."
            )

    if not komentarz:

        komentarz.append(
            "Nie wykryto istotnych odchyleń w analizowanych parametrach."
        )

    return " ".join(komentarz)