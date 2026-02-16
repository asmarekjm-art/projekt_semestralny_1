import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

df = None
canvas = None

def wczytaj_dane():
    global df

    sciezka = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if not sciezka:
        return

    try:
        df = pd.read_csv(sciezka)
        pokaz(df)
    except Exception as e:
        messagebox.showerror("Błąd", str(e))
def filtruj_dane():
    global df

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    dane = df.copy()

    # ===== PŁEĆ =====
    plec = []
    if var_k.get():
        plec.append("K")
    if var_m.get():
        plec.append("M")

    if plec:
        dane = dane[dane["plec"].isin(plec)]

    # ===== WIEK =====
    try:
        if entry_min.get() != "":
            dane = dane[dane["wiek"] >= int(entry_min.get())]

        if entry_max.get() != "":
            dane = dane[dane["wiek"] <= int(entry_max.get())]

    except ValueError:
        messagebox.showwarning("Błąd", "Wiek musi być liczbą")
        return

    # ===== CUKRZYCA =====
    cuk = []
    if var_cuk_tak.get():
        cuk.append("tak")
    if var_cuk_nie.get():
        cuk.append("nie")

    if cuk:
        dane = dane[dane["cukrzyca"].isin(cuk)]

    # ===== NADCIŚNIENIE =====
    nad = []
    if var_nad_tak.get():
        nad.append("tak")
    if var_nad_nie.get():
        nad.append("nie")

    if nad:
        dane = dane[dane["nadcisnienie"].isin(nad)]

    pokaz(dane)


# ===== GUI =====
okno = tk.Tk()
...
okno.mainloop()