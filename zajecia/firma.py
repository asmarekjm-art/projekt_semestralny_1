# pracownicy: id, imię, nazwisko
pracownicy = {
    12: ("Stanisław", "Kowalski"),
    33: ("Jan", "Wolski"),
    21: ("Ewa", "Kwaśny"),
    44: ("Henryk", "Stawarz"),
    55: ("Janina", "Suchodolska"),
    10: ("Jan", "Miętka")
}

# relacje zwierzchnika: podwładny → szef
zwierzchnik = {
    33: 12,
    21: 33,
    44: 12,
    55: 44,
    10: 44
}

# relacje podwładnych: szef → lista pracowników
podwladni = {}

# budowanie struktury podwładnych
for p, szef in zwierzchnik.items():
    if szef not in podwladni:
        podwladni[szef] = []
    podwladni[szef].append(p)


# =========================================
#   FUNKCJE PROGRAMU
# =========================================

def wyswietl_menu():
    print("\n====== Projekt Firma ======")
    print("A – zwierzchnik")
    print("B – podwładni")
    print("X – wyjście z programu")
    print("===========================")


def opcja_zwierzchnik():
    try:
        p = int(input("Podaj identyfikator pracownika: "))
    except ValueError:
        print("Błąd: identyfikator musi być liczbą!")
        return

    if p not in pracownicy:
        print("Błąd: nie ma takiego pracownika!")
        return

    # czy ma szefa?
    if p not in zwierzchnik:
        print("Prezes")
        return

    szef = zwierzchnik[p]
    imie, nazwisko = pracownicy[szef]
    print(f"Zwierzchnik: {imie} {nazwisko}")


def opcja_podwladni():
    try:
        p = int(input("Podaj identyfikator pracownika: "))
    except ValueError:
        print("Błąd: identyfikator musi być liczbą!")
        return

    if p not in pracownicy:
        print("Błąd: nie ma takiego pracownika!")
        return

    lista = podwladni.get(p, [])

    print(f"Liczba bezpośrednich podwładnych: {len(lista)}")


# =========================================
#   GŁÓWNY PROGRAM
# =========================================

def main():
    while True:
        wyswietl_menu()
        wybor = input("Wybierz opcję: ").upper()

        if wybor == "A":
            opcja_zwierzchnik()
        elif wybor == "B":
            opcja_podwladni()
        elif wybor == "X":
            print("Zamykanie programu...")
            break
        else:
            print("Niepoprawny wybór! Spróbuj ponownie.")


# start
if __name__ == "__main__":
    main()
