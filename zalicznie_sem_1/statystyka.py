# =================
# IMPORTY
# =================

import pandas as pd
from dane import get_dane

log = print


# =================
# STATYSTYKI OPISOWE
# =================

def statystyki_opisowe(df=None):
    try:
        if df is None:
            df = get_dane()

        if df is None or df.empty:
            log("Brak danych do statystyk", "ERROR")
            return None

        num = df.select_dtypes(include="number")

        if num.empty:
            log("Brak danych liczbowych", "WARNING")
            return None

        stats = num.describe().round(2)

        log("Statystyki opisowe OK", "SUCCESS")
        return stats

    except Exception as e:
        log(f"Błąd statystyk: {e}", "ERROR")
        return None


# =================
# PASEK STATYSTYK (GUI)
# =================

def pokaz_statystyki(df, label):

    if df is None or df.empty:
        label.config(text="Brak danych")
        return

    try:
        liczba = len(df)

        wiek = "-"
        bmi = "-"
        cuk1 = "-"
        cuk2 = "-"
        nad = "-"

        # wiek
        if "wiek" in df.columns:
            wiek = round(df["wiek"].mean(), 1)

        # BMI (spójność z dane.py!)
        if "bmi" in df.columns:
            bmi = round(df["bmi"].mean(), 1)

        # cukrzyca
        if "cukrzyca_typ" in df.columns:
            total = len(df)

            cuk1 = round((df["cukrzyca_typ"] == "typ_1").sum() / total * 100, 1)
            cuk2 = round((df["cukrzyca_typ"] == "typ_2").sum() / total * 100, 1)

        # nadciśnienie
        if "nadcisnienie" in df.columns:
            nad = round((df["nadcisnienie"] == "tak").mean() * 100, 1)

        tekst = (
            f"Pacjenci: {liczba}   |   "
            f"Śr. wiek: {wiek}   |   "
            f"Śr. BMI: {bmi}   |   "
            f"T1: {cuk1}%   |   "
            f"T2: {cuk2}%   |   "
            f"Nadciśnienie: {nad}%"
        )

        label.config(text=tekst)

        log("Statystyki GUI OK", "INFO")

    except Exception as e:
        label.config(text="Błąd statystyk")
        log(f"Błąd statystyk: {e}", "ERROR")


# =================
# STATYSTYKI ROZSZERZONE
# =================

def statystyki_rozszerzone(df=None):
    try:
        if df is None:
            df = get_dane()

        if df is None or df.empty:
            log("Brak danych", "ERROR")
            return {}

        wyniki = {}

        if "wiek" in df.columns:
            wyniki["sredni_wiek"] = round(df["wiek"].mean(), 1)
            wyniki["mediana_wieku"] = round(df["wiek"].median(), 1)

        if "bmi" in df.columns:
            wyniki["srednie_bmi"] = round(df["bmi"].mean(), 1)
            wyniki["max_bmi"] = round(df["bmi"].max(), 1)
            wyniki["min_bmi"] = round(df["bmi"].min(), 1)

        if "cukrzyca_typ" in df.columns:
            total = len(df)
            wyniki["cukrzyca_typ1_%"] = round((df["cukrzyca_typ"] == "typ_1").sum() / total * 100, 1)
            wyniki["cukrzyca_typ2_%"] = round((df["cukrzyca_typ"] == "typ_2").sum() / total * 100, 1)

        if "nadcisnienie" in df.columns:
            wyniki["nadcisnienie_%"] = round((df["nadcisnienie"] == "tak").mean() * 100, 1)

        wyniki["liczba_pacjentow"] = len(df)

        log("Statystyki rozszerzone OK", "SUCCESS")
        return wyniki

    except Exception as e:
        log(f"Błąd statystyk rozszerzonych: {e}", "ERROR")
        return {}


# =================
# TEKST DO RAPORTU
# =================

def generuj_tekst_raportu(df=None):
    try:
        stats = statystyki_rozszerzone(df)

        if not stats:
            return "Brak danych do raportu"

        tekst = (
            f"Liczba pacjentów: {stats.get('liczba_pacjentow','-')}\n"
            f"Średni wiek: {stats.get('sredni_wiek','-')}\n"
            f"Mediana wieku: {stats.get('mediana_wieku','-')}\n"
            f"Średnie BMI: {stats.get('srednie_bmi','-')}\n"
            f"Min BMI: {stats.get('min_bmi','-')}\n"
            f"Max BMI: {stats.get('max_bmi','-')}\n"
            f"Cukrzyca typ 1: {stats.get('cukrzyca_typ1_%','-')}%\n"
            f"Cukrzyca typ 2: {stats.get('cukrzyca_typ2_%','-')}%\n"
            f"Nadciśnienie: {stats.get('nadcisnienie_%','-')}%\n"
        )

        log("Raport OK", "SUCCESS")
        return tekst

    except Exception as e:
        log(f"Błąd raportu: {e}", "ERROR")
        return "Błąd generowania raportu"


# =================
# TEST STATYSTYCZNY
# =================

def rysuj_test(*args, **kwargs):
    log("Test statystyczny jeszcze niezaimplementowany", "WARNING")