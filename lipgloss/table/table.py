"""
Table — renders tabular data with borders and per-cell styling.

Port of: table/table.go

Key API (all setters return self for chaining):
  Table()
  .headers(*cols: str)
  .rows(*rows: list[str])
  .row(*cols: str)
  .width(n: int)
  .height(n: int)
  .offset(n: int)
  .border(b: Border)
  .border_top/bottom/left/right/header/column/row(v: bool)
  .border_style(s: Style)
  .style_func(fn: Callable[[int, int], Style])
  .render() -> str

HeaderRow sentinel constant: use in style_func to identify the header row (row == HeaderRow).
"""
from __future__ import annotations

from typing import Callable

from ..borders import Border, rounded_border
from ..join import join_horizontal
from ..position import Top
from ..size import height as _lipgloss_height
from ..style import Style
from .resizing import Resizer
from .rows import Data, StringData, data_to_matrix

HeaderRow: int = -1


def _default_styles(row: int, col: int) -> Style:
    return Style()


def _btoi(b: bool) -> int:
    return 1 if b else 0


class Table:
    """Renders tabular data with configurable borders, styles, and sizing.

    Port of: Table in table/table.go
    """

    def __init__(self) -> None:
        self._style_func: Callable[[int, int], Style] = _default_styles
        self._border: Border = rounded_border()
        self._border_top: bool = True
        self._border_bottom: bool = True
        self._border_left: bool = True
        self._border_right: bool = True
        self._border_header: bool = True
        self._border_column: bool = True
        self._border_row: bool = False
        self._border_style: Style = Style()
        self._headers: list[str] = []
        self._data: Data = StringData()
        self._width: int = 0
        self._height: int = 0
        self._use_manual_height: bool = False
        self._offset: int = 0
        self._wrap: bool = True
        self._widths: list[int] = []
        self._heights: list[int] = []

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def style_func(self, fn: Callable[[int, int], Style]) -> "Table":
        self._style_func = fn
        return self

    def data(self, data: Data) -> "Table":
        self._data = data
        return self

    def rows(self, *rows: list[str]) -> "Table":
        if isinstance(self._data, StringData):
            for row in rows:
                self._data.append(list(row))
        return self

    def row(self, *cols: str) -> "Table":
        if isinstance(self._data, StringData):
            self._data.append(list(cols))
        return self

    def headers(self, *cols: str) -> "Table":
        self._headers = list(cols)
        return self

    def border(self, b: Border) -> "Table":
        self._border = b
        return self

    def border_top(self, v: bool) -> "Table":
        self._border_top = v
        return self

    def border_bottom(self, v: bool) -> "Table":
        self._border_bottom = v
        return self

    def border_left(self, v: bool) -> "Table":
        self._border_left = v
        return self

    def border_right(self, v: bool) -> "Table":
        self._border_right = v
        return self

    def border_header(self, v: bool) -> "Table":
        self._border_header = v
        return self

    def border_column(self, v: bool) -> "Table":
        self._border_column = v
        return self

    def border_row(self, v: bool) -> "Table":
        self._border_row = v
        return self

    def border_style(self, s: Style) -> "Table":
        self._border_style = s
        return self

    def width(self, w: int) -> "Table":
        self._width = w
        return self

    def height(self, h: int) -> "Table":
        self._height = h
        self._use_manual_height = True
        return self

    def offset(self, o: int) -> "Table":
        self._offset = o
        return self

    def wrap(self, w: bool) -> "Table":
        self._wrap = w
        return self

    def clear_rows(self) -> "Table":
        self._data = StringData()
        return self

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_style(self, row: int, col: int) -> Style:
        if self._style_func is None:
            return Style()
        return self._style_func(row, col)

    def _resize(self) -> None:
        has_headers = bool(self._headers)
        rows = data_to_matrix(self._data)
        r = Resizer(self._width, self._height, self._headers, rows)
        r.wrap = self._wrap
        r.border_column = self._border_column
        r.y_paddings = [[] for _ in r.all_rows]

        all_rows: list[list[str]] = []
        if has_headers:
            all_rows = [list(self._headers)] + rows
        else:
            all_rows = rows

        r.row_heights = r._default_row_heights()

        for i, row in enumerate(all_rows):
            r.y_paddings[i] = [0] * len(row)
            for j in range(len(row)):
                if j >= len(r.columns):
                    continue
                col = r.columns[j]
                row_index = i - _btoi(has_headers)
                s = self._get_style(row_index, j)

                total_h_padding = (
                    s.get_margin_left()
                    + s.get_margin_right()
                    + s.get_padding_left()
                    + s.get_padding_right()
                )
                col.x_padding = max(col.x_padding, total_h_padding)
                col.fixed_width = max(col.fixed_width, s.get_width())

                r.row_heights[i] = max(r.row_heights[i], s.get_height())

                total_v_padding = (
                    s.get_margin_top()
                    + s.get_margin_bottom()
                    + s.get_padding_top()
                    + s.get_padding_bottom()
                )
                r.y_paddings[i][j] = total_v_padding

        self._widths, self._heights = r.optimized_widths()

    # ------------------------------------------------------------------
    # Border construction
    # ------------------------------------------------------------------

    def _construct_top_border(self) -> str:
        parts: list[str] = []
        if self._border_left:
            parts.append(self._border_style.render(self._border.top_left))
        for i, w in enumerate(self._widths):
            parts.append(self._border_style.render(self._border.top * w))
            if i < len(self._widths) - 1 and self._border_column:
                parts.append(self._border_style.render(self._border.middle_top))
        if self._border_right:
            parts.append(self._border_style.render(self._border.top_right))
        return "".join(parts)

    def _construct_bottom_border(self) -> str:
        parts: list[str] = []
        if self._border_left:
            parts.append(self._border_style.render(self._border.bottom_left))
        for i, w in enumerate(self._widths):
            parts.append(self._border_style.render(self._border.bottom * w))
            if i < len(self._widths) - 1 and self._border_column:
                parts.append(self._border_style.render(self._border.middle_bottom))
        if self._border_right:
            parts.append(self._border_style.render(self._border.bottom_right))
        return "".join(parts)

    def _construct_headers(self) -> str:
        height = self._heights[HeaderRow + 1]
        parts: list[str] = []
        if self._border_left:
            parts.append(self._border_style.render(self._border.left))
        for i, header in enumerate(self._headers):
            cell_style = self._get_style(HeaderRow, i)
            h_margins = cell_style.get_margin_left() + cell_style.get_margin_right()
            v_margins = cell_style.get_margin_top() + cell_style.get_margin_bottom()
            parts.append(
                cell_style.height(height - v_margins)
                .max_height(height)
                .width(self._widths[i] - h_margins)
                .max_width(self._widths[i])
                .render(header)
            )
            if i < len(self._headers) - 1 and self._border_column:
                parts.append(self._border_style.render(self._border.left))

        if self._border_header:
            if self._border_right:
                parts.append(self._border_style.render(self._border.right))
            parts.append("\n")
            if self._border_left:
                parts.append(self._border_style.render(self._border.middle_left))
            for i in range(len(self._headers)):
                parts.append(self._border_style.render(self._border.top * self._widths[i]))
                if i < len(self._headers) - 1 and self._border_column:
                    parts.append(self._border_style.render(self._border.middle))
            if self._border_right:
                parts.append(self._border_style.render(self._border.middle_right))
        elif self._border_right:
            parts.append(self._border_style.render(self._border.right))

        return "".join(parts)

    def _construct_row(self, index: int, is_overflow: bool) -> str:
        has_headers = bool(self._headers)
        height = self._heights[index + _btoi(has_headers)]
        if is_overflow:
            height = 1

        cells: list[str] = []
        left_border = (self._border_style.render(self._border.left) + "\n") * height
        if self._border_left:
            cells.append(left_border)

        for c in range(self._data.columns()):
            cell = "…" if is_overflow else self._data.at(index, c)
            cell_style = self._get_style(index, c)
            h_margins = cell_style.get_margin_left() + cell_style.get_margin_right()
            v_margins = cell_style.get_margin_top() + cell_style.get_margin_bottom()
            cells.append(
                cell_style.height(height - v_margins)
                .max_height(height)
                .width(self._widths[c] - h_margins)
                .max_width(self._widths[c])
                .render(cell)
            )
            if c < self._data.columns() - 1 and self._border_column:
                cells.append(left_border)

        if self._border_right:
            right_border = (self._border_style.render(self._border.right) + "\n") * height
            cells.append(right_border)

        cells = [c.rstrip("\n") for c in cells]
        result = join_horizontal(Top, *cells) + "\n"

        if self._border_row and index < self._data.rows() - 1 and not is_overflow:
            row_parts: list[str] = []
            row_parts.append(self._border_style.render(self._border.middle_left))
            for i, w in enumerate(self._widths):
                row_parts.append(self._border_style.render(self._border.bottom * w))
                if i < len(self._widths) - 1 and self._border_column:
                    row_parts.append(self._border_style.render(self._border.middle))
            row_parts.append(self._border_style.render(self._border.middle_right))
            result += "".join(row_parts) + "\n"

        return result

    def _construct_rows(self, available_lines: int) -> str:
        parts: list[str] = []
        offset_row_count = self._data.rows() - self._offset
        rows_to_render = max(available_lines, 1)
        needs_overflow = rows_to_render < offset_row_count

        row_idx = self._offset
        if not needs_overflow:
            row_idx = self._data.rows() - rows_to_render

        while rows_to_render > 0 and row_idx < self._data.rows():
            is_overflow = needs_overflow and rows_to_render == 1
            parts.append(self._construct_row(row_idx, is_overflow))
            row_idx += 1
            rows_to_render -= 1

        return "".join(parts)

    def _compute_height(self) -> int:
        has_headers = bool(self._headers)
        return (
            sum(self._heights)
            - 1
            + _btoi(has_headers)
            + _btoi(self._border_top)
            + _btoi(self._border_bottom)
            + _btoi(self._border_header)
            + self._data.rows() * _btoi(self._border_row)
        )

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> str:
        return str(self)

    def __str__(self) -> str:
        has_headers = bool(self._headers)
        has_rows = self._data is not None and self._data.rows() > 0

        if not has_headers and not has_rows:
            return ""

        # Pad headers to match column count.
        if has_headers:
            while len(self._headers) < self._data.columns():
                self._headers.append("")

        self._resize()

        parts: list[str] = []

        if self._border_top:
            parts.append(self._construct_top_border())
            parts.append("\n")

        if has_headers:
            parts.append(self._construct_headers())
            parts.append("\n")

        bottom = ""
        if self._border_bottom:
            bottom = self._construct_bottom_border()

        if self._data.rows() > 0:
            if self._use_manual_height:
                top_height = _lipgloss_height("".join(parts)) - 1
                available_lines = self._height - (top_height + _lipgloss_height(bottom))
                if available_lines > self._data.rows():
                    available_lines = self._data.rows()
                parts.append(self._construct_rows(available_lines))
            else:
                for r in range(self._offset, self._data.rows()):
                    parts.append(self._construct_row(r, False))

        parts.append(bottom)
        result = "".join(parts)

        # Apply max constraints (width=0 means no limit, matching Go behaviour).
        s = Style().max_height(self._compute_height())
        if self._width > 0:
            s = s.max_width(self._width)
        return s.render(result)
