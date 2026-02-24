"""
List rendering sub-package.

Port of: list/list.go, list/enumerator.go

Usage::

    from lipgloss import list as lst

    l = (
        lst.List("Glossier", "Claire's Boutique", "Nyx", "Mac", "Milk")
        .enumerator(lst.Roman)
    )
    print(l.render())
"""
