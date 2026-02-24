"""
Per-character styling.

Port of: runes.go
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .style import Style


def style_runes(
    s: str,
    indices: list[int],
    matched: "Style",
    unmatched: "Style",
) -> str:
    """Apply different styles to individual characters in *s*.

    Characters at positions listed in *indices* are rendered with *matched*;
    all other characters use *unmatched*.

    Full implementation deferred to MVP task 5 (Layout Utilities).
    """
    raise NotImplementedError("style_runes() is not yet implemented (MVP task 5)")
