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
from statystyka import statystyki_opisowe, pokaz_statystyki
from wykresy import *
from eksport import eksport_csv, raport_pdf


# =================
# OKNO
# =================

okno = ttkb.Window(themename="flatly")
okno.title("Analiza pacjentów")
okno.geometry("1200x720")

# =================
# GLOBALNE DANE
# =================

aktualne_dane = None


# =================
# LOGI
# =================

log_boxes = []


def stworz_log_panel(parent):
    frame = ttk.LabelFrame(parent, text="Logi")
    frame.pack(fill="x", padx=5, pady=5)

    box = ttkb.Text(frame, height=7)
    box.pack(side="left", fill="both", expand=True)

    scroll = ttk.Scrollbar(frame, command=box.yview)
    scroll.pack(side="right", fill="y")
    box.configure(yscrollcommand=scroll.set)

    box.tag_config("ERROR", foreground="red")
    box.tag_config("SUCCESS", foreground="green")

    log_boxes.append(box)


def log(msg, level="INFO"):
    czas = datetime.now().strftime("%H:%M:%S")
    txt = f"[{czas}] {level}: {msg}\n"

    for b in log_boxes:
        b.insert("end", txt, level)
        b.see("end")


# =================
# ZAKŁADKI
# =================

notebook = ttk.Notebook(okno)
notebook.pack(fill="both", expand=True)

tab_dane = ttk.Frame(notebook)
tab_wykresy = ttk.Frame(notebook)
tab_stat = ttk.Frame(notebook)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")
notebook.add(tab_stat, text="Statystyka")


# =================
# TOOLBAR DANE
# =================

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x")

search_entry = ttk.Entry(toolbar)
search_entry.pack(side="left")

ttk.Button(toolbar, text="Szukaj",
           command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left")

ttk.Button(toolbar, text="Wczytaj",
           command=lambda: wczytaj_dane(
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left")

ttk.Button(toolbar, text="Eksport CSV", command=eksport_csv).pack(side="left")
ttk.Button(toolbar, text="PDF", command=raport_pdf).pack(side="left")


# =================
# FILTRY (MINIMAL)
# =================

ramka_filtry = ttk.LabelFrame(tab_dane, text="Filtry")
ramka_filtry.pack(fill="x")

var_k = ttkb.BooleanVar(value=True)
var_m = ttkb.BooleanVar(value=True)

ttk.Checkbutton(ramka_filtry, text="K", variable=var_k).pack(side="left")
ttk.Checkbutton(ramka_filtry, text="M", variable=var_m).pack(side="left")

ttk.Button(ramka_filtry, text="Filtruj",
           command=lambda: filtruj_dane(
               var_k, var_m,
               None, None,
               None, None,
               None, None,
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left")


# =================
# TABELA
# =================

tabela = ttk.Treeview(tab_dane)
tabela.pack(fill="both", expand=True)


def pokaz(df):
    global aktualne_dane
    aktualne_dane = df

    tabela.delete(*tabela.get_children())

    if df is None or df.empty:
        log("Brak danych", "ERROR")
        return

    tabela["columns"] = list(df.columns)
    tabela["show"] = "headings"

    for col in df.columns:
        tabela.heading(col, text=col)

    for _, row in df.iterrows():
        tabela.insert("", "end", values=list(row))


# =================
# STAT LABEL
# =================

stat_label = ttk.Label(tab_dane, text="Brak danych")
stat_label.pack()

stworz_log_panel(tab_dane)


# =================
# WYKRESY TAB
# =================

panel_btn = ttk.Frame(tab_wykresy)
panel_btn.pack(fill="x")

plot = ttk.Frame(tab_wykresy)
plot.pack(fill="both", expand=True)


def rysuj(fig):
    for w in plot.winfo_children():
        w.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


def wykres(f):
    fig = f()
    rysuj(fig)
    log(f"Wykres: {f.__name__}", "SUCCESS")


ttk.Button(panel_btn, text="BMI", command=lambda: wykres(wykres_bmi)).pack(side="left")
ttk.Button(panel_btn, text="Nadciśnienie", command=lambda: wykres(wykres_nadcisnienie_kolowy)).pack(side="left")

ttk.Button(panel_btn, text="CSV", command=eksport_csv).pack(side="right")
ttk.Button(panel_btn, text="PDF", command=raport_pdf).pack(side="right")

stworz_log_panel(tab_wykresy)


# =================
# STATYSTYKA TAB
# =================

toolbar_stat = ttk.Frame(tab_stat)
toolbar_stat.pack(fill="x")

ttk.Button(toolbar_stat, text="CSV", command=eksport_csv).pack(side="left")
ttk.Button(toolbar_stat, text="PDF", command=raport_pdf).pack(side="left")

plot_stat = ttk.Frame(tab_stat)
plot_stat.pack(fill="both", expand=True)


def wykres_stat(f):
    fig = f()
    for w in plot_stat.winfo_children():
        w.destroy()

    canvas = FigureCanvasTkAgg(fig, master=plot_stat)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


ttk.Button(toolbar_stat, text="BMI", command=lambda: wykres_stat(wykres_bmi)).pack(side="left")

stworz_log_panel(tab_stat)


# =================
# PODPIĘCIE LOGÓW
# =================

eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log

okno.after(100, lambda: log("Start", "SUCCESS"))