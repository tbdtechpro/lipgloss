"""
Lip Gloss — CSS-like terminal styling for Python.

Ported from the Go library: https://github.com/charmbracelet/lipgloss

Example usage::

    import lipgloss

    style = (
        lipgloss.Style()
        .bold(True)
        .foreground(lipgloss.Color("#FAFAFA"))
        .background(lipgloss.Color("#7D56F4"))
        .padding_top(2)
        .padding_left(4)
        .width(22)
    )

    print(style.render("Hello, kitty"))
"""

__version__ = "0.1.0"

# Borders
from .borders import (
    Border,
    ascii_border,
    block_border,
    double_border,
    hidden_border,
    inner_half_block_border,
    markdown_border,
    normal_border,
    outer_half_block_border,
    rounded_border,
    thick_border,
)

# Color types
from .color import (
    AdaptiveColor,
    ANSIColor,
    Color,
    CompleteAdaptiveColor,
    CompleteColor,
    NoColor,
    TerminalColor,
)

# Layout utilities
from .join import join_horizontal, join_vertical

# Position constants and placement functions
from .position import (
    Bottom,
    Center,
    Left,
    Position,
    Right,
    Top,
    place,
    place_horizontal,
    place_vertical,
)

# Renderer
from .renderer import ColorProfile, Renderer, default_renderer, new_renderer, set_default_renderer

# Per-rune styling
from .runes import style_runes

# Measurement
from .size import height, size, width

# Style
from .style import Style, new_style

# Themes
from . import themes

# Whitespace options
from .whitespace import (
    WhitespaceOption,
    whitespace_background,
    whitespace_chars,
    whitespace_foreground,
)

__all__ = [
    # Version
    "__version__",
    # Themes
    "themes",
    # Style
    "Style",
    "new_style",
    # Color types
    "TerminalColor",
    "NoColor",
    "Color",
    "ANSIColor",
    "AdaptiveColor",
    "CompleteColor",
    "CompleteAdaptiveColor",
    # Borders
    "Border",
    "normal_border",
    "rounded_border",
    "thick_border",
    "double_border",
    "ascii_border",
    "markdown_border",
    "hidden_border",
    "block_border",
    "outer_half_block_border",
    "inner_half_block_border",
    # Position constants
    "Position",
    "Top",
    "Bottom",
    "Left",
    "Right",
    "Center",
    # Placement
    "place",
    "place_horizontal",
    "place_vertical",
    # Whitespace
    "WhitespaceOption",
    "whitespace_foreground",
    "whitespace_background",
    "whitespace_chars",
    # Join
    "join_horizontal",
    "join_vertical",
    # Measurement
    "width",
    "height",
    "size",
    # Per-rune styling
    "style_runes",
    # Renderer
    "ColorProfile",
    "Renderer",
    "default_renderer",
    "set_default_renderer",
    "new_renderer",
]
