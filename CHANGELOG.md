# Changelog

All notable changes to the Python port of Lip Gloss are documented here.

This file follows the [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) format.
Versions follow [Semantic Versioning](https://semver.org/).

---

## [Unreleased]

### Planned
- Task 10: Bubble Tea integration tests and examples
- Ongoing test coverage improvements

---

## [0.1.0] — 2026-02-24

Initial pre-alpha release of the Python port. All core features of the Go Lip Gloss library
are implemented and tested.

### Added

#### Core style system (`lipgloss/style.py`)
- `Style` — immutable fluent builder; every setter returns a new copy
- All boolean text-formatting properties: `bold`, `italic`, `underline`, `strikethrough`,
  `reverse`, `blink`, `faint`, `underline_spaces`, `strikethrough_spaces`, `color_whitespace`
- Color properties: `foreground`, `background`
- Dimension properties: `width`, `height`, `max_width`, `max_height`
- Padding (all four sides + CSS shorthand 1–4 values)
- Margin (all four sides + CSS shorthand + `margin_background`)
- Border properties: `border_style`, per-side enable (`border_top` etc.), per-side foreground
  and background colors; `border` shorthand
- Alignment: `align`, `align_horizontal`, `align_vertical`
- Misc: `inline`, `tab_width`, `transform`, `set_string`
- Full getter (`get_*`) and unsetter (`unset_*`) for every property
- `inherit(parent)` — copies only unset properties; margins/padding never inherited
- `copy()` — independent deep copy
- `render(*strings)` — applies all properties and returns an ANSI-escaped string

#### Color system (`lipgloss/color.py`)
- `TerminalColor` — Protocol type for all color values
- `NoColor` — explicit no-color sentinel
- `Color(str)` — hex (`#RRGGBB`) or ANSI index string; auto-degrades across profiles
- `ANSIColor(int)` — convenience wrapper for ANSI 0–15
- `AdaptiveColor(light, dark)` — chooses light/dark variant at render time
- `CompleteColor(true_color, ansi256, ansi)` — explicit per-profile values
- `CompleteAdaptiveColor(light, dark)` — combines adaptive selection with per-profile values

#### Renderer (`lipgloss/renderer.py`)
- `ColorProfile` enum: `TrueColor`, `ANSI256`, `ANSI`, `ASCII`
- `Renderer` — wraps an output stream; detects color profile and dark-background status
- `default_renderer()`, `set_default_renderer(r)`, `new_renderer(w)` module-level helpers
- `Renderer.new_style()` — creates a `Style` bound to this renderer

#### Border system (`lipgloss/borders.py`)
- `Border` dataclass with all 14 fields
- Factory functions: `normal_border`, `rounded_border`, `thick_border`, `double_border`,
  `ascii_border`, `markdown_border`, `hidden_border`, `block_border`,
  `outer_half_block_border`, `inner_half_block_border`

#### Layout utilities
- `join_horizontal(pos, *strings)` — join blocks side by side (`lipgloss/join.py`)
- `join_vertical(pos, *strings)` — stack blocks vertically (`lipgloss/join.py`)
- `place(width, height, h_pos, v_pos, s, *opts)` — place string in a box (`lipgloss/position.py`)
- `place_horizontal(width, pos, s, *opts)` — horizontal placement
- `place_vertical(height, pos, s, *opts)` — vertical placement
- `Position` type alias (`float`); constants `Top`, `Bottom`, `Left`, `Right`, `Center`
- `width(s)`, `height(s)`, `size(s)` — ANSI-aware measurement (`lipgloss/size.py`)
- `WhitespaceOption` helpers: `whitespace_foreground`, `whitespace_background`,
  `whitespace_chars` (`lipgloss/whitespace.py`)

#### Per-rune styling (`lipgloss/runes.py`)
- `style_runes(s, indices, matched, unmatched)` — apply different styles to individual characters

#### Table sub-package (`lipgloss/table/`)
- `Table` — fluent builder with `headers`, `rows`, `row`, `border`, `border_style`,
  `border_top/bottom/left/right/header/column`, `style_func`, `width`, `height`, `offset`
- `HeaderRow` — sentinel constant for use in `style_func`
- `StringData`, `Filter`, `data_to_matrix` — data source abstractions (`rows.py`)
- Column flex-sizing algorithm (`resizing.py`)

#### List sub-package (`lipgloss/list/`)
- `List` — fluent builder with `item`, `items`, `enumerator`, `enumerator_style`,
  `item_style`, `hide`
- `Items` — sequence wrapper passed to enumerator functions
- Built-in enumerators: `Bullet`, `Arabic`, `Alphabet`, `Roman`, `Asterisk`, `Dash`

#### Tree sub-package (`lipgloss/tree/`)
- `Tree` — fluent builder with `child`, `root_style`, `item_style`, `enumerator_style`,
  `enumerator`, `indenter`, `hide`, `offset`
- `root(label)` — convenience constructor
- `NodeChildren`, `Leaf`, `Node` protocol — children and node types
- Built-in enumerators: `DefaultEnumerator`, `RoundedEnumerator`, `DefaultIndenter`
- Auto-nesting: rootless `Tree` after a `Leaf` promotes the `Leaf` as the new root

#### Test suite (`tests/`)
- 275 tests across 9 test files covering all implemented features
- Fixtures for all four color profiles in `conftest.py`

#### CI / tooling
- `.github/workflows/python.yml` — matrix CI (Python 3.10, 3.11, 3.12): black, isort,
  flake8, mypy, pytest with 60% coverage floor
- `pyproject.toml` — packaging, dev extras, tool config (black, isort, mypy, flake8)
- `py.typed` marker (PEP 561)

#### Examples (`examples/`)
- `basic_style.py` — Style properties showcase
- `table.py` — Language greeting table
- `list.py` — Grocery list with custom enumerator
- `tree.py` — Recursive directory tree renderer
- `layout.py` — Multi-section terminal layout

---

[Unreleased]: https://github.com/tbdtechpro/lipgloss/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/tbdtechpro/lipgloss/releases/tag/v0.1.0
