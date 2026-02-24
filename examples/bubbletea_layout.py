"""
bubbletea_layout.py — layout showcase using lipgloss + bubbletea.

Demonstrates join_horizontal, join_vertical, place, borders, adaptive colors,
and table rendering all in a single Bubble Tea view().  This is the Python
equivalent of combining Go's Lip Gloss layout example with Bubble Tea.

Controls:
  tab / shift+tab   cycle active panel
  q  or  ESC        quit

Run with:  python examples/bubbletea_layout.py
"""

from typing import Optional

import bubbletea as tea

import lipgloss
from lipgloss import join_horizontal, join_vertical, place
from lipgloss import table as tbl
from lipgloss.borders import normal_border, rounded_border, thick_border

# ── Palette ───────────────────────────────────────────────────────────────────

PURPLE = lipgloss.Color("#7D56F4")
PINK = lipgloss.Color("#E377C2")
GREEN = lipgloss.Color("#04B575")
GRAY = lipgloss.Color("240")
LIGHT_GRAY = lipgloss.Color("245")
HIGHLIGHT = lipgloss.Color("99")

# ── Panel styles ──────────────────────────────────────────────────────────────

PANEL_ACTIVE = (
    lipgloss.Style()
    .border_style(rounded_border())
    .border(rounded_border(), True)
    .border_foreground(PURPLE)
    .padding(0, 1)
)

PANEL_INACTIVE = (
    lipgloss.Style()
    .border_style(normal_border())
    .border(normal_border(), True)
    .border_foreground(GRAY)
    .padding(0, 1)
)

TITLE_STYLE = lipgloss.Style().bold(True).foreground(PURPLE)

LABEL_STYLE = lipgloss.Style().foreground(GRAY)

VALUE_STYLE = lipgloss.Style().foreground(HIGHLIGHT)

HELP_STYLE = lipgloss.Style().faint(True)

# ── Panels ────────────────────────────────────────────────────────────────────

PANELS = ["stats", "languages", "history"]


def _stats_panel(active: bool) -> str:
    """Key/value statistics panel."""
    style = PANEL_ACTIVE if active else PANEL_INACTIVE

    rows = [
        (LABEL_STYLE.render("Requests"), VALUE_STYLE.render("1,234")),
        (LABEL_STYLE.render("Errors  "), VALUE_STYLE.render("   12")),
        (LABEL_STYLE.render("Uptime  "), VALUE_STYLE.render(" 99.1%")),
        (LABEL_STYLE.render("Latency "), VALUE_STYLE.render(" 42ms")),
    ]

    title = TITLE_STYLE.render("Stats")
    body = "\n".join(f"{k}  {v}" for k, v in rows)
    content = join_vertical(lipgloss.Top, title, "", body)
    return style.width(24).render(content)


def _languages_panel(active: bool) -> str:
    """Table of languages rendered with lipgloss table sub-package."""
    panel_style = PANEL_ACTIVE if active else PANEL_INACTIVE

    header_style = lipgloss.Style().bold(True).foreground(lipgloss.Color("#FAFAFA"))
    even_style = lipgloss.Style().foreground(LIGHT_GRAY)
    odd_style = lipgloss.Style().foreground(GRAY)

    def style_func(row: int, col: int) -> lipgloss.Style:
        if row == tbl.HeaderRow:
            return header_style
        return even_style if row % 2 == 0 else odd_style

    t = (
        tbl.Table()
        .border(thick_border())
        .border_style(lipgloss.Style().foreground(PURPLE))
        .style_func(style_func)
        .headers("Language", "Year", "Paradigm")
        .row("Python", "1991", "Multi")
        .row("Go", "2009", "Concurrent")
        .row("Rust", "2010", "Systems")
        .row("Haskell", "1990", "Functional")
    )

    title = TITLE_STYLE.render("Languages")
    return panel_style.render(join_vertical(lipgloss.Top, title, "", t.render()))


def _history_panel(active: bool) -> str:
    """Scrolling event history panel."""
    panel_style = PANEL_ACTIVE if active else PANEL_INACTIVE

    events = [
        (GREEN, "✓", "deploy  ", "v1.2.3 → production"),
        (PINK, "↑", "scale   ", "web: 2 → 4 replicas"),
        (GREEN, "✓", "health  ", "all checks passed"),
        (GRAY, "·", "log     ", "startup complete"),
        (GREEN, "✓", "migrate ", "schema applied"),
    ]

    title = TITLE_STYLE.render("History")
    lines = []
    for color, icon, kind, detail in events:
        icon_str = lipgloss.Style().foreground(color).render(icon)
        kind_str = lipgloss.Style().foreground(GRAY).render(kind)
        detail_str = lipgloss.Style().foreground(LIGHT_GRAY).render(detail)
        lines.append(f"{icon_str} {kind_str} {detail_str}")

    body = "\n".join(lines)
    content = join_vertical(lipgloss.Top, title, "", body)
    return panel_style.width(38).render(content)


# ── Model ─────────────────────────────────────────────────────────────────────


class LayoutModel(tea.Model):
    """Layout showcase with three tabbed panels."""

    def __init__(self) -> None:
        self.active = 0

    def init(self) -> Optional[tea.Cmd]:
        return None

    def update(self, msg: tea.Msg):  # type: ignore[override]
        if isinstance(msg, tea.KeyMsg):
            key = msg.key
            if key in ("q", "ctrl+c"):
                return self, tea.quit_cmd
            if key == "tab":
                self.active = (self.active + 1) % len(PANELS)
            elif key == "shift+tab":
                self.active = (self.active - 1) % len(PANELS)
        return self, None

    def view(self) -> str:
        # ── header ────────────────────────────────────────────────────────────
        header = (
            lipgloss.Style()
            .bold(True)
            .foreground(lipgloss.Color("#FAFAFA"))
            .background(PURPLE)
            .padding(0, 2)
            .render("  Lipgloss + Bubbletea Layout Showcase  ")
        )

        # ── tab bar ───────────────────────────────────────────────────────────
        tabs = []
        for i, name in enumerate(PANELS):
            if i == self.active:
                tab = lipgloss.Style().bold(True).foreground(PURPLE).render(f"[ {name} ]")
            else:
                tab = lipgloss.Style().foreground(GRAY).render(f"  {name}  ")
            tabs.append(tab)
        tab_bar = "  ".join(tabs)

        # ── panels ────────────────────────────────────────────────────────────
        stats = _stats_panel(self.active == 0)
        langs = _languages_panel(self.active == 1)
        hist = _history_panel(self.active == 2)

        panels_row = join_horizontal(lipgloss.Top, stats, "  ", langs, "  ", hist)

        # ── status bar ────────────────────────────────────────────────────────
        status = place(
            lipgloss.width(panels_row),
            1,
            lipgloss.Left,
            lipgloss.Center,
            HELP_STYLE.render("tab next panel  shift+tab prev  q quit"),
            lipgloss.whitespace_background(lipgloss.Color("235")),
        )

        return join_vertical(lipgloss.Left, header, "", tab_bar, "", panels_row, "", status)


# ── Entry point ───────────────────────────────────────────────────────────────


def main() -> None:
    model = LayoutModel()
    p = tea.Program(model, alt_screen=True)
    p.run()


if __name__ == "__main__":
    main()
