# =================
# IMPORTY
# =================
from matplotlib.figure import Figure
from dane import get_dane


# =================
# LOG
# =================
def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# HELPER
# =================
def norm_str(series):
    return series.astype(str).str.lower().str.strip()


# =================
# BMI
# =================
def wykres_bmi():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych", "WARNING")
        return None

    dane = dane.copy()

    cols = {c.lower(): c for c in dane.columns}

    if "bmi" not in cols:
        log("Brak kolumny BMI", "ERROR")
        return None

    plec_key = None
    for key in ["plec", "płeć", "gender"]:
        if key in cols:
            plec_key = cols[key]
            break

    if plec_key is None:
        log("Brak kolumny płeć", "ERROR")
        return None

    col_bmi = cols["bmi"]
    col_plec = plec_key

    dane[col_plec] = dane[col_plec].astype(str).str.upper().str.strip()

    kobiety = dane[dane[col_plec] == "K"][col_bmi].dropna()
    mezczyzni = dane[dane[col_plec] == "M"][col_bmi].dropna()

    if kobiety.empty and mezczyzni.empty:
        log("Brak danych BMI", "WARNING")
        return None

    fig = Figure(figsize=(8, 4))
    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    if not kobiety.empty:
        ax1.hist(kobiety, bins=15)
    ax1.set_title("Kobiety")
    ax1.set_xlabel("BMI")
    ax1.set_ylabel("Liczba")

    if not mezczyzni.empty:
        ax2.hist(mezczyzni, bins=15)
    ax2.set_title("Mężczyźni")
    ax2.set_xlabel("BMI")

    fig.suptitle("Rozkład BMI według płci")

    return fig


# =================
# NADCIŚNIENIE
# =================
def wykres_nadcisnienie_kolowy():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych", "ERROR")
        return None

    if "nadcisnienie" not in dane.columns:
        log("Brak kolumny nadcisnienie", "ERROR")
        return None

    nad = norm_str(dane["nadcisnienie"])

    values = [
        nad.isin(["tak", "1", "true"]).sum(),
        nad.isin(["nie", "0", "false"]).sum()
    ]

    if sum(values) == 0:
        log("Brak danych do wykresu", "ERROR")
        return None

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(values, labels=["Tak", "Nie"], autopct="%1.1f%%", startangle=90)
    ax.set_title(f"Nadciśnienie (N={len(dane)})")

    return fig


# =================
# CUKRZYCA (FIX 🔥)
# =================
def wykres_cukrzyca_typ_kolowy():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych", "ERROR")
        return None

    if "cukrzyca_typ" not in dane.columns:
        log("Brak kolumny cukrzyca_typ", "ERROR")
        return None

    typ = norm_str(dane["cukrzyca_typ"])

    values = [
        (typ == "brak").sum(),
        (typ == "typ_1").sum(),
        (typ == "typ_2").sum()
    ]

    if sum(values) == 0:
        log("Brak danych", "ERROR")
        return None

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(values,
           labels=["Brak", "Typ 1", "Typ 2"],
           autopct="%1.1f%%",
           startangle=90)

    ax.set_title(f"Cukrzyca (N={len(dane)})")

    return fig


# =================
# LEKI
# =================
def wykres_leki_cukrzyca():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych", "ERROR")
        return None

    if not {"leki_na_cukrzyce", "cukrzyca_typ"}.issubset(dane.columns):
        log("Brak kolumn", "ERROR")
        return None

    dane = dane.copy()

    dane = dane[norm_str(dane["cukrzyca_typ"]) != "brak"]

    if dane.empty:
        log("Brak pacjentów z cukrzycą")
        return None

    dane["leki_na_cukrzyce"] = (
        dane["leki_na_cukrzyce"]
        .fillna("brak")
        .replace("", "brak")
    )

    counts = dane["leki_na_cukrzyce"].value_counts()

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    ax.bar(range(len(counts)), counts.values)
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.index, rotation=30)

    ax.set_title("Leczenie cukrzycy")
    ax.set_ylabel("Liczba")

    return fig