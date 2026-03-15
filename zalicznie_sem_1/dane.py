# =================
# IMPORTY
# =================

import pandas as pd
from tkinter import filedialog

pd.options.mode.chained_assignment = None


# =================
# ZMIENNE GLOBALNE
# =================

df = pd.DataFrame()
df_filtered = None


# =================
# LOG (nadpisywany z gui)
# =================

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# POBIERANIE DANYCH
# =================

def get_dane():
    """Zwraca dane po filtrach lub pełną bazę."""
    return df_filtered if df_filtered is not None else df


# =================
# ANALIZA CIŚNIENIA
# =================

def nadcisnienie(val):

    if not isinstance(val, str):
        return "nie"

    try:

        s, d = val.split("/")
        s = int(s)
        d = int(d)

        if s >= 140 or d >= 90:
            return "tak"

        return "nie"

    except Exception:
        return "nie"


# =================
# WCZYTYWANIE CSV
# =================

def wczytaj_dane(pokaz, pokaz_statystyki):

    global df, df_filtered

    log("Otwieranie okna wyboru pliku")

    path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )

    if not path:
        log("Nie wybrano pliku")
        return

    log(f"Wybrany plik: {path}")

    try:

        df = pd.read_csv(
            path,
            sep=None,
            engine="python"
        )

        df_filtered = None

        log(f"Wczytano {len(df)} rekordów")
        log(f"Kolumny: {list(df.columns)}")

        # =================
        # KONWERSJA LICZB
        # =================

        for col in ["wiek", "waga", "wzrost"]:

            if col in df.columns:

                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

        # =================
        # BMI
        # =================

        if {"waga", "wzrost"}.issubset(df.columns):

            log("Obliczanie BMI")

            df["BMI"] = df["waga"] / ((df["wzrost"] / 100) ** 2)

            df["BMI"] = df["BMI"].replace(
                [float("inf"), -float("inf")],
                None
            )

            log("Kolumna BMI została dodana")

        else:

            log("Brak kolumn waga/wzrost — BMI pominięte")

        # =================
        # NADCIŚNIENIE
        # =================

        if "cisnienie" in df.columns:

            log("Analiza nadciśnienia")

            df["nadcisnienie"] = df["cisnienie"].apply(nadcisnienie)

            log("Kolumna nadcisnienie została dodana")

        else:

            log("Brak kolumny cisnienie")

        pokaz(df)
        pokaz_statystyki(df)

        log("Dane zostały wyświetlone")

    except Exception as e:

        log("Błąd wczytywania danych", "ERROR")
        log(str(e), "ERROR")


# =================
# SORTOWANIE
# =================

def sortuj_kolumne(col, reverse, pokaz):

    global df_filtered

    dane = get_dane()

    if dane is None or dane.empty:
        log("Sortowanie przerwane – brak danych")
        return

    log(f"Sortowanie kolumny: {col}")

    try:

        dane = dane.sort_values(
            by=col,
            ascending=not reverse
        )

    except Exception:

        log("Sortowanie jako tekst")

        dane = dane.sort_values(
            by=col,
            ascending=not reverse,
            key=lambda x: x.astype(str)
        )

    df_filtered = dane

    log("Sortowanie zakończone")

    pokaz(dane)


# =================
# FILTROWANIE
# =================

def filtruj_dane(
    var_k,
    var_m,
    var_cuk_tak,
    var_cuk_nie,
    var_nad_tak,
    var_nad_nie,
    entry_min,
    entry_max,
    pokaz,
    pokaz_statystyki
):

    global df_filtered

    if df.empty:
        log("Filtrowanie przerwane – brak danych")
        return

    log("Rozpoczęcie filtrowania")

    dane = df.copy()

    # =================
    # FILTR PŁCI
    # =================

    plec = []

    if var_k.get():
        plec.append("K")

    if var_m.get():
        plec.append("M")

    if plec and "plec" in dane.columns:

        dane = dane[dane["plec"].isin(plec)]

        log(f"Filtr płci: {plec}")

    # =================
    # FILTR WIEKU
    # =================

    if "wiek" in dane.columns:

        try:

            min_wiek = entry_min.get().strip()
            max_wiek = entry_max.get().strip()

            if min_wiek:
                dane = dane[dane["wiek"] >= int(min_wiek)]
                log(f"Wiek od: {min_wiek}")

            if max_wiek:
                dane = dane[dane["wiek"] <= int(max_wiek)]
                log(f"Wiek do: {max_wiek}")

        except ValueError:

            log("Błąd – wiek musi być liczbą", "ERROR")
            return

    # =================
    # FILTR CUKRZYCY
    # =================

    cuk = []

    if var_cuk_tak.get():
        cuk.append("tak")

    if var_cuk_nie.get():
        cuk.append("nie")

    if cuk and "cukrzyca" in dane.columns:

        dane = dane[dane["cukrzyca"].isin(cuk)]

        log(f"Filtr cukrzycy: {cuk}")

    # =================
    # FILTR NADCIŚNIENIA
    # =================

    nad = []

    if var_nad_tak.get():
        nad.append("tak")

    if var_nad_nie.get():
        nad.append("nie")

    if nad and "nadcisnienie" in dane.columns:

        dane = dane[dane["nadcisnienie"].isin(nad)]

        log(f"Filtr nadciśnienia: {nad}")

    df_filtered = dane

    log(f"Wynik filtrowania: {len(dane)} rekordów")

    pokaz(dane)
    pokaz_statystyki(dane)


# =================
# WYSZUKIWANIE
# =================

def wyszukaj(search_entry, pokaz):

    dane = get_dane()

    if dane is None or dane.empty:
        log("Wyszukiwanie przerwane – brak danych")
        return

    tekst = search_entry.get().strip().lower()

    if not tekst:
        pokaz(dane)
        return

    log(f"Wyszukiwanie: {tekst}")

    mask = dane.astype(str).apply(
        lambda col: col.str.lower().str.contains(tekst, na=False)
    ).any(axis=1)

    wynik = dane[mask]

    log(f"Znaleziono {len(wynik)} rekordów")

    pokaz(wynik)


# =================
# RESET FILTRÓW
# =================

def reset_filtry(
    var_k, var_m,
    var_cuk_tak, var_cuk_nie,
    var_nad_tak, var_nad_nie,
    entry_min, entry_max,
    pokaz,
    pokaz_stat
):

    global df_filtered

    log("Reset filtrów")

    var_k.set(True)
    var_m.set(True)

    var_cuk_tak.set(True)
    var_cuk_nie.set(True)

    var_nad_tak.set(True)
    var_nad_nie.set(True)

    entry_min.delete(0, "end")
    entry_max.delete(0, "end")

    df_filtered = None

    if not df.empty:

        pokaz(df)
        pokaz_stat(df)

        log("Przywrócono pełny zbiór danych")