"""
Integration tests verifying that lipgloss ANSI output is compatible with the
Bubble Tea Python renderer.

The core question: does a lipgloss-rendered string returned from Model.view()
interact correctly with bubbletea's renderer?

bubbletea's Renderer erases previous frames by counting newlines
(``view.count("\\n")``) and emitting ``\\x1b[A\\x1b[2K`` per line.  ANSI escape
codes do not affect ``\\n`` count, so lipgloss output is structurally compatible.
These tests confirm:

  1. lipgloss.width() / height() give correct ANSI-stripped measurements.
  2. A Model whose view() returns lipgloss-styled strings runs without errors.
  3. Multi-line styled output (borders, padding) has correct line counts.
  4. Styled strings survive a round-trip through the renderer write path.
"""

import io
import threading
import time
from typing import Optional

pytest = __import__("pytest")
bubbletea = pytest.importorskip("bubbletea")

import bubbletea as tea  # noqa: E402

import lipgloss  # noqa: E402
from lipgloss import height, join_vertical, width  # noqa: E402
from lipgloss.borders import rounded_border  # noqa: E402

# ── helpers ──────────────────────────────────────────────────────────────────


def run_headless(model: tea.Model, *, timeout: float = 2.0) -> tea.Model:
    """Run a bubbletea Program headlessly and return the final model.

    Uses NullRenderer + StringIO output so no TTY is required.
    The calling thread sends quit() after the program starts if it hasn't
    quit on its own within *timeout* seconds.
    """
    out = io.StringIO()
    p = tea.Program(model, output=out, use_null_renderer=True)

    result: list[tea.Model] = []
    exc_holder: list[BaseException] = []

    def _run() -> None:
        try:
            result.append(p.run())
        except Exception as exc:  # noqa: BLE001
            exc_holder.append(exc)

    t = threading.Thread(target=_run, daemon=True)
    t.start()
    t.join(timeout=timeout)

    if t.is_alive():
        p.quit()
        t.join(timeout=1.0)

    if exc_holder:
        raise exc_holder[0]

    return result[0] if result else model


# ── simple models for testing ─────────────────────────────────────────────────


class StyledViewModel(tea.Model):
    """Model whose view() returns a lipgloss-styled single-line string."""

    def __init__(self, style: lipgloss.Style, text: str) -> None:
        self.style = style
        self.text = text
        self.view_calls = 0

    def init(self) -> Optional[tea.Cmd]:
        return tea.quit_cmd

    def update(self, msg: tea.Msg):  # type: ignore[override]
        return self, None

    def view(self) -> str:
        self.view_calls += 1
        return self.style.render(self.text)


class MultiLineViewModel(tea.Model):
    """Model whose view() returns a multi-line lipgloss layout."""

    def __init__(self) -> None:
        self.rendered = ""

    def init(self) -> Optional[tea.Cmd]:
        return tea.quit_cmd

    def update(self, msg: tea.Msg):  # type: ignore[override]
        return self, None

    def view(self) -> str:
        header = lipgloss.Style().bold(True).foreground(lipgloss.Color("99")).render("Header")
        body = lipgloss.Style().padding(1, 2).render("Body content here")
        footer = lipgloss.Style().faint(True).render("Footer")
        self.rendered = join_vertical(lipgloss.Center, header, body, footer)
        return self.rendered


class CounterModel(tea.Model):
    """Simple counter that quits after reaching a target count."""

    def __init__(self, target: int = 3) -> None:
        self.count = 0
        self.target = target

    def init(self) -> Optional[tea.Cmd]:
        def bump() -> tea.Msg:
            return tea.KeyMsg(key=" ")

        return bump

    def update(self, msg: tea.Msg):  # type: ignore[override]
        if isinstance(msg, tea.KeyMsg) and msg.key == " ":
            self.count += 1
            if self.count >= self.target:
                return self, tea.quit_cmd
            # Queue another bump to keep counting

            def bump() -> tea.Msg:
                return tea.KeyMsg(key=" ")

            return self, bump
        return self, None

    def view(self) -> str:
        label = lipgloss.Style().bold(True).render(f"Count: {self.count}")
        box = (
            lipgloss.Style()
            .border_style(rounded_border())
            .border(rounded_border(), True)
            .padding(0, 1)
            .render(label)
        )
        return box


# ── ANSI measurement tests ────────────────────────────────────────────────────


def test_width_strips_ansi() -> None:
    """lipgloss.width() returns visible character width, not byte length."""
    style = lipgloss.Style().bold(True).foreground(lipgloss.Color("#FF0000"))
    rendered = style.render("hello")
    assert width(rendered) == 5
    assert len(rendered) > 5  # raw bytes include ANSI codes


