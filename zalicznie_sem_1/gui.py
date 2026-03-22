# =================
# IMPORTY
# =================
from datetime import datetime
from tkinter import ttk
import ttkbootstrap as ttkb

import dane, wykresy, statystyka, eksport

from dane import wczytaj_dane, filtruj_dane, wyszukaj, reset_filtry, get_dane
from statystyka import statystyki_opisowe

from gui_dane import create_tab_dane
from gui_wykresy import create_tab_wykresy
from gui_analiza import create_tab_analiza
from eksport import zapisz_dane_lub_raport


# =================
# APP FACTORY
# =================
def create_app():

    # ================= OKNO =================
    okno = ttkb.Window(themename="flatly")
    okno.title("JodiApp 📊 | Clinical Data Analysis Suite")
    okno.state("zoomed")

    # ================= LOG SYSTEM =================
    log_box = None
    last_log = {"msg": None}

    def log(msg, level="INFO"):
        nonlocal log_box

        if log_box is None:
            return

        # nie blokuj ERROR/WARNING
        if last_log["msg"] == msg and level == "INFO":
            return
        last_log["msg"] = msg

        try:
            if int(log_box.index('end-1c').split('.')[0]) > 500:
                log_box.delete("1.0", "50.0")
        except:
            pass

        czas = datetime.now().strftime("%H:%M:%S")
        log_box.insert("end", f"[{czas}] {level}: {msg}\n")
        log_box.see("end")

    # podpięcie logów
    eksport.log = log
    dane.log = log
    wykresy.log = log
    statystyka.log = log

    # ================= LAYOUT =================
    main_pane = ttk.PanedWindow(okno, orient="vertical")
    main_pane.pack(fill="both", expand=True)

    frame_top = ttk.Frame(main_pane)
    main_pane.add(frame_top, weight=5)

    # ================= HEADER =================
    header = ttk.Frame(frame_top)
    header.pack(fill="x", pady=10, padx=20)

    header.columnconfigure(0, weight=0)
    header.columnconfigure(1, weight=1)

    logo_frame = ttk.Frame(header)
    logo_frame.grid(row=0, column=0, sticky="w")

    ttk.Label(logo_frame, text="JODI", font=("Bahnschrift SemiBold", 38), foreground="#111827").pack(side="left")
    ttk.Label(logo_frame, text=" ", font=("Bahnschrift SemiBold", 38)).pack(side="left")
    ttk.Label(logo_frame, text="APP", font=("Bahnschrift SemiBold", 38), foreground="#3b82f6").pack(side="left")

    right = ttk.Frame(header)
    right.grid(row=0, column=1, sticky="w", padx=30)

    ttk.Label(right, text="Clinical Data Analysis", font=("Segoe UI", 14), foreground="#1f2937").pack(anchor="w")
    ttk.Label(right, text="Analiza danych medycznych i statystycznych", font=("Segoe UI", 10), foreground="gray").pack(anchor="w")

    # ================= NOTEBOOK =================
    notebook = ttk.Notebook(frame_top)
    notebook.pack(fill="both", expand=True)

    tab_dane = ttk.Frame(notebook)
    tab_wykresy = ttk.Frame(notebook)
    tab_analiza = ttk.Frame(notebook)

    notebook.add(tab_dane, text="Dane")
    notebook.add(tab_wykresy, text="Wykresy")
    notebook.add(tab_analiza, text="Analiza")

    create_tab_wykresy(tab_wykresy, log)
    create_tab_analiza(tab_analiza, log)

    # ================= LOGI =================
    frame_log = ttk.LabelFrame(main_pane, text="Logi")
    main_pane.add(frame_log, weight=0)
    frame_log.configure(height=120)
    frame_log.pack_propagate(False)

    log_box = ttkb.Text(frame_log, wrap="word")
    log_box.pack(fill="both", expand=True)

    # ================= TAB DANE =================
    frame_toolbar = ttk.Frame(tab_dane)
    frame_toolbar.pack(fill="x")

    frame_filtry = ttk.Frame(tab_dane)
    frame_filtry.pack(fill="x")

    frame_tabela = ttk.Frame(tab_dane)
    frame_tabela.pack(fill="both", expand=True)

    pokaz, podsumowanie, opis, ustaw_opis = create_tab_dane(frame_tabela)

    # ================= CALLBACK =================
    def po_wczytaniu(d):
        if d is None:
            return

        try:
            podsumowanie(d)
            try:
                ustaw_opis(opis(d))
            except:
                ustaw_opis("")
        except Exception as e:
            log(f"Błąd: {e}", "ERROR")

    # ================= TOOLBAR =================
    toolbar = ttk.Frame(frame_toolbar)
    toolbar.pack(fill="x", pady=5)

    toolbar_left = ttk.Frame(toolbar)
    toolbar_left.pack(side="left")

    toolbar_right = ttk.Frame(toolbar)
    toolbar_right.pack(side="right")

    search_entry = ttk.Entry(toolbar_left, width=20)
    search_entry.pack(side="left", padx=5)
    search_entry.insert(0, "Szukaj...")
    search_entry.configure(foreground="gray")

    okno.after(200, lambda: search_entry.focus())

    def clear_placeholder(e):
        if search_entry.get() == "Szukaj...":
            search_entry.delete(0, "end")
            search_entry.configure(foreground="black")

    def restore_placeholder(e):
        if not search_entry.get():
            search_entry.insert(0, "Szukaj...")
            search_entry.configure(foreground="gray")

    search_entry.bind("<FocusIn>", clear_placeholder)
    search_entry.bind("<FocusOut>", restore_placeholder)
    search_entry.bind("<Return>", lambda e: wyszukaj(search_entry, pokaz))

    ttk.Button(toolbar_left, text="Szukaj", command=lambda: wyszukaj(search_entry, pokaz)).pack(side="left", padx=5)
    ttk.Button(toolbar_left, text="Wczytaj bazę", command=lambda: wczytaj_dane(pokaz, po_wczytaniu)).pack(side="left", padx=5)

    # ================= STATYSTYKI =================
    tryb_stat = False

    def opis_statystyk():
        return (
            "Statystyki opisowe:\n"
            "• count, mean, std\n"
            "• min / max\n"
            "• kwartyle\n\n"
            "Interpretacja:\n"
            "• wysoka std → duża zmienność\n"
            "• median ≠ mean → asymetria"
        )

    def toggle_statystyki():
        nonlocal tryb_stat

        df = get_dane()
        if df is None or df.empty:
            log("Brak danych — najpierw wczytaj bazę", "WARNING")
            return

        if not tryb_stat:
            try:
                stats = statystyki_opisowe(df)
                if stats is None or stats.empty:
                    stats = df.describe(include="all")
            except Exception as e:
                log(f"Błąd statystyki: {e}", "ERROR")
                stats = df.describe(include="all")

            pokaz(stats)
            ustaw_opis(opis_statystyk())

            btn_stat.config(text="Pokaż dane")
            tryb_stat = True
            log("Wyświetlono statystyki")

        else:
            pokaz(df)
            ustaw_opis(opis(df))

            btn_stat.config(text="Statystyki opisowe")
            tryb_stat = False
            log("Powrót do danych")

    btn_stat = ttk.Button(toolbar_left, text="Statystyki opisowe", command=toggle_statystyki)
    btn_stat.pack(side="left", padx=5)

    ttk.Button(
        toolbar_right,
        text="💾 Zapisz",
        command=lambda: zapisz_dane_lub_raport(log)
    ).pack(side="right", padx=5)

    # ================= FILTRY =================
    ramka_filtry = ttk.LabelFrame(frame_filtry, text="🔎 Filtry", padding=10)
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

    # ================= START =================
    okno.after(100, lambda: log("Aplikacja uruchomiona poprawnie 🚀"))

    return okno