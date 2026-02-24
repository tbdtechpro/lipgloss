"""
Renderer — terminal output handler and color profile detector.

Port of: renderer.go

The Renderer wraps an output writer and lazily detects the terminal's
color profile (TrueColor → ANSI256 → ANSI → ASCII) and whether it has
a dark background.

Module-level helpers mirror the Go package-level functions:
  default_renderer()          -> Renderer
  set_default_renderer(r)
  new_renderer(w) -> Renderer
"""
