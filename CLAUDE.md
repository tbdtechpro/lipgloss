# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

This repository is a **Go → Python translation project**. The Go source files are the reference implementation and exist solely to inform the development of the Python port. Once the Python translation reaches reasonable feature parity, the Go files will be removed.

The subject of the translation is **Lip Gloss** — a terminal styling library by [Charm](https://charm.sh) that provides a CSS-like declarative API for composing styled terminal output. Users describe styles with chained method calls (colors, padding, borders, alignment) and call `render()` to produce ANSI-escaped strings.

### Role of each file type

| File type | Purpose |
|-----------|---------|
| `.go` files | **Reference only.** Authoritative source of truth for behavior, API shape, and edge cases. Do not modify Go files except to understand them. They will be deleted once parity is reached. |
| `.py` files | **The translation target.** All new development goes here. |

---

## Repository Structure

```
lipgloss/
├── # Go reference files (root package `lipgloss`) — read to inform Python translation
├── style.go                # Core Style struct; propKey bit-flag property system
├── set.go                  # All property setters (return Style by value)
├── get.go                  # All property getters
├── unset.go                # Property unsetters
├── renderer.go             # Renderer struct; terminal color profile detection
├── color.go                # TerminalColor interface; Color, NoColor, ANSIColor, AdaptiveColor, CompleteColor
├── borders.go              # Border style definitions (Normal, Rounded, Double, Thick, ASCII, Markdown)
├── join.go                 # JoinHorizontal / JoinVertical for composing styled blocks
├── position.go             # Position type; Place, PlaceHorizontal, PlaceVertical
├── align.go                # Horizontal and vertical text alignment helpers
├── whitespace.go           # Whitespace rendering with optional styling
├── runes.go                # StyleRunes for per-rune styling
├── size.go                 # Width / Height measurement utilities
├── ranges.go               # Range manipulation utilities
├── ansi_unix.go            # Unix ANSI handling
├── ansi_windows.go         # Windows ANSI handling
├── go.mod                  # Go module: github.com/charmbracelet/lipgloss, go 1.24
├── go.sum
│
├── table/                  # Go reference: table rendering
│   ├── table.go
│   ├── rows.go
│   ├── resizing.go
│   └── table_test.go
│
├── list/                   # Go reference: list rendering
│   ├── list.go
│   ├── enumerator.go
│   └── list_test.go
│
├── tree/                   # Go reference: tree rendering
│   ├── tree.go
│   ├── children.go
│   ├── enumerator.go
│   ├── renderer.go
│   └── tree_test.go
│
├── # Python translation files (live alongside Go files during development)
├── lipgloss.py             # Public API; Style class, color helpers, join/place utilities
├── style.py                # Style implementation
├── color.py                # Color types
├── borders.py              # Border definitions
├── renderer.py             # Renderer class
├── table/table.py          # Table sub-package
├── list/list.py            # List sub-package
├── tree/tree.py            # Tree sub-package
├── pyproject.toml          # Python packaging (requires Python 3.10+)
│
├── examples/               # Go example programs (reference for Python examples)
│   ├── layout/
│   ├── list/
│   ├── table/
│   ├── tree/
│   └── ssh/
│
├── README.md               # Project overview — describes the vibe-coding experiment
├── Taskfile.yaml           # Task runner (Go: lint + test)
├── .golangci.yml           # golangci-lint v2 config
└── .github/workflows/      # CI: build, lint, coverage, release
```

---

## Core Concept

Lip Gloss is a **style-and-render** library. A `Style` holds declarative properties (colors, padding, margins, borders, alignment, width, height). Calling `render(text)` applies those properties and returns an ANSI-escaped string ready to print.

```
Style() → set properties → render(text) → ANSI string
```

In Go, `Style` is an **immutable value type**: each setter returns a new `Style`. The Python port replicates this — setters return modified copies to enable fluent chaining without mutation side-effects.

---

## Go Reference — How to Read the Source

When translating or understanding behavior, the key Go files to consult are:

| Question | Go file to read |
|----------|----------------|
| What properties does Style support? | `style.go` (the `propKey` constants) |
| How does a setter work? | `set.go` |
| How does rendering work? | `style.go` (`Render` method) |
| How are colors resolved? | `color.go`, `renderer.go` |
| How does `Inherit` work? | `get.go`, `set.go` (bit-flag checks) |
| How are borders rendered? | `borders.go`, `style.go` |
| How does `JoinHorizontal`/`JoinVertical` work? | `join.go` |
| How is string width measured? | `size.go`, uses `ansi.StringWidth` |
| How does the table layout algorithm work? | `table/table.go`, `table/resizing.go` |
| How do list enumerators work? | `list/enumerator.go`, `list/list.go` |
| How does tree rendering work? | `tree/tree.go`, `tree/enumerator.go` |

### Key Go Conventions (informing Python design)

- `Style` is a **value type** — all setters return a new `Style`. Never mutate in place.
- Properties use bit-flags (`propKey`). `Inherit()` only copies properties that are explicitly set on the parent — unset properties do not override.
- String width is measured with `ansi.StringWidth`, not `len` — ANSI escape codes are zero-width and some Unicode characters are double-wide.
- Color profiles degrade automatically: TrueColor → ANSI256 → ANSI → ASCII based on terminal capability detection.
- `Position` is a `float64` alias: `0.0` = left/top, `0.5` = center, `1.0` = right/bottom.
- Platform-specific behavior uses `_unix.go` / `_windows.go` file suffixes.

---

## Python Development

### Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Code Style

- **Formatter**: `black` (line length 100)
- **Import sorting**: `isort` (black profile)
- **Type checking**: `mypy` (strict, `disallow_untyped_defs = true`)
- **Linting**: `flake8`
- Python 3.10+ required.

### Python Key Types

- `Style` — core class; fluent builder that returns copies from every setter
- `Color` — wraps a hex string or ANSI index string
- `AdaptiveColor` — dataclass with `light` and `dark` fields
- `CompleteColor` — dataclass with `true_color`, `ansi256`, `ansi` fields
- `NoColor` — sentinel for explicit no-color
- `Renderer` — manages output writer and color profile detection

### Python Color Types

```python
import lipgloss

lipgloss.Color("21")                                        # ANSI 256 index
lipgloss.Color("#FF5733")                                   # True-color hex
lipgloss.AdaptiveColor(light="236", dark="248")             # Background-adaptive
lipgloss.CompleteColor(true_color="#0000FF", ansi256="86", ansi="5")  # Per-profile
lipgloss.NoColor()                                          # Explicit no-color
```

### Python Style Usage

```python
import lipgloss

style = (
    lipgloss.Style()
    .bold(True)
    .foreground(lipgloss.Color("#FAFAFA"))
    .background(lipgloss.Color("#7D56F4"))
    .padding_top(2)
    .padding_left(4)
    .width(22)
)

print(style.render("Hello, kitty"))
```

### Python Sub-package APIs

**table**:
```python
from lipgloss import table
t = table.Table().headers("Name", "Value").rows([["foo", "bar"]])
print(t.render())
```

**list**:
```python
from lipgloss import list as lst
l = lst.List("A", "B", "C").enumerator(lst.Bullet)
print(l.render())
```

**tree**:
```python
from lipgloss import tree
t = tree.Tree().root(".").child("A", "B", "C")
print(t.render())
```

---

## Go → Python Naming Reference

| Go | Python |
|----|--------|
| `NewStyle()` | `Style()` |
| `.Bold(true)` | `.bold(True)` |
| `.Foreground(c)` | `.foreground(c)` |
| `.Background(c)` | `.background(c)` |
| `.Padding(n)` | `.padding(n)` |
| `.PaddingTop(n)` | `.padding_top(n)` |
| `.MarginLeft(n)` | `.margin_left(n)` |
| `.BorderStyle(b)` | `.border_style(b)` |
| `.BorderForeground(c)` | `.border_foreground(c)` |
| `.Align(pos)` | `.align(pos)` |
| `.Width(n)` | `.width(n)` |
| `.Height(n)` | `.height(n)` |
| `.MaxWidth(n)` | `.max_width(n)` |
| `.Inline(true)` | `.inline(True)` |
| `.Inherit(s)` | `.inherit(s)` |
| `.Render("text")` | `.render("text")` |
| `NormalBorder()` | `normal_border()` |
| `RoundedBorder()` | `rounded_border()` |
| `JoinHorizontal(pos, ...)` | `join_horizontal(pos, ...)` |
| `JoinVertical(pos, ...)` | `join_vertical(pos, ...)` |
| `Width(s)` | `width(s)` |
| `Height(s)` | `height(s)` |
| `Place(h, w, hPos, vPos, s)` | `place(h, w, h_pos, v_pos, s)` |
| `AdaptiveColor{Light: ..., Dark: ...}` | `AdaptiveColor(light=..., dark=...)` |
| `CompleteColor{TrueColor: ..., ANSI256: ..., ANSI: ...}` | `CompleteColor(true_color=..., ansi256=..., ansi=...)` |

---

## CI / GitHub Actions

Workflows in `.github/workflows/` currently target Go. As the Python port matures, Python CI (pytest, mypy, flake8) should be added.

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `build.yml` | push/PR | Build Go reference |
| `lint.yml` | push/PR | Run golangci-lint on Go reference |
| `coverage.yml` | push/PR | Go test coverage with race detector |
| `release.yml` | tag | Release automation via GoReleaser |

---

## Important Notes for AI Assistants

- **Go files are reference material, not targets for modification.** Read them to understand intended behavior; write Python equivalents in `.py` files.
- **The Go files will be removed** once the Python port reaches reasonable feature parity. Do not add new Go code.
- **This repo is an experiment.** The Python port is AI-generated and unvalidated. Do not represent it as production-ready.
- **`Style` must behave as an immutable builder in Python.** Every setter should return a new instance (or a copy). Silently mutating the receiver is a correctness bug.
- **String width is not `len()`.** Use ANSI-aware measurement (e.g. the `wcwidth` package or equivalent) — ANSI escape codes are zero-width and some Unicode characters are double-wide.
- **Color profiles degrade automatically.** The renderer detects terminal capability and coerces colors down the chain (TrueColor → ANSI256 → ANSI → ASCII). The Python port must replicate this.
- **`Inherit()` only copies unset properties.** A property already set on the child must not be overridden by the parent. See `style.go` for the bit-flag implementation.
- **Never log to stdout** in a running TUI program — it will corrupt the display. Always use file logging.
