"""
ANSI-aware string measurement.

Port of: size.go
"""

from __future__ import annotations

import re

# Regex that matches ANSI escape sequences (CSI, OSC, and simple escapes).
_ANSI_ESCAPE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def _strip_ansi(s: str) -> str:
    """Remove all ANSI escape sequences from *s*."""
    return _ANSI_ESCAPE.sub("", s)


def _visible_width(line: str) -> int:
    """Return the visible cell width of a single line using wcwidth."""
    try:
        from wcwidth import wcswidth  # type: ignore[import]

        w = wcswidth(_strip_ansi(line))
        return w if w >= 0 else len(_strip_ansi(line))
    except ImportError:
        return len(_strip_ansi(line))


def width(s: str) -> int:
    """Return the visible width of the widest line in *s*."""
    return max((_visible_width(line) for line in s.split("\n")), default=0)


def height(s: str) -> int:
    """Return the number of lines in *s*."""
    return s.count("\n") + 1


def size(s: str) -> tuple[int, int]:
    """Return ``(width, height)`` of *s*."""
    return width(s), height(s)
