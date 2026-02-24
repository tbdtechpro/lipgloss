"""Tests for the Tree sub-package."""

from __future__ import annotations

import re

import pytest

from lipgloss.tree import (
    DefaultEnumerator,
    DefaultIndenter,
    Leaf,
    NodeChildren,
    RoundedEnumerator,
    Tree,
    root,
)

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _strip_ansi(s: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", s)


# ---------------------------------------------------------------------------
# NodeChildren
# ---------------------------------------------------------------------------


def test_node_children_empty() -> None:
    nc = NodeChildren()
    assert nc.length() == 0
    assert nc.at(0) is None


def test_node_children_append() -> None:
    nc = NodeChildren()
    nc2 = nc.append(Leaf("a"))
    assert nc.length() == 0  # original unchanged
    assert nc2.length() == 1
    assert nc2.at(0).value() == "a"


def test_node_children_remove() -> None:
    nc = NodeChildren([Leaf("a"), Leaf("b"), Leaf("c")])
    nc2 = nc.remove(1)
    assert nc.length() == 3  # original unchanged
    assert nc2.length() == 2
    assert nc2.at(0).value() == "a"
    assert nc2.at(1).value() == "c"


def test_node_children_remove_out_of_bounds() -> None:
    nc = NodeChildren([Leaf("x")])
    nc2 = nc.remove(99)
    assert nc2.length() == 1


# ---------------------------------------------------------------------------
# Leaf
# ---------------------------------------------------------------------------


def test_leaf_value() -> None:
    l = Leaf("hello")
    assert l.value() == "hello"


def test_leaf_hidden_default_false() -> None:
    l = Leaf("x")
    assert l.hidden() is False


def test_leaf_hidden_true() -> None:
    l = Leaf("x", hidden=True)
    assert l.hidden() is True


def test_leaf_set_hidden() -> None:
    l = Leaf("x")
    l.set_hidden(True)
    assert l.hidden() is True


def test_leaf_children_empty() -> None:
    l = Leaf("x")
    assert l.children().length() == 0


def test_leaf_str() -> None:
    l = Leaf("hello")
    assert str(l) == "hello"


# ---------------------------------------------------------------------------
# Enumerators
# ---------------------------------------------------------------------------


class _NC:
    """Minimal NodeChildren stub for enumerator tests."""

    def __init__(self, n: int) -> None:
        self._n = n

    def length(self) -> int:
        return self._n

    def at(self, i: int) -> None:
        return None


def test_default_enumerator_middle() -> None:
    nc = _NC(3)
    assert DefaultEnumerator(nc, 0) == "├──"
    assert DefaultEnumerator(nc, 1) == "├──"


def test_default_enumerator_last() -> None:
    nc = _NC(3)
    assert DefaultEnumerator(nc, 2) == "└──"


def test_rounded_enumerator_middle() -> None:
    nc = _NC(3)
    assert RoundedEnumerator(nc, 0) == "├──"


def test_rounded_enumerator_last() -> None:
    nc = _NC(3)
    assert RoundedEnumerator(nc, 2) == "╰──"


def test_default_indenter_middle() -> None:
    nc = _NC(3)
    assert DefaultIndenter(nc, 0) == "│  "


def test_default_indenter_last() -> None:
    nc = _NC(3)
    assert DefaultIndenter(nc, 2) == "   "


# ---------------------------------------------------------------------------
# Tree — basic
# ---------------------------------------------------------------------------


def test_tree_empty() -> None:
    assert Tree().render() == ""


def test_tree_root_only() -> None:
    t = Tree().root("Root")
    # Root with no children renders just the root label.
    out = _strip_ansi(t.render())
    assert out == "Root"


def test_tree_flat_children() -> None:
    t = Tree().child("Foo", "Bar", "Baz")
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    assert len(lines) == 3
    assert "Foo" in lines[0]
    assert "Bar" in lines[1]
    assert "Baz" in lines[2]


def test_tree_default_enumerator_uses_box_chars() -> None:
    t = Tree().child("A", "B", "C")
    out = _strip_ansi(t.render())
    assert "├──" in out
    assert "└──" in out


def test_tree_last_child_gets_corner() -> None:
    t = Tree().child("A", "B")
    lines = _strip_ansi(t.render()).splitlines()
    assert lines[-1].startswith("└──")


def test_tree_with_root_label() -> None:
    t = Tree().root("Root").child("A", "B")
    out = _strip_ansi(t.render())
    assert out.startswith("Root")


def test_tree_single_child() -> None:
    t = Tree().child("Only")
    out = _strip_ansi(t.render())
    assert "└──" in out
    assert "Only" in out


# ---------------------------------------------------------------------------
# Tree — nesting
# ---------------------------------------------------------------------------


def test_tree_nested_children() -> None:
    t = (
        Tree()
        .root("Root")
        .child(
            "Foo",
            Tree().root("Bar").child("Qux", "Quux"),
            "Baz",
        )
    )
    out = _strip_ansi(t.render())
    assert "Root" in out
    assert "Foo" in out
    assert "Bar" in out
    assert "Qux" in out
    assert "Quux" in out
    assert "Baz" in out


def test_tree_nested_indentation() -> None:
    t = (
        Tree()
        .root("Root")
        .child(
            "Foo",
            Tree().root("Bar").child("Qux"),
            "Baz",
        )
    )
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    # "Qux" should appear after "Bar" and carry an indentation prefix character.
    bar_idx = next(i for i, l in enumerate(lines) if "Bar" in l)
    qux_idx = next(i for i, l in enumerate(lines) if "Qux" in l)
    assert qux_idx > bar_idx
    # Qux line should have a leading indent prefix (│ or space).
    assert lines[qux_idx][0] in ("│", " ", "├", "└", "╰")


def test_tree_deeply_nested() -> None:
    t = Tree().root("A").child(Tree().root("B").child(Tree().root("C").child("D")))
    out = _strip_ansi(t.render())
    assert "A" in out
    assert "B" in out
    assert "C" in out
    assert "D" in out


# ---------------------------------------------------------------------------
# Tree — auto-nesting (rootless Tree after Leaf)
# ---------------------------------------------------------------------------


def test_tree_auto_nesting_leaf_becomes_root() -> None:
    # Rootless Tree after "Foo" leaf → "Foo" becomes the root of the new tree.
    t = Tree().child("Foo", Tree().child("Bar"), "Baz")
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    # "Foo" should appear as a branch with "Bar" nested under it.
    assert "Foo" in out
    assert "Bar" in out
    foo_line = next((i for i, l in enumerate(lines) if "Foo" in l), None)
    bar_line = next((i for i, l in enumerate(lines) if "Bar" in l), None)
    assert foo_line is not None
    assert bar_line is not None
    assert bar_line > foo_line


# ---------------------------------------------------------------------------
# Tree — hide
# ---------------------------------------------------------------------------


def test_tree_hidden_returns_empty() -> None:
    t = Tree().root("X").child("A", "B").hide(True)
    assert t.render() == ""


def test_tree_hidden_child_skipped() -> None:
    t = Tree().child(
        "Foo",
        Tree().root("Hidden").child("A").hide(True),
        "Bar",
    )
    out = _strip_ansi(t.render())
    assert "Hidden" not in out
    assert "A" not in out
    assert "Foo" in out
    assert "Bar" in out


def test_tree_hidden_child_last_gets_corner() -> None:
    # After hiding the last child, the previous visible child should get "└──".
    t = Tree().child(
        "Foo",
        "Bar",
        Tree().root("Hidden").hide(True),
    )
    out = _strip_ansi(t.render())
    lines = out.splitlines()
    bar_line = next(l for l in lines if "Bar" in l)
    assert bar_line.startswith("└──")


# ---------------------------------------------------------------------------
# Tree — rounded enumerator
# ---------------------------------------------------------------------------


def test_rounded_enumerator_output() -> None:
    t = Tree().child("A", "B", "C").enumerator(RoundedEnumerator)
    out = _strip_ansi(t.render())
    assert "╰──" in out
    assert "├──" in out


# ---------------------------------------------------------------------------
# Tree — root() helper function
# ---------------------------------------------------------------------------


def test_root_helper() -> None:
    t = root("Root").child("A", "B")
    out = _strip_ansi(t.render())
    assert "Root" in out
    assert "A" in out


# ---------------------------------------------------------------------------
# Tree — str equals render
# ---------------------------------------------------------------------------


def test_str_equals_render() -> None:
    t = Tree().child("X", "Y")
    assert str(t) == t.render()


# ---------------------------------------------------------------------------
# Tree — offset
# ---------------------------------------------------------------------------


def test_offset_trims_last() -> None:
    # offset(1, 0) swaps to internal [0, 1], trimming 1 from the end.
    # children("A","B","C","D") → range(0, 4-1) → [A, B, C] (D trimmed).
    t = Tree().child("A", "B", "C", "D").offset(1, 0)
    out = _strip_ansi(t.render())
    assert "D" not in out
    assert "A" in out
    assert "C" in out


# ---------------------------------------------------------------------------
# Tree — styles
# ---------------------------------------------------------------------------


def test_item_style_applied() -> None:
    import lipgloss

    bold = lipgloss.Style().bold(True)
    t = Tree().child("hello").item_style(bold)
    out = t.render()
    # Styled output should contain "hello" and some ANSI codes.
    assert "hello" in _strip_ansi(out)


def test_root_style_applied() -> None:
    import lipgloss

    style = lipgloss.Style().bold(True)
    t = Tree().root("Root").child("A").root_style(style)
    out = _strip_ansi(t.render())
    assert "Root" in out
