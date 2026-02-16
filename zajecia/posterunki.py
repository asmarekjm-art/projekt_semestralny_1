# Projekt Posterunki

def wyswietl_menu():
    print("Projekt Posterunki")
    print("K – koniec działania")
    print("N – wypisanie liczby posterunków")
    print("? – wypisanie współrzędnych najbliższego i najdalszego posterunku")
    print("D x y – dodanie nowego posterunku o współrzędnych (x, y)")
    print("U – usunięcie najdalszego posterunku")
    print()


def odleglosc_kwadrat(p):
    x, y = p
    return x * x + y * y


posterunki = []

while True:
    wyswietl_menu()
    polecenie = input("Wybierz polecenie: ").strip()

    if not polecenie:
        continue

    cmd = polecenie.split()

    # K – koniec programu
    if cmd[0].lower() == 'k':
        print("Koniec działania programu.")
        break

    # N – liczba posterunków
    elif cmd[0].lower() == 'n':
        print(len(posterunki))

    # D x y – dodanie posterunku
    elif cmd[0].lower() == 'd':
        if len(cmd) != 3:
            print("Błąd: podaj współrzędne x y")
            continue

        x = int(cmd[1])
        y = int(cmd[2])
        posterunki.append((x, y))

    # ? – najbliższy i najdalszy
    elif cmd[0] == '?':
        if len(posterunki) == 0:
            print("Błąd: brak posterunków")
            continue

        najblizszy = min(posterunki, key=odleglosc_kwadrat)
        najdalszy = max(posterunki, key=odleglosc_kwadrat)

        print(f"Najbliższy: {najblizszy[0]} {najblizszy[1]}")
        print(f"Najdalszy: {najdalszy[0]} {najdalszy[1]}")

    # U – usunięcie najdalszego
    elif cmd[0].lower() == 'u':
        if len(posterunki) == 0:
            print("Błąd: brak posterunków")
            continue

        najdalszy = max(posterunki, key=odleglosc_kwadrat)
        posterunki.remove(najdalszy)

    else:
        print("Błąd: nieznane polecenie")
