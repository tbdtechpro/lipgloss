"""
Tree — renders hierarchical tree structures.

Port of: tree/tree.go, tree/renderer.go

Key API (all setters return self for chaining):
  Tree()
  .root(label: str)
  .child(*items)                    — str (leaf) or Tree (branch)
  .enumerator(fn)
  .indenter(fn)
  .root_style(s: Style)
  .item_style(s: Style)
  .enumerator_style(s: Style)
  .hide(hidden: bool)
  .offset(start, end)
  .render() -> str

The enumerator callable signature is:
  fn(children: NodeChildren, index: int) -> str
returning the prefix string for each child (e.g. "├──" or "└──").
"""

from __future__ import annotations

from typing import Any, Callable

from ..join import join_horizontal, join_vertical
from ..position import Left, Top
from ..size import height as _height
from ..size import width as _width
from ..style import Style
from .children import Leaf, NodeChildren
from .enumerator import DefaultEnumerator, DefaultIndenter


def _ensure_parent(nodes: NodeChildren, item: "Tree") -> tuple["Tree", int]:
    """Auto-nest a rootless Tree under its most recent sibling.

    Port of: ensureParent in tree/tree.go

    If *item* has no root value and *nodes* is non-empty:
    - If the last sibling is a Tree  → merge item's children into it.
    - If the last sibling is a Leaf  → promote the Leaf to be item's root.
    Returns (new_item, remove_index) where remove_index=-1 means no removal needed.
    """
    if item._value != "" or nodes.length() == 0:
        return item, -1

    j = nodes.length() - 1
    parent = nodes.at(j)

    if isinstance(parent, Tree):
        for i in range(item._children.length()):
            parent.child(item._children.at(i))
        return parent, j

    if isinstance(parent, Leaf):
        item._value = parent.value()
        return item, j

    return item, -1


class _Renderer:
    """Internal renderer for Tree nodes.

    Port of: renderer / newRenderer() in tree/renderer.go
    """

    def __init__(self) -> None:
        self.style_root: Style = Style()
        self.style_enum_func: Callable[[NodeChildren, int], Style] = (
            lambda c, i: Style().padding_right(1)
        )
        self.style_item_func: Callable[[NodeChildren, int], Style] = lambda c, i: Style()
        self.enumerator: Callable[[NodeChildren, int], str] = DefaultEnumerator
        self.indenter: Callable[[NodeChildren, int], str] = DefaultIndenter

    def render(self, node: Any, root: bool, prefix: str) -> str:
        """Recursively render *node* and its children.

        Port of: renderer.render() in tree/renderer.go
        """
        if node.hidden():
            return ""

        strs: list[str] = []
        max_len = 0

        children: NodeChildren = node.children()

        # Print root label when rendering as the root node.
        if node.value() and root:
            strs.append(self.style_root.render(node.value()))

        # First pass: compute max prefix width.
        # Remove hidden next-siblings so the enumerator correctly identifies the
        # last *visible* child (matching Go's behaviour).
        i = 0
        while i < children.length():
            if i < children.length() - 1:
                next_child = children.at(i + 1)
                if next_child is not None and next_child.hidden():
                    children = children.remove(i + 1)
                    continue  # re-examine same index with new next sibling
            pfx = self.enumerator(children, i)
            pfx = self.style_enum_func(children, i).render(pfx)
            max_len = max(_width(pfx), max_len)
            i += 1

        # Second pass: render each child.
        for i in range(children.length()):
            child = children.at(i)
            if child is None or child.hidden():
                continue

            indent = self.indenter(children, i)
            node_prefix = self.enumerator(children, i)
            enum_style = self.style_enum_func(children, i)
            item_style = self.style_item_func(children, i)

            node_prefix = enum_style.render(node_prefix)
            pad = max_len - _width(node_prefix)
            if pad > 0:
                node_prefix = " " * pad + node_prefix

            item = item_style.render(child.value())
            multiline_prefix = prefix

            # Extend node_prefix height to match a multiline item.
            while _height(item) > _height(node_prefix):
                node_prefix = join_vertical(Left, node_prefix, enum_style.render(indent))

            # Extend accumulated prefix to match node_prefix height.
            while _height(node_prefix) > _height(multiline_prefix):
                multiline_prefix = join_vertical(Left, multiline_prefix, prefix)

            strs.append(join_horizontal(Top, multiline_prefix, node_prefix, item))

            # Recurse into child's subtree using its own renderer if set.
            renderer = self
            if isinstance(child, Tree) and child._renderer is not None:
                renderer = child._renderer

            child_prefix = prefix + enum_style.render(indent)
            s = renderer.render(child, False, child_prefix)
            if s:
                strs.append(s)

        return "\n".join(strs)


