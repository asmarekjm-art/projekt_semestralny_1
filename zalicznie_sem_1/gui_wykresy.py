# =================
# IMPORTY
# =================
import ttkbootstrap as ttkb
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane

import matplotlib.pyplot as plt
import pandas as pd


def create_tab_wykresy(parent, log):

    frame_top = ttk.Frame(parent)
    frame_top.pack(fill="x", pady=5)

    frame_plot = ttk.Frame(parent)
    frame_plot.pack(fill="both", expand=True)

    current_fig = {"fig": None}

    # =================
    # RENDER
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
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        df["bmi"].dropna().plot(kind="hist", bins=20, ax=ax)
        ax.set_title("Histogram BMI")

        pokaz(fig)

    def plec_bar():
        df = pobierz_df()
        if df is None or "plec" not in df.columns:
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        df["plec"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Płeć pacjentów")

        pokaz(fig)

    def nadcisnienie_bar():
        df = pobierz_df()
        if df is None or "nadcisnienie" not in df.columns:
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        df["nadcisnienie"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Nadciśnienie")

        pokaz(fig)

    def cukrzyca_bar():
        df = pobierz_df()
        if df is None or "cukrzyca_typ" not in df.columns:
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        df["cukrzyca_typ"].value_counts().plot(kind="bar", ax=ax)
        ax.set_title("Cukrzyca")

        pokaz(fig)

    def bmi_vs_wiek():
        df = pobierz_df()
        if df is None or not {"bmi", "wiek"}.issubset(df.columns):
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.scatter(df["wiek"], df["bmi"])
        ax.set_title("BMI vs wiek")
        ax.set_xlabel("Wiek")
        ax.set_ylabel("BMI")

        pokaz(fig)

    # =================
    # PRZYCISKI WYKRESÓW
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