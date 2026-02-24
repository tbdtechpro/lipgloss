"""Tests for color types."""

from __future__ import annotations

from lipgloss.color import (
    AdaptiveColor,
    ANSIColor,
    Color,
    CompleteAdaptiveColor,
    CompleteColor,
    NoColor,
    TerminalColor,
)
from lipgloss.renderer import ColorProfile, Renderer

# ---------------------------------------------------------------------------
# Protocol conformance
# ---------------------------------------------------------------------------


def test_color_satisfies_protocol() -> None:
    assert isinstance(Color("#FF0000"), TerminalColor)


def test_no_color_satisfies_protocol() -> None:
    assert isinstance(NoColor(), TerminalColor)


def test_ansi_color_satisfies_protocol() -> None:
    assert isinstance(ANSIColor(1), TerminalColor)


def test_adaptive_color_satisfies_protocol() -> None:
    assert isinstance(AdaptiveColor(light="0", dark="15"), TerminalColor)


def test_complete_color_satisfies_protocol() -> None:
    assert isinstance(CompleteColor(true_color="#FF0000", ansi256="196", ansi="1"), TerminalColor)


# ---------------------------------------------------------------------------
# NoColor
# ---------------------------------------------------------------------------


def test_no_color_resolves_to_empty(truecolor_renderer: Renderer) -> None:
    assert NoColor().resolve(truecolor_renderer) == ""


def test_no_color_resolves_to_empty_on_ascii(ascii_renderer: Renderer) -> None:
    assert NoColor().resolve(ascii_renderer) == ""


# ---------------------------------------------------------------------------
# Color (hex and ANSI index strings)
# ---------------------------------------------------------------------------


def test_color_hex_truecolor(truecolor_renderer: Renderer) -> None:
    result = Color("#FF0000").resolve(truecolor_renderer)
    assert result == "\x1b[38;2;255;0;0m"


def test_color_ansi_index(truecolor_renderer: Renderer) -> None:
    result = Color("200").resolve(truecolor_renderer)
    assert result == "\x1b[38;5;200m"


def test_color_ascii_returns_empty(ascii_renderer: Renderer) -> None:
    assert Color("#FF0000").resolve(ascii_renderer) == ""


# ---------------------------------------------------------------------------
# ANSIColor
# ---------------------------------------------------------------------------


def test_ansi_color_basic(truecolor_renderer: Renderer) -> None:
    result = ANSIColor(1).resolve(truecolor_renderer)
    # ANSI index 1 → basic red \x1b[31m
    assert result == "\x1b[31m"


def test_ansi_color_bright(truecolor_renderer: Renderer) -> None:
    result = ANSIColor(9).resolve(truecolor_renderer)
    # Bright red = index 9 → \x1b[91m
    assert result == "\x1b[91m"


# ---------------------------------------------------------------------------
# AdaptiveColor
# ---------------------------------------------------------------------------


def test_adaptive_color_dark_background(truecolor_renderer: Renderer) -> None:
    truecolor_renderer.set_dark_background(True)
    c = AdaptiveColor(light="0", dark="15")
    result = c.resolve(truecolor_renderer)
    # dark="15" → bright white \x1b[97m
    assert result == "\x1b[97m"


def test_adaptive_color_light_background(truecolor_renderer: Renderer) -> None:
    truecolor_renderer.set_dark_background(False)
    c = AdaptiveColor(light="0", dark="15")
    result = c.resolve(truecolor_renderer)
    # light="0" → black \x1b[30m
    assert result == "\x1b[30m"


# ---------------------------------------------------------------------------
# CompleteColor
# ---------------------------------------------------------------------------


def test_complete_color_truecolor(truecolor_renderer: Renderer) -> None:
    c = CompleteColor(true_color="#FF0000", ansi256="196", ansi="1")
    result = c.resolve(truecolor_renderer)
    assert result == "\x1b[38;2;255;0;0m"


def test_complete_color_ansi256(ansi256_renderer: Renderer) -> None:
    c = CompleteColor(true_color="#FF0000", ansi256="196", ansi="1")
    result = c.resolve(ansi256_renderer)
    assert result == "\x1b[38;5;196m"


def test_complete_color_ansi(ansi_renderer: Renderer) -> None:
    c = CompleteColor(true_color="#FF0000", ansi256="196", ansi="1")
    result = c.resolve(ansi_renderer)
    assert result == "\x1b[31m"


def test_complete_color_ascii_returns_empty(ascii_renderer: Renderer) -> None:
    c = CompleteColor(true_color="#FF0000", ansi256="196", ansi="1")
    assert c.resolve(ascii_renderer) == ""


# ---------------------------------------------------------------------------
# CompleteAdaptiveColor
# ---------------------------------------------------------------------------


def test_complete_adaptive_color_dark(truecolor_renderer: Renderer) -> None:
    truecolor_renderer.set_dark_background(True)
    c = CompleteAdaptiveColor(
        light=CompleteColor(true_color="#000000", ansi256="0", ansi="0"),
        dark=CompleteColor(true_color="#FFFFFF", ansi256="15", ansi="7"),
    )
    result = c.resolve(truecolor_renderer)
    assert result == "\x1b[38;2;255;255;255m"


def test_complete_adaptive_color_light(truecolor_renderer: Renderer) -> None:
    truecolor_renderer.set_dark_background(False)
    c = CompleteAdaptiveColor(
        light=CompleteColor(true_color="#000000", ansi256="0", ansi="0"),
        dark=CompleteColor(true_color="#FFFFFF", ansi256="15", ansi="7"),
    )
    result = c.resolve(truecolor_renderer)
    assert result == "\x1b[38;2;0;0;0m"
