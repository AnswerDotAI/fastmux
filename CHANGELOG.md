# Release notes

<!-- do not remove -->

## 0.0.3

### New Features

- Fix pasting control chars on tmux 3.7 with paste-buffer -S ([#6](https://github.com/AnswerDotAI/fastmux/issues/6))
- Add screen viewport capture, SGR mouse click/wheel input, and poll refinements (until/settle) with exact session pinning ([#4](https://github.com/AnswerDotAI/fastmux/issues/4))
- Add background sessions module (`fastmux.bg`) with named, managed sessions ([#3](https://github.com/AnswerDotAI/fastmux/issues/3))


## 0.0.2

### New Features

- Add bg module for named managed sessions driven by sid; rework poll to track last-seen state ([#2](https://github.com/AnswerDotAI/fastmux/issues/2))
- Add pyskills module and harden tmux server lookups ([#1](https://github.com/AnswerDotAI/fastmux/pull/1)), thanks to [@ncoop57](https://github.com/ncoop57)


## 0.0.1

- Initial MVP
