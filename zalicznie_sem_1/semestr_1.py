# =================
# IMPORT BIBLIOTEK
# =================

# standard
from datetime import datetime
from tkinter import filedialog, messagebox, ttk
from io import BytesIO

# data science
import pandas as pd
from scipy.stats import ttest_ind

# wykresy
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# PDF
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet

# GUI
import ttkbootstrap as tk

# =================
# ZMIENNE GLOBALNE
# =================

# dane
df = None
df_filtered = None

# wykresy
canvas = None
current_fig = None

# dane do raportów
current_data = None
current_title = ""

# =================
# FUNKCJE POMOCNICZE
# =================
def get_dane():
    """Zwraca dane po filtrach lub pełną bazę."""

    return df_filtered if df_filtered is not None else df


# WCZYTYWANIE DANYCH CSV
#=================
def wczytaj_dane():
    global df

    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if not path:
        return

    try:
        df = pd.read_csv(path, sep=None, engine="python")

        global df_filtered
        df_filtered = None

        # oblicz BMI jeśli są dane
        if "waga" in df.columns and "wzrost" in df.columns:
            df["BMI"] = df["waga"] / (df["wzrost"] / 100) ** 2

        # nadciśnienie z ciśnienia
        if "cisnienie" in df.columns:

            def nadcisnienie(val):
                try:
                    s, d = val.split("/")
                    return "tak" if int(s) >= 140 or int(d) >= 90 else "nie"
                except:
                    return "nie"

            df["nadcisnienie"] = df["cisnienie"].apply(nadcisnienie)

        pokaz(df)
        pokaz_statystyki(df)

        messagebox.showinfo("Sukces", "Dane wczytane poprawnie")

    except Exception as e:
        messagebox.showerror("Błąd", f"Nie udało się wczytać pliku:\n{e}")

# SORTOWANIE TABELI
#=================
def sortuj_kolumne(col, reverse):

    global df_filtered

    dane = get_dane()

    if dane is None:
        return

    try:
        dane = dane.sort_values(by=col, ascending=not reverse)
    except Exception:
        dane = dane.sort_values(by=col, ascending=not reverse, key=lambda x: x.astype(str))

    df_filtered = dane

    pokaz(dane)

    tabela.heading(
        col,
        command=lambda: sortuj_kolumne(col, not reverse)
    )

# WYŚWIETLANIE TABELI DANYCH
#==============
def pokaz(dane):

    # usuń stare dane z tabeli
    tabela.delete(*tabela.get_children())

    # ustaw kolumny
    tabela["columns"] = list(dane.columns)
    tabela["show"] = "headings"

    # nagłówki kolumn
    for col in dane.columns:
        tabela.heading(
            col,
            text=col,
            command=lambda c=col: sortuj_kolumne(c, False)
        )
        tabela.column(col, anchor="center", width=100, stretch=False)

    # wstaw dane do tabeli
    for row in dane.itertuples(index=False):
        tabela.insert("", "end", values=row)


#FILTROWANIE DANYCH
#==================
def filtruj_dane():

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    dane = df.copy()

    # płeć
    plec = [p for p, var in [("K", var_k), ("M", var_m)] if var.get()]
    if plec:
        dane = dane[dane["plec"].isin(plec)]

    # wiek
    try:
        if entry_min.get():
            dane = dane[dane["wiek"] >= int(entry_min.get())]

        if entry_max.get():
            dane = dane[dane["wiek"] <= int(entry_max.get())]

    except ValueError:
        messagebox.showwarning("Błąd", "Wiek musi być liczbą")
        return

    # cukrzyca
    cuk = [c for c, var in [("tak", var_cuk_tak), ("nie", var_cuk_nie)] if var.get()]
    if cuk:
        dane = dane[dane["cukrzyca"].isin(cuk)]

    # nadciśnienie
    nad = [n for n, var in [("tak", var_nad_tak), ("nie", var_nad_nie)] if var.get()]
    if nad and "nadcisnienie" in dane.columns:
        dane = dane[dane["nadcisnienie"].isin(nad)]

    global df_filtered
    df_filtered = dane

    pokaz(dane)
    pokaz_statystyki(dane)

