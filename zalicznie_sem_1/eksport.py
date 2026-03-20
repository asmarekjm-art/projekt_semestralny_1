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
# USUWANIE POLSKICH ZNAKÓW
# =================
def usun_polskie_znaki(tekst):
    znaki = {
        "ą": "a", "ć": "c", "ę": "e", "ł": "l",
        "ń": "n", "ó": "o", "ś": "s", "ż": "z", "ź": "z",
        "Ą": "A", "Ć": "C", "Ę": "E", "Ł": "L",
        "Ń": "N", "Ó": "O", "Ś": "S", "Ż": "Z", "Ź": "Z"
    }

    for pl, en in znaki.items():
        tekst = tekst.replace(pl, en)

    return tekst


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
        fig.tight_layout()
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
        Paragraph(usun_polskie_znaki("Raport analizy danych pacjentów"), styles["Title"])
    )

    elements.append(
        Paragraph(
            usun_polskie_znaki(
                f"Data wygenerowania raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            ),
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
        wnioski.append(f"Srednie BMI: {bmi_mean}")

        if bmi_mean > 25:
            wnioski.append("Pacjenci maja tendencje do nadwagi.")

    if "wiek" in dane.columns:
        wiek_mean = round(dane["wiek"].mean(), 1)
        wnioski.append(f"Sredni wiek: {wiek_mean}")

    elements.append(
        Paragraph(usun_polskie_znaki("Wnioski:"), styles["Heading2"])
    )

    for w in wnioski:
        elements.append(
            Paragraph(usun_polskie_znaki(f"- {w}"), styles["Normal"])
        )

    elements.append(Spacer(1, 20))

    # =================
    # STATYSTYKI
    # =================
    elements.append(
        Paragraph(usun_polskie_znaki(f"Liczba pacjentow: {len(dane)}"), styles["Normal"])
    )

    if "wiek" in dane.columns:
        elements.append(
            Paragraph(
                usun_polskie_znaki(f"Sredni wiek: {dane['wiek'].mean():.1f}"),
                styles["Normal"]
            )
        )

    if "bmi" in dane.columns:
        elements.append(
            Paragraph(
                usun_polskie_znaki(f"Srednie BMI: {dane['bmi'].mean():.2f}"),
                styles["Normal"]
            )
        )

    if "cukrzyca" in dane.columns:
        proc = (dane["cukrzyca"] == "tak").mean() * 100
        elements.append(
            Paragraph(
                usun_polskie_znaki(f"Cukrzyca w populacji: {proc:.1f}%"),
                styles["Normal"]
            )
        )

    if "nadcisnienie" in dane.columns:
        proc = (dane["nadcisnienie"] == "tak").mean() * 100
        elements.append(
            Paragraph(
                usun_polskie_znaki(f"Nadcisnienie w populacji: {proc:.1f}%"),
                styles["Normal"]
            )
        )

    elements.append(Spacer(1, 20))

    # =================
    # PRZYKŁADOWE DANE
    # =================
    elements.append(
        Paragraph(usun_polskie_znaki("Przykladowe dane:"), styles["Heading2"])
    )

    sample = dane.head(5)

    for _, row in sample.iterrows():
        tekst = ", ".join([f"{col}: {row[col]}" for col in sample.columns])
        elements.append(
            Paragraph(usun_polskie_znaki(tekst), styles["Normal"])
        )

    elements.append(Spacer(1, 20))

    # =================
    # KOMENTARZ
    # =================
    elements.append(
        Paragraph(usun_polskie_znaki("Komentarz analityczny"), styles["Heading2"])
    )

    komentarz = generuj_komentarz(dane)

    elements.append(
        Paragraph(usun_polskie_znaki(komentarz), styles["Normal"])
    )

    try:
        doc = SimpleDocTemplate(path, pagesize=A4)
        doc.build(elements)
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
            komentarz.append("BMI wskazuje na otylosc.")
        elif bmi > 25:
            komentarz.append("BMI wskazuje na nadwage.")
        else:
            komentarz.append("BMI w normie.")

    if "nadcisnienie" in dane.columns:
        proc = (dane["nadcisnienie"] == "tak").mean() * 100
        if proc > 30:
            komentarz.append("Wysoki poziom nadcisnienia.")

    if "cukrzyca" in dane.columns:
        proc = (dane["cukrzyca"] == "tak").mean() * 100
        if proc > 15:
            komentarz.append("Podwyzszony poziom cukrzycy.")

    if not komentarz:
        komentarz.append("Brak istotnych odchylen.")

    return " ".join(komentarz)