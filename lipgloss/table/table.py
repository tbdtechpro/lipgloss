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
  .border_top/bottom/left/right/header/column(v: bool)
  .border_style(s: Style)
  .style_func(fn: Callable[[int, int], Style])
  .render() -> str

HeaderRow sentinel constant: use in style_func to identify the header row (row == HeaderRow).
"""

HeaderRow: int = -1