# WYSZUKIWANIE PACJENTA
#==================
def wyszukaj():

    dane = get_dane()

    if dane is None:
        return

    tekst = search_entry.get().lower()

    # jeśli pole wyszukiwania jest puste
    if not tekst:
        pokaz(dane)
        return

    mask = dane.apply(
        lambda col: col.astype(str).str.lower().str.contains(tekst)
    ).any(axis=1)

    wynik = dane[mask]

    pokaz(wynik)

#=============
# FUNKCJE POMOCNICZE WYKRESÓW
#=============
def wyczysc_wykres():
    global canvas

    if canvas is not None:
        canvas.get_tk_widget().destroy()

#=============
#GENEROWANIE WYKRESÓW
#=================
def wykres_bmi():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "BMI" not in dane.columns or "plec" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak kolumn BMI lub plec")
        return

    wyczysc_wykres()

    kobiety = dane[dane["plec"] == "K"]["BMI"]
    mezczyzni = dane[dane["plec"] == "M"]["BMI"]

    fig = Figure(figsize=(8, 4))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # kobiety
    ax1.hist(kobiety, bins=15, color="pink", alpha=0.7)
    ax1.axvline(18.5, linestyle="--", color="red")
    ax1.axvline(25, linestyle="--", color="green")

    ax1.set_title("Kobiety")
    ax1.set_xlabel("BMI")
    ax1.set_ylabel("Liczba pacjentów")
    ax1.set_xlim(15, 45)
    ax1.grid(alpha=0.3)

    # mężczyźni
    ax2.hist(mezczyzni, bins=15, color="lightblue", alpha=0.7)
    ax2.axvline(18.5, linestyle="--", color="red")
    ax2.axvline(25, linestyle="--", color="green")

    ax2.set_title("Mężczyźni")
    ax2.set_xlabel("BMI")
    ax2.set_xlim(15, 45)
    ax2.grid(alpha=0.3)

    fig.suptitle("Rozkład BMI według płci")

    global current_fig, current_data, current_title

    current_fig = fig
    current_data = dane
    current_title = "Rozkład BMI według płci"



def wykres_nadcisnienie_kolowy():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "nadcisnienie" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak danych o nadciśnieniu")
        return

    wyczysc_wykres()

    counts = dane["nadcisnienie"].value_counts()

    labels = ["Nadciśnienie", "Brak nadciśnienia"]
    values = [
        counts.get("tak", 0),
        counts.get("nie", 0)
    ]

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=["red", "green"],
        startangle=90
    )

    ax.set_title(f"Procent pacjentów z nadciśnieniem (N={len(dane)})")

    global current_fig, current_data, current_title

    current_fig = fig
    current_data = dane
    current_title = "Procent pacjentów z nadciśnieniem"


def wykres_cukrzyca_typ_kolowy():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "cukrzyca" not in dane.columns or "typ_cukrzycy" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak danych o cukrzycy")
        return

    wyczysc_wykres()

    brak = len(dane[dane["cukrzyca"] == "nie"])
    typ1 = len(dane[dane["typ_cukrzycy"] == "typ 1"])
    typ2 = len(dane[dane["typ_cukrzycy"] == "typ 2"])

    labels = ["Brak cukrzycy", "Typ 1", "Typ 2"]
    values = [brak, typ1, typ2]

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        colors=["green", "orange", "red"],
        startangle=90
    )

    ax.set_title(f"Cukrzyca w populacji (N={len(dane)})")

    global current_fig, current_data, current_title

    current_fig = fig
    current_data = dane
    current_title = "Cukrzyca w populacji"

