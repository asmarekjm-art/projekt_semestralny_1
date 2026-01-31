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


# pole do wyświetlania tabeli
pole_tekstowe = tk.Text(okno, wrap="none")
pole_tekstowe.pack(fill="both", expand=True)


okno.mainloop()