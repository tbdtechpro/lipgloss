# Attribution

This repository is an experiment in AI-assisted ("vibe-coded") software development. The Python code,
commit history, tests, and documentation were generated primarily by AI with minimal direct human
authorship of the implementation itself.

---

## Original Go Library

All credit for the design, architecture, and reference implementation belongs to the
[Charm](https://charm.sh) team.

> **Lip Gloss** — Style definitions for nice terminal layouts
> <https://github.com/charmbracelet/lipgloss>

The Go source files in this repository are reproduced directly from the upstream Charm project and
remain their copyright. They are included here solely as the reference implementation for the
Python port and will be removed once the Python port reaches feature parity.

**Charm team members and contributors:** see
<https://github.com/charmbracelet/lipgloss/graphs/contributors>

The Go Lip Gloss library is licensed under the MIT License. See [LICENSE](LICENSE) for the
full license text (which covers both the original Go code and the Python port).

---

## AI Tooling

The Python port was generated using:

| Tool | Role |
|------|------|
| **Claude** (Anthropic) | Primary code generation, translation from Go to Python, test writing, documentation |

The AI-generated code has been reviewed and directed by a human experimenter but has **not** been
independently validated for correctness, completeness, or production readiness.

---

## Dependencies

The Python port depends on the following open-source packages:

| Package | License | Purpose |
|---------|---------|---------|
| [wcwidth](https://github.com/jquast/wcwidth) | MIT | ANSI-aware string width measurement |
| [pytest](https://pytest.org) | MIT | Test runner |
| [pytest-cov](https://pytest-cov.readthedocs.io) | MIT | Coverage reporting |
| [black](https://black.readthedocs.io) | MIT | Code formatting |
| [isort](https://pycli.readthedocs.io/projects/isort) | MIT | Import sorting |
| [flake8](https://flake8.pycqa.org) | MIT | Linting |
| [mypy](https://mypy-lang.org) | MIT | Static type checking |

---

## Experiment Context

This port is part of an ongoing experiment to explore:

- How well large language models can translate non-trivial, idiomatic Go code to idiomatic Python
- The developer-experience of directing AI to build a complete library from scratch
- Whether AI-generated code can pass a real test suite and meet production-quality standards

The human role in this experiment was: experimental design, repository setup, direction of the AI,
review of outputs, and judgement calls on API design. The AI's role was: reading the Go reference,
writing Python implementations, writing tests, writing documentation, and iterating on bugs.

---

*Charm热爱开源 • Charm loves open source*