def wykres_leki_cukrzyca():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "leki_na_cukrzyce" not in dane.columns or "cukrzyca" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak danych o cukrzycy lub lekach")
        return

    wyczysc_wykres()

    dane_cukrzyca = dane[dane["cukrzyca"] == "tak"].copy()

    dane_cukrzyca["leki_na_cukrzyce"] = (
        dane_cukrzyca["leki_na_cukrzyce"]
        .fillna("brak leków")
        .replace("", "brak leków")
    )

    counts = dane_cukrzyca["leki_na_cukrzyce"].value_counts()

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    x = range(len(counts))

    ax.bar(x, counts.values, color="purple", alpha=0.7)

    ax.set_xticks(x)
    ax.set_xticklabels(counts.index, rotation=30, ha="right")

    ax.set_ylabel("Liczba pacjentów")
    ax.set_title(f"Leczenie cukrzycy (N={len(dane_cukrzyca)})")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    global current_fig, current_data, current_title

    current_fig = fig
    current_data = dane_cukrzyca
    current_title = "Leczenie cukrzycy"

#=============
#OBLICZANIE STATYSTYK
#=================

#statystyki opisowe
def statystyki_opisowe():

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    # wybierz tylko kolumny liczbowe
    num = dane.select_dtypes(include="number")

    if num.empty:
        messagebox.showwarning("Błąd", "Brak danych liczbowych")
        return

    opis = num.describe().T

    pokaz(opis.round(2))

def pokaz_statystyki(dane):

    global stat_label

    if dane is None or len(dane) == 0:
        stat_label.config(text="Brak danych")
        return

    liczba = len(dane)
    liczba_all = len(df) if df is not None else liczba

    # średni wiek
    sredni_wiek = "-"
    if "wiek" in dane.columns:
        sredni_wiek = round(dane["wiek"].mean(), 1)

    # średni BMI
    sredni_bmi = "-"
    if "BMI" in dane.columns:
        sredni_bmi = round(dane["BMI"].mean(), 1)

    # cukrzyca %
    cuk_proc = "-"
    if "cukrzyca" in dane.columns:
        cuk_proc = round((dane["cukrzyca"] == "tak").mean() * 100, 1)

    # nadciśnienie %
    nad_proc = "-"
    if "nadcisnienie" in dane.columns:
        nad_proc = round((dane["nadcisnienie"] == "tak").mean() * 100, 1)

    tekst = (
        f"Pacjenci: {liczba}/{liczba_all}   |   "
        f"Średni wiek: {sredni_wiek}   |   "
        f"Średni BMI: {sredni_bmi}   |   "
        f"Cukrzyca: {cuk_proc}%   |   "
        f"Nadciśnienie: {nad_proc}%"
    )

    stat_label.config(text=tekst)


#=============
# EKSPORT DANYCH
#================
def eksport_pdf():

    global current_fig, current_data, current_title

    if current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )

    if not path:
        return

    # zapis wykresu do pamięci
    img_buffer = BytesIO()
    current_fig.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
    img_buffer.seek(0)

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    # tytuł raportu
    elements.append(
        Paragraph(
            f"Raport analizy danych pacjentów",
            styles["Heading1"]
        )
    )

    elements.append(Spacer(1, 12))

    # tytuł wykresu
    elements.append(
        Paragraph(
            f"<b>{current_title}</b>",
            styles["Heading2"]
        )
    )

    elements.append(Spacer(1, 12))

    # data raportu
    elements.append(
        Paragraph(
            f"Data raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )

    elements.append(Spacer(1, 20))

    # wykres
    img = Image(img_buffer)
    img.drawHeight = 300
    img.drawWidth = 450

    elements.append(img)
    elements.append(Spacer(1, 20))

    # statystyki
    if current_data is not None:

        liczba = len(current_data)

        tekst = f"Liczba pacjentów w analizie: {liczba}"

        if "wiek" in current_data.columns:
            tekst += f"<br/>Średni wiek: {current_data['wiek'].mean():.1f}"

        if "BMI" in current_data.columns:
            tekst += f"<br/>Średnie BMI: {current_data['BMI'].mean():.1f}"

        elements.append(
            Paragraph(
                tekst,
                styles["Normal"]
            )
        )

    doc.build(elements)

    messagebox.showinfo("Sukces", f"Raport zapisany:\n{path}")

#eksport danych do csv

def eksport_csv():
    global df, df_filtered

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    dane_do_zapisu = df_filtered if df_filtered is not None else df

    path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")]
    )

    if not path:
        return

    dane_do_zapisu.to_csv(path, index=False)

    messagebox.showinfo(
        "Sukces",
        f"Zapisano {len(dane_do_zapisu)} rekordów"
    )
#eksport wykresów do PNG
def eksport_png():

    global current_fig

    if current_fig is None:
        messagebox.showwarning("Brak wykresu", "Najpierw wygeneruj wykres")
        return

    path = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png")]
    )

    if not path:
        return

    current_fig.savefig(path, dpi=300, bbox_inches="tight")

    messagebox.showinfo("Sukces", f"Wykres zapisany:\n{path}")

