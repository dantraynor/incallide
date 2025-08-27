#!/bin/bash

# Incallide Mini Player Launch Script
# This script is called by the Tidal Luna plugin to launch the terminal player

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🎵 Launching Incallide Mini Player...${NC}"

# Check if we're in the right directory
if [ ! -f "mini_player.py" ]; then
    # Try to find the incallide directory
    if [ -d "$HOME/incallide" ]; then
        cd "$HOME/incallide"
    elif [ -d "/workspaces/incallide" ]; then
        cd "/workspaces/incallide"
    else
        echo -e "${YELLOW}Warning: Could not find incallide directory${NC}"
    fi
fi

# Check if virtual environment exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
elif [ -d "venv" ]; then
    source venv/bin/activate
else
    echo -e "${YELLOW}No virtual environment found, using system Python${NC}"
fi

# Check if websockets is installed
python3 -c "import websockets" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing required packages..."
    pip install websockets rich pynput --quiet
fi

# Run the mini player
python3 mini_player.py

# Keep terminal open on exit
echo ""
echo "Press any key to close this window..."
read -n 1