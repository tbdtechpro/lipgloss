# Lip Gloss — Python Usage Guide

This guide covers the full Python API for the Lip Gloss terminal styling library.
Lip Gloss takes a CSS-like, declarative approach to terminal output: you describe
what a piece of text should look like, then call `render()` to produce an
ANSI-escaped string ready to print.

---

## Table of Contents

1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [The Style Builder](#the-style-builder)
4. [Color System](#color-system)
5. [Text Formatting](#text-formatting)
6. [Colors on Text](#colors-on-text)
7. [Padding and Margins](#padding-and-margins)
8. [Width and Height](#width-and-height)
9. [Borders](#borders)
10. [Alignment](#alignment)
11. [Inline Mode and Truncation](#inline-mode-and-truncation)
12. [Tab Width](#tab-width)
13. [Transform](#transform)
14. [Inheriting and Copying Styles](#inheriting-and-copying-styles)
15. [Getters and Unsetters](#getters-and-unsetters)
16. [Measurement Utilities](#measurement-utilities)
17. [Joining Blocks](#joining-blocks)
18. [Placing Text in Whitespace](#placing-text-in-whitespace)
19. [Per-Rune Styling](#per-rune-styling)
20. [Table Sub-package](#table-sub-package)
21. [List Sub-package](#list-sub-package)
22. [Tree Sub-package](#tree-sub-package)
23. [Custom Renderers](#custom-renderers)

---

## Installation

```bash
pip install -e ".[dev]"   # from source with dev extras
```

Runtime dependency: [`wcwidth`](https://github.com/jquast/wcwidth) for ANSI-aware
string width measurement.

Python 3.10 or later is required.

---

## Quick Start

```python
import lipgloss

style = (
    lipgloss.Style()
    .bold(True)
    .foreground(lipgloss.Color("#FAFAFA"))
    .background(lipgloss.Color("#7D56F4"))
    .padding(1, 4)
    .width(22)
)

print(style.render("Hello, kitty"))
```

---

## The Style Builder

`Style` is an **immutable fluent builder**. Every setter returns a *new* `Style`
with that property changed — the original is never modified. This lets you safely
derive specialised styles from a base style without side-effects.

```python
base = lipgloss.Style().foreground(lipgloss.Color("99"))

# These are independent copies — base is unchanged.
bold_variant = base.bold(True)
wide_variant = base.width(40)
```

To render, call `.render(*strings)`. Multiple arguments are joined with a space:

```python
style = lipgloss.Style().bold(True)
print(style.render("Hello,", "world"))  # "Hello, world" in bold
```

You can also attach a string to the style itself:

```python
style = lipgloss.Style().bold(True).set_string("Hello, kitty")
print(str(style))   # same as style.render()
print(style.render("extra"))  # "Hello, kitty extra"
```

---

## Color System

Lip Gloss supports four color types. The renderer automatically degrades colors to
the best available option for the current terminal.

### `Color(str)` — hex or ANSI index

```python
lipgloss.Color("#FF5733")   # true-color hex
lipgloss.Color("#0F0")      # 3-digit hex shorthand
lipgloss.Color("21")        # ANSI-256 index
lipgloss.Color("5")         # ANSI-16 index (magenta)
```

### `ANSIColor(int)` — ANSI 0–15

```python
lipgloss.ANSIColor(1)   # red
lipgloss.ANSIColor(12)  # bright blue
```

### `AdaptiveColor(light, dark)` — background-adaptive

Chooses `light` or `dark` depending on whether the terminal has a light or dark
background. Each value is a string accepted by `Color`.

```python
lipgloss.AdaptiveColor(light="236", dark="248")
lipgloss.AdaptiveColor(light="#874BFD", dark="#7D56F4")
```

### `CompleteColor(true_color, ansi256, ansi)` — explicit per-profile

Bypasses automatic degradation; you specify the exact value for each profile.

```python
lipgloss.CompleteColor(true_color="#0000FF", ansi256="21", ansi="5")
```

### `CompleteAdaptiveColor(light, dark)` — adaptive + per-profile

Combines `AdaptiveColor` and `CompleteColor`.

```python
lipgloss.CompleteAdaptiveColor(
    light=lipgloss.CompleteColor(true_color="#d7ffae", ansi256="193", ansi="11"),
    dark=lipgloss.CompleteColor(true_color="#d75fee", ansi256="163", ansi="5"),
)
```

### `NoColor()` — explicit no-color

```python
lipgloss.NoColor()   # resolves to an empty escape — uses terminal default
```

---

## Text Formatting

```python
style = (
    lipgloss.Style()
    .bold(True)
    .italic(True)
    .underline(True)
    .strikethrough(True)
    .reverse(True)       # swap fg/bg
    .blink(True)
    .faint(True)
)
```

By default, underline and strikethrough are also applied to spaces. To control
this separately:

```python
style = (
    lipgloss.Style()
    .underline(True)
    .underline_spaces(False)   # don't underline spaces between words
)
```

Similarly for strikethrough:

```python
lipgloss.Style().strikethrough(True).strikethrough_spaces(False)
```

---

## Colors on Text

```python
style = (
    lipgloss.Style()
    .foreground(lipgloss.Color("#FAFAFA"))
    .background(lipgloss.Color("#7D56F4"))
)
```

By default, the background color is also applied to whitespace characters
(padding, alignment fill). To disable this:

```python
lipgloss.Style().background(lipgloss.Color("63")).color_whitespace(False)
```

---

## Padding and Margins

Padding adds space *inside* the border (or around the content if there is no
border). Margins add space *outside*.

### Per-side

```python
style = (
    lipgloss.Style()
    .padding_top(2)
    .padding_right(4)
    .padding_bottom(2)
    .padding_left(4)
)
```

### CSS shorthand (1–4 values, same order as CSS)

```python
lipgloss.Style().padding(2)           # 2 on all sides
lipgloss.Style().padding(2, 4)        # top/bottom=2, left/right=4
lipgloss.Style().padding(1, 4, 2)     # top=1, left/right=4, bottom=2
lipgloss.Style().padding(1, 2, 3, 4)  # top, right, bottom, left
```

The same shorthand works for margins:

```python
lipgloss.Style().margin(1, 2)
```

### Margin background

You can colour the margin area:

```python
lipgloss.Style().margin(2).margin_background(lipgloss.Color("236"))
```

> **Note:** Margins and padding are *never* inherited via `.inherit()`.

---

## Width and Height

`width` and `height` set the *minimum* dimensions. Content is padded to fill
the space; it is never truncated by these properties (use `max_width` /
`max_height` for truncation).

```python
style = lipgloss.Style().width(24).height(10)
```

`max_width` and `max_height` truncate content that exceeds the limit:

```python
style = lipgloss.Style().max_width(20).max_height(5)
```

---

## Borders

### Predefined borders

```python
lipgloss.normal_border()         # ┌─┐  │ │  └─┘
lipgloss.rounded_border()        # ╭─╮  │ │  ╰─╯
lipgloss.thick_border()          # ┏━┓  ┃ ┃  ┗━┛
lipgloss.double_border()         # ╔═╗  ║ ║  ╚═╝
lipgloss.ascii_border()          # +-+  | |  +-+
lipgloss.markdown_border()       # | — | (for markdown tables)
lipgloss.hidden_border()         # spaces (preserves spacing)
lipgloss.block_border()          # full-block characters
lipgloss.outer_half_block_border()
lipgloss.inner_half_block_border()
```

### Applying a border

```python
# All four sides
style = lipgloss.Style().border_style(lipgloss.rounded_border())

# Specific sides using the shorthand
style = lipgloss.Style().border(lipgloss.thick_border(), True, False)  # top + bottom only

# Clockwise from top: top=True, right=False, bottom=False, left=True
style = lipgloss.Style().border(lipgloss.double_border(), True, False, False, True)
```

### Border colors

```python
style = (
    lipgloss.Style()
    .border_style(lipgloss.rounded_border())
    .border_foreground(lipgloss.Color("228"))   # all sides
    .border_background(lipgloss.Color("63"))    # all sides
)

# Per-side
style = (
    lipgloss.Style()
    .border_style(lipgloss.normal_border())
    .border_top_foreground(lipgloss.Color("228"))
    .border_bottom_foreground(lipgloss.Color("63"))
)
```

### Custom borders

```python
from lipgloss.borders import Border

my_border = Border(
    top="._.:*:", bottom="._.:*:",
    left="|*", right="|*",
    top_left="*", top_right="*",
    bottom_left="*", bottom_right="*",
)

style = lipgloss.Style().border_style(my_border)
```

---

## Alignment

`Position` is a `float` in `[0.0, 1.0]`: `0.0` = left/top, `0.5` = center,
`1.0` = right/bottom.

```python
lipgloss.Left    # 0.0
lipgloss.Center  # 0.5
lipgloss.Right   # 1.0
lipgloss.Top     # 0.0
lipgloss.Bottom  # 1.0
```

### Horizontal alignment

Requires `width` to be set (otherwise there is nothing to align within):

```python
style = lipgloss.Style().width(40).align(lipgloss.Center)
style = lipgloss.Style().width(40).align_horizontal(lipgloss.Right)
```

### Vertical alignment

Requires `height` to be set:

```python
style = lipgloss.Style().height(10).align_vertical(lipgloss.Bottom)
```

### Both at once

```python
style = lipgloss.Style().width(40).height(10).align(lipgloss.Center, lipgloss.Center)
```

---

## Inline Mode and Truncation

`inline(True)` forces the output onto a single line, stripping newlines and
ignoring padding, margins, and borders:

```python
style = lipgloss.Style().inline(True)
print(style.render("first line\nsecond line"))  # "first linesecond line"
```

Combine with `max_width` to clamp to a fixed number of visible cells:

```python
style = lipgloss.Style().inline(True).max_width(20)
```

---

## Tab Width

Tabs are converted to spaces at render time. The default is 4 spaces:

```python
lipgloss.Style().tab_width(2)    # render tabs as 2 spaces
lipgloss.Style().tab_width(0)    # remove tabs entirely
lipgloss.Style().tab_width(-1)   # leave tabs unchanged (NoTabConversion)
```

---

## Transform

Apply an arbitrary function to the rendered string after all style properties
have been applied:

```python
style = lipgloss.Style().transform(str.upper)
print(style.render("hello"))  # "HELLO"
```

---

## Inheriting and Copying Styles

### Copying

Every setter already returns a copy, so `base_style.bold(True)` is a copy with bold
added. For an explicit copy with no changes:

```python
copy = style.copy()
```

### Inheritance

`inherit(parent)` copies properties from `parent` that are **not already set** on
`self`. This lets child styles override only what they need to:

```python
base = (
    lipgloss.Style()
    .foreground(lipgloss.Color("229"))
    .background(lipgloss.Color("63"))
)

# foreground is already set, so only background is inherited
child = lipgloss.Style().foreground(lipgloss.Color("201")).inherit(base)
```

> **Note:** Margins and padding are never inherited, matching Go's behaviour.

---

## Getters and Unsetters

Every property has a getter and an unsetter:

```python
style = lipgloss.Style().bold(True).width(40)

style.get_bold()    # True
style.get_width()   # 40

style2 = style.unset_bold()    # bold removed; style is unchanged
style2 = style.unset_width()   # width removed
```

---

## Measurement Utilities

These functions measure the *visible* dimensions of ANSI-escaped strings,
ignoring escape codes and handling double-wide Unicode characters correctly.

```python
import lipgloss

s = lipgloss.Style().bold(True).render("Hello")

lipgloss.width(s)      # visible width of the widest line
lipgloss.height(s)     # number of lines
w, h = lipgloss.size(s)
```

---

## Joining Blocks

### Horizontal join

Place blocks side by side. `pos` controls vertical alignment of shorter blocks.

```python
left  = lipgloss.Style().width(20).height(5).render("Left")
right = lipgloss.Style().width(20).height(3).render("Right")

# Align shorter block to the top, center, or bottom
result = lipgloss.join_horizontal(lipgloss.Top,    left, right)
result = lipgloss.join_horizontal(lipgloss.Center, left, right)
result = lipgloss.join_horizontal(lipgloss.Bottom, left, right)
result = lipgloss.join_horizontal(0.2, left, right)  # 20% from top
```

### Vertical join

Stack blocks. `pos` controls horizontal alignment of narrower blocks.

```python
top    = lipgloss.Style().width(30).render("Top block")
bottom = lipgloss.Style().width(20).render("Bottom block")

result = lipgloss.join_vertical(lipgloss.Left,   top, bottom)
result = lipgloss.join_vertical(lipgloss.Center, top, bottom)
result = lipgloss.join_vertical(lipgloss.Right,  top, bottom)
```

---

## Placing Text in Whitespace

Place a styled block inside a larger space. The whitespace fill is configurable.

```python
paragraph = lipgloss.Style().border_style(lipgloss.rounded_border()).render("Hello!")

# Center in an 80×10 box
result = lipgloss.place(80, 10, lipgloss.Center, lipgloss.Center, paragraph)

# Horizontal only
result = lipgloss.place_horizontal(80, lipgloss.Center, paragraph)

# Vertical only
result = lipgloss.place_vertical(10, lipgloss.Bottom, paragraph)
```

### Styled whitespace

Pass `WhitespaceOption` helpers to control the fill characters and colors:

```python
result = lipgloss.place(
    80, 10,
    lipgloss.Center, lipgloss.Center,
    paragraph,
    lipgloss.whitespace_chars("·"),
    lipgloss.whitespace_foreground(lipgloss.Color("240")),
    lipgloss.whitespace_background(lipgloss.Color("235")),
)
```

---

## Per-Rune Styling

Apply different styles to individual characters within a string:

```python
matched   = lipgloss.Style().foreground(lipgloss.Color("10")).bold(True)
unmatched = lipgloss.Style().foreground(lipgloss.Color("240"))

# Highlight characters at indices 0 and 2
result = lipgloss.style_runes("Hello", [0, 2], matched, unmatched)
```

---

## Table Sub-package

```python
from lipgloss import table
```

### Basic usage

```python
t = (
    table.Table()
    .headers("Name", "Language", "Stars")
    .rows(
        ["Bubble Tea", "Go", "27k"],
        ["Lip Gloss",  "Go", "8k"],
        ["Wish",       "Go", "3k"],
    )
)
print(t.render())
```

### Borders

```python
t = (
    table.Table()
    .border(lipgloss.rounded_border())
    .border_header(True)   # separator between header and data rows
    .border_column(True)   # separators between columns
    .headers("Col A", "Col B")
    .rows(["x", "y"])
)
```

Disable specific sides:

```python
t.border_top(False).border_bottom(False)
```

### Styling with `style_func`

`style_func` receives `(row, col)` and returns a `Style`. `table.HeaderRow` is the
sentinel for the header row.

```python
header_style = lipgloss.Style().bold(True).foreground(lipgloss.Color("99"))
even_style   = lipgloss.Style().foreground(lipgloss.Color("245"))
odd_style    = lipgloss.Style().foreground(lipgloss.Color("241"))

def style_func(row: int, col: int) -> lipgloss.Style:
    if row == table.HeaderRow:
        return header_style
    return even_style if row % 2 == 0 else odd_style

t = table.Table().style_func(style_func).headers("A", "B").rows(...)
```

### Data sources

```python
data = table.StringData(
    ["Alice", "30"],
    ["Bob",   "25"],
)
t = table.Table().headers("Name", "Age").data(data)
```

Filter rows:

```python
filtered = table.Filter(data, lambda row: row[1] != "30")
```

### Width, height, and offset

```python
t = table.Table().width(60).height(10).offset(2)  # skip first 2 data rows
```

---

## List Sub-package

```python
from lipgloss import list as lst
```

### Basic usage

```python
l = lst.List("Apple", "Banana", "Cherry")
print(l.render())
# • Apple
# • Banana
# • Cherry
```

### Built-in enumerators

```python
lst.Bullet     # •  (default)
lst.Arabic     # 1. 2. 3.
lst.Alphabet   # A. B. C.
lst.Roman      # I. II. III.
lst.Asterisk   # *
lst.Dash       # -
```

```python
l = lst.List("A", "B", "C").enumerator(lst.Roman)
```

### Custom enumerator

The enumerator function receives an `Items` wrapper and the current index:

```python
def my_enum(items: lst.Items, i: int) -> str:
    return f"{i + 1})"

l = lst.List("One", "Two", "Three").enumerator(my_enum)
```

### Styling

```python
l = (
    lst.List("Glossier", "Nyx", "Mac")
    .enumerator(lst.Roman)
    .enumerator_style(lipgloss.Style().foreground(lipgloss.Color("99")).margin_right(1))
    .item_style(lipgloss.Style().foreground(lipgloss.Color("212")))
)
```

### Nested lists

Pass a `List` instance as an item to create a sub-list:

```python
l = lst.List(
    "Fruits",
    lst.List("Apple", "Banana", "Cherry"),
    "Vegetables",
    lst.List("Carrot", "Broccoli"),
)
```

### Hiding lists

```python
l = lst.List("A", "B").hide(True)   # renders as empty string
```

---

## Tree Sub-package

```python
from lipgloss import tree as tr
```

### Basic usage

```python
t = tr.root(".").child("A", "B", "C")
print(t.render())
# .
# ├── A
# ├── B
# └── C
```

### Nested trees

Pass a `Tree` as a child to create branches:

```python
t = (
    tr.root(".")
    .child("macOS")
    .child(
        tr.root("Linux").child("Arch", "NixOS", "Void")
    )
    .child(
        tr.root("BSD").child("FreeBSD", "OpenBSD")
    )
)
```

### Enumerators

```python
tr.DefaultEnumerator   # ├── / └──  (default)
tr.RoundedEnumerator   # ├── / ╰──
```

```python
t = tr.root("root").child("A", "B").enumerator(tr.RoundedEnumerator)
```

### Styling

```python
t = (
    tr.root("⁜ Makeup")
    .child("Glossier", "Fenty Beauty", "Nyx")
    .enumerator(tr.RoundedEnumerator)
    .enumerator_style(lipgloss.Style().foreground(lipgloss.Color("63")).margin_right(1))
    .root_style(lipgloss.Style().foreground(lipgloss.Color("35")))
    .item_style(lipgloss.Style().foreground(lipgloss.Color("212")))
)
```

### Hiding nodes

```python
t = tr.root("root").child("A", "B").hide(True)   # whole tree hidden
```

### Offset

Trim children from the start and end:

```python
t = tr.root("root").child("A", "B", "C", "D").offset(1, 1)
# Shows B and C, skipping A (start) and D (end)
```

---

## Custom Renderers

A `Renderer` binds a style to a specific output stream and detects its color
profile and background color independently. This is useful for SSH servers or
any scenario where multiple outputs with different capabilities coexist.

```python
import io
import lipgloss

# Create a renderer for a specific output
buf = io.StringIO()
renderer = lipgloss.new_renderer(buf)

# Create styles bound to this renderer
style = renderer.new_style().bold(True).foreground(lipgloss.Color("#FF0000"))
buf.write(style.render("Hello from a custom renderer"))

print(buf.getvalue())
```

### Forcing a color profile

```python
from lipgloss.renderer import Renderer, ColorProfile

renderer = Renderer()
# Inspect the detected profile
profile = renderer.color_profile()  # ColorProfile.TrueColor, .ANSI256, .ANSI, or .ASCII
```

### Replacing the global default renderer

```python
renderer = lipgloss.new_renderer(my_output_stream)
lipgloss.set_default_renderer(renderer)

# All subsequent Style() calls will use this renderer
style = lipgloss.Style().bold(True)
```

---

## Tips and Patterns

### Building a status bar

```python
bar_style = lipgloss.Style().background(lipgloss.Color("235"))
key_style = lipgloss.Style().background(lipgloss.Color("62")).foreground(lipgloss.Color("231")).padding(0, 1)
val_style = lipgloss.Style().inherit(bar_style).foreground(lipgloss.Color("243"))

key = key_style.render("STATUS")
val = val_style.width(60 - lipgloss.width(key)).render("All systems nominal")
print(bar_style.render(lipgloss.join_horizontal(lipgloss.Top, key, val)))
```

### Adaptive colors for light/dark terminals

```python
fg = lipgloss.AdaptiveColor(light="#333333", dark="#DDDDDD")
bg = lipgloss.AdaptiveColor(light="#EEEEEE", dark="#1A1A1A")
style = lipgloss.Style().foreground(fg).background(bg)
```

### Deriving a "muted" variant from a bold style

```python
active   = lipgloss.Style().bold(True).foreground(lipgloss.Color("99"))
inactive = active.unset_bold().foreground(lipgloss.Color("240"))
```
