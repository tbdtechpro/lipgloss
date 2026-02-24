"""
Color types for Lip Gloss.

Port of: color.go

Implements the TerminalColor protocol and all concrete color types:
  - NoColor       — explicit absence of color
  - Color         — hex ("#FF5733") or ANSI index string ("21")
  - ANSIColor     — convenience wrapper for ANSI 0–15
  - AdaptiveColor — selects light or dark variant based on terminal background
  - CompleteColor — explicit values per color profile; no automatic degradation
  - CompleteAdaptiveColor — combines CompleteColor with light/dark adaptability

All color types must implement the TerminalColor protocol:
  resolve(renderer: Renderer) -> str
"""
