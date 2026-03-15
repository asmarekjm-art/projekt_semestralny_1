# =================
# IMPORTY
# =================

import pandas as pd
from tkinter import filedialog, messagebox

pd.options.mode.chained_assignment = None


# =================
# ZMIENNE GLOBALNE
# =================

df = None
df_filtered = None


# =================
# POBRANIE DANYCH
# =================

def get_dane():
    """Zwraca dane po filtrach lub pełną bazę."""
    return df_filtered if df_filtered is not None else df


# =================
# OBLICZANIE NADCIŚNIENIA
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
        else:
            return "nie"

    except Exception:
        return "nie"


# =================
# WCZYTYWANIE CSV
# =================

def wczytaj_dane(pokaz, pokaz_statystyki):

    global df, df_filtered

    path = filedialog.askopenfilename(
        filetypes=[("CSV files", "*.csv")]
    )

    if not path:
        return

    try:

        df = pd.read_csv(path, sep=None, engine="python")
        df_filtered = None

        # =================
        # BMI
        # =================

        if {"waga", "wzrost"}.issubset(df.columns):

            df["BMI"] = df["waga"] / ((df["wzrost"] / 100) ** 2)

            df["BMI"] = df["BMI"].replace(
                [float("inf"), -float("inf")],
                None
            )

        # =================
        # NADCIŚNIENIE
        # =================

        if "cisnienie" in df.columns:

            df["nadcisnienie"] = df["cisnienie"].apply(
                nadcisnienie
            )

        pokaz(df)
        pokaz_statystyki(df)

        log("Dane zostały wczytane")        )

    except Exception as e:

        messagebox.showerror(
            "Błąd",
            str(e)
        )


# =================
# SORTOWANIE
# =================

def sortuj_kolumne(col, reverse, pokaz):

    global df_filtered

    dane = get_dane()

    if dane is None:
        return

    try:

        dane = dane.sort_values(
            by=col,
            ascending=not reverse
        )

    except Exception:

        dane = dane.sort_values(
            by=col,
            ascending=not reverse,
            key=lambda x: x.astype(str)
        )

    df_filtered = dane

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

    if df is None:

        messagebox.showwarning(
            "Brak danych",
            "Najpierw wczytaj plik CSV"
        )
        return

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

    # =================
    # FILTR WIEKU
    # =================

    try:

        if entry_min.get():
            dane = dane[dane["wiek"] >= int(entry_min.get())]

        if entry_max.get():
            dane = dane[dane["wiek"] <= int(entry_max.get())]

    except ValueError:

        messagebox.showwarning(
            "Błąd",
            "Wiek musi być liczbą"
        )
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

    df_filtered = dane

    pokaz(dane)
    pokaz_statystyki(dane)


# =================
# WYSZUKIWANIE
# =================

def wyszukaj(search_entry, pokaz):

    dane = get_dane()

    if dane is None:
        return

    tekst = search_entry.get().lower()

    if not tekst:
        pokaz(dane)
        return

    mask = dane.apply(
        lambda col: col.astype(str)
        .str.lower()
        .str.contains(tekst, na=False)
    ).any(axis=1)

    wynik = dane[mask]

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

    var_k.set(True)
    var_m.set(True)

    var_cuk_tak.set(True)
    var_cuk_nie.set(True)
    var_cuk_nie.set(True)

    var_nad_tak.set(True)
    var_nad_nie.set(True)

    entry_min.delete(0, "end")
    entry_max.delete(0, "end")

    df_filtered = None

    if df is not None:
        pokaz(df)
        pokaz_stat(df)