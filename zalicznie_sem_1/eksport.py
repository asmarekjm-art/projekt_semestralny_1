# =================
# IMPORTY
# =================

from tkinter import filedialog, messagebox
from dane import get_dane
import wykresy


# =================
# EKSPORT CSV
# =================

def eksport_csv():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not path:
        return

    dane.to_csv(path, index=False)

    log("Dane zapisane do CSV")


# =================
# EKSPORT WYKRESU PNG
# =================

def eksport_png():

    if wykresy.current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG image", "*.png")]
    )

    if not path:
        return

    wykresy.current_fig.savefig(path, dpi=300)

    log("Wykres zapisany jako PNG")


# =================
# EKSPORT WYKRESU PDF
# =================

def eksport_pdf():

    if wykresy.current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF file", "*.pdf")]
    )

    if not path:
        return

    wykresy.current_fig.savefig(path)

    messagebox.showinfo("Sukces", "Wykres zapisany jako PDF")