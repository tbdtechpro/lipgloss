"""Tests for join_horizontal() and join_vertical()."""

from __future__ import annotations

import lipgloss
from lipgloss.join import join_horizontal, join_vertical

# ---------------------------------------------------------------------------
# join_horizontal — basic
# ---------------------------------------------------------------------------


def test_join_horizontal_empty() -> None:
    assert join_horizontal(lipgloss.Top) == ""


def test_join_horizontal_single() -> None:
    assert join_horizontal(lipgloss.Top, "abc") == "abc"


def test_join_horizontal_two_same_height() -> None:
    result = join_horizontal(lipgloss.Top, "aaa", "bbb")
    assert result == "aaabbb"


def test_join_horizontal_two_blocks_multiline_same_height() -> None:
    result = join_horizontal(lipgloss.Top, "a\nb", "c\nd")
    lines = result.split("\n")
    assert lines[0] == "ac"
    assert lines[1] == "bd"


def test_join_horizontal_pads_shorter_block_at_top() -> None:
    # blockA is 3 lines, blockB is 1 line; pos=Top → blockB padded below
    result = join_horizontal(lipgloss.Top, "aaa\nbbb\nccc", "xxx")
    lines = result.split("\n")
    assert len(lines) == 3
    assert "xxx" in lines[0]
    assert lines[1].endswith("   ")  # three spaces from empty blockB line


def test_join_horizontal_pads_shorter_block_at_bottom() -> None:
    result = join_horizontal(lipgloss.Bottom, "aaa\nbbb\nccc", "xxx")
    lines = result.split("\n")
    assert len(lines) == 3
    assert "xxx" in lines[2]


def test_join_horizontal_pads_shorter_block_at_center() -> None:
    result = join_horizontal(lipgloss.Center, "aaa\nbbb\nccc\nddd\neee", "xxx")
    lines = result.split("\n")
    assert len(lines) == 5
    # "xxx" should appear somewhere in the middle rows
    xxx_row = next(i for i, l in enumerate(lines) if "xxx" in l)
    assert 1 <= xxx_row <= 3


def test_join_horizontal_pads_width_with_spaces() -> None:
    # "ab" is narrower than "xyz" — join should pad "ab" to width of "xyz"
    result = join_horizontal(lipgloss.Top, "ab", "xyz")
    assert result == "abxyz"


def test_join_horizontal_three_blocks() -> None:
    result = join_horizontal(lipgloss.Top, "a", "b", "c")
    assert result == "abc"


# ---------------------------------------------------------------------------
# join_vertical — basic
# ---------------------------------------------------------------------------


def test_join_vertical_empty() -> None:
    assert join_vertical(lipgloss.Left) == ""


def test_join_vertical_single() -> None:
    assert join_vertical(lipgloss.Left, "abc") == "abc"


def test_join_vertical_two_same_width() -> None:
    result = join_vertical(lipgloss.Left, "abc", "def")
    assert result == "abc\ndef"


def test_join_vertical_left_align_pads_narrower() -> None:
    result = join_vertical(lipgloss.Left, "hi", "world")
    lines = result.split("\n")
    # "hi" should be padded on right to match "world" width
    assert lines[0] == "hi   "
    assert lines[1] == "world"


def test_join_vertical_right_align_pads_narrower() -> None:
    result = join_vertical(lipgloss.Right, "hi", "world")
    lines = result.split("\n")
    assert lines[0] == "   hi"
    assert lines[1] == "world"


def test_join_vertical_center_align() -> None:
    result = join_vertical(lipgloss.Center, "hi", "world")
    lines = result.split("\n")
    # "hi" (2 wide) centered in 5: gap=3, split=round(3*0.5)=2,
    # right=3-2=1, left=3-right=2 → "  hi "
    assert lines[0] == "  hi "
    assert lines[1] == "world"


def test_join_vertical_three_blocks() -> None:
    result = join_vertical(lipgloss.Left, "a", "b", "c")
    assert result == "a\nb\nc"


def test_join_vertical_multiline_blocks() -> None:
    result = join_vertical(lipgloss.Left, "aa\nbb", "cc\ndd")
    assert result == "aa\nbb\ncc\ndd"


# ---------------------------------------------------------------------------
# Width correctness (ANSI-safe)
# ---------------------------------------------------------------------------


def test_join_horizontal_correct_width_padding() -> None:
    # Each block is 3 wide, 1 high → result should be 6 wide
    result = join_horizontal(lipgloss.Top, "abc", "def")
    from lipgloss.size import width

    assert width(result) == 6


def test_join_vertical_correct_height() -> None:
    result = join_vertical(lipgloss.Left, "a\nb", "c\nd\ne")
    assert result.count("\n") == 4  # 5 lines total
