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

log_box = ttkb.Text(frame_log, wrap="word")

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
        podsumowanie_label.config(text="Brak AnyChart")
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

    # dodatkowe info jeśli są dane liczbowe
    num = df.select_dtypes(include="number")

    if not num.empty:
        srednia = round(num.mean().mean(), 2)
        info += f" | 📈 Średnia (ogólna): {srednia}"

    # jeśli jest BMI
    if "bmi" in df.columns:
        bmi_mean = round(df["bmi"].mean(), 2)
        info += f" | ⚖️ Średnie BMI: {bmi_mean}"

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
# STATYSTYKI OPISOWE
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

        stat_label.config(text=opis_stat)
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
        lambda d: pokaz_statystyki(d, stat_label),
        entry_bmi_min, entry_bmi_max
)).pack(side="left", padx=5)


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
# OPIS / STATYSTYKI
# =================

opis_stat = """
📊 STATYSTYKI OPISOWE:

• count → liczba obserwacji
• mean → średnia wartość
• std → odchylenie standardowe (zmienność danych)
• min / max → zakres wartości
• 50% → mediana (środkowa wartość)

🧠 Interpretacja:
• niskie std → dane są do siebie podobne
• wysokie std → duże różnice między pacjentami
• średnia ≠ mediana → możliwe wartości odstające
"""

ramka_stat = ttk.LabelFrame(
    tab_dane,
    text="📊 Statystyki opisowe",
    padding=5,
    bootstyle="info"
)
ramka_stat.pack(fill="x", padx=10, pady=5)

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

# canvas + scroll
canvas_stat = ttkb.Canvas(ramka_stat, height=150)
scroll_stat = ttk.Scrollbar(ramka_stat, orient="vertical", command=canvas_stat.yview)

frame_stat_inner = ttk.Frame(canvas_stat)

frame_stat_inner.bind(
    "<Configure>",
    lambda e: canvas_stat.configure(scrollregion=canvas_stat.bbox("all"))
)

canvas_stat.create_window((0, 0), window=frame_stat_inner, anchor="nw")
canvas_stat.configure(yscrollcommand=scroll_stat.set)

canvas_stat.pack(side="left", fill="both", expand=True)
scroll_stat.pack(side="right", fill="y")

# label
stat_label = ttk.Label(
    frame_stat_inner,
    text="",
    justify="left",
    font=("Segoe UI", 10)
)
stat_label.pack(anchor="w")

# =================
# WYKRESY
# =================

sub_notebook = ttk.Notebook(tab_wykresy)
sub_notebook.pack(fill="both", expand=True)

def create_tab(name, func):
    tab = ttk.Frame(sub_notebook)
    sub_notebook.add(tab, text=name)

    current_fig = {"fig": None}

    plot_area = ttk.Frame(tab)
    plot_area.pack(fill="both", expand=True)

    btn_frame = ttk.Frame(tab)
    btn_frame.pack()

    def draw():
        for w in plot_area.winfo_children():
            w.destroy()

        fig = func()
        if fig is None:
            ttk.Label(plot_area, text="Brak danych").pack()
            return

        current_fig["fig"] = fig

        canvas = FigureCanvasTkAgg(fig, master=plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        log(f"Wykres: {name}")

    def save_png():
        if current_fig["fig"]:
            current_fig["fig"].savefig(f"{name}.png")

    def save_pdf():
        if current_fig["fig"]:
            current_fig["fig"].savefig(f"{name}.pdf")

    ttk.Button(btn_frame, text="Odśwież", command=draw).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="PNG", command=save_png).pack(side="left", padx=5)
    ttk.Button(btn_frame, text="PDF", command=save_pdf).pack(side="left", padx=5)

    tab.bind("<Map>", lambda e: draw())


create_tab("BMI", wykres_bmi)
create_tab("Nadciśnienie", wykres_nadcisnienie_kolowy)
create_tab("Cukrzyca", wykres_cukrzyca_typ_kolowy)
create_tab("Leki", wykres_leki_cukrzyca)


# =================
# STATYSTYKA
# =================

sub_stat = ttk.Notebook(tab_stat)
sub_stat.pack(fill="both", expand=True)

def create_stat_tab(name, func):
    tab = ttk.Frame(sub_stat)
    sub_stat.add(tab, text=name)

    plot_area = ttk.Frame(tab)
    plot_area.pack(fill="both", expand=True)

    def draw():
        for w in plot_area.winfo_children():
            w.destroy()

        fig = func()
        if fig is None:
            ttk.Label(plot_area, text="Brak danych").pack()
            return

        canvas = FigureCanvasTkAgg(fig, master=plot_area)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    tab.bind("<Map>", lambda e: draw())


def stat_hist():
    df = get_dane()
    if df is None:
        return None

    num = df.select_dtypes(include="number")
    if num.empty:
        return None

    fig, ax = plt.subplots()
    num.iloc[:, 0].hist(ax=ax)
    ax.set_title("Histogram")
    return fig


def stat_box():
    df = get_dane()
    if df is None:
        return None

    if "bmi" not in df.columns:
        return None

    fig, ax = plt.subplots()
    df.boxplot(column="bmi", ax=ax)
    return fig


create_stat_tab("Histogram", stat_hist)
create_stat_tab("Boxplot BMI", stat_box)


# =================
# ANALIZA
# =================

frame_analiza = ttk.Frame(tab_analiza)
frame_analiza.pack(fill="both", expand=True)

def analiza():
    df = get_dane()
    if df is None:
        log("Brak danych do analizy", "WARNING")
        return

    num = df.select_dtypes(include="number")
    if num.empty:
        return

    for w in frame_analiza.winfo_children():
        w.destroy()

    fig, ax = plt.subplots()

    cax = ax.imshow(num.corr(), cmap="coolwarm")
    fig.colorbar(cax)

    ax.set_xticks(range(len(num.columns)))
    ax.set_yticks(range(len(num.columns)))
    ax.set_xticklabels(num.columns, rotation=45)
    ax.set_yticklabels(num.columns)

    canvas = FigureCanvasTkAgg(fig, master=frame_analiza)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


ttk.Button(frame_analiza, text="Pokaż korelacje", command=analiza).pack()


# =================
# START
# =================

okno.after(100, lambda: log("Aplikacja uruchomiona"))