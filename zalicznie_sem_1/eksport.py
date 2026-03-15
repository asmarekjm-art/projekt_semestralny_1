# =================
# IMPORTY
# =================

from tkinter import filedialog, messagebox
from datetime import datetime
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

from dane import df, df_filtered
from wykresy import current_fig, current_data, current_title


# =================
# EKSPORT CSV
# =================

def eksport_csv():

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    dane_do_zapisu = df_filtered if df_filtered is not None else df

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not path:
        return

    dane_do_zapisu.to_csv(path, index=False)

    messagebox.showinfo(
        "Sukces",
        f"Zapisano {len(dane_do_zapisu)} rekordów"
    )


# =================
# EKSPORT PNG
# =================

def eksport_png():

    if current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )

    if not path:
        return

    current_fig.savefig(path, dpi=300, bbox_inches="tight")

    messagebox.showinfo(
        "Sukces",
        f"Wykres zapisany:\n{path}"
    )


# =================
# EKSPORT PDF
# =================

def eksport_pdf():

    if current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not path:
        return

    # zapis wykresu do pamięci
    img_buffer = BytesIO()

    current_fig.savefig(
        img_buffer,
        format="png",
        dpi=300,
        bbox_inches="tight"
    )

    img_buffer.seek(0)

    doc = SimpleDocTemplate(path, pagesize=A4)

    styles = getSampleStyleSheet()

    elements = []

    # tytuł raportu
    elements.append(
        Paragraph(
            "Raport analizy danych pacjentów",
            styles["Heading1"]
        )
    )

    elements.append(Spacer(1, 12))

    # tytuł wykresu
    elements.append(
        Paragraph(
            f"<b>{current_title}</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 12))

    # data raportu
    elements.append(
        Paragraph(
            f"Data raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # wykres
    img = Image(img_buffer)

    img.drawHeight = 300
    img.drawWidth = 450

    elements.append(img)

    elements.append(Spacer(1, 20))

    # statystyki
    if current_data is not None:

        liczba = len(current_data)

        tekst = f"Liczba pacjentów w analizie: {liczba}"

        if "wiek" in current_data.columns:
            tekst += f"<br/>Średni wiek: {current_data['wiek'].mean():.1f}"

        if "BMI" in current_data.columns:
            tekst += f"<br/>Średnie BMI: {current_data['BMI'].mean():.1f}"

        elements.append(
            Paragraph(
                tekst,
                styles["Normal"]
            )
        )

    doc.build(elements)

    messagebox.showinfo(
        "Sukces",
        f"Raport zapisany:\n{path}"
    )