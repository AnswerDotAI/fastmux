"""Drive and inspect tmux from Python: live session, window, and pane handles with CLI-style reprs

Modules:

- `fastmux.skill`: Work with tmux sessions, windows, and panes from Python, plus named background sessions keyed by sid. Use this when code needs to read what is on a terminal, send input to a TUI or other rich terminal app, build pane layouts, search text across terminals, or keep a terminal open that you and the user can both see. For plain line-oriented programs (REPLs, shells, ssh) use `ptymini.skill`'s bgterm sessions instead. They share this module's wait parameters (`wait_ms`, `until=`, `settle_ms`). tmux is for when the terminal itself matters."""

__version__ = "0.0.4"
from .core import *

