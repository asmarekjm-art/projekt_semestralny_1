import ttkbootstrap as ttkb
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def create_tab_analiza(parent, log):

    # =================
    # LAYOUT
    # =================
    frame_top = ttk.Frame(parent)
    frame_top.pack(fill="x", pady=5)

    frame_wykres = ttk.Frame(parent)
    frame_wykres.pack(fill="both", expand=True)

    frame_wynik = ttk.LabelFrame(parent, text="📊 Wyniki")
    frame_wynik.pack(fill="x", padx=10, pady=5)

    label_wynik = ttk.Label(frame_wynik, text="", justify="left")
    label_wynik.pack(anchor="w", padx=5, pady=5)

    canvas_holder = {"canvas": None}

    # =================
    # RENDER
    # =================
    def pokaz(fig):
        for w in frame_wykres.winfo_children():
            w.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_wykres)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        canvas_holder["canvas"] = canvas

    # =================
    # POMOCNICZE
    # =================
    def brak_danych():
        log("Brak danych — wczytaj bazę", "WARNING")
        label_wynik.config(text="Brak danych")

    # =================
    # 1️⃣ GAUSS
    # =================
    def rozklad_gaussa():
        df = get_dane()
        if df is None or df.empty:
            brak_danych()
            return

        if "bmi" not in df.columns:
            log("Brak kolumny BMI", "ERROR")
            return

        data = df["bmi"].dropna()
        if data.empty:
            brak_danych()
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.hist(data, bins=20, density=True)

        mu, std = stats.norm.fit(data)
        x = np.linspace(min(data), max(data), 100)
        p = stats.norm.pdf(x, mu, std)

        ax.plot(x, p)
        ax.set_title("Rozkład Gaussa BMI")

        pokaz(fig)

        label_wynik.config(
            text=f"Średnia: {mu:.2f}\nOdchylenie: {std:.2f}"
        )

        log("Wygenerowano rozkład Gaussa")

    # =================
    # 2️⃣ T-TEST
    # =================
    def test_t():
        df = get_dane()
        if df is None or df.empty:
            brak_danych()
            return

        if not {"plec", "bmi"}.issubset(df.columns):
            log("Brak wymaganych kolumn (plec, bmi)", "ERROR")
            return

        k = df[df["plec"] == "K"]["bmi"].dropna()
        m = df[df["plec"] == "M"]["bmi"].dropna()

        if k.empty or m.empty:
            brak_danych()
            return

        t, p = stats.ttest_ind(k, m)

        wynik = "Istotna różnica (p < 0.05)" if p < 0.05 else "Brak istotnej różnicy"

        label_wynik.config(
            text=f"TEST T-STUDENTA\n\n"
                 f"t = {t:.3f}\n"
                 f"p = {p:.5f}\n\n"
                 f"Wniosek: {wynik}"
        )

        log("Wykonano test t-Studenta")

    # =================
    # 3️⃣ CHI-KWADRAT
    # =================
    def chi_kwadrat():
        df = get_dane()
        if df is None or df.empty:
            brak_danych()
            return

        if not {"plec", "nadcisnienie"}.issubset(df.columns):
            log("Brak kolumn (plec, nadcisnienie)", "ERROR")
            return

        tab = pd.crosstab(df["plec"], df["nadcisnienie"])

        if tab.empty:
            brak_danych()
            return

        chi2, p, _, _ = stats.chi2_contingency(tab)

        wynik = "Zależność istotna" if p < 0.05 else "Brak zależności"

        label_wynik.config(
            text=f"TEST CHI²\n\n"
                 f"Chi² = {chi2:.3f}\n"
                 f"p = {p:.5f}\n\n"
                 f"Wniosek: {wynik}"
        )

        log("Wykonano test chi-kwadrat")

    # =================
    # 4️⃣ BOXPLOT
    # =================
    def boxplot():
        df = get_dane()
        if df is None or df.empty:
            brak_danych()
            return

        if "bmi" not in df.columns:
            log("Brak kolumny BMI", "ERROR")
            return

        data = df["bmi"].dropna()
        if data.empty:
            brak_danych()
            return

        fig = plt.Figure(figsize=(5, 4))
        ax = fig.add_subplot(111)

        ax.boxplot(data)
        ax.set_title("Boxplot BMI")

        pokaz(fig)

        label_wynik.config(text="Boxplot BMI — wykrywanie wartości odstających")

        log("Wygenerowano boxplot")

    # =================
    # PRZYCISKI
    # =================
    ttk.Button(frame_top, text="Gauss", command=rozklad_gaussa).pack(side="left", padx=5)
    ttk.Button(frame_top, text="t-test", command=test_t).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Chi²", command=chi_kwadrat).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Boxplot", command=boxplot).pack(side="left", padx=5)