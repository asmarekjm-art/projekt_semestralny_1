import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.stats import ttest_ind
from datetime import datetime
#import
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

df = None
canvas = None

df_filtered = None

current_fig = None
current_data = None
current_title = ""

# ======================
# WCZYTYWANIE CSV
# ======================
def wczytaj_dane():
    global df

    path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if not path:
        return

    try:
        df = pd.read_csv(path)
        # ===== oblicz BMI jeśli są dane =====
        if "waga" in df.columns and "wzrost" in df.columns:
            df["BMI"] = df["waga"] / (df["wzrost"] / 100) ** 2

        # ===== nadciśnienie z ciśnienia =====
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



# ======================
# POKAZ DANE
# ======================
def pokaz(dane):
    pole.delete("1.0", tk.END)
    pole.insert(tk.END, dane.to_string())


# ======================
# FILTRUJ
# ======================
def filtruj_dane():
    global df

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    dane = df.copy()

    # ===== PŁEĆ =====
    plec = []
    if var_k.get():
        plec.append("K")
    if var_m.get():
        plec.append("M")

    if plec:
        dane = dane[dane["plec"].isin(plec)]

    # ===== WIEK =====
    try:
        if entry_min.get() != "":
            dane = dane[dane["wiek"] >= int(entry_min.get())]

        if entry_max.get() != "":
            dane = dane[dane["wiek"] <= int(entry_max.get())]

    except ValueError:
        messagebox.showwarning("Błąd", "Wiek musi być liczbą")
        return


    # ===== CUKRZYCA =====
    cuk = []
    if var_cuk_tak.get():
        cuk.append("tak")
    if var_cuk_nie.get():
        cuk.append("nie")

    if cuk:
        dane = dane[dane["cukrzyca"].isin(cuk)]

    # ===== NADCIŚNIENIE =====
    nad = []
    if var_nad_tak.get():
        nad.append("tak")
    if var_nad_nie.get():
        nad.append("nie")

    if nad and "nadcisnienie" in dane.columns:
        dane = dane[dane["nadcisnienie"].isin(nad)]

    global df_filtered
    df_filtered = dane

    pokaz(dane)
    pokaz_statystyki(dane)


# ======================
# WYKRES BMI
# ======================
def wykres_bmi():
    global df, canvas
    dane = df_filtered if df_filtered is not None else df
    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "BMI" not in dane.columns or "plec" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak kolumn BMI lub plec")
        return

    if canvas:
        canvas.get_tk_widget().destroy()

    kobiety = dane[dane["plec"] == "K"]["BMI"]
    mezczyzni = dane[dane["plec"] == "M"]["BMI"]

    fig = Figure(figsize=(8, 4))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    # ===== Kobiety =====
    ax1.hist(kobiety, bins=15, color="pink", alpha=0.7)
    ax1.axvline(18.5, linestyle="--", color="red")
    ax1.axvline(25, linestyle="--", color="green")

    ax1.set_title("Kobiety")
    ax1.set_xlabel("BMI")
    ax1.set_ylabel("Liczba pacjentów")
    ax1.set_xlim(15, 45)
    ax1.grid(alpha=0.3)

    # ===== Mężczyźni =====
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


#=====
#nadcisnienie
def wykres_nadcisnienie_kolowy():
    global df, canvas
    dane = df_filtered if df_filtered is not None else df
    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "nadcisnienie" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak danych o nadciśnieniu")
        return

    if canvas:
        canvas.get_tk_widget().destroy()

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


#=========
#wykres cykrzyca podział na typ 1 i 2 oraz brak

def wykres_cukrzyca_typ_kolowy():
    global df, canvas
    dane = df_filtered if df_filtered is not None else df
    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "cukrzyca" not in df.columns or "typ_cukrzycy" not in df.columns:
        messagebox.showwarning("Błąd", "Brak danych o cukrzycy")
        return

    if canvas:
        canvas.get_tk_widget().destroy()

    # liczby
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


