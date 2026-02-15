import tkinter as tk
from tkinter import filedialog, messagebox
import pandas as pd
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

df = None
canvas = None

# ======================
# WCZYTYWANIE CSV
# ======================
def wczytaj_dane():
    global df

    sciezka = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])

    if not sciezka:
        return

    try:
        df = pd.read_csv(sciezka)
        pokaz(df)
    except Exception as e:
        messagebox.showerror("Błąd", str(e))
