"""
Border definitions.

Port of: borders.go

Defines the Border dataclass and all predefined border factories:
  normal_border()   — single-line box drawing
  rounded_border()  — single-line with rounded corners
  double_border()   — double-line box drawing
  thick_border()    — heavy box drawing
  ascii_border()    — plain ASCII (+, -, |)
  markdown_border() — pipe-and-dash for markdown tables
  hidden_border()   — spaces (preserves spacing, no visible lines)
"""
