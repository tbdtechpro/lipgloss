"""
list.py — grocery list with custom enumerator, ported from examples/list/grocery/main.go

Run with:  python examples/list.py
"""

import lipgloss
from lipgloss import list as lst

PURCHASED = {
    "Bananas",
    "Barley",
    "Cashews",
    "Coconut Milk",
    "Dill",
    "Eggs",
    "Fish Cake",
    "Leeks",
    "Papaya",
}

dim = lipgloss.Style().foreground(lipgloss.Color("240"))
bright = lipgloss.Style().foreground(lipgloss.Color("10"))
strikethrough_style = lipgloss.Style().strikethrough(True).foreground(lipgloss.Color("240"))
normal_style = lipgloss.Style().foreground(lipgloss.Color("255"))

ALL_ITEMS = [
    "Artichoke",
    "Baking Flour",
    "Bananas",
    "Barley",
    "Bean Sprouts",
    "Cashew Apple",
    "Cashews",
    "Coconut Milk",
    "Curry Paste",
    "Currywurst",
    "Dill",
    "Dragonfruit",
    "Dried Shrimp",
    "Eggs",
    "Fish Cake",
    "Furikake",
    "Jicama",
    "Kohlrabi",
    "Leeks",
    "Lentils",
    "Licorice Root",
]


def grocery_enumerator(items: lst.Items, i: int) -> str:
    # Match against the original names list by index.
    name = ALL_ITEMS[i] if i < len(ALL_ITEMS) else ""
    if name in PURCHASED:
        return bright.render("✓")
    return dim.render("•")


def main() -> None:
    # Pre-style each item's text (strikethrough for purchased items).
    styled_items = [
        strikethrough_style.render(name) if name in PURCHASED else normal_style.render(name)
        for name in ALL_ITEMS
    ]

    li = lst.List(*styled_items).enumerator(grocery_enumerator)
    print(li.render())


if __name__ == "__main__":
    main()
