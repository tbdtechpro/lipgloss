"""Tests for place(), place_horizontal(), place_vertical()."""

from __future__ import annotations

import lipgloss
from lipgloss.position import Center, Left, Right, Top, Bottom, place, place_horizontal, place_vertical
from lipgloss.size import height, width


# ---------------------------------------------------------------------------
# place_horizontal
# ---------------------------------------------------------------------------


def test_place_horizontal_no_op_when_wider(style: lipgloss.Style) -> None:
    # String is wider than the target — should return unchanged
    result = place_horizontal(3, Left, "hello")
    assert result == "hello"


def test_place_horizontal_left(style: lipgloss.Style) -> None:
    result = place_horizontal(10, Left, "hi")
    assert result == "hi        "
    assert len(result) == 10


def test_place_horizontal_right(style: lipgloss.Style) -> None:
    result = place_horizontal(10, Right, "hi")
    assert result == "        hi"
    assert len(result) == 10


def test_place_horizontal_center_even(style: lipgloss.Style) -> None:
    # "hi" is 2 wide, placed in 10 → 4 left, 4 right
    result = place_horizontal(10, Center, "hi")
    assert result == "    hi    "


def test_place_horizontal_center_odd_gap(style: lipgloss.Style) -> None:
    # "hi" is 2 wide, placed in 9 → gap=7, 3 left, 4 right (remainder on right)
    result = place_horizontal(9, Center, "hi")
    assert len(result) == 9
    assert "hi" in result


def test_place_horizontal_multiline(style: lipgloss.Style) -> None:
    result = place_horizontal(10, Left, "hi\nhello")
    lines = result.split("\n")
    assert len(lines) == 2
    assert len(lines[0]) == 10
    assert len(lines[1]) == 10


def test_place_horizontal_exact_width_no_change(style: lipgloss.Style) -> None:
    result = place_horizontal(5, Left, "hello")
    assert result == "hello"


# ---------------------------------------------------------------------------
# place_vertical
# ---------------------------------------------------------------------------


def test_place_vertical_no_op_when_taller(style: lipgloss.Style) -> None:
    result = place_vertical(2, Top, "a\nb\nc")
    assert result == "a\nb\nc"


def test_place_vertical_top(style: lipgloss.Style) -> None:
    result = place_vertical(5, Top, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    assert lines[0] == "hi"
    # Remaining lines are spaces (whitespace fill)
    for line in lines[1:]:
        assert set(line) <= {" "}


def test_place_vertical_bottom(style: lipgloss.Style) -> None:
    result = place_vertical(5, Bottom, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    assert lines[-1] == "hi"


def test_place_vertical_center(style: lipgloss.Style) -> None:
    result = place_vertical(5, Center, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    hi_idx = next(i for i, l in enumerate(lines) if l.strip() == "hi")
    assert 1 <= hi_idx <= 3


def test_place_vertical_exact_height_no_change(style: lipgloss.Style) -> None:
    result = place_vertical(1, Top, "hi")
    assert result == "hi"


# ---------------------------------------------------------------------------
# place (combined)
# ---------------------------------------------------------------------------


def test_place_top_left(style: lipgloss.Style) -> None:
    result = place(20, 5, Left, Top, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    assert lines[0].startswith("hi")
    assert width(result) == 20


def test_place_bottom_right(style: lipgloss.Style) -> None:
    result = place(20, 5, Right, Bottom, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    assert lines[-1].endswith("hi")


def test_place_center_center(style: lipgloss.Style) -> None:
    result = place(20, 5, Center, Center, "hi")
    lines = result.split("\n")
    assert len(lines) == 5
    hi_row = next(i for i, l in enumerate(lines) if "hi" in l)
    assert 1 <= hi_row <= 3
    # Check horizontal centering — "hi" should have leading spaces
    hi_line = lines[hi_row].rstrip()
    assert hi_line.startswith("   ")


def test_place_preserves_width(style: lipgloss.Style) -> None:
    result = place(30, 5, Left, Top, "hello")
    assert width(result) == 30


def test_place_preserves_height(style: lipgloss.Style) -> None:
    result = place(10, 8, Left, Top, "hi")
    assert height(result) == 8
