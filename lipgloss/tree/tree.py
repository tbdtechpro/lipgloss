"""
Tree — renders hierarchical tree structures.

Port of: tree/tree.go, tree/renderer.go

Key API (all setters return self for chaining):
  Tree()
  .root(label: str)
  .child(*items)                    — str (leaf) or Tree (branch)
  .enumerator(fn)
  .root_style(s: Style)
  .item_style(s: Style)
  .enumerator_style(s: Style)
  .render() -> str

The enumerator callable signature is:
  fn(children: Children, index: int) -> str
returning the prefix string for each child (e.g. "├── " or "└── ").
"""
