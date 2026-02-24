"""
Position type and placement functions.

Port of: position.go
"""

from __future__ import annotations

from typing import Any

# Position is a float in [0.0, 1.0]:
#   0.0 = left / top
#   0.5 = center
#   1.0 = right / bottom
Position = float

Top: Position = 0.0
Bottom: Position = 1.0
Left: Position = 0.0
Right: Position = 1.0
Center: Position = 0.5


def place(
    width: int,
    height: int,
    h_pos: Position,
    v_pos: Position,
    s: str,
    **whitespace_opts: Any,
) -> str:
    """Place a string in a box of the given dimensions.

    ``h_pos`` controls horizontal alignment; ``v_pos`` controls vertical.
    ``whitespace_opts`` are forwarded to the whitespace renderer (foreground,
    background, chars).

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("place() is not yet implemented (MVP task 5)")


def place_horizontal(
    width: int,
    pos: Position,
    s: str,
    **whitespace_opts: Any,
) -> str:
    """Place a string horizontally in a space of the given width.

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("place_horizontal() is not yet implemented (MVP task 5)")


def place_vertical(
    height: int,
    pos: Position,
    s: str,
    **whitespace_opts: Any,
) -> str:
    """Place a string vertically in a space of the given height.

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("place_vertical() is not yet implemented (MVP task 5)")
