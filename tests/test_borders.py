"""Tests for border definitions and border rendering via Style."""

from __future__ import annotations

import lipgloss
from lipgloss.borders import (
    Border,
    ascii_border,
    block_border,
    double_border,
    hidden_border,
    inner_half_block_border,
    markdown_border,
    normal_border,
    outer_half_block_border,
    rounded_border,
    thick_border,
)

# ---------------------------------------------------------------------------
# Border definitions — spot-check key runes
# ---------------------------------------------------------------------------


def test_normal_border_chars() -> None:
    b = normal_border()
    assert b.top == "─"
    assert b.left == "│"
    assert b.top_left == "┌"
    assert b.top_right == "┐"
    assert b.bottom_left == "└"
    assert b.bottom_right == "┘"


def test_rounded_border_corners() -> None:
    b = rounded_border()
    assert b.top_left == "╭"
    assert b.top_right == "╮"
    assert b.bottom_left == "╰"
    assert b.bottom_right == "╯"


def test_thick_border_chars() -> None:
    b = thick_border()
    assert b.top == "━"
    assert b.left == "┃"


def test_double_border_chars() -> None:
    b = double_border()
    assert b.top == "═"
    assert b.left == "║"


def test_ascii_border_chars() -> None:
    b = ascii_border()
    assert b.top == "-"
    assert b.left == "|"
    assert b.top_left == "+"


def test_hidden_border_is_spaces() -> None:
    b = hidden_border()
    assert b.top == " "
    assert b.left == " "


def test_block_border_chars() -> None:
    b = block_border()
    assert b.top == "█"


def test_markdown_border_pipes() -> None:
    b = markdown_border()
    assert b.left == "|"
    assert b.right == "|"


def test_outer_half_block_border() -> None:
    b = outer_half_block_border()
    assert b.top == "▀"
    assert b.bottom == "▄"


def test_inner_half_block_border() -> None:
    b = inner_half_block_border()
    assert b.top == "▄"
    assert b.bottom == "▀"


# ---------------------------------------------------------------------------
# Border.get_*_size helpers
# ---------------------------------------------------------------------------


def test_normal_border_sizes() -> None:
    b = normal_border()
    assert b.get_top_size() == 1
    assert b.get_bottom_size() == 1
    assert b.get_left_size() == 1
    assert b.get_right_size() == 1


def test_empty_border_sizes() -> None:
    b = Border()
    assert b.get_top_size() == 0
    assert b.get_left_size() == 0


# ---------------------------------------------------------------------------
# Rendering borders via Style
# ---------------------------------------------------------------------------


def test_render_rounded_border(style: lipgloss.Style) -> None:
    out = style.border_style(rounded_border()).render("hi")
    assert "╭" in out
    assert "╰" in out
    assert "╮" in out
    assert "╯" in out
    assert "hi" in out


def test_render_normal_border(style: lipgloss.Style) -> None:
    out = style.border_style(normal_border()).render("hi")
    assert "┌" in out
    assert "└" in out


def test_render_border_top_only(style: lipgloss.Style) -> None:
    out = style.border_style(normal_border()).border_top(True).render("hi")
    assert "─" in out
    assert "│" not in out


def test_render_border_left_only(style: lipgloss.Style) -> None:
    out = style.border_style(normal_border()).border_left(True).render("hi")
    assert "│" in out
    assert "─" not in out


def test_render_no_border_when_no_style(style: lipgloss.Style) -> None:
    # No border_style set — corners should not appear
    out = style.border_top(True).render("hi")
    assert "┌" not in out
    assert out == "hi"


def test_render_border_with_foreground_color(style: lipgloss.Style) -> None:
    from lipgloss.color import Color

    out = style.border_style(rounded_border()).border_foreground(Color("#FF0000")).render("hi")
    # Should contain the red foreground escape somewhere (on border chars)
    assert "\x1b[38;2;255;0;0m" in out


def test_render_ascii_border(style: lipgloss.Style) -> None:
    out = style.border_style(ascii_border()).render("hi")
    assert "+" in out
    assert "-" in out
    assert "|" in out


def test_border_helper_method(style: lipgloss.Style) -> None:
    # .border(style, top, right, bottom, left)
    out = style.border(normal_border(), True, False, True, False).render("hi")
    assert "─" in out
    assert "│" not in out


def test_render_border_structure(style: lipgloss.Style) -> None:
    # The rendered block should have at least 3 lines (top, content, bottom)
    out = style.border_style(normal_border()).render("hello")
    lines = out.split("\n")
    assert len(lines) == 3
    assert lines[0].startswith("┌")
    assert lines[2].startswith("└")
    assert "hello" in lines[1]
