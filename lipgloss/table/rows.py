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
