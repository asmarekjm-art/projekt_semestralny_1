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
# LAYOUT
# =================

main_pane = ttk.PanedWindow(okno, orient="vertical")
main_pane.pack(fill="both", expand=True)

frame_top = ttk.Frame(main_pane)
main_pane.add(frame_top, weight=5)

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
# DANE
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



def toggle_statystyki():
    global tryb_stat

    df = get_dane()
    if df is None:
        return

    if not tryb_stat:
        stats = statystyki_opisowe(df)

        if stats is None or stats.empty:
            stat_label.config(text="Brak danych")
            return

        pokaz(stats)
        stat_label.config(text=opis_stat)
        stat_label.pack(fill="x", pady=5)

        btn_stat.config(text="Baza")
        tryb_stat = True

    else:
        pokaz(df)
        stat_label.pack_forget()

        btn_stat.config(text="Statystyki opisowe")
        tryb_stat = False

btn_stat = ttk.Button(
    toolbar,
    text="Statystyki opisowe",
    command=toggle_statystyki
)
btn_stat.pack(side="left", padx=5)

ttk.Button(toolbar, text="Eksport CSV",
           command=eksport_csv).pack(side="left", padx=5)

ttk.Button(toolbar, text="Raport PDF",
           command=raport_pdf).pack(side="left", padx=5)

tryb_stat = False
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

opis_stat = """
STATYSTYKI OPISOWE:

count – liczba obserwacji
mean – średnia wartość
std – odchylenie standardowe

min / max – zakres wartości

25% – dolny kwartyl
50% – mediana
75% – górny kwartyl

Interpretacja:
- niskie std → dane podobne
- wysokie std → duże różnice
"""

stat_label = ttk.Label(
    tab_dane,
    text="",
    justify="left",
    font=("Segoe UI", 9)
)
stat_label.pack(fill="x", pady=5)

# =================
# WYKRESY
# =================

sub_notebook = ttk.Notebook(tab_wykresy)
sub_notebook.pack(fill="both", expand=True)

tabs = {}
current_fig = None


