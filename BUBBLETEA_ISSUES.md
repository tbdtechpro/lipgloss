# Bubbletea Fork — Known Issues

Issues discovered while integrating `tbdtechpro/bubbletea` with this project.

---

## 1. Editable install is not importable (`pip install -e .` broken)

**Symptom:** After `pip install -e /path/to/bubbletea`, `import bubbletea` raises
`ModuleNotFoundError`.

**Root cause:** The package uses a *flat layout* — all Python modules
(`tea.py`, `model.py`, `commands.py`, …) sit at the repository root alongside
`__init__.py`. `pyproject.toml` does not declare a `package-dir` mapping, so
setuptools' editable-install finder generates:

```python
MAPPING = {'bubbletea': '/path/to/bubbletea/bubbletea', ...}
```

…pointing at a `bubbletea/` *subdirectory* that does not exist.

**Fix:** Add a `package-dir` entry to `pyproject.toml` so setuptools knows the
`bubbletea` package root is the repository root itself:

```toml
[tool.setuptools.packages.find]
where = ["."]
exclude = ["tests*", "examples*", "tutorials*"]

[tool.setuptools.package-dir]
bubbletea = ""
```

Alternatively, move all source files into a `bubbletea/` subdirectory (the
conventional *src* or *pkg* layout) and update all relative imports accordingly.

**Workaround used in lipgloss:** A `.pth` file was added to the system
site-packages pointing at the *parent* directory of the repo:

```
/home/user
```

This makes `import bubbletea` resolve via the `__init__.py` at the repo root.
This is a dev-environment hack and should not be relied on for distribution.

---

## 2. PyPI name collision

**Symptom:** `pip install bubbletea` installs the wrong package — a medical
chatbot library (`bubbletea 0.0.2` by Baihan Lin, `github.com/doerlbh/bubbletea`)
that has no `bubbletea` module and depends on `pandas`/`numpy`.

**Impact:** Any user or CI environment that runs `pip install bubbletea` expecting
the Charm TUI framework will silently get the wrong package.

**Recommendation:** Either:
- Publish under a distinct PyPI name (e.g. `charm-bubbletea`, `bubbletea-tui`,
  or `bubbletea-py`) to avoid the collision, or
- Coordinate with the existing PyPI package owner if the name can be transferred,
  or
- Distribute only via direct git URL until a name is settled:
  ```
  pip install git+https://github.com/tbdtechpro/bubbletea.git
  ```

---

## 3. `tutorials` namespace packages included unintentionally

**Symptom:** The editable-install finder also registers several `tutorials.*`
namespace packages:

```python
NAMESPACES = {
    'tutorials': [...],
    'tutorials.basics': [...],
    'tutorials.python-basics': [...],
    ...
}
```

These are example/documentation directories, not importable packages, and
should not be exposed by the distribution.

**Fix:** Ensure `tutorials*` is listed in the `exclude` list inside
`[tool.setuptools.packages.find]` (same as `tests*` and `examples*`).
Also verify none of the tutorial directories contain an `__init__.py` —
if they do, remove it.

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

**Fix:** Use `.max_width(n)` instead of `.width(n)` for single-line bars.
`.max_width(n)` truncates rather than wraps, keeping the output to one row.

**Workaround until migrated:**
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

This is documented in the `.width()` and `.padding()` docstrings as of the fix
applied in this session; the interaction is now explained with examples in both
method docstrings.

---

## 6. `visible_width()` and `strip_ansi()` were private but needed by apps

**Symptom:** An app developer needs to measure the visible column width of a
lipgloss-rendered string before deciding how much padding to add, or to splice
two styled strings together with correct alignment. The helpers existed but were
prefixed `_`, making them private and unstable.

**Fix applied:** Both are now exported as public API from `lipgloss/__init__.py`:
```python
from lipgloss import visible_width, strip_ansi

visible_width("\x1b[1mHello\x1b[0m")  # → 5
strip_ansi("\x1b[32mGreen\x1b[0m")    # → "Green"
```
