# incallide README Rewrite & Repo Cleanup — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rewrite the `incallide` README and clean up the repo so a recruiter understands the project in under 30 seconds.

**Architecture:** File moves + documentation rewrite. No application code changes. `tidal_tui.py` becomes the canonical entrypoint; three prior iterations move to `archive/`; `DEPLOYMENT.md` is folded into the new README; `LICENSE`, `CI`, and `docs/` directories are added.

**Tech Stack:** Markdown, Bash, GitHub Actions YAML. Plan references Python 3.11+ / Textual / tidalapi / python-vlc / Rich / term-image.

**Spec:** [`docs/superpowers/specs/2026-04-22-readme-rewrite-design.md`](../specs/2026-04-22-readme-rewrite-design.md)

---

## Task 1: Archive prior entrypoints

**Files:**
- Create: `archive/README.md`
- Move: `main.py` → `archive/main.py`
- Move: `enhanced_player.py` → `archive/enhanced_player.py`
- Move: `simple_tui.py` → `archive/simple_tui.py`

- [ ] **Step 1: Create the archive directory and move files with git mv**

Run:
```bash
mkdir -p archive
git mv main.py archive/main.py
git mv enhanced_player.py archive/enhanced_player.py
git mv simple_tui.py archive/simple_tui.py
```

- [ ] **Step 2: Create `archive/README.md`**

Write this exact content to `archive/README.md`:

```markdown
# archive/

Earlier iterations of the project, kept for posterity. **None of these are the current entrypoint** — see [`tidal_tui.py`](../tidal_tui.py) in the repo root.

| File | What it was |
| --- | --- |
| `main.py` | The original prototype: a Rich-console command-line player. Minimal feature set, useful as a reference for the VLC + tidalapi integration. |
| `enhanced_player.py` | A fuller CLI iteration with async playback progress, now superseded by the Textual TUI. |
| `simple_tui.py` | The first Textual-based TUI. Lighter than `tidal_tui.py` but without album-art rendering. |

These files are not guaranteed to run against the current `requirements.txt` and are not exercised by CI's compile check beyond syntax validation.
```

- [ ] **Step 3: Verify working tree**

Run:
```bash
git status
ls archive/
```
Expected: `archive/` contains `README.md`, `main.py`, `enhanced_player.py`, `simple_tui.py`. `git status` shows renames and a new untracked `archive/README.md`.

- [ ] **Step 4: Commit**

Run:
```bash
git add archive/
git commit -m "Archive earlier player iterations to archive/"
```

---

## Task 2: Update `launch.sh` to use the canonical entrypoint

**Files:**
- Modify: `launch.sh`

- [ ] **Step 1: Replace `launch.sh` with an updated version**

Write this exact content to `launch.sh`:

```bash
#!/bin/bash

# incallide launch script
echo "Launching incallide..."

if [ ! -d ".venv" ]; then
    echo "Virtual environment not found. Run: python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

if ! command -v vlc &> /dev/null; then
    echo "VLC not found. Install it (e.g. 'brew install vlc' on macOS or 'apt install vlc' on Debian/Ubuntu)."
    exit 1
fi

source .venv/bin/activate
python tidal_tui.py
```

- [ ] **Step 2: Keep it executable**

Run:
```bash
chmod +x launch.sh
```

- [ ] **Step 3: Commit**

Run:
```bash
git add launch.sh
git commit -m "Point launch.sh at the canonical tidal_tui.py entrypoint"
```

---

## Task 3: Delete outdated `DEPLOYMENT.md`

**Files:**
- Delete: `DEPLOYMENT.md`

- [ ] **Step 1: Remove the file**

Run:
```bash
git rm DEPLOYMENT.md
```

- [ ] **Step 2: Commit**

Run:
```bash
git commit -m "Remove outdated DEPLOYMENT.md (content folded into README)"
```

---

## Task 4: Add `docs/` directory for screenshots

**Files:**
- Create: `docs/.gitkeep`

- [ ] **Step 1: Create the directory and placeholder**

Run:
```bash
mkdir -p docs
touch docs/.gitkeep
```

- [ ] **Step 2: Commit**

Run:
```bash
git add docs/.gitkeep
git commit -m "Add docs/ directory for screenshots and media"
```

---

## Task 5: Add MIT `LICENSE`

**Files:**
- Create: `LICENSE`

- [ ] **Step 1: Write the MIT license**

Write this exact content to `LICENSE`:

