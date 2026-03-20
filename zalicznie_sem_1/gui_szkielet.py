from tkinter import ttk


def create_tab_dane(parent):

    # =================
    # TABELA
    # =================
    ramka_tabela = ttk.Frame(parent)
    ramka_tabela.pack(fill="both", expand=True)

    scroll_y = ttk.Scrollbar(ramka_tabela, orient="vertical")
    scroll_x = ttk.Scrollbar(ramka_tabela, orient="horizontal")

    tabela = ttk.Treeview(
        ramka_tabela,
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )

    scroll_y.config(command=tabela.yview)
    scroll_x.config(command=tabela.xview)

    scroll_y.pack(side="right", fill="y")
    scroll_x.pack(side="bottom", fill="x")
    tabela.pack(fill="both", expand=True)

    # =================
    # PODSUMOWANIE
    # =================
    podsumowanie_label = ttk.Label(parent, text="", justify="left")
    podsumowanie_label.pack(fill="x", padx=10, pady=5)

    opis_label = ttk.Label(parent, text="", justify="left", foreground="gray")
    opis_label.pack(fill="x", padx=10, pady=(0, 10))

    # =================
    # FUNKCJE
    # =================
    def pokaz(df):
        tabela["columns"] = ()
        tabela.delete(*tabela.get_children())

        if df is None or df.empty:
            podsumowanie_label.config(text="Brak danych")
            return

        cols = ["ID"] + list(df.columns)
        tabela["columns"] = cols
        tabela["show"] = "headings"

        for col in cols:
            tabela.heading(col, text=col)
            tabela.column(col, width=120, anchor="center")

        for i, row in df.iterrows():
            tabela.insert("", "end", values=[i] + list(row))

    def aktualizuj_podsumowanie(df):
        if df is None or df.empty:
            podsumowanie_label.config(text="Brak danych")
            return

        tekst = f"📦 Pacjenci: {len(df)}"

        if "wiek" in df.columns:
            tekst += f" | 🎂 Śr. wiek: {df['wiek'].mean():.1f}"

        if "bmi" in df.columns:
            tekst += f" | ⚖️ Śr. BMI: {df['bmi'].mean():.2f}"

        podsumowanie_label.config(text=tekst)

    def generuj_opis(df):
        if df is None or df.empty:
            return "Brak danych do analizy"

        tekst = "📊 Wnioski:\n"

        if "bmi" in df.columns and df["bmi"].mean() > 25:
            tekst += "• Średnie BMI powyżej normy\n"

        return tekst

    # 👉 ZWRACAMY funkcje do użycia w gui.py
    return pokaz, aktualizuj_podsumowanie, generuj_opis

