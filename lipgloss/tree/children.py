"""
Node and Children types for the tree sub-package.

Port of: tree/children.go, tree/tree.go (Node/Leaf definitions)

Types:
  Node      — protocol: .value() -> str, .hidden() -> bool, .children() -> Children
  Leaf(str) — terminal node with no children; implements Node
  Children  — sequence of Node with .at(i) -> Node and .__len__()
"""
