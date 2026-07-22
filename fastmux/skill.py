"""Live handles for tmux sessions, windows, and panes, with reprs that match the tmux CLI. Use this when code needs to read terminal screens or scrollback, drive interactive processes, build pane layouts, or search text across terminals.

fastmux shells out to the `tmux` binary and keys every object on its server-unique tmux id (`$1`, `@1`, `%1`), so handles stay valid however sessions get renamed or windows renumbered. A handle is a dict of the fields tmux reports (`p.width`, `p.cmd`, `p.dead`), `refresh()` re-queries it in place, and any failed tmux command raises `TmuxError` carrying tmux's own message.

Core APIs:
- `tmux()` returns all sessions as a session/window/pane tree, empty if no server is running. `tmux(target)` takes standard tmux target syntax and returns the matching handle. A session name or `$id` gives a `Session`, `sess:win` or `@id` a `Window`, `sess:win.pane` or `%id` a `Pane`.
- `new_session(cmd=None, name=None, width=None, height=None, remain=False)` starts a detached session and returns it. `remain=True` keeps finished panes around so their exit status stays readable.
- `Session` has `windows`, `panes`, `pane` (the active one), `new_window(cmd)`, `rename`, `attach_command`, and `kill`. `Window` has `panes`, `select`, `layout('tiled')`, `rename`, and `kill`.

Reading a pane: `repr(p)` is the pane's current screen, and `p.text`/`p.ansi` give that screen as a string, plain or with escape sequences. The whole transcript (scrollback plus screen) indexes like a list of lines, so `p[3]` is one line, `p[-200:]` is the last 200 as a `Capture` with a source footer, and `len(p)` counts lines. String keys keep dict lookup (`p['id']`); ints and slices read the transcript.

Writing to a pane: `p.send(text)` pastes literal text through a tmux buffer with no key-name interpretation, `p.send_keys('C-c', 'Enter')` sends tmux key names, and `p.interrupt()` is Ctrl-C. Each polls afterwards and returns a fresh `Capture`. Output takes time to appear, so pass `wait_ms` rather than re-reading immediately, e.g. `p.send('ls\n', wait_ms=2000)`. `p.wait(timeout_ms=...)` blocks until the pane's command exits and returns its status (`None` on timeout); the pane needs `remain=True` to outlive its command.

Layouts: `p.rsplit()`, `p.bsplit()`, `p.lsplit()`, and `p.asplit()` split with the new pane to the right/below/left/above, taking `cmd`, `size`, `cwd`, and `env`. Splits and new windows never steal focus unless `focus=True`, and new sessions start detached, so building layouts beside an attached user never moves their cursor. `p.resize(width, height)`, `p.zoom()`, and `p.select()` adjust a single pane. `.kill()` on any handle destroys it, raising a `sys.audit` event first.

Searching: `.search(pattern)` on a `Pane`, `Window`, or `Session`, or `tmux().search(pattern)` for the whole server, greps the last `SEARCH_LINES` lines of each transcript, substring by default and regex with `regex=True`. Hits display rg-style, and `tmux(hit.target)` returns the pane that printed the line.

Important:
Target only ids and `target` strings taken from fastmux objects, since hand-built name targets can be ambiguous to tmux (a session named `5` can resolve as a window index). A tmux server is shared, and killing, resizing, or writing to another session's panes changes what an attached user sees, so work in sessions you created and kill them when done. Run `doc(fastmux.core)` for the module overview and `doc(obj)` for full parameter docments before first use.
"""

from fastmux.core import *

__all__ = ['tmux', 'new_session', 'TmuxError', 'Session', 'Window', 'Pane', 'Capture',
           'Sessions', 'Windows', 'Panes', 'SearchMatch', 'SearchResults', 'SEARCH_LINES']