#=============
#ANALIZA STATYSTYCZNA(T-STUDENTA)
#===========
def okno_ttest():

    global current_fig, current_data, current_title

    dane = get_dane()

    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    win = tk.Toplevel(okno)
    win.title("Test t-Studenta")
    win.geometry("900x650")

    # ===== PANEL GÓRNY =====
    top = ttk.Frame(win)
    top.pack(fill="x", pady=5)

    ttk.Label(top, text="Wybierz analizę:").pack(side="left", padx=5)

    wybor = ttk.Combobox(
        top,
        values=[
            "BMI — Płeć",
            "BMI — Cukrzyca",
            "BMI — Nadciśnienie",
            "Wiek — Płeć"
        ],
        state="readonly",
        width=25
    )
    wybor.pack(side="left", padx=5)
    wybor.current(0)

    ttk.Button(top, text="Uruchom", command=lambda: rysuj()).pack(side="left", padx=5)

    # ===== OBSZAR WYKRESU =====
    plot_frame = ttk.Frame(win)
    plot_frame.pack(fill="both", expand=True)

    # ===== WYNIK TESTU =====
    wynik_label = ttk.Label(
        win,
        text="",
        justify="left",
        font=("Arial", 10)
    )
    wynik_label.pack(pady=5)

    # ===== PANEL DOLNY =====
    bottom = ttk.Frame(win)
    bottom.pack(fill="x", pady=10)

    def rysuj():

        global current_fig, current_data, current_title

        # wyczyść poprzedni wykres
        for widget in plot_frame.winfo_children():
            widget.destroy()

        typ = wybor.get()

        # ===== WYBÓR GRUP =====
        if typ == "BMI — Płeć":

            g1 = dane[dane["plec"] == "K"]["BMI"].dropna()
            g2 = dane[dane["plec"] == "M"]["BMI"].dropna()

            nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
            ylabel = "BMI"

        elif typ == "BMI — Cukrzyca":

            g1 = dane[dane["cukrzyca"] == "tak"]["BMI"].dropna()
            g2 = dane[dane["cukrzyca"] == "nie"]["BMI"].dropna()

            nazwa1, nazwa2 = "Cukrzyca", "Brak"
            ylabel = "BMI"

        elif typ == "BMI — Nadciśnienie":

            g1 = dane[dane["nadcisnienie"] == "tak"]["BMI"].dropna()
            g2 = dane[dane["nadcisnienie"] == "nie"]["BMI"].dropna()

            nazwa1, nazwa2 = "Nadciśnienie", "Brak"
            ylabel = "BMI"

        elif typ == "Wiek — Płeć":

            g1 = dane[dane["plec"] == "K"]["wiek"].dropna()
            g2 = dane[dane["plec"] == "M"]["wiek"].dropna()

            nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
            ylabel = "Wiek"

        else:
            return

        # ===== SPRAWDZENIE DANYCH =====
        if len(g1) < 2 or len(g2) < 2:
            wynik_label.config(text="Za mało danych")
            return

        # ===== TEST T-STUDENTA =====
        t, p = ttest_ind(g1, g2, equal_var=False)

        tekst = (
            f"{nazwa1}: {g1.mean():.2f} ± {g1.std():.2f} (n={len(g1)})\n"
            f"{nazwa2}: {g2.mean():.2f} ± {g2.std():.2f} (n={len(g2)})\n"
            f"t = {t:.3f}    p = {p:.4f}"
        )

        wynik_label.config(text=tekst)

        # ===== WYKRES =====
        fig = Figure(figsize=(6,4))
        ax = fig.add_subplot(111)

        ax.boxplot([g1, g2], tick_labels=[nazwa1, nazwa2])

        ax.set_ylabel(ylabel)
        ax.set_title(typ)
        ax.grid(alpha=0.3)

        canvas = FigureCanvasTkAgg(fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        current_fig = fig
        current_data = dane
        current_title = typ

 # ===== PRZYCISKI =====

    ttk.Button(
        bottom,
        text="Eksport PDF",
        width=15,
        command=eksport_pdf
    ).pack(side="right", padx=10)

    ttk.Button(
        bottom,
        text="Zamknij",
        width=15,
        command=win.destroy
    ).pack(side="right", padx=10)

    rysuj()

#zamknij wykres

def zamknij_wykres():
    global canvas, current_fig

    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None

    current_fig = None


#okno z wykresami
def okno_wykresy():

    global canvas

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    win = tk.Toplevel(okno)
    win.title("Wykresy")
    win.geometry("900x600")


    top = ttk.Frame(win)
    top.pack(fill="x", pady=5)

    ttk.Label(top, text="Wybierz wykres:").pack(side="left", padx=5)

    wybor = ttk.Combobox(
        top,
        values=[
            "BMI",
            "Nadciśnienie %",
            "Cukrzyca typy %",
            "Leki na cukrzycę"
        ],
        state="readonly",
        width=25
    )
    wybor.pack(side="left", padx=5)
    wybor.current(0)

    ttk.Button(top, text="Pokaż", command=lambda: rysuj()).pack(side="left", padx=5)


    plot_frame = ttk.Frame(win)
    plot_frame.pack(fill="both", expand=True)


    bottom = ttk.Frame(win)
    bottom.pack(fill="x", pady=10)

    def rysuj():

        global canvas

        if canvas:
            canvas.get_tk_widget().destroy()

        typ = wybor.get()

        if typ == "BMI":
            wykres_bmi()
        elif typ == "Nadciśnienie %":
            wykres_nadcisnienie_kolowy()
        elif typ == "Cukrzyca typy %":
            wykres_cukrzyca_typ_kolowy()
        elif typ == "Leki na cukrzycę":
            wykres_leki_cukrzyca()

        else:
            return

        canvas = FigureCanvasTkAgg(current_fig, master=plot_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    ttk.Button(
        bottom,
        text="Eksport PDF",
        width=15,
        command=eksport_pdf
    ).pack(side="right", padx=10)

    ttk.Button(
        bottom,
        text="Zamknij",
        width=15,
        command=win.destroy
    ).pack(side="right", padx=10)

    rysuj()

def reset_filtry():

    global df_filtered

    var_k.set(True)
    var_m.set(True)

    var_cuk_tak.set(True)
    var_cuk_nie.set(True)

    var_nad_tak.set(True)
    var_nad_nie.set(True)

    entry_min.delete(0, tk.END)
    entry_max.delete(0, tk.END)

    df_filtered = None

    if df is not None:
        pokaz(df)
        pokaz_statystyki(df)

#rysowanie wykresu
def rysuj_wykres():

    global canvas

    if df is None:
        return

    if canvas:
        canvas.get_tk_widget().destroy()

    tab = notebook_wykresy.tab(notebook_wykresy.select(), "text")

    if tab == "BMI":
        wykres_bmi()

    elif tab == "Nadciśnienie":
        wykres_nadcisnienie_kolowy()

    elif tab == "Cukrzyca":
        wykres_cukrzyca_typ_kolowy()

    elif tab == "Leki":
        wykres_leki_cukrzyca()

    if current_fig is None:
        return

    canvas = FigureCanvasTkAgg(current_fig, master=plot_frame)

    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

#zmien wykresy
def zmien_wykres(event):

    global plot_frame, canvas

    if canvas:
        canvas.get_tk_widget().destroy()

    tab = notebook_wykresy.tab(notebook_wykresy.select(), "text")

    if tab == "BMI":
        plot_frame = ttk.Frame(tab_bmi)

    elif tab == "Nadciśnienie":
        plot_frame = ttk.Frame(tab_nad)

    elif tab == "Cukrzyca":
        plot_frame = ttk.Frame(tab_cuk)

    elif tab == "Leki":
        plot_frame = ttk.Frame(tab_leki)

    plot_frame.pack(fill="both", expand=True)

    rysuj_wykres()

# RYSOWANIE TESTU STATYSTYCZNEGO

def rysuj_test():

    global current_fig

    dane = get_dane()

    if dane is None:
        return

    for widget in plot_stat.winfo_children():
        widget.destroy()

    typ = wybor_test.get()

    if typ == "BMI — Płeć":
        g1 = dane[dane["plec"] == "K"]["BMI"].dropna()
        g2 = dane[dane["plec"] == "M"]["BMI"].dropna()
        nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
        ylabel = "BMI"

    elif typ == "BMI — Cukrzyca":
        g1 = dane[dane["cukrzyca"] == "tak"]["BMI"].dropna()
        g2 = dane[dane["cukrzyca"] == "nie"]["BMI"].dropna()
        nazwa1, nazwa2 = "Cukrzyca", "Brak"
        ylabel = "BMI"

    elif typ == "BMI — Nadciśnienie":
        g1 = dane[dane["nadcisnienie"] == "tak"]["BMI"].dropna()
        g2 = dane[dane["nadcisnienie"] == "nie"]["BMI"].dropna()
        nazwa1, nazwa2 = "Nadciśnienie", "Brak"
        ylabel = "BMI"

    elif typ == "Wiek — Płeć":
        g1 = dane[dane["plec"] == "K"]["wiek"].dropna()
        g2 = dane[dane["plec"] == "M"]["wiek"].dropna()
        nazwa1, nazwa2 = "Kobiety", "Mężczyźni"
        ylabel = "Wiek"

    else:
        return


    if len(g1) < 2 or len(g2) < 2:
        wynik_stat.config(text="Za mało danych")
        return


    t, p = ttest_ind(g1, g2, equal_var=False)

    tekst = (
        f"{nazwa1}: {g1.mean():.2f} ± {g1.std():.2f} (n={len(g1)})\n"
        f"{nazwa2}: {g2.mean():.2f} ± {g2.std():.2f} (n={len(g2)})\n"
        f"t = {t:.3f}    p = {p:.4f}"
    )

    wynik_stat.config(text=tekst)


    fig = Figure(figsize=(6,4))
    ax = fig.add_subplot(111)

    ax.boxplot([g1, g2], tick_labels=[nazwa1, nazwa2])

    ax.set_ylabel(ylabel)
    ax.set_title(typ)
    ax.grid(alpha=0.3)

    canvas = FigureCanvasTkAgg(fig, master=plot_stat)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

    current_fig = fig
#=============
# INTERFEJS GRAFICZNY APLIKACJI (GUI)
#=============
okno = tk.Window(themename="flatly")
okno.title("Analiza pacjentów")

okno.geometry("1200x700")
okno.minsize(1150, 600)

style = ttk.Style()
style.configure("Treeview", rowheight=28, font=("Segoe UI", 10))
style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))



