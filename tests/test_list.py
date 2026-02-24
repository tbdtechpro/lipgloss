"""Tests for the List sub-package and enumerators."""

from __future__ import annotations

import re

import pytest

from lipgloss.list import (
    Alphabet,
    Arabic,
    Asterisk,
    Bullet,
    Dash,
    Items,
    List,
    Roman,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# Enumerators
# ---------------------------------------------------------------------------


class _FakeItems:
    """Minimal Items stub for enumerator tests."""

    def __init__(self, n: int) -> None:
        self._n = n

    def at(self, i: int) -> str:
        return str(i)

    def length(self) -> int:
        return self._n

    def __len__(self) -> int:
        return self._n


_ITEMS = _FakeItems(30)


def test_arabic_first() -> None:
    assert Arabic(_ITEMS, 0) == "1."


def test_arabic_tenth() -> None:
    assert Arabic(_ITEMS, 9) == "10."


def test_alphabet_first() -> None:
    assert Alphabet(_ITEMS, 0) == "A."


def test_alphabet_last_single() -> None:
    assert Alphabet(_ITEMS, 25) == "Z."


def test_alphabet_double_first() -> None:
    # index 26 → "AA."
    assert Alphabet(_ITEMS, 26) == "AA."


def test_roman_first() -> None:
    assert Roman(_ITEMS, 0) == "I."


def test_roman_second() -> None:
    assert Roman(_ITEMS, 1) == "II."


def test_roman_third() -> None:
    assert Roman(_ITEMS, 2) == "III."


def test_roman_fourth() -> None:
    assert Roman(_ITEMS, 3) == "IV."


def test_roman_ninth() -> None:
    assert Roman(_ITEMS, 8) == "IX."


def test_roman_tenth() -> None:
    assert Roman(_ITEMS, 9) == "X."


def test_bullet_always_same() -> None:
    assert Bullet(_ITEMS, 0) == "•"
    assert Bullet(_ITEMS, 99) == "•"


def test_asterisk_always_same() -> None:
    assert Asterisk(_ITEMS, 0) == "*"


def test_dash_always_same() -> None:
    assert Dash(_ITEMS, 0) == "-"


# ---------------------------------------------------------------------------
# Items wrapper
# ---------------------------------------------------------------------------


def test_items_len() -> None:
    items = Items(["a", "b", "c"])
    assert len(items) == 3
    assert items.length() == 3


def test_items_at() -> None:
    items = Items(["x", "y"])
    assert items.at(0) == "x"
    assert items.at(1) == "y"


# ---------------------------------------------------------------------------
# List — basic
# ---------------------------------------------------------------------------


def test_list_empty() -> None:
    assert List().render() == ""


def test_list_single_item() -> None:
    out = _strip_ansi(List("hello").render())
    assert "hello" in out


def test_list_three_items() -> None:
    out = _strip_ansi(List("A", "B", "C").render())
    lines = out.splitlines()
    assert len(lines) == 3
    assert "A" in lines[0]
    assert "B" in lines[1]
    assert "C" in lines[2]


def test_list_default_bullet() -> None:
    out = _strip_ansi(List("X", "Y").render())
    assert "•" in out


def test_list_item_method() -> None:
    l = List().item("A").item("B")
    out = _strip_ansi(l.render())
    assert "A" in out
    assert "B" in out


def test_list_items_method() -> None:
    l = List().items("P", "Q", "R")
    out = _strip_ansi(l.render())
    lines = out.splitlines()
    assert len(lines) == 3


def test_list_arabic_enumerator() -> None:
    l = List("Foo", "Bar", "Baz").enumerator(Arabic)
    out = _strip_ansi(l.render())
    assert "1." in out
    assert "2." in out
    assert "3." in out


def test_list_roman_alignment() -> None:
    l = List("A", "B", "C", "D", "E").enumerator(Roman)
    out = _strip_ansi(l.render())
    lines = out.splitlines()
    # "III." is the widest prefix; all lines should be the same width up to content.
    # The "I." line should be right-padded/aligned.
    assert "III." in lines[2]
    # First item should have spaces before "I." for alignment.
    assert lines[0].startswith(" ")


def test_list_alphabet_enumerator() -> None:
    l = List("X", "Y", "Z").enumerator(Alphabet)
    out = _strip_ansi(l.render())
    assert "A." in out
    assert "B." in out
    assert "C." in out


def test_list_dash_enumerator() -> None:
    l = List("X", "Y").enumerator(Dash)
    out = _strip_ansi(l.render())
    assert "-" in out


def test_list_asterisk_enumerator() -> None:
    l = List("X", "Y").enumerator(Asterisk)
    out = _strip_ansi(l.render())
    assert "*" in out


# ---------------------------------------------------------------------------
# List — hide
# ---------------------------------------------------------------------------


def test_list_hidden_returns_empty() -> None:
    l = List("A", "B").hide(True)
    assert l.render() == ""


def test_list_hidden_false_renders() -> None:
    l = List("A", "B").hide(False)
    assert l.render() != ""


def test_nested_list_hidden() -> None:
    nested = List("X", "Y").hide(True)
    parent = List("A", nested, "B")
    out = _strip_ansi(parent.render())
    lines = out.splitlines()
    # Only "A" and "B" should appear; nested list is hidden.
    assert len(lines) == 2
    assert "X" not in out
    assert "Y" not in out


# ---------------------------------------------------------------------------
# List — nesting
# ---------------------------------------------------------------------------


def test_nested_list_indented() -> None:
    nested = List("Inner1", "Inner2")
    parent = List("Outer", nested)
    out = _strip_ansi(parent.render())
    lines = out.splitlines()
    # Outer item first, then indented inner items.
    assert "Outer" in lines[0]
    # Inner items should be indented (start with spaces).
    inner_lines = [l for l in lines[1:] if l.strip()]
    for line in inner_lines:
        assert line.startswith(" ")


def test_nested_list_content() -> None:
    nested = List("Apple", "Banana")
    parent = List("Fruit", nested, "Veg")
    out = _strip_ansi(parent.render())
    assert "Fruit" in out
    assert "Apple" in out
    assert "Banana" in out
    assert "Veg" in out


def test_list_str_equals_render() -> None:
    l = List("A", "B")
    assert str(l) == l.render()


def test_list_custom_enumerator() -> None:
    def star_enum(items: Items, i: int) -> str:
        return f"[{i + 1}]"

    l = List("X", "Y", "Z").enumerator(star_enum)
    out = _strip_ansi(l.render())
    assert "[1]" in out
    assert "[2]" in out
    assert "[3]" in out
