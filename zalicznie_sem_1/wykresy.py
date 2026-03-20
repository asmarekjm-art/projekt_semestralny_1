# =================
# IMPORTY
# =================

from matplotlib.figure import Figure
from dane import get_dane


# =================
# LOG (nadpisywany z gui)
# =================

def log(msg, level="INFO"):
    print(f"[{level}] {msg}")


# =================
# WYKRES BMI
# =================

def wykres_bmi():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych — najpierw wczytaj bazę", "WARNING")
        return None

    # normalizacja nazw kolumn
    cols = {c.lower(): c for c in dane.columns}

    if "bmi" not in cols:
        log(f"Brak kolumny BMI. Dostępne: {list(dane.columns)}", "ERROR")
        return None

    plec_key = None
    for key in ["plec", "płeć", "gender"]:
        if key in cols:
            plec_key = cols[key]
            break

    if plec_key is None:
        log(f"Brak kolumny płeć. Dostępne: {list(dane.columns)}", "ERROR")
        return None

    col_bmi = cols["bmi"]
    col_plec = plec_key

    # 🔥 normalizacja wartości
    dane[col_plec] = dane[col_plec].astype(str).str.upper().str.strip()

    kobiety = dane[dane[col_plec] == "K"][col_bmi].dropna()
    mezczyzni = dane[dane[col_plec] == "M"][col_bmi].dropna()

    if kobiety.empty and mezczyzni.empty:
        log("Brak danych BMI po filtracji", "WARNING")
        return None

    fig = Figure(figsize=(8, 4))

    ax1 = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    if not kobiety.empty:
        ax1.hist(kobiety, bins=15, color="pink", alpha=0.7)
    ax1.axvline(18.5, linestyle="--", color="red")
    ax1.axvline(25, linestyle="--", color="green")
    ax1.set_title("Kobiety")
    ax1.set_xlabel("BMI")
    ax1.set_ylabel("Liczba pacjentów")
    ax1.set_xlim(15, 45)
    ax1.grid(alpha=0.3)

    if not mezczyzni.empty:
        ax2.hist(mezczyzni, bins=15, color="lightblue", alpha=0.7)
    ax2.axvline(18.5, linestyle="--", color="red")
    ax2.axvline(25, linestyle="--", color="green")
    ax2.set_title("Mężczyźni")
    ax2.set_xlabel("BMI")
    ax2.set_xlim(15, 45)
    ax2.grid(alpha=0.3)

    fig.suptitle("Rozkład BMI według płci")

    log("Wykres BMI wygenerowany")

    return fig


# =================
# NADCIŚNIENIE
# =================

def wykres_nadcisnienie_kolowy():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych do wykresu nadciśnienia", "ERROR")
        return None

    if "nadcisnienie" not in dane.columns:
        log("Brak kolumny nadcisnienie", "ERROR")
        return None

    nad = dane["nadcisnienie"].astype(str).str.lower().str.strip()

    values = [
        nad.isin(["tak", "1", "true", "yes"]).sum(),
        nad.isin(["nie", "0", "false", "no"]).sum()
    ]

    if sum(values) == 0:
        log("Brak danych do wykresu nadciśnienia", "ERROR")
        return None

    labels = ["Nadciśnienie", "Brak nadciśnienia"]

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(values, labels=labels, autopct="%1.1f%%", colors=["red", "green"], startangle=90)
    ax.set_title(f"Nadciśnienie w populacji (N={len(dane)})")

    log("Generowanie wykresu nadciśnienia")

    return fig


# =================
# CUKRZYCA
# =================

def wykres_cukrzyca_typ_kolowy():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych do wykresu cukrzycy", "ERROR")
        return None

    if not {"cukrzyca", "typ_cukrzycy"}.issubset(dane.columns):
        log("Brak kolumn cukrzyca lub typ_cukrzycy", "ERROR")
        return None

    cuk = dane["cukrzyca"].astype(str).str.lower().str.strip()
    typ = dane["typ_cukrzycy"].astype(str).str.lower().str.strip()

    brak = (cuk == "nie").sum()
    typ1 = (typ == "typ 1").sum()
    typ2 = (typ == "typ 2").sum()

    values = [brak, typ1, typ2]

    if sum(values) == 0:
        log("Brak danych do wykresu cukrzycy", "ERROR")
        return None

    labels = ["Brak cukrzycy", "Typ 1", "Typ 2"]

    fig = Figure(figsize=(5, 4))
    ax = fig.add_subplot(111)

    ax.pie(values, labels=labels, autopct="%1.1f%%",
           colors=["green", "orange", "red"], startangle=90)

    ax.set_title(f"Cukrzyca w populacji (N={len(dane)})")

    log("Generowanie wykresu cukrzycy")

    return fig


# =================
# LEKI NA CUKRZYCĘ
# =================

def wykres_leki_cukrzyca():

    dane = get_dane()

    if dane is None or dane.empty:
        log("Brak danych do wykresu leków", "ERROR")
        return None

    if not {"leki_na_cukrzyce", "cukrzyca"}.issubset(dane.columns):
        log("Brak kolumn leki_na_cukrzyce lub cukrzyca", "ERROR")
        return None

    cuk = dane["cukrzyca"].astype(str).str.lower().str.strip()
    dane_cukrzyca = dane[cuk == "tak"].copy()

    if dane_cukrzyca.empty:
        log("Brak pacjentów z cukrzycą")
        return None

    dane_cukrzyca["leki_na_cukrzyce"] = (
        dane_cukrzyca["leki_na_cukrzyce"]
        .fillna("brak leków")
        .replace("", "brak leków")
    )

    counts = dane_cukrzyca["leki_na_cukrzyce"].value_counts()

    fig = Figure(figsize=(6, 4))
    ax = fig.add_subplot(111)

    x = range(len(counts))

    ax.bar(x, counts.values, color="purple", alpha=0.7)
    ax.set_xticks(x)
    ax.set_xticklabels(counts.index, rotation=30, ha="right")

    ax.set_ylabel("Liczba pacjentów")
    ax.set_title(f"Leczenie cukrzycy (N={len(dane_cukrzyca)})")
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()

    log("Generowanie wykresu leczenia cukrzycy")

    return fig