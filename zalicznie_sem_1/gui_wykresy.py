# =================
# IMPORTY
# =================
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

from dane import get_dane

# 🔥 GLOBAL do raportu
aktualny_fig_global = None


# =================
# FUNKCJA GŁÓWNA
# =================
def create_tab_wykresy(parent, log):

    frame_top = ttk.Frame(parent)
    frame_top.pack(fill="x", pady=5)

    frame_wykres = ttk.Frame(parent)
    frame_wykres.pack(fill="both", expand=True)

    canvas = None
    aktualny_fig = None

    # =================
    # RYSOWANIE
    # =================
    def rysuj(fig):
        nonlocal canvas, aktualny_fig
        global aktualny_fig_global

        aktualny_fig = fig
        aktualny_fig_global = fig  # 🔥 do raportu

        if canvas:
            canvas.get_tk_widget().destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_wykres)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    # =================
    # HISTOGRAM / BAR
    # =================
    def wykres_hist():
        df = get_dane()

        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return

        col = combo.get()

        fig, ax = plt.subplots()

        if df[col].dtype == "object":
            counts = df[col].value_counts()

            ax.bar(counts.index.astype(str), counts.values)
            ax.set_title(f"Liczność kategorii: {col}")
            ax.set_ylabel("Liczba")

        else:
            ax.hist(df[col].dropna(), bins=20)
            ax.set_title(f"Histogram: {col}")

        rysuj(fig)
        log(f"Wykres: {col}")

    # =================
    # BOXPLOT
    # =================
    def wykres_box():
        df = get_dane()

        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return

        col = combo.get()

        fig, ax = plt.subplots()
        ax.boxplot(df[col].dropna())
        ax.set_title(f"Boxplot: {col}")

        rysuj(fig)
        log(f"Boxplot: {col}")

    # =================
    # SCATTER
    # =================
    def wykres_scatter():
        df = get_dane()

        if df is None or df.empty:
            log("Brak danych", "WARNING")
            return

        x = combo_x.get()
        y = combo_y.get()

        fig, ax = plt.subplots()
        ax.scatter(df[x], df[y])
        ax.set_xlabel(x)
        ax.set_ylabel(y)
        ax.set_title(f"{x} vs {y}")

        rysuj(fig)
        log(f"Scatter: {x} vs {y}")

    # =================
    # ZAPIS WYKRESU
    # =================
    def zapisz_wykres():
        nonlocal aktualny_fig

        if aktualny_fig is None:
            log("Najpierw wygeneruj wykres", "WARNING")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[
                ("PNG", "*.png"),
                ("PDF", "*.pdf")
            ]
        )

        if path:
            aktualny_fig.savefig(path, dpi=150, bbox_inches="tight")
            log(f"Zapisano wykres: {path}")

    # =================
    # UI
    # =================
    ttk.Label(frame_top, text="Kolumna:").pack(side="left", padx=5)

    combo = ttk.Combobox(frame_top, state="readonly", width=20)
    combo.pack(side="left", padx=5)

    ttk.Button(frame_top, text="Histogram", command=wykres_hist)\
        .pack(side="left", padx=5)

    ttk.Button(frame_top, text="Boxplot", command=wykres_box)\
        .pack(side="left", padx=5)

    ttk.Separator(frame_top, orient="vertical")\
        .pack(side="left", fill="y", padx=10)

    ttk.Label(frame_top, text="X:").pack(side="left", padx=5)
    combo_x = ttk.Combobox(frame_top, state="readonly", width=15)
    combo_x.pack(side="left", padx=5)

    ttk.Label(frame_top, text="Y:").pack(side="left", padx=5)
    combo_y = ttk.Combobox(frame_top, state="readonly", width=15)
    combo_y.pack(side="left", padx=5)

    ttk.Button(frame_top, text="Scatter", command=wykres_scatter)\
        .pack(side="left", padx=5)

    ttk.Separator(frame_top, orient="vertical")\
        .pack(side="left", fill="y", padx=10)

    ttk.Button(frame_top, text="💾 Zapisz", command=zapisz_wykres)\
        .pack(side="left", padx=5)

    # =================
    # ODŚWIEŻ KOLUMNY
    # =================
    def odswiez():
        df = get_dane()

        if df is None or df.empty:
            return

        cols = list(df.columns)

        combo["values"] = cols
        combo_x["values"] = cols
        combo_y["values"] = cols

        if cols:
            combo.set(cols[0])
            combo_x.set(cols[0])
            combo_y.set(cols[-1])

    parent.bind("<Visibility>", lambda e: odswiez())
    odswiez()