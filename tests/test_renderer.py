"""Tests for Renderer and color-string resolution."""

from __future__ import annotations

import io

import pytest

from lipgloss.renderer import ColorProfile, Renderer

# ---------------------------------------------------------------------------
# Color profile detection
# ---------------------------------------------------------------------------


def test_set_color_profile(truecolor_renderer: Renderer) -> None:
    assert truecolor_renderer.color_profile() == ColorProfile.TRUE_COLOR


def test_ascii_profile(ascii_renderer: Renderer) -> None:
    assert ascii_renderer.color_profile() == ColorProfile.ASCII


def test_ansi256_profile(ansi256_renderer: Renderer) -> None:
    assert ansi256_renderer.color_profile() == ColorProfile.ANSI256


def test_ansi_profile(ansi_renderer: Renderer) -> None:
    assert ansi_renderer.color_profile() == ColorProfile.ANSI


# ---------------------------------------------------------------------------
# _resolve_color_string — ASCII profile returns empty string
# ---------------------------------------------------------------------------


def test_ascii_profile_returns_empty_for_hex(ascii_renderer: Renderer) -> None:
    assert ascii_renderer._resolve_color_string("#FF0000") == ""


def test_ascii_profile_returns_empty_for_ansi_index(ascii_renderer: Renderer) -> None:
    assert ascii_renderer._resolve_color_string("9") == ""


# ---------------------------------------------------------------------------
# _resolve_color_string — TrueColor profile
# ---------------------------------------------------------------------------


def test_truecolor_hex_red(truecolor_renderer: Renderer) -> None:
    result = truecolor_renderer._resolve_color_string("#FF0000")
    assert result == "\x1b[38;2;255;0;0m"


def test_truecolor_hex_green(truecolor_renderer: Renderer) -> None:
    result = truecolor_renderer._resolve_color_string("#00FF00")
    assert result == "\x1b[38;2;0;255;0m"


def test_truecolor_hex_blue(truecolor_renderer: Renderer) -> None:
    result = truecolor_renderer._resolve_color_string("#0000FF")
    assert result == "\x1b[38;2;0;0;255m"


def test_truecolor_ansi_basic_color(truecolor_renderer: Renderer) -> None:
    # ANSI index 0–15 → basic ANSI escapes even on TrueColor profile
    result = truecolor_renderer._resolve_color_string("1")
    assert result == "\x1b[31m"  # basic red


def test_truecolor_ansi256_index(truecolor_renderer: Renderer) -> None:
    result = truecolor_renderer._resolve_color_string("200")
    assert result == "\x1b[38;5;200m"


# ---------------------------------------------------------------------------
# _resolve_color_string — ANSI256 profile
# ---------------------------------------------------------------------------


def test_ansi256_hex_degrades(ansi256_renderer: Renderer) -> None:
    result = ansi256_renderer._resolve_color_string("#FF0000")
    # Should produce a 256-color escape (not a 24-bit one)
    assert result.startswith("\x1b[38;5;")
    assert "38;2;" not in result


def test_ansi256_index_passthrough(ansi256_renderer: Renderer) -> None:
    result = ansi256_renderer._resolve_color_string("100")
    assert result == "\x1b[38;5;100m"


# ---------------------------------------------------------------------------
# _resolve_color_string — ANSI (16-colour) profile
# ---------------------------------------------------------------------------


def test_ansi_profile_basic_color(ansi_renderer: Renderer) -> None:
    result = ansi_renderer._resolve_color_string("3")
    assert result == "\x1b[33m"  # basic yellow


def test_ansi_profile_256_index_degrades(ansi_renderer: Renderer) -> None:
    # Any 256-color index should degrade to a basic 16-color escape
    result = ansi_renderer._resolve_color_string("200")
    assert result.startswith("\x1b[")
    assert "38;5;" not in result
    assert "38;2;" not in result


# ---------------------------------------------------------------------------
# dark background detection override
# ---------------------------------------------------------------------------


def test_set_dark_background(truecolor_renderer: Renderer) -> None:
    truecolor_renderer.set_dark_background(True)
    assert truecolor_renderer.has_dark_background() is True
    truecolor_renderer.set_dark_background(False)
    assert truecolor_renderer.has_dark_background() is False
