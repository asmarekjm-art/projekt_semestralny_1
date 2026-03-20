# =================
# IMPORTY
# =================
import ttkbootstrap as ttkb
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import matplotlib.pyplot as plt

import dane, wykresy, statystyka, eksport

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry, get_dane
from statystyka import statystyki_opisowe, pokaz_statystyki
from wykresy import (
    wykres_bmi,
    wykres_nadcisnienie_kolowy,
    wykres_cukrzyca_typ_kolowy,
    wykres_leki_cukrzyca
)
from eksport import eksport_csv, raport_pdf

podsumowanie_label = None


# =================
# OKNO
# =================
okno = ttkb.Window(themename="flatly")
okno.title("Analiza pacjentów")
okno.geometry("1400x900")


# =================
# LAYOUT
# =================
main_pane = ttk.PanedWindow(okno, orient="vertical")
main_pane.pack(fill="both", expand=True)

frame_top = ttk.Frame(main_pane)
main_pane.add(frame_top, weight=5)

frame_log = ttk.LabelFrame(main_pane, text="Logi")
main_pane.add(frame_log, weight=0)
frame_log.configure(height=120)
frame_log.pack_propagate(False)


# =================
# LOGI
# =================
log_box = ttkb.Text(frame_log, wrap="word")
log_box.pack(fill="both", expand=True)

last_log = {"msg": None}

def log(msg, level="INFO"):
    if last_log["msg"] == msg:
        return
    last_log["msg"] = msg

    czas = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{czas}] {level}: {msg}\n")
    log_box.see("end")


eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log


# =================
# NOTEBOOK
# =================
notebook = ttk.Notebook(frame_top)
notebook.pack(fill="both", expand=True)

tab_dane = ttk.Frame(notebook)
tab_wykresy = ttk.Frame(notebook)
tab_stat = ttk.Frame(notebook)
tab_analiza = ttk.Frame(notebook)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")
notebook.add(tab_stat, text="Statystyka")
notebook.add(tab_analiza, text="Analiza")


# =================
# TABELA + FUNKCJA
# =================
def pokaz(df):
    tabela.delete(*tabela.get_children())

    if df is None or df.empty:
        if podsumowanie_label:
            podsumowanie_label.config(text="Brak danych")
        return

    cols = ["ID"] + list(df.columns)
    tabela["columns"] = cols
    tabela["show"] = "headings"

    for col in cols:
        tabela.heading(col, text=col)
        tabela.column(col, width=100)

    for i, row in df.iterrows():
        tabela.insert("", "end", values=[i] + list(row))

    info = f"📦 Rekordy: {len(df)} | 📊 Kolumny: {len(df.columns)}"

    num = df.select_dtypes(include="number")
    if not num.empty:
        srednia = round(num.mean().mean(), 2)
        info += f" | 📈 Średnia: {srednia}"

    if "bmi" in df.columns:
        bmi_mean = round(df["bmi"].mean(), 2)
        info += f" | ⚖️ BMI: {bmi_mean}"

    if podsumowanie_label:
        podsumowanie_label.config(text=info)


# =================
# TOOLBAR
# =================
toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left", padx=5)

