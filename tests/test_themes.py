"""Tests for the built-in color scheme themes."""

from __future__ import annotations

import lipgloss
from lipgloss.color import Color, TerminalColor
from lipgloss.themes import CatppuccinMochaTheme, DraculaTheme, GleamTheme
from lipgloss.themes import catppuccin_mocha, dracula, gleam


# ---------------------------------------------------------------------------
# Module-level access via lipgloss.themes
# ---------------------------------------------------------------------------


def test_themes_accessible_from_top_level() -> None:
    assert hasattr(lipgloss, "themes")


def test_themes_exposes_singletons() -> None:
    assert lipgloss.themes.catppuccin_mocha is catppuccin_mocha
    assert lipgloss.themes.dracula is dracula
    assert lipgloss.themes.gleam is gleam


# ---------------------------------------------------------------------------
# Catppuccin Mocha
# ---------------------------------------------------------------------------


def test_catppuccin_mocha_is_correct_type() -> None:
    assert isinstance(catppuccin_mocha, CatppuccinMochaTheme)


def test_catppuccin_mocha_all_colors_are_Color_instances() -> None:
    import dataclasses

    for field in dataclasses.fields(catppuccin_mocha):
        value = getattr(catppuccin_mocha, field.name)
        assert isinstance(value, Color), f"field {field.name!r} is not a Color"


def test_catppuccin_mocha_all_colors_satisfy_protocol() -> None:
    import dataclasses

    for field in dataclasses.fields(catppuccin_mocha):
        value = getattr(catppuccin_mocha, field.name)
        assert isinstance(value, TerminalColor), f"field {field.name!r} does not satisfy TerminalColor"


def test_catppuccin_mocha_spot_check() -> None:
    assert str(catppuccin_mocha.base) == "#1e1e2e"
    assert str(catppuccin_mocha.mauve) == "#cba6f7"
    assert str(catppuccin_mocha.text) == "#cdd6f4"
    assert str(catppuccin_mocha.crust) == "#11111b"
    assert str(catppuccin_mocha.green) == "#a6e3a1"


def test_catppuccin_mocha_is_frozen() -> None:
    import dataclasses

    assert catppuccin_mocha.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_catppuccin_mocha_usable_in_style() -> None:
    style = lipgloss.Style().foreground(catppuccin_mocha.mauve).background(catppuccin_mocha.base)
    rendered = style.render("hi")
    assert "hi" in rendered


# ---------------------------------------------------------------------------
# Dracula
# ---------------------------------------------------------------------------


def test_dracula_is_correct_type() -> None:
    assert isinstance(dracula, DraculaTheme)


def test_dracula_all_colors_are_Color_instances() -> None:
    import dataclasses

    for field in dataclasses.fields(dracula):
        value = getattr(dracula, field.name)
        assert isinstance(value, Color), f"field {field.name!r} is not a Color"


def test_dracula_spot_check() -> None:
    assert str(dracula.background) == "#282a36"
    assert str(dracula.purple) == "#bd93f9"
    assert str(dracula.foreground) == "#f8f8f2"
    assert str(dracula.pink) == "#ff79c6"
    assert str(dracula.comment) == "#6272a4"


def test_dracula_is_frozen() -> None:
    assert dracula.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_dracula_usable_in_style() -> None:
    style = lipgloss.Style().foreground(dracula.purple).background(dracula.background)
    rendered = style.render("hi")
    assert "hi" in rendered


# ---------------------------------------------------------------------------
# Gleam
# ---------------------------------------------------------------------------


def test_gleam_is_correct_type() -> None:
    assert isinstance(gleam, GleamTheme)


def test_gleam_all_colors_are_Color_instances() -> None:
    import dataclasses

    for field in dataclasses.fields(gleam):
        value = getattr(gleam, field.name)
        assert isinstance(value, Color), f"field {field.name!r} is not a Color"


def test_gleam_spot_check() -> None:
    assert str(gleam.faff_pink) == "#ffaff3"
    assert str(gleam.underwater_blue) == "#292d3e"
    assert str(gleam.white) == "#fefefc"
    assert str(gleam.blue) == "#a6f0fc"


def test_gleam_is_frozen() -> None:
    assert gleam.__dataclass_params__.frozen  # type: ignore[attr-defined]


def test_gleam_usable_in_style() -> None:
    style = lipgloss.Style().foreground(gleam.faff_pink).background(gleam.underwater_blue)
    rendered = style.render("hi")
    assert "hi" in rendered


# ---------------------------------------------------------------------------
# Cross-theme: singletons are immutable and reusable
# ---------------------------------------------------------------------------


def test_singletons_are_identical_on_repeated_import() -> None:
    from lipgloss.themes import catppuccin_mocha as m1
    from lipgloss.themes import catppuccin_mocha as m2

    assert m1 is m2


def test_theme_color_is_valid_hex() -> None:
    """Every hex color in every theme is a 7-char lowercase #rrggbb string."""
    import dataclasses
    import re

    hex_re = re.compile(r"^#[0-9a-f]{6}$")
    for theme in (catppuccin_mocha, dracula, gleam):
        for field in dataclasses.fields(theme):  # type: ignore[arg-type]
            value = getattr(theme, field.name)
            if isinstance(value, Color):
                assert hex_re.match(str(value).lower()), (
                    f"{type(theme).__name__}.{field.name} = {value!r} is not a valid #rrggbb hex"
                )
