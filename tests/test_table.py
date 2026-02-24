"""Tests for the Table sub-package."""

from __future__ import annotations

import re

import lipgloss
from lipgloss.table import Filter, HeaderRow, StringData, Table
from lipgloss.table.resizing import _median

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# StringData
# ---------------------------------------------------------------------------


def test_string_data_empty() -> None:
    d = StringData()
    assert d.rows() == 0
    assert d.columns() == 0


def test_string_data_append() -> None:
    d = StringData()
    d.append(["Alice", "30"])
    d.append(["Bob", "25"])
    assert d.rows() == 2
    assert d.columns() == 2


def test_string_data_at() -> None:
    d = StringData(["Alice", "30"], ["Bob", "25"])
    assert d.at(0, 0) == "Alice"
    assert d.at(0, 1) == "30"
    assert d.at(1, 0) == "Bob"
    assert d.at(1, 1) == "25"


def test_string_data_at_out_of_bounds() -> None:
    d = StringData(["Alice"])
    assert d.at(0, 5) == ""
    assert d.at(5, 0) == ""


def test_string_data_item() -> None:
    d = StringData()
    d.item("foo", "bar")
    assert d.rows() == 1
    assert d.at(0, 0) == "foo"
    assert d.at(0, 1) == "bar"


def test_string_data_tracks_max_columns() -> None:
    d = StringData()
    d.append(["a", "b"])
    d.append(["c", "d", "e"])
    assert d.columns() == 3


# ---------------------------------------------------------------------------
# Filter
# ---------------------------------------------------------------------------


def test_filter_even_rows() -> None:
    d = StringData(["A"], ["B"], ["C"], ["D"])
    f = Filter(d).filter(lambda i: i % 2 == 0)
    assert f.rows() == 2
    assert f.at(0, 0) == "A"
    assert f.at(1, 0) == "C"


def test_filter_columns_delegates() -> None:
    d = StringData(["A", "B"], ["C", "D"])
    f = Filter(d)
    assert f.columns() == 2


def test_filter_no_predicate_passes_all() -> None:
    d = StringData(["X"], ["Y"], ["Z"])
    f = Filter(d, lambda _: True)
    assert f.rows() == 3


# ---------------------------------------------------------------------------
# Resizer helper: _median
# ---------------------------------------------------------------------------


def test_median_empty() -> None:
    assert _median([]) == 0


def test_median_single() -> None:
    assert _median([5]) == 5


def test_median_odd() -> None:
    assert _median([3, 1, 2]) == 2


def test_median_even() -> None:
    assert _median([4, 1, 3, 2]) == 2  # (2+3)//2 == 2


# ---------------------------------------------------------------------------
# Table — basic rendering
# ---------------------------------------------------------------------------


def test_table_empty() -> None:
    assert Table().render() == ""


def test_table_headers_only() -> None:
    t = Table().headers("Name", "Age")
    out = _strip_ansi(t.render())
    assert "Name" in out
    assert "Age" in out


def test_table_simple_rows() -> None:
    t = Table().headers("Name", "Age").row("Alice", "30").row("Bob", "25")
    out = _strip_ansi(t.render())
    assert "Alice" in out
    assert "Bob" in out
    assert "30" in out
    assert "25" in out


def test_table_rounded_border_default() -> None:
    t = Table().headers("X").row("y")
    out = _strip_ansi(t.render())
    # Rounded border characters
    assert "╭" in out
    assert "╰" in out


def test_table_no_border() -> None:
    t = (
        Table()
        .headers("A", "B")
        .row("x", "y")
        .border_top(False)
        .border_bottom(False)
        .border_left(False)
        .border_right(False)
        .border_header(False)
        .border_column(False)
    )
    out = _strip_ansi(t.render())
    assert "╭" not in out
    assert "A" in out


def test_table_row_separator() -> None:
    t = Table().headers("Name", "Score").row("Alice", "100").row("Bob", "80").border_row(True)
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    # Should have a separator line between data rows.
    assert len(lines) > 4


def test_table_multiple_rows() -> None:
    t = Table().headers("Col").rows(["one"], ["two"], ["three"])
    out = _strip_ansi(t.render())
    assert "one" in out
    assert "two" in out
    assert "three" in out


def test_table_clear_rows() -> None:
    t = Table().headers("X").row("a").clear_rows()
    out = t.render()
    assert "a" not in out


def test_table_offset() -> None:
    t = Table().headers("N").row("A").row("B").row("C").offset(1)
    out = _strip_ansi(t.render())
    # With offset=1, "A" should be skipped.
    assert "B" in out
    assert "C" in out


def test_table_with_style_func() -> None:
    header_style = lipgloss.Style().bold(True)
    data_style = lipgloss.Style()

    def sf(row: int, col: int) -> lipgloss.Style:
        if row == HeaderRow:
            return header_style
        return data_style

    t = Table().headers("Name").row("Alice").style_func(sf)
    out = t.render()
    # Simply ensure it renders without error.
    assert "Name" in _strip_ansi(out)
    assert "Alice" in _strip_ansi(out)


def test_table_data_source() -> None:
    d = StringData(["x", "y"], ["a", "b"])
    t = Table().headers("C1", "C2").data(d)
    out = _strip_ansi(t.render())
    assert "x" in out
    assert "a" in out


def test_table_fixed_width() -> None:
    t = Table().headers("Name", "Age").row("Alice", "30").width(40)
    out = _strip_ansi(t.render())
    # Each line should be at most 40 chars wide.
    for line in out.splitlines():
        assert len(line) <= 40, f"Line too long: {line!r}"


def test_table_str_equals_render() -> None:
    t = Table().headers("X").row("y")
    assert str(t) == t.render()


# ---------------------------------------------------------------------------
# Table — border characters
# ---------------------------------------------------------------------------


def test_table_uses_border_object() -> None:
    from lipgloss.borders import ascii_border

    t = Table().headers("A").row("b").border(ascii_border())
    out = _strip_ansi(t.render())
    assert "+" in out


def test_table_header_separator() -> None:
    t = Table().headers("Name", "Score").row("Alice", "100")
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    # Line 0: top border, line 1: headers, line 2: separator, line 3: data, line 4: bottom
    assert len(lines) >= 4
    # Separator line should contain ┼ or ─
    assert "─" in lines[2] or "┼" in lines[2]
