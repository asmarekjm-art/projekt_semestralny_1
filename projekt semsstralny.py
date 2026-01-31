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

print("Średni wiek kobiet:", kobiety["wiek"].mean())
print("Średni wiek mężczyzn:", mezczyzni["wiek"].mean())