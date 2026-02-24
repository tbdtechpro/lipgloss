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
"""
