"""
Whitespace rendering with optional styling.

Port of: whitespace.go
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Callable

if TYPE_CHECKING:
    from .color import TerminalColor

# A WhitespaceOption is a callable that mutates a _Whitespace config object.
# The concrete type is an internal detail; callers only interact with the
# factory functions below.
WhitespaceOption = Callable[["_Whitespace"], None]


class _Whitespace:
    """Internal configuration object built up by WhitespaceOption callables."""

    def __init__(self) -> None:
        self.foreground: TerminalColor | None = None
        self.background: TerminalColor | None = None
        self.chars: str = " "


def whitespace_foreground(c: "TerminalColor") -> WhitespaceOption:
    """Return a WhitespaceOption that sets the foreground color of filler."""

    def _apply(ws: _Whitespace) -> None:
        ws.foreground = c

    return _apply


def whitespace_background(c: "TerminalColor") -> WhitespaceOption:
    """Return a WhitespaceOption that sets the background color of filler."""

    def _apply(ws: _Whitespace) -> None:
        ws.background = c

    return _apply


def whitespace_chars(s: str) -> WhitespaceOption:
    """Return a WhitespaceOption that sets the fill character(s)."""

    def _apply(ws: _Whitespace) -> None:
        ws.chars = s

    return _apply
