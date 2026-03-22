# =================
# IMPORTY
# =================
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane
from eksport import zapisz_figure

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats


def create_tab_analiza(parent, log):

    parent.rowconfigure(0, weight=1)
    parent.columnconfigure(0, weight=1)

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

    # ================= UTILS =================
    def pobierz_df():
        df = get_dane()
        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return None
        return df

    def pokaz(fig, frame):
        if current_fig["fig"]:
            plt.close(current_fig["fig"])

        for w in frame.winfo_children():
            w.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        current_fig["fig"] = fig

    # ================= GAUSS =================
    combo_gauss = ttk.Combobox(tab_gauss, state="readonly")
    combo_gauss.pack(pady=5)

    ttk.Label(tab_gauss, text="Wybierz zmienną liczbową", foreground="gray").pack()

    frame_gauss = ttk.Frame(tab_gauss)
    frame_gauss.pack(fill="both", expand=True)

    def gauss_plot():
        df = pobierz_df()
        if df is None:
            return

        col = combo_gauss.get()
        if not col:
            return

        data = pd.to_numeric(df[col], errors="coerce").dropna()

        if len(data) < 5:
            label_info.config(text="Za mało danych do rozkładu")
            return

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        ax.hist(data, bins=20, density=True)

        mu, std = stats.norm.fit(data)
        x_vals = np.linspace(min(data), max(data), 100)
        ax.plot(x_vals, stats.norm.pdf(x_vals, mu, std))

        ax.set_title(f"Rozkład: {col}")

        pokaz(fig, frame_gauss)

        label_info.config(
            text=f"Średnia = {mu:.2f}, SD = {std:.2f} → rozkład przybliżony normalny"
        )

    combo_gauss.bind("<<ComboboxSelected>>", lambda e: gauss_plot())

    # ================= T-TEST =================
    combo_t = ttk.Combobox(tab_t, state="readonly")
    combo_t.pack(pady=5)

    ttk.Label(tab_t, text="Porównanie K vs M", foreground="gray").pack()

    frame_t = ttk.Frame(tab_t)
    frame_t.pack(fill="both", expand=True)

    def t_plot():
        df = pobierz_df()
        if df is None:
            return

        if "plec" not in df.columns:
            label_info.config(text="Brak kolumny 'plec'")
            return

        col = combo_t.get()
        if not col:
            return

        k = pd.to_numeric(df[df["plec"] == "K"][col], errors="coerce").dropna()
        m = pd.to_numeric(df[df["plec"] == "M"][col], errors="coerce").dropna()

        if len(k) < 2 or len(m) < 2:
            label_info.config(text="Za mało danych")
            return

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        ax.boxplot([k, m], labels=["K", "M"])
        ax.set_title(f"{col} vs płeć")

        pokaz(fig, frame_t)

        t_stat, p = stats.ttest_ind(k, m)

        label_info.config(
            text=f"t={t_stat:.2f}, p={p:.4f} → "
                 f"{'Istotna różnica między grupami' if p < 0.05 else 'Brak istotnej różnicy'}"
        )

    combo_t.bind("<<ComboboxSelected>>", lambda e: t_plot())

    # ================= CHI² =================
    combo_x = ttk.Combobox(tab_chi, state="readonly")
    combo_y = ttk.Combobox(tab_chi, state="readonly")

    combo_x.pack(pady=4)
    combo_y.pack(pady=4)

    ttk.Label(tab_chi, text="Wybierz dwie zmienne", foreground="gray").pack()

    frame_chi = ttk.Frame(tab_chi)
    frame_chi.pack(fill="both", expand=True)

    def chi_plot():
        df = pobierz_df()
        if df is None:
            return

        x, y = combo_x.get(), combo_y.get()

        if not x or not y or x == y:
            label_info.config(text="Wybierz dwie różne zmienne")
            return

        tabela = pd.crosstab(df[x], df[y])

        if tabela.shape[0] < 2 or tabela.shape[1] < 2:
            label_info.config(text="Za mało kategorii")
            return

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        im = ax.imshow(tabela.values)
        fig.colorbar(im)

        pokaz(fig, frame_chi)

        chi2, p, *_ = stats.chi2_contingency(tabela)

        label_info.config(
            text=f"Chi²={chi2:.2f}, p={p:.4f} → "
                 f"{'Istnieje zależność między zmiennymi' if p < 0.05 else 'Brak istotnej zależności'}"
        )

    combo_x.bind("<<ComboboxSelected>>", lambda e: chi_plot())
    combo_y.bind("<<ComboboxSelected>>", lambda e: chi_plot())

    # ================= KORELACJA =================
    combo_corr_x = ttk.Combobox(tab_corr, state="readonly")
    combo_corr_y = ttk.Combobox(tab_corr, state="readonly")

    combo_corr_x.pack(pady=4)
    combo_corr_y.pack(pady=4)

    ttk.Label(tab_corr, text="Wybierz dwie zmienne liczbowe", foreground="gray").pack()

    frame_corr = ttk.Frame(tab_corr)
    frame_corr.pack(fill="both", expand=True)

    def corr_plot():
        df = pobierz_df()
        if df is None:
            return

        x, y = combo_corr_x.get(), combo_corr_y.get()

        if not x or not y or x == y:
            label_info.config(text="Wybierz dwie różne zmienne")
            return

        data = df[[x, y]].apply(pd.to_numeric, errors="coerce").dropna()

        if len(data) < 3:
            label_info.config(text="Za mało danych")
            return

        fig = plt.Figure(figsize=(10, 6))
        ax = fig.add_subplot(111)

        ax.scatter(data[x], data[y])

        try:
            slope, intercept = np.polyfit(data[x], data[y], 1)
            ax.plot(data[x], slope * data[x] + intercept)
        except:
            pass

        pokaz(fig, frame_corr)

        r, p = stats.pearsonr(data[x], data[y])

        wniosek = (
            "silna korelacja" if abs(r) > 0.7 else
            "umiarkowana korelacja" if abs(r) > 0.4 else
            "słaba korelacja"
        )

        label_info.config(
            text=f"r={r:.2f}, p={p:.4f} → {wniosek}"
        )

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

    # ================= 🔥 JEDEN PRZYCISK ZAPISU =================
    frame_btn = ttk.Frame(parent)
    frame_btn.grid(row=1, column=0, sticky="ew")

    ttk.Button(
        frame_btn,
        text="💾 Zapisz wykres",
        command=lambda: zapisz_figure(current_fig["fig"], log)
    ).pack(side="left", padx=5)

    # ================= INFO =================
    label_info = ttk.Label(
        parent,
        text="Wybierz parametry analizy",
        anchor="w",
        wraplength=900,
        justify="left"
    )
    label_info.grid(row=2, column=0, sticky="ew", padx=10, pady=5)