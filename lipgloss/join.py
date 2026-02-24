"""
Horizontal and vertical block joining.

Port of: join.go
"""

from __future__ import annotations

from .position import Position
from .style import _visible_width


def join_horizontal(pos: Position, *strs: str) -> str:
    """Join text blocks side-by-side along a vertical axis.

    ``pos`` controls vertical alignment of shorter blocks relative to the
    tallest (0.0 = top, 0.5 = center, 1.0 = bottom).
    """
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]

    blocks = [s.split("\n") for s in strs]
    max_widths = [max((_visible_width(line) for line in b), default=0) for b in blocks]
    max_height = max(len(b) for b in blocks)

    pos_clamped = max(0.0, min(1.0, float(pos)))

    # Pad each block to max_height
    for i, block in enumerate(blocks):
        if len(block) >= max_height:
            continue
        extra = max_height - len(block)
        if pos_clamped == 0.0:  # Top — append empty lines below
            blocks[i] = block + [""] * extra
        elif pos_clamped == 1.0:  # Bottom — prepend empty lines above
            blocks[i] = [""] * extra + block
        else:
            split = int(round(extra * pos_clamped))
            top = extra - split
            bottom = extra - top
            blocks[i] = [""] * top + block + [""] * bottom

    lines: list[str] = []
    for row in range(max_height):
        parts: list[str] = []
        for j, block in enumerate(blocks):
            line = block[row]
            pad = max_widths[j] - _visible_width(line)
            parts.append(line + " " * pad)
        lines.append("".join(parts))
    return "\n".join(lines)


def join_vertical(pos: Position, *strs: str) -> str:
    """Stack text blocks top-to-bottom along a horizontal axis.

    ``pos`` controls horizontal alignment of narrower lines relative to the
    widest (0.0 = left, 0.5 = center, 1.0 = right).
    """
    if not strs:
        return ""
    if len(strs) == 1:
        return strs[0]

    blocks = [s.split("\n") for s in strs]
    max_w = max(
        (_visible_width(line) for block in blocks for line in block),
        default=0,
    )

    pos_clamped = max(0.0, min(1.0, float(pos)))

    all_lines: list[str] = []
    for bi, block in enumerate(blocks):
        for li, line in enumerate(block):
            w = max_w - _visible_width(line)
            if pos_clamped == 0.0:
                all_lines.append(line + " " * w)
            elif pos_clamped == 1.0:
                all_lines.append(" " * w + line)
            else:
                if w < 1:
                    all_lines.append(line)
                else:
                    split = int(round(w * pos_clamped))
                    right = w - split
                    left = w - right
                    all_lines.append(" " * left + line + " " * right)
    return "\n".join(all_lines)
