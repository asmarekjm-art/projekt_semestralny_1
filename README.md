# Analiza danych pacjentów – aplikacja Python

Projekt wykonany w ramach przedmiotu **Analityk danych biomedycznych**.

Aplikacja umożliwia analizę danych medycznych pacjentów z pliku CSV, ich filtrowanie, obliczanie statystyk oraz wizualizację wyników w formie wykresów.

---

## Funkcjonalności aplikacji

### Wczytywanie danych
- import danych pacjentów z pliku CSV
- automatyczne obliczanie BMI
- automatyczne wyznaczanie nadciśnienia na podstawie wartości ciśnienia

### Filtrowanie danych
Możliwość filtrowania pacjentów według:
- płci
- wieku (zakres)
- cukrzycy
- nadciśnienia

### Statystyki
Wyświetlane są podstawowe statystyki:
- liczba pacjentów
- średni wiek
- średnie BMI
- procent pacjentów z cukrzycą

### Wizualizacja danych
Aplikacja zawiera wykresy:

- histogram BMI z podziałem na płeć
- procent pacjentów z nadciśnieniem (wykres kołowy)
- podział cukrzycy: typ 1 / typ 2 / brak
- leczenie cukrzycy (wykres słupkowy)

### Eksport danych
- eksport przefiltrowanych danych do pliku CSV

### Interfejs GUI
Aplikacja posiada graficzny interfejs użytkownika wykonany w bibliotece **Tkinter**.

---

## Technologie

- Python
- Pandas
- Matplotlib
- Tkinter

---

## Uruchomienie programu

1. Zainstaluj wymagane biblioteki:

```bash
pip install pandas matplotlib
