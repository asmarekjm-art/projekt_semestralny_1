import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from scipy.stats import ttest_ind
#import
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont

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

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)
#=====
#nadcisnienie
def wykres_nadcisnienie_kolowy():
    global df, canvas
    dane = df_filtered if df_filtered is not None else df
    if dane is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "nadcisnienie" not in df.columns:
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

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


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

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()

    canvas.get_tk_widget().pack(fill="both", expand=True)

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

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

#+=============
# eksport danych do pliku .csv
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

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    for style in styles.byName.values():
        style.fontName = "HYSMyeongJo-Medium"

    elements = []

    elements.append(Paragraph(current_title, styles["Heading1"]))
    elements.append(Spacer(1, 12))

    img = Image(img_buffer)
    img.drawHeight = 300
    img.drawWidth = 450

    elements.append(img)
    elements.append(Spacer(1, 12))

    if current_data is not None and len(current_data) > 0:

        data_table = [list(current_data.columns)]

        for _, row in current_data.head(20).iterrows():
            data_table.append([str(x) for x in row])

        table = Table(data_table, repeatRows=1)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, -1), "HYSMyeongJo-Medium"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))

        elements.append(Paragraph("Dane (pierwsze 20 rekordów)", styles["Heading2"]))
        elements.append(table)

    doc.build(elements)

    messagebox.showinfo("Sukces", f"Zapisano PDF:\n{path}")


#======
#statystyka
def pokaz_statystyki(dane):
    global stat_label

    if dane is None or len(dane) == 0:
        stat_label.config(text="Brak danych")
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

    stat_label.config(text=tekst)

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

    # zapis wykresu jako obraz
    img_path = "temp_plot.png"
    current_fig.savefig(img_path, dpi=300, bbox_inches="tight")

    pdfmetrics.registerFont(UnicodeCIDFont("HYSMyeongJo-Medium"))

    doc = SimpleDocTemplate(path, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    style = styles["Heading1"]
    style.fontName = "HYSMyeongJo-Medium"

    elements.append(Paragraph(current_title, style))
    elements.append(Spacer(1, 12))

    # obraz wykresu
    elements.append(Image(img_path, width=450, height=300))
    elements.append(Spacer(1, 12))

    # dane tabelaryczne
    if current_data is not None:
        data_table = [list(current_data.columns)]

        for _, row in current_data.head(20).iterrows():
            data_table.append(list(row))

        table = Table(data_table)

        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.black),
            ("FONTNAME", (0, 0), (-1, -1), "HYSMyeongJo-Medium"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
        ]))

        elements.append(Paragraph("Dane (pierwsze 20 rekordów)", styles["Heading2"]))
        elements.append(table)

    doc.build(elements)

    messagebox.showinfo("Sukces", "Zapisano PDF")

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

#Statystyka Tstudenta
def statystyka_ttest():
    global df, df_filtered

    dane = df_filtered if df_filtered is not None else df

    if dane is None or len(dane) == 0:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj dane")
        return

    wyniki = []

    try:

        # ===== BMI K vs M =====
        if "BMI" in dane.columns and "plec" in dane.columns:

            k = dane[dane["plec"] == "K"]["BMI"].dropna()
            m = dane[dane["plec"] == "M"]["BMI"].dropna()

            if len(k) > 1 and len(m) > 1:
                t, p = ttest_ind(k, m, equal_var=False)

                wyniki.append(
                    f"BMI Kobiety vs Mężczyźni\n"
                    f"K: {k.mean():.2f} ± {k.std():.2f} (n={len(k)})\n"
                    f"M: {m.mean():.2f} ± {m.std():.2f} (n={len(m)})\n"
                    f"p = {p:.4f}\n"
                )

        # ===== BMI cukrzyca =====
        if "BMI" in dane.columns and "cukrzyca" in dane.columns:

            tak = dane[dane["cukrzyca"] == "tak"]["BMI"].dropna()
            nie = dane[dane["cukrzyca"] == "nie"]["BMI"].dropna()

            if len(tak) > 1 and len(nie) > 1:
                t, p = ttest_ind(tak, nie, equal_var=False)

                wyniki.append(
                    f"BMI Cukrzyca vs Brak\n"
                    f"Cukrzyca: {tak.mean():.2f} ± {tak.std():.2f} (n={len(tak)})\n"
                    f"Brak: {nie.mean():.2f} ± {nie.std():.2f} (n={len(nie)})\n"
                    f"p = {p:.4f}\n"
                )

        # ===== BMI nadciśnienie =====
        if "BMI" in dane.columns and "nadcisnienie" in dane.columns:

            tak = dane[dane["nadcisnienie"] == "tak"]["BMI"].dropna()
            nie = dane[dane["nadcisnienie"] == "nie"]["BMI"].dropna()

            if len(tak) > 1 and len(nie) > 1:
                t, p = ttest_ind(tak, nie, equal_var=False)

                wyniki.append(
                    f"BMI Nadciśnienie vs Brak\n"
                    f"Nadciśnienie: {tak.mean():.2f} ± {tak.std():.2f} (n={len(tak)})\n"
                    f"Brak: {nie.mean():.2f} ± {nie.std():.2f} (n={len(nie)})\n"
                    f"p = {p:.4f}\n"
                )

    except Exception as e:
        messagebox.showerror("Błąd", str(e))
        return

    if not wyniki:
        messagebox.showinfo("Wyniki", "Brak danych do testów")
        return

    tekst = "\n-----------------------\n".join(wyniki)

    messagebox.showinfo("Test t-Studenta", tekst)

