"""Tests for Style — setters, getters, unsetters, render(), inherit."""

from __future__ import annotations

import lipgloss
from lipgloss.color import Color, NoColor
from lipgloss.renderer import Renderer


# ---------------------------------------------------------------------------
# Immutability / copy
# ---------------------------------------------------------------------------


def test_setter_returns_new_instance(style: lipgloss.Style) -> None:
    s2 = style.bold(True)
    assert s2 is not style


def test_original_unmodified_after_setter(style: lipgloss.Style) -> None:
    style.bold(True)
    assert style.get_bold() is False


def test_copy_is_independent(style: lipgloss.Style) -> None:
    s2 = style.bold(True)
    s3 = s2.copy()
    s4 = s3.unset_bold()
    assert s2.get_bold() is True
    assert s4.get_bold() is False


# ---------------------------------------------------------------------------
# Boolean property round-trips
# ---------------------------------------------------------------------------


def _check_bool_prop(style: lipgloss.Style, setter: str, getter: str, unsetter: str) -> None:
    s = getattr(style, setter)(True)
    assert getattr(s, getter)() is True
    s2 = getattr(s, unsetter)()
    assert getattr(s2, getter)() is False


def test_bold(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "bold", "get_bold", "unset_bold")


def test_italic(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "italic", "get_italic", "unset_italic")


def test_underline(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "underline", "get_underline", "unset_underline")


def test_strikethrough(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "strikethrough", "get_strikethrough", "unset_strikethrough")


def test_reverse(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "reverse", "get_reverse", "unset_reverse")


def test_blink(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "blink", "get_blink", "unset_blink")


def test_faint(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "faint", "get_faint", "unset_faint")


def test_inline(style: lipgloss.Style) -> None:
    _check_bool_prop(style, "inline", "get_inline", "unset_inline")


# ---------------------------------------------------------------------------
# Dimension properties
# ---------------------------------------------------------------------------


def test_width(style: lipgloss.Style) -> None:
    assert style.width(42).get_width() == 42
    assert style.width(42).unset_width().get_width() == 0


def test_height(style: lipgloss.Style) -> None:
    assert style.height(10).get_height() == 10


def test_max_width(style: lipgloss.Style) -> None:
    assert style.max_width(80).get_max_width() == 80


def test_max_height(style: lipgloss.Style) -> None:
    assert style.max_height(24).get_max_height() == 24


def test_tab_width(style: lipgloss.Style) -> None:
    assert style.tab_width(8).get_tab_width() == 8
    assert style.get_tab_width() == 4  # default


# ---------------------------------------------------------------------------
# Padding CSS shorthand
# ---------------------------------------------------------------------------


def test_padding_single_value(style: lipgloss.Style) -> None:
    s = style.padding(2)
    assert s.get_padding_top() == 2
    assert s.get_padding_right() == 2
    assert s.get_padding_bottom() == 2
    assert s.get_padding_left() == 2


def test_padding_two_values(style: lipgloss.Style) -> None:
    s = style.padding(1, 3)
    assert s.get_padding_top() == 1
    assert s.get_padding_right() == 3
    assert s.get_padding_bottom() == 1
    assert s.get_padding_left() == 3


def test_padding_four_values(style: lipgloss.Style) -> None:
    s = style.padding(1, 2, 3, 4)
    assert s.get_padding_top() == 1
    assert s.get_padding_right() == 2
    assert s.get_padding_bottom() == 3
    assert s.get_padding_left() == 4


# ---------------------------------------------------------------------------
# Margin CSS shorthand
# ---------------------------------------------------------------------------


def test_margin_single_value(style: lipgloss.Style) -> None:
    s = style.margin(2)
    assert s.get_margin_top() == 2
    assert s.get_margin_right() == 2
    assert s.get_margin_bottom() == 2
    assert s.get_margin_left() == 2


def test_margin_four_values(style: lipgloss.Style) -> None:
    s = style.margin(1, 2, 3, 4)
    assert s.get_margin_top() == 1
    assert s.get_margin_right() == 2
    assert s.get_margin_bottom() == 3
    assert s.get_margin_left() == 4


