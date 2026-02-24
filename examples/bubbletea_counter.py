"""
bubbletea_counter.py — simple counter TUI built with lipgloss + bubbletea.

Demonstrates that lipgloss-rendered strings drop directly into a Bubble Tea
view() method as a Python replacement for the Go Lip Gloss + Bubble Tea stack.

Controls:
  +  or  =   increment counter
  -          decrement counter
  r          reset to zero
  q  or ESC  quit

Run with:  python examples/bubbletea_counter.py
"""

from typing import Optional

import bubbletea as tea

import lipgloss
from lipgloss import join_vertical
from lipgloss.borders import rounded_border

# ── Styles ────────────────────────────────────────────────────────────────────

TITLE_STYLE = (
    lipgloss.Style()
    .bold(True)
    .foreground(lipgloss.Color("#FAFAFA"))
    .background(lipgloss.Color("#7D56F4"))
    .padding(0, 2)
)

COUNT_STYLE = (
    lipgloss.Style()
    .bold(True)
    .foreground(lipgloss.Color("#04B575"))
    .width(16)
    .align(lipgloss.Center)
)

BOX_STYLE = (
    lipgloss.Style()
    .border_style(rounded_border())
    .border(rounded_border(), True)
    .border_foreground(lipgloss.Color("62"))
    .padding(1, 3)
    .align(lipgloss.Center)
)

HELP_STYLE = lipgloss.Style().faint(True)

# ── Model ─────────────────────────────────────────────────────────────────────


class CounterModel(tea.Model):
    """Counter with styled header, value box, and help footer."""

    def __init__(self) -> None:
        self.count = 0

    def init(self) -> Optional[tea.Cmd]:
        return None

    def update(self, msg: tea.Msg):  # type: ignore[override]
        if isinstance(msg, tea.KeyMsg):
            key = msg.key
            if key in ("q", "ctrl+c"):
                return self, tea.quit_cmd
            if key in ("+", "="):
                self.count += 1
            elif key == "-":
                self.count -= 1
            elif key == "r":
                self.count = 0
        return self, None

    def view(self) -> str:
        title = TITLE_STYLE.render("  Counter  ")
        count_str = COUNT_STYLE.render(str(self.count))
        box = BOX_STYLE.render(count_str)
        help_text = HELP_STYLE.render("+ increment  − decrement  r reset  q quit")
        return join_vertical(lipgloss.Center, title, "", box, "", help_text)


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    model = CounterModel()
    p = tea.Program(model, alt_screen=True)
    p.run()


if __name__ == "__main__":
    main()
