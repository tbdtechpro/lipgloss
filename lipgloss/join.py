"""
Horizontal and vertical block joining.

Port of: join.go
"""

from __future__ import annotations

from .position import Position


def join_horizontal(pos: Position, *strs: str) -> str:
    """Join text blocks side-by-side along a vertical axis.

    ``pos`` controls vertical alignment of shorter blocks relative to the
    tallest (0.0 = top, 0.5 = center, 1.0 = bottom).

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("join_horizontal() is not yet implemented (MVP task 5)")


def join_vertical(pos: Position, *strs: str) -> str:
    """Stack text blocks top-to-bottom along a horizontal axis.

    ``pos`` controls horizontal alignment of narrower lines relative to the
    widest (0.0 = left, 0.5 = center, 1.0 = right).

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("join_vertical() is not yet implemented (MVP task 5)")
