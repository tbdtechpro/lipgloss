# Python Lip Gloss — MVP Task List

Tasks required to bring the Python port to feature parity with the Go library for MVP status,
and to verify it works in conjunction with the
[Python Bubble Tea port](https://github.com/tbdtechpro/bubbletea).

Items are grouped by area and ordered by priority within each group.
Completed items are checked off.

---

## 1. Project Scaffolding

Foundation files needed before any implementation work begins.

- [x] **Create `pyproject.toml` and `setup.py`**
  - Package name: `lipgloss`, version `0.1.0`.
  - Python 3.10+ required.
  - Dev extras: `pytest`, `pytest-cov`, `black`, `isort`, `flake8`, `mypy`.
  - Runtime dependency: `wcwidth` (ANSI-aware string width).
  - Files: `pyproject.toml`, `setup.py`

- [x] **Create package directory structure**
  - Root package `lipgloss/` with `__init__.py`, `style.py`, `color.py`,
    `borders.py`, `renderer.py`, `position.py`, `whitespace.py`, `size.py`,
    `join.py`, `runes.py`.
  - Sub-packages: `lipgloss/table/`, `lipgloss/list/`, `lipgloss/tree/` each
    with their own `__init__.py`.
  - All stub files include docstrings referencing the corresponding Go source file.
  - Package verified importable via `pip install -e ".[dev]"`.
  - Files: full `lipgloss/` package tree, `tests/__init__.py`

- [x] **Add `py.typed` marker file (PEP 561)**
  - Empty marker file signals to type checkers that this package ships inline types.
  - Created as part of task 1.2; `pyproject.toml` already includes it in package-data.
  - File: `lipgloss/py.typed`

- [x] **Create `__init__.py` with public API exports**
  - All public symbols exported and verified importable: `Style`, `new_style`,
    color types (`Color`, `ANSIColor`, `AdaptiveColor`, `CompleteColor`,
    `CompleteAdaptiveColor`, `NoColor`, `TerminalColor`), all border factories,
    `Position` constants, `join_horizontal`, `join_vertical`, `place`,
    `place_horizontal`, `place_vertical`, `width`, `height`, `size`,
    `style_runes`, `ColorProfile`, `Renderer`, `default_renderer`,
    `set_default_renderer`, `new_renderer`, whitespace option helpers.
  - All core rendering is fully implemented. `style_runes` and the table/list/tree
    sub-packages still raise `NotImplementedError` (tasks 5.5, 6, 7, 8).
  - File: `lipgloss/__init__.py`

---

## 2. Color System

The color system must be implemented before Style, because Style depends on it.

- [x] **Implement `TerminalColor` protocol and all color types**
  - `TerminalColor`: abstract base / Protocol with `resolve(renderer) -> str` method
    that returns the ANSI escape sequence string for a given color profile.
  - `NoColor`: sentinel for absent color; resolves to empty string / default terminal color.
  - `Color(str)`: hex (`"#FF5733"`) or ANSI index string (`"21"`); resolves via
    color profile.
  - `ANSIColor(int)`: convenience wrapper for ANSI 0–15; equivalent to
    `Color(str(n))`.
  - `AdaptiveColor(light, dark)`: dataclass; resolves to `light` or `dark` based on
    `renderer.has_dark_background()`.
  - `CompleteColor(true_color, ansi256, ansi)`: dataclass; explicit per-profile values,
    no automatic degradation.
  - `CompleteAdaptiveColor(light: CompleteColor, dark: CompleteColor)`: combines both
    adaptability and explicit per-profile values.
  - File: `lipgloss/color.py` (new)

- [x] **Implement `Renderer` with color profile detection**
  - `ColorProfile` enum: `TrueColor`, `ANSI256`, `ANSI`, `ASCII`.
  - `Renderer` class: wraps an `io.TextIOWrapper`; detects color profile from
    `$COLORTERM`, `$TERM`, `$NO_COLOR`, `isatty()`.
  - `renderer.color_profile() -> ColorProfile`: lazy detection via `functools.cached_property`.
  - `renderer.has_dark_background() -> bool`: detect via terminal query or assume `True`
    as a safe default.
  - `renderer.new_style() -> Style`: convenience method to create a `Style` bound to
    this renderer.
  - Module-level `default_renderer()`, `set_default_renderer(r)`, `new_renderer(w)`.
  - File: `lipgloss/renderer.py` (new)

---

## 3. Core Style System

The central component of the library. All other rendering features depend on `Style`.

- [x] **Implement `Style` as an immutable fluent builder**
  - Internally stores properties in a dict keyed by property name; the set of which
    keys are present acts as the bit-flag equivalent from Go.
  - Every setter returns a new `Style` (copy with the property added/changed), never
    mutating the receiver — matches Go's value-type semantics.
  - `Style.render(*strings) -> str`: applies all set properties and returns an
    ANSI-escaped string.  Multiple arguments are joined with a space before rendering
    (matches Go behaviour).
  - `Style.__str__()`: delegates to `render()` on any pre-set string (`.set_string()`).
  - File: `lipgloss/style.py` (new)

- [x] **Implement all boolean inline-formatting properties**
  - `.bold(v: bool)` / `.unset_bold()`
  - `.italic(v: bool)` / `.unset_italic()`
  - `.underline(v: bool)` / `.unset_underline()`
  - `.strikethrough(v: bool)` / `.unset_strikethrough()`
  - `.reverse(v: bool)` / `.unset_reverse()`
  - `.blink(v: bool)` / `.unset_blink()`
  - `.faint(v: bool)` / `.unset_faint()`
  - `.underline_spaces(v: bool)` / `.unset_underline_spaces()`
  - `.strikethrough_spaces(v: bool)` / `.unset_strikethrough_spaces()`
  - `.color_whitespace(v: bool)` / `.unset_color_whitespace()`
  - File: `lipgloss/style.py`

- [x] **Implement color properties**
  - `.foreground(c: TerminalColor)` / `.unset_foreground()`
  - `.background(c: TerminalColor)` / `.unset_background()`
  - File: `lipgloss/style.py`

- [x] **Implement dimension properties**
  - `.width(n: int)` / `.unset_width()`
  - `.height(n: int)` / `.unset_height()`
  - `.max_width(n: int)` / `.unset_max_width()`
  - `.max_height(n: int)` / `.unset_max_height()`
  - File: `lipgloss/style.py`

- [x] **Implement padding properties with CSS-shorthand overloads**
  - `.padding(top, [right, [bottom, [left]]])` — 1-to-4 argument shorthand.
  - `.padding_top(n)` / `.padding_right(n)` / `.padding_bottom(n)` / `.padding_left(n)`.
  - Unsetters for all four sides.
  - File: `lipgloss/style.py`

- [x] **Implement margin properties with CSS-shorthand overloads**
  - `.margin(top, [right, [bottom, [left]]])` — 1-to-4 argument shorthand.
  - `.margin_top(n)` / `.margin_right(n)` / `.margin_bottom(n)` / `.margin_left(n)`.
  - `.margin_background(c: TerminalColor)` / `.unset_margin_background()`.
  - Unsetters for all four sides.
  - File: `lipgloss/style.py`

- [x] **Implement border properties**
  - `.border(border, [top, right, bottom, left])` — shorthand for style + edges.
  - `.border_style(b: Border)` / `.unset_border_style()`
  - `.border_top(v: bool)` / `.border_right(v: bool)` / `.border_bottom(v: bool)` / `.border_left(v: bool)` + unsetters.
  - Foreground colors: `.border_foreground(c)`, `.border_top_foreground(c)`,
    `.border_right_foreground(c)`, `.border_bottom_foreground(c)`,
    `.border_left_foreground(c)` + unsetters.
  - Background colors: same pattern for `border_*_background`.
  - File: `lipgloss/style.py`

- [x] **Implement alignment, inline, tab-width, and transform properties**
  - `.align(h: Position)` — horizontal alignment.
  - `.align_horizontal(h: Position)` / `.align_vertical(v: Position)` + unsetters.
  - `.inline(v: bool)` / `.unset_inline()` — force single-line output.
  - `.tab_width(n: int)` / `.unset_tab_width()` — default 4; `0` removes tabs;
    `-1` (`NoTabConversion`) leaves tabs intact.
  - `.transform(fn: Callable[[str], str])` / `.unset_transform()`.
  - File: `lipgloss/style.py`

- [x] **Implement `Style.inherit()` and `Style.copy()`**
  - `.inherit(parent: Style)`: copy only the properties from `parent` that are not
    already set on `self` — mirrors Go's bit-flag "unset check".
  - `.copy()`: return a new `Style` with identical properties (deep copy of internal dict).
  - File: `lipgloss/style.py`

- [x] **Implement `Style.set_string()` and getters**
  - `.set_string(*strings)`: attach strings to the style so `render()` / `__str__()`
    work without arguments.
  - Getter for every settable property (e.g. `.get_bold() -> bool`,
    `.get_foreground() -> TerminalColor`, `.get_width() -> int`, etc.).
  - File: `lipgloss/style.py`

---

## 4. Border System

- [x] **Implement `Border` dataclass**
  - Fields: `top`, `bottom`, `left`, `right`, `top_left`, `top_right`,
    `bottom_left`, `bottom_right`, `middle_left`, `middle_right`, `middle`,
    `middle_top`, `middle_bottom` — all `str`.
  - File: `lipgloss/borders.py`

- [x] **Implement all predefined border factories**
  - `normal_border()` — single-line box drawing characters.
  - `rounded_border()` — single-line with rounded corners.
  - `double_border()` — double-line box drawing characters.
  - `thick_border()` — heavy box drawing characters.
  - `ascii_border()` — plain ASCII `+`, `-`, `|`.
  - `markdown_border()` — pipe-and-dash style for markdown tables.
  - `hidden_border()` — space characters (preserves spacing without visible lines).
  - Also: `block_border()`, `outer_half_block_border()`, `inner_half_block_border()`.
  - File: `lipgloss/borders.py`

---

## 5. Layout Utilities

- [x] **Implement ANSI-aware string measurement (`size.py`)**
  - `width(s: str) -> int`: width of the widest line, stripping ANSI codes before
    measuring with `wcwidth`.
  - `height(s: str) -> int`: number of lines (`s.count("\n") + 1`).
  - `size(s: str) -> tuple[int, int]`: returns `(width, height)`.
  - Internal helper `_get_lines(s: str) -> tuple[list[str], int]`: splits on `\n`,
    returns lines and max width — used by join/place.
  - File: `lipgloss/size.py` (new)

- [x] **Implement `join_horizontal` and `join_vertical`**
  - `join_horizontal(pos: Position, *strs: str) -> str`: join blocks side-by-side,
    padding shorter blocks to the height of the tallest at `pos`.
  - `join_vertical(pos: Position, *strs: str) -> str`: stack blocks, padding narrower
    lines to the width of the widest at `pos`.
  - Reference: `join.go` for padding/alignment logic.
  - File: `lipgloss/join.py` (new)

- [x] **Implement `Position` constants and `place` functions**
  - `Position = float` (type alias or `NewType`).
  - Constants: `Top = 0.0`, `Bottom = 1.0`, `Left = 0.0`, `Right = 1.0`,
    `Center = 0.5`.
  - `place(width, height, h_pos, v_pos, s, **whitespace_opts) -> str`.
  - `place_horizontal(width, pos, s, **whitespace_opts) -> str`.
  - `place_vertical(height, pos, s, **whitespace_opts) -> str`.
  - File: `lipgloss/position.py` (new)

- [x] **Implement `WhitespaceOption` and styled whitespace rendering**
  - `whitespace_foreground(c: TerminalColor) -> WhitespaceOption`.
  - `whitespace_background(c: TerminalColor) -> WhitespaceOption`.
  - `whitespace_chars(s: str) -> WhitespaceOption`.
  - Used internally by `place*` functions to fill gaps.
  - Reference: `whitespace.go`.
  - File: `lipgloss/whitespace.py` (new)

- [ ] **Implement `style_runes`**
  - `style_runes(s: str, indices: list[int], matched: Style, unmatched: Style) -> str`:
    apply `matched` style to characters at `indices`, `unmatched` to the rest.
  - Reference: `runes.go`.
  - File: `lipgloss/runes.py` (new)

---

## 6. Table Sub-package

- [ ] **Implement `Table` class (core)**
  - `Table()` constructor; method-chaining builder.
  - `.headers(*cols: str)` — set header row.
  - `.rows(*rows: list[str])` — set all data rows at once.
  - `.row(*cols: str)` — append a single row incrementally.
  - `.width(n: int)` — set total table width.
  - `.height(n: int)` — set total table height.
  - `.offset(n: int)` — starting row offset for scrolling.
  - `.__str__() / .render() -> str` — render to ANSI string.
  - Reference: `table/table.go`.
  - File: `lipgloss/table/table.py` (new)

- [ ] **Implement table styling**
  - `.border(b: Border)` — set border style.
  - `.border_top(v: bool)` / `.border_bottom(v: bool)` / `.border_left(v: bool)` /
    `.border_right(v: bool)` / `.border_header(v: bool)` / `.border_column(v: bool)`.
  - `.border_style(s: Style)` — style applied to border characters.
  - `.style_func(fn: Callable[[int, int], Style])` — per-cell style; row 0 is the
    header row (use `table.HeaderRow` sentinel constant).
  - File: `lipgloss/table/table.py`

- [ ] **Implement column resizing algorithm**
  - Port the flex-sizing algorithm from `table/resizing.go`: distribute available
    width across columns, respecting min-width (content) and table-level constraints.
  - File: `lipgloss/table/resizing.py` (new)

- [ ] **Implement `Rows` abstraction**
  - `StringData(*rows)`: wraps a list-of-lists for use as table data.
  - `Filter(data, fn)`: wraps a data source with a row-filter predicate.
  - Reference: `table/rows.go`.
  - File: `lipgloss/table/rows.py` (new)

---

## 7. List Sub-package

- [ ] **Implement `List` class**
  - `List(*items)` constructor; method-chaining builder.
  - Items can be `str` (leaf) or another `List` (nested sub-list).
  - `.item(*items)` — append items incrementally.
  - `.enumerator(fn: Callable[[Items, int], str])` — set custom enumerator function.
  - `.enumerator_style(s: Style)` — style applied to the enumerator prefix.
  - `.item_style(s: Style)` — style applied to each item's text.
  - `.__str__() / .render() -> str` — render to ANSI string.
  - Reference: `list/list.go`.
  - File: `lipgloss/list/list.py` (new)

- [ ] **Implement built-in enumerators**
  - `Bullet` — `•` prefix.
  - `Arabic` — `1.`, `2.`, `3.` …
  - `Alphabet` — `a.`, `b.`, `c.` …
  - `Roman` — `i.`, `ii.`, `iii.` …
  - `Tree` — tree-branch characters (uses the tree enumerator logic).
  - Reference: `list/enumerator.go`.
  - File: `lipgloss/list/enumerator.py` (new)

---

## 8. Tree Sub-package

- [ ] **Implement `Tree` class**
  - `Tree()` constructor; `root(label: str)` sets the root label.
  - `.child(*items)` — append children; items can be `str` (leaf) or `Tree` (branch).
  - `.enumerator(fn: Callable[[Children, int], str])` — custom enumerator.
  - `.root_style(s: Style)` — style applied to the root label.
  - `.item_style(s: Style)` — style applied to child nodes.
  - `.enumerator_style(s: Style)` — style applied to enumerator prefix.
  - `.__str__() / .render() -> str` — render to ANSI string.
  - Reference: `tree/tree.go`, `tree/renderer.go`.
  - File: `lipgloss/tree/tree.py` (new)

- [ ] **Implement built-in tree enumerators**
  - `default_enumerator` — `├── ` / `└── ` style.
  - `rounded_enumerator` — `├── ` / `╰── ` style.
  - Reference: `tree/enumerator.go`.
  - File: `lipgloss/tree/enumerator.py` (new)

- [ ] **Implement `Children` and `Leaf`/`Node` types**
  - `Node` protocol: `.value() -> str`, `.hidden() -> bool`, `.children() -> Children`.
  - `Leaf(str)` — terminal node with no children.
  - `Children` — sequence wrapper with `.at(i)` and `.__len__()`.
  - Reference: `tree/children.go`, `tree/tree.go`.
  - File: `lipgloss/tree/children.py` (new)

---

## 9. Test Suite

- [x] **Create `tests/` directory with `conftest.py` and shared fixtures**
  - Fixtures: `truecolor_renderer()`, `ansi256_renderer()`, `ansi_renderer()`,
    `ascii_renderer()`, `style()` (bound to TrueColor renderer).
  - File: `tests/conftest.py`

- [x] **Write unit tests for the color system**
  - `Color`, `ANSIColor`, `AdaptiveColor`, `CompleteColor`, `CompleteAdaptiveColor`,
    `NoColor` each resolve to the expected ANSI string under TrueColor, ANSI256, ANSI,
    and ASCII profiles.
  - Adaptive variants choose the correct branch based on `has_dark_background()`.
  - Also covers `Renderer` color profile detection and `_resolve_color_string()`.
  - Files: `tests/test_color.py`, `tests/test_renderer.py`

- [x] **Write unit tests for `Style` core rendering**
  - Bold, italic, underline, strikethrough, reverse, blink, faint.
  - Foreground and background colors.
  - Padding: all four sides, CSS shorthands (1-, 2-, 3-, 4-arg).
  - Margin: all four sides, CSS shorthands.
  - Width / height expansion; alignment (left, right, center, horizontal and vertical).
  - MaxWidth / MaxHeight enforcement.
  - Borders: all predefined styles, edge selection, foreground/background colors.
    Covered in dedicated `tests/test_borders.py`.
  - Tab width: default (4), custom, 0 (remove), `-1` (preserve).
  - Inline mode: collapses to single line.
  - Transform: applied to string.
  - File: `tests/test_style.py`

- [x] **Write unit tests for `Style.inherit()` and `Style.copy()`**
  - Properties already set on child are not overridden by parent.
  - Margins and padding are never inherited (matches Go behaviour).
  - Copy is independent (mutating copy does not affect original).
  - File: `tests/test_style.py`

- [x] **Write unit tests for layout utilities**
  - `width()` / `height()` / `size()`: plain strings, multi-line, ANSI-escaped.
    File: `tests/test_size.py`
  - `join_horizontal()`: equal-height blocks, top/center/bottom positioning, width padding.
    File: `tests/test_join.py`
  - `join_vertical()`: equal-width blocks, left/center/right positioning.
    File: `tests/test_join.py`
  - `place()` / `place_horizontal()` / `place_vertical()`: all positions, no-op when
    content already fits, dimension preservation.
    File: `tests/test_position.py`

- [ ] **Write unit tests for the table sub-package**
  - Basic rendering with headers and rows.
  - Border styles (normal, rounded, ASCII, markdown, none).
  - Column resizing: content-driven widths, fixed table width.
  - `style_func` per-cell styling, `HeaderRow` sentinel.
  - Offset / scrolling.
  - File: `tests/test_table.py` (new)

- [ ] **Write unit tests for the list sub-package**
  - All five built-in enumerators.
  - Custom enumerator function.
  - Nested lists (two levels).
  - `enumerator_style` and `item_style`.
  - File: `tests/test_list.py` (new)

- [ ] **Write unit tests for the tree sub-package**
  - Single-level tree with `default_enumerator` and `rounded_enumerator`.
  - Multi-level nested tree.
  - Custom enumerator.
  - Hidden nodes are skipped.
  - Root / item / enumerator styling.
  - File: `tests/test_tree.py` (new)

---

## 10. Bubble Tea Integration

The integration point is straightforward: a Bubble Tea `Model.view()` returns a `str`.
Using lipgloss to build that string requires no special wiring — lipgloss just produces
ANSI-escaped strings that the Bubble Tea renderer prints as-is.

- [ ] **Verify ANSI string compatibility with the Bubble Tea Python renderer**
  - Confirm that lipgloss-rendered strings (with embedded ANSI escape codes) display
    correctly when returned from a Bubble Tea `view()` and written by
    `bubbletea.Renderer`.
  - Specifically: the Bubble Tea renderer uses line-diff output to avoid full redraws.
    Verify that lipgloss strings that contain escape codes do not confuse the diff
    logic (off-by-one visible widths, etc.).
  - File: `tests/test_bubbletea_integration.py` (new)

- [ ] **Write a combined lipgloss + Bubble Tea example program**
  - Simple counter app where `view()` uses lipgloss styles: a styled header, a
    centered count, and a footer rendered with `join_vertical`.
  - Demonstrates that the two Python ports can be used together as a drop-in
    replacement for Go Bubble Tea + Lip Gloss.
  - File: `examples/bubbletea_counter.py` (new)

- [ ] **Write a layout showcase example using lipgloss + Bubble Tea**
  - Demonstrates `join_horizontal`, `join_vertical`, `place`, borders, adaptive
    colors, and table rendering all in one Bubble Tea view.
  - File: `examples/bubbletea_layout.py` (new)

---

## 11. Packaging & Type Safety

- [ ] **Run `mypy` over all Python source files and fix all errors**
  - Strict mode: `disallow_untyped_defs = true`, `check_untyped_defs = true`.
  - All public functions and methods must have complete type annotations.
  - Files: all `.py` source files

- [ ] **Run `black` and `isort` and resolve all formatting issues**
  - Line length 100, isort black profile.
  - Files: all `.py` source files

- [ ] **Ensure all public symbols are exported from `lipgloss/__init__.py`**
  - `__all__` must include every symbol intended to be part of the public API.
  - File: `lipgloss/__init__.py`

---

## 12. CI / GitHub Actions

- [ ] **Add Python lint + test workflow**
  - `.github/workflows/python.yml`: runs on push/PR against Python 3.10, 3.11, 3.12.
  - Steps: `pip install -e ".[dev]"`, `black --check`, `isort --check`, `flake8`,
    `mypy`, `pytest --cov`.
  - File: `.github/workflows/python.yml` (new)

- [ ] **Add Python coverage reporting**
  - `pytest --cov=lipgloss --cov-fail-under=60`.
  - File: `.github/workflows/python.yml`

---

## 13. Examples

- [ ] **Port the basic styling example**
  - Shows `Style` with colors, bold, padding, borders, and `render()`.
  - File: `examples/basic_style.py` (new)

- [ ] **Port the table example**
  - Reproduces the Go `examples/table` output: language greeting table with
    header styling, alternating row colors, and a normal border.
  - File: `examples/table.py` (new)

- [ ] **Port the list example**
  - Reproduces the Go `examples/list` output: nested grocery list with
    Roman enumerator and custom styles.
  - File: `examples/list.py` (new)

- [ ] **Port the tree example**
  - Reproduces the Go `examples/tree` output: OS family tree with
    `rounded_enumerator` and custom styles.
  - File: `examples/tree.py` (new)

- [ ] **Port the layout example**
  - Reproduces the Go `examples/layout` output: multiple styled columns joined
    horizontally with `join_horizontal` and `place`.
  - File: `examples/layout.py` (new)

---

## 14. Documentation

- [ ] **Create `ATTRIBUTION.md`**
  - Credit the original Charm team, and the AI tooling used in this experiment.
  - File: `ATTRIBUTION.md` (new)

- [ ] **Add `CHANGELOG.md`**
  - Track version history from `0.1.0` onwards.
  - Follow [Keep a Changelog](https://keepachangelog.com) format.
  - File: `CHANGELOG.md` (new)

- [ ] **Write a Python usage guide**
  - Covers: `Style` basics, color types, borders, padding/margins, join/place
    layout, table/list/tree sub-packages, custom renderers, and using lipgloss
    inside a Bubble Tea `view()`.
  - File: `docs/python-guide.md` (new)
