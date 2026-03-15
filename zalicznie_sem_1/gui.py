# =================
# IMPORTY
# =================

import ttkbootstrap as ttkb
from tkinter import ttk

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry
from statystyka import statystyki_opisowe, pokaz_statystyki, rysuj_test
from wykresy import (
    wykres_bmi,
    wykres_nadcisnienie_kolowy,
    wykres_cukrzyca_typ_kolowy,
    wykres_leki_cukrzyca
)
from eksport import eksport_csv, eksport_pdf, eksport_png

import eksport
import dane
import wykresy


# =================
# OKNO
# =================

okno = ttkb.Window(themename="flatly")
okno.title("Analiza pacjentów")
okno.geometry("1200x700")
okno.minsize(1100, 600)

style = ttk.Style()
style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))


# =================
# PASEK STATYSTYK
# =================

stat_label = ttk.Label(
    okno,
    text="Brak danych",
    font=("Arial", 10, "bold"),
    anchor="w"
)

stat_label.pack(fill="x", padx=10, pady=5)


# =================
# ZAKŁADKI
# =================

notebook = ttk.Notebook(okno)
notebook.pack(fill="both", expand=True)

tab_dane = ttk.Frame(notebook, padding=10)
tab_wykresy = ttk.Frame(notebook, padding=10)
tab_stat = ttk.Frame(notebook, padding=10)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")
notebook.add(tab_stat, text="Statystyka")


# =================
# ZMIENNE FILTRÓW
# =================

var_k = ttkb.BooleanVar(value=True)
var_m = ttkb.BooleanVar(value=True)

var_cuk_tak = ttkb.BooleanVar(value=True)
var_cuk_nie = ttkb.BooleanVar(value=True)

var_nad_tak = ttkb.BooleanVar(value=True)
var_nad_nie = ttkb.BooleanVar(value=True)


# =================
# TOOLBAR
# =================

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

ttk.Label(toolbar, text="Szukaj:").pack(side="left", padx=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left")

ttk.Button(
    toolbar,
    text="Szukaj",
    command=lambda: wyszukaj(search_entry, pokaz)
).pack(side="left", padx=5)

search_entry.bind(
    "<Return>",
    lambda e: wyszukaj(search_entry, pokaz)
)

ttk.Button(
    toolbar,
    text="Wczytaj bazę",
    command=lambda: wczytaj_dane(
        pokaz,
        lambda d: pokaz_statystyki(d, stat_label)
    )
).pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Statystyki opisowe",
    command=lambda: statystyki_opisowe(pokaz)
).pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Eksport CSV",
    command=eksport_csv
).pack(side="left", padx=5)


# =================
# FILTRY
# =================

ramka_filtry = ttk.LabelFrame(tab_dane, text="Filtry danych", padding=10)
ramka_filtry.pack(fill="x", padx=10, pady=10)

ramka_filtry.columnconfigure(0, weight=1)
ramka_filtry.columnconfigure(1, weight=1)


# PŁEĆ

sekcja_plec = ttk.LabelFrame(ramka_filtry, text="Płeć")
sekcja_plec.grid(row=0, column=0, padx=5, pady=5)

ttk.Checkbutton(sekcja_plec, text="Kobiety", variable=var_k).pack(anchor="w")
ttk.Checkbutton(sekcja_plec, text="Mężczyźni", variable=var_m).pack(anchor="w")


# WIEK

sekcja_wiek = ttk.LabelFrame(ramka_filtry, text="Wiek")
sekcja_wiek.grid(row=0, column=1, padx=5, pady=5)

wiek_frame = ttk.Frame(sekcja_wiek)
wiek_frame.pack()

ttk.Label(wiek_frame, text="Od").grid(row=0, column=0)

entry_min = ttk.Entry(wiek_frame, width=8)
entry_min.grid(row=0, column=1, padx=5)

ttk.Label(wiek_frame, text="Do").grid(row=0, column=2)

entry_max = ttk.Entry(wiek_frame, width=8)
entry_max.grid(row=0, column=3, padx=5)


# CUKRZYCA

sekcja_cuk = ttk.LabelFrame(ramka_filtry, text="Cukrzyca")
sekcja_cuk.grid(row=1, column=0, padx=5, pady=5)

ttk.Checkbutton(sekcja_cuk, text="Tak", variable=var_cuk_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_cuk, text="Nie", variable=var_cuk_nie).pack(anchor="w")


# NADCIŚNIENIE

sekcja_nad = ttk.LabelFrame(ramka_filtry, text="Nadciśnienie")
sekcja_nad.grid(row=1, column=1, padx=5, pady=5)

ttk.Checkbutton(sekcja_nad, text="Tak", variable=var_nad_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_nad, text="Nie", variable=var_nad_nie).pack(anchor="w")


# PRZYCISKI FILTRÓW

frame_btn = ttk.Frame(ramka_filtry)
frame_btn.grid(row=2, column=0, columnspan=2, pady=5)

