"""
tree.py — styled tree view of the current directory, ported from examples/tree/files/main.go

Run with:  python examples/tree.py
"""

import os
import sys

import lipgloss
from lipgloss import tree as tr


def add_branches(root: tr.Tree, path: str) -> None:
    """Recursively add directory entries as tree children."""
    try:
        entries = sorted(os.scandir(path), key=lambda e: e.name)
    except PermissionError:
        return

    for entry in entries:
        # Skip hidden files/directories.
        if entry.name.startswith("."):
            continue

        if entry.is_dir(follow_symlinks=False):
            branch = tr.root(entry.name)
            root.child(branch)
            add_branches(branch, entry.path)
        else:
            root.child(entry.name)


def main() -> None:
    enumerator_style = lipgloss.Style().foreground(lipgloss.Color("240")).padding_right(1)
    item_style = lipgloss.Style().foreground(lipgloss.Color("99")).bold(True).padding_right(1)

    cwd = os.getcwd()

    t = (
        tr.root(cwd)
        .enumerator_style(enumerator_style)
        .root_style(item_style)
        .item_style(item_style)
    )

    add_branches(t, ".")

    print(t.render())


if __name__ == "__main__":
    main()
