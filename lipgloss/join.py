"""
Horizontal and vertical block joining.

Port of: join.go

Functions:
  join_horizontal(pos: Position, *strs: str) -> str
      Join text blocks side-by-side. Shorter blocks are padded vertically
      to the height of the tallest block, aligned at `pos`.

  join_vertical(pos: Position, *strs: str) -> str
      Stack text blocks top-to-bottom. Shorter lines are padded horizontally
      to the width of the widest block, aligned at `pos`.

Both functions use ANSI-aware width measurement (see size.py).
"""
