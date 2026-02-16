biblioteka = [
    {"sygnatura": "K/1",  "autor": "Henryk Sienkiewicz",  "tytul": "W pustyni i w puszczy"},
    {"sygnatura": "L/2",  "autor": "Bolesław Prus",       "tytul": "Lalka"},
    {"sygnatura": "M/3",  "autor": "Alexandre Dumas",     "tytul": "Trzej muszkieterowie"},
    {"sygnatura": "M/6",  "autor": "Henryk Sienkiewicz",  "tytul": "Quo vadis"},
    {"sygnatura": "K/2",  "autor": "Alexandre Dumas",     "tytul": "Hrabia Monte Christo"},
    {"sygnatura": "L/10", "autor": "Jan Brzechwa",        "tytul": "Bajki"},
    {"sygnatura": "P/1",  "autor": "Julian Tuwim",        "tytul": "Kwiaty polskie"},
    {"sygnatura": "P/2",  "autor": "A. A. Milne",         "tytul": "Kubuś Puchatek"}
]
def wyswietl_menu():
    print("\n====== Projekt Biblioteka ======")
    print("A – lista książek danego autora")
    print("B – wyszukanie książki")
    print("X – wyjście z programu")
    print("================================")

# Opcja A – lista autorów i wybór jednego
def lista_autorow():
    autorzy = sorted(set(ks["autor"] for ks in biblioteka))

    print("\nLista autorów:")
    for i, autor in enumerate(autorzy, 1):
        print(f"{i}. {autor}")

    try:
        numer = int(input("Podaj numer autora: "))
        if numer < 1 or numer > len(autorzy):
            raise ValueError
    except ValueError:
        print("Błąd: niepoprawny numer!")
        return

    wybrany = autorzy[numer - 1]
    print(f"\nKsiążki autora: {wybrany}")
    for ks in biblioteka:
        if ks["autor"] == wybrany:
            print(f"{ks['sygnatura']}, {ks['autor']}, {ks['tytul']}")


# Opcja B – wyszukiwanie po początku tytułu
def wyszukaj_ksiazke():
    fragment = input("Podaj początek tytułu: ").strip().lower()

    dopasowania = [ks for ks in biblioteka if ks["tytul"].lower().startswith(fragment)]

    if not dopasowania:
        print("Brak książek spełniających kryteria!")
        return

    print("\nWyniki wyszukiwania:")
    for ks in dopasowania:
        print(f"{ks['sygnatura']}, {ks['autor']}, {ks['tytul']}")


def main():
    while True:
        wyswietl_menu()
        wybor = input("Wybierz opcję: ").upper()

        if wybor == "A":
            lista_autorow()
        elif wybor == "B":
            wyszukaj_ksiazke()
        elif wybor == "X":
            print("Zamykanie programu...")
            break
        else:
            print("Niepoprawny wybór! Spróbuj ponownie.")


if __name__ == "__main__":
    main()
