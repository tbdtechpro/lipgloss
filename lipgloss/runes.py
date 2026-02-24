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
    all other characters use *unmatched*.  Out-of-bounds indices are ignored.
    Consecutive characters sharing the same style are flushed as a single
    render call (mirrors the Go implementation).
    """
    index_set = set(indices)
    runes = list(s)
    out: list[str] = []
    group: list[str] = []
    current_matched: bool | None = None

    for i, ch in enumerate(runes):
        is_matched = i in index_set
        if current_matched is None:
            current_matched = is_matched

        next_matched = (i + 1) in index_set
        group.append(ch)

        # Flush when the style changes or we reach the last character.
        if is_matched != next_matched or i == len(runes) - 1:
            style = matched if is_matched else unmatched
            out.append(style.render("".join(group)))
            group = []
            current_matched = None

    return "".join(out)
