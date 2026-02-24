"""
List — renders bullet/numbered/nested lists.

Port of: list/list.go

Key API (all setters return self for chaining):
  List(*items)
  .item(*items)
  .enumerator(fn: Callable[[Items, int], str])
  .enumerator_style(s: Style)
  .item_style(s: Style)
  .hide(hidden: bool)
  .render() -> str

Items can be str (leaf) or another List instance (nested sub-list).

The enumerator callable signature is:
  fn(items: Items, index: int) -> str
where Items provides .at(i) and .__len__().
"""
from __future__ import annotations

from typing import Any, Callable

from ..size import width as _vis_width
from ..style import Style
from .enumerator import Bullet


class Items:
    """Sequence wrapper passed to enumerator/style functions.

    Mirrors the Go Items/Children interface used by enumerators.
    """

    def __init__(self, items: list[Any]) -> None:
        self._items = items

    def at(self, i: int) -> Any:
        return self._items[i]

    def length(self) -> int:
        return len(self._items)

    def __len__(self) -> int:
        return len(self._items)


class List:
    """Renders a bullet/numbered list, supporting arbitrary nesting.

    Standalone port of list/list.go (without delegating to tree.Tree).
    """

    def __init__(self, *items: Any) -> None:
        self._items: list[Any] = []
        self._enumerator: Callable[[Items, int], str] = Bullet
        # Default enumerator style adds 1 space of right padding (matches tree default).
        self._enum_style: Style = Style().padding_right(1)
        self._item_style: Style = Style()
        self._hidden: bool = False
        for it in items:
            self.item(it)

    # ------------------------------------------------------------------
    # Setters
    # ------------------------------------------------------------------

    def item(self, it: Any) -> "List":
        """Append a single item (str or nested List)."""
        self._items.append(it)
        return self

    def items(self, *its: Any) -> "List":
        """Append multiple items."""
        for it in its:
            self.item(it)
        return self

    def enumerator(self, fn: Callable[[Items, int], str]) -> "List":
        """Set the enumerator function."""
        self._enumerator = fn
        return self

    def enumerator_style(self, style: Style) -> "List":
        """Set the style applied to each enumeration prefix."""
        self._enum_style = style
        return self

    def item_style(self, style: Style) -> "List":
        """Set the style applied to each item's text."""
        self._item_style = style
        return self

    def hide(self, hidden: bool) -> "List":
        """Hide/show this list."""
        self._hidden = hidden
        return self

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> str:
        return str(self)

    def __str__(self) -> str:
        if self._hidden:
            return ""
        return self._render("")

    def _render(self, prefix: str) -> str:
        """Render this list, prepending *prefix* to every line.

        *prefix* accumulates the indentation from parent lists.
        """
        if not self._items:
            return ""

        items_obj = Items(self._items)

        # Build the styled prefix for each item and find the max width.
        styled_prefixes: list[str] = []
        for i in range(len(self._items)):
            raw = self._enumerator(items_obj, i)
            styled = self._enum_style.render(raw)
            styled_prefixes.append(styled)

        max_w = max((_vis_width(p) for p in styled_prefixes), default=0)

        # Child indent = current prefix + spaces equal to the widest prefix.
        child_indent = prefix + " " * max_w

        lines: list[str] = []
        for i, it in enumerate(self._items):
            styled_prefix = styled_prefixes[i]
            prefix_w = _vis_width(styled_prefix)

            # Left-pad shorter prefixes so all items line up (right-align).
            if prefix_w < max_w:
                styled_prefix = " " * (max_w - prefix_w) + styled_prefix

            if isinstance(it, List):
                if it._hidden:
                    continue
                # A nested list has an empty root value (matching Go behaviour
                # where list delegates to tree.Tree with no root set).
                # Only its children are rendered with the increased indent.
                nested = it._render(child_indent)
                if nested:
                    lines.append(nested)
            else:
                item_text = self._item_style.render(str(it))
                lines.append(prefix + styled_prefix + item_text)

        return "\n".join(lines)