#PANEL STATYSTYK (GÓRNY PASEK)
stat_label = ttk.Label(
    okno,
    text="Brak danych",
    font=("Arial", 10, "bold"),
    anchor="w"
)

stat_label.pack(fill="x", padx=10, pady=5)

#ZAKŁADKI APLIKACJI

notebook = ttk.Notebook(okno)
notebook.pack(fill="both", expand=True)


tab_dane = ttk.Frame(notebook, padding=10)
tab_wykresy = ttk.Frame(notebook, padding=10)
tab_stat = ttk.Frame(notebook, padding=10)

notebook.add(tab_dane, text="Dane")
notebook.add(tab_wykresy, text="Wykresy")
notebook.add(tab_stat, text="Statystyka")



# ===== ZMIENNE =====
var_k = tk.BooleanVar(value=True)
var_m = tk.BooleanVar(value=True)
var_cuk_tak = tk.BooleanVar(value=True)
var_cuk_nie = tk.BooleanVar(value=True)
var_nad_tak = tk.BooleanVar(value=True)
var_nad_nie = tk.BooleanVar(value=True)

# PANEL OPERACJI NA DANYCH

toolbar = ttk.Frame(tab_dane)
toolbar.pack(fill="x", pady=5)

ttk.Label(toolbar, text="Szukaj:").pack(side="left", padx=5)

