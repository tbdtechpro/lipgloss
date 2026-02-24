"""Tests for style_runes()."""

from __future__ import annotations

import lipgloss
from lipgloss.runes import style_runes


def _strip_ansi(s: str) -> str:
    import re

    return re.sub(r"\x1b\[[0-9;]*m", "", s)


def test_style_runes_no_indices() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("hello", [], matched, unmatched)
    # All characters are unmatched; output equals unstyled text.
    assert _strip_ansi(result) == "hello"


def test_style_runes_all_indices() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("hello", [0, 1, 2, 3, 4], matched, unmatched)
    assert _strip_ansi(result) == "hello"


def test_style_runes_first_char() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("hello", [0], matched, unmatched)
    # Strips to original text regardless of styling.
    assert _strip_ansi(result) == "hello"


def test_style_runes_middle_chars() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("hello", [1, 2, 3], matched, unmatched)
    assert _strip_ansi(result) == "hello"


def test_style_runes_alternating() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("abcde", [0, 2, 4], matched, unmatched)
    assert _strip_ansi(result) == "abcde"


def test_style_runes_empty_string() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("", [], matched, unmatched)
    assert result == ""


def test_style_runes_single_char() -> None:
    matched = lipgloss.Style().bold(True)
    unmatched = lipgloss.Style()
    result = style_runes("x", [0], matched, unmatched)
    assert _strip_ansi(result) == "x"


def test_style_runes_groups_consecutive() -> None:
    # Indices 0,1 should be grouped together (one render call), 2,3,4 separately.
    matched = lipgloss.Style()
    unmatched = lipgloss.Style()
    result = style_runes("hello", [0, 1], matched, unmatched)
    assert _strip_ansi(result) == "hello"


def test_style_runes_last_char() -> None:
    matched = lipgloss.Style().underline(True)
    unmatched = lipgloss.Style()
    result = style_runes("hello", [4], matched, unmatched)
    assert _strip_ansi(result) == "hello"


def test_style_runes_preserves_order() -> None:
    matched = lipgloss.Style()
    unmatched = lipgloss.Style()
    result = style_runes("abcdef", [1, 3, 5], matched, unmatched)
    assert _strip_ansi(result) == "abcdef"
