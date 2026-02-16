import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

df = None
canvas = None


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

    pokaz(dane)


# ======================
# WYKRES BMI
# ======================
def wykres_bmi():
    global df, canvas

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "BMI" not in df.columns or "plec" not in df.columns:
        messagebox.showwarning("Błąd", "Brak kolumn BMI lub plec")
        return

    # usuń poprzedni wykres
    if canvas:
        canvas.get_tk_widget().destroy()

    kobiety = df[df["plec"] == "K"]["BMI"]
    mezczyzni = df[df["plec"] == "M"]["BMI"]

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    ax.hist(kobiety, bins=10, alpha=0.6, label="Kobiety")
    ax.hist(mezczyzni, bins=10, alpha=0.6, label="Mężczyźni")

    ax.axvline(18.5, linestyle="--", label="Niedowaga")
    ax.axvline(25, linestyle="--", label="Nadwaga")

    ax.set_title("Rozkład BMI — Kobiety vs Mężczyźni")
    ax.set_xlabel("BMI")
    ax.set_ylabel("Liczba pacjentów")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# ======================
# GUI
# ======================
okno = tk.Tk()
okno.title("Analiza pacjentów")


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

# ===== PRZYCISKI =====
tk.Button(ramka_przyciski, text="Wczytaj CSV", width=22, command=wczytaj_dane).pack(pady=4)

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
    text="Wykres BMI",
    width=22,
    command=wykres_bmi
).pack(pady=4)

# ===== FILTRY =====
tk.Label(ramka_przyciski, text="Płeć").pack()
tk.Checkbutton(ramka_przyciski, text="K", variable=var_k).pack()
tk.Checkbutton(ramka_przyciski, text="M", variable=var_m).pack()

tk.Label(ramka_przyciski, text="Wiek od").pack()
entry_min = tk.Entry(ramka_przyciski)
entry_min.pack()

tk.Label(ramka_przyciski, text="Wiek do").pack()
entry_max = tk.Entry(ramka_przyciski)
entry_max.pack()

tk.Label(ramka_przyciski, text="Cukrzyca").pack()
tk.Checkbutton(ramka_przyciski, text="tak", variable=var_cuk_tak).pack()
tk.Checkbutton(ramka_przyciski, text="nie", variable=var_cuk_nie).pack()

tk.Label(ramka_przyciski, text="Nadciśnienie").pack()
tk.Checkbutton(ramka_przyciski, text="tak", variable=var_nad_tak).pack()
tk.Checkbutton(ramka_przyciski, text="nie", variable=var_nad_nie).pack()

# ===== START =====
okno.mainloop()
