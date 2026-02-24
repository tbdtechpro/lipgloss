"""
layout.py — multi-column layout showcase using join, place, and borders.

A simplified port of examples/layout/main.go (omitting dependencies on
go-colorful / gamut that have no direct Python equivalent).

Run with:  python examples/layout.py
"""

import lipgloss

# ── Constants ─────────────────────────────────────────────────────────────────

WIDTH = 96
COLUMN_WIDTH = 30

# ── Color tokens ──────────────────────────────────────────────────────────────

highlight = lipgloss.AdaptiveColor(light="#874BFD", dark="#7D56F4")
special = lipgloss.AdaptiveColor(light="#43BF6D", dark="#73F59F")
subtle = lipgloss.AdaptiveColor(light="#D9DCCF", dark="#383838")

# ── Base styles ───────────────────────────────────────────────────────────────

base = lipgloss.Style().foreground(lipgloss.Color("#EEEEEE"))

divider = lipgloss.Style().set_string("•").padding(0, 1).foreground(subtle).render()

# ── Tab styles ────────────────────────────────────────────────────────────────

from lipgloss.borders import Border  # noqa: E402

active_tab_border = Border(
    top="─",
    bottom=" ",
    left="│",
    right="│",
    top_left="╭",
    top_right="╮",
    bottom_left="┘",
    bottom_right="└",
)

tab_border = Border(
    top="─",
    bottom="─",
    left="│",
    right="│",
    top_left="╭",
    top_right="╮",
    bottom_left="┴",
    bottom_right="┴",
)

tab_style = lipgloss.Style().border_style(tab_border).border_foreground(highlight).padding(0, 1)

active_tab_style = tab_style.border_style(active_tab_border)

tab_gap_style = tab_style.border_top(False).border_left(False).border_right(False)

# ── Title styles ──────────────────────────────────────────────────────────────

title_style = (
    lipgloss.Style()
    .margin_left(1)
    .margin_right(5)
    .padding(0, 1)
    .italic(True)
    .foreground(lipgloss.Color("#FFF7DB"))
)

desc_style = base.margin_top(1)

info_style = base.border_style(lipgloss.normal_border()).border_top(True).border_foreground(subtle)

# ── Dialog styles ─────────────────────────────────────────────────────────────

dialog_box_style = (
    lipgloss.Style()
    .border(lipgloss.rounded_border())
    .border_foreground(lipgloss.Color("#874BFD"))
    .padding(1, 0)
)

button_style = (
    lipgloss.Style()
    .foreground(lipgloss.Color("#FFF7DB"))
    .background(lipgloss.Color("#888B7E"))
    .padding(0, 3)
    .margin_top(1)
)

active_button_style = (
    button_style.foreground(lipgloss.Color("#FFF7DB"))
    .background(lipgloss.Color("#F25D94"))
    .margin_right(2)
    .underline(True)
)

# ── List styles ───────────────────────────────────────────────────────────────

list_style = (
    lipgloss.Style()
    .border(lipgloss.normal_border(), False, True, False, False)
    .border_foreground(subtle)
    .margin_right(2)
    .height(8)
    .width(COLUMN_WIDTH + 1)
)

list_header = (
    base.border_style(lipgloss.normal_border())
    .border_bottom(True)
    .border_foreground(subtle)
    .margin_right(2)
    .render
)

list_item = base.padding_left(2).render

check_mark = lipgloss.Style().set_string("✓").foreground(special).padding_right(1).render()


def list_done(s: str) -> str:
    return check_mark + (
        lipgloss.Style()
        .strikethrough(True)
        .foreground(lipgloss.AdaptiveColor(light="#969B86", dark="#696969"))
        .render(s)
    )


# ── Status bar styles ─────────────────────────────────────────────────────────

status_nugget = lipgloss.Style().foreground(lipgloss.Color("#FFFDF5")).padding(0, 1)

status_bar_style = (
    lipgloss.Style()
    .foreground(lipgloss.AdaptiveColor(light="#343433", dark="#C1C6B2"))
    .background(lipgloss.AdaptiveColor(light="#D9DCCF", dark="#353533"))
)

status_style = (
    lipgloss.Style()
    .inherit(status_bar_style)
    .foreground(lipgloss.Color("#FFFDF5"))
    .background(lipgloss.Color("#FF5F87"))
    .padding(0, 1)
    .margin_right(1)
)

encoding_style = status_nugget.background(lipgloss.Color("#A550DF")).align(lipgloss.Right)
status_text = lipgloss.Style().inherit(status_bar_style)
fish_cake_style = status_nugget.background(lipgloss.Color("#6124DF"))

doc_style = lipgloss.Style().padding(1, 2, 1, 2)

