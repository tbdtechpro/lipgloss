"""
Column width distribution algorithm.

Port of: table/resizing.go

Distributes available table width across columns using a flex-sizing
algorithm: columns are first given their minimum content width, then
remaining space is distributed proportionally. Respects a fixed
table-level width constraint when set.

Internal function used by Table.render(); not part of the public API.
"""

from __future__ import annotations

import math
import re
import unicodedata

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*[mK]")


def _visible_width(s: str) -> int:
    """Return the visible terminal width of *s*, stripping ANSI escapes."""
    s = _ANSI_RE.sub("", s)
    w = 0
    for ch in s:
        eaw = unicodedata.east_asian_width(ch)
        if eaw in ("W", "F"):
            w += 2
        else:
            w += 1
    return w


def _median(values: list[int]) -> int:
    if not values:
        return 0
    sorted_vals = sorted(values)
    n = len(sorted_vals)
    mid = n // 2
    if n % 2 == 1:
        return sorted_vals[mid]
    return (sorted_vals[mid - 1] + sorted_vals[mid]) // 2


def _word_wrap_height(content: str, col_width: int) -> int:
    """Estimate the number of lines after wrapping *content* at *col_width*."""
    if col_width <= 0:
        return 1
    content = content.replace("\r\n", "\n")
    total = 0
    for line in content.split("\n"):
        vis = _visible_width(line)
        if vis == 0:
            total += 1
        else:
            total += math.ceil(vis / col_width)
    return total


class _ResizerColumn:
    """Tracks per-column statistics used during width optimisation."""

    def __init__(self, index: int, min_w: int, max_w: int, median_w: int) -> None:
        self.index = index
        self.min = min_w
        self.max = max_w
        self.median = median_w
        self.rows: list[list[str]] = []
        self.x_padding: int = 0
        self.fixed_width: int = 0


