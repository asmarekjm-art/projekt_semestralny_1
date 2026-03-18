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
okno.minsize(900, 600)

style = ttk.Style()
style.configure("Treeview", rowheight=26)


# =================
# LAYOUT GŁÓWNY (NAPRAWIONY)
# =================

main_pane = ttk.PanedWindow(okno, orient="vertical")
main_pane.pack(fill="both", expand=True)

# GÓRA
frame_top = ttk.Frame(main_pane)
main_pane.add(frame_top, weight=5)

# DÓŁ (LOGI)
frame_log = ttk.LabelFrame(main_pane, text="Logi")
main_pane.add(frame_log, weight=1)

frame_log.configure(height=120)
frame_log.pack_propagate(False)
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
# -----------------
# ZAKŁADKA DANE (BEZ ZMIAN)
# -----------------
# =================

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left", padx=5)
search_entry.bind("<Return>", lambda e: wyszukaj(search_entry, pokaz))

ttk.Button(toolbar, text="Szukaj",
           command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left", padx=5)

ttk.Button(toolbar, text="Wczytaj bazę",
           command=lambda: wczytaj_dane(
               pokaz,
               lambda d: pokaz_statystyki(d, stat_label)
           )).pack(side="left", padx=5)

ttk.Button(toolbar, text="Statystyki opisowe",
           command=lambda: pokaz(statystyki_opisowe(get_dane()))
           ).pack(side="left", padx=5)

ttk.Button(toolbar, text="Baza",
           command=lambda: pokaz(get_dane())
           ).pack(side="left", padx=5)

ttk.Button(toolbar, text="Eksport CSV",
           command=eksport_csv).pack(side="left", padx=5)

ttk.Button(toolbar, text="Raport PDF",
           command=raport_pdf).pack(side="left", padx=5)


# =================
# FILTRY
# =================

ramka_filtry = ttk.LabelFrame(tab_dane, text="🔎 Filtry", padding=12)
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
        tabela.column(col, width=100)

    for i, row in df.iterrows():
        tabela.insert("", "end", values=[i] + list(row))



stat_label = ttk.Label(tab_dane, text="Brak danych",
                       font=("Segoe UI", 10, "bold"))
stat_label.pack(fill="x", pady=5)

# =================
# -----------------
# ZAKŁADKA WYKRESY
# -----------------
# =================

sub_notebook = ttk.Notebook(tab_wykresy)
sub_notebook.pack(fill="both", expand=True)

tab_bmi = ttk.Frame(sub_notebook)
tab_nad = ttk.Frame(sub_notebook)
tab_cuk = ttk.Frame(sub_notebook)
tab_leki = ttk.Frame(sub_notebook)

sub_notebook.add(tab_bmi, text="BMI")
sub_notebook.add(tab_nad, text="Nadciśnienie")
sub_notebook.add(tab_cuk, text="Cukrzyca")
sub_notebook.add(tab_leki, text="Leki")

current_fig = None


def stworz_widok_wykresu(parent, funkcja, nazwa):
    frame = ttk.Frame(parent)
    frame.pack(fill="both", expand=True)

    plot_area = ttk.Frame(frame)
    plot_area.pack(fill="both", expand=True)

    bottom_panel = ttk.Frame(frame)
    bottom_panel.pack(pady=10)

    def pokaz():
        nonlocal plot_area
        global current_fig

        for w in plot_area.winfo_children():
            w.destroy()

        fig = funkcja()

        if fig is None:
            ttk.Label(plot_area, text="Brak danych do wykresu").pack(expand=True)
            return

        current_fig = fig

        canvas = FigureCanvasTkAgg(fig, master=plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        log(f"Wykres: {nazwa}")

    def eksport_png():
        if current_fig:
            current_fig.savefig(f"{nazwa}.png")
            log(f"Zapisano {nazwa}.png")

    def eksport_pdf():
        if current_fig:
            current_fig.savefig(f"{nazwa}.pdf")
            log(f"Zapisano {nazwa}.pdf")

    ttk.Button(bottom_panel, text="Odśwież", command=pokaz).pack(side="left", padx=5)
    ttk.Button(bottom_panel, text="Zapisz PNG", command=eksport_png).pack(side="left", padx=5)
    ttk.Button(bottom_panel, text="Zapisz PDF", command=eksport_pdf).pack(side="left", padx=5)

    return pokaz


# tworzenie wykresów
load_bmi = stworz_widok_wykresu(tab_bmi, wykres_bmi, "BMI")
load_nad = stworz_widok_wykresu(tab_nad, wykres_nadcisnienie_kolowy, "Nadcisnienie")
load_cuk = stworz_widok_wykresu(tab_cuk, wykres_cukrzyca_typ_kolowy, "Cukrzyca")
load_leki = stworz_widok_wykresu(tab_leki, wykres_leki_cukrzyca, "Leki")


def on_tab_change(event):
    selected = event.widget.select()
    tab = event.widget.tab(selected, "text")

    if tab == "BMI":
        load_bmi()
    elif tab == "Nadciśnienie":
        load_nad()
    elif tab == "Cukrzyca":
        load_cuk()
    elif tab == "Leki":
        load_leki()


sub_notebook.bind("<<NotebookTabChanged>>", on_tab_change)

# =================
# -----------------
# ZAKŁADKA STATYSTYKA (NAPRAWA)
# -----------------
# =================

frame_stat = ttk.Frame(tab_stat)
frame_stat.pack(fill="both", expand=True, padx=10, pady=10)

ttk.Label(frame_stat, text="Wybierz zmienną:").pack(anchor="w")

stat_var = ttkb.StringVar()

combo_stat = ttk.Combobox(frame_stat, textvariable=stat_var, state="readonly")
combo_stat.pack(fill="x", pady=5)

stat_text = ttkb.Text(frame_stat)
stat_text.pack(fill="both", expand=True)


def odswiez_kolumny():
    dane_df = get_dane()
    if dane_df is not None:
        combo_stat["values"] = list(dane_df.columns)


def pokaz_stat():
    dane_df = get_dane()

    if dane_df is None:
        log("Brak danych", "WARNING")
        return

    kol = stat_var.get()

    if kol not in dane_df.columns:
        log("Wybierz zmienną", "WARNING")
        return

    wynik = statystyki_opisowe(dane_df[[kol]])

    stat_text.delete("1.0", "end")
    stat_text.insert("end", str(wynik))


ttk.Button(frame_stat, text="Pokaż statystyki",
           command=pokaz_stat).pack(pady=5)


def odswiez_statystyka(event=None):
    odswiez_kolumny()


tab_stat.bind("<Visibility>", odswiez_statystyka)


# =================
# -----------------
# ZAKŁADKA ANALIZA (NAPRAWA)
# -----------------
# =================

frame_analiza = ttk.Frame(tab_analiza)
frame_analiza.pack(fill="both", expand=True, padx=10, pady=10)

analiza_text = ttkb.Text(frame_analiza)
analiza_text.pack(fill="both", expand=True)


def analiza_korelacji():
    dane_df = get_dane()

    if dane_df is None:
        log("Brak danych", "WARNING")
        return

    if dane_df.select_dtypes(include="number").empty:
        log("Brak danych numerycznych", "WARNING")
        return

    corr = dane_df.corr(numeric_only=True)

    analiza_text.delete("1.0", "end")
    analiza_text.insert("end", str(corr))


ttk.Button(frame_analiza, text="Pokaż korelacje",
           command=analiza_korelacji).pack(pady=5)

# =================
# LOGI
# =================

log_box = ttkb.Text(frame_log)

scroll = ttk.Scrollbar(frame_log, command=log_box.yview)
log_box.configure(yscrollcommand=scroll.set)

log_box.pack(side="left", fill="both", expand=True)
scroll.pack(side="right", fill="y")


def log(msg, level="INFO"):
    czas = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{czas}] {level}: {msg}\n")
    log_box.see("end")


eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log

okno.after(100, lambda: log("Aplikacja uruchomiona"))