def format_paragraph(words, width):
    lines = []
    current_line = ""

    for word in words:
        if not current_line:
            if len(word) > width:
                lines.append(word)
            else:
                current_line = word
        else:
            if len(current_line) + 1 + len(word) <= width:
                current_line += " " + word
            else:
                lines.append(current_line)
                if len(word) > width:
                    lines.append(word)
                    current_line = ""
                else:
                    current_line = word

    if current_line:
        lines.append(current_line)

    return lines


def format_text_file(input_file, output_file, width):
    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Podział na akapity (puste linie)
    paragraphs = text.split("\n\n")

    formatted_paragraphs = []

    for paragraph in paragraphs:
        lines = paragraph.splitlines()

        # Jeśli akapit pusty
        if not any(lines):
            formatted_paragraphs.append("")
            continue

        words = []
        for line in lines:
            words.extend(line.split(" "))

        formatted_lines = format_paragraph(words, width)
        formatted_paragraphs.append("\n".join(formatted_lines))

    # Połącz akapity pustą linią
    result = "\n\n".join(formatted_paragraphs)

    # Zapis do pliku
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(result)

    # Wyświetlenie w konsoli
    print("\n===== SFORMATOWANY TEKST =====\n")
    print(result)
    print("\n===== KONIEC =====")


# ====== URUCHOMIENIE ======
if __name__ == "__main__":
    input_filename = "gold-bug.txt"
    output_filename = "gold-bug_formatted.txt"
    column_width = 30

    format_text_file(input_filename, output_filename, column_width)
    print("\nFormatowanie zakończone pomyślnie.")
