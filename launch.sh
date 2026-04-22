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