search_entry = ttk.Entry(toolbar, width=20)
search_entry.pack(side="left")

ttk.Button(
    toolbar,
    text="Szukaj",
    command=wyszukaj
).pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Wczytaj bazę",
    command=wczytaj_dane
).pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Statystyki opisowe",
    command=statystyki_opisowe
).pack(side="left", padx=5)


ttk.Button(
    toolbar,
    text="Eksport CSV",
    command=eksport_csv
).pack(side="left", padx=5)

ttk.Button(
    toolbar,
    text="Eksport PDF",
    command=eksport_pdf
).pack(side="left", padx=5)

#PANEL FILTRÓW DANYCH

ramka_filtry = ttk.LabelFrame(
    tab_dane,
    text="Filtry danych",
    padding=10
)
ramka_filtry.pack(fill="x", padx=10, pady=10)
ramka_filtry.columnconfigure(0, weight=1)
ramka_filtry.columnconfigure(1, weight=1)

#TABELA DANYCH PACJENTÓW

ramka_tabela = ttk.Frame(tab_dane)
ramka_tabela.pack(fill="both", expand=True)
ramka_tabela.pack_propagate(False)

ramka_tree = ttk.Frame(ramka_tabela)
ramka_tree.pack(fill="both", expand=True)

tabela = ttk.Treeview(ramka_tree)

