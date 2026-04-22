# incallide README Rewrite & Repo Cleanup — Design

**Issue:** [portfolio-improvements #6](https://github.com/dantraynor/portfolio-improvements/issues/6)
**Date:** 2026-04-22
**Author:** Daniel Traynor

## Goal

Turn a repo that currently communicates nothing (2-word README, four overlapping entrypoints, no license, no CI) into a project page a recruiter can understand in under 30 seconds. No behavior changes to the player code.

## Non-Goals

- No feature work on the player itself.
- No refactoring of `tidal_tui.py` internals.
- No screenshot capture (user will drop one in later).
- No automated GitHub topic setting (user will run `gh repo edit` manually).

## Changes

### 1. Canonical entrypoint: `tidal_tui.py`

The richest experience (Textual TUI with album covers) becomes the single supported entrypoint. `launch.sh` updated to run it.

### 2. Archive prior iterations

Move to `archive/`:

- `main.py` — original Rich-console CLI prototype.
- `enhanced_player.py` — expanded CLI with async playback progress.
- `simple_tui.py` — first Textual-based TUI, no album art.

Add `archive/README.md` explaining the evolution: CLI prototype → enhanced CLI → lighter TUI → current TUI. Framing: project history, not dead code.

### 3. Rewrite `README.md`

Sections, in order:

1. Title + one-line pitch + screenshot (`docs/screenshot.png`, placeholder with `<!-- TODO: capture and commit -->`).
2. **What it is** — terminal-native Tidal client with album art in the terminal.
3. **Why I built it** — wanted a keyboard-driven, stay-in-the-terminal alternative to the Tidal desktop app.
4. **Features** — HiFi streaming, search, album-art rendering, OAuth session persistence, keyboard shortcuts.
5. **Tech stack** — Python 3.11+, Textual, tidalapi, python-vlc, Rich, term-image.
6. **Install & run** — system prereqs (VLC), venv, `pip install -r requirements.txt`, `python tidal_tui.py`.
7. **Keyboard shortcuts** — pulled from `tidal_tui.py` bindings.
8. **Troubleshooting** — audio/auth gotchas (ported from `DEPLOYMENT.md`).
9. **Project history** — one-liner pointing to `archive/`.
10. **License** — MIT, link to `LICENSE`.

### 4. Delete `DEPLOYMENT.md`

Useful content folded into the new README's Install and Troubleshooting sections. The file references `/workspaces/incallide` container paths that don't apply outside the original dev environment.

### 5. Add `LICENSE`

Standard MIT license, "Copyright (c) 2026 Daniel Traynor".

### 6. Add `.github/workflows/ci.yml`

- Triggers: push + PR targeting `main`.
- Matrix: Python 3.11, 3.12 on `ubuntu-latest`.
- Steps:
  1. `actions/checkout@v4`
  2. `actions/setup-python@v5`
  3. `sudo apt-get update && sudo apt-get install -y vlc` (so `import vlc` resolves).
  4. `pip install -r requirements.txt`.
  5. `python -m py_compile tidal_tui.py archive/main.py archive/enhanced_player.py archive/simple_tui.py` — syntax-level smoke check.

### 7. `docs/` directory

Create `docs/` as the home for the README screenshot. Ship with a `.gitkeep` so the directory exists in git; README references `docs/screenshot.png` with a TODO comment.

## File tree after

```
.
├── .github/workflows/ci.yml     (new)
├── archive/
│   ├── README.md                (new)
│   ├── enhanced_player.py       (moved)
│   ├── main.py                  (moved)
│   └── simple_tui.py            (moved)
├── docs/
│   └── .gitkeep                 (new)
├── .env.example
├── .gitignore
├── LICENSE                      (new)
├── README.md                    (rewritten)
├── launch.sh                    (updated)
├── requirements.txt
├── setup.sh
└── tidal_tui.py                 (unchanged; now canonical)
```

## Verification

- `python -m py_compile tidal_tui.py` succeeds locally.
- `README.md` renders on GitHub without broken links.
- CI workflow passes on a PR.
- `LICENSE` file is detected by GitHub's license-detection.

## Out-of-band follow-ups (checklist in PR description)

- Capture a screenshot/GIF → `docs/screenshot.png`.
- `gh repo edit dantraynor/incallide --add-topic tidal,music-player,terminal,python,tui`.
