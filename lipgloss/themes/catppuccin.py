"""
Catppuccin Mocha theme.

Palette source: https://github.com/catppuccin/catppuccin
"""

from dataclasses import dataclass

from lipgloss.color import Color


@dataclass(frozen=True)
class CatppuccinMochaTheme:
    """Catppuccin Mocha — a dark, warm, pastel color scheme.

    Attributes correspond directly to the official Catppuccin Mocha palette
    names. Background colors run from darkest (``crust``) to lightest
    (``surface2``); text colors from dimmest (``subtext0``) to brightest
    (``text``).
    """

    # ------------------------------------------------------------------ #
    # Background / surface ramp                                           #
    # ------------------------------------------------------------------ #
    crust: Color = Color("#11111b")
    mantle: Color = Color("#181825")
    base: Color = Color("#1e1e2e")
    surface0: Color = Color("#313244")
    surface1: Color = Color("#45475a")
    surface2: Color = Color("#585b70")

    # ------------------------------------------------------------------ #
    # Overlay / muted text                                                #
    # ------------------------------------------------------------------ #
    overlay0: Color = Color("#6c7086")
    overlay1: Color = Color("#7f849c")
    overlay2: Color = Color("#9399b2")

    # ------------------------------------------------------------------ #
    # Text ramp                                                           #
    # ------------------------------------------------------------------ #
    subtext0: Color = Color("#a6adc8")
    subtext1: Color = Color("#bac2de")
    text: Color = Color("#cdd6f4")

    # ------------------------------------------------------------------ #
    # Accent colors                                                       #
    # ------------------------------------------------------------------ #
    lavender: Color = Color("#b4befe")
    blue: Color = Color("#89b4fa")
    sapphire: Color = Color("#74c7ec")
    sky: Color = Color("#89dceb")
    teal: Color = Color("#94e2d5")
    green: Color = Color("#a6e3a1")
    yellow: Color = Color("#f9e2af")
    peach: Color = Color("#fab387")
    maroon: Color = Color("#eba0ac")
    red: Color = Color("#f38ba8")
    mauve: Color = Color("#cba6f7")
    pink: Color = Color("#f5c2e7")
    flamingo: Color = Color("#f2cdcd")
    rosewater: Color = Color("#f5e0dc")


#: Shared singleton — import and use directly.
catppuccin_mocha = CatppuccinMochaTheme()
