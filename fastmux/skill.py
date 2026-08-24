"""Work with tmux sessions, windows, and panes from Python, plus named background sessions keyed by sid. Use this when code needs to read what is on a terminal, send input to an interactive program, build pane layouts, search text across terminals, or keep a terminal open that you and the user can both see.

fastmux shells out to the `tmux` binary and keys every object on its server-unique tmux id (`$1`, `@1`, `%1`), so handles stay valid however sessions get renamed or windows renumbered. A handle is a dict of the fields tmux reports (`p.width`, `p.cmd`, `p.dead`), `refresh()` re-queries it in place, and any failed tmux command raises `TmuxError` carrying tmux's own message.

Two surfaces share those objects, and the choice is about who holds the reference:
- Handles (`fastmux.core`): hold `Session`/`Window`/`Pane` objects when you work in a persistent process and the sessions are yours - richest API, best reprs.
- Sids (`fastmux.bg`): address by name when the session outlives any one call, is shared with a user who attaches by name (`tmux attach -t <sid>`), or is referred to across contexts. A sid is a session name, a `%pane_id`, a handle, or None for the current pane; `bg.pane(sid)` bridges back to the handle surface.

Core APIs (handles):
- `tmux()` returns all sessions as a session/window/pane tree, empty if no server is running. `tmux(target)` takes standard tmux target syntax and returns the matching handle. A session name or `$id` gives a `Session`, `sess:win` or `@id` a `Window`, `sess:win.pane` or `%id` a `Pane`. `current_pane()` is the caller's own pane inside tmux, else the active pane of the most recent session.
- `new_session(cmd=None, name=None, width=None, height=None, remain=False)` starts a detached session and returns it. `remain=True` keeps finished panes around so their exit status stays readable.
- `Session` has `windows`, `panes`, `pane` (the active one), `new_window(cmd)`, `rename`, `attach_command`, and `kill`. `Window` has `panes`, `select`, `layout('tiled')`, `rename`, and `kill`.

Background sessions (sids):
- `start_session(sid=None, cmd=None, ...)` creates-or-reuses the named session, detached and managed: `remain` set, dead-pane banner cleared, and the created pane recorded so later splits don't change what the sid addresses. With `sid=None` it generates a `fastmux-`-prefixed name; `managed_sessions()` lists every session it created; `close(sid)` kills the session owning the sid's pane (a `%pane_id` sid means its *owning session* dies).
- `send(sid, chars)`, `send_keys(sid, *keys)`, `interrupt(sid)`, `poll(sid)`, and `display(sid)` mirror the `Pane` verbs below with a sid in front. Anything else (`wait`, `search`, splits, slicing) goes through `pane(sid)`.

Reading a pane: `repr(p)` is the pane's current screen, and `p.text`/`p.ansi` give that screen as a string, plain or with escape sequences. The whole transcript (scrollback plus screen) indexes like a list of lines, so `p[3]` is one line, `p[-200:]` is the last 200 as a `Capture` with a source footer, and `len(p)` counts lines. String keys keep dict lookup (`p['id']`); ints and slices read the transcript.

Writing to a pane: `p.send(text)` pastes literal text through a tmux buffer with no key-name interpretation, `p.send_keys('C-c', 'Enter')` sends tmux key names, and `p.interrupt()` is Ctrl-C. Each polls afterwards and returns a fresh `Capture`. Polling waits for the pane to differ from its *last-seen state* (the last capture a verb returned for it), so output that arrived between calls satisfies the next `poll` immediately, and `poll(sid, wait_ms=...)` after an unwatched gap never waits on already-arrived output. Output takes time to appear, so pass `wait_ms` rather than re-reading immediately, e.g. `p.send('ls\n', wait_ms=2000)`. `p.wait(timeout_ms=...)` blocks until the pane's command exits and returns its status (`None` on timeout); the pane needs `remain` to outlive its command.

Waiting: every wait is bounded and returns the latest `Capture` on timeout rather than raising, so the caller reads what came back and decides. Keep bounds short - a few seconds of `wait_ms`, 1-3s of `settle_ms` - and re-poll on evidence instead of taking one long blind wait: a pane still busy at the bound then shows itself busy promptly, and a spinner still animating at the third short poll is a finding, not a nuisance. `until=` waits for a regex to match the capture and returns within one `interval_ms` of matching; it tests presence, not arrival, so match text only the awaited output can produce. `settle_ms=` samples on after the wait until the capture has stopped changing for that long. Quiet costs the full `settle_ms` even when the pane finished long ago, the settle phase runs at most `settle_ms` past the `wait_ms` deadline (unused `wait_ms` is its budget for repaint resets), and a pane with a spinner or clock never settles: against those, `until` is the only sharp tool. `poll` alone is the no-send wait: `poll(sid, settle_ms=2000)` watches without typing.

Layouts: `p.rsplit()`, `p.bsplit()`, `p.lsplit()`, and `p.asplit()` split with the new pane to the right/below/left/above, taking `cmd`, `size`, `cwd`, and `env`. Splits and new windows never steal focus unless `focus=True`, and new sessions start detached, so building layouts beside an attached user never moves their cursor. `p.resize(width, height)`, `p.zoom()`, and `p.select()` adjust a single pane. `.kill()` on any handle destroys it, raising a `sys.audit` event first.

Searching: `.search(pattern)` on a `Pane`, `Window`, or `Session`, or `tmux().search(pattern)` for the whole server, greps the last `SEARCH_LINES` lines of each transcript, substring by default and regex with `regex=True`. Hits display rg-style, and `tmux(hit.target)` returns the pane that printed the line.

Important:
Target only ids, `target` strings, and sids taken from fastmux objects or agreed with the user, since hand-built name targets can be ambiguous to tmux (a session named `5` can resolve as a window index). A tmux server is shared, and killing, resizing, or writing to another session's panes changes what an attached user sees, so work in sessions you created and kill them when done; `sid=None` addresses the user's own current pane, so drive it only when they offer it. tmux snapshot polling is not a byte-perfect log transport: for huge structured outputs, write to a file instead. Run `doc(fastmux.core)` or `doc(fastmux.bg)` for module overviews and `doc(obj)` for full parameter docments before first use.
"""

from fastmux.core import *
from fastmux.bg import *
from pyskills.core import allow

__all__ = ['tmux', 'new_session', 'current_pane', 'TmuxError', 'Session', 'Window', 'Pane', 'Capture',
           'Sessions', 'Windows', 'Panes', 'SearchMatch', 'SearchResults', 'SEARCH_LINES',
           'SESSION_PREFIX', 'start_session', 'pane', 'send', 'send_keys', 'interrupt', 'poll', 'display',
           'close', 'managed_sessions']

allow(start_session, pane, send, send_keys, interrupt, poll, display, close, managed_sessions)
