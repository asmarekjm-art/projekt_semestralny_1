# =================
# IMPORTY
# =================
import pandas as pd
from tkinter import filedialog

pd.options.mode.chained_assignment = None

# =================
# GLOBALNE
# =================
df = pd.DataFrame()
df_filtered = None


# =================
# LOG
# =================
def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# GET DATA
# =================
def get_dane():
    return df_filtered if df_filtered is not None else df


# =================
# HELPER
# =================
def safe_float(val):
    try:
        return float(val)
    except:
        return None


# =================
# NADCIŚNIENIE
# =================
def nadcisnienie(val):
    if not isinstance(val, str):
        return "nie"

    try:
        s, d = val.split("/")
        s, d = int(s), int(d)
        return "tak" if s >= 140 or d >= 90 else "nie"
    except:
        return "nie"


# =================
# WCZYTYWANIE
# =================
def wczytaj_dane(pokaz, pokaz_stat):

    global df, df_filtered

    path = filedialog.askopenfilename(filetypes=[("CSV", "*.csv")])

    if not path:
        log("Nie wybrano pliku")
        return

    try:
        df = pd.read_csv(path, sep=None, engine="python")
        df_filtered = None

        # 🔥 lepsze typy danych
        df = df.convert_dtypes()

        # ujednolicenie kolumn
        df.columns = df.columns.str.lower()

        # 🔥 opcjonalnie: sortowanie kolumn
        df = df.reindex(sorted(df.columns), axis=1)

        log(f"Wczytano {len(df)} rekordów")
        log(f"Kolumny: {list(df.columns)}")

        # =================
        # KONWERSJE
        # =================
        for col in ["wiek", "waga", "wzrost"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # BMI
        if {"waga", "wzrost"}.issubset(df.columns):
            df["bmi"] = df["waga"] / ((df["wzrost"] / 100) ** 2)

        # nadciśnienie
        if "cisnienie" in df.columns:
            df["nadcisnienie"] = df["cisnienie"].apply(nadcisnienie)

        # cukrzyca
        if "cukrzyca_typ" in df.columns:
            df["cukrzyca_typ"] = (
                df["cukrzyca_typ"]
                .astype(str)
                .str.lower()
                .str.replace(" ", "_")
            )

        pokaz(df)
        pokaz_stat(df)

        log("Dane wczytane OK")
        log("Dane gotowe do analizy i wizualizacji 📊")

    except Exception as e:
        log("Błąd wczytywania", "ERROR")
        log(str(e), "ERROR")


# =================
# FILTROWANIE
# =================
def filtruj_dane(
    var_k, var_m,
    var_cuk_typ1, var_cuk_typ2, var_cuk_brak,
    var_nad_tak, var_nad_nie,
    entry_min, entry_max,
    pokaz,
    callback_stat,
    entry_bmi_min=None, entry_bmi_max=None
):
    global df_filtered

    dane = get_dane().copy()

    if dane is None or dane.empty:
        log("Brak danych")
        return

    # =================
    # WIEK
    # =================
    if "wiek" in dane.columns:
        min_wiek = safe_float(entry_min.get())
        max_wiek = safe_float(entry_max.get())

        if min_wiek is not None:
            dane = dane[dane["wiek"] >= min_wiek]

        if max_wiek is not None:
            dane = dane[dane["wiek"] <= max_wiek]

    # =================
    # BMI
    # =================
    if "bmi" in dane.columns:
        try:
            min_bmi = safe_float(entry_bmi_min.get()) if entry_bmi_min else None
            max_bmi = safe_float(entry_bmi_max.get()) if entry_bmi_max else None

            if min_bmi is not None:
                dane = dane[dane["bmi"] >= min_bmi]

            if max_bmi is not None:
                dane = dane[dane["bmi"] <= max_bmi]

        except:
            log("Błąd filtrowania BMI", "ERROR")

    # =================
    # PŁEĆ
    # =================
    if "plec" in dane.columns:
        plec = []
        if var_k.get():
            plec.append("K")
        if var_m.get():
            plec.append("M")

        if plec:
            dane = dane[dane["plec"].isin(plec)]

    # =================
    # CUKRZYCA
    # =================
    if "cukrzyca_typ" in dane.columns:
        typy = []

        if var_cuk_typ1.get():
            typy.append("typ_1")

        if var_cuk_typ2.get():
            typy.append("typ_2")

        if var_cuk_brak.get():
            typy.append("brak")

        if typy:
            dane = dane[dane["cukrzyca_typ"].isin(typy)]

    # =================
    # NADCIŚNIENIE
    # =================
    if "nadcisnienie" in dane.columns:
        nad = []

        if var_nad_tak.get():
            nad.append("tak")

        if var_nad_nie.get():
            nad.append("nie")

        if nad:
            dane = dane[dane["nadcisnienie"].isin(nad)]

    df_filtered = dane

    log(f"Filtrowanie -> {len(dane)} rekordów")

    pokaz(dane)
    callback_stat(dane)


# =================
# WYSZUKIWANIE
# =================
def wyszukaj(search_entry, pokaz):

    dane = get_dane()

    if dane is None or dane.empty:
        return

    tekst = search_entry.get().strip().lower()

    if not tekst or tekst == "szukaj...":
        pokaz(dane)
        return

    mask = dane.astype(str).apply(
        lambda col: col.str.lower().str.contains(tekst, na=False)
    ).any(axis=1)

    wynik = dane[mask]

    log(f"Szukaj -> {len(wynik)}")

    pokaz(wynik)


# =================
# RESET
# =================
def reset_filtry(
    var_k, var_m,
    var_cuk_typ1, var_cuk_typ2, var_cuk_brak,
    var_nad_tak, var_nad_nie,
    entry_min, entry_max,
    pokaz,
    pokaz_stat,
    entry_bmi_min, entry_bmi_max   # 🔥 NOWE
):
    global df_filtered

    # checkboxy
    var_k.set(True)
    var_m.set(True)

    var_cuk_typ1.set(True)
    var_cuk_typ2.set(True)
    var_cuk_brak.set(True)

    var_nad_tak.set(True)
    var_nad_nie.set(True)

    # zakres wieku
    entry_min.delete(0, "end")
    entry_max.delete(0, "end")

    # 🔥 zakres BMI
    entry_bmi_min.delete(0, "end")
    entry_bmi_max.delete(0, "end")

    df_filtered = None

    if not df.empty:
        pokaz(df)
        pokaz_stat(df)

        log("Reset filtrów OK")