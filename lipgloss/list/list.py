"""
List — renders bullet/numbered/nested lists.

Port of: list/list.go

Key API (all setters return self for chaining):
  List(*items)
  .item(*items)
  .enumerator(fn: Callable[[Items, int], str])
  .enumerator_style(s: Style)
  .item_style(s: Style)
  .render() -> str

Items can be str (leaf) or another List instance (nested sub-list).

The enumerator callable signature is:
  fn(items: Items, index: int) -> str
where Items provides .at(i) -> str and .__len__().
"""
