# =================
# IMPORTY
# =================

from scipy.stats import ttest_ind
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from tkinter import messagebox

from dane import get_dane


# =================
# STATYSTYKI OPISOWE
# =================

def statystyki_opisowe(pokaz):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    num = dane.select_dtypes(include="number")

    if num.empty:
        messagebox.showwarning("Błąd", "Brak danych liczbowych")
        return

    opis = num.describe().T

    # podpisy wierszy
    opis = opis.rename(index={
        "wiek": "Wiek pacjentów [lata]",
        "waga": "Masa ciała [kg]",
        "wzrost": "Wzrost [cm]",
        "BMI": "BMI (Body Mass Index)"
    })

    # podpisy kolumn
    opis = opis.rename(columns={
        "count": "Liczba obserwacji",
        "mean": "Średnia",
        "std": "Odchylenie std",
        "min": "Minimum",
        "25%": "1 kwartyl",
        "50%": "Mediana",
        "75%": "3 kwartyl",
        "max": "Maximum"
    })

    pokaz(opis.round(2))


# =================
# PASEK STATYSTYK
# =================

def pokaz_statystyki(dane, stat_label):

    if dane is None or len(dane) == 0:
        stat_label.config(text="Brak danych")
        return

    liczba = len(dane)

    sredni_wiek = "-"
    sredni_bmi = "-"
    cuk_proc = "-"
    nad_proc = "-"

    if "wiek" in dane.columns:
        sredni_wiek = round(dane["wiek"].mean(), 1)

    if "BMI" in dane.columns:
        sredni_bmi = round(dane["BMI"].mean(), 1)

    if "cukrzyca" in dane.columns:
        cuk_proc = round((dane["cukrzyca"] == "tak").mean() * 100, 1)

    if "nadcisnienie" in dane.columns:
        nad_proc = round((dane["nadcisnienie"] == "tak").mean() * 100, 1)

    tekst = (
        f"Pacjenci: {liczba} | "
        f"Średni wiek: {sredni_wiek} | "
        f"Średni BMI: {sredni_bmi} | "
        f"Cukrzyca: {cuk_proc}% | "
        f"Nadciśnienie: {nad_proc}%"
    )

    stat_label.config(text=tekst)


# =================
# WYBÓR GRUP DO TESTU
# =================

def przygotuj_grupy(dane, typ):

    if typ == "BMI — Płeć":
        g1 = dane[dane["plec"] == "K"]["BMI"].dropna()
        g2 = dane[dane["plec"] == "M"]["BMI"].dropna()
        nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
        ylabel = "BMI"

    elif typ == "BMI — Cukrzyca":
        g1 = dane[dane["cukrzyca"] == "tak"]["BMI"].dropna()
        g2 = dane[dane["cukrzyca"] == "nie"]["BMI"].dropna()
        nazwa1, nazwa2 = "Cukrzyca", "Brak"
        ylabel = "BMI"

    elif typ == "BMI — Nadciśnienie":
        g1 = dane[dane["nadcisnienie"] == "tak"]["BMI"].dropna()
        g2 = dane[dane["nadcisnienie"] == "nie"]["BMI"].dropna()
        nazwa1, nazwa2 = "Nadciśnienie", "Brak"
        ylabel = "BMI"

    elif typ == "Wiek — Płeć":
        g1 = dane[dane["plec"] == "K"]["wiek"].dropna()
        g2 = dane[dane["plec"] == "M"]["wiek"].dropna()
        nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
        ylabel = "Wiek"

    else:
        return None

    return g1, g2, nazwa1, nazwa2, ylabel


# =================
# TEST T-STUDENTA
# =================

def rysuj_test(plot_stat, wynik_stat, wybor_test):

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    for widget in plot_stat.winfo_children():
        widget.destroy()

    typ = wybor_test.get()

    wynik = przygotuj_grupy(dane, typ)

    if wynik is None:
        return

    g1, g2, nazwa1, nazwa2, ylabel = wynik

    if len(g1) < 2 or len(g2) < 2:
        wynik_stat.config(text="Za mało danych do testu")
        return

    t, p = ttest_ind(g1, g2, equal_var=False)

    tekst = (
        f"{nazwa1}: {g1.mean():.2f} ± {g1.std():.2f} (n={len(g1)})\n"
        f"{nazwa2}: {g2.mean():.2f} ± {g2.std():.2f} (n={len(g2)})\n"
        f"t = {t:.3f}    p = {p:.4f}"
    )

    wynik_stat.config(text=tekst)

    fig = Figure(figsize=(6,4))
    ax = fig.add_subplot(111)

    ax.boxplot([g1, g2], tick_labels=[nazwa1, nazwa2])

    ax.set_ylabel(ylabel)
    ax.set_title(typ)
    ax.grid(alpha=0.3)

    canvas = FigureCanvasTkAgg(fig, master=plot_stat)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)