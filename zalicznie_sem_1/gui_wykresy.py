import ttkbootstrap as ttkb
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

    frame_btn = ttk.Frame(parent)
    frame_btn.pack(fill="x", pady=10)

    canvas_holder = {"canvas": None}

    # =================
    # RENDER WYKRESU
    # =================
    def pokaz_wykres(fig):

        if fig is None:
            log("Brak wykresu do wyświetlenia", "WARNING")
            return

        # usuń poprzedni wykres
        for widget in frame_wykres.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=frame_wykres)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        canvas_holder["canvas"] = canvas

    # =================
    # WYKRESY
    # =================
    def rysuj_bmi():
        log("Rysowanie BMI")
        pokaz_wykres(wykres_bmi())

    def rysuj_nadcisnienie():
        log("Rysowanie nadciśnienia")
        pokaz_wykres(wykres_nadcisnienie_kolowy())

    def rysuj_cukrzyca():
        log("Rysowanie cukrzycy")
        pokaz_wykres(wykres_cukrzyca_typ_kolowy())

    def rysuj_leki():
        log("Rysowanie leków")
        pokaz_wykres(wykres_leki_cukrzyca())

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
        canvas = canvas_holder["canvas"]
        if canvas:
            canvas.figure.savefig("wykres.png")
            log("Zapisano wykres jako PNG")
        else:
            log("Najpierw wygeneruj wykres", "WARNING")

    def zapisz_pdf():
        canvas = canvas_holder["canvas"]
        if canvas:
            canvas.figure.savefig("wykres.pdf")
            log("Zapisano wykres jako PDF")
        else:
            log("Najpierw wygeneruj wykres", "WARNING")

    ttk.Button(frame_btn, text="Zapisz PNG", command=zapisz_png).pack(side="left", padx=5)
    ttk.Button(frame_btn, text="Zapisz PDF", command=zapisz_pdf).pack(side="left", padx=5)