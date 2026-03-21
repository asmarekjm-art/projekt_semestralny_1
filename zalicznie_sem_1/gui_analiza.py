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

    # ================= LAYOUT GRID =================
    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

    # ================= NOTEBOOK =================
    notebook = ttk.Notebook(parent)
    notebook.grid(row=0, column=0, sticky="nsew")

    tab_gauss = ttk.Frame(notebook)
    tab_t = ttk.Frame(notebook)
    tab_chi = ttk.Frame(notebook)
    tab_corr = ttk.Frame(notebook)

    notebook.add(tab_gauss, text="Gauss")
    notebook.add(tab_t, text="t-Studenta")
    notebook.add(tab_chi, text="Chi²")
    notebook.add(tab_corr, text="Korelacja")

    current_fig = {"fig": None}

    # ================= POMOCNICZE =================
    def pobierz_df():
        df = get_dane()
        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return None
        return df

    def pokaz(fig, frame):
        for w in frame.winfo_children():
            w.destroy()

        container = ttk.Frame(frame)
        container.pack(expand=True)

        canvas = FigureCanvasTkAgg(fig, master=container)
        canvas.draw()
        canvas.get_tk_widget().pack()

        current_fig["fig"] = fig

    # ================= ZAPIS =================
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

    # ================= GAUSS =================
    frame_gauss = ttk.Frame(tab_gauss)
    frame_gauss.pack(fill="both", expand=True)

    combo_gauss = ttk.Combobox(tab_gauss, state="readonly")
    combo_gauss.pack(pady=5)

    ttk.Label(tab_gauss, text="Wybierz zmienną liczbową", foreground="gray").pack()

    def gauss_plot():
        df = pobierz_df()
        if df is None:
            return

        col = combo_gauss.get()
        if not col:
            return

        data = pd.to_numeric(df[col], errors="coerce").dropna()
        if data.empty:
            return

        fig = plt.Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)

        ax.hist(data, bins=20, density=True)

        mu, std = stats.norm.fit(data)
        x_vals = np.linspace(min(data), max(data), 100)
        y_vals = stats.norm.pdf(x_vals, mu, std)

        ax.plot(x_vals, y_vals)
        ax.set_title(f"Rozkład: {col}")

        fig.tight_layout()
        pokaz(fig, frame_gauss)

        label_info.config(text=f"Średnia: {round(mu,2)}, SD: {round(std,2)}")

    combo_gauss.bind("<<ComboboxSelected>>", lambda e: gauss_plot())

    # ================= T-TEST =================
    frame_t = ttk.Frame(tab_t)
    frame_t.pack(fill="both", expand=True)

    combo_t = ttk.Combobox(tab_t, state="readonly")
    combo_t.pack(pady=5)

    ttk.Label(tab_t, text="Porównanie K vs M", foreground="gray").pack()

    def t_plot():
        df = pobierz_df()
        if df is None:
            return

        col = combo_t.get()
        if not col or "plec" not in df.columns:
            return

        k = pd.to_numeric(df[df["plec"] == "K"][col], errors="coerce").dropna()
        m = pd.to_numeric(df[df["plec"] == "M"][col], errors="coerce").dropna()

        if len(k) < 2 or len(m) < 2:
            return

        fig = plt.Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)

        ax.boxplot([k, m], labels=["K", "M"])
        ax.set_title(f"{col} vs płeć")

        fig.tight_layout()
        pokaz(fig, frame_t)

        t_stat, p = stats.ttest_ind(k, m)
        wniosek = "istotna różnica" if p < 0.05 else "brak różnicy"

        label_info.config(text=f"t={round(t_stat,2)}, p={round(p,4)} → {wniosek}")

    combo_t.bind("<<ComboboxSelected>>", lambda e: t_plot())

    # ================= CHI² =================
    frame_chi = ttk.Frame(tab_chi)
    frame_chi.pack(fill="both", expand=True)

    combo_x = ttk.Combobox(tab_chi, state="readonly")
    combo_y = ttk.Combobox(tab_chi, state="readonly")

    combo_x.pack(pady=4)
    combo_y.pack(pady=4)

    ttk.Label(tab_chi, text="Wybierz dwie różne zmienne", foreground="gray").pack()

    def chi_plot():
        df = pobierz_df()
        if df is None:
            return

        x = combo_x.get()
        y = combo_y.get()

        if not x or not y or x == y:
            label_info.config(text="Wybierz dwie różne zmienne")
            return

        data = df[[x, y]].copy()

        def prepare(series):
            if pd.api.types.is_numeric_dtype(series):
                series = pd.to_numeric(series, errors="coerce").dropna()
                if series.nunique() < 2:
                    return None
                return pd.cut(series, bins=5, duplicates="drop")
            else:
                return series.astype(str)

        col_x = prepare(data[x])
        col_y = prepare(data[y])

        if col_x is None or col_y is None:
            label_info.config(text="Nieprawidłowe dane")
            return

        data = pd.DataFrame({x: col_x, y: col_y}).dropna()
        tabela = pd.crosstab(data[x], data[y])

        fig = plt.Figure(figsize=(8, 6))
        ax = fig.add_subplot(111)

        im = ax.imshow(tabela.values)
        ax.set_aspect('auto')

        ax.set_xticks(range(len(tabela.columns)))
        ax.set_xticklabels(tabela.columns, rotation=45, ha="right")
        ax.set_yticks(range(len(tabela.index)))
        ax.set_yticklabels(tabela.index)

        for i in range(len(tabela.index)):
            for j in range(len(tabela.columns)):
                ax.text(j, i, tabela.values[i, j],
                        ha="center", va="center", fontsize=8)

        fig.colorbar(im, ax=ax)
        fig.tight_layout()

        pokaz(fig, frame_chi)

        chi2, p, *_ = stats.chi2_contingency(tabela)
        wniosek = "zależność" if p < 0.05 else "brak zależności"

        label_info.config(text=f"Chi²={round(chi2,2)}, p={round(p,4)} → {wniosek}")

    combo_x.bind("<<ComboboxSelected>>", lambda e: chi_plot())
    combo_y.bind("<<ComboboxSelected>>", lambda e: chi_plot())

    # ================= KORELACJA =================
    frame_corr = ttk.Frame(tab_corr)
    frame_corr.pack(fill="both", expand=True)

    combo_corr_x = ttk.Combobox(tab_corr, state="readonly")
    combo_corr_y = ttk.Combobox(tab_corr, state="readonly")

    combo_corr_x.pack(pady=4)
    combo_corr_y.pack(pady=4)

    ttk.Label(tab_corr, text="Wybierz dwie zmienne liczbowe", foreground="gray").pack()

    def corr_plot():
        df = pobierz_df()
        if df is None:
            return

        x = combo_corr_x.get()
        y = combo_corr_y.get()

        if not x or not y or x == y:
            label_info.config(text="Wybierz dwie różne zmienne")
            return

        data = df[[x, y]].copy()

        data[x] = pd.to_numeric(data[x], errors="coerce")
        data[y] = pd.to_numeric(data[y], errors="coerce")
        data = data.dropna()

        if len(data) < 2:
            label_info.config(text="Za mało danych do korelacji")
            return

        fig = plt.Figure(figsize=(7, 5))
        ax = fig.add_subplot(111)

        ax.scatter(data[x], data[y])

        slope, intercept = np.polyfit(data[x], data[y], 1)
        ax.plot(data[x], slope * data[x] + intercept)

        ax.set_title(f"{x} vs {y}")
        ax.set_xlabel(x)
        ax.set_ylabel(y)

        fig.tight_layout()
        pokaz(fig, frame_corr)

        r, p = stats.pearsonr(data[x], data[y])
        label_info.config(text=f"r={round(r,2)}, p={round(p,4)}")

    combo_corr_x.bind("<<ComboboxSelected>>", lambda e: corr_plot())
    combo_corr_y.bind("<<ComboboxSelected>>", lambda e: corr_plot())

    # ================= REFRESH =================
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
        combo_corr_x["values"] = num
        combo_corr_y["values"] = num

    for combo in [combo_gauss, combo_t, combo_x, combo_y, combo_corr_x, combo_corr_y]:
        combo.bind("<Button-1>", lambda e: refresh())

    refresh()

    # ================= PRZYCISKI =================
    frame_btn = ttk.Frame(parent)
    frame_btn.grid(row=1, column=0, sticky="ew")

    ttk.Button(frame_btn, text="Zapisz PNG", command=zapisz_png).pack(side="left", padx=5)
    ttk.Button(frame_btn, text="Zapisz PDF", command=zapisz_pdf).pack(side="left", padx=5)

    # ================= WNIOSKI =================
    label_info = ttk.Label(
        parent,
        text="Wybierz parametry analizy",
        anchor="w",
        wraplength=900,
        justify="left"
    )
    label_info.grid(row=2, column=0, sticky="ew", padx=10, pady=5)