# ======================
# GUI
# ======================
okno = tk.Tk()
okno.title("Analiza pacjentów")

#===statystyka
stat_label = tk.Label(
    okno,
    text="Statystyki pojawią się po wczytaniu danych",
    font=("Arial", 10, "bold"),
    bg="#ecf0f1",
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

tk.Button(ramka_przyciski, text="Wczytaj CSV", width=22, command=wczytaj_dane).pack(pady=4)


# ===== MENU WYKRESÓW =====
menu_button = tk.Menubutton(
    ramka_przyciski,
    text="Wykresy",
    width=22,
    relief="raised"
)

menu_button.pack(pady=4)

menu = tk.Menu(menu_button, tearoff=0)
menu_button.config(menu=menu)

menu.add_command(label="Wykres BMI", command=wykres_bmi)
menu.add_command(label="Nadciśnienie %", command=wykres_nadcisnienie_kolowy)
menu.add_command(label="Cukrzyca typy %", command=wykres_cukrzyca_typ_kolowy)
menu.add_command(label="Leki na cukrzycę", command=wykres_leki_cukrzyca)

#pdf

tk.Button(
    ramka_przyciski,
    text="Eksport wykres do PDF",
    width=22,
    bg="#2196F3",
    fg="white",
    command=eksport_pdf
).pack(pady=4)

tk.Button(
    ramka_przyciski,
    text="Statystyka t-Studenta",
    width=22,
    bg="#9C27B0",
    fg="white",
    command=statystyka_ttest
).pack(pady=4)

# ===== RAMKA FILTRÓW =====
ramka_filtry = tk.LabelFrame(ramka_przyciski, text="Filtry", padx=5, pady=5)
ramka_filtry.pack(pady=5, fill="x")

# ===== FILTRY =====
tk.Label(ramka_filtry, text="Płeć").pack()
tk.Checkbutton(ramka_filtry, text="K", variable=var_k).pack()
tk.Checkbutton(ramka_filtry, text="M", variable=var_m).pack()

tk.Label(ramka_filtry, text="Wiek od").pack()
entry_min = tk.Entry(ramka_filtry)
entry_min.pack()

tk.Label(ramka_filtry, text="Wiek do").pack()
entry_max = tk.Entry(ramka_filtry)
entry_max.pack()

tk.Label(ramka_filtry, text="Cukrzyca").pack()
tk.Checkbutton(ramka_filtry, text="tak", variable=var_cuk_tak).pack()
tk.Checkbutton(ramka_filtry, text="nie", variable=var_cuk_nie).pack()

tk.Label(ramka_filtry, text="Nadciśnienie").pack()
tk.Checkbutton(ramka_filtry, text="tak", variable=var_nad_tak).pack()
tk.Checkbutton(ramka_filtry, text="nie", variable=var_nad_nie).pack()


tk.Button(
    ramka_przyciski,
    text="Filtruj dane",
    width=22,
    bg="#4CAF50",
    fg="white",
    command=filtruj_dane
).pack(pady=6)

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
