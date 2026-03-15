# =================
# IMPORTY
# =================

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

from dane import get_dane


# =================
# ZMIENNE GLOBALNE
# =================

canvas = None
current_fig = None
current_data = None
current_title = ""


# =================
# CZYSZCZENIE WYKRESU
# =================

def wyczysc_wykres():

    global canvas

    if canvas is not None:
        canvas.get_tk_widget().destroy()


# =================
# WYŚWIETLANIE WYKRESU
# =================

def pokaz_wykres(frame, fig):

    global canvas

    wyczysc_wykres()

    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# =================
# ZAPIS AKTUALNEGO WYKRESU
# =================

def zapisz_aktualny_wykres(fig, dane, tytul):

    global current_fig, current_data, current_title

    current_fig = fig
    current_data = dane
    current_title = tytul


# =================
# WYKRES BMI
# =================

def wykres_bmi(frame):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    if {"BMI", "plec"}.issubset(dane.columns) is False:
        messagebox.showwarning("Błąd", "Brak kolumn BMI lub plec")
        return

    kobiety = dane[dane["plec"] == "K"]["BMI"]
    mezczyzni = dane[dane["plec"] == "M"]["BMI"]

    fig = Figure(figsize=(8,4))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    ax1.hist(kobiety, bins=15, color="pink", alpha=0.7)
    ax1.axvline(18.5, linestyle="--", color="red")
    ax1.axvline(25, linestyle="--", color="green")

    ax1.set_title("Kobiety")
    ax1.set_xlabel("BMI")
    ax1.set_ylabel("Liczba pacjentów")
    ax1.set_xlim(15,45)
    ax1.grid(alpha=0.3)

    ax2.hist(mezczyzni, bins=15, color="lightblue", alpha=0.7)
    ax2.axvline(18.5, linestyle="--", color="red")
    ax2.axvline(25, linestyle="--", color="green")

    ax2.set_title("Mężczyźni")
    ax2.set_xlabel("BMI")
    ax2.set_xlim(15,45)
    ax2.grid(alpha=0.3)

    fig.suptitle("Rozkład BMI według płci")

    zapisz_aktualny_wykres(fig, dane, "Rozkład BMI według płci")

    pokaz_wykres(frame, fig)


# =================
# WYKRES NADCIŚNIENIA
# =================

def wykres_nadcisnienie_kolowy(frame):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    if "nadcisnienie" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak danych o nadciśnieniu")
        return

    counts = dane["nadcisnienie"].value_counts()

    labels = ["Nadciśnienie", "Brak nadciśnienia"]

    values = [
        counts.get("tak",0),
        counts.get("nie",0)
    ]

    fig = Figure(figsize=(5,4))
    ax = fig.add_subplot(111)

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=["red","green"],
        startangle=90
    )

    ax.set_title(f"Procent pacjentów z nadciśnieniem (N={len(dane)})")

    zapisz_aktualny_wykres(fig, dane, "Procent pacjentów z nadciśnieniem")

    pokaz_wykres(frame, fig)


# =================
# WYKRES CUKRZYCY
# =================

def wykres_cukrzyca_typ_kolowy(frame):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    if {"cukrzyca","typ_cukrzycy"}.issubset(dane.columns) is False:
        messagebox.showwarning("Błąd", "Brak danych o cukrzycy")
        return

    brak = len(dane[dane["cukrzyca"] == "nie"])
    typ1 = len(dane[dane["typ_cukrzycy"] == "typ 1"])
    typ2 = len(dane[dane["typ_cukrzycy"] == "typ 2"])

    labels = ["Brak cukrzycy","Typ 1","Typ 2"]
    values = [brak,typ1,typ2]

    fig = Figure(figsize=(5,4))
    ax = fig.add_subplot(111)

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=["green","orange","red"],
        startangle=90
    )

    ax.set_title(f"Cukrzyca w populacji (N={len(dane)})")

    zapisz_aktualny_wykres(fig, dane, "Cukrzyca w populacji")

    pokaz_wykres(frame, fig)


# =================
# WYKRES LEKÓW
# =================

def wykres_leki_cukrzyca(frame):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    if {"leki_na_cukrzyce","cukrzyca"}.issubset(dane.columns) is False:
        messagebox.showwarning("Błąd", "Brak danych o lekach")
        return

    dane_cukrzyca = dane[dane["cukrzyca"]=="tak"].copy()

    dane_cukrzyca["leki_na_cukrzyce"] = (
        dane_cukrzyca["leki_na_cukrzyce"]
        .fillna("brak leków")
        .replace("", "brak leków")
    )

    counts = dane_cukrzyca["leki_na_cukrzyce"].value_counts()

    fig = Figure(figsize=(6,4))
    ax = fig.add_subplot(111)

    x = range(len(counts))

    ax.bar(x, counts.values, color="purple", alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(counts.index, rotation=30, ha="right")

    ax.set_ylabel("Liczba pacjentów")
    ax.set_title(f"Leczenie cukrzycy (N={len(dane_cukrzyca)})")

    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    zapisz_aktualny_wykres(fig, dane_cukrzyca, "Leczenie cukrzycy")

    pokaz_wykres(frame, fig)