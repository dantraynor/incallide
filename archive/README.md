# archive/

Earlier iterations of the project, kept for posterity. **None of these are the current entrypoint** — see [`tidal_tui.py`](../tidal_tui.py) in the repo root.

| File | What it was |
| --- | --- |
| `main.py` | The original prototype: a Rich-console command-line player. Minimal feature set, useful as a reference for the VLC + tidalapi integration. |
| `enhanced_player.py` | A fuller CLI iteration with async playback progress, now superseded by the Textual TUI. |
| `simple_tui.py` | The first Textual-based TUI. Lighter than `tidal_tui.py` but without album-art rendering. |

These files are not guaranteed to run against the current `requirements.txt` and are not exercised by CI's compile check beyond syntax validation.
