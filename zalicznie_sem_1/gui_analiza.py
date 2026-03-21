# =================
# IMPORTY
# =================
import ttkbootstrap as ttkb
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def create_tab_analiza(parent, log):

    notebook = ttk.Notebook(parent)
    notebook.pack(fill="both", expand=True)

    tab_gauss = ttk.Frame(notebook)
    tab_t = ttk.Frame(notebook)
    tab_chi = ttk.Frame(notebook)

    notebook.add(tab_gauss, text="Gauss")
    notebook.add(tab_t, text="t-Studenta")
    notebook.add(tab_chi, text="Chi²")

    current_fig = {"fig": None}

    # 🔥 WNIOSKI POD WYKRESEM
    label_info = ttk.Label(parent, text="", anchor="w")
    label_info.pack(fill="x", padx=10, pady=5)

    # =================
    # POMOCNICZE
    # =================
    def pobierz_df():
        df = get_dane()
        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return None
        return df

    def pokaz(fig, frame):
        for w in frame.winfo_children():
            w.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        current_fig["fig"] = fig

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

    # =================
    # GAUSS
    # =================
    frame_gauss = ttk.Frame(tab_gauss)
    frame_gauss.pack(fill="both", expand=True)

    combo_gauss = ttk.Combobox(tab_gauss, state="readonly")
    combo_gauss.pack(pady=5)

    def gauss_plot():
        df = pobierz_df()
        if df is None:
            return

        col = combo_gauss.get()
        if col == "":
            return

        data = df[col].dropna()

        if data.empty:
            log("Brak danych", "WARNING")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.hist(data, bins=20, density=True)

        mu, std = stats.norm.fit(data)
        x = np.linspace(min(data), max(data), 100)
        y = stats.norm.pdf(x, mu, std)

        ax.plot(x, y)
        ax.set_title(f"Rozkład: {col}")

        pokaz(fig, frame_gauss)

        label_info.config(
            text=f"Średnia: {round(mu,2)}, odchylenie: {round(std,2)} → rozkład zbliżony do normalnego"
        )

    combo_gauss.bind("<<ComboboxSelected>>", lambda e: gauss_plot())

    # =================
    # T-TEST
    # =================
    frame_t = ttk.Frame(tab_t)
    frame_t.pack(fill="both", expand=True)

    combo_t = ttk.Combobox(tab_t, state="readonly")
    combo_t.pack(pady=5)

    def t_plot():
        df = pobierz_df()
        if df is None:
            return

        col = combo_t.get()
        if col == "" or "plec" not in df.columns:
            log("Brak danych do testu t", "ERROR")
            return

        k = df[df["plec"] == "K"][col].dropna()
        m = df[df["plec"] == "M"][col].dropna()

        if len(k) < 2 or len(m) < 2:
            log("Za mało danych", "WARNING")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        ax.boxplot([k, m], labels=["K", "M"])
        ax.set_title(f"{col} vs płeć")

        pokaz(fig, frame_t)

        # TEST T
        t_stat, p = stats.ttest_ind(k, m)

        if p < 0.05:
            wniosek = "Istnieje istotna statystycznie różnica"
        else:
            wniosek = "Brak istotnej różnicy"

        label_info.config(
            text=f"t={round(t_stat,2)}, p={round(p,4)} → {wniosek}"
        )

    combo_t.bind("<<ComboboxSelected>>", lambda e: t_plot())

    # =================
    # CHI²
    # =================
    frame_chi = ttk.Frame(tab_chi)
    frame_chi.pack(fill="both", expand=True)

    combo_x = ttk.Combobox(tab_chi, state="readonly")
    combo_y = ttk.Combobox(tab_chi, state="readonly")

    combo_x.pack(pady=2)
    combo_y.pack(pady=2)

    def chi_plot():
        df = pobierz_df()
        if df is None:
            return

        x = combo_x.get()
        y = combo_y.get()

        if x == "" or y == "":
            return

        tabela = pd.crosstab(df[x], df[y])

        if tabela.empty:
            log("Brak danych do Chi²", "WARNING")
            return

        fig = plt.Figure(figsize=(6, 4))
        ax = fig.add_subplot(111)

        tabela.plot(kind="bar", ax=ax)
        ax.set_title(f"{x} vs {y}")

        pokaz(fig, frame_chi)

        # TEST CHI²
        chi2, p, dof, expected = stats.chi2_contingency(tabela)

        if p < 0.05:
            wniosek = "Zmiennie są zależne (istotne statystycznie)"
        else:
            wniosek = "Brak zależności między zmiennymi"

        label_info.config(
            text=f"Chi²={round(chi2,2)}, p={round(p,4)} → {wniosek}"
        )

    combo_x.bind("<<ComboboxSelected>>", lambda e: chi_plot())
    combo_y.bind("<<ComboboxSelected>>", lambda e: chi_plot())

    # =================
    # REFRESH
    # =================
    def refresh():
        df = get_dane()
        if df is None:
            return

        num = list(df.select_dtypes(include="number").columns)
        all_cols = list(df.columns)

        combo_gauss["values"] = num
        combo_t["values"] = num
        combo_x["values"] = all_cols
        combo_y["values"] = all_cols

    combo_gauss.bind("<Button-1>", lambda e: refresh())
    combo_t.bind("<Button-1>", lambda e: refresh())
    combo_x.bind("<Button-1>", lambda e: refresh())
    combo_y.bind("<Button-1>", lambda e: refresh())

    # =================
    # PRZYCISKI
    # =================
    frame_btn = ttk.Frame(parent)
    frame_btn.pack(fill="x")

    ttk.Button(frame_btn, text="Zapisz PNG", command=zapisz_png).pack(side="left", padx=5)
    ttk.Button(frame_btn, text="Zapisz PDF", command=zapisz_pdf).pack(side="left", padx=5)