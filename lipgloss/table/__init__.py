"""
Table rendering sub-package.

Port of: table/table.go, table/rows.go, table/resizing.go

Usage::

    from lipgloss import table

    t = (
        table.Table()
        .headers("Language", "Formal", "Informal")
        .rows(
            ["Chinese", "您好", "你好"],
            ["Japanese", "こんにちは", "やあ"],
        )
    )
    print(t.render())
"""

from .rows import Data, Filter, StringData, data_to_matrix
from .table import HeaderRow, Table

__all__ = [
    "Data",
    "Filter",
    "HeaderRow",
    "StringData",
    "Table",
    "data_to_matrix",
]
