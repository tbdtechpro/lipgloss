"""
Table data source abstractions.

Port of: table/rows.go

Classes:
  StringData(*rows)         — wraps a list-of-lists as a table data source.
  Filter(data, predicate)   — wraps any data source with a row-filter function.

Both implement the same protocol:
  .at(row: int, col: int) -> str
  .rows() -> int
  .columns() -> int
"""
from __future__ import annotations

from typing import Callable, Protocol, runtime_checkable


@runtime_checkable
class Data(Protocol):
    """Protocol for table data sources."""

    def at(self, row: int, col: int) -> str:
        """Return the cell value at (row, col)."""
        ...

    def rows(self) -> int:
        """Return the number of rows."""
        ...

    def columns(self) -> int:
        """Return the number of columns."""
        ...


class StringData:
    """String-based implementation of the Data protocol.

    Port of: StringData in table/rows.go
    """

    def __init__(self, *rows: list[str]) -> None:
        self._rows: list[list[str]] = []
        self._columns: int = 0
        for row in rows:
            self.append(list(row))

    def append(self, row: list[str]) -> None:
        """Append a row to the data."""
        self._columns = max(self._columns, len(row))
        self._rows.append(list(row))

    def item(self, *cells: str) -> "StringData":
        """Append a row given as individual cell arguments."""
        self.append(list(cells))
        return self

    def at(self, row: int, col: int) -> str:
        if row >= len(self._rows) or col >= len(self._rows[row]):
            return ""
        return self._rows[row][col]

    def rows(self) -> int:
        return len(self._rows)

    def columns(self) -> int:
        return self._columns


class Filter:
    """Wraps any Data source with a row-filter predicate.

    Port of: Filter in table/rows.go
    """

    def __init__(
        self,
        data: Data,
        predicate: Callable[[int], bool] | None = None,
    ) -> None:
        self._data = data
        self._predicate: Callable[[int], bool] = predicate if predicate is not None else (lambda _: True)

    def filter(self, predicate: Callable[[int], bool]) -> "Filter":
        """Set the filter predicate."""
        self._predicate = predicate
        return self

    def at(self, row: int, col: int) -> str:
        j = 0
        for i in range(self._data.rows()):
            if self._predicate(i):
                if j == row:
                    return self._data.at(i, col)
                j += 1
        return ""

    def rows(self) -> int:
        return sum(1 for i in range(self._data.rows()) if self._predicate(i))

    def columns(self) -> int:
        return self._data.columns()


def data_to_matrix(data: Data) -> list[list[str]]:
    """Convert any Data source to a list-of-lists."""
    num_rows = data.rows()
    num_cols = data.columns()
    return [[data.at(i, j) for j in range(num_cols)] for i in range(num_rows)]
