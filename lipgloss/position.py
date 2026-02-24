"""
Position type and placement functions.

Port of: position.go

Position is a float in [0.0, 1.0]:
  0.0 = left / top
  0.5 = center
  1.0 = right / bottom

Constants: Top, Bottom, Left, Right, Center

Functions:
  place(width, height, h_pos, v_pos, s, **ws_opts) -> str
  place_horizontal(width, pos, s, **ws_opts)       -> str
  place_vertical(height, pos, s, **ws_opts)        -> str
"""