ttk.Button(
    frame_btn,
    text="Filtruj",
    command=lambda: filtruj_dane(
        var_k, var_m,
        var_cuk_tak, var_cuk_nie,
        var_nad_tak, var_nad_nie,
        entry_min, entry_max,
        pokaz,
        lambda d: pokaz_statystyki(d, stat_label)
    )
).pack(side="left", padx=3)

ttk.Button(
    frame_btn,
    text="Reset",
    command=lambda: reset_filtry(
        var_k, var_m,
        var_cuk_tak, var_cuk_nie,
        var_nad_tak, var_nad_nie,
        entry_min, entry_max,
        pokaz,
        lambda d: pokaz_statystyki(d, stat_label)
    )
).pack(side="left", padx=3)


# =================
# TABELA
# =================

ramka_tabela = ttk.Frame(tab_dane)
ramka_tabela.pack(fill="both", expand=True)

tabela = ttk.Treeview(ramka_tabela)

scroll_y = ttk.Scrollbar(ramka_tabela, orient="vertical", command=tabela.yview)
scroll_x = ttk.Scrollbar(ramka_tabela, orient="horizontal", command=tabela.xview)

tabela.configure(
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

tabela.pack(fill="both", expand=True)


# =================
# WYŚWIETLANIE DANYCH
# =================

def pokaz(dane):

    tabela.delete(*tabela.get_children())

    if dane is None or dane.empty:
        return

    kolumny = ["Zmienne"] + list(dane.columns)

    tabela["columns"] = kolumny
    tabela["show"] = "headings"

    for col in kolumny:
        tabela.heading(col, text=col)
        tabela.column(col, width=120, anchor="center")

    for idx, row in dane.iterrows():
        tabela.insert("", "end", values=[idx] + list(row))


# =================
# WYKRESY
# =================

notebook_wykresy = ttk.Notebook(tab_wykresy)
notebook_wykresy.pack(fill="both", expand=True)

tab_bmi = ttk.Frame(notebook_wykresy)
tab_nad = ttk.Frame(notebook_wykresy)
tab_cuk = ttk.Frame(notebook_wykresy)
tab_leki = ttk.Frame(notebook_wykresy)

notebook_wykresy.add(tab_bmi, text="BMI")
notebook_wykresy.add(tab_nad, text="Nadciśnienie")
notebook_wykresy.add(tab_cuk, text="Cukrzyca")
notebook_wykresy.add(tab_leki, text="Leki")


def zmien_wykres(event):

    tab_frame = event.widget.nametowidget(event.widget.select())

    for widget in tab_frame.winfo_children():
        widget.destroy()

    tab = event.widget.tab("current")["text"]

    if tab == "BMI":
        wykres_bmi(tab_bmi)

    elif tab == "Nadciśnienie":
        wykres_nadcisnienie_kolowy(tab_nad)

    elif tab == "Cukrzyca":
        wykres_cukrzyca_typ_kolowy(tab_cuk)

    elif tab == "Leki":
        wykres_leki_cukrzyca(tab_leki)


notebook_wykresy.bind("<<NotebookTabChanged>>", zmien_wykres)


# =================
# EKSPORT WYKRESÓW
# =================

frame_export = ttk.Frame(tab_wykresy)
frame_export.pack(pady=10)

ttk.Button(
    frame_export,
    text="Zapisz wykres PNG",
    command=eksport_png
).pack(side="left", padx=5)

ttk.Button(
    frame_export,
    text="Zapisz wykres PDF",
    command=eksport_pdf
).pack(side="left", padx=5)


# =================
# STATYSTYKA
# =================

top_stat = ttk.Frame(tab_stat)
top_stat.pack(pady=10)

ttk.Label(top_stat, text="Wybierz analizę:", font=("Arial", 11)).pack(side="left", padx=5)

wybor_test = ttk.Combobox(
    top_stat,
    values=[
        "BMI — Płeć",
        "BMI — Cukrzyca",
        "BMI — Nadciśnienie",
        "Wiek — Płeć"
    ],
    state="readonly",
    width=25
)

wybor_test.pack(side="left", padx=5)
wybor_test.current(0)

ttk.Button(
    top_stat,
    text="Uruchom test",
    command=lambda: rysuj_test(plot_stat, wynik_stat, wybor_test)
).pack(side="left", padx=10)

plot_stat = ttk.Frame(tab_stat)
plot_stat.pack(fill="both", expand=True)

wynik_stat = ttk.Label(
    tab_stat,
    text="",
    font=("Arial", 10),
    justify="left"
)

wynik_stat.pack(pady=10)


# =================
# LOGI
# =================

frame_log = ttk.Frame(okno)
frame_log.pack(fill="x", padx=10, pady=5)

log_box = ttkb.Text(frame_log, height=4)
log_box.pack(fill="x")


def log(msg):
    log_box.insert("end", msg + "\n")
    log_box.see("end")


eksport.log = log
dane.log = log
wykresy.log = log

log("Aplikacja uruchomiona")