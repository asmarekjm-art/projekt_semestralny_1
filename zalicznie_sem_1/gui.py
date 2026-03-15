# =================
# IMPORTY
# =================

import ttkbootstrap as ttkb
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime

import dane
import wykresy
import statystyka
import eksport

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry
from statystyka import statystyki_opisowe, pokaz_statystyki, rysuj_test
from wykresy import (
    wykres_bmi,
    wykres_nadcisnienie_kolowy,
    wykres_cukrzyca_typ_kolowy,
    wykres_leki_cukrzyca
)
from eksport import eksport_csv, raport_pdf


# =================
# OKNO
# =================

okno = ttkb.Window(themename="flatly")
okno.title("Analiza pacjentów")
okno.geometry("1200x720")
okno.minsize(1100,650)

style = ttk.Style()
style.configure("Treeview", rowheight=26)


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
# TOOLBAR
# =================

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Szukaj",
    command=lambda: wyszukaj(search_entry, pokaz)
).pack(side="left", padx=5)

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

ttk.Button(
    toolbar,
    text="Raport PDF",
    command=raport_pdf
).pack(side="left", padx=5)


# =================
# ZMIENNE FILTRÓW
# =================

var_k = ttkb.BooleanVar(value=True)
var_m = ttkb.BooleanVar(value=True)

var_cuk_tak = ttkb.BooleanVar(value=True)
var_cuk_nie = ttkb.BooleanVar(value=True)

var_nad_tak = ttkb.BooleanVar(value=True)
var_nad_nie = ttkb.BooleanVar(value=True)

var_typ1 = ttkb.BooleanVar(value=True)
var_typ2 = ttkb.BooleanVar(value=True)


# =================
# FILTRY
# =================

ramka_filtry = ttk.LabelFrame(tab_dane, text="Filtry danych", padding=10)
ramka_filtry.pack(fill="x", padx=5, pady=5)

ramka_filtry.columnconfigure((0,1,2,3), weight=1)

# płeć
sekcja_plec = ttk.LabelFrame(ramka_filtry, text="Płeć")
sekcja_plec.grid(row=0, column=0, padx=5)

ttk.Checkbutton(sekcja_plec, text="Kobiety", variable=var_k).pack(anchor="w")
ttk.Checkbutton(sekcja_plec, text="Mężczyźni", variable=var_m).pack(anchor="w")

# wiek
sekcja_wiek = ttk.LabelFrame(ramka_filtry, text="Wiek")
sekcja_wiek.grid(row=0, column=1, padx=5)

ttk.Label(sekcja_wiek,text="Od").grid(row=0,column=0)
entry_min = ttk.Entry(sekcja_wiek,width=6)
entry_min.grid(row=0,column=1)

ttk.Label(sekcja_wiek,text="Do").grid(row=0,column=2)
entry_max = ttk.Entry(sekcja_wiek,width=6)
entry_max.grid(row=0,column=3)

# BMI
sekcja_bmi = ttk.LabelFrame(ramka_filtry, text="BMI")
sekcja_bmi.grid(row=0, column=2, padx=5)

ttk.Label(sekcja_bmi,text="Od").grid(row=0,column=0)
entry_bmi_min = ttk.Entry(sekcja_bmi,width=6)
entry_bmi_min.grid(row=0,column=1)

ttk.Label(sekcja_bmi,text="Do").grid(row=0,column=2)
entry_bmi_max = ttk.Entry(sekcja_bmi,width=6)
entry_bmi_max.grid(row=0,column=3)

# cholesterol
sekcja_chol = ttk.LabelFrame(ramka_filtry, text="Cholesterol")
sekcja_chol.grid(row=0, column=3, padx=5)

ttk.Label(sekcja_chol,text="Od").grid(row=0,column=0)
entry_chol_min = ttk.Entry(sekcja_chol,width=6)
entry_chol_min.grid(row=0,column=1)

ttk.Label(sekcja_chol,text="Do").grid(row=0,column=2)
entry_chol_max = ttk.Entry(sekcja_chol,width=6)
entry_chol_max.grid(row=0,column=3)

# cukrzyca
sekcja_cuk = ttk.LabelFrame(ramka_filtry, text="Cukrzyca")
sekcja_cuk.grid(row=1, column=0)

ttk.Checkbutton(sekcja_cuk,text="Tak",variable=var_cuk_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_cuk,text="Nie",variable=var_cuk_nie).pack(anchor="w")

# nadciśnienie
sekcja_nad = ttk.LabelFrame(ramka_filtry, text="Nadciśnienie")
sekcja_nad.grid(row=1, column=1)

ttk.Checkbutton(sekcja_nad,text="Tak",variable=var_nad_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_nad,text="Nie",variable=var_nad_nie).pack(anchor="w")

