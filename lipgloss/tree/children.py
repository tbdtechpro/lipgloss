"""
Node and Children types for the tree sub-package.

Port of: tree/children.go, tree/tree.go (Node/Leaf definitions)

Types:
  Node      — protocol: .value() -> str, .hidden() -> bool, .children() -> Children
  Leaf(str) — terminal node with no children; implements Node
  NodeChildren — sequence of Node with .at(i) -> Node and .length() -> int
"""

from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Node(Protocol):
    """Protocol for tree nodes."""

    def value(self) -> str: ...

    def hidden(self) -> bool: ...

    def set_hidden(self, h: bool) -> None: ...

    def set_value(self, v: Any) -> None: ...

    def children(self) -> "NodeChildren": ...

    def __str__(self) -> str: ...


class NodeChildren:
    """Ordered list of Node objects.

    Port of: NodeChildren in tree/children.go
    Immutable-style: append/remove return new instances.
    """

    def __init__(self, nodes: list[Any] | None = None) -> None:
        self._nodes: list[Any] = list(nodes) if nodes else []

    def at(self, i: int) -> Any:
        if 0 <= i < len(self._nodes):
            return self._nodes[i]
        return None

    def length(self) -> int:
        return len(self._nodes)

    def __len__(self) -> int:
        return len(self._nodes)

    def append(self, node: Any) -> "NodeChildren":
        return NodeChildren(self._nodes + [node])

    def remove(self, index: int) -> "NodeChildren":
        nodes = self._nodes[:]
        if 0 <= index < len(nodes):
            del nodes[index]
        return NodeChildren(nodes)


class Leaf:
    """Terminal tree node with no children.

    Port of: Leaf in tree/tree.go
    """

    def __init__(self, value: Any = "", hidden: bool = False) -> None:
        self._value: str = ""
        self._hidden: bool = hidden
        self.set_value(value)

    def value(self) -> str:
        return self._value

    def set_value(self, v: Any) -> None:
        if isinstance(v, str):
            self._value = v
        elif hasattr(v, "__str__"):
            self._value = str(v)
        else:
            self._value = repr(v)

    def hidden(self) -> bool:
        return self._hidden

    def set_hidden(self, h: bool) -> None:
        self._hidden = h

    def children(self) -> NodeChildren:
        return NodeChildren()

    def __str__(self) -> str:
        return self._value
