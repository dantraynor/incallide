#!/bin/bash

# incallide setup script
echo "Setting up incallide..."

if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required. Install it and try again."
    exit 1
fi

echo "Creating virtual environment (.venv)..."
python3 -m venv .venv

echo "Activating virtual environment..."
source .venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
pip install -r requirements.txt

echo ""
echo "Setup complete. To run incallide:"
echo "  source .venv/bin/activate"
echo "  python tidal_tui.py"
echo ""
echo "Note: VLC must also be installed on your system (brew install vlc / apt install vlc)."
