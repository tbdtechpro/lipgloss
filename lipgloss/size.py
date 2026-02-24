"""
ANSI-aware string measurement.

Port of: size.go

Functions:
  width(s: str)  -> int          Width of the widest line (ANSI-stripped).
  height(s: str) -> int          Number of lines.
  size(s: str)   -> (int, int)   (width, height) shorthand.

All functions strip ANSI escape codes before measuring so that styled
strings return their visible cell width rather than their byte length.
Uses wcwidth for Unicode double-wide character support.
"""
