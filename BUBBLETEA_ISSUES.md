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