class Resizer:
    """Determines optimal column widths and row heights for a table.

    Port of: resizer / resize() in table/resizing.go
    """

    def __init__(
        self,
        table_width: int,
        table_height: int,
        headers: list[str],
        rows: list[list[str]],
    ) -> None:
        self.table_width = table_width
        self.table_height = table_height
        self.headers = headers
        if headers:
            self.all_rows: list[list[str]] = [list(headers)] + rows
        else:
            self.all_rows = list(rows)

        self.row_heights: list[int] = []
        self.columns: list[_ResizerColumn] = []
        self.wrap: bool = False
        self.border_column: bool = True
        self.y_paddings: list[list[int]] = []

        # Build per-column statistics.
        for row in self.all_rows:
            for i, cell in enumerate(row):
                cell_len = _visible_width(cell)
                if len(self.columns) <= i:
                    self.columns.append(_ResizerColumn(i, cell_len, cell_len, cell_len))
                    continue
                self.columns[i].rows.append(row)
                self.columns[i].min = min(self.columns[i].min, cell_len)
                self.columns[i].max = max(self.columns[i].max, cell_len)

        # Compute median visible width for each column.
        for j, col in enumerate(self.columns):
            widths = [_visible_width(row[j]) for row in col.rows if j < len(row)]
            col.median = _median(widths)

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------

    def optimized_widths(self) -> tuple[list[int], list[int]]:
        """Return (col_widths, row_heights) using either expand or shrink."""
        if self.table_width <= 0:
            self.table_width = self.detect_table_width()
        if self._max_total() <= self.table_width:
            return self._expand_table_width()
        return self._shrink_table_width()

    def detect_table_width(self) -> int:
        """Detect the natural table width from content."""
        return (
            self._max_char_count()
            + self._total_horizontal_padding()
            + self._total_horizontal_border()
        )

    # ------------------------------------------------------------------
    # Expand / shrink algorithms
    # ------------------------------------------------------------------

    def _expand_table_width(self) -> tuple[list[int], list[int]]:
        col_widths = self._max_column_widths()
        _BIG = 2**31 - 1

        while True:
            total_width = sum(col_widths) + self._total_horizontal_border()
            if total_width >= self.table_width:
                break

            shorter_idx = 0
            shorter_width = _BIG
            for j, w in enumerate(col_widths):
                if w == self.columns[j].fixed_width:
                    continue
                if w < shorter_width:
                    shorter_width = w
                    shorter_idx = j
            col_widths[shorter_idx] += 1

        return col_widths, self._expand_row_heights(col_widths)

    def _shrink_table_width(self) -> tuple[list[int], list[int]]:
        col_widths = self._max_column_widths()

        def shrink_biggest(very_big_only: bool) -> None:
            while True:
                total_width = sum(col_widths) + self._total_horizontal_border()
                if total_width <= self.table_width:
                    break

                big_idx = -1
                big_width = -(2**31)
                for j, w in enumerate(col_widths):
                    if w == self.columns[j].fixed_width:
                        continue
                    if very_big_only:
                        if w >= self.table_width // 2 and w > big_width:
                            big_width = w
                            big_idx = j
                    else:
                        if w > big_width:
                            big_width = w
                            big_idx = j

                if big_idx < 0 or col_widths[big_idx] == 0:
                    break
                col_widths[big_idx] -= 1

        def shrink_to_median() -> None:
            while True:
                total_width = sum(col_widths) + self._total_horizontal_border()
                if total_width <= self.table_width:
                    break

                biggest_diff = -(2**31)
                biggest_diff_idx = -1
                for j, w in enumerate(col_widths):
                    if w == self.columns[j].fixed_width:
                        continue
                    diff = w - self.columns[j].median
                    if diff > 0 and diff > biggest_diff:
                        biggest_diff = diff
                        biggest_diff_idx = j

                if biggest_diff_idx < 0 or col_widths[biggest_diff_idx] == 0:
                    break
                col_widths[biggest_diff_idx] -= 1

        shrink_biggest(True)
        shrink_to_median()
        shrink_biggest(False)

        return col_widths, self._expand_row_heights(col_widths)

    # ------------------------------------------------------------------
    # Row height helpers
    # ------------------------------------------------------------------

    def _expand_row_heights(self, col_widths: list[int]) -> list[int]:
        row_heights = self._default_row_heights()
        if not self.wrap:
            return row_heights
        has_headers = bool(self.headers)

        for i, row in enumerate(self.all_rows):
            for j, cell in enumerate(row):
                if has_headers and i == 0:
                    # Headers are always height 1.
                    continue
                if j >= len(col_widths):
                    continue
                avail = col_widths[j] - self._x_padding_for_col(j)
                h = _word_wrap_height(cell, avail) + self._x_padding_for_cell(i, j)
                if h > row_heights[i]:
                    row_heights[i] = h
        return row_heights

    def _default_row_heights(self) -> list[int]:
        row_heights = []
        for i in range(len(self.all_rows)):
            h = self.row_heights[i] if i < len(self.row_heights) else 0
            row_heights.append(max(h, 1))
        return row_heights

    # ------------------------------------------------------------------
    # Width helpers
    # ------------------------------------------------------------------

    def _max_column_widths(self) -> list[int]:
        result = []
        for col in self.columns:
            if col.fixed_width > 0:
                result.append(col.fixed_width)
            else:
                result.append(col.max + self._x_padding_for_col(col.index))
        return result

    def _max_char_count(self) -> int:
        count = 0
        for col in self.columns:
            if col.fixed_width > 0:
                count += col.fixed_width - self._x_padding_for_col(col.index)
            else:
                count += col.max
        return count

    def _max_total(self) -> int:
        total = 0
        for j, col in enumerate(self.columns):
            if col.fixed_width > 0:
                total += col.fixed_width
            else:
                total += col.max + self._x_padding_for_col(j)
        return total

    def _total_horizontal_padding(self) -> int:
        return sum(col.x_padding for col in self.columns)

    def _x_padding_for_col(self, j: int) -> int:
        if j >= len(self.columns):
            return 0
        return self.columns[j].x_padding

    def _x_padding_for_cell(self, i: int, j: int) -> int:
        if i >= len(self.y_paddings) or j >= len(self.y_paddings[i]):
            return 0
        return self.y_paddings[i][j]

    def _total_horizontal_border(self) -> int:
        return len(self.columns) * self._border_per_cell() + self._extra_border()

    def _border_per_cell(self) -> int:
        return 1 if self.border_column else 0

    def _extra_border(self) -> int:
        return 1 if self.border_column else 0