ttk.Button(toolbar, text="Szukaj",
           command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left", padx=5)

ttk.Button(toolbar, text="Wczytaj bazę",
           command=lambda: wczytaj_dane(
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left", padx=5)


# =================
# STATYSTYKI OPISOWE (PRZYWRÓCONE)
# =================
tryb_stat = False

def toggle_statystyki():
    global tryb_stat

    df = get_dane()
    if df is None:
        log("Brak danych — najpierw wczytaj bazę", "WARNING")
        return

    if not tryb_stat:
        stats = statystyki_opisowe(df)
        if stats is not None:
            pokaz(stats)

        pokaz_statystyki(df, stat_label)

        stat_label.pack(fill="x", pady=5)
        btn_stat.config(text="Baza")
        tryb_stat = True
    else:
        pokaz(df)
        stat_label.pack_forget()
        btn_stat.config(text="Statystyki opisowe")
        tryb_stat = False


btn_stat = ttk.Button(toolbar, text="Statystyki opisowe", command=toggle_statystyki)
btn_stat.pack(side="left", padx=5)

ttk.Button(toolbar, text="Eksport CSV", command=eksport_csv).pack(side="left", padx=5)
ttk.Button(toolbar, text="Raport PDF", command=raport_pdf).pack(side="left", padx=5)


# =================
# FILTRY
# =================
ramka_filtry = ttk.LabelFrame(tab_dane, text="🔎 Filtry", padding=10)
ramka_filtry.pack(fill="x", padx=10, pady=5)

for i in range(6):
    ramka_filtry.columnconfigure(i, weight=1)

var_k = ttkb.BooleanVar(value=True)
var_m = ttkb.BooleanVar(value=True)

var_cuk_typ1 = ttkb.BooleanVar(value=True)
var_cuk_typ2 = ttkb.BooleanVar(value=True)
var_cuk_brak = ttkb.BooleanVar(value=True)

var_nad_tak = ttkb.BooleanVar(value=True)
var_nad_nie = ttkb.BooleanVar(value=True)

ttk.Label(ramka_filtry, text="Płeć").grid(row=0, column=0)
ttk.Checkbutton(ramka_filtry, text="K", variable=var_k).grid(row=0, column=1)
ttk.Checkbutton(ramka_filtry, text="M", variable=var_m).grid(row=0, column=2)

ttk.Label(ramka_filtry, text="Wiek").grid(row=0, column=3)
entry_min = ttk.Entry(ramka_filtry, width=6)
entry_min.grid(row=0, column=4)
entry_max = ttk.Entry(ramka_filtry, width=6)
entry_max.grid(row=0, column=5)

ttk.Label(ramka_filtry, text="BMI").grid(row=1, column=0)
entry_bmi_min = ttk.Entry(ramka_filtry, width=6)
entry_bmi_min.grid(row=1, column=1)
entry_bmi_max = ttk.Entry(ramka_filtry, width=6)
entry_bmi_max.grid(row=1, column=2)

ttk.Label(ramka_filtry, text="Nadciśnienie").grid(row=1, column=3)
ttk.Checkbutton(ramka_filtry, text="Tak", variable=var_nad_tak).grid(row=1, column=4)
ttk.Checkbutton(ramka_filtry, text="Nie", variable=var_nad_nie).grid(row=1, column=5)

ttk.Label(ramka_filtry, text="Cukrzyca").grid(row=2, column=0)
ttk.Checkbutton(ramka_filtry, text="Typ 1", variable=var_cuk_typ1).grid(row=2, column=1)
ttk.Checkbutton(ramka_filtry, text="Typ 2", variable=var_cuk_typ2).grid(row=2, column=2)
ttk.Checkbutton(ramka_filtry, text="Brak", variable=var_cuk_brak).grid(row=2, column=3)

# =================
# TABELA
# =================
ramka_tabela = ttk.Frame(tab_dane)
ramka_tabela.pack(fill="both", expand=True)

scroll_y = ttk.Scrollbar(ramka_tabela, orient="vertical")
scroll_x = ttk.Scrollbar(ramka_tabela, orient="horizontal")

tabela = ttk.Treeview(
    ramka_tabela,
    yscrollcommand=scroll_y.set,
    xscrollcommand=scroll_x.set
)

scroll_y.config(command=tabela.yview)
scroll_x.config(command=tabela.xview)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")
tabela.pack(fill="both", expand=True)


# =================
# STAT LABEL (PRZYWRÓCONY)
# =================
ramka_stat = ttk.LabelFrame(tab_dane, text="📊 Statystyki opisowe")
ramka_stat.pack(fill="x", padx=10, pady=5)

stat_label = ttk.Label(ramka_stat, text="", justify="left")
stat_label.pack(anchor="w")


# =================
# PODSUMOWANIE
# =================
podsumowanie_label = ttk.Label(
    tab_dane,
    text="",
    justify="left",
    font=("Segoe UI", 10)
)
podsumowanie_label.pack(fill="x", padx=10, pady=5)


# =================
# START
# =================
okno.after(100, lambda: log("Aplikacja uruchomiona"))
