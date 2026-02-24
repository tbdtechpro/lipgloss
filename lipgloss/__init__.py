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
