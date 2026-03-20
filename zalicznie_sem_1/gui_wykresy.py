import ttkbootstrap as ttkb
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from dane import get_dane

from wykresy import (
    wykres_bmi,
    wykres_nadcisnienie_kolowy,
    wykres_cukrzyca_typ_kolowy,
    wykres_leki_cukrzyca
)


def create_tab_wykresy(parent, log):

    # =================
    # LAYOUT
    # =================
    frame_top = ttk.Frame(parent)
    frame_top.pack(fill="x", pady=5)

    frame_wykres = ttk.Frame(parent)
    frame_wykres.pack(fill="both", expand=True)

    frame_wnioski = ttk.LabelFrame(parent, text="📊 Wnioski")
    frame_wnioski.pack(fill="x", padx=10, pady=5)

    label_wnioski = ttk.Label(frame_wnioski, text="", justify="left")
    label_wnioski.pack(anchor="w", padx=5, pady=5)

    frame_btn = ttk.Frame(parent)
    frame_btn.pack(fill="x", pady=10)

    canvas_holder = {"canvas": None}

    # =================
    # WNIOSKI
    # =================
    def generuj_wnioski(df, typ):
        if df is None or df.empty:
            return "Brak danych"

        if typ == "bmi":
            if "bmi" in df.columns:
                bmi = df["bmi"].mean()
                if bmi < 18.5:
                    return f"Średnie BMI: {bmi:.2f} → niedożywienie"
                elif bmi < 25:
                    return f"Średnie BMI: {bmi:.2f} → norma"
                elif bmi < 30:
                    return f"Średnie BMI: {bmi:.2f} → nadwaga"
                else:
                    return f"Średnie BMI: {bmi:.2f} → otyłość"

        if typ == "nadcisnienie":
            if "nadcisnienie" in df.columns:
                nad = df["nadcisnienie"].astype(str).str.lower()
                proc = (nad.isin(["tak", "1"]).sum() / len(df)) * 100
                return f"Nadciśnienie: {proc:.1f}% pacjentów"

        if typ == "cukrzyca":
            return "Rozkład cukrzycy w populacji"

        if typ == "leki":
            return "Najczęstsze leki widoczne na wykresie"

        return ""

    # =================
    # RENDER WYKRESU
    # =================
    def pokaz_wykres(fig):
        if fig is None:
            log("Brak wykresu", "WARNING")
            return

        for widget in frame_wykres.winfo_children():
            widget.destroy()

        import matplotlib.pyplot as plt
        plt.close("all")

        canvas = FigureCanvasTkAgg(fig, master=frame_wykres)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        canvas_holder["canvas"] = canvas

    # =================
    # WYKRESY
    # =================
    def rysuj_bmi():
        df = get_dane()
        pokaz_wykres(wykres_bmi())
        label_wnioski.config(text=generuj_wnioski(df, "bmi"))

    def rysuj_nadcisnienie():
        df = get_dane()
        pokaz_wykres(wykres_nadcisnienie_kolowy())
        label_wnioski.config(text=generuj_wnioski(df, "nadcisnienie"))

    def rysuj_cukrzyca():
        df = get_dane()
        pokaz_wykres(wykres_cukrzyca_typ_kolowy())
        label_wnioski.config(text=generuj_wnioski(df, "cukrzyca"))

    def rysuj_leki():
        df = get_dane()
        pokaz_wykres(wykres_leki_cukrzyca())
        label_wnioski.config(text=generuj_wnioski(df, "leki"))

    # =================
    # PRZYCISKI
    # =================
    ttk.Button(frame_top, text="BMI", command=rysuj_bmi).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Nadciśnienie", command=rysuj_nadcisnienie).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Cukrzyca", command=rysuj_cukrzyca).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Leki", command=rysuj_leki).pack(side="left", padx=5)

    # =================
    # EKSPORT
    # =================
    def zapisz_png():
        canvas = canvas_holder["canvas"]
        if canvas:
            canvas.figure.savefig("wykres.png")
            log("Zapisano PNG")

    def zapisz_pdf():
        canvas = canvas_holder["canvas"]
        if canvas:
            canvas.figure.savefig("wykres.pdf")
            log("Zapisano PDF")

    ttk.Button(frame_btn, text="Zapisz PNG", command=zapisz_png).pack(side="left", padx=5)
    ttk.Button(frame_btn, text="Zapisz PDF", command=zapisz_pdf).pack(side="left", padx=5)