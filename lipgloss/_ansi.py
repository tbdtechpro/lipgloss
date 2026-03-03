"""
Shared ANSI escape sequence utilities.

Internal module — not part of the public API.
"""

from __future__ import annotations

import re

# Matches the full range of ANSI/VT escape sequences:
#   ESC followed by one of:
#     - a C1 control character (@ through Z, \, or _)
#     - a CSI sequence: [ + optional parameter bytes + optional intermediate bytes + final byte
# This is broader than the common r"\x1b\[[0-9;]*[mK]" subset and correctly
# strips OSC, DCS, and other multi-byte escapes that the narrower pattern misses.
ANSI_RE = re.compile(r"\x1b(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")


def strip_ansi(s: str) -> str:
    """Remove all ANSI escape sequences from *s*."""
    return ANSI_RE.sub("", s)
