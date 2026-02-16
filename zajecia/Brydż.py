import random

# Kolory i wartości
kolory = ["Pik", "Kier", "Karo", "Trefl"]
wartosci = ["A", "K", "D", "W", "10", "9", "8", "7", "6", "5", "4", "3", "2"]

# Tworzymy talię jako listę kart typu (kolor, wartość)
talia = [(kolor, wartosc) for kolor in kolory for wartosc in wartosci]

# Tasowanie talii
random.shuffle(talia)

# Wylosowanie 13 kart (ręka gracza)
reka = talia[:13]

# Punktacja Miltona-Worka
punkty_kart = {
    "A": 4,
    "K": 3,
    "D": 2,
    "W": 1
}

# Funkcja obliczająca punkty
def licz_punkty(reka):
    suma = 0
    for i, wartosc in reka:
        suma += punkty_kart.get(wartosc, 0)
    return suma

# Grupowanie kart według kolorów
reka_kolory = {kolor: [] for kolor in kolory}
for kolor, wartosc in reka:
    reka_kolory[kolor].append(wartosc)

# --- WYŚWIETLENIE WYNIKU ---
for kolor in kolory:
    wartosci_kart = " ".join(reka_kolory[kolor]) if reka_kolory[kolor] else "–"
    print(f"{kolor}: {wartosci_kart}")

print("\nPkt:", licz_punkty(reka))
