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