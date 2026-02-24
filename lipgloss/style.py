"""
Style — the core styling primitive.

Port of: style.go, set.go, get.go, unset.go
"""

from __future__ import annotations

from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from .borders import Border
    from .color import TerminalColor
    from .position import Position
    from .renderer import Renderer


class Style:
    """An immutable fluent builder for terminal styles.

    Every setter returns a *new* Style; the receiver is never mutated.
    Properties are tracked by key presence in an internal dict, mirroring
    Go's propKey bit-flag approach.

    Example::

        style = (
            Style()
            .bold(True)
            .foreground(Color("#FAFAFA"))
            .background(Color("#7D56F4"))
            .padding(2, 4)
            .width(22)
        )
        print(style.render("Hello, kitty"))
    """

    def __init__(self, _renderer: "Renderer | None" = None) -> None:
        from .renderer import default_renderer

        self._renderer: Renderer = _renderer or default_renderer()
        self._props: dict[str, Any] = {}
        self._value: str = ""  # attached string set via set_string()

    # ------------------------------------------------------------------
    # Core rendering
    # ------------------------------------------------------------------

    def render(self, *strings: str) -> str:
        """Apply all set properties and return an ANSI-escaped string.

        If *strings* are provided they are joined with a space and rendered.
        If no *strings* are provided the attached string from set_string()
        is used.

        Full implementation deferred to MVP task 3 (Core Style System).
        """
        raise NotImplementedError("Style.render() is not yet implemented (MVP task 3)")

    def __str__(self) -> str:
        return self.render()

    # ------------------------------------------------------------------
    # Copy, inherit, set_string
    # ------------------------------------------------------------------

    def copy(self) -> "Style":
        """Return an independent copy of this style."""
        s = Style(_renderer=self._renderer)
        s._props = deepcopy(self._props)
        s._value = self._value
        return s

    def inherit(self, parent: "Style") -> "Style":
        """Copy unset properties from *parent*.

        Properties already set on this style are not overridden.
        """
        s = self.copy()
        for key, value in parent._props.items():
            if key not in s._props:
                s._props[key] = deepcopy(value)
        return s

    def set_string(self, *strings: str) -> "Style":
        """Attach strings so that render() / str() work without arguments."""
        s = self.copy()
        s._value = " ".join(strings)
        return s

    def get_value(self) -> str:
        """Return the string attached via set_string()."""
        return self._value

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _set(self, key: str, value: Any) -> "Style":
        """Return a copy of this style with *key* set to *value*."""
        s = self.copy()
        s._props[key] = value
        return s

    def _unset(self, key: str) -> "Style":
        """Return a copy of this style with *key* removed."""
        s = self.copy()
        s._props.pop(key, None)
        return s

    def _get(self, key: str, default: Any = None) -> Any:
        """Return the value for *key*, or *default* if not set."""
        return self._props.get(key, default)

    def _is_set(self, key: str) -> bool:
        """Return True if *key* has been explicitly set."""
        return key in self._props

    # ------------------------------------------------------------------
    # Boolean inline-formatting setters / getters / unsetters
    # ------------------------------------------------------------------

    def bold(self, v: bool = True) -> "Style":
        """Set bold text."""
        return self._set("bold", v)

    def get_bold(self) -> bool:
        return self._get("bold", False)

    def unset_bold(self) -> "Style":
        return self._unset("bold")

    def italic(self, v: bool = True) -> "Style":
        """Set italic text."""
        return self._set("italic", v)

    def get_italic(self) -> bool:
        return self._get("italic", False)

    def unset_italic(self) -> "Style":
        return self._unset("italic")

    def underline(self, v: bool = True) -> "Style":
        """Set underlined text."""
        return self._set("underline", v)

    def get_underline(self) -> bool:
        return self._get("underline", False)

    def unset_underline(self) -> "Style":
        return self._unset("underline")

    def strikethrough(self, v: bool = True) -> "Style":
        """Set strikethrough text."""
        return self._set("strikethrough", v)

    def get_strikethrough(self) -> bool:
        return self._get("strikethrough", False)

    def unset_strikethrough(self) -> "Style":
        return self._unset("strikethrough")

    def reverse(self, v: bool = True) -> "Style":
        """Swap foreground and background colors."""
        return self._set("reverse", v)

    def get_reverse(self) -> bool:
        return self._get("reverse", False)

    def unset_reverse(self) -> "Style":
        return self._unset("reverse")

    def blink(self, v: bool = True) -> "Style":
        """Set blinking text."""
        return self._set("blink", v)

    def get_blink(self) -> bool:
        return self._get("blink", False)

    def unset_blink(self) -> "Style":
        return self._unset("blink")

    def faint(self, v: bool = True) -> "Style":
        """Dim / faint text."""
        return self._set("faint", v)

    def get_faint(self) -> bool:
        return self._get("faint", False)

    def unset_faint(self) -> "Style":
        return self._unset("faint")

    def underline_spaces(self, v: bool = True) -> "Style":
        """Underline spaces between words."""
        return self._set("underline_spaces", v)

    def get_underline_spaces(self) -> bool:
        return self._get("underline_spaces", False)

    def unset_underline_spaces(self) -> "Style":
        return self._unset("underline_spaces")

    def strikethrough_spaces(self, v: bool = True) -> "Style":
        """Apply strikethrough to spaces between words."""
        return self._set("strikethrough_spaces", v)

    def get_strikethrough_spaces(self) -> bool:
        return self._get("strikethrough_spaces", False)

    def unset_strikethrough_spaces(self) -> "Style":
        return self._unset("strikethrough_spaces")

    def color_whitespace(self, v: bool = True) -> "Style":
        """Apply foreground / background colors to whitespace characters."""
        return self._set("color_whitespace", v)

    def get_color_whitespace(self) -> bool:
        return self._get("color_whitespace", True)

    def unset_color_whitespace(self) -> "Style":
        return self._unset("color_whitespace")

    # ------------------------------------------------------------------
    # Color setters / getters / unsetters
    # ------------------------------------------------------------------

    def foreground(self, c: "TerminalColor") -> "Style":
        """Set the foreground color."""
        return self._set("foreground", c)

    def get_foreground(self) -> "TerminalColor | None":
        return self._get("foreground")

    def unset_foreground(self) -> "Style":
        return self._unset("foreground")

    def background(self, c: "TerminalColor") -> "Style":
        """Set the background color."""
        return self._set("background", c)

    def get_background(self) -> "TerminalColor | None":
        return self._get("background")

    def unset_background(self) -> "Style":
        return self._unset("background")

    # ------------------------------------------------------------------
    # Dimension setters / getters / unsetters
    # ------------------------------------------------------------------

    def width(self, n: int) -> "Style":
        """Set minimum width."""
        return self._set("width", n)

    def get_width(self) -> int:
        return self._get("width", 0)

    def unset_width(self) -> "Style":
        return self._unset("width")

    def height(self, n: int) -> "Style":
        """Set minimum height."""
        return self._set("height", n)

    def get_height(self) -> int:
        return self._get("height", 0)

    def unset_height(self) -> "Style":
        return self._unset("height")

    def max_width(self, n: int) -> "Style":
        """Set maximum width; content is truncated beyond this."""
        return self._set("max_width", n)

    def get_max_width(self) -> int:
        return self._get("max_width", 0)

    def unset_max_width(self) -> "Style":
        return self._unset("max_width")

    def max_height(self, n: int) -> "Style":
        """Set maximum height; content is truncated beyond this."""
        return self._set("max_height", n)

    def get_max_height(self) -> int:
        return self._get("max_height", 0)

    def unset_max_height(self) -> "Style":
        return self._unset("max_height")

    # ------------------------------------------------------------------
    # Padding — CSS shorthand (1–4 args) and per-side
    # ------------------------------------------------------------------

    def padding(self, *values: int) -> "Style":
        """Set padding using CSS shorthand (1–4 values)."""
        top, right, bottom, left = _expand_sides(*values)
        return (
            self._set("padding_top", top)
            ._set("padding_right", right)
            ._set("padding_bottom", bottom)
            ._set("padding_left", left)
        )

    def padding_top(self, n: int) -> "Style":
        return self._set("padding_top", n)

    def get_padding_top(self) -> int:
        return self._get("padding_top", 0)

    def unset_padding_top(self) -> "Style":
        return self._unset("padding_top")

    def padding_right(self, n: int) -> "Style":
        return self._set("padding_right", n)

    def get_padding_right(self) -> int:
        return self._get("padding_right", 0)

    def unset_padding_right(self) -> "Style":
        return self._unset("padding_right")

    def padding_bottom(self, n: int) -> "Style":
        return self._set("padding_bottom", n)

    def get_padding_bottom(self) -> int:
        return self._get("padding_bottom", 0)

    def unset_padding_bottom(self) -> "Style":
        return self._unset("padding_bottom")

    def padding_left(self, n: int) -> "Style":
        return self._set("padding_left", n)

    def get_padding_left(self) -> int:
        return self._get("padding_left", 0)

    def unset_padding_left(self) -> "Style":
        return self._unset("padding_left")

    # ------------------------------------------------------------------
    # Margins — CSS shorthand (1–4 args) and per-side
    # ------------------------------------------------------------------

    def margin(self, *values: int) -> "Style":
        """Set margins using CSS shorthand (1–4 values)."""
        top, right, bottom, left = _expand_sides(*values)
        return (
            self._set("margin_top", top)
            ._set("margin_right", right)
            ._set("margin_bottom", bottom)
            ._set("margin_left", left)
        )

    def margin_top(self, n: int) -> "Style":
        return self._set("margin_top", n)

    def get_margin_top(self) -> int:
        return self._get("margin_top", 0)

    def unset_margin_top(self) -> "Style":
        return self._unset("margin_top")

    def margin_right(self, n: int) -> "Style":
        return self._set("margin_right", n)

    def get_margin_right(self) -> int:
        return self._get("margin_right", 0)

    def unset_margin_right(self) -> "Style":
        return self._unset("margin_right")

    def margin_bottom(self, n: int) -> "Style":
        return self._set("margin_bottom", n)

    def get_margin_bottom(self) -> int:
        return self._get("margin_bottom", 0)

    def unset_margin_bottom(self) -> "Style":
        return self._unset("margin_bottom")

    def margin_left(self, n: int) -> "Style":
        return self._set("margin_left", n)

    def get_margin_left(self) -> int:
        return self._get("margin_left", 0)

    def unset_margin_left(self) -> "Style":
        return self._unset("margin_left")

    def margin_background(self, c: "TerminalColor") -> "Style":
        """Set the background color of the margin area."""
        return self._set("margin_background", c)

    def get_margin_background(self) -> "TerminalColor | None":
        return self._get("margin_background")

    def unset_margin_background(self) -> "Style":
        return self._unset("margin_background")

    # ------------------------------------------------------------------
    # Borders
    # ------------------------------------------------------------------

    def border(self, b: "Border", *sides: bool) -> "Style":
        """Set border style and optionally which sides to show.

        When *sides* has 1–4 values they follow CSS order (top, right,
        bottom, left).
        """
        s = self._set("border_style", b)
        if sides:
            top, right, bottom, left = _expand_sides_bool(*sides)
            s = (
                s._set("border_top", top)
                ._set("border_right", right)
                ._set("border_bottom", bottom)
                ._set("border_left", left)
            )
        return s

    def border_style(self, b: "Border") -> "Style":
        return self._set("border_style", b)

    def get_border_style(self) -> "Border | None":
        return self._get("border_style")

    def unset_border_style(self) -> "Style":
        return self._unset("border_style")

    def border_top(self, v: bool = True) -> "Style":
        return self._set("border_top", v)

    def get_border_top(self) -> bool:
        return self._get("border_top", False)

    def unset_border_top(self) -> "Style":
        return self._unset("border_top")

    def border_right(self, v: bool = True) -> "Style":
        return self._set("border_right", v)

    def get_border_right(self) -> bool:
        return self._get("border_right", False)

    def unset_border_right(self) -> "Style":
        return self._unset("border_right")

    def border_bottom(self, v: bool = True) -> "Style":
        return self._set("border_bottom", v)

    def get_border_bottom(self) -> bool:
        return self._get("border_bottom", False)

    def unset_border_bottom(self) -> "Style":
        return self._unset("border_bottom")

    def border_left(self, v: bool = True) -> "Style":
        return self._set("border_left", v)

    def get_border_left(self) -> bool:
        return self._get("border_left", False)

    def unset_border_left(self) -> "Style":
        return self._unset("border_left")

    # Border foreground colors

    def border_foreground(self, c: "TerminalColor") -> "Style":
        """Set foreground color for all four border sides."""
        return (
            self._set("border_top_foreground", c)
            ._set("border_right_foreground", c)
            ._set("border_bottom_foreground", c)
            ._set("border_left_foreground", c)
        )

    def border_top_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_top_foreground", c)

    def get_border_top_foreground(self) -> "TerminalColor | None":
        return self._get("border_top_foreground")

    def unset_border_top_foreground(self) -> "Style":
        return self._unset("border_top_foreground")

    def border_right_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_right_foreground", c)

    def get_border_right_foreground(self) -> "TerminalColor | None":
        return self._get("border_right_foreground")

    def unset_border_right_foreground(self) -> "Style":
        return self._unset("border_right_foreground")

    def border_bottom_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_bottom_foreground", c)

    def get_border_bottom_foreground(self) -> "TerminalColor | None":
        return self._get("border_bottom_foreground")

    def unset_border_bottom_foreground(self) -> "Style":
        return self._unset("border_bottom_foreground")

    def border_left_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_left_foreground", c)

    def get_border_left_foreground(self) -> "TerminalColor | None":
        return self._get("border_left_foreground")

    def unset_border_left_foreground(self) -> "Style":
        return self._unset("border_left_foreground")

    # Border background colors

    def border_background(self, c: "TerminalColor") -> "Style":
        """Set background color for all four border sides."""
        return (
            self._set("border_top_background", c)
            ._set("border_right_background", c)
            ._set("border_bottom_background", c)
            ._set("border_left_background", c)
        )

    def border_top_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_top_background", c)

    def get_border_top_background(self) -> "TerminalColor | None":
        return self._get("border_top_background")

    def unset_border_top_background(self) -> "Style":
        return self._unset("border_top_background")

    def border_right_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_right_background", c)

    def get_border_right_background(self) -> "TerminalColor | None":
        return self._get("border_right_background")

    def unset_border_right_background(self) -> "Style":
        return self._unset("border_right_background")

    def border_bottom_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_bottom_background", c)

    def get_border_bottom_background(self) -> "TerminalColor | None":
        return self._get("border_bottom_background")

    def unset_border_bottom_background(self) -> "Style":
        return self._unset("border_bottom_background")

    def border_left_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_left_background", c)

    def get_border_left_background(self) -> "TerminalColor | None":
        return self._get("border_left_background")

    def unset_border_left_background(self) -> "Style":
        return self._unset("border_left_background")

    # ------------------------------------------------------------------
    # Alignment
    # ------------------------------------------------------------------

    def align(self, *alignments: "Position") -> "Style":
        """Set horizontal (and optionally vertical) alignment.

        With one argument sets horizontal alignment.
        With two arguments sets horizontal then vertical.
        """
        s = self
        if len(alignments) >= 1:
            s = s._set("align_horizontal", alignments[0])
        if len(alignments) >= 2:
            s = s._set("align_vertical", alignments[1])
        return s

    def align_horizontal(self, v: "Position") -> "Style":
        return self._set("align_horizontal", v)

    def get_align_horizontal(self) -> "Position":
        from .position import Left
        return self._get("align_horizontal", Left)

    def unset_align_horizontal(self) -> "Style":
        return self._unset("align_horizontal")

    def align_vertical(self, v: "Position") -> "Style":
        return self._set("align_vertical", v)

    def get_align_vertical(self) -> "Position":
        from .position import Top
        return self._get("align_vertical", Top)

    def unset_align_vertical(self) -> "Style":
        return self._unset("align_vertical")

    # ------------------------------------------------------------------
    # Inline, tab-width, transform
    # ------------------------------------------------------------------

    def inline(self, v: bool = True) -> "Style":
        """Force output onto a single line, ignoring padding/margin/borders."""
        return self._set("inline", v)

    def get_inline(self) -> bool:
        return self._get("inline", False)

    def unset_inline(self) -> "Style":
        return self._unset("inline")

    def tab_width(self, n: int) -> "Style":
        """Set tab stop width.  0 removes tabs; -1 leaves them intact."""
        return self._set("tab_width", n)

    def get_tab_width(self) -> int:
        return self._get("tab_width", 4)

    def unset_tab_width(self) -> "Style":
        return self._unset("tab_width")

    def transform(self, fn: Callable[[str], str]) -> "Style":
        """Apply an arbitrary transform to the rendered string."""
        return self._set("transform", fn)

    def get_transform(self) -> "Callable[[str], str] | None":
        return self._get("transform")

    def unset_transform(self) -> "Style":
        return self._unset("transform")