#======
# wykres słupkowy lekow na cukrzyce

def wykres_leki_cukrzyca():
    global df, canvas
    dane = df_filtered if df_filtered is not None else df
    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "leki_na_cukrzyce" not in df.columns or "cukrzyca" not in df.columns:
        messagebox.showwarning("Błąd", "Brak danych o cukrzycy lub lekach")
        return

    if canvas:
        canvas.get_tk_widget().destroy()

    # tylko osoby z cukrzycą
    dane_cukrzyca = dane[dane["cukrzyca"] == "tak"].copy()

    # brak leków jeśli puste
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



#======
#statystyka
def pokaz_statystyki(dane):

    global stat_label

    if dane is None or len(dane) == 0:
        stat_label.config(
            text="Brak danych",
            bg="#f8d7da"
        )
        return

    liczba = len(dane)

    sredni_wiek = round(dane["wiek"].mean(), 1) if "wiek" in dane.columns else "-"
    sredni_bmi = round(dane["BMI"].mean(), 1) if "BMI" in dane.columns else "-"

    if "cukrzyca" in dane.columns:
        cuk_proc = round((dane["cukrzyca"] == "tak").mean() * 100, 1)
    else:
        cuk_proc = "-"

    tekst = (
        f"Pacjenci: {liczba}   |   "
        f"Średni wiek: {sredni_wiek}   |   "
        f"Średni BMI: {sredni_bmi}   |   "
        f"Cukrzyca: {cuk_proc}%"
    )

    stat_label.config(
        text=tekst,
        bg="#d4edda"
    )

#PDF
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

    from io import BytesIO

    img_buffer = BytesIO()
    current_fig.savefig(img_buffer, format="png", dpi=300, bbox_inches="tight")
    img_buffer.seek(0)

    pdfmetrics.registerFont(TTFont("Arial", "arial.ttf"))

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    for style in styles.byName.values():
        style.fontName = "Arial"

    elements = []

    elements.append(
        Paragraph(
            f"Data raportu: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            styles["Normal"]
        )
    )
    elements.append(Spacer(1, 12))

    img = Image(img_buffer)
    img.drawHeight = 300
    img.drawWidth = 450

    elements.append(img)
    elements.append(Spacer(1, 12))

    if current_data is not None:
        elements.append(
            Paragraph(
                f"Liczba pacjentów w analizie (N = {len(current_data)})",
                styles["Normal"]
            )
        )
    doc.build(elements)

    messagebox.showinfo("Sukces", f"Zapisano PDF:\n{path}")

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

#Statystyka -Tstudenta dla bmi
def statystyka_ttest():

    global df, df_filtered

    dane = df_filtered if df_filtered is not None else df

    if dane is None or len(dane) == 0:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    if "BMI" not in dane.columns or "plec" not in dane.columns:
        messagebox.showwarning("Błąd", "Brak kolumn BMI lub plec")
        return

    k = dane[dane["plec"] == "K"]["BMI"].dropna()
    m = dane[dane["plec"] == "M"]["BMI"].dropna()

    if len(k) < 2 or len(m) < 2:
        messagebox.showwarning("Błąd", "Za mało danych")
        return

    # ===== TEST =====
    t, p = ttest_ind(k, m, equal_var=False)

    tekst = (
        f"BMI Kobiety vs Mężczyźni\n\n"
        f"Kobiety: {k.mean():.2f} ± {k.std():.2f} (n={len(k)})\n"
        f"Mężczyźni: {m.mean():.2f} ± {m.std():.2f} (n={len(m)})\n\n"
        f"t = {t:.3f}\n"
        f"p = {p:.5f}"
    )

    # ===== OKNO =====
    win = tk.Toplevel(okno)
    win.title("Test t-Studenta")
    win.geometry("700x600")

    top = tk.Frame(win)
    top.pack(fill="x", pady=10)

    tk.Label(
        top,
        text=tekst,
        justify="left",
        font=("Arial", 10)
    ).pack(anchor="w", padx=10)

    # ===== WYKRES =====
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    from matplotlib.figure import Figure
    import numpy as np

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    ax.boxplot(
        [k, m],
        labels=["Kobiety", "Mężczyźni"],
        patch_artist=True
    )

    x1 = np.random.normal(1, 0.04, size=len(k))
    x2 = np.random.normal(2, 0.04, size=len(m))

    ax.scatter(x1, k, alpha=0.6)
    ax.scatter(x2, m, alpha=0.6)

    ax.set_ylabel("BMI")
    ax.set_title("BMI — Kobiety vs Mężczyźni")

    canvas = FigureCanvasTkAgg(fig, master=win)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    # ===== PRZYCISK ZAMKNIJ =====
    tk.Button(
        win,
        text="Zamknij",
        bg="#e53935",
        fg="white",
        width=15,
        command=win.destroy
    ).pack(pady=10)


