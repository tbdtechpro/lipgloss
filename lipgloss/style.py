"""
Style — the core styling primitive.

Port of: style.go, set.go, get.go, unset.go

Style is an immutable fluent builder. Every setter returns a new Style;
the receiver is never mutated. Properties are stored in an internal dict;
the presence of a key acts as the "is set" flag (equivalent to Go's
propKey bit-flags).

Key methods:
  render(*strings) -> str   Apply all set properties; return ANSI string.
  inherit(parent)  -> Style Copy unset properties from parent.
  copy()           -> Style Return an independent copy.
  set_string(*s)   -> Style Attach strings so render() works with no args.
"""
