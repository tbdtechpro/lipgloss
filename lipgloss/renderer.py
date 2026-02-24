"""
Renderer — terminal output handler and color profile detector.

Port of: renderer.go
"""

from __future__ import annotations

import os
import sys
from enum import Enum, auto
from functools import cached_property
from typing import IO, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .style import Style


class ColorProfile(Enum):
    """Terminal color capability levels, highest to lowest."""

    TRUE_COLOR = auto()
    ANSI256 = auto()
    ANSI = auto()
    ASCII = auto()


class Renderer:
    """Terminal output handler that detects color capabilities.

    Wraps an output writer and lazily detects the color profile and
    background luminance of the attached terminal.
    """

    def __init__(self, output: IO[str] = sys.stdout) -> None:
        self._output = output
        # Cached detection results; set to None to force re-detection.
        self._color_profile: ColorProfile | None = None
        self._has_dark_background: bool | None = None

    def color_profile(self) -> ColorProfile:
        """Return the detected color profile, detecting lazily on first call."""
        if self._color_profile is None:
            self._color_profile = self._detect_color_profile()
        return self._color_profile

    def set_color_profile(self, profile: ColorProfile) -> None:
        """Override the detected color profile."""
        self._color_profile = profile

    def has_dark_background(self) -> bool:
        """Return True if the terminal background is dark."""
        if self._has_dark_background is None:
            self._has_dark_background = self._detect_dark_background()
        return self._has_dark_background

    def set_dark_background(self, dark: bool) -> None:
        """Override the detected background luminance."""
        self._has_dark_background = dark

    def new_style(self) -> "Style":
        """Return a new Style bound to this renderer."""
        from .style import Style

        return Style(_renderer=self)

    # ------------------------------------------------------------------
    # Internal helpers (not part of public API)
    # ------------------------------------------------------------------

    def _detect_color_profile(self) -> ColorProfile:
        """Detect terminal color capability from environment variables."""
        if os.environ.get("NO_COLOR"):
            return ColorProfile.ASCII

        colorterm = os.environ.get("COLORTERM", "").lower()
        if colorterm in ("truecolor", "24bit"):
            return ColorProfile.TRUE_COLOR

        term = os.environ.get("TERM", "")
        term_program = os.environ.get("TERM_PROGRAM", "").lower()

        if "256color" in term or term_program in ("iterm.app", "hyper"):
            return ColorProfile.ANSI256

        if term in ("xterm", "screen", "vt100", "rxvt") or term.startswith("xterm-"):
            return ColorProfile.ANSI

        if hasattr(self._output, "isatty") and not self._output.isatty():
            return ColorProfile.ASCII

        return ColorProfile.ANSI256

    def _detect_dark_background(self) -> bool:
        """Assume dark background (safe default for most terminals)."""
        return True

    def _resolve_color_string(self, color_str: str) -> str:
        """Resolve a hex or ANSI index color string to an ANSI escape fragment.

        Returns an empty string for the ASCII profile (no color output).
        Implementation detail used by Color.resolve().
        """
        # Full implementation deferred to MVP task 2.2.
        raise NotImplementedError(
            "_resolve_color_string is not yet implemented (MVP task 2.2)"
        )


# ---------------------------------------------------------------------------
# Module-level singleton and helpers (mirrors Go's package-level functions)
# ---------------------------------------------------------------------------

_default_renderer = Renderer(sys.stdout)


def default_renderer() -> Renderer:
    """Return the global default renderer."""
    return _default_renderer


def set_default_renderer(r: Renderer) -> None:
    """Replace the global default renderer."""
    global _default_renderer
    _default_renderer = r


def new_renderer(output: IO[str]) -> Renderer:
    """Create a new Renderer writing to the given output stream."""
    return Renderer(output)
