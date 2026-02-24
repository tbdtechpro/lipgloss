# CLAUDE.md

This file provides guidance for AI assistants working in this repository.

## Repository Overview

This repository contains two parallel implementations of the **Lip Gloss** terminal styling library:

1. **Go library** (`github.com/charmbracelet/lipgloss`) — the original, battle-tested implementation, production-ready.
2. **Python port** — a Python port of the Go library, mirroring the API in an idiomatic Python style (pre-alpha, in development).

Lip Gloss provides a CSS-like declarative API for composing styled terminal output. Users describe styles with chained method calls (colors, padding, borders, alignment) and call `render()` / `Render()` to produce ANSI-escaped strings.

---

## Repository Structure

```
lipgloss/
├── # Go source files (root package `lipgloss`)
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
├── table/                  # Table rendering sub-package
│   ├── table.go
│   ├── rows.go
│   ├── resizing.go
│   └── table_test.go
│
├── list/                   # List rendering sub-package
│   ├── list.go
│   ├── enumerator.go
│   └── list_test.go
│
├── tree/                   # Tree rendering sub-package
│   ├── tree.go
│   ├── children.go
│   ├── enumerator.go
│   ├── renderer.go
│   └── tree_test.go
│
├── # Python port files (to be added alongside Go files)
├── lipgloss.py             # (planned) Public API; Style class, color helpers, join/place utilities
├── style.py                # (planned) Style implementation
├── color.py                # (planned) Color types
├── borders.py              # (planned) Border definitions
├── renderer.py             # (planned) Renderer class
├── table/table.py          # (planned) Table sub-package
├── list/list.py            # (planned) List sub-package
├── tree/tree.py            # (planned) Tree sub-package
├── pyproject.toml          # (planned) Python packaging (requires Python 3.10+)
│
├── examples/               # Example programs
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

Lip Gloss is a **style-and-render** library. A `Style` holds declarative properties (colors, padding, margins, borders, alignment, width, height). Calling `Render(text)` applies those properties and returns an ANSI-escaped string ready to print.

```
NewStyle() → set properties → Render(text) → ANSI string
```

Styles are **immutable value types** in Go: each setter returns a new `Style`. The Python port should replicate this — either via true immutability or by returning `self` after copy to enable fluent chaining.

---

## Go Development

### Running Tests

```bash
go test ./...
# with race detector (mirrors CI)
go test -race ./...
# table tests only
go test ./table
```

Or via Task:

```bash
task test
task test:table
```

### Updating Golden Files

Snapshot/golden tests live in `testdata/` directories. Update them with:

```bash
go test ./... -update
```

### Running the Linter

```bash
task lint
# equivalent to:
golangci-lint run
```

### Linter Configuration (`.golangci.yml`)

- **Version**: golangci-lint v2
- **Formatters**: `gofumpt`, `goimports` (use these, not plain `gofmt`)
- **Enabled linters**: `bodyclose`, `exhaustive`, `goconst`, `godot`, `gosec`, `misspell`, `nestif`, `nilerr`, `revive`, `unconvert`, `unparam`, `whitespace`, `wrapcheck`, and others
- Tests are excluded from linting (`run.tests: false`)

### Key Go Conventions

- All exported types, functions, and variables must have godoc comments ending in a period (enforced by `godot`).
- `Style` is a **value type** — all setters return a new `Style`. Never mutate in place.
- Properties are stored as bit-flags (`propKey`). `Inherit()` only copies properties that are explicitly set on the parent.
- Use `ansi.StringWidth` (not `len` or `utf8.RuneCountInString`) when measuring visible terminal width.
- Platform-specific code uses `_unix.go` / `_windows.go` suffixes.
- Wrap errors rather than returning them bare (`wrapcheck`).

### Key Go Types

| Type | Description |
|------|-------------|
| `Style` | Core styling struct; value type, immutable setters |
| `Renderer` | Terminal output handler; detects color profile via `termenv` |
| `TerminalColor` | Interface satisfied by `Color`, `NoColor`, `ANSIColor`, `AdaptiveColor`, `CompleteColor` |
| `Border` | Struct of rune strings defining border characters |
| `Position` | Float alias for alignment (0.0 = left/top, 0.5 = center, 1.0 = right/bottom) |

### Go Color Types

| Type | Usage |
|------|-------|
| `Color("21")` | ANSI 256 index |
| `Color("#FF5733")` | True-color hex |
| `ANSIColor(1)` | Basic ANSI 16 |
| `AdaptiveColor{Light: "...", Dark: "..."}` | Background-adaptive |
| `CompleteColor{TrueColor: "...", ANSI256: "...", ANSI: "..."}` | Explicit per-profile |
| `NoColor{}` | Explicit no-color |

---

## Python Development

### Setup (once pyproject.toml is added)

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

### Python API Design Principles

The Python port mirrors the Go API with language-appropriate idioms:

| Go | Python |
|----|--------|
| `lipgloss.NewStyle()` | `lipgloss.new_style()` or `lipgloss.Style()` |
| `.Bold(true)` | `.bold(True)` |
| `.Foreground(lipgloss.Color("#FF0000"))` | `.foreground(lipgloss.Color("#FF0000"))` |
| `.Render("text")` | `.render("text")` |
| `lipgloss.JoinHorizontal(pos, a, b)` | `lipgloss.join_horizontal(pos, a, b)` |
| `lipgloss.JoinVertical(pos, a, b)` | `lipgloss.join_vertical(pos, a, b)` |
| `lipgloss.Width(s)` | `lipgloss.width(s)` |
| `lipgloss.Height(s)` | `lipgloss.height(s)` |
| `lipgloss.Place(...)` | `lipgloss.place(...)` |

### Python Key Types (planned)

- `Style` — core class in `style.py`; implement as fluent builder returning copies
- `Color` — string subclass or simple class wrapping a hex/ANSI value
- `AdaptiveColor` — dataclass with `light` and `dark` fields
- `CompleteColor` — dataclass with `true_color`, `ansi256`, `ansi` fields
- `Renderer` — class managing output and color profile detection

### Python Color Types (planned)

```python
import lipgloss

