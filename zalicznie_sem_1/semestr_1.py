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

    if canvas:
        canvas.get_tk_widget().destroy()

    kobiety = df[df["plec"] == "K"]["BMI"]
    mezczyzni = df[df["plec"] == "M"]["BMI"]

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

    canvas = FigureCanvasTkAgg(fig, master=ramka_tabela)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)

#==================
# leki a cisnienie
#==================
def wykres_leki_cisnienie():
    global df, canvas

    if df is None:
        messagebox.showwarning("Brak danych", "Najpierw wczytaj plik CSV")
        return

    if "leki_na_cisnienie" not in df.columns or "cisnienie" not in df.columns:
        messagebox.showwarning("Błąd", "Brak danych o lekach lub ciśnieniu")
        return

    if canvas:
        canvas.get_tk_widget().destroy()

    # pobierz skurczowe
    def skurczowe(val):
        try:
            return int(str(val).split("/")[0])
        except:
            return None

    df["cis_sk"] = df["cisnienie"].apply(skurczowe)

    z_lekami = df[df["leki_na_cisnienie"] != "brak lekow"]["cis_sk"].dropna()
    bez_lekow = df[df["leki_na_cisnienie"] == "brak lekow"]["cis_sk"].dropna()

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    # punkty pacjentów
    ax.scatter([1]*len(bez_lekow), bez_lekow, alpha=0.4, color="orange", label="Bez leków")
    ax.scatter([2]*len(z_lekami), z_lekami, alpha=0.4, color="blue", label="Z lekami")

    # średnie
    ax.scatter(1, bez_lekow.mean(), color="black", s=80, marker="D")
    ax.scatter(2, z_lekami.mean(), color="black", s=80, marker="D")

    # linia nadciśnienia
    ax.axhline(140, linestyle="--", color="red", label="Nadciśnienie ≥140")

    ax.set_xticks([1, 2])
    ax.set_xticklabels(["Bez leków", "Z lekami"])

    ax.set_ylabel("Ciśnienie skurczowe")
    ax.set_title("Ciśnienie vs leczenie")
    ax.grid(alpha=0.3)
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


tk.Button(ramka_przyciski, text="Wczytaj CSV", width=22, command=wczytaj_dane).pack(pady=4)

tk.Button(
    ramka_przyciski,
    text="Wykres BMI",
    width=22,
    command=wykres_bmi
).pack(pady=4)

tk.Button(
    ramka_przyciski,
    text="Leki a ciśnienie",
    width=22,
    command=wykres_leki_cisnienie
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

tk.Button(
    ramka_przyciski,
    text="Filtruj dane",
    width=22,
    bg="#4CAF50",
    fg="white",
    command=filtruj_dane
).pack(pady=6)
# ===== START =====
okno.mainloop()