class Tree:
    """Hierarchical tree node with configurable rendering.

    Port of: Tree in tree/tree.go
    """

    def __init__(self) -> None:
        self._value: str = ""
        self._hidden: bool = False
        self._offset: list[int] = [0, 0]
        self._children: NodeChildren = NodeChildren()
        self._renderer: _Renderer | None = None

    def _ensure_renderer(self) -> _Renderer:
        if self._renderer is None:
            self._renderer = _Renderer()
        return self._renderer

    # ------------------------------------------------------------------
    # Node protocol methods (allows Tree to appear as a child of another Tree)
    # ------------------------------------------------------------------

    def value(self) -> str:
        return self._value

    def set_value(self, v: Any) -> None:
        self.root(v)

    def hidden(self) -> bool:
        return self._hidden

    def set_hidden(self, h: bool) -> None:
        self._hidden = h

    def children(self) -> NodeChildren:
        """Return children with offset applied."""
        data: list[Any] = []
        end = self._children.length() - self._offset[1]
        for i in range(self._offset[0], end):
            data.append(self._children.at(i))
        return NodeChildren(data)

    def __str__(self) -> str:
        return self._ensure_renderer().render(self, root=True, prefix="")

    # ------------------------------------------------------------------
    # Builder setters
    # ------------------------------------------------------------------

    def root(self, label: Any) -> "Tree":
        """Set the root label of this tree."""
        if isinstance(label, Tree):
            self._value = label._value
            self.child(label._children)
        elif isinstance(label, str):
            self._value = label
        else:
            self._value = str(label)
        return self

    def child(self, *items: Any) -> "Tree":
        """Append children to this tree.

        Accepts str (leaf), Tree (branch), NodeChildren, Leaf, or any object
        whose __str__ is used as the leaf value.
        """
        for item in items:
            if isinstance(item, Tree):
                new_item, rm = _ensure_parent(self._children, item)
                if rm >= 0:
                    self._children = self._children.remove(rm)
                self._children = self._children.append(new_item)
            elif isinstance(item, NodeChildren):
                for j in range(item.length()):
                    self._children = self._children.append(item.at(j))
            elif isinstance(item, Leaf):
                self._children = self._children.append(item)
            elif isinstance(item, str):
                self._children = self._children.append(Leaf(item))
            elif item is None:
                continue
            else:
                self._children = self._children.append(Leaf(str(item)))
        return self

    def hide(self, h: bool) -> "Tree":
        """Hide or show this tree node."""
        self._hidden = h
        return self

    def offset(self, start: int, end: int) -> "Tree":
        """Set start/end child offset for scrolling."""
        if start > end:
            start, end = end, start
        start = max(start, 0)
        if end < 0 or end > self._children.length():
            end = self._children.length()
        self._offset = [start, end]
        return self

    def enumerator(self, fn: Callable[[NodeChildren, int], str]) -> "Tree":
        """Set the enumerator function."""
        self._ensure_renderer().enumerator = fn
        return self

    def indenter(self, fn: Callable[[NodeChildren, int], str]) -> "Tree":
        """Set the indenter function."""
        self._ensure_renderer().indenter = fn
        return self

    def root_style(self, style: Style) -> "Tree":
        """Set the style applied to the root label."""
        self._ensure_renderer().style_root = style
        return self

    def enumerator_style(self, style: Style) -> "Tree":
        """Set a static style for all enumerator prefixes."""
        self._ensure_renderer().style_enum_func = lambda c, i: style
        return self

    def enumerator_style_func(self, fn: Callable[[NodeChildren, int], Style]) -> "Tree":
        """Set a conditional style function for enumerator prefixes."""
        self._ensure_renderer().style_enum_func = fn
        return self

    def item_style(self, style: Style) -> "Tree":
        """Set a static style for all item text."""
        self._ensure_renderer().style_item_func = lambda c, i: style
        return self

    def item_style_func(self, fn: Callable[[NodeChildren, int], Style]) -> "Tree":
        """Set a conditional style function for item text."""
        self._ensure_renderer().style_item_func = fn
        return self

    # ------------------------------------------------------------------
    # Render
    # ------------------------------------------------------------------

    def render(self) -> str:
        return str(self)


def new_tree() -> Tree:
    """Return a new, empty Tree. Alias for Tree()."""
    return Tree()


def root(label: Any) -> Tree:
    """Return a new Tree with the given root label set.

    Shorthand for Tree().root(label).
    """
    return Tree().root(label)