scroll_y = ttk.Scrollbar(ramka_tree, orient="vertical", command=tabela.yview)
scroll_x = ttk.Scrollbar(ramka_tree, orient="horizontal", command=tabela.xview)

tabela.configure(yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set)

scroll_y.pack(side="right", fill="y")
scroll_x.pack(side="bottom", fill="x")

tabela.pack(fill="both", expand=True)


# PANEL WYKRESÓW
# =================

notebook_wykresy = ttk.Notebook(tab_wykresy)
notebook_wykresy.pack(fill="both", expand=True)

tab_bmi = ttk.Frame(notebook_wykresy)
tab_nad = ttk.Frame(notebook_wykresy)
tab_cuk = ttk.Frame(notebook_wykresy)
tab_leki = ttk.Frame(notebook_wykresy)

notebook_wykresy.add(tab_bmi, text="BMI")
notebook_wykresy.add(tab_nad, text="Nadciśnienie")
notebook_wykresy.add(tab_cuk, text="Cukrzyca")
notebook_wykresy.add(tab_leki, text="Leki")
notebook_wykresy.bind("<<NotebookTabChanged>>", zmien_wykres)

plot_frame = ttk.Frame(tab_bmi)
plot_frame.pack(fill="both", expand=True)

frame_export = ttk.Frame(tab_wykresy)
frame_export.pack(pady=5)