# ANSI 256
lipgloss.Color("21")

# True-color hex
lipgloss.Color("#FF5733")

# Adaptive (light/dark background)
lipgloss.AdaptiveColor(light="236", dark="248")

# Explicit per-profile
lipgloss.CompleteColor(true_color="#0000FF", ansi256="86", ansi="5")

# No color
lipgloss.NoColor()
```

### Python Style Usage (planned)

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

### Python Sub-package APIs (planned)

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

## Python vs Go Naming Reference

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

---

## CI / GitHub Actions

Workflows in `.github/workflows/` delegate to reusable workflows from `charmbracelet/meta`:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| `build.yml` | push/PR | Build Go |
| `lint.yml` | push/PR | Run golangci-lint |
| `coverage.yml` | push/PR | Code coverage with race detector |
| `release.yml` | tag | Release automation via GoReleaser |

---

## Important Notes for AI Assistants

- **Two separate implementations exist (or will exist) side by side.** Go files are at the root; Python files will also be at the root and in sub-packages, identified by `.py` extension. They implement the same concepts with language-appropriate idioms.
- **Go module path**: `github.com/charmbracelet/lipgloss`. Do not change this.
- **This repo is an experiment.** The Python port is AI-generated and unvalidated. See `README.md`. Do not represent it as production-ready.
- **The Python port is pre-alpha.** The Go source is the reference — when in doubt about intended behavior, read the Go implementation.
- **`Style` is a value type in Go.** Python should replicate this with copy-on-write or by returning modified copies from each setter to enable fluent chaining without mutation bugs.
- **String width is not `len()`.** Always use ANSI-aware width measurement. In Go this is `ansi.StringWidth`; in Python use a library like `wcwidth` or strip ANSI codes before measuring.
- **Color profiles degrade automatically.** The renderer detects terminal capability (TrueColor → ANSI256 → ANSI → ASCII) and coerces colors to the best available option. The Python port must replicate this behavior.
- **Retracted versions**: `v0.7.0` (freeze bug) and `v0.11.1` (line-wrap bug) are retracted. Do not re-introduce those version tags.
- **Never log to stdout** in a running TUI program — it will corrupt the display. Always use file logging.
- **Golden tests** in `testdata/` directories must be updated with `-update` when rendering output changes.
