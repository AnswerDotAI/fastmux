r"""Work with tmux sessions, windows, and panes from Python, plus named background sessions keyed by sid. Use this when code needs to read what is on a terminal, send input to a TUI or other rich terminal app, build pane layouts, search text across terminals, or keep a terminal open that you and the user can both see. For plain line-oriented programs (REPLs, shells, ssh) use `ptymini.skill`'s bgterm sessions instead. They share this module's wait parameters (`wait_ms`, `until=`, `settle_ms`). tmux is for when the terminal itself matters.

fastmux drives the `tmux` binary. A handle is a dict of tmux's fields (`p.width`, `p.cmd`, `p.dead`) identified by tmux's server-unique id (`$1` session, `@1` window, `%1` pane), so renaming a session or renumbering windows leaves it valid; `refresh()` updates in place. Failed tmux commands raise `TmuxError` with tmux's message. `doc(fastmux.core)`/`doc(fastmux.bg)` for overviews; `doc(obj)` before first use.

## Handles or sids

Same objects, two ways to address them; choose by who holds the reference:
- Handles (`fastmux.core`: `Session`/`Window`/`Pane`): persistent process, sessions you own; richest API and reprs. `tmux()` = whole tree, `tmux(target)` = one handle, `current_pane()` = caller's pane, `new_session()` = new detached session.
- Sids (`fastmux.bg`): by name, for sessions that outlive a call, are shared with a user (`tmux attach -t <sid>`), or are referenced across contexts. A sid is a session name, `%pane_id`, handle, or `None` (current pane). `start_session(sid)` creates/reuses; `managed_sessions()` lists what it created; `close(sid)` kills the owning session. `send`/`send_keys`/`interrupt`/`poll`/`click`/`wheel`/`display`/`screen` take a sid first and otherwise match the `Pane` methods; for anything else (`wait`, `search`, splits, slicing) use `pane(sid)`.

## Reading and writing a pane

`repr(p)` = current screen; `p.text`/`p.ansi` = it as plain text/with escapes. The transcript (scrollback + screen) indexes like a list: `p[3]` one line, `p[-200:]` a `Capture` with source footer, `len(p)` line count; str keys still read fields (`p['id']`). For TUIs, `p.screen()` gives a `Screen`: viewport plus size and cursor.

`p.send(text)` pastes literally via a tmux buffer; `p.send_keys('C-c', 'Enter')` sends key names; `p.interrupt()` = Ctrl-C; `p.click(target)` clicks a `(col,row)` or an on-screen str/regex; `p.wheel(n)` scrolls. Each then polls and returns a fresh `Capture`. A poll waits for the pane to differ from its last returned capture, so output that arrived between calls satisfies the next poll at once. Output takes time: pass `wait_ms` (`p.send('ls\n', wait_ms=2000)`) rather than re-reading straight away. `p.wait()` waits for the command to exit and returns its status.

## Waiting

Every wait is bounded; on timeout it returns the latest `Capture` (never raises), so read it, then decide. Keep waits short: a few seconds of `wait_ms`, 1-3 s of `settle_ms`; a spinner still going after three short polls means rethink what you're waiting for. `until=` waits for a regex: pick one only the awaited output produces. `settle_ms` waits until the capture has stopped changing for that long; spinners/clocks never settle, so wait for identifiable output with `until` instead. `poll(sid, settle_ms=2000)` watches without sending input.

## Layouts and search

`p.rsplit()`/`bsplit()`/`lsplit()`/`asplit()` put the new pane right/below/left/above. Splits and new windows never take focus unless `focus=True`, and new sessions start detached, so building layouts beside an attached user never moves their cursor. `p.resize()`/`zoom()`/`select()` adjust one pane; `.kill()` on any handle destroys it (raising a `sys.audit` event first).

`.search(pattern)` on a `Pane`/`Window`/`Session`, or `tmux().search(pattern)` server-wide, greps recent transcript lines; hits display rg-style, and `tmux(hit.target)` returns the pane that printed the line.

## Sharing the server

Use only ids, `target` strings, and sids from fastmux objects or the user: hand-built targets are ambiguous (a session named `5` can resolve as a window index). The server is shared: killing, resizing, or writing to another session's panes changes what an attached user sees. Work in sessions you created; kill them when done. `sid=None` = the user's current pane: use only when offered. Polling snapshots the screen, not a byte-perfect log: write large structured output to a file.
"""

from fastmux.core import *
from fastmux.bg import *
from pyskills.core import allow

__all__ = ['tmux', 'new_session', 'current_pane', 'TmuxError', 'Session', 'Window', 'Pane', 'Capture', 'Screen',
           'Sessions', 'Windows', 'Panes', 'SearchMatch', 'SearchResults', 'SEARCH_LINES',
           'SESSION_PREFIX', 'start_session', 'pane', 'send', 'send_keys', 'interrupt', 'poll', 'click', 'wheel', 'display', 'screen',
           'close', 'managed_sessions']

allow(tmux, current_pane, start_session, pane, send, send_keys, interrupt, poll, click, wheel, display, screen, close, managed_sessions,
        {
            Sessions: ['search'],
            Session: ['refresh', 'windows', 'panes', 'pane', 'search'],
            Window: ['refresh', 'panes', 'search'],
            Pane: ['refresh', 'fmt', 'capture', 'text', 'ansi', 'display', 'screen', 'click', 'wheel', 'poll', 'wait', 'search'],
        })
