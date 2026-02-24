"""
Position type and placement functions.

Port of: position.go
"""

from __future__ import annotations

from typing import Any

from .style import _visible_width
from .whitespace import WhitespaceOption, _Whitespace

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


def _render_whitespace(ws: _Whitespace, width: int, renderer: Any) -> str:
    """Render *width* cells of whitespace with optional ANSI styling."""
    from .style import _extract_sgr_params, _fg_to_bg_escape

    if width <= 0:
        return ""
    chars = ws.chars or " "
    runes = list(chars)
    j = 0
    out: list[str] = []
    i = 0
    while i < width:
        ch = runes[j]
        out.append(ch)
        j = (j + 1) % len(runes)
        # advance by visible width of char (usually 1)
        try:
            from wcwidth import wcwidth  # type: ignore[import]

            cw = wcwidth(ch)
            i += cw if cw > 0 else 1
        except ImportError:
            i += 1
    result = "".join(out)
    # Pad any shortfall with spaces
    short = width - _visible_width(result)
    if short > 0:
        result += " " * short

    # Apply styling
    params: list[str] = []
    if ws.foreground is not None:
        fg_e = ws.foreground.resolve(renderer)
        if fg_e:
            params.extend(_extract_sgr_params(fg_e))
    if ws.background is not None:
        bg_e = ws.background.resolve(renderer)
        if bg_e:
            params.extend(_extract_sgr_params(_fg_to_bg_escape(bg_e)))
    if params:
        result = "\x1b[" + ";".join(params) + "m" + result + "\x1b[0m"
    return result


def place(
    width: int,
    height: int,
    h_pos: Position,
    v_pos: Position,
    s: str,
    *whitespace_opts: WhitespaceOption,
) -> str:
    """Place a string in a box of the given dimensions."""
    return place_vertical(
        height, v_pos, place_horizontal(width, h_pos, s, *whitespace_opts), *whitespace_opts
    )


def place_horizontal(
    width: int,
    pos: Position,
    s: str,
    *whitespace_opts: WhitespaceOption,
) -> str:
    """Place a string horizontally in a space of the given width."""
    from .renderer import default_renderer

    lines = s.split("\n")
    content_width = max((_visible_width(ln) for ln in lines), default=0)
    gap = width - content_width
    if gap <= 0:
        return s

    ws = _Whitespace()
    for opt in whitespace_opts:
        opt(ws)
    renderer = default_renderer()

    pos_clamped = max(0.0, min(1.0, float(pos)))
    result: list[str] = []
    for i, line in enumerate(lines):
        short = max(0, content_width - _visible_width(line))
        total_gap = gap + short
        if pos_clamped == 0.0:  # Left
            result.append(line + _render_whitespace(ws, total_gap, renderer))
        elif pos_clamped == 1.0:  # Right
            result.append(_render_whitespace(ws, total_gap, renderer) + line)
        else:
            split = int(round(total_gap * pos_clamped))
            left_n = total_gap - split
            right_n = total_gap - left_n
            result.append(
                _render_whitespace(ws, left_n, renderer)
                + line
                + _render_whitespace(ws, right_n, renderer)
            )
    return "\n".join(result)


def place_vertical(
    height: int,
    pos: Position,
    s: str,
    *whitespace_opts: WhitespaceOption,
) -> str:
    """Place a string vertically in a space of the given height."""
    from .renderer import default_renderer

    content_height = s.count("\n") + 1
    gap = height - content_height
    if gap <= 0:
        return s

    ws = _Whitespace()
    for opt in whitespace_opts:
        opt(ws)
    renderer = default_renderer()

    lines = s.split("\n")
    w = max((_visible_width(ln) for ln in lines), default=0)
    empty_line = _render_whitespace(ws, w, renderer)

    pos_clamped = max(0.0, min(1.0, float(pos)))
    if pos_clamped == 0.0:  # Top
        return s + "\n" + "\n".join(empty_line for _ in range(gap))
    if pos_clamped == 1.0:  # Bottom
        return "\n".join(empty_line for _ in range(gap)) + "\n" + s
    # Middle
    split = int(round(gap * pos_clamped))
    top = gap - split
    bottom = gap - top
    top_lines = "\n".join(empty_line for _ in range(top))
    bot_lines = "\n".join(empty_line for _ in range(bottom))
    parts = []
    if top_lines:
        parts.append(top_lines)
    parts.append(s)
    if bot_lines:
        parts.append(bot_lines)
    return "\n".join(parts)
