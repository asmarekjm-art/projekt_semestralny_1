import ttkbootstrap as ttkb
from tkinter import ttk
from dane import get_dane
from statystyka import statystyki_opisowe


def create_tab_statystyka(parent, log):

    # =================
    # LAYOUT
    # =================
    frame_table = ttk.Frame(parent)
    frame_table.pack(fill="both", expand=True, padx=10, pady=5)

    tabela = ttk.Treeview(frame_table)
    tabela.pack(fill="both", expand=True)

    # =================
    # OPIS (SCROLL)
    # =================
    frame_opis = ttk.LabelFrame(parent, text="📊 Opis statystyki")
    frame_opis.pack(fill="x", padx=10, pady=5)

    canvas = ttkb.Canvas(frame_opis, height=150)
    scroll = ttk.Scrollbar(frame_opis, orient="vertical", command=canvas.yview)

    inner = ttk.Frame(canvas)

    inner.bind(
        "<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
    )

    canvas.create_window((0, 0), window=inner, anchor="nw")
    canvas.configure(yscrollcommand=scroll.set)

    canvas.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    label_opis = ttk.Label(inner, text="", justify="left", wraplength=1200)
    label_opis.pack(anchor="nw", padx=5, pady=5)

    # =================
    # OPIS TEKST
    # =================
    opis_stat = """
count – liczba obserwacji  
mean – średnia  
std – odchylenie standardowe  
min/max – zakres  
25/50/75% – kwartyle  

Interpretacja:
• niskie std → dane stabilne  
• wysokie std → duża zmienność  
• mean ≠ median → możliwe outliery  
"""

    # =================
    # FUNKCJA WYSWIETLANIA
    # =================
    def pokaz_statystyki():

        df = get_dane()

        if df is None or df.empty:
            log("Brak danych do statystyki", "WARNING")
            return

        try:
            stats = statystyki_opisowe(df)

            if stats is None or stats.empty:
                stats = df.select_dtypes(include="number").describe()

        except Exception as e:
            log(f"Błąd statystyki: {e}", "ERROR")
            stats = df.select_dtypes(include="number").describe()

        # czyszczenie
        tabela.delete(*tabela.get_children())
        tabela["columns"] = [""] + list(stats.columns)
        tabela["show"] = "headings"

        for col in tabela["columns"]:
            tabela.heading(col, text=col)
            tabela.column(col, width=120, anchor="center")

        for i, row in stats.iterrows():
            tabela.insert("", "end", values=[i] + list(row))

        label_opis.config(text=opis_stat)

        log("Statystyki wyświetlone")

    # =================
    # PRZYCISK
    # =================
    ttk.Button(parent, text="Odśwież statystyki", command=pokaz_statystyki)\
        .pack(pady=5)