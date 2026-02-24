"""
table.py — language greeting table, ported from examples/table/languages/main.go

Run with:  python examples/table.py
"""

import lipgloss
from lipgloss import table

PURPLE = lipgloss.Color("99")
GRAY = lipgloss.Color("245")
LIGHT_GRAY = lipgloss.Color("241")

ROWS = [
    ["Chinese", "您好", "你好"],
    ["Japanese", "こんにちは", "やあ"],
    ["Arabic", "أهلين", "أهلا"],
    ["Russian", "Здравствуйте", "Привет"],
    ["Spanish", "Hola", "¿Qué tal?"],
    ["English", "You look absolutely fabulous.", "How's it going?"],
]

header_style = lipgloss.Style().foreground(PURPLE).bold(True).align(lipgloss.Center)
cell_style = lipgloss.Style().padding(0, 1).width(14)
odd_row_style = cell_style.foreground(GRAY)
even_row_style = cell_style.foreground(LIGHT_GRAY)
border_style = lipgloss.Style().foreground(PURPLE)


def style_func(row: int, col: int) -> lipgloss.Style:
    if row == table.HeaderRow:
        return header_style

    style = even_row_style if row % 2 == 0 else odd_row_style

    # Make the second column (Formal) a little wider.
    if col == 1:
        style = style.width(22)

    # Arabic is right-to-left, so right-align those cells.
    if row < len(ROWS) and ROWS[row][0] == "Arabic" and col != 0:
        style = style.align(lipgloss.Right)

    return style


def main() -> None:
    t = (
        table.Table()
        .border(lipgloss.thick_border())
        .border_style(border_style)
        .style_func(style_func)
        .headers("LANGUAGE", "FORMAL", "INFORMAL")
        .rows(*ROWS)
    )
    print(t.render())


if __name__ == "__main__":
    main()