#zamknij wykres
def zamknij_wykres():
    global canvas, current_fig

    if canvas:
        canvas.get_tk_widget().destroy()
        canvas = None

    current_fig = None


#okno z wykresami
from tkinter import ttk

def okno_wykresy():

    global canvas

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    win = tk.Toplevel(okno)
    win.title("Wykresy")
    win.geometry("900x600")

    # ===== GÓRA =====
    top = tk.Frame(win)
    top.pack(fill="x", pady=5)

    tk.Label(top, text="Wybierz wykres:").pack(side="left", padx=5)

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

    tk.Button(top, text="Pokaż", command=lambda: rysuj()).pack(side="left", padx=5)

    # ===== ŚRODEK =====
    plot_frame = tk.Frame(win)
    plot_frame.pack(fill="both", expand=True)

    # ===== DÓŁ =====
    bottom = tk.Frame(win)
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

    tk.Button(
        bottom,
        text="Eksport PDF",
        bg="#3949ab",
        fg="white",
        width=15,
        command=eksport_pdf
    ).pack(side="right", padx=10)

    tk.Button(
        bottom,
        text="Zamknij",
        bg="#e53935",
        fg="white",
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
# ======================
# GUI
# ======================
okno = tk.Tk()
okno.title("Analiza pacjentów")

#===statystyka
stat_label = tk.Label(
    okno,
    text="Brak danych",
    font=("Arial", 10, "bold"),
    bg="#f8d7da",
    anchor="w",
    padx=10
)

stat_label.pack(fill="x")

# ===== ZMIENNE =====
var_k = tk.BooleanVar(value=True)
var_m = tk.BooleanVar(value=True)
var_cuk_tak = tk.BooleanVar(value=True)
var_cuk_nie = tk.BooleanVar(value=True)
var_nad_tak = tk.BooleanVar(value=True)
var_nad_nie = tk.BooleanVar(value=True)

# ===== LEWA STRONA =====
ramka_tabela = tk.Frame(okno)
ramka_tabela.pack(side="left", fill="both", expand=True)

scroll = tk.Scrollbar(ramka_tabela)
scroll.pack(side="right", fill="y")

pole = tk.Text(ramka_tabela, wrap="none", yscrollcommand=scroll.set)
pole.pack(side="left", fill="both", expand=True)

scroll.config(command=pole.yview)

# ===== PRAWA STRONA =====
ramka_przyciski = tk.Frame(okno)
ramka_przyciski.pack(side="right", fill="y", padx=10, pady=10)

tk.Label(ramka_przyciski, text="Panel sterowania", font=("Arial", 10, "bold")).pack(pady=5)

#wczytak dane
tk.Button(
    ramka_przyciski,
    text="Wczytaj CSV",
    width=22,
    bg="royal blue",
    fg="white",
    activebackground="#c62828",
    activeforeground="white",
    command=wczytaj_dane
).pack(pady=4)


# ===== MENU WYKRESÓW =====
tk.Button(
    ramka_przyciski,
    text="Wykresy",
    width=22,
    bg="royal blue",
    fg="white",
    command=okno_wykresy
).pack(pady=4)


#statystyka
tk.Button(
    ramka_przyciski,
    text="Statystyka t-Studenta",
    width=22,
    bg="pink",
    fg="white",
    command=statystyka_ttest
).pack(pady=4)

# ===== RAMKA FILTRÓW =====
ramka_filtry = tk.LabelFrame(
    ramka_przyciski,
    text="Filtry pacjentów",
    padx=10,
    pady=10,
    bg="#f5f6fa",
    font=("Arial", 9, "bold")
)
ramka_filtry.pack(pady=8, fill="x")


# ===== PŁEĆ =====
sekcja_plec = tk.LabelFrame(ramka_filtry, text="Płeć", bg="#f5f6fa")
sekcja_plec.pack(fill="x", pady=5)

tk.Checkbutton(sekcja_plec, text="Kobiety", variable=var_k, bg="#f5f6fa").pack(anchor="w")
tk.Checkbutton(sekcja_plec, text="Mężczyźni", variable=var_m, bg="#f5f6fa").pack(anchor="w")


# ===== WIEK =====
sekcja_wiek = tk.LabelFrame(ramka_filtry, text="Wiek", bg="#f5f6fa")
sekcja_wiek.pack(fill="x", pady=5)

wiek_frame = tk.Frame(sekcja_wiek, bg="#f5f6fa")
wiek_frame.pack(fill="x")

tk.Label(wiek_frame, text="Od:", bg="#f5f6fa").grid(row=0, column=0, sticky="w")
entry_min = tk.Entry(wiek_frame, width=8)
entry_min.grid(row=0, column=1, padx=5)

tk.Label(wiek_frame, text="Do:", bg="#f5f6fa").grid(row=0, column=2, sticky="w")
entry_max = tk.Entry(wiek_frame, width=8)
entry_max.grid(row=0, column=3, padx=5)


# ===== CUKRZYCA =====
sekcja_cuk = tk.LabelFrame(ramka_filtry, text="Cukrzyca", bg="#f5f6fa")
sekcja_cuk.pack(fill="x", pady=5)

tk.Checkbutton(sekcja_cuk, text="Tak", variable=var_cuk_tak, bg="#f5f6fa").pack(anchor="w")
tk.Checkbutton(sekcja_cuk, text="Nie", variable=var_cuk_nie, bg="#f5f6fa").pack(anchor="w")


# ===== NADCIŚNIENIE =====
sekcja_nad = tk.LabelFrame(ramka_filtry, text="Nadciśnienie", bg="#f5f6fa")
sekcja_nad.pack(fill="x", pady=5)

tk.Checkbutton(sekcja_nad, text="Tak", variable=var_nad_tak, bg="#f5f6fa").pack(anchor="w")
tk.Checkbutton(sekcja_nad, text="Nie", variable=var_nad_nie, bg="#f5f6fa").pack(anchor="w")

frame_btn = tk.Frame(ramka_filtry, bg="#f5f6fa")
frame_btn.pack(fill="x", pady=8)

btn_filtruj = tk.Button(
    frame_btn,
    text="Filtruj",
    bg="#43a047",
    fg="white",
    activebackground="#2e7d32",
    activeforeground="white",
    relief="flat",
    height=1,
    command=filtruj_dane
)
btn_filtruj.pack(side="left", expand=True, fill="x", padx=3)

btn_reset = tk.Button(
    frame_btn,
    text="Reset",
    bg="#757575",
    fg="white",
    activebackground="#424242",
    activeforeground="white",
    relief="flat",
    height=1,
    command=reset_filtry
)
btn_reset.pack(side="left", expand=True, fill="x", padx=3)
tk.Button(
    ramka_przyciski,
    text="Eksport danych",
    width=22,
    bg="#4CAF50",      # zielony
    fg="white",        # biały tekst
    command=eksport_csv
).pack(pady=4)



# ===== START =====
okno.mainloop()
