"""
Border definitions.

Port of: borders.go
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Border:
    """Defines the rune strings used to draw each part of a border.

    All fields default to empty string (no border character).
    """

    top: str = ""
    bottom: str = ""
    left: str = ""
    right: str = ""
    top_left: str = ""
    top_right: str = ""
    bottom_left: str = ""
    bottom_right: str = ""
    middle_left: str = ""
    middle_right: str = ""
    middle: str = ""
    middle_top: str = ""
    middle_bottom: str = ""

    def get_top_size(self) -> int:
        """Return the rendered width of the top border (0 if absent)."""
        return _border_edge_width(self.top_left, self.top, self.top_right)

    def get_bottom_size(self) -> int:
        """Return the rendered width of the bottom border (0 if absent)."""
        return _border_edge_width(self.bottom_left, self.bottom, self.bottom_right)

    def get_left_size(self) -> int:
        """Return the rendered width of the left border (0 if absent)."""
        return _border_edge_width(self.top_left, self.left, self.bottom_left)

    def get_right_size(self) -> int:
        """Return the rendered width of the right border (0 if absent)."""
        return _border_edge_width(self.top_right, self.right, self.bottom_right)


def _border_edge_width(*parts: str) -> int:
    """Return the maximum single-rune visual width across all border parts."""
    return max((len(p) > 0) for p in parts) if any(parts) else 0


# ---------------------------------------------------------------------------
# Predefined border factories — exact rune values from borders.go
# ---------------------------------------------------------------------------


def normal_border() -> Border:
    """Single-line box drawing with 90-degree corners."""
    return Border(
        top="─", bottom="─", left="│", right="│",
        top_left="┌", top_right="┐", bottom_left="└", bottom_right="┘",
        middle_left="├", middle_right="┤", middle="┼",
        middle_top="┬", middle_bottom="┴",
    )


def rounded_border() -> Border:
    """Single-line box drawing with rounded corners."""
    return Border(
        top="─", bottom="─", left="│", right="│",
        top_left="╭", top_right="╮", bottom_left="╰", bottom_right="╯",
        middle_left="├", middle_right="┤", middle="┼",
        middle_top="┬", middle_bottom="┴",
    )


def thick_border() -> Border:
    """Heavy box drawing characters."""
    return Border(
        top="━", bottom="━", left="┃", right="┃",
        top_left="┏", top_right="┓", bottom_left="┗", bottom_right="┛",
        middle_left="┣", middle_right="┫", middle="╋",
        middle_top="┳", middle_bottom="┻",
    )


def double_border() -> Border:
    """Double-line box drawing characters."""
    return Border(
        top="═", bottom="═", left="║", right="║",
        top_left="╔", top_right="╗", bottom_left="╚", bottom_right="╝",
        middle_left="╠", middle_right="╣", middle="╬",
        middle_top="╦", middle_bottom="╩",
    )


def ascii_border() -> Border:
    """Plain ASCII border using +, -, and |."""
    return Border(
        top="-", bottom="-", left="|", right="|",
        top_left="+", top_right="+", bottom_left="+", bottom_right="+",
        middle_left="+", middle_right="+", middle="+",
        middle_top="+", middle_bottom="+",
    )


def markdown_border() -> Border:
    """Pipe-and-dash border suitable for Markdown tables.

    For best results, disable the top and bottom border::

        table.New().border(markdown_border()).border_top(False).border_bottom(False)
    """
    return Border(
        top="-", bottom="-", left="|", right="|",
        top_left="|", top_right="|", bottom_left="|", bottom_right="|",
        middle_left="|", middle_right="|", middle="|",
        middle_top="|", middle_bottom="|",
    )


def hidden_border() -> Border:
    """Space characters — preserves layout spacing without visible lines."""
    return Border(
        top=" ", bottom=" ", left=" ", right=" ",
        top_left=" ", top_right=" ", bottom_left=" ", bottom_right=" ",
        middle_left=" ", middle_right=" ", middle=" ",
        middle_top=" ", middle_bottom=" ",
    )


def block_border() -> Border:
    """Full block characters (█) on all sides."""
    return Border(
        top="█", bottom="█", left="█", right="█",
        top_left="█", top_right="█", bottom_left="█", bottom_right="█",
        middle_left="█", middle_right="█", middle="█",
        middle_top="█", middle_bottom="█",
    )


def outer_half_block_border() -> Border:
    """Half-block border that sits outside the frame."""
    return Border(
        top="▀", bottom="▄", left="▌", right="▐",
        top_left="▛", top_right="▜", bottom_left="▙", bottom_right="▟",
    )


def inner_half_block_border() -> Border:
    """Half-block border that sits inside the frame."""
    return Border(
        top="▄", bottom="▀", left="▐", right="▌",
        top_left="▗", top_right="▖", bottom_left="▝", bottom_right="▘",
    )