ttk.Button(
    frame_export,
    text="Eksport PDF",
    command=eksport_pdf
).pack(side="left", padx=5)

ttk.Button(
    frame_export,
    text="Eksport PNG",
    command=eksport_png
).pack(side="left", padx=5)
# PANEL ANALIZY STATYSTYCZNEJ

top_stat = ttk.Frame(tab_stat)
top_stat.pack(pady=10)

ttk.Label(
    top_stat,
    text="Wybierz analizę:",
    font=("Arial", 11)
).pack(side="left", padx=5)

wybor_test = ttk.Combobox(
    top_stat,
    values=[
        "BMI — Płeć",
        "BMI — Cukrzyca",
        "BMI — Nadciśnienie",
        "Wiek — Płeć"
    ],
    state="readonly",
    width=25
)

wybor_test.pack(side="left", padx=5)
wybor_test.current(0)

ttk.Button(
    top_stat,
    text="Uruchom test",
    command=rysuj_test
).pack(side="left", padx=10)


# RAMKA NA WYKRES

plot_stat = ttk.Frame(tab_stat)
plot_stat.pack(fill="both", expand=True)


# WYNIK TESTU

wynik_stat = ttk.Label(
    tab_stat,
    text="",
    font=("Arial", 10),
    justify="left"
)

wynik_stat.pack(pady=10)


# ===== PŁEĆ =====
sekcja_plec = ttk.LabelFrame(ramka_filtry, text="Płeć")
sekcja_plec.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

ttk.Checkbutton(sekcja_plec, text="Kobiety", variable=var_k).pack(anchor="w")
ttk.Checkbutton(sekcja_plec, text="Mężczyźni", variable=var_m).pack(anchor="w")


# ===== WIEK =====
sekcja_wiek = ttk.LabelFrame(ramka_filtry, text="Wiek")
sekcja_wiek.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

wiek_frame = ttk.Frame(sekcja_wiek)
wiek_frame.pack(fill="x")

ttk.Label(wiek_frame, text="Od:").grid(row=0, column=0, sticky="w")
entry_min = tk.Entry(wiek_frame, width=8)
entry_min.grid(row=0, column=1, padx=5)

ttk.Label(wiek_frame, text="Do:").grid(row=0, column=2, sticky="w")
entry_max = tk.Entry(wiek_frame, width=8)
entry_max.grid(row=0, column=3, padx=5)


# ===== CUKRZYCA =====
sekcja_cuk = ttk.LabelFrame(ramka_filtry, text="Cukrzyca")
sekcja_cuk.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

ttk.Checkbutton(sekcja_cuk, text="Tak", variable=var_cuk_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_cuk, text="Nie", variable=var_cuk_nie).pack(anchor="w")


# ===== NADCIŚNIENIE =====
sekcja_nad = ttk.LabelFrame(ramka_filtry, text="Nadciśnienie")
sekcja_nad.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")

ttk.Checkbutton(sekcja_nad, text="Tak", variable=var_nad_tak).pack(anchor="w")
ttk.Checkbutton(sekcja_nad, text="Nie", variable=var_nad_nie).pack(anchor="w")

frame_btn = ttk.Frame(ramka_filtry)
frame_btn.grid(row=2, column=0, columnspan=2, pady=5)


btn_filtruj = ttk.Button(
    frame_btn,
    text="Filtruj",
    command=filtruj_dane
)

btn_filtruj.pack(side="left", expand=True, fill="x", padx=3)

btn_reset = ttk.Button(
    frame_btn,
    text="Reset",
    command=reset_filtry
)

btn_reset.pack(side="left", expand=True, fill="x", padx=3)


# START APLIKACJI
okno.mainloop()