# ---------------------------------------------------------------------------
# Module-level convenience constructor
# ---------------------------------------------------------------------------


def new_style() -> Style:
    """Return a new empty Style using the default renderer."""
    return Style()


# ---------------------------------------------------------------------------
# Internal CSS-shorthand helpers
# ---------------------------------------------------------------------------


def _expand_sides(*values: int) -> tuple[int, int, int, int]:
    """Expand 1–4 int values to (top, right, bottom, left) following CSS order."""
    if len(values) == 1:
        return values[0], values[0], values[0], values[0]
    if len(values) == 2:
        return values[0], values[1], values[0], values[1]
    if len(values) == 3:
        return values[0], values[1], values[2], values[1]
    if len(values) == 4:
        return values[0], values[1], values[2], values[3]
    raise ValueError(f"Expected 1–4 values, got {len(values)}")


def _expand_sides_bool(*values: bool) -> tuple[bool, bool, bool, bool]:
    """Expand 1–4 bool values to (top, right, bottom, left) following CSS order."""
    if len(values) == 1:
        return values[0], values[0], values[0], values[0]
    if len(values) == 2:
        return values[0], values[1], values[0], values[1]
    if len(values) == 3:
        return values[0], values[1], values[2], values[1]
    if len(values) == 4:
        return values[0], values[1], values[2], values[3]
    raise ValueError(f"Expected 1–4 values, got {len(values)}")