```
MIT License

Copyright (c) 2026 Daniel Traynor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

- [ ] **Step 2: Commit**

Run:
```bash
git add LICENSE
git commit -m "Add MIT LICENSE"
```

---

## Task 6: Rewrite `README.md`

**Files:**
- Modify: `README.md` (full rewrite)

- [ ] **Step 1: Overwrite `README.md`**

Write this exact content to `README.md`:

````markdown
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
````

- [ ] **Step 2: Commit**

Run:
```bash
git add README.md
git commit -m "Rewrite README: overview, tech stack, install, shortcuts, license"
```

---

## Task 7: Add CI workflow

**Files:**
- Create: `.github/workflows/ci.yml`

- [ ] **Step 1: Create the workflow directory**

Run:
```bash
mkdir -p .github/workflows
```

- [ ] **Step 2: Write the workflow**

Write this exact content to `.github/workflows/ci.yml`:

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  install-and-smoke:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.11", "3.12"]

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install VLC
        run: |
          sudo apt-get update
          sudo apt-get install -y vlc

      - name: Install Python dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Syntax smoke check
        run: |
          python -m py_compile tidal_tui.py
          python -m py_compile archive/main.py
          python -m py_compile archive/enhanced_player.py
          python -m py_compile archive/simple_tui.py
```

- [ ] **Step 3: Verify locally that the py_compile steps pass**

Run:
```bash
python -m py_compile tidal_tui.py archive/main.py archive/enhanced_player.py archive/simple_tui.py
echo "exit=$?"
```
Expected: `exit=0` (no output above it).

- [ ] **Step 4: Commit**

Run:
```bash
git add .github/workflows/ci.yml
git commit -m "Add CI workflow: install deps + py_compile smoke check"
```

---

## Task 8: Verification pass

- [ ] **Step 1: Confirm the file tree matches the spec**

Run:
```bash
ls -la
ls archive/
ls .github/workflows/
ls docs/
```
Expected (root): `.github/`, `.context/`, `.env.example`, `.gitignore`, `LICENSE`, `README.md`, `archive/`, `docs/`, `launch.sh`, `requirements.txt`, `setup.sh`, `tidal_tui.py`. No `main.py`, `enhanced_player.py`, `simple_tui.py`, or `DEPLOYMENT.md` in root.

- [ ] **Step 2: Confirm no remaining references to the deleted/moved files at the repo root**

Use the Grep tool with pattern `main\.py|enhanced_player\.py|simple_tui\.py|DEPLOYMENT\.md` across the repo. Every match must be inside `archive/README.md`, `README.md` ("project history" link), `.github/workflows/ci.yml` (archive compile steps), or the spec/plan docs. Any match in `launch.sh`, `setup.sh`, or `tidal_tui.py` is a bug — fix and recommit.

- [ ] **Step 3: Confirm `README.md` renders without broken internal links**

Open `README.md` and verify these links exist in the repo:
- `docs/screenshot.png` — OK to be missing (placeholder); there is an HTML `<!-- TODO -->` comment above the image.
- `archive/` and `archive/README.md` — must exist.
- `LICENSE` — must exist.

- [ ] **Step 4: Confirm py_compile passes locally**

Run:
```bash
python -m py_compile tidal_tui.py archive/main.py archive/enhanced_player.py archive/simple_tui.py && echo OK
```
Expected: `OK`.

If Python 3.11+ isn't installed locally and the import fails on a dependency, the compile step in CI will still exercise it — do not treat missing local deps as a blocker.

- [ ] **Step 5: Push branch and open PR**

Run:
```bash
git push -u origin dantraynor/readme-rewrite
gh pr create --title "Rewrite README and clean up repo" --body "$(cat <<'EOF'
## Summary
- Rewrite `README.md` with overview, motivation, tech stack, install/run, shortcuts, troubleshooting, license.
- Promote `tidal_tui.py` to the canonical entrypoint; archive `main.py`, `enhanced_player.py`, `simple_tui.py` to `archive/` with a history note.
- Delete outdated `DEPLOYMENT.md`; fold relevant content into the README.
- Add MIT `LICENSE`.
- Add `.github/workflows/ci.yml` that installs VLC + Python deps and runs a `py_compile` smoke check on Python 3.11 and 3.12.
- Add empty `docs/` directory ready for a screenshot.

Closes dantraynor/portfolio-improvements#6.

## Follow-ups for me (not in this PR)
- [ ] Capture a screenshot/GIF of the TUI and commit it to `docs/screenshot.png`.
- [ ] Run: `gh repo edit dantraynor/incallide --add-topic tidal,music-player,terminal,python,tui`.

## Test plan
- [ ] CI passes on both Python 3.11 and 3.12.
- [ ] `README.md` renders on GitHub with no broken links (screenshot placeholder is expected).
- [ ] GitHub detects the MIT license in the repo sidebar.
EOF
)"
```
Expected: PR URL is printed.

---

## Rollback

Each task is its own commit. To revert any task, `git revert <sha>` on the corresponding commit. The archive task uses `git mv` so a revert restores the files to the root.
