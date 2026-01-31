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
def analizuj():
    messagebox.showinfo("Info", "Tu później dodamy analizę 😉")


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