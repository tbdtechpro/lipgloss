"""
Built-in list enumerators.

Port of: list/enumerator.go

Each enumerator is a callable with signature:
  fn(items: Items, index: int) -> str

Built-ins:
  Bullet   — "• " prefix for every item
  Arabic   — "1.", "2.", "3." …
  Alphabet — "a.", "b.", "c." …
  Roman    — "i.", "ii.", "iii." …  (lowercase Roman numerals)
  Tree     — tree branch characters (delegates to tree enumerator logic)
"""
