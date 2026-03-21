# =================
# IMPORTY
# =================
from datetime import datetime
from tkinter import ttk
import ttkbootstrap as ttkb

import dane, wykresy, statystyka, eksport

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry, get_dane
from statystyka import statystyki_opisowe
from eksport import eksport_csv, raport_pdf

from gui_dane import create_tab_dane
from gui_wykresy import create_tab_wykresy
from gui_analiza import create_tab_analiza


# =================
# OKNO
# =================
okno = ttkb.Window(themename="flatly")
okno.title("JodiApp 📊 | Clinical Data Analysis Suite")
okno.state("zoomed")


# =================
# LOG SYSTEM
# =================
log_box = None
last_log = {"msg": None}


def log(msg, level="INFO"):
    global log_box

    if last_log["msg"] == msg:
        return
    last_log["msg"] = msg

    if int(log_box.index('end-1c').split('.')[0]) > 500:
        log_box.delete("1.0", "50.0")

    czas = datetime.now().strftime("%H:%M:%S")
    log_box.insert("end", f"[{czas}] {level}: {msg}\n")
    log_box.see("end")


# podpinamy logi do modułów
eksport.log = log
dane.log = log
wykresy.log = log
statystyka.log = log


# =================
# LAYOUT GŁÓWNY
# =================
main_pane = ttk.PanedWindow(okno, orient="vertical")
main_pane.pack(fill="both", expand=True)

frame_top = ttk.Frame(main_pane)
main_pane.add(frame_top, weight=5)

header = ttk.Frame(frame_top)
header.pack(fill="x", padx=15, pady=10)

ttk.Label(
    header,
    text="JodiApp",
    font=("Segoe UI", 24, "bold")
).pack(side="left")

ttk.Label(
    header,
    text="  |  Clinical Data Analysis",
    font=("Segoe UI", 14)
).pack(side="left")

ttk.Label(
    header,
    text="v1.0",
    font=("Segoe UI", 9),
    foreground="gray"
).pack(side="right")

frame_log = ttk.LabelFrame(main_pane, text="Logi")
main_pane.add(frame_log, weight=0)
frame_log.configure(height=120)
frame_log.pack_propagate(False)

log_box = ttkb.Text(frame_log, wrap="word")
log_box.pack(fill="both", expand=True)


# =================
# NOTEBOOK
# =================
notebook = ttk.Notebook(frame_top)
notebook.pack(fill="both", expand=True, padx=5, pady=5)

tab_dane = ttk.Frame(notebook)
tab_wykresy = ttk.Frame(notebook)
tab_analiza = ttk.Frame(notebook)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")
notebook.add(tab_analiza, text="Analiza")

create_tab_wykresy(tab_wykresy, log)
create_tab_analiza(tab_analiza, log)


# =================
# TAB: DANE
# =================
frame_toolbar = ttk.Frame(tab_dane)
frame_toolbar.pack(fill="x")

frame_filtry = ttk.Frame(tab_dane)
frame_filtry.pack(fill="x")

frame_tabela = ttk.Frame(tab_dane)
frame_tabela.pack(fill="both", expand=True)

pokaz, podsumowanie, opis, ustaw_opis = create_tab_dane(frame_tabela)


# =================
# CALLBACK PO WCZYTANIU
# =================
def po_wczytaniu(d):
    if d is None:
        return

    try:
        podsumowanie(d)

        try:
            ustaw_opis(opis(d))
        except Exception:
            ustaw_opis("")

    except Exception as e:
        log(f"Błąd po_wczytaniu: {e}", "ERROR")


# =================
# TOOLBAR
# =================
toolbar = ttk.Frame(frame_toolbar)
toolbar.pack(fill="x", pady=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left", padx=5)
search_entry.focus()

search_entry.bind("<Return>", lambda e: wyszukaj(search_entry, pokaz))

ttk.Button(toolbar, text="Szukaj",
           command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left", padx=5)

ttk.Button(toolbar, text="Wczytaj bazę",
           command=lambda: wczytaj_dane(pokaz, po_wczytaniu)
           ).pack(side="left", padx=5)


# =================
# STATYSTYKI OPISOWE
# =================
tryb_stat = False

opis_stat = """📊 STATYSTYKI OPISOWE:

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


def toggle_statystyki():
    global tryb_stat

    df = get_dane()
    if df is None or df.empty:
        log("Brak danych — najpierw wczytaj bazę", "WARNING")
        return

    if not tryb_stat:
        try:
            stats = statystyki_opisowe(df)
            if stats is None or stats.empty:
                stats = df.select_dtypes(include="number").describe()
        except Exception as e:
            log(f"Błąd statystyki: {e}", "ERROR")
            stats = df.select_dtypes(include="number").describe()

        pokaz(stats)
        ustaw_opis(opis_stat)

        btn_stat.config(text="Pokaż dane")
        tryb_stat = True
        log("Wyświetlono statystyki opisowe")

    else:
        pokaz(df)

        try:
            ustaw_opis(opis(df))
        except Exception:
            ustaw_opis("")

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
ramka_filtry = ttk.LabelFrame(frame_filtry, text="🔎 Filtry", padding=10)
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

# UI
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


# =================
# START
# =================
okno.after(100, lambda: log("Aplikacja uruchomiona poprawnie"))
