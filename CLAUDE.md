# CLAUDE.md

This file provides guidance to AI assistants working with the lipgloss codebase.

## Project Overview

Lipgloss is a Go library for declarative terminal styling. It provides a CSS-like API for building styled TUI (terminal user interface) output. It is part of the [Charm](https://charm.sh) ecosystem and is commonly used with [Bubble Tea](https://github.com/charmbracelet/bubbletea).

Module path: `github.com/charmbracelet/lipgloss`
Go version: 1.24+

## Repository Structure

```
lipgloss/
├── *.go                  # Core styling library (root package)
├── table/                # Table rendering sub-package
├── list/                 # List rendering sub-package
├── tree/                 # Tree rendering sub-package
├── examples/             # Runnable example programs
│   ├── layout/
│   ├── list/
│   ├── table/
│   ├── tree/
│   └── ssh/
├── .github/workflows/    # CI: build, lint, coverage, release
├── Taskfile.yaml         # Task runner commands
├── .golangci.yml         # Linter configuration
└── .goreleaser.yml       # Release configuration
```

### Root Package Files

| File | Purpose |
|------|---------|
| `style.go` | Core `Style` struct; `propKey` bit-flag property system |
| `set.go` | All property setters (return `Style` by value) |
| `get.go` | All property getters |
| `unset.go` | Property unsetters |
| `renderer.go` | `Renderer` struct; terminal color profile detection |
| `color.go` | `TerminalColor` interface; `Color`, `NoColor`, `ANSIColor`, `AdaptiveColor`, `CompleteColor` |
| `borders.go` | Border style definitions (Normal, Rounded, Double, Thick, ASCII, Markdown) |
| `join.go` | `JoinHorizontal` / `JoinVertical` for composing styled blocks |
| `position.go` | `Position` type; `Place`, `PlaceHorizontal`, `PlaceVertical` |
| `align.go` | Horizontal and vertical text alignment helpers |
| `whitespace.go` | Whitespace rendering with optional styling |
| `runes.go` | `StyleRunes` for per-rune styling |
| `size.go` | `Width` / `Height` measurement utilities |
| `ranges.go` | Range manipulation utilities |
| `ansi_unix.go` / `ansi_windows.go` | Platform-specific ANSI handling |

## Development Commands

```bash
# Run all tests
go test ./...

# Run tests with race detector (mirrors CI)
go test -race ./...

# Run only table tests
go test ./table

# Via task runner
task test
task test:table
task lint
```

The project uses [Task](https://taskfile.dev) (`Taskfile.yaml`) as its task runner. Direct `go` commands work equally well.

## Testing

- Test files live alongside source files (`*_test.go`).
- Golden/snapshot tests use `testdata/` directories within each package. Update golden files with:
  ```bash
  go test ./... -update
  ```
- CI runs tests with `-race -covermode atomic`. Always verify race-safety for concurrent code.
- `table/table_test.go` is very large (~64k lines) — it contains comprehensive rendering snapshots.
- The `tree` package also has `example_test.go` with runnable `Example*` functions.

## Code Conventions

### Style is Immutable / Value Type

`Style` is a struct passed by value. Every setter returns a new `Style`. Never mutate a style in place:

```go
// Correct: each call returns a new style
s := lipgloss.NewStyle().Bold(true).Foreground(lipgloss.Color("#FF0000"))

// Correct: re-assign to apply more settings
s = s.Padding(1, 2)
```

### Property System

Properties are stored as bit-flags (`propKey`) on the `props int64` field, with actual values in a separate `vals` map. This lets `Inherit()` apply only the properties that have been explicitly set on the parent style:

```go
// Only bold propagates; foreground does not because it's unset in parent
child := lipgloss.NewStyle().Inherit(parent)
```

### Color Types

Use the most appropriate color type:

| Type | Use case |
|------|----------|
| `Color("21")` | ANSI 256 index |
| `Color("#FF5733")` | True-color hex |
| `ANSIColor(1)` | Basic ANSI 16 colors |
| `AdaptiveColor{Light: "...", Dark: "..."}` | Different values based on terminal background |
| `CompleteColor{TrueColor: "...", ANSI256: "...", ANSI: "..."}` | Explicit per-profile values |
| `NoColor{}` | Explicit no-color |

Colors are rendered via the `Renderer`'s color profile, which automatically degrades (TrueColor → ANSI256 → ANSI → ASCII) based on terminal capabilities.

### Renderer

The global renderer (`lipgloss.DefaultRenderer()`) is used by default. Create a custom renderer when writing to a specific `io.Writer` (e.g., for SSH sessions or testing):

```go
r := lipgloss.NewRenderer(w)
style := r.NewStyle().Bold(true)
```

The `Renderer` uses `sync.Once` for lazy color profile detection and `sync.RWMutex` for thread safety.

### Formatting Conventions

- **Formatter**: `gofumpt` + `goimports` (stricter than standard `gofmt`)
- **Linter**: `golangci-lint` with the config in `.golangci.yml`
- All exported types and functions must have doc comments ending with a period (`godot` linter enforced).
- Do not use naked returns (`nakedret`).
- Wrap errors rather than returning them bare (`wrapcheck`).
- Avoid magic numbers; use named constants.
- Avoid deeply nested `if` blocks (`nestif`).

### Sub-package Patterns

**table**: Constructed via `table.New()`, configured with method chaining. `StyleFunc` is used for per-cell styling. Column widths are computed by the `resizing.go` algorithm.

**list**: Constructed via `list.New()`. Supports custom `Enumerator` functions (signature: `func(items Items, index int) string`). Nesting is done by adding a `*list.List` as an item.

**tree**: Node-based. `tree.New()` builds a root; `.Child(...)` accepts strings (leaves) or `*tree.Tree` (branches). Custom `Enumerator` signature: `func(children Children, index int) string`.

## Key Dependencies

| Module | Purpose |
|--------|---------|
| `github.com/charmbracelet/x/ansi` | ANSI escape code parsing and string-width measurement |
| `github.com/charmbracelet/x/cellbuf` | Cell-based terminal buffer for layout |
| `github.com/muesli/termenv` | Terminal color profiles and output |
| `github.com/rivo/uniseg` | Unicode grapheme cluster segmentation |
| `github.com/aymanbagabas/go-udiff` | Diff output in tests |
| `github.com/charmbracelet/x/exp/golden` | Golden file test helpers |

## CI/CD

GitHub Actions workflows live in `.github/workflows/`:

- **build.yml**: Builds on push to `master` and on PRs.
- **coverage.yml**: Runs `go test -race -covermode atomic ./...` and reports to Coveralls.
- **lint.yml**: Runs `golangci-lint`.
- **release.yml**: Handles tagged releases via GoReleaser.

The project retracts `v0.7.0` (app freeze bug) and `v0.11.1` (line-wrap bug). Do not re-introduce those version tags.

## Common Pitfalls

- **Platform differences**: ANSI handling differs between Unix (`ansi_unix.go`) and Windows (`ansi_windows.go`). Test on both if changing escape code logic.
- **String width**: Always use `ansi.StringWidth` (or the cellbuf equivalent) — not `len()` or `utf8.RuneCountInString()` — when measuring visible terminal width, because ANSI escape codes are zero-width and some Unicode characters are double-wide.
- **Style inheritance**: `Inherit()` only copies *unset* properties from the parent. If a property is already set on the child, it will not be overridden.
- **Immutability**: Because `Style` is a value type, forgetting to re-assign the result of a setter is a silent bug.
- **Golden test updates**: Rendering output changes require updating golden files. Run with `-update` flag.