# ── History ───────────────────────────────────────────────────────────────────

history_style = (
    lipgloss.Style()
    .align(lipgloss.Left)
    .foreground(lipgloss.Color("#FAFAFA"))
    .background(highlight)
    .margin(1, 3, 0, 0)
    .padding(1, 2)
    .height(7)
    .width(COLUMN_WIDTH)
)

HISTORY_A = (
    "The Romans learned from the Greeks that quinces slowly cooked with honey "
    'would "set" when cool. The Apicius gives a recipe for preserving whole quinces '
    "in a bath of honey diluted with defrutum: Roman marmalade."
)
HISTORY_B = (
    "Medieval quince preserves, which went by the French name cotignac, began to "
    "lose their medieval seasoning of spices in the 16th century. La Varenne provided "
    "recipes for both thick and clear cotignac."
)
HISTORY_C = (
    'In 1524, Henry VIII received a "box of marmalade" from Mr. Hull of Exeter. '
    "This was probably marmelada, a solid quince paste from Portugal, still made "
    "and sold in southern Europe today."
)


# ── Main ──────────────────────────────────────────────────────────────────────


def main() -> None:
    parts: list[str] = []

    # Tabs
    row = lipgloss.join_horizontal(
        lipgloss.Top,
        active_tab_style.render("Lip Gloss"),
        tab_style.render("Blush"),
        tab_style.render("Eye Shadow"),
        tab_style.render("Mascara"),
        tab_style.render("Foundation"),
    )
    gap_width = max(0, WIDTH - lipgloss.width(row) - 2)
    gap = tab_gap_style.render(" " * gap_width)
    row = lipgloss.join_horizontal(lipgloss.Bottom, row, gap)
    parts.append(row + "\n")

    # Title + description
    title = title_style.render("Lip Gloss")
    desc = lipgloss.join_vertical(
        lipgloss.Left,
        desc_style.render("Style Definitions for Nice Terminal Layouts"),
        info_style.render("From Charm" + divider + "https://github.com/charmbracelet/lipgloss"),
    )
    parts.append(lipgloss.join_horizontal(lipgloss.Top, title, desc) + "\n")

    # Dialog
    ok_button = active_button_style.render("Yes")
    cancel_button = button_style.render("Maybe")
    question = (
        lipgloss.Style()
        .width(50)
        .align(lipgloss.Center)
        .render("Are you sure you want to eat marmalade?")
    )
    buttons = lipgloss.join_horizontal(lipgloss.Top, ok_button, cancel_button)
    ui = lipgloss.join_vertical(lipgloss.Center, question, buttons)
    dialog = lipgloss.place(
        WIDTH,
        9,
        lipgloss.Center,
        lipgloss.Center,
        dialog_box_style.render(ui),
        lipgloss.whitespace_chars("猫咪"),
        lipgloss.whitespace_foreground(subtle),
    )
    parts.append(dialog + "\n")

    # Lists
    lists = lipgloss.join_horizontal(
        lipgloss.Top,
        list_style.render(
            lipgloss.join_vertical(
                lipgloss.Left,
                list_header("Citrus Fruits to Try"),
                list_done("Grapefruit"),
                list_done("Yuzu"),
                list_item("Citron"),
                list_item("Kumquat"),
                list_item("Pomelo"),
            )
        ),
        list_style.width(COLUMN_WIDTH).render(
            lipgloss.join_vertical(
                lipgloss.Left,
                list_header("Actual Lip Gloss Vendors"),
                list_item("Glossier"),
                list_item("Claire's Boutique"),
                list_done("Nyx"),
                list_item("Mac"),
                list_done("Milk"),
            )
        ),
    )
    parts.append(lists)

    # History
    history = lipgloss.join_horizontal(
        lipgloss.Top,
        history_style.align(lipgloss.Right).render(HISTORY_A),
        history_style.align(lipgloss.Center).render(HISTORY_B),
        history_style.margin_right(0).render(HISTORY_C),
    )
    parts.append("\n\n" + history + "\n\n")

    # Status bar
    status_key = status_style.render("STATUS")
    encoding = encoding_style.render("UTF-8")
    fish_cake = fish_cake_style.render("🍥 Fish Cake")
    remaining = (
        WIDTH - lipgloss.width(status_key) - lipgloss.width(encoding) - lipgloss.width(fish_cake)
    )
    status_val = status_text.width(remaining).render("Ravishing")
    bar = lipgloss.join_horizontal(lipgloss.Top, status_key, status_val, encoding, fish_cake)
    parts.append(status_bar_style.width(WIDTH).render(bar))

    print(doc_style.render("\n".join(parts)))


if __name__ == "__main__":
    main()
