# =================
# IMPORTY
# =================

from tkinter import filedialog, messagebox
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from dane import get_dane

import matplotlib.pyplot as plt


# =================
# LOG (nadpisywany w gui)
# =================

log = print


# =================
# EKSPORT CSV
# =================

def eksport_csv():

    dane = get_dane()

    if dane is None or dane.empty:

        messagebox.showwarning(
            "Brak danych",
            "Nie ma danych do eksportu"
        )

        log("Eksport CSV przerwany – brak danych")

        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV", "*.csv")]
    )

    if not path:
        return

    try:

        dane.to_csv(path, index=False)

        log(f"CSV zapisany: {path}")

    except Exception as e:

        messagebox.showerror(
            "Błąd eksportu",
            str(e)
        )

        log("Błąd eksportu CSV")


# =================
# EKSPORT WYKRESU PNG
# =================

def eksport_png():

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG", "*.png")]
    )

    if not path:
        return

    try:

        plt.savefig(path)

        log(f"Wykres zapisany PNG: {path}")

    except Exception as e:

        messagebox.showerror(
            "Błąd",
            str(e)
        )

        log("Błąd zapisu PNG")


# =================
# EKSPORT WYKRESU PDF
# =================

def eksport_pdf():

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not path:
        return

    try:

        plt.savefig(path)

        log(f"Wykres zapisany PDF: {path}")

    except Exception as e:

        messagebox.showerror(
            "Błąd",
            str(e)
        )

        log("Błąd zapisu PDF")


# =================
# RAPORT PDF
# =================

def raport_pdf():

    dane = get_dane()

    if dane is None or dane.empty:

        messagebox.showwarning(
            "Brak danych",
            "Brak danych do raportu"
        )

        log("Raport PDF przerwany – brak danych")

        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF", "*.pdf")]
    )

    if not path:
        return

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Raport analizy pacjentów",
            styles["Title"]
        )
    )

    elements.append(Spacer(1,20))

    liczba = len(dane)

    elements.append(
        Paragraph(
            f"Liczba pacjentów: {liczba}",
            styles["Normal"]
        )
    )

    # =================
    # BMI
    # =================

    if "BMI" in dane.columns:

        bmi = dane["BMI"].mean()

        elements.append(
            Paragraph(
                f"Średnie BMI: {bmi:.2f}",
                styles["Normal"]
            )
        )

    # =================
    # CUKRZYCA
    # =================

    if "cukrzyca" in dane.columns:

        proc = (dane["cukrzyca"]=="tak").mean()*100

        elements.append(
            Paragraph(
                f"Cukrzyca w populacji: {proc:.1f}%",
                styles["Normal"]
            )
        )

    # =================
    # NADCIŚNIENIE
    # =================

    if "nadcisnienie" in dane.columns:

        proc = (dane["nadcisnienie"]=="tak").mean()*100

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

    komentarz = generuj_komentarz(dane)

    elements.append(
        Paragraph(
            "Komentarz analityczny:",
            styles["Heading2"]
        )
    )

    elements.append(
        Paragraph(
            komentarz,
            styles["Normal"]
        )
    )

    try:

        doc = SimpleDocTemplate(
            path,
            pagesize=A4
        )

        doc.build(elements)

        log(f"Raport PDF zapisany: {path}")

    except Exception as e:

        messagebox.showerror(
            "Błąd zapisu PDF",
            str(e)
        )

        log("Błąd zapisu raportu PDF")


# =================
# GENEROWANIE KOMENTARZA
# =================

def generuj_komentarz(dane):

    komentarz = []

    if "BMI" in dane.columns:

        bmi = dane["BMI"].mean()

        if bmi > 25:

            komentarz.append(
                "Średnie BMI wskazuje na nadwagę w badanej populacji."
            )

        else:

            komentarz.append(
                "Średnie BMI znajduje się w zakresie normy."
            )

    if "nadcisnienie" in dane.columns:

        proc = (dane["nadcisnienie"]=="tak").mean()*100

        if proc > 30:

            komentarz.append(
                "Wysoki odsetek nadciśnienia może wskazywać na zwiększone ryzyko chorób sercowo-naczyniowych."
            )

    if "cukrzyca" in dane.columns:

        proc = (dane["cukrzyca"]=="tak").mean()*100

        if proc > 15:

            komentarz.append(
                "Odsetek cukrzycy jest stosunkowo wysoki i może wymagać dalszej analizy populacji."
            )

    if not komentarz:

        komentarz.append(
            "Nie wykryto istotnych odchyleń w analizowanych parametrach."
        )

    return " ".join(komentarz)