# ---------------------------------------------------------------------------
# Alignment
# ---------------------------------------------------------------------------


def test_align_horizontal(style: lipgloss.Style) -> None:
    s = style.align(lipgloss.Center)
    assert s.get_align_horizontal() == lipgloss.Center


def test_align_both(style: lipgloss.Style) -> None:
    s = style.align(lipgloss.Right, lipgloss.Bottom)
    assert s.get_align_horizontal() == lipgloss.Right
    assert s.get_align_vertical() == lipgloss.Bottom


# ---------------------------------------------------------------------------
# set_string / get_value
# ---------------------------------------------------------------------------


def test_set_string(style: lipgloss.Style) -> None:
    s = style.set_string("hello", "world")
    assert s.get_value() == "hello world"


def test_set_string_renders_without_args(style: lipgloss.Style) -> None:
    s = style.set_string("hi")
    assert s.render() == "hi"


def test_render_args_join_with_space(style: lipgloss.Style) -> None:
    assert style.render("hello", "world") == "hello world"


# ---------------------------------------------------------------------------
# Inherit
# ---------------------------------------------------------------------------


def test_inherit_copies_unset_prop(style: lipgloss.Style) -> None:
    parent = style.bold(True).italic(True)
    child = style.bold(False).inherit(parent)
    # bold is already set on child (False) — should NOT be overridden
    assert child.get_bold() is False
    # italic is unset on child — should be inherited from parent
    assert child.get_italic() is True


def test_inherit_does_not_copy_margins(style: lipgloss.Style) -> None:
    parent = style.margin_top(5)
    child = style.inherit(parent)
    assert child.get_margin_top() == 0


def test_inherit_does_not_copy_padding(style: lipgloss.Style) -> None:
    parent = style.padding_left(4)
    child = style.inherit(parent)
    assert child.get_padding_left() == 0


# ---------------------------------------------------------------------------
# render() — text content
# ---------------------------------------------------------------------------


def test_render_plain(style: lipgloss.Style) -> None:
    assert style.render("hello") == "hello"


def test_render_no_props_returns_string(style: lipgloss.Style) -> None:
    assert style.render("abc") == "abc"


def test_render_bold(style: lipgloss.Style) -> None:
    out = style.bold(True).render("x")
    assert "\x1b[1m" in out
    assert out.endswith("\x1b[0m")


def test_render_italic(style: lipgloss.Style) -> None:
    out = style.italic(True).render("x")
    assert "\x1b[3m" in out


def test_render_underline(style: lipgloss.Style) -> None:
    out = style.underline(True).render("x")
    assert "\x1b[4m" in out


def test_render_strikethrough(style: lipgloss.Style) -> None:
    out = style.strikethrough(True).render("x")
    assert "\x1b[9m" in out


def test_render_faint(style: lipgloss.Style) -> None:
    out = style.faint(True).render("x")
    assert "\x1b[2m" in out


def test_render_foreground_hex(style: lipgloss.Style) -> None:
    out = style.foreground(Color("#FF0000")).render("x")
    assert "\x1b[38;2;255;0;0m" in out


def test_render_background_hex(style: lipgloss.Style) -> None:
    out = style.background(Color("#0000FF")).render("x")
    assert "\x1b[48;2;0;0;255m" in out


def test_render_nocolor_no_escape(style: lipgloss.Style) -> None:
    out = style.foreground(NoColor()).render("hello")
    assert out == "hello"


def test_render_multicolor(style: lipgloss.Style) -> None:
    out = style.bold(True).foreground(Color("#FF0000")).render("hi")
    assert "\x1b[" in out
    assert "hi" in out


# ---------------------------------------------------------------------------
# render() — inline mode
# ---------------------------------------------------------------------------


def test_render_inline_strips_newlines(style: lipgloss.Style) -> None:
    out = style.inline(True).render("a\nb\nc")
    assert "\n" not in out
    assert "abc" in out


# ---------------------------------------------------------------------------
# render() — padding
# ---------------------------------------------------------------------------


def test_render_padding_left(style: lipgloss.Style) -> None:
    out = style.padding_left(3).render("hi")
    assert out == "   hi"


def test_render_padding_right(style: lipgloss.Style) -> None:
    out = style.padding_right(3).render("hi")
    assert out == "hi   "


def test_render_padding_top(style: lipgloss.Style) -> None:
    # Top padding adds N lines above the content.  The empty lines are
    # horizontally aligned to match content width (spaces appended), so
    # we check structure rather than exact "\n\n" prefix.
    out = style.padding_top(2).render("hi")
    lines = out.split("\n")
    assert len(lines) == 3
    assert lines[-1] == "hi"


def test_render_padding_bottom(style: lipgloss.Style) -> None:
    out = style.padding_bottom(2).render("hi")
    lines = out.split("\n")
    assert len(lines) == 3
    assert lines[0] == "hi"


# ---------------------------------------------------------------------------
# render() — width and horizontal alignment
# ---------------------------------------------------------------------------


def test_render_width_pads_to_width(style: lipgloss.Style) -> None:
    out = style.width(10).render("hi")
    assert len(out) == 10


def test_render_width_left_align(style: lipgloss.Style) -> None:
    out = style.width(10).align(lipgloss.Left).render("hi")
    assert out == "hi        "


def test_render_width_right_align(style: lipgloss.Style) -> None:
    out = style.width(10).align(lipgloss.Right).render("hi")
    assert out == "        hi"


def test_render_width_center_align(style: lipgloss.Style) -> None:
    out = style.width(10).align(lipgloss.Center).render("hi")
    assert out == "    hi    "


# ---------------------------------------------------------------------------
# render() — height and vertical alignment
# ---------------------------------------------------------------------------


def test_render_height_pads_lines(style: lipgloss.Style) -> None:
    out = style.height(4).render("hi")
    assert out.count("\n") == 3


def test_render_height_top_align(style: lipgloss.Style) -> None:
    out = style.height(3).align(lipgloss.Left, lipgloss.Top).render("hi")
    lines = out.split("\n")
    assert lines[0] == "hi"


def test_render_height_bottom_align(style: lipgloss.Style) -> None:
    out = style.height(3).align(lipgloss.Left, lipgloss.Bottom).render("hi")
    lines = out.split("\n")
    assert lines[-1] == "hi"


# ---------------------------------------------------------------------------
# render() — max_width / max_height
# ---------------------------------------------------------------------------


def test_render_max_width_truncates(style: lipgloss.Style) -> None:
    out = style.max_width(5).render("Hello World")
    assert out == "Hello"


def test_render_max_height_truncates(style: lipgloss.Style) -> None:
    out = style.max_height(2).render("a\nb\nc\nd")
    assert out.count("\n") == 1
    assert out == "a\nb"


# ---------------------------------------------------------------------------
# render() — tab width
# ---------------------------------------------------------------------------


def test_render_tab_default(style: lipgloss.Style) -> None:
    out = style.render("\thi")
    assert out == "    hi"


def test_render_tab_custom_width(style: lipgloss.Style) -> None:
    out = style.tab_width(2).render("\thi")
    assert out == "  hi"


def test_render_tab_width_zero_removes_tabs(style: lipgloss.Style) -> None:
    out = style.tab_width(0).render("\thi")
    assert out == "hi"


def test_render_tab_width_minus1_preserves(style: lipgloss.Style) -> None:
    out = style.tab_width(-1).render("\thi")
    assert out == "\thi"


# ---------------------------------------------------------------------------
# render() — transform
# ---------------------------------------------------------------------------


def test_render_transform(style: lipgloss.Style) -> None:
    s = style.transform(str.upper)
    assert s.render("hello") == "HELLO"


# ---------------------------------------------------------------------------
# render() — word wrap with width
# ---------------------------------------------------------------------------


def test_render_wraps_long_line(style: lipgloss.Style) -> None:
    # width 5, "hello world" → should wrap between words
    out = style.width(5).render("hello world")
    assert "\n" in out


# ---------------------------------------------------------------------------
# __str__
# ---------------------------------------------------------------------------


def test_str_uses_set_string(style: lipgloss.Style) -> None:
    s = style.set_string("hi there")
    assert str(s) == "hi there"
