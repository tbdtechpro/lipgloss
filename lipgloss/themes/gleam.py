"""
Gleam language brand theme.

Palette source: https://gleam.run/branding/
"""

from dataclasses import dataclass

from lipgloss.color import Color


@dataclass(frozen=True)
class GleamTheme:
    """Gleam — the official brand palette of the Gleam programming language.

    Gleam's palette is "all pretty and pink", anchored by Faff Pink
    (``#ffaff3``), the signature color of Lucy the starfish mascot.

    See https://gleam.run/branding/ for the canonical values.
    """

    # ------------------------------------------------------------------ #
    # Brand accents                                                       #
    # ------------------------------------------------------------------ #
    faff_pink: Color = Color("#ffaff3")
    """Primary Gleam brand color — the signature Lucy pink."""

    blue: Color = Color("#a6f0fc")
    """Bright accent blue."""

    aged_plastic_yellow: Color = Color("#fffbe8")
    """Warm off-white / cream accent."""

    # ------------------------------------------------------------------ #
    # Neutrals / backgrounds                                             #
    # ------------------------------------------------------------------ #
    unexpected_aubergine: Color = Color("#584355")
    """Mid-tone purple-grey; useful for muted highlights."""

    underwater_blue: Color = Color("#292d3e")
    """Dark navy background."""

    charcoal: Color = Color("#2f2f2f")
    """Dark grey surface."""

    black: Color = Color("#1e1e1e")
    """Near-black background."""

    blacker: Color = Color("#151515")
    """Deepest background shade."""

    white: Color = Color("#fefefc")
    """Near-white foreground."""


#: Shared singleton — import and use directly.
gleam = GleamTheme()
