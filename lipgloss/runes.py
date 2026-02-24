"""
Per-character styling.

Port of: runes.go

Functions:
  style_runes(s: str, indices: list[int], matched: Style, unmatched: Style) -> str
      Apply `matched` style to characters at the given `indices` and
      `unmatched` style to all other characters. Returns the composed
      ANSI string.
"""
