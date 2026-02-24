"""
Built-in list enumerators.

Port of: list/enumerator.go

Each enumerator is a callable with signature:
  fn(items: Items, index: int) -> str

Built-ins:
  Bullet    — "•" prefix for every item
  Asterisk  — "*" prefix for every item
  Dash      — "-" prefix for every item
  Arabic    — "1.", "2.", "3." …
  Alphabet  — "A.", "B.", "C." … (uppercase, wraps at ZZ. etc.)
  Roman     — "I.", "II.", "III." … (uppercase Roman numerals)
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .list import Items

_ABC_LEN = 26


def Alphabet(items: "Items", i: int) -> str:
    """Alphabetical enumeration: A., B., … Z., AA., AB., …"""
    if i >= _ABC_LEN * _ABC_LEN + _ABC_LEN:
        return (
            chr(ord("A") + i // _ABC_LEN // _ABC_LEN - 1)
            + chr(ord("A") + (i // _ABC_LEN) % _ABC_LEN - 1)
            + chr(ord("A") + i % _ABC_LEN)
            + "."
        )
    if i >= _ABC_LEN:
        return chr(ord("A") + i // _ABC_LEN - 1) + chr(ord("A") + i % _ABC_LEN) + "."
    return chr(ord("A") + i % _ABC_LEN) + "."


def Arabic(items: "Items", i: int) -> str:
    """Arabic numeral enumeration: 1., 2., 3., …"""
    return f"{i + 1}."


def Roman(items: "Items", i: int) -> str:
    """Roman numeral enumeration: I., II., III., IV., …"""
    roman = ["M", "CM", "D", "CD", "C", "XC", "L", "XL", "X", "IX", "V", "IV", "I"]
    arabic = [1000, 900, 500, 400, 100, 90, 50, 40, 10, 9, 5, 4, 1]
    result: list[str] = []
    for v, value in enumerate(arabic):
        while i >= value - 1:
            i -= value
            result.append(roman[v])
    result.append(".")
    return "".join(result)


def Bullet(items: "Items", i: int) -> str:
    """Bullet enumeration: • for every item."""
    return "•"


def Asterisk(items: "Items", i: int) -> str:
    """Asterisk enumeration: * for every item."""
    return "*"


def Dash(items: "Items", i: int) -> str:
    """Dash enumeration: - for every item."""
    return "-"
