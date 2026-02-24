"""
Whitespace rendering with optional styling.

Port of: whitespace.go

Used internally by place_horizontal() and place_vertical() to fill the
empty space around a positioned block. Supports styled whitespace via
WhitespaceOption callables that configure foreground color, background
color, and fill characters.

Public helpers:
  whitespace_foreground(c: TerminalColor) -> WhitespaceOption
  whitespace_background(c: TerminalColor) -> WhitespaceOption
  whitespace_chars(s: str)                -> WhitespaceOption
"""
