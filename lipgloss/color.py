"""
Color types for Lip Gloss.

Port of: color.go
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:
    from .renderer import Renderer


@runtime_checkable
class TerminalColor(Protocol):
    """Protocol satisfied by all color types.

    Implementors resolve themselves to an ANSI color escape string given
    the renderer's current color profile.
    """

    def resolve(self, renderer: "Renderer") -> str:
        """Return the ANSI color escape string for this color."""
        ...


class NoColor:
    """Explicit absence of color.

    When used as a foreground the terminal's default text color is used.
    When used as a background no background color is drawn.
    """

    def resolve(self, renderer: "Renderer") -> str:
        return ""

    def __repr__(self) -> str:
        return "NoColor()"


class Color(str):
    """A color specified by hex value or ANSI index string.

    Examples::

        Color("21")        # ANSI 256 index
        Color("#FF5733")   # true-color hex
    """

    def resolve(self, renderer: "Renderer") -> str:
        return renderer._resolve_color_string(str(self))

    def __repr__(self) -> str:
        return f"Color({str(self)!r})"


class ANSIColor(int):
    """A color in the basic ANSI 0–15 palette.

    Equivalent to ``Color(str(n))`` but more explicit.
    """

    def resolve(self, renderer: "Renderer") -> str:
        return Color(str(int(self))).resolve(renderer)

    def __repr__(self) -> str:
        return f"ANSIColor({int(self)})"


@dataclass
class AdaptiveColor:
    """Selects between two colors based on the terminal's background luminance.

    Example::

        AdaptiveColor(light="236", dark="248")
    """

    light: str
    dark: str

    def resolve(self, renderer: "Renderer") -> str:
        if renderer.has_dark_background():
            return Color(self.dark).resolve(renderer)
        return Color(self.light).resolve(renderer)


@dataclass
class CompleteColor:
    """Explicit color values for each color profile with no automatic degradation.

    Example::

        CompleteColor(true_color="#0000FF", ansi256="86", ansi="5")
    """

    true_color: str
    ansi256: str
    ansi: str

    def resolve(self, renderer: "Renderer") -> str:
        from .renderer import ColorProfile

        profile = renderer.color_profile()
        if profile == ColorProfile.TRUE_COLOR:
            return Color(self.true_color).resolve(renderer)
        if profile == ColorProfile.ANSI256:
            return Color(self.ansi256).resolve(renderer)
        if profile == ColorProfile.ANSI:
            return Color(self.ansi).resolve(renderer)
        return ""


@dataclass
class CompleteAdaptiveColor:
    """Combines explicit per-profile values with light/dark background selection.

    Example::

        CompleteAdaptiveColor(
            light=CompleteColor(true_color="#d7ffae", ansi256="193", ansi="11"),
            dark=CompleteColor(true_color="#d75fee", ansi256="163", ansi="5"),
        )
    """

    light: CompleteColor
    dark: CompleteColor

    def resolve(self, renderer: "Renderer") -> str:
        if renderer.has_dark_background():
            return self.dark.resolve(renderer)
        return self.light.resolve(renderer)
