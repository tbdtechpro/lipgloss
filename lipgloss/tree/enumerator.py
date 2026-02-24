"""
Built-in tree enumerators.

Port of: tree/enumerator.go

Each enumerator is a callable with signature:
  fn(children: Children, index: int) -> str

Built-ins:
  default_enumerator — "├── " for non-last children, "└── " for the last
  rounded_enumerator — "├── " for non-last children, "╰── " for the last
"""
