"""
Style — the core styling primitive.

Port of: style.go, set.go, get.go, unset.go
"""

from __future__ import annotations

import re
from copy import deepcopy
from typing import TYPE_CHECKING, Any, Callable, cast

if TYPE_CHECKING:
    from .borders import Border
    from .color import TerminalColor
    from .position import Position
    from .renderer import Renderer

# Regex to strip ANSI escape sequences (used for visible-width measurement).
_ANSI_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


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
        """Apply all set properties and return an ANSI-escaped string."""
        strs = list(strings)
        if self._value:
            strs = [self._value] + strs
        str_ = " ".join(strs)

        # Collect property values
        bold = self._get("bold", False)
        italic = self._get("italic", False)
        underline = self._get("underline", False)
        strikethrough = self._get("strikethrough", False)
        reverse = self._get("reverse", False)
        blink = self._get("blink", False)
        faint = self._get("faint", False)
        underline_spaces = self._get("underline_spaces", False) or (
            underline and self._get("underline_spaces", True)
        )
        strikethrough_spaces = self._get("strikethrough_spaces", False) or (
            strikethrough and self._get("strikethrough_spaces", True)
        )
        color_whitespace = self._get("color_whitespace", True)
        inline = self._get("inline", False)
        max_width = self._get("max_width", 0)
        max_height = self._get("max_height", 0)
        width_ = self._get("width", 0)
        height_ = self._get("height", 0)
        h_align = self._get("align_horizontal", 0.0)
        v_align = self._get("align_vertical", 0.0)
        pad_top = self._get("padding_top", 0)
        pad_right = self._get("padding_right", 0)
        pad_bottom = self._get("padding_bottom", 0)
        pad_left = self._get("padding_left", 0)
        transform = self._get("transform")

        fg_color = self._get("foreground")
        bg_color = self._get("background")

        # Apply transform first
        if transform is not None:
            str_ = transform(str_)

        # If no props set at all, just handle tabs and return
        if not self._props:
            return _maybe_convert_tabs(str_, self._get("tab_width", 4), self._is_set("tab_width"))

        # Resolve colors to ANSI escape fragments
        fg_esc = fg_color.resolve(self._renderer) if fg_color is not None else ""
        bg_esc = bg_color.resolve(self._renderer) if bg_color is not None else ""

        style_whitespace = reverse
        use_space_styler = (
            (underline and not underline_spaces)
            or (strikethrough and not strikethrough_spaces)
            or underline_spaces
            or strikethrough_spaces
        )

        # Build SGR sequence for the main text styler
        def _build_sgr(
            bold: bool,
            italic: bool,
            underline: bool,
            strikethrough: bool,
            reverse: bool,
            blink: bool,
            faint: bool,
            fg: str,
            bg: str,
        ) -> str:
            params: list[str] = []
            if bold:
                params.append("1")
            if faint:
                params.append("2")
            if italic:
                params.append("3")
            if underline:
                params.append("4")
            if blink:
                params.append("5")
            if reverse:
                params.append("7")
            if strikethrough:
                params.append("9")
            if fg:
                # fg is already a full escape like \x1b[38;2;...m — extract params
                params.extend(_extract_sgr_params(fg))
            if bg:
                params.extend(_extract_sgr_params(_fg_to_bg_escape(bg)))
            return "\x1b[" + ";".join(params) + "m" if params else ""

        main_sgr = _build_sgr(
            bold, italic, underline, strikethrough, reverse, blink, faint, fg_esc, bg_esc
        )
        reset = "\x1b[0m" if main_sgr else ""

        # Whitespace styler (for padding/margin background, reverse)
        ws_params: list[str] = []
        if reverse:
            ws_params.append("7")
        if fg_esc and style_whitespace:
            ws_params.extend(_extract_sgr_params(fg_esc))
        if bg_esc and color_whitespace:
            ws_params.extend(_extract_sgr_params(_fg_to_bg_escape(bg_esc)))
        ws_sgr = "\x1b[" + ";".join(ws_params) + "m" if ws_params else ""
        ws_reset = "\x1b[0m" if ws_sgr else ""

        # Space styler (for underline/strikethrough on spaces)
        sp_params: list[str] = []
        if fg_esc:
            sp_params.extend(_extract_sgr_params(fg_esc))
        if bg_esc:
            sp_params.extend(_extract_sgr_params(_fg_to_bg_escape(bg_esc)))
        if underline_spaces:
            sp_params.append("4")
        if strikethrough_spaces:
            sp_params.append("9")
        sp_sgr = "\x1b[" + ";".join(sp_params) + "m" if sp_params else ""
        sp_reset = "\x1b[0m" if sp_sgr else ""

        def style_str(s: str) -> str:
            if not main_sgr:
                return s
            return main_sgr + s + reset

        def style_ws(s: str) -> str:
            if not ws_sgr:
                return s
            return ws_sgr + s + ws_reset

        def style_sp(s: str) -> str:
            if not sp_sgr:
                return s
            return sp_sgr + s + sp_reset

        # Tab conversion
        str_ = _maybe_convert_tabs(str_, self._get("tab_width", 4), self._is_set("tab_width"))
        # Normalize carriage returns
        str_ = str_.replace("\r\n", "\n")

        # Strip newlines in inline mode
        if inline:
            str_ = str_.replace("\n", "")

        # Word wrap to fit width (before padding)
        if not inline and width_ > 0:
            wrap_at = width_ - pad_left - pad_right
            if wrap_at > 0:
                str_ = _word_wrap(str_, wrap_at)

        # Render core text line-by-line
        lines = str_.split("\n")
        rendered_lines: list[str] = []
        for line in lines:
            if use_space_styler:
                parts: list[str] = []
                for ch in line:
                    if ch == " " or ch == "\t":
                        parts.append(style_sp(ch))
                    else:
                        parts.append(style_str(ch))
                rendered_lines.append("".join(parts))
            else:
                rendered_lines.append(style_str(line))
        str_ = "\n".join(rendered_lines)

        # Padding
        if not inline:
            if pad_left > 0:
                pad_l = style_ws(" " * pad_left)
                str_ = "\n".join(pad_l + line for line in str_.split("\n"))
            if pad_right > 0:
                pad_r = style_ws(" " * pad_right)
                str_ = "\n".join(line + pad_r for line in str_.split("\n"))
            if pad_top > 0:
                str_ = "\n" * pad_top + str_
            if pad_bottom > 0:
                str_ = str_ + "\n" * pad_bottom

        # Vertical alignment / height
        if height_ > 0:
            str_ = _align_text_vertical(str_, v_align, height_)

        # Horizontal alignment (also normalises line widths)
        num_lines = str_.count("\n")
        if num_lines != 0 or width_ != 0:
            str_ = _align_text_horizontal(
                str_, h_align, width_, style_ws if (color_whitespace or style_whitespace) else None
            )

        if not inline:
            str_ = self._apply_border(str_)
            str_ = self._apply_margins(str_)

        # Truncate to MaxWidth
        if max_width > 0:
            lines = str_.split("\n")
            str_ = "\n".join(_truncate_ansi(line, max_width) for line in lines)

        # Truncate to MaxHeight
        if max_height > 0:
            lines = str_.split("\n")
            str_ = "\n".join(lines[:max_height])

        return str_

    # ------------------------------------------------------------------
    # Border and margin application helpers
    # ------------------------------------------------------------------

    def _apply_border(self, str_: str) -> str:
        border = self._get("border_style")
        has_top = self._get("border_top", False)
        has_right = self._get("border_right", False)
        has_bottom = self._get("border_bottom", False)
        has_left = self._get("border_left", False)

        # If a border style is set but no sides explicitly chosen, show all sides.
        if border is not None and not any(
            [
                self._is_set("border_top"),
                self._is_set("border_right"),
                self._is_set("border_bottom"),
                self._is_set("border_left"),
            ]
        ):
            has_top = has_right = has_bottom = has_left = True

        if border is None or not any([has_top, has_right, has_bottom, has_left]):
            return str_

        top_fg = self._get("border_top_foreground")
        right_fg = self._get("border_right_foreground")
        bottom_fg = self._get("border_bottom_foreground")
        left_fg = self._get("border_left_foreground")
        top_bg = self._get("border_top_background")
        right_bg = self._get("border_right_background")
        bottom_bg = self._get("border_bottom_background")
        left_bg = self._get("border_left_background")

        lines = str_.split("\n")
        content_width = max((_visible_width(ln) for ln in lines), default=0)

        if has_left:
            left_char = border.left or " "
            content_width += _char_width(left_char)
        else:
            left_char = ""
        right_char = border.right if has_right else ""
        if has_right and not right_char:
            right_char = " "

        # Corner resolution
        top_left = border.top_left if (has_top and has_left) else ""
        top_right = border.top_right if (has_top and has_right) else ""
        bottom_left = border.bottom_left if (has_bottom and has_left) else ""
        bottom_right = border.bottom_right if (has_bottom and has_right) else ""

        # Limit corners to first rune
        top_left = top_left[:1] if top_left else ""
        top_right = top_right[:1] if top_right else ""
        bottom_left = bottom_left[:1] if bottom_left else ""
        bottom_right = bottom_right[:1] if bottom_right else ""

        out: list[str] = []

        def _style_border_part(
            s: str, fg: "TerminalColor | None", bg: "TerminalColor | None"
        ) -> str:
            if not s:
                return s
            fg_e = fg.resolve(self._renderer) if fg is not None else ""
            bg_e = bg.resolve(self._renderer) if bg is not None else ""
            params: list[str] = []
            if fg_e:
                params.extend(_extract_sgr_params(fg_e))
            if bg_e:
                params.extend(_extract_sgr_params(_fg_to_bg_escape(bg_e)))
            if not params:
                return s
            return "\x1b[" + ";".join(params) + "m" + s + "\x1b[0m"

        if has_top:
            top_str = _render_horizontal_edge(top_left, border.top, top_right, content_width)
            out.append(_style_border_part(top_str, top_fg, top_bg))

        left_runes = list(left_char) if left_char else []
        right_runes = list(right_char) if right_char else []
        li = ri = 0
        for i, line in enumerate(lines):
            row = ""
            if left_runes:
                r = left_runes[li % len(left_runes)]
                li += 1
                row += _style_border_part(r, left_fg, left_bg)
            row += line
            if right_runes:
                r = right_runes[ri % len(right_runes)]
                ri += 1
                row += _style_border_part(r, right_fg, right_bg)
            out.append(row)

        if has_bottom:
            bot_str = _render_horizontal_edge(
                bottom_left, border.bottom, bottom_right, content_width
            )
            out.append(_style_border_part(bot_str, bottom_fg, bottom_bg))

        return "\n".join(out)

    def _apply_margins(self, str_: str) -> str:
        top_margin = self._get("margin_top", 0)
        right_margin = self._get("margin_right", 0)
        bottom_margin = self._get("margin_bottom", 0)
        left_margin = self._get("margin_left", 0)

        margin_bg = self._get("margin_background")

        def style_margin(s: str) -> str:
            if margin_bg is None:
                return s
            bg_e = margin_bg.resolve(self._renderer)
            if not bg_e:
                return s
            params = _extract_sgr_params(_fg_to_bg_escape(bg_e))
            if not params:
                return s
            return "\x1b[" + ";".join(params) + "m" + s + "\x1b[0m"

        if left_margin > 0:
            pad = style_margin(" " * left_margin)
            str_ = "\n".join(pad + line for line in str_.split("\n"))
        if right_margin > 0:
            pad = style_margin(" " * right_margin)
            str_ = "\n".join(line + pad for line in str_.split("\n"))

        if top_margin > 0 or bottom_margin > 0:
            lines = str_.split("\n")
            w = max((_visible_width(ln) for ln in lines), default=0)
            empty_line = style_margin(" " * w)
            if top_margin > 0:
                str_ = (empty_line + "\n") * top_margin + str_
            if bottom_margin > 0:
                str_ = str_ + ("\n" + empty_line) * bottom_margin

        return str_

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

    # Keys that are never inherited (matches Go's Inherit() exclusions).
    _NO_INHERIT = frozenset(
        {
            "margin_top",
            "margin_right",
            "margin_bottom",
            "margin_left",
            "padding_top",
            "padding_right",
            "padding_bottom",
            "padding_left",
        }
    )

    def inherit(self, parent: "Style") -> "Style":
        """Copy unset properties from *parent*.

        Properties already set on this style are not overridden.
        Margins and padding are never inherited (matches Go behaviour).
        """
        s = self.copy()
        for key, value in parent._props.items():
            if key in self._NO_INHERIT:
                continue
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
        return bool(self._get("bold", False))

    def unset_bold(self) -> "Style":
        return self._unset("bold")

    def italic(self, v: bool = True) -> "Style":
        """Set italic text."""
        return self._set("italic", v)

    def get_italic(self) -> bool:
        return bool(self._get("italic", False))

    def unset_italic(self) -> "Style":
        return self._unset("italic")

    def underline(self, v: bool = True) -> "Style":
        """Set underlined text."""
        return self._set("underline", v)

    def get_underline(self) -> bool:
        return bool(self._get("underline", False))

    def unset_underline(self) -> "Style":
        return self._unset("underline")

    def strikethrough(self, v: bool = True) -> "Style":
        """Set strikethrough text."""
        return self._set("strikethrough", v)

    def get_strikethrough(self) -> bool:
        return bool(self._get("strikethrough", False))

    def unset_strikethrough(self) -> "Style":
        return self._unset("strikethrough")

    def reverse(self, v: bool = True) -> "Style":
        """Swap foreground and background colors."""
        return self._set("reverse", v)

    def get_reverse(self) -> bool:
        return bool(self._get("reverse", False))

    def unset_reverse(self) -> "Style":
        return self._unset("reverse")

    def blink(self, v: bool = True) -> "Style":
        """Set blinking text."""
        return self._set("blink", v)

    def get_blink(self) -> bool:
        return bool(self._get("blink", False))

    def unset_blink(self) -> "Style":
        return self._unset("blink")

    def faint(self, v: bool = True) -> "Style":
        """Dim / faint text."""
        return self._set("faint", v)

    def get_faint(self) -> bool:
        return bool(self._get("faint", False))

    def unset_faint(self) -> "Style":
        return self._unset("faint")

    def underline_spaces(self, v: bool = True) -> "Style":
        """Underline spaces between words."""
        return self._set("underline_spaces", v)

    def get_underline_spaces(self) -> bool:
        return bool(self._get("underline_spaces", False))

    def unset_underline_spaces(self) -> "Style":
        return self._unset("underline_spaces")

    def strikethrough_spaces(self, v: bool = True) -> "Style":
        """Apply strikethrough to spaces between words."""
        return self._set("strikethrough_spaces", v)

    def get_strikethrough_spaces(self) -> bool:
        return bool(self._get("strikethrough_spaces", False))

    def unset_strikethrough_spaces(self) -> "Style":
        return self._unset("strikethrough_spaces")

    def color_whitespace(self, v: bool = True) -> "Style":
        """Apply foreground / background colors to whitespace characters."""
        return self._set("color_whitespace", v)

    def get_color_whitespace(self) -> bool:
        return bool(self._get("color_whitespace", True))

    def unset_color_whitespace(self) -> "Style":
        return self._unset("color_whitespace")

    # ------------------------------------------------------------------
    # Color setters / getters / unsetters
    # ------------------------------------------------------------------

    def foreground(self, c: "TerminalColor") -> "Style":
        """Set the foreground color."""
        return self._set("foreground", c)

    def get_foreground(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("foreground"))

    def unset_foreground(self) -> "Style":
        return self._unset("foreground")

    def background(self, c: "TerminalColor") -> "Style":
        """Set the background color."""
        return self._set("background", c)

    def get_background(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("background"))

    def unset_background(self) -> "Style":
        return self._unset("background")

    # ------------------------------------------------------------------
    # Dimension setters / getters / unsetters
    # ------------------------------------------------------------------

    def width(self, n: int) -> "Style":
        """Set minimum width."""
        return self._set("width", n)

    def get_width(self) -> int:
        return int(self._get("width", 0))

    def unset_width(self) -> "Style":
        return self._unset("width")

    def height(self, n: int) -> "Style":
        """Set minimum height."""
        return self._set("height", n)

    def get_height(self) -> int:
        return int(self._get("height", 0))

    def unset_height(self) -> "Style":
        return self._unset("height")

    def max_width(self, n: int) -> "Style":
        """Set maximum width; content is truncated beyond this."""
        return self._set("max_width", n)

    def get_max_width(self) -> int:
        return int(self._get("max_width", 0))

    def unset_max_width(self) -> "Style":
        return self._unset("max_width")

    def max_height(self, n: int) -> "Style":
        """Set maximum height; content is truncated beyond this."""
        return self._set("max_height", n)

    def get_max_height(self) -> int:
        return int(self._get("max_height", 0))

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
        return int(self._get("padding_top", 0))

    def unset_padding_top(self) -> "Style":
        return self._unset("padding_top")

    def padding_right(self, n: int) -> "Style":
        return self._set("padding_right", n)

    def get_padding_right(self) -> int:
        return int(self._get("padding_right", 0))

    def unset_padding_right(self) -> "Style":
        return self._unset("padding_right")

    def padding_bottom(self, n: int) -> "Style":
        return self._set("padding_bottom", n)

    def get_padding_bottom(self) -> int:
        return int(self._get("padding_bottom", 0))

    def unset_padding_bottom(self) -> "Style":
        return self._unset("padding_bottom")

    def padding_left(self, n: int) -> "Style":
        return self._set("padding_left", n)

    def get_padding_left(self) -> int:
        return int(self._get("padding_left", 0))

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
        return int(self._get("margin_top", 0))

    def unset_margin_top(self) -> "Style":
        return self._unset("margin_top")

    def margin_right(self, n: int) -> "Style":
        return self._set("margin_right", n)

    def get_margin_right(self) -> int:
        return int(self._get("margin_right", 0))

    def unset_margin_right(self) -> "Style":
        return self._unset("margin_right")

    def margin_bottom(self, n: int) -> "Style":
        return self._set("margin_bottom", n)

    def get_margin_bottom(self) -> int:
        return int(self._get("margin_bottom", 0))

    def unset_margin_bottom(self) -> "Style":
        return self._unset("margin_bottom")

    def margin_left(self, n: int) -> "Style":
        return self._set("margin_left", n)

    def get_margin_left(self) -> int:
        return int(self._get("margin_left", 0))

    def unset_margin_left(self) -> "Style":
        return self._unset("margin_left")

    def margin_background(self, c: "TerminalColor") -> "Style":
        """Set the background color of the margin area."""
        return self._set("margin_background", c)

    def get_margin_background(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("margin_background"))

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
        return cast("Border | None", self._get("border_style"))

    def unset_border_style(self) -> "Style":
        return self._unset("border_style")

    def border_top(self, v: bool = True) -> "Style":
        return self._set("border_top", v)

    def get_border_top(self) -> bool:
        return bool(self._get("border_top", False))

    def unset_border_top(self) -> "Style":
        return self._unset("border_top")

    def border_right(self, v: bool = True) -> "Style":
        return self._set("border_right", v)

    def get_border_right(self) -> bool:
        return bool(self._get("border_right", False))

    def unset_border_right(self) -> "Style":
        return self._unset("border_right")

    def border_bottom(self, v: bool = True) -> "Style":
        return self._set("border_bottom", v)

    def get_border_bottom(self) -> bool:
        return bool(self._get("border_bottom", False))

    def unset_border_bottom(self) -> "Style":
        return self._unset("border_bottom")

    def border_left(self, v: bool = True) -> "Style":
        return self._set("border_left", v)

    def get_border_left(self) -> bool:
        return bool(self._get("border_left", False))

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
        return cast("TerminalColor | None", self._get("border_top_foreground"))

    def unset_border_top_foreground(self) -> "Style":
        return self._unset("border_top_foreground")

    def border_right_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_right_foreground", c)

    def get_border_right_foreground(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_right_foreground"))

    def unset_border_right_foreground(self) -> "Style":
        return self._unset("border_right_foreground")

    def border_bottom_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_bottom_foreground", c)

    def get_border_bottom_foreground(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_bottom_foreground"))

    def unset_border_bottom_foreground(self) -> "Style":
        return self._unset("border_bottom_foreground")

    def border_left_foreground(self, c: "TerminalColor") -> "Style":
        return self._set("border_left_foreground", c)

    def get_border_left_foreground(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_left_foreground"))

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
        return cast("TerminalColor | None", self._get("border_top_background"))

    def unset_border_top_background(self) -> "Style":
        return self._unset("border_top_background")

    def border_right_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_right_background", c)

    def get_border_right_background(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_right_background"))

    def unset_border_right_background(self) -> "Style":
        return self._unset("border_right_background")

    def border_bottom_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_bottom_background", c)

    def get_border_bottom_background(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_bottom_background"))

    def unset_border_bottom_background(self) -> "Style":
        return self._unset("border_bottom_background")

    def border_left_background(self, c: "TerminalColor") -> "Style":
        return self._set("border_left_background", c)

    def get_border_left_background(self) -> "TerminalColor | None":
        return cast("TerminalColor | None", self._get("border_left_background"))

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

        return float(self._get("align_horizontal", Left))

    def unset_align_horizontal(self) -> "Style":
        return self._unset("align_horizontal")

    def align_vertical(self, v: "Position") -> "Style":
        return self._set("align_vertical", v)

    def get_align_vertical(self) -> "Position":
        from .position import Top

        return float(self._get("align_vertical", Top))

    def unset_align_vertical(self) -> "Style":
        return self._unset("align_vertical")

    # ------------------------------------------------------------------
    # Inline, tab-width, transform
    # ------------------------------------------------------------------

    def inline(self, v: bool = True) -> "Style":
        """Force output onto a single line, ignoring padding/margin/borders."""
        return self._set("inline", v)

    def get_inline(self) -> bool:
        return bool(self._get("inline", False))

    def unset_inline(self) -> "Style":
        return self._unset("inline")

    def tab_width(self, n: int) -> "Style":
        """Set tab stop width.  0 removes tabs; -1 leaves them intact."""
        return self._set("tab_width", n)

    def get_tab_width(self) -> int:
        return int(self._get("tab_width", 4))

    def unset_tab_width(self) -> "Style":
        return self._unset("tab_width")

    def transform(self, fn: Callable[[str], str]) -> "Style":
        """Apply an arbitrary transform to the rendered string."""
        return self._set("transform", fn)

    def get_transform(self) -> "Callable[[str], str] | None":
        return cast("Callable[[str], str] | None", self._get("transform"))

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


# ---------------------------------------------------------------------------
# Rendering helpers (used by Style.render and its sub-methods)
# ---------------------------------------------------------------------------


def _strip_ansi(s: str) -> str:
    return _ANSI_RE.sub("", s)


def _char_width(ch: str) -> int:
    if not ch:
        return 0
    try:
        from wcwidth import wcwidth  # type: ignore[import]

        w = wcwidth(ch)
        return w if w >= 0 else 1
    except ImportError:
        return 1


def _visible_width(line: str) -> int:
    stripped = _strip_ansi(line)
    try:
        from wcwidth import wcswidth  # type: ignore[import]

        w = wcswidth(stripped)
        return w if w >= 0 else len(stripped)
    except ImportError:
        return len(stripped)


def _extract_sgr_params(escape: str) -> list[str]:
    """Extract the numeric params from a single SGR escape like \\x1b[38;2;1;2;3m."""
    if not escape:
        return []
    m = re.match(r"\x1b\[([0-9;]*)m", escape)
    if not m:
        return []
    raw = m.group(1)
    return [p for p in raw.split(";") if p]


def _fg_to_bg_escape(fg_escape: str) -> str:
    """Convert a foreground colour escape to its background equivalent."""
    if not fg_escape:
        return ""
    # \x1b[38;... → \x1b[48;...   \x1b[3Xm → \x1b[4Xm   \x1b[9Xm → \x1b[10Xm
    params = _extract_sgr_params(fg_escape)
    if not params:
        return ""
    out: list[str] = []
    i = 0
    while i < len(params):
        p = params[i]
        if p == "38" and i + 1 < len(params):
            out.append("48")
            i += 1
            continue
        try:
            n = int(p)
        except ValueError:
            out.append(p)
            i += 1
            continue
        if 30 <= n <= 37:
            out.append(str(n + 10))
        elif 90 <= n <= 97:
            out.append(str(n + 10))
        else:
            out.append(p)
        i += 1
    return "\x1b[" + ";".join(out) + "m"


def _maybe_convert_tabs(s: str, tab_width: int, explicit: bool) -> str:
    if not explicit:
        tab_width = 4
    if tab_width == -1:
        return s
    if tab_width == 0:
        return s.replace("\t", "")
    return s.replace("\t", " " * tab_width)


def _word_wrap(s: str, width: int) -> str:
    """Simple word-wrap that breaks long lines at *width* visible cells."""
    if width <= 0:
        return s
    result_lines: list[str] = []
    for line in s.split("\n"):
        if _visible_width(line) <= width:
            result_lines.append(line)
            continue
        words = line.split(" ")
        current = ""
        for word in words:
            if not current:
                current = word
            elif _visible_width(current) + 1 + _visible_width(word) <= width:
                current += " " + word
            else:
                result_lines.append(current)
                current = word
        result_lines.append(current)
    return "\n".join(result_lines)


def _truncate_ansi(line: str, max_width: int) -> str:
    """Truncate an ANSI-escaped line to at most *max_width* visible cells."""
    if _visible_width(line) <= max_width:
        return line
    visible = 0
    out: list[str] = []
    i = 0
    while i < len(line):
        # Check for ANSI escape sequence
        m = _ANSI_RE.match(line, i)
        if m:
            out.append(m.group(0))
            i = m.end()
            continue
        ch = line[i]
        cw = _char_width(ch)
        if visible + cw > max_width:
            break
        out.append(ch)
        visible += cw
        i += 1
    return "".join(out)


def _align_text_horizontal(
    str_: str,
    pos: float,
    width: int,
    style_ws: "Callable[[str], str] | None",
) -> str:
    lines = str_.split("\n")
    widest = max((_visible_width(ln) for ln in lines), default=0)
    result: list[str] = []
    for line in lines:
        line_w = _visible_width(line)
        short = widest - line_w
        short += max(0, width - (short + line_w))
        if short <= 0:
            result.append(line)
            continue
        pos_clamped = max(0.0, min(1.0, pos))
        if pos_clamped == 1.0:  # Right
            sp = " " * short
            if style_ws:
                sp = style_ws(sp)
            result.append(sp + line)
        elif pos_clamped == 0.5:  # Center
            left_n = short // 2
            right_n = left_n + short % 2
            lsp = " " * left_n
            rsp = " " * right_n
            if style_ws:
                lsp = style_ws(lsp)
                rsp = style_ws(rsp)
            result.append(lsp + line + rsp)
        else:  # Left (default)
            sp = " " * short
            if style_ws:
                sp = style_ws(sp)
            result.append(line + sp)
    return "\n".join(result)


def _align_text_vertical(str_: str, pos: float, height: int) -> str:
    str_height = str_.count("\n") + 1
    if height <= str_height:
        return str_
    pos_clamped = max(0.0, min(1.0, pos))
    if pos_clamped == 0.0:  # Top
        return str_ + "\n" * (height - str_height)
    if pos_clamped == 1.0:  # Bottom
        return "\n" * (height - str_height) + str_
    # Center
    top_pad = (height - str_height) // 2
    bottom_pad = (height - str_height) // 2
    if str_height + top_pad + bottom_pad < height:
        bottom_pad += 1
    return "\n" * top_pad + str_ + "\n" * bottom_pad


def _render_horizontal_edge(left: str, middle: str, right: str, width: int) -> str:
    if not middle:
        middle = " "
    left_w = _visible_width(left)
    right_w = _visible_width(right)
    runes = list(middle)
    j = 0
    out: list[str] = [left]
    i = left_w + right_w
    while i < width + right_w:
        ch = runes[j]
        out.append(ch)
        j = (j + 1) % len(runes)
        i += _char_width(ch)
    out.append(right)
    return "".join(out)