# typ cukrzycy
sekcja_typ = ttk.LabelFrame(ramka_filtry, text="Typ cukrzycy")
sekcja_typ.grid(row=1, column=2)

ttk.Checkbutton(sekcja_typ,text="Typ 1",variable=var_typ1).pack(anchor="w")
ttk.Checkbutton(sekcja_typ,text="Typ 2",variable=var_typ2).pack(anchor="w")

# leki nadciśnienia
sekcja_leki = ttk.LabelFrame(ramka_filtry, text="Leki nadciśnienia")
sekcja_leki.grid(row=1, column=3)

leki_combo = ttk.Combobox(
    sekcja_leki,
    values=["wszystkie","ACEI","ARB","beta-bloker","diuretyk"],
    width=15
)
leki_combo.current(0)
leki_combo.pack()

# przyciski
frame_btn = ttk.Frame(ramka_filtry)
frame_btn.grid(row=2,column=0,columnspan=4,pady=5)

ttk.Button(
    frame_btn,
    text="Filtruj",
    command=lambda: filtruj_dane(
        var_k,var_m,
        var_cuk_tak,var_cuk_nie,
        var_nad_tak,var_nad_nie,
        entry_min,entry_max,
        pokaz,
        lambda d: pokaz_statystyki(d, stat_label)
    )
).pack(side="left",padx=5)

ttk.Button(
    frame_btn,
    text="Reset",
    command=lambda: reset_filtry(
        var_k,var_m,
        var_cuk_tak,var_cuk_nie,
        var_nad_tak,var_nad_nie,
        entry_min,entry_max,
        pokaz,
        lambda d: pokaz_statystyki(d, stat_label)
    )
).pack(side="left",padx=5)


# =================
# PANEL TABELA + STAT + LOGI
# =================

panel_dol = ttk.Frame(tab_dane)
panel_dol.pack(fill="both", expand=True)


# =================
# TABELA
# =================

ramka_tabela = ttk.Frame(panel_dol)
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


def pokaz(dane_df):

    tabela.delete(*tabela.get_children())

    if dane_df is None or dane_df.empty:
        return

    kolumny = ["ID"] + list(dane_df.columns)

    tabela["columns"] = kolumny
    tabela["show"] = "headings"

    for col in kolumny:
        tabela.heading(col, text=col)
        tabela.column(col, width=110, anchor="center")

    for idx, row in dane_df.iterrows():
        tabela.insert("", "end", values=[idx] + list(row))


# =================
# STATYSTYKA
# =================

stat_label = ttk.Label(
    panel_dol,
    text="Brak danych",
    font=("Arial",10,"bold"),
    anchor="w"
)

stat_label.pack(fill="x", padx=5, pady=3)


# =================
# LOGI
# =================

frame_log = ttk.LabelFrame(panel_dol,text="Logi programu")
frame_log.pack(fill="x",padx=5,pady=5)

log_box = ttkb.Text(frame_log,height=7)

scroll_log = ttk.Scrollbar(frame_log,command=log_box.yview)
log_box.configure(yscrollcommand=scroll_log.set)

log_box.pack(side="left",fill="both",expand=True)
scroll_log.pack(side="right",fill="y")


def log(msg, level="INFO"):

    czas = datetime.now().strftime("%H:%M:%S")
    wpis = f"[{czas}] {level}: {msg}\n"

    log_box.insert("end", wpis)
    log_box.see("end")


# =================
# WYKRESY
# =================

panel_wykresy = ttk.Frame(tab_wykresy)
panel_wykresy.pack(fill="x", pady=10)

plot_wykres = ttk.Frame(tab_wykresy)
plot_wykres.pack(fill="both", expand=True)


def pokaz_wykres(fig):

    for widget in plot_wykres.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_wykres)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def generuj_wykres(funkcja):

    fig = funkcja()
    pokaz_wykres(fig)


ttk.Button(panel_wykresy,text="Rozkład BMI",
command=lambda: generuj_wykres(wykres_bmi)).pack(side="left", padx=5)

ttk.Button(panel_wykresy,text="Nadciśnienie",
command=lambda: generuj_wykres(wykres_nadcisnienie_kolowy)).pack(side="left", padx=5)

ttk.Button(panel_wykresy,text="Cukrzyca",
command=lambda: generuj_wykres(wykres_cukrzyca_typ_kolowy)).pack(side="left", padx=5)

ttk.Button(panel_wykresy,text="Leki",
command=lambda: generuj_wykres(wykres_leki_cukrzyca)).pack(side="left", padx=5)


# =================
# PODPIĘCIE LOGÓW
# =================

eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log

okno.after(100, lambda: log("Aplikacja uruchomiona"))