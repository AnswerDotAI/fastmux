"""Drive and inspect tmux from Python: live session, window, and pane handles with CLI-style reprs

Modules:

- `fastmux.skill`: Work with tmux sessions, windows, and panes from Python, plus named background sessions keyed by sid. Use this when code needs to read what is on a terminal, send input to an interactive program, build pane layouts, search text across terminals, or keep a terminal open that you and the user can both see."""

__version__ = "0.0.3"
from .core import *