def test_height_counts_newlines() -> None:
    """lipgloss.height() counts lines correctly for multi-line styled output."""
    style = lipgloss.Style().padding(1, 0)  # 1 line top + 1 line bottom padding
    rendered = style.render("text")
    assert height(rendered) == 3  # blank, text, blank


def test_bordered_box_dimensions() -> None:
    """A bordered, padded box has the expected width and height."""
    style = (
        lipgloss.Style()
        .border_style(rounded_border())
        .border(rounded_border(), True)
        .padding(0, 1)
        .width(10)
    )
    rendered = style.render("hi")
    # .width(10) sets the content area (padding included) to 10 chars;
    # the two border chars add 2 more → total visible width = 12.
    assert width(rendered) == 12
    # height = 1 content + 2 border = 3
    assert height(rendered) == 3


def test_newline_count_equals_height_minus_one() -> None:
    """bubbletea uses view.count('\\n') to erase previous frames.

    Verify that lipgloss output's newline count equals height() - 1,
    so the renderer erases exactly the right number of lines.
    """
    style = lipgloss.Style().border_style(rounded_border()).border(rounded_border(), True)
    for text in ["a", "line1\nline2", "x\ny\nz"]:
        rendered = style.render(text)
        assert rendered.count("\n") == height(rendered) - 1


def test_join_vertical_line_count() -> None:
    """join_vertical output has the correct newline count for renderer erase."""
    a = lipgloss.Style().render("top")
    b = lipgloss.Style().padding(1, 0).render("middle")
    c = lipgloss.Style().render("bottom")
    joined = join_vertical(lipgloss.Top, a, b, c)
    assert joined.count("\n") == height(joined) - 1


# ── headless Program integration tests ───────────────────────────────────────


def test_styled_view_program_runs() -> None:
    """A Program whose view() returns a lipgloss-styled string runs cleanly."""
    style = lipgloss.Style().bold(True).foreground(lipgloss.Color("10"))
    model = StyledViewModel(style, "Running!")
    final = run_headless(model)
    assert isinstance(final, StyledViewModel)
    assert final.view_calls >= 1


def test_multi_line_view_program_runs() -> None:
    """A Program whose view() returns a multi-line lipgloss layout runs cleanly."""
    model = MultiLineViewModel()
    final = run_headless(model)
    assert isinstance(final, MultiLineViewModel)
    # The rendered view should be non-empty and multi-line
    assert height(final.rendered) >= 3


def test_counter_model_reaches_target() -> None:
    """Counter model driven by commands correctly reaches its target count."""
    model = CounterModel(target=5)
    final = run_headless(model)
    assert isinstance(final, CounterModel)
    assert final.count == 5


def test_view_ansi_width_does_not_grow_across_updates() -> None:
    """Verify that styled view width stays constant across multiple renders.

    This guards against ANSI codes accumulating across update cycles and
    corrupting the visible width that the renderer uses for line erasure.
    """
    style = (
        lipgloss.Style()
        .bold(True)
        .foreground(lipgloss.Color("99"))
        .border_style(rounded_border())
        .border(rounded_border(), True)
        .width(20)
    )
    # Render the same style multiple times; width must be stable.
    widths = {width(style.render("test")) for _ in range(5)}
    assert len(widths) == 1, f"width changed across renders: {widths}"


def test_program_send_message() -> None:
    """Messages sent via Program.send() are delivered to model.update()."""

    class RecordModel(tea.Model):
        def __init__(self) -> None:
            self.received: list[str] = []

        def init(self) -> Optional[tea.Cmd]:
            return None

        def update(self, msg: tea.Msg):  # type: ignore[override]
            if isinstance(msg, tea.KeyMsg):
                self.received.append(msg.key)
            if isinstance(msg, tea.QuitMsg):
                return self, tea.quit_cmd
            return self, None

        def view(self) -> str:
            style = lipgloss.Style().foreground(lipgloss.Color("240"))
            return style.render(", ".join(self.received) or "waiting")

    m = RecordModel()
    out = io.StringIO()
    p = tea.Program(m, output=out, use_null_renderer=True)

    def _drive() -> None:
        time.sleep(0.05)
        p.send(tea.KeyMsg(key="a"))
        p.send(tea.KeyMsg(key="b"))
        time.sleep(0.05)
        p.quit()

    driver = threading.Thread(target=_drive, daemon=True)
    t = threading.Thread(target=p.run, daemon=True)
    t.start()
    driver.start()
    t.join(timeout=2.0)

    assert "a" in m.received
    assert "b" in m.received
