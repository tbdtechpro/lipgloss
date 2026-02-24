"""
Built-in tree enumerators and indenters.

Port of: tree/enumerator.go

Each enumerator is a callable with signature:
  fn(children: NodeChildren, index: int) -> str

Built-ins:
  DefaultEnumerator — "├──" for non-last children, "└──" for the last
  RoundedEnumerator — "├──" for non-last children, "╰──" for the last
  DefaultIndenter   — "│  " for non-last children, "   " for the last
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .children import NodeChildren


def DefaultEnumerator(children: "NodeChildren", index: int) -> str:
    """Standard tree enumerator using box-drawing characters.

    ├── Foo
    ├── Bar
    └── Baz
    """
    if children.length() - 1 == index:
        return "└──"
    return "├──"


def RoundedEnumerator(children: "NodeChildren", index: int) -> str:
    """Tree enumerator with a rounded corner for the last item.

    ├── Foo
    ├── Bar
    ╰── Baz
    """
    if children.length() - 1 == index:
        return "╰──"
    return "├──"


def DefaultIndenter(children: "NodeChildren", index: int) -> str:
    """Standard tree indenter connecting sibling elements.

    ├── Foo
    │   ├── Bar
    │   └── Baz
    └── Qux
        └── Quux
    """
    if children.length() - 1 == index:
        return "   "
    return "│  "
