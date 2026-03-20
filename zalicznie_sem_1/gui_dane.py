from tkinter import ttk
import ttkbootstrap as ttkb

def create_tab_dane(parent):

    # =================
    # TABELA
    # =================
    ramka_tabela = ttk.Frame(parent, padding=5)
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

    # =================
    # OPIS (SCROLL)
    # =================
    ramka_opis = ttk.Frame(parent)
    ramka_opis.pack(fill="x", padx=10, pady=(0, 10))

    canvas_opis = ttkb.Canvas(ramka_opis, height=150)
    scroll_opis = ttk.Scrollbar(ramka_opis, orient="vertical", command=canvas_opis.yview)

    frame_opis_inner = ttk.Frame(canvas_opis)

    frame_opis_inner.bind(
        "<Configure>",
        lambda e: canvas_opis.configure(scrollregion=canvas_opis.bbox("all"))
    )

    canvas_opis.create_window((0, 0), window=frame_opis_inner, anchor="nw")
    canvas_opis.configure(yscrollcommand=scroll_opis.set)

    canvas_opis.pack(side="left", fill="both", expand=True)
    scroll_opis.pack(side="right", fill="y")

    opis_label = ttk.Label(
        frame_opis_inner,
        text="",
        justify="left",
        foreground="gray",
        wraplength=1200  # 👈 żeby ładnie łamało tekst
    )
    opis_label.pack(anchor="nw")

    # =================
    # FUNKCJE
    # =================
    def pokaz(df):
        tabela["columns"] = ()
        tabela.delete(*tabela.get_children())

        if df is None or df.empty:
            podsumowanie_label.config(text="Brak danych")
            opis_label.config(text="")
            return

        cols = ["ID"] + list(df.columns)
        tabela["columns"] = cols
        tabela["show"] = "headings"

        for col in cols:
            tabela.heading(col, text=col)
            tabela.column(col, width=110, anchor="center", stretch=True)

        for i, row in df.iterrows():
            tabela.insert("", "end", values=[i] + list(row))

        # ✅ NOWE:
        aktualizuj_podsumowanie(df)
        ustaw_opis(generuj_opis(df))

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

        if "wiek" in df.columns:
            sredni_wiek = df["wiek"].mean()
            tekst += f"• Średni wiek pacjentów: {sredni_wiek:.1f}\n"

        if "bmi" in df.columns:
            bmi = df["bmi"].mean()
            tekst += f"• Średnie BMI: {bmi:.2f}\n"

            if bmi < 18.5:
                tekst += "• Populacja niedożywiona\n"
            elif bmi < 25:
                tekst += "• BMI w normie\n"
            elif bmi < 30:
                tekst += "• Nadwaga\n"
            else:
                tekst += "• Otyłość\n"

        if "nadcisnienie" in df.columns:
            nad = df["nadcisnienie"].astype(str).str.lower().str.strip()

            proc = (
                           nad.isin(["1", "tak", "true", "yes"]).sum()
                           / len(nad)
                   ) * 100

            tekst += f"• Nadciśnienie: {proc:.1f}% pacjentów\n"

        if "cukrzyca" in df.columns:
            cuk = df["cukrzyca"].value_counts(normalize=True)
            if 2 in cuk:
                tekst += f"• Cukrzyca typu 2: {cuk[2] * 100:.1f}%\n"

        return tekst

    def ustaw_opis(tekst):
        opis_label.config(text=tekst)

    return pokaz, aktualizuj_podsumowanie, generuj_opis, ustaw_opis