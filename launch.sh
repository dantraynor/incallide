#!/bin/bash

# Tidal Terminal Player Launch Script
echo "🎵 Launching Tidal Terminal Player..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run the setup first."
    exit 1
fi

# Check if VLC is installed
if ! command -v vlc &> /dev/null; then
    echo "❌ VLC is not installed. Installing VLC..."
    sudo apt update && sudo apt install -y vlc-bin vlc-plugin-base libvlc-dev
fi

# Activate virtual environment and run the player
echo "🚀 Starting Tidal Terminal Player..."
source .venv/bin/activate
python main.py
