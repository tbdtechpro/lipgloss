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
        profile = self.color_profile()
        if profile == ColorProfile.ASCII:
            return ""

        color_str = color_str.strip()

        if color_str.startswith("#"):
            # True-color hex: #RRGGBB
            hex_val = color_str.lstrip("#")
            if len(hex_val) == 6:
                r = int(hex_val[0:2], 16)
                g = int(hex_val[2:4], 16)
                b = int(hex_val[4:6], 16)
                if profile == ColorProfile.TRUE_COLOR:
                    return f"\x1b[38;2;{r};{g};{b}m"
                # Degrade to ANSI256
                idx = _rgb_to_ansi256(r, g, b)
                if profile == ColorProfile.ANSI256:
                    return f"\x1b[38;5;{idx}m"
                # Degrade to ANSI16
                ansi16 = _ansi256_to_ansi16(idx)
                return _ansi16_fg_escape(ansi16)
            return ""

        # Numeric ANSI index string
        try:
            idx = int(color_str)
        except ValueError:
            return ""

        if idx < 0:
            return ""

        if idx < 16:
            # Basic ANSI color (0–15)
            return _ansi16_fg_escape(idx)

        if profile == ColorProfile.ANSI:
            # Degrade 256-color index to nearest ANSI16
            return _ansi16_fg_escape(_ansi256_to_ansi16(idx))

        # ANSI256 or TRUE_COLOR: emit 256-color escape
        return f"\x1b[38;5;{idx}m"


# ---------------------------------------------------------------------------
# Color-conversion helpers
# ---------------------------------------------------------------------------


def _ansi16_fg_escape(idx: int) -> str:
    """Return the ANSI escape for a basic 0–15 foreground color."""
    if idx < 8:
        return f"\x1b[{30 + idx}m"
    return f"\x1b[{90 + idx - 8}m"


def _rgb_to_ansi256(r: int, g: int, b: int) -> int:
    """Convert an RGB triplet to the nearest xterm-256 palette index."""
    # Grayscale ramp (232–255)
    if r == g == b:
        if r < 8:
            return 16
        if r > 248:
            return 231
        return round((r - 8) / 247 * 24) + 232
    # 6x6x6 colour cube (16–231)
    return 16 + 36 * round(r / 255 * 5) + 6 * round(g / 255 * 5) + round(b / 255 * 5)


# Approximate mapping from xterm-256 index to ANSI-16 index used when
# degrading to a 4-bit terminal.  The 16 basic colours map to themselves;
# the colour-cube and grayscale entries are mapped to the nearest of the
# 8 standard colours (0–7) by comparing perceived brightness.
def _ansi256_to_ansi16(idx: int) -> int:
    """Map an xterm-256 colour index to the nearest ANSI-16 index (0–15)."""
    if idx < 16:
        return idx
    if idx >= 232:
        # Grayscale ramp — map to black, dark-gray, light-gray or white
        level = idx - 232  # 0–23
        if level < 6:
            return 0  # black
        if level < 12:
            return 8  # dark gray (bright black)
        if level < 18:
            return 7  # light gray
        return 15  # white
    # Colour cube: convert cube indices back to approximate RGB
    idx -= 16
    b_i = idx % 6
    g_i = (idx // 6) % 6
    r_i = idx // 36
    r = r_i * 51
    g = g_i * 51
    b = b_i * 51
    # Pick nearest of 8 basic colours by hue/brightness heuristic
    bright = (r + g + b) > 382  # roughly above mid-point → use bright variant
    if r > g and r > b:
        return 9 if bright else 1  # red
    if g > r and g > b:
        return 10 if bright else 2  # green
    if b > r and b > g:
        return 12 if bright else 4  # blue
    if r > b and g > b:
        return 11 if bright else 3  # yellow
    if r > g and b > g:
        return 13 if bright else 5  # magenta
    if g > r and b > r:
        return 14 if bright else 6  # cyan
    return 15 if bright else 0  # white / black


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
