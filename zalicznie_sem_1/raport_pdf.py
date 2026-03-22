# =================
# IMPORTY
# =================
from tkinter import ttk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from dane import get_dane


# =================
# STYL WYKRESÓW
# =================
def styl(ax, title, xlabel="", ylabel=""):
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(True, linestyle="--", alpha=0.4)


def normalize(series):
    return series.astype(str).str.lower().str.strip()


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

        data = df["bmi"].dropna()
        if data.empty:
            log("Brak danych BMI", "WARNING")
            return

        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)

        ax.hist(data, bins=20)

        styl(ax, "Rozkład BMI pacjentów", "BMI", "Liczba")
        pokaz(fig)

        label_info.config(text=f"Średnie BMI: {round(data.mean(),1)}")


    def plec_bar():
        df = pobierz_df()
        if df is None or "plec" not in df.columns:
            log("Brak kolumny płeć", "ERROR")
            return

        counts = df["plec"].dropna().value_counts()

        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)

        ax.bar(counts.index.astype(str), counts.values)

        styl(ax, "Struktura płci pacjentów", "Płeć", "Liczba")
        pokaz(fig)

        label_info.config(text=f"Liczba kategorii: {len(counts)}")


    def nadcisnienie_bar():
        df = pobierz_df()
        if df is None or "nadcisnienie" not in df.columns:
            log("Brak kolumny nadciśnienie", "ERROR")
            return

        nad = normalize(df["nadcisnienie"])
        counts = nad.value_counts()

        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)

        ax.bar(counts.index, counts.values)

        styl(ax, "Występowanie nadciśnienia", "Status", "Liczba")
        pokaz(fig)

        tak = nad.isin(["tak", "1", "true", "yes"]).sum()
        proc = round((tak / len(nad)) * 100, 1)

        label_info.config(text=f"Nadciśnienie: {proc}%")


    def cukrzyca_bar():
        df = pobierz_df()
        if df is None:
            return

        col = next((c for c in df.columns if "cukr" in c.lower()), None)

        if col is None:
            log("Nie znaleziono kolumny cukrzyca", "ERROR")
            return

        counts = df[col].dropna().value_counts()

        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)

        ax.bar(counts.index.astype(str), counts.values)

        styl(ax, "Typy cukrzycy", "Typ", "Liczba")
        pokaz(fig)

        tekst = ", ".join([f"{k}: {v}" for k, v in counts.items()])
        label_info.config(text=tekst)


    def bmi_vs_wiek():
        df = pobierz_df()
        if df is None or "bmi" not in df.columns or "wiek" not in df.columns:
            log("Brak kolumn BMI lub wiek", "ERROR")
            return

        data = df[["wiek", "bmi"]].dropna()

        if len(data) < 2:
            log("Za mało danych", "WARNING")
            return

        fig = Figure(figsize=(8, 5))
        ax = fig.add_subplot(111)

        ax.scatter(data["wiek"], data["bmi"])

        styl(ax, "BMI vs wiek", "Wiek", "BMI")
        pokaz(fig)

        label_info.config(text="Zależność BMI od wieku")


    # =================
    # PRZYCISKI
    # =================
    ttk.Button(frame_top, text="Histogram BMI", command=hist_bmi).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Płeć", command=plec_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Nadciśnienie", command=nadcisnienie_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Cukrzyca", command=cukrzyca_bar).pack(side="left", padx=5)
    ttk.Button(frame_top, text="BMI vs wiek", command=bmi_vs_wiek).pack(side="left", padx=5)


    # =================
    # ZAPIS (NAPRAWIONY 🔥)
    # =================
    def zapisz_png():
        if current_fig["fig"] is None:
            log("Najpierw wygeneruj wykres!", "WARNING")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")]
        )

        if not path:
            return

        if not path.endswith(".png"):
            path += ".png"

        current_fig["fig"].savefig(path)
        log("Zapisano PNG")


    def zapisz_pdf():
        if current_fig["fig"] is None:
            log("Najpierw wygeneruj wykres!", "WARNING")
            return

        path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )

        if not path:
            return

        if not path.endswith(".pdf"):
            path += ".pdf"

        current_fig["fig"].savefig(path)
        log("Zapisano PDF")


    ttk.Button(frame_top, text="Zapisz PNG", command=zapisz_png).pack(side="right", padx=5)
    ttk.Button(frame_top, text="Zapisz PDF", command=zapisz_pdf).pack(side="right", padx=5)