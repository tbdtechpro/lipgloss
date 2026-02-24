"""
Tree rendering sub-package.

Port of: tree/tree.go, tree/children.go, tree/enumerator.go, tree/renderer.go

Usage::

    from lipgloss import tree

    t = (
        tree.Tree()
        .root(".")
        .child("macOS", "Linux", "BSD")
    )
    print(t.render())

Nested trees::

    t = (
        tree.Tree()
        .root(".")
        .child(
            tree.Tree().root("src").child("main.py", "utils.py"),
            tree.Tree().root("tests").child("test_main.py"),
        )
    )
    print(t.render())
"""

from .children import Leaf, Node, NodeChildren
from .enumerator import DefaultEnumerator, DefaultIndenter, RoundedEnumerator
from .tree import Tree, new_tree, root

__all__ = [
    # Core types
    "Tree",
    "Leaf",
    "Node",
    "NodeChildren",
    # Convenience constructors
    "new_tree",
    "root",
    # Enumerators
    "DefaultEnumerator",
    "RoundedEnumerator",
    "DefaultIndenter",
]