def create_tab(name, func):
    tab = ttk.Frame(sub_notebook)
    sub_notebook.add(tab, text=name)

    frame = ttk.Frame(tab)
    frame.pack(fill="both", expand=True)

    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=0)
    frame.columnconfigure(0, weight=1)

    plot_area = ttk.Frame(frame)
    plot_area.grid(row=0, column=0, sticky="nsew")

    bottom = ttk.Frame(frame)
    bottom.grid(row=1, column=0, sticky="ew", pady=10)

    def draw():
        global current_fig

        for w in plot_area.winfo_children():
            w.destroy()

        fig = func()

        if fig is None:
            ttk.Label(plot_area, text="Brak danych do wykresu").pack(expand=True)
            return

        current_fig = fig

        canvas = FigureCanvasTkAgg(fig, master=plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        log(f"Wykres: {name}")

    def save_png():
        if current_fig:
            current_fig.savefig(f"{name}.png")
            log(f"Zapisano {name}.png")

    def save_pdf():
        if current_fig:
            current_fig.savefig(f"{name}.pdf")
            log(f"Zapisano {name}.pdf")

    ttk.Button(bottom, text="Odśwież", command=draw).pack(side="left", padx=5)
    ttk.Button(bottom, text="Zapisz PNG", command=save_png).pack(side="left", padx=5)
    ttk.Button(bottom, text="Zapisz PDF", command=save_pdf).pack(side="left", padx=5)

    tabs[str(tab)] = draw
    return draw


create_tab("BMI", wykres_bmi)
create_tab("Nadcisnienie", wykres_nadcisnienie_kolowy)
create_tab("Cukrzyca", wykres_cukrzyca_typ_kolowy)
create_tab("Leki", wykres_leki_cukrzyca)


def on_tab_change(event):
    selected_tab = str(event.widget.select())
    if selected_tab in tabs:
        tabs[selected_tab]()


sub_notebook.bind("<<NotebookTabChanged>>", on_tab_change)
okno.after(250, lambda: on_tab_change(type("e", (), {"widget": sub_notebook})()))
okno.after(200, lambda: list(tabs.values())[0]() if tabs and get_dane() is not None else None)


# =================
# STATYSTYKA
# =================

sub_stat = ttk.Notebook(tab_stat)
sub_stat.pack(fill="both", expand=True)

current_fig_stat = None


def create_stat_tab(name, draw_func):
    tab = ttk.Frame(sub_stat)
    sub_stat.add(tab, text=name)

    frame = ttk.Frame(tab)
    frame.pack(fill="both", expand=True)

    frame.rowconfigure(0, weight=1)
    frame.rowconfigure(1, weight=0)
    frame.columnconfigure(0, weight=1)

    plot_area = ttk.Frame(frame)
    plot_area.grid(row=0, column=0, sticky="nsew")

    bottom = ttk.Frame(frame)
    bottom.grid(row=1, column=0, sticky="ew", pady=10)

    def draw():
        global current_fig_stat

        for w in plot_area.winfo_children():
            w.destroy()

        fig = draw_func()

        if fig is None:
            ttk.Label(plot_area, text="Brak danych").pack(expand=True)
            return

        current_fig_stat = fig

        canvas = FigureCanvasTkAgg(fig, master=plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        log(f"Statystyka: {name}")

    ttk.Button(bottom, text="Odśwież", command=draw).pack(side="left", padx=5)

    return draw


def stat_hist():
    df = get_dane()
    if df is None:
        return None

    num = df.select_dtypes(include="number")
    if num.empty:
        return None

    fig, ax = plt.subplots()
    num.iloc[:, 0].dropna().hist(ax=ax, bins=20)
    ax.set_title(f"Rozkład: {num.columns[0]}")
    return fig


def stat_ttest():
    df = get_dane()
    if df is None:
        return None

    cols = {c.lower(): c for c in df.columns}

    if "bmi" not in cols:
        return None

    plec_col = next((cols[k] for k in ["plec", "płeć", "gender"] if k in cols), None)
    if plec_col is None:
        return None

    k = df[df[plec_col] == "K"][cols["bmi"]].dropna()
    m = df[df[plec_col] == "M"][cols["bmi"]].dropna()

    if len(k) == 0 or len(m) == 0:
        return None

    fig, ax = plt.subplots()
    ax.hist(k, alpha=0.6, label="K")
    ax.hist(m, alpha=0.6, label="M")

    ax.legend()
    ax.set_title("t-Studenta (BMI K vs M)")
    return fig


def stat_boxplot():
    df = get_dane()
    if df is None:
        return None

    cols = {c.lower(): c for c in df.columns}

    if "bmi" not in cols:
        return None

    fig, ax = plt.subplots()
    df.boxplot(column=cols["bmi"], ax=ax)

    ax.set_title("Boxplot BMI")
    return fig


load_hist = create_stat_tab("Rozkład", stat_hist)
load_t = create_stat_tab("t-Studenta", stat_ttest)
load_box = create_stat_tab("Boxplot", stat_boxplot)

stat_tabs = {
    "Rozkład": load_hist,
    "t-Studenta": load_t,
    "Boxplot": load_box
}


def on_stat_change(event):
    tab_name = event.widget.tab(event.widget.select(), "text")
    if tab_name in stat_tabs:
        stat_tabs[tab_name]()


sub_stat.bind("<<NotebookTabChanged>>", on_stat_change)

# 🔥 auto start statystyki
okno.after(400, lambda: on_stat_change(type("e", (), {"widget": sub_stat})()))


# =================
# ANALIZA
# =================

frame_analiza = ttk.Frame(tab_analiza)
frame_analiza.pack(fill="both", expand=True, padx=10, pady=10)


def analiza():
    df = get_dane()
    if df is None:
        return

    num = df.select_dtypes(include="number")
    if num.empty:
        return

    for w in frame_analiza.winfo_children():
        w.destroy()

    corr = num.corr()

    fig, ax = plt.subplots()
    cax = ax.imshow(corr, cmap="coolwarm")

    ax.set_xticks(range(len(corr.columns)))
    ax.set_yticks(range(len(corr.columns)))
    ax.set_xticklabels(corr.columns, rotation=45)
    ax.set_yticklabels(corr.columns)

    fig.colorbar(cax)

    canvas = FigureCanvasTkAgg(fig, master=frame_analiza)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


ttk.Button(frame_analiza, text="Pokaż korelacje", command=analiza).pack()


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