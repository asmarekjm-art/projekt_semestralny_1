import pandas as pd
import os

plik = "pacjenci.csv"

try:
    df = pd.read_csv(plik, encoding="utf-8")
    print("\nTabela wczytana poprawnie:\n")
    print(df.to_string())
except Exception as e:
    print("\nBŁĄD:", e)

print("\n=== KOBIETY ===")
print(kobiety.to_string())

print("\n=== MĘŻCZYŹNI ===")
print(mezczyzni.to_string())
# wyliczenie sredniego wieku dla kazdej płci

kobiety = df[df["plec"] == "K"]
mezczyzni = df[df["plec"] == "M"]

    sciezka = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )

    if not sciezka:
        return

    try:
        df = pd.read_csv(sciezka)
        pole_tekstowe.delete(1.0, tk.END)
        pole_tekstowe.insert(tk.END, df.to_string(index=False))
    except Exception as e:
        messagebox.showerror("Błąd", str(e))

# ======================
# WYKRES BMI vs wiek (K/M)
# ======================
def wykres_bmi():
    global df

    if df is None:
        return

    dane = df.copy()

    # grupy wiekowe
    dane["grupa"] = pd.cut(
        dane["wiek"],
        bins=[0, 20, 40, 60, 80, 200],
        labels=["<20", "20–40", "40–60", "60–80", "80+"],
        right=False
    )

    # średnie BMI dla K i M
    tabela = (
        dane
        .groupby(["grupa", "plec"])["BMI"]
        .mean()
        .unstack()
        .round(1)
    )

    x = range(len(tabela.index))

    plt.figure(figsize=(7,4))

    plt.bar([i-0.2 for i in x], tabela["K"], width=0.4, label="Kobiety")
    plt.bar([i+0.2 for i in x], tabela["M"], width=0.4, label="Mężczyźni")

    plt.xticks(x, tabela.index.astype(str))
    plt.xlabel("Grupa wiekowa")
    plt.ylabel("Średnie BMI")
    plt.title("BMI vs grupy wiekowe dla kobiet i mezczyzn")
    plt.legend()

    plt.show()


# ======================
# pusty przycisk (na przyszłość)
# ======================
# FILTR WIEKU
# ======================
def filtruj_wiek():
    global df

    if df is None:
        return

    try:
        min_wiek = int(entry_min.get())
        max_wiek = int(entry_max.get())

        dane = df[(df["wiek"] >= min_wiek) & (df["wiek"] <= max_wiek)]
        pokaz(dane)

    except:
        messagebox.showwarning("Błąd", "Podaj liczby wieku")


# ======================
# MIN / MAX
# ======================
def pokaz_minmax():
    global df

    if df is None:
        return

    txt = (
        f"Wiek      min: {df['wiek'].min()}   max: {df['wiek'].max()}\n"
        f"BMI       min: {df['BMI'].min():.1f}   max: {df['BMI'].max():.1f}\n"
        f"Ciśnienie min: {df['cisnienie'].min()}   "
        f"max: {df['cisnienie'].max()}"
    )

    pole.delete(1.0, tk.END)
    pole.insert(tk.END, txt)

def wykres_cisnienia():
    global df

    if df is None:
        return

    dane = df.copy()

    dane["grupa"] = pd.cut(
        dane["wiek"],
        bins=[0, 20, 40, 60, 80, 200],
        labels=["<20", "20–40", "40–60", "60–80", "80+"],
        right=False
    )

    srednie = dane.groupby("grupa")["cisnienie_skurczowe"].mean()

    plt.figure(figsize=(6,4))
    plt.bar(srednie.index.astype(str), srednie.values)


# ======================
# GUI
# ======================
okno = tk.Tk()
okno.title("Analiza pacjentów")
okno.geometry("900x500")


# przyciski
btn_wczytaj = tk.Button(okno, text="Wczytaj dane CSV", command=wczytaj_dane)
btn_wczytaj.pack(pady=5)

btn_analiza = tk.Button(okno, text="Analizuj", command=analizuj)
btn_analiza.pack(pady=5)



tk.Label(ramka_przyciski, text="Płeć").pack()
tk.Checkbutton(ramka_przyciski, text="Kobiety", variable=var_k).pack()
tk.Checkbutton(ramka_przyciski, text="Mężczyźni", variable=var_m).pack()


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

tk.Button(ramka_przyciski, text="BMI vs wiek, plec oraz tętno", width=22,
          command=wykres_bmi_wiek_plec_tetno).pack(pady=4)

ramka_wykres = tk.Frame(okno)
ramka_wykres.pack(side="bottom", fill="both", expand=True)


okno.mainloop()