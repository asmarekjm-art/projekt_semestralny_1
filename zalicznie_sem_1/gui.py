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

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry, get_dane
from statystyka import statystyki_opisowe, pokaz_statystyki
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
okno.geometry("1200x700")

style = ttk.Style()
style.configure("Treeview", rowheight=26)


# =================
# ZAKŁADKI
# =================

notebook = ttk.Notebook(okno)
notebook.pack(fill="both", expand=True)

tab_dane = ttk.Frame(notebook)
tab_wykresy = ttk.Frame(notebook)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")


# =================
# TOOLBAR
# =================

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

search_entry = ttk.Entry(toolbar, width=25)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", lambda e: wyszukaj(search_entry, pokaz))

ttk.Button(toolbar, text="Szukaj",
           command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left", padx=5)

ttk.Button(toolbar, text="Wczytaj",
           command=lambda: wczytaj_dane(
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left", padx=5)

ttk.Button(toolbar, text="Statystyki opisowe",
           command=lambda: pokaz(statystyki_opisowe(get_dane()))
           ).pack(side="left", padx=5)

ttk.Button(toolbar, text="Eksport CSV",
           command=eksport_csv).pack(side="left", padx=5)

ttk.Button(toolbar, text="Raport PDF",
           command=raport_pdf).pack(side="left", padx=5)


# =================
# FILTRY
# =================

ramka_filtry = ttk.LabelFrame(tab_dane, text="🔎 Filtry", padding=10)
ramka_filtry.pack(fill="x", padx=10, pady=5)

for i in range(6):
    ramka_filtry.columnconfigure(i, weight=1)

# zmienne
var_k = ttkb.BooleanVar(value=True)
var_m = ttkb.BooleanVar(value=True)

var_cuk_typ1 = ttkb.BooleanVar(value=True)
var_cuk_typ2 = ttkb.BooleanVar(value=True)
var_cuk_brak = ttkb.BooleanVar(value=True)

var_nad_tak = ttkb.BooleanVar(value=True)
var_nad_nie = ttkb.BooleanVar(value=True)

# --- WIERSZ 1
ttk.Label(ramka_filtry, text="Płeć").grid(row=0, column=0, sticky="w")
ttk.Checkbutton(ramka_filtry, text="K", variable=var_k).grid(row=0, column=1)
ttk.Checkbutton(ramka_filtry, text="M", variable=var_m).grid(row=0, column=2)

ttk.Label(ramka_filtry, text="Wiek").grid(row=0, column=3)
entry_min = ttk.Entry(ramka_filtry, width=6)
entry_min.grid(row=0, column=4)
entry_max = ttk.Entry(ramka_filtry, width=6)
entry_max.grid(row=0, column=5)

# --- WIERSZ 2
ttk.Label(ramka_filtry, text="BMI").grid(row=1, column=0)
entry_bmi_min = ttk.Entry(ramka_filtry, width=6)
entry_bmi_min.grid(row=1, column=1)
entry_bmi_max = ttk.Entry(ramka_filtry, width=6)
entry_bmi_max.grid(row=1, column=2)

ttk.Label(ramka_filtry, text="Nadciśnienie").grid(row=1, column=3)
ttk.Checkbutton(ramka_filtry, text="Tak", variable=var_nad_tak).grid(row=1, column=4)
ttk.Checkbutton(ramka_filtry, text="Nie", variable=var_nad_nie).grid(row=1, column=5)

# --- WIERSZ 3
ttk.Label(ramka_filtry, text="Cukrzyca").grid(row=2, column=0)
ttk.Checkbutton(ramka_filtry, text="Typ 1", variable=var_cuk_typ1).grid(row=2, column=1)
ttk.Checkbutton(ramka_filtry, text="Typ 2", variable=var_cuk_typ2).grid(row=2, column=2)
ttk.Checkbutton(ramka_filtry, text="Brak", variable=var_cuk_brak).grid(row=2, column=3)

# --- PRZYCISKI
frame_btn = ttk.Frame(ramka_filtry)
frame_btn.grid(row=3, column=0, columnspan=6, pady=10)

ttk.Button(frame_btn, text="Filtruj",
           command=lambda: filtruj_dane(
               var_k, var_m,
               var_cuk_typ1, var_cuk_typ2, var_cuk_brak,
               var_nad_tak, var_nad_nie,
               entry_min, entry_max,
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label),
               entry_bmi_min, entry_bmi_max
           )).pack(side="left", padx=5)

ttk.Button(frame_btn, text="Reset",
           command=lambda: reset_filtry(
               var_k, var_m,
               var_cuk_typ1, var_cuk_typ2, var_cuk_brak,
               var_nad_tak, var_nad_nie,
               entry_min, entry_max,
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left", padx=5)


# =================
# TABELA
# =================

ramka_tabela = ttk.Frame(tab_dane)
ramka_tabela.pack(fill="both", expand=True)

tabela = ttk.Treeview(ramka_tabela)

scroll_y = ttk.Scrollbar(ramka_tabela, command=tabela.yview)
scroll_x = ttk.Scrollbar(ramka_tabela, command=tabela.xview, orient="horizontal")

tabela.configure(yscrollcommand=scroll_y.set,
                 xscrollcommand=scroll_x.set)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tabela.pack(fill="both", expand=True)


def pokaz(df):
    tabela.delete(*tabela.get_children())

    if df is None or df.empty:
        return

    cols = ["ID"] + list(df.columns)
    tabela["columns"] = cols
    tabela["show"] = "headings"

    for col in cols:
        tabela.heading(col, text=col)
        tabela.column(col, width=max(100, len(col) * 10), anchor="center")

    for i, row in df.iterrows():
        tabela.insert("", "end", values=[i] + list(row))


# =================
# STATYSTYKI
# =================

stat_label = ttk.Label(tab_dane, text="Brak danych",
                       font=("Segoe UI", 10, "bold"))
stat_label.pack(fill="x", pady=5)


# =================
# WYKRESY
# =================

plot_frame = ttk.Frame(tab_wykresy)
plot_frame.pack(fill="both", expand=True)


def pokaz_wykres(fig):
    for w in plot_frame.winfo_children():
        w.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def generuj_wykres(f):
    pokaz_wykres(f())


panel = ttk.Frame(tab_wykresy)
panel.pack(pady=10)

for text, func in [
    ("BMI", wykres_bmi),
    ("Nadciśnienie", wykres_nadcisnienie_kolowy),
    ("Cukrzyca", wykres_cukrzyca_typ_kolowy),
    ("Leki", wykres_leki_cukrzyca),
]:
    ttk.Button(panel, text=text,
               command=lambda f=func: generuj_wykres(f)
               ).pack(side="left", padx=8)


# =================
# LOGI
# =================

frame_log = ttk.LabelFrame(okno, text="Logi")
frame_log.pack(fill="x", padx=10, pady=5)

log_box = ttkb.Text(frame_log, height=5)

scroll = ttk.Scrollbar(frame_log, command=log_box.yview)
log_box.configure(yscrollcommand=scroll.set)

log_box.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")


def log(msg, level="INFO"):
    czas = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{czas}] {level}: {msg}\n")
    log_box.see("end")


# =================
# PODPIĘCIE LOGÓW
# =================

eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log

okno.after(100, lambda: log("Aplikacja uruchomiona"))