"""Tests for ANSI-aware width/height/size utilities."""

from __future__ import annotations

from lipgloss.size import height, size, width

# ---------------------------------------------------------------------------
# width()
# ---------------------------------------------------------------------------


def test_width_plain_ascii() -> None:
    assert width("hello") == 5


def test_width_empty() -> None:
    assert width("") == 0


def test_width_multiline_returns_widest() -> None:
    assert width("hi\nhello\nok") == 5


def test_width_strips_ansi() -> None:
    # ANSI bold escape around "hello" — visible width is still 5
    ansi_str = "\x1b[1mhello\x1b[0m"
    assert width(ansi_str) == 5


def test_width_ansi_with_color() -> None:
    ansi_str = "\x1b[38;2;255;0;0mred\x1b[0m"
    assert width(ansi_str) == 3


def test_width_multiline_with_ansi() -> None:
    # Second line has ANSI escape but visible width 5
    s = "hi\n\x1b[1mhello\x1b[0m"
    assert width(s) == 5


# ---------------------------------------------------------------------------
# height()
# ---------------------------------------------------------------------------


def test_height_single_line() -> None:
    assert height("hello") == 1


def test_height_two_lines() -> None:
    assert height("hello\nworld") == 2


def test_height_empty() -> None:
    assert height("") == 1


def test_height_trailing_newline() -> None:
    assert height("hello\n") == 2


# ---------------------------------------------------------------------------
# size()
# ---------------------------------------------------------------------------


def test_size_single_line() -> None:
    assert size("hello") == (5, 1)


def test_size_multiline() -> None:
    assert size("hi\nhello") == (5, 2)


def test_size_with_ansi() -> None:
    s = "\x1b[1mhello\x1b[0m\nhi"
    assert size(s) == (5, 2)
