#!/bin/bash

# Tidal Terminal Player Setup Script
echo "🎵 Setting up Tidal Terminal Player..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv tidal_player_env

# Activate virtual environment
echo "🔄 Activating virtual environment..."
source tidal_player_env/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📥 Installing required packages..."
pip install -r requirements.txt

# Make main.py executable
chmod +x main.py

echo "✅ Setup complete!"
echo ""
echo "To run the Tidal Terminal Player:"
echo "1. Activate the virtual environment: source tidal_player_env/bin/activate"
echo "2. Run the player: python3 main.py"
echo ""
echo "🎵 Happy listening!"