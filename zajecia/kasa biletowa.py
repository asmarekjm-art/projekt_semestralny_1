# ================================
# Kasa biletowa – wersja interaktywna
# ================================

# wczytanie liczby stacji pośrednich
N = int(input("Podaj liczbę stacji pośrednich N: "))

# wczytanie cen biletów
print("Podaj ceny biletów na kolejnych odcinkach (0-1, 1-2, ..., N-(N+1)):")
ceny = list(map(int, input().split()))

# obliczenie tablicy prefiksowej
pref = [0] * (N + 2)
for i in range(1, N + 2):
    pref[i] = pref[i - 1] + ceny[i - 1]

print("\nWpisz K aby zakończyć program")
print("Lub podaj stację początkową i końcową")

# obsługa zapytań
while True:
    start = input("\nPodaj stację początkową (lub K): ")

    if start.lower() == "k":
        break

    end = input("Podaj stację końcową: ")

    try:
        x = int(start)
        y = int(end)
    except ValueError:
        print("Błąd: podaj liczby całkowite")
        continue

    if x < 0 or x > N + 1 or y < 0 or y > N + 1:
        print("Błąd: niepoprawny numer stacji")
    else:
        print("Cena biletu:", abs(pref[y] - pref[x]))

# ===== PODSUMOWANIE NA KOŃCU =====
print("\nPodsumowanie:")
print("Liczba stacji pośrednich:", N)
print("Ceny na odcinkach:")
for i in range(len(ceny)):
    print(f"{i} - {i+1} : {ceny[i]}")