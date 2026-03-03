# lipgloss — App Integration Issues
# Source: discovered while building KeroGrid with bubbletea + lipgloss
#
# COPY TARGET: append this block to BUBBLETEA_ISSUES.md in tbdtechpro/lipgloss
# ─────────────────────────────────────────────────────────────────────────────

---

## 4. `.width(n)` word-wraps content — silently breaks bubbletea line counting

**Symptom:** A styled header or hints bar renders as two terminal rows instead
of one. On the next keypress the entire TUI cascades upward and off-screen.

**Root cause:** `.width(n)` sets a *minimum* column width, but also word-wraps
content that exceeds `n` characters, injecting a `\n` into the rendered string.
Most developers expect `.width(n)` to be a padding-only operation (analogous to
CSS `min-width`).

The injected `\n` inflates `view.count("\n")` in bubbletea's renderer by one.
The renderer then erases one extra line on the next redraw, shifts the cursor
above the TUI frame, and every subsequent redraw compounds the offset.

Example — this silently produces a two-line string when `tw = 80`:
```python
lipgloss.Style()
    .background(mocha.crust)
    .width(80)
    .render(
        "  Tab/↑↓ Navigate    ◄/Space/► Cycle option"
        "    Enter Activate    F5 Generate    Ctrl+Q Quit  "
    )
    # ^^^^ 93 visible characters — wraps at column 80, embeds \n
```

**Fix — option A (non-breaking, recommended):**
Add a `.max_width(n)` method that hard-truncates content to `n` columns instead
of wrapping, giving developers an explicit choice between the two behaviours:
```
.width(n)      — existing: pad to n, wrap if longer   (soft / layout)
.max_width(n)  — new:      pad to n, truncate if longer (hard / line)
```

**Fix — option B (breaking, cleaner long-term):**
Change `.width(n)` to padding-only (no word-wrap) and introduce `.wrap(n)` for
intentional wrapping. This matches what the name implies and aligns with the
mental model developers bring from CSS/HTML layout.

**Workaround until fixed:**
Measure the content before rendering and ensure it is shorter than `tw` before
calling `.width(tw)`:
```python
hints = "  Tab/↑↓ Nav    ◄ Space ► Cycle    Enter Activate    F5 Gen    Ctrl+Q Quit"
# Keep to 74 chars — well under any realistic terminal width
lipgloss.Style().width(tw).render(hints)
```

---

## 5. `.padding()` and `.width()` wrap threshold is undocumented

**Symptom:** A developer sets `.width(80).padding(0, 1)` expecting wrapping (if
any) to occur at 80 characters. Wrapping actually occurs at 78 characters.

**Root cause:** The word-wrap threshold inside `render()` is
`width - pad_left - pad_right`. With `.padding(0, 1)` that is `80 − 1 − 1 = 78`.
The content must fit within the inner box, not the outer styled box.

This is internally consistent but is not documented in either `.width()` or
`.padding()`, and the interaction is not obvious.

**Fix:** Add a note to both method docstrings explaining the interaction, with
an example:
```python
# Wraps at 78 chars, not 80 — the padding eats into the wrap budget:
Style().width(80).padding(0, 1).render(text)

# To fill 80 cols with visible 1-col side padding the text must be <= 78:
Style().width(80).padding(0, 1).render(text[:78])
```

---

## 6. `_visible_width()` and `_strip_ansi()` are private but needed by apps

**Symptom:** An app developer needs to measure the visible column width of a
lipgloss-rendered string before deciding how much padding to add, or to splice
two styled strings together with correct alignment. The helpers exist but are
prefixed `_`, making them private and unstable.

**Root cause:** `_visible_width()` and `_strip_ansi()` are implementation
details of `style.py`. There is no documented public surface for ANSI-aware
string measurement.

**Fix:** Expose them as public API, either from `lipgloss/__init__.py` or a
`lipgloss/utils.py` module:
```python
# lipgloss/__init__.py additions
from lipgloss.style import _visible_width as visible_width
from lipgloss.style import _strip_ansi   as strip_ansi
```
With proper docstrings and inclusion in the test suite so they remain stable
across versions.
