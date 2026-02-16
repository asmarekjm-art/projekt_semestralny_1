import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

df = None
canvas = None


# ======================
# WYŚWIETLANIE (kolor BMI)
# ======================
def pokaz(dane):
    pole.delete(1.0, tk.END)

    pole.tag_config("green", foreground="green")
    pole.tag_config("orange", foreground="orange")
    pole.tag_config("red", foreground="red")

    tekst = dane.to_string(index=False)
    linie = tekst.split("\n")

    ma_bmi = "BMI" in dane.columns

    for linia in linie:
        if ma_bmi and linia.strip() != "" and not linia.startswith("ID"):
            try:
                bmi = float(linia.split()[-1])

                if bmi < 25:
                    pole.insert(tk.END, linia + "\n", "green")
                elif bmi < 30:
                    pole.insert(tk.END, linia + "\n", "orange")
                else:
                    pole.insert(tk.END, linia + "\n", "red")

            except:
                pole.insert(tk.END, linia + "\n")
        else:
            pole.insert(tk.END, linia + "\n")


# ======================
# WCZYTYWANIE CSV
# ======================
def wczytaj_dane():
    global df

    sciezka = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if not sciezka:
        return

    try:
        df = pd.read_csv(sciezka)
        pokaz(df)
    except Exception as e:
        messagebox.showerror("Błąd", str(e))


# ======================
# FILTRY
# ======================
def filtruj_dane():
    global df

    if df is None:
        return

    dane = df.copy()

    plec = []
    if var_k.get():
        plec.append("K")
    if var_m.get():
        plec.append("M")

    if plec:
        dane = dane[dane["plec"].isin(plec)]

    try:
        if entry_min.get():
            dane = dane[dane["wiek"] >= int(entry_min.get())]
        if entry_max.get():
            dane = dane[dane["wiek"] <= int(entry_max.get())]
    except:
        messagebox.showwarning("Błąd", "Wiek musi być liczbą")
        return

    cuk = []
    if var_cuk_tak.get():
        cuk.append("tak")
    if var_cuk_nie.get():
        cuk.append("nie")

    if cuk:
        dane = dane[dane["cukrzyca"].isin(cuk)]

    nad = []
    if var_nad_tak.get():
        nad.append("tak")
    if var_nad_nie.get():
        nad.append("nie")

    if nad:
        dane = dane[dane["nadcisnienie"].isin(nad)]

    pokaz(dane)


# ======================
# WYKRES BMI vs wiek
# ======================
def wykres_bmi():
    global canvas

    if df is None:
        return

    dane = df.copy()

    dane["grupa"] = pd.cut(
        dane["wiek"],
        bins=[0, 20, 40, 60, 80, 200],
        labels=["<20", "20–40", "40–60", "60–80", "80+"],
        right=False
    )

    tabela = dane.groupby(["grupa", "plec"])["BMI"].mean().unstack()

    if canvas:
        canvas.get_tk_widget().destroy()

    fig = Figure(figsize=(5, 3))
    ax = fig.add_subplot(111)

    x = range(len(tabela.index))

    if "K" in tabela:
        ax.bar([i-0.2 for i in x], tabela["K"], width=0.4, label="K")
    if "M" in tabela:
        ax.bar([i+0.2 for i in x], tabela["M"], width=0.4, label="M")

    ax.set_xticks(list(x))
    ax.set_xticklabels(tabela.index.astype(str))
    ax.set_ylabel("BMI")
    ax.set_title("BMI vs wiek")
    ax.legend()

    canvas = FigureCanvasTkAgg(fig, master=ramka_wykres)
    canvas.draw()
    canvas.get_tk_widget().pack(fill="both", expand=True)


# ======================
# STATUS CIŚNIENIA (tylko na lekach)
# ======================
def tabela_status_cisnienia():
    global df

    if df is None:
        return

    dane = df.copy()
    dane = dane[dane["leki_cisnienie"] != "brak"]

    cis = dane["cisnienie"].str.split("/", expand=True)
    dane["sk"] = cis[0].astype(int)
    dane["roz"] = cis[1].astype(int)

    def klasyfikuj(s, r):
        if s >= 140 or r >= 90:
            return "nadciśnienie"
        elif s < 90 or r < 60:
            return "hipotonia"
        else:
            return "prawidłowe"

    dane["status"] = [klasyfikuj(s, r) for s, r in zip(dane["sk"], dane["roz"])]

    wynik = dane[["plec", "wiek", "leki_cisnienie", "cisnienie", "status"]]

    pokaz(wynik)


# ======================
# LISTA PACJENTÓW Z CUKRZYCĄ
# ======================
def tabela_pacjenci_cukrzyca():
    global df

    if df is None:
        return

    dane = df[df["cukrzyca"] == "tak"]

    wynik = dane[["plec","wiek", "typ_cukrzycy", "leczenie_cukrzycy", "BMI"]]

    pokaz(wynik)


# ======================
# GUI
# ======================
okno = tk.Tk()
okno.title("Analiza pacjentów")



var_k = tk.BooleanVar(value=True)
var_m = tk.BooleanVar(value=True)
var_cuk_tak = tk.BooleanVar(value=True)
var_cuk_nie = tk.BooleanVar(value=True)
var_nad_tak = tk.BooleanVar(value=True)
var_nad_nie = tk.BooleanVar(value=True)


ramka_tabela = tk.Frame(okno)
ramka_tabela.pack(side="left", fill="both", expand=True)

scroll = tk.Scrollbar(ramka_tabela)
scroll.pack(side="right", fill="y")

pole = tk.Text(ramka_tabela, wrap="none", yscrollcommand=scroll.set)
pole.pack(side="left", fill="both", expand=True)

scroll.config(command=pole.yview)


ramka_przyciski = tk.Frame(okno)
ramka_przyciski.pack(side="right", fill="y", padx=10, pady=10)

tk.Button(ramka_przyciski, text="Wczytaj CSV", width=22, command=wczytaj_dane).pack(pady=4)

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

tk.Button(ramka_przyciski, text="Zastosuj filtry", width=22, command=filtruj_dane).pack(pady=6)
tk.Button(ramka_przyciski, text="Wykres BMI", width=22, command=wykres_bmi).pack(pady=4)
tk.Button(ramka_przyciski, text="Status ciśnienia", width=22, command=tabela_status_cisnienia).pack(pady=4)
tk.Button(ramka_przyciski, text="Pacjenci z cukrzycą", width=22, command=tabela_pacjenci_cukrzyca).pack(pady=4)

ramka_wykres = tk.Frame(okno)
ramka_wykres.pack(side="bottom", fill="both", expand=True)

okno.mainloop()
