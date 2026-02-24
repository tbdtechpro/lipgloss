"""
Built-in color scheme themes for Lip Gloss.

Each theme exposes its palette as typed ``Color`` attributes so they can be
passed directly to ``Style`` methods::

    from lipgloss import Style, themes

    mocha = themes.catppuccin_mocha
    style = Style().foreground(mocha.mauve).background(mocha.base)
    print(style.render("Hello!"))

Available themes
----------------
- :data:`catppuccin_mocha` — Catppuccin Mocha (dark)
- :data:`dracula` — Dracula
- :data:`gleam` — Gleam language brand palette
"""

from .catppuccin import CatppuccinMochaTheme, catppuccin_mocha
from .dracula import DraculaTheme, dracula
from .gleam import GleamTheme, gleam

__all__ = [
    "CatppuccinMochaTheme",
    "catppuccin_mocha",
    "DraculaTheme",
    "dracula",
    "GleamTheme",
    "gleam",
]
