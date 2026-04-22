# incallide

A terminal-native music player for [Tidal](https://tidal.com), with album art rendered in the terminal.

<!-- TODO: capture and commit a screenshot/GIF to docs/screenshot.png -->
![incallide screenshot](docs/screenshot.png)

## What it is

`incallide` is a keyboard-driven TUI (built with [Textual](https://textual.textualize.io/)) that streams from your Tidal subscription, renders album covers inline with [term-image](https://github.com/AnonymouX47/term-image), and drives playback through [VLC](https://www.videolan.org/). Search, browse, and play without leaving the terminal.

## Why I built it

The Tidal desktop app is heavy and mouse-oriented. I wanted a client I could drive from the keyboard, keep pinned next to my editor in a tiling WM or tmux session, and still get HiFi streaming with cover art. I also wanted an excuse to build something non-trivial with Textual.

## Features

- HiFi / lossless streaming via `tidalapi`
- In-terminal album art via `term-image`
- Full keyboard navigation (vim-style `hjkl` + shortcuts)
- Search → play flow without leaving the keyboard
- OAuth session persistence (log in once)
- VLC-backed audio with volume control

## Tech stack

- **Python 3.11+**
- **[Textual](https://textual.textualize.io/)** — TUI framework
- **[tidalapi](https://github.com/tamland/python-tidal)** — Tidal API client
- **[python-vlc](https://pypi.org/project/python-vlc/)** — audio playback
- **[Rich](https://rich.readthedocs.io/)** — terminal rendering primitives
- **[term-image](https://github.com/AnonymouX47/term-image)** — inline image rendering

## Install & run

### Prerequisites

- Python 3.11 or newer
- [VLC](https://www.videolan.org/) installed on the system
  - macOS: `brew install vlc`
  - Debian/Ubuntu: `sudo apt install vlc`
- A Tidal account

### Setup

```bash
git clone https://github.com/dantraynor/incallide.git
cd incallide
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Run

```bash
python tidal_tui.py
# or
./launch.sh
```

First launch opens a browser for Tidal OAuth; the session is cached at `~/.tidal_session.json`.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `ctrl+s` | Focus search |
| `enter` | Play selected track |
| `space` | Play / pause |
| `n` | Next track |
| `p` | Previous track |
| `=` / `-` | Volume up / down |
| `j` / `k` | Move down / up |
| `h` / `l` | Move left / right |
| `ctrl+c` | Quit |

## Troubleshooting

- **No sound:** confirm VLC works outside the app (`vlc --version`) and your system has an active audio output.
- **Login fails:** delete `~/.tidal_session.json` and re-run to force a fresh OAuth flow.
- **`ImportError: vlc`:** install VLC at the system level, not just `python-vlc` — the Python binding wraps the native library.

## Project history

Earlier CLI/TUI iterations live in [`archive/`](archive/). See [`archive/README.md`](archive/README.md) for context on each.

## License

[MIT](LICENSE) © 2026 Daniel Traynor.
