"""
Column width distribution algorithm.

Port of: table/resizing.go

Distributes available table width across columns using a flex-sizing
algorithm: columns are first given their minimum content width, then
remaining space is distributed proportionally. Respects a fixed
table-level width constraint when set.

Internal function used by Table.render(); not part of the public API.
"""
