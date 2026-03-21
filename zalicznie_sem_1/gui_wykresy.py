# =================
# IMPORTY
# =================
import ttkbootstrap as ttkb
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane

import matplotlib.pyplot as plt
import pandas as pd


# =================
# STYL WYKRESÓW
# =================
def styl(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.5)


# =================
# GŁÓWNA FUNKCJA
# =================
def create_tab_wykresy(parent, log):

    frame_top = ttk.Frame(parent)
    frame_top.pack(fill="x", pady=5)

    frame_plot = ttk.Frame(parent)
    frame_plot.pack(fill="both", expand=True)

    label_info = ttk.Label(parent, text="", anchor="w")
    label_info.pack(fill="x", padx=10, pady=5)

    current_fig = {"fig": None}


    # =================
    # POMOCNICZE
    # =================
    def pokaz(fig):
        for w in frame_plot.winfo_children():
            w.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_plot)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        current_fig["fig"] = fig

    def pobierz_df():
        df = get_dane()
        if df is None or df.empty:
            log("Brak danych — wczytaj bazę", "WARNING")
            return None
        return df


    # =================
    # WYKRESY
    # =================

    def hist_bmi():
        df = pobierz_df()
        if df is None or "bmi" not in df.columns:
            log("Brak kolumny BMI", "ERROR")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        data = df["bmi"].dropna()

        ax.hist(data, bins=20)

        styl(ax, "Rozkład BMI pacjentów", "BMI", "Liczba pacjentów")
        pokaz(fig)

        srednia = round(data.mean(), 1)
        label_info.config(text=f"Średnie BMI: {srednia}")


    def plec_bar():
        df = pobierz_df()
        if df is None or "plec" not in df.columns:
            log("Brak kolumny płeć", "ERROR")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        counts = df["plec"].value_counts()
        counts.plot(kind="bar", ax=ax)

        styl(ax, "Struktura płci pacjentów", "Płeć", "Liczba")
        pokaz(fig)

        label_info.config(text=f"Liczba kategorii: {len(counts)}")


    def nadcisnienie_bar():
        df = pobierz_df()
        if df is None or "nadcisnienie" not in df.columns:
            log("Brak kolumny nadciśnienie", "ERROR")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        counts = df["nadcisnienie"].value_counts()
        counts.plot(kind="bar", ax=ax)

        styl(ax, "Występowanie nadciśnienia", "Status", "Liczba")
        pokaz(fig)

        proc = round((counts.get("tak", 0) / len(df)) * 100, 1)
        label_info.config(text=f"Nadciśnienie u {proc}% pacjentów")


    def cukrzyca_bar():
        df = pobierz_df()
        if df is None:
            return

        col = None
        for c in df.columns:
            if "cukr" in c.lower():
                col = c
                break

        if col is None:
            log("Nie znaleziono kolumny cukrzyca", "ERROR")
            label_info.config(text="Brak danych o cukrzycy")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        counts = df[col].value_counts()
        counts.plot(kind="bar", ax=ax)

        styl(ax, "Typy cukrzycy w badanej grupie", "Typ", "Liczba pacjentów")
        pokaz(fig)

        tekst = "Rozkład cukrzycy: "
        tekst += ", ".join([f"{k}: {v}" for k, v in counts.items()])
        label_info.config(text=tekst)


    # 🔥 NOWA FUNKCJA (bo jej brakowało)
    def bmi_vs_wiek():
        df = pobierz_df()
        if df is None or "bmi" not in df.columns or "wiek" not in df.columns:
            log("Brak kolumn BMI lub wiek", "ERROR")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.scatter(df["wiek"], df["bmi"])

        styl(ax, "BMI vs wiek", "Wiek", "BMI")
        pokaz(fig)

        label_info.config(text="Zależność BMI od wieku (scatter)")


    # =================
    # PRZYCISKI
    # =================
    ttk.Button(frame_top, text="Histogram BMI", command=hist_bmi).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Płeć", command=plec_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Nadciśnienie", command=nadcisnienie_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Cukrzyca", command=cukrzyca_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="BMI vs wiek", command=bmi_vs_wiek).pack(side="left", padx=5)


    # =================
    # ZAPIS
    # =================
    def zapisz_png():
        if current_fig["fig"] is None:
            log("Najpierw wygeneruj wykres!", "WARNING")
            return

        path = filedialog.asksaveasfilename(defaultextension=".png")
        if path:
            current_fig["fig"].savefig(path)
            log("Zapisano PNG")


    def zapisz_pdf():
        if current_fig["fig"] is None:
            log("Najpierw wygeneruj wykres!", "WARNING")
            return

        path = filedialog.asksaveasfilename(defaultextension=".pdf")
        if path:
            current_fig["fig"].savefig(path)
            log("Zapisano PDF")


    ttk.Button(frame_top, text="Zapisz PNG", command=zapisz_png).pack(side="right", padx=5)
    ttk.Button(frame_top, text="Zapisz PDF", command=zapisz_pdf).pack(side="right", padx=5)