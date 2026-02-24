"""
Dracula theme.

Palette source: https://draculatheme.com/contribute
"""

from dataclasses import dataclass

from lipgloss.color import Color


@dataclass(frozen=True)
class DraculaTheme:
    """Dracula — a dark theme with vivid accent colors.

    See https://draculatheme.com for the canonical palette specification.
    """

    # ------------------------------------------------------------------ #
    # Base palette                                                        #
    # ------------------------------------------------------------------ #
    background: Color = Color("#282a36")
    current_line: Color = Color("#44475a")
    foreground: Color = Color("#f8f8f2")
    comment: Color = Color("#6272a4")

    # ------------------------------------------------------------------ #
    # Accent colors                                                       #
    # ------------------------------------------------------------------ #
    cyan: Color = Color("#8be9fd")
    green: Color = Color("#50fa7b")
    orange: Color = Color("#ffb86c")
    pink: Color = Color("#ff79c6")
    purple: Color = Color("#bd93f9")
    red: Color = Color("#ff5555")
    yellow: Color = Color("#f1fa8c")


#: Shared singleton — import and use directly.
dracula = DraculaTheme()
