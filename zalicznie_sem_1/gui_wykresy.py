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
    frame_top.pack(fill="x")

    frame_wykres = ttk.Frame(parent)
    frame_wykres.pack(fill="both", expand=True)

    frame_btn = ttk.Frame(parent)
    frame_btn.pack(fill="x", pady=10)

    canvas_wykres = {"obj": None}

    # =================
    # RYSOWANIE
    # =================
    def pokaz_wykres(fig):
        for widget in frame_wykres.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_wykres)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        canvas_wykres["obj"] = canvas

    def get_df():
        df = get_dane()
        if df is None or df.empty:
            log("Brak danych do wykresu", "WARNING")
            return None
        return df

    # =================
    # WYKRESY
    # =================
    def rysuj_bmi():
        df = get_df()
        if df is not None:
            pokaz_wykres(wykres_bmi(df))

    def rysuj_nadcisnienie():
        df = get_df()
        if df is not None:
            pokaz_wykres(wykres_nadcisnienie_kolowy(df))

    def rysuj_cukrzyca():
        df = get_df()
        if df is not None:
            pokaz_wykres(wykres_cukrzyca_typ_kolowy(df))

    def rysuj_leki():
        df = get_df()
        if df is not None:
            pokaz_wykres(wykres_leki_cukrzyca(df))

    # =================
    # PRZYCISKI WYBORU
    # =================
    ttk.Button(frame_top, text="BMI", command=rysuj_bmi).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Nadciśnienie", command=rysuj_nadcisnienie).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Cukrzyca", command=rysuj_cukrzyca).pack(side="left", padx=5)
    ttk.Button(frame_top, text="Leki", command=rysuj_leki).pack(side="left", padx=5)

    # =================
    # EKSPORT
    # =================
    def zapisz_png():
        canvas = canvas_wykres["obj"]
        if canvas:
            canvas.figure.savefig("wykres.png")
            log("Zapisano PNG")

    def zapisz_pdf():
        canvas = canvas_wykres["obj"]
        if canvas:
            canvas.figure.savefig("wykres.pdf")
            log("Zapisano PDF")

    ttk.Button(frame_btn, text="Zapisz PNG", command=zapisz_png).pack(side="left", padx=5)
    ttk.Button(frame_btn, text="Zapisz PDF", command=zapisz_pdf).pack(side="left", padx=5)