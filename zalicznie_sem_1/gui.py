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

    if int(log_box.index('end-1c').split('.')[0]) > 200:
        log_box.delete("1.0", "2.0")

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

tryb_stat = False

opis_stat = """
📊 STATYSTYKI OPISOWE:

• count – liczba obserwacji
• mean – średnia wartość
• std – odchylenie standardowe
• min – wartość minimalna
• 25% – pierwszy kwartyl
• 50% – mediana
• 75% – trzeci kwartyl
• max – wartość maksymalna

🧠 Interpretacja:
• niskie std → dane są podobne
• wysokie std → duża zmienność
• mean ≠ median → możliwe wartości odstające
"""

# =================
# TABELA STATYSTYK (ZAKŁADKA STATYSTYKA)
# =================
frame_stat_table = ttk.Frame(tab_stat)
frame_stat_table.pack(fill="both", expand=True, padx=10, pady=5)
frame_stat_table.configure(height=400)
frame_stat_table.pack_propagate(False)

tabela_stat = ttk.Treeview(frame_stat_table)
tabela_stat.pack(fill="both", expand=True)

# =================
# TABELA + FUNKCJA
# =================
def pokaz(df):
    global tabela, podsumowanie_label

    if tabela is None:
        return

    tabela["columns"] = ()
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
        tabela.column(col, width=120, anchor="center")

    for i, row in df.iterrows():
        tabela.insert("", "end", values=[i] + list(row))

def aktualizuj_podsumowanie(df):
    global podsumowanie_label

    if podsumowanie_label is None:
        return

    if df is None or df.empty:
        podsumowanie_label.config(text="Brak danych")
        return

    tekst = f"📦 Pacjenci: {len(df)}"

    if "wiek" in df.columns:
        tekst += f" | 🎂 Śr. wiek: {df['wiek'].mean():.1f}"

    if "bmi" in df.columns:
        tekst += f" | ⚖️ Śr. BMI: {df['bmi'].mean():.2f}"

    if "nadcisnienie" in df.columns:
        nad = df["nadcisnienie"].astype(str).str.lower()
        proc_nad = nad.isin(["tak", "1", "true"]).sum() / len(df) * 100
        tekst += f" | ❤️ Nadciśnienie: {proc_nad:.1f}%"

    if "cukrzyca" in df.columns:
        cuk = df["cukrzyca"].astype(str).str.lower()
        proc_cuk = (~cuk.isin(["brak", "0", "nie", "nan"])).sum() / len(df) * 100
        tekst += f" | 🍬 Cukrzyca: {proc_cuk:.1f}%"

    podsumowanie_label.config(text=tekst)


def generuj_opis(df):
    if df is None or df.empty:
        return "Brak danych do analizy"

    tekst = "📊 Wnioski:\n"

    if "wiek" in df.columns:
        sredni_wiek = df["wiek"].mean()
        if sredni_wiek > 50:
            tekst += "• Populacja raczej starsza\n"
        else:
            tekst += "• Populacja raczej młodsza\n"

    if "bmi" in df.columns:
        bmi = df["bmi"].mean()
        if bmi > 25:
            tekst += "• Średnie BMI powyżej normy\n"
        else:
            tekst += "• BMI w normie\n"

    if "nadcisnienie" in df.columns:
        nad = df["nadcisnienie"].astype(str).str.lower()
        proc = nad.isin(["tak", "1", "true"]).sum() / len(df) * 100

        if proc > 50:
            tekst += "• Dużo przypadków nadciśnienia\n"
        else:
            tekst += "• Niewiele nadciśnienia\n"

    if "cukrzyca" in df.columns:
        cuk = df["cukrzyca"].astype(str).str.lower()
        proc = (~cuk.isin(["brak", "0", "nie", "nan"])).sum() / len(df) * 100

        if proc > 30:
            tekst += "• Wysoki odsetek cukrzycy\n"
        else:
            tekst += "• Niski poziom cukrzycy\n"

    return tekst
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
               po_wczytaniu,
           )).pack(side="left", padx=5)

def pokaz_statystyki_w_tabie(df):
    tabela_stat["columns"] = ()
    tabela_stat.delete(*tabela_stat.get_children())

    if df is None or df.empty:
        return

    stats = statystyki_opisowe(df)
    if stats is None:
        return

    cols = [""] + list(stats.columns)
    tabela_stat["columns"] = cols
    tabela_stat["show"] = "headings"

    for col in cols:
        tabela_stat.heading(col, text=col)
        tabela_stat.column(col, width=120, anchor="center")

    for i, row in stats.iterrows():
        tabela_stat.insert("", "end", values=[i] + list(row))
# =================
# STATYSTYKI OPISOWE (PRZYWRÓCONE)
# =================
def toggle_statystyki():
    global tryb_stat

    df = get_dane()
    if df is None or df.empty:
        log("Brak danych — najpierw wczytaj bazę", "WARNING")
        return

    if not tryb_stat:
        stats = statystyki_opisowe(df)
        if stats is not None:
            pokaz(stats)

        opis_label.config(text=opis_stat)  # 👈 POKAŻ OPIS

        btn_stat.config(text="Pokaż dane")
        tryb_stat = True
        log("Wyświetlono statystyki opisowe")

    else:
        pokaz(df)
        opis_label.config(text=generuj_opis(df))
        btn_stat.config(text="Statystyki opisowe")
        tryb_stat = False
        log("Powrót do danych")

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
        po_wczytaniu,
        entry_bmi_min, entry_bmi_max
)).pack(side="left", padx=5)

ttk.Button(frame_btn, text="Reset",
    command=lambda: reset_filtry(
        var_k, var_m,
        var_cuk_typ1, var_cuk_typ2, var_cuk_brak,
        var_nad_tak, var_nad_nie,
        entry_min, entry_max,
        pokaz,
        po_wczytaniu,
        entry_bmi_min, entry_bmi_max
)).pack(side="left", padx=5)

def po_wczytaniu(d):
    aktualizuj_podsumowanie(d)

    try:
        pokaz_statystyki_w_tabie(d)
    except Exception as e:
        log(f"Błąd statystyki: {e}", "ERROR")

    try:
        if not tryb_stat:
            opis_label.config(text=generuj_opis(d))
    except Exception as e:
        log(f"Błąd opisu: {e}", "ERROR")
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
# PODSUMOWANIE
# =================
podsumowanie_label = ttk.Label(
    tab_dane,
    text="",
    justify="left",
    font=("Segoe UI", 10)
)
podsumowanie_label.pack(fill="x", padx=10, pady=5)

opis_label = ttk.Label(
    tab_dane,
    text="",
    justify="left",
    font=("Segoe UI", 10),
    foreground="gray"
)
opis_label.pack(fill="x", padx=10, pady=(0, 10))
# =================
# =================
# OPIS STATYSTYKI (SCROLL)
# =================
ramka_stat_opis = ttk.LabelFrame(tab_stat, text="📊 Statystyki opisowe")
ramka_stat_opis.pack(fill="x", padx=10, pady=10)
ramka_stat_opis.configure(height=180)
ramka_stat_opis.pack_propagate(False)

canvas_stat = ttkb.Canvas(ramka_stat_opis)
scroll_stat = ttk.Scrollbar(ramka_stat_opis, orient="vertical", command=canvas_stat.yview)

frame_stat_inner = ttk.Frame(canvas_stat)

frame_stat_inner.bind(
    "<Configure>",
    lambda e: canvas_stat.configure(scrollregion=canvas_stat.bbox("all"))
)

canvas_stat.create_window((0, 0), window=frame_stat_inner, anchor="nw")
canvas_stat.configure(yscrollcommand=scroll_stat.set)

canvas_stat.pack(side="left", fill="both", expand=True)
scroll_stat.pack(side="right", fill="y")

opis_stat_label = ttk.Label(
    frame_stat_inner,
    text="",
    justify="left",
    font=("Segoe UI", 11)
)
opis_stat_label.pack(anchor="nw")

# =================
# START
# =================
okno.after(100, lambda: log("Aplikacja uruchomiona poprawnie"))
