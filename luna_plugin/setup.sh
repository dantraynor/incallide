#!/bin/bash

# Incallide Luna Plugin Setup Script for macOS
echo "🎵 Incallide Luna Plugin Setup"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    echo -e "${RED}❌ This plugin is designed for macOS only${NC}"
    exit 1
fi

# Check Python version
echo "Checking Python version..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    echo -e "${GREEN}✓ Python $PYTHON_VERSION found${NC}"
    
    # Check if version is 3.9 or higher
    if [[ $(echo "$PYTHON_VERSION 3.9" | awk '{print ($1 >= $2)}') -eq 0 ]]; then
        echo -e "${YELLOW}⚠️  Python 3.9 or higher is recommended${NC}"
    fi
else
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    echo "Please install Python 3.9 or later from python.org"
    exit 1
fi

# Check for Tidal/Tidal Luna
echo "Checking for Tidal installation..."
TIDAL_FOUND=false
for app in "TIDAL" "Tidal" "Tidal Luna"; do
    if [[ -d "/Applications/$app.app" ]] || [[ -d "$HOME/Applications/$app.app" ]]; then
        echo -e "${GREEN}✓ Found: $app${NC}"
        TIDAL_FOUND=true
        break
    fi
done

if [[ "$TIDAL_FOUND" == false ]]; then
    echo -e "${YELLOW}⚠️  TIDAL/Tidal Luna not found${NC}"
    echo "Please install TIDAL or Tidal Luna first"
    echo "The plugin will still be installed but won't work without Tidal"
fi

# Create virtual environment
echo "Creating virtual environment..."
if [[ -d "venv" ]]; then
    echo -e "${YELLOW}Virtual environment already exists${NC}"
    read -p "Do you want to recreate it? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        echo -e "${GREEN}✓ Virtual environment recreated${NC}"
    fi
else
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip --quiet

# Install requirements
echo "Installing dependencies..."
if pip install -r requirements.txt; then
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}❌ Failed to install dependencies${NC}"
    echo "You may need to install Xcode Command Line Tools:"
    echo "  xcode-select --install"
    exit 1
fi

# Create config directory
CONFIG_DIR="$HOME/.incallide-luna"
if [[ ! -d "$CONFIG_DIR" ]]; then
    mkdir -p "$CONFIG_DIR"
    echo -e "${GREEN}✓ Created config directory: $CONFIG_DIR${NC}"
fi

# Create launch script
echo "Creating launch script..."
cat > run.sh << 'EOF'
#!/bin/bash
# Activate virtual environment and run the plugin
source venv/bin/activate
python src/main.py "$@"
EOF
chmod +x run.sh
echo -e "${GREEN}✓ Created run.sh launch script${NC}"

# Test the installation
echo ""
echo "Testing installation..."
if python src/main.py --test > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Installation test passed${NC}"
else
    echo -e "${YELLOW}⚠️  Installation test had issues${NC}"
    echo "Run './run.sh --test' for details"
fi

# Check for accessibility permissions
echo ""
echo "Checking accessibility permissions..."
echo -e "${YELLOW}⚠️  IMPORTANT: Grant accessibility permissions${NC}"
echo "   1. Open System Preferences"
echo "   2. Go to Security & Privacy → Privacy → Accessibility"
echo "   3. Add Terminal (or your terminal app) to the list"
echo "   4. Check the box to enable"
echo ""

# Success message
echo -e "${GREEN}✅ Setup complete!${NC}"
echo ""
echo "To run the plugin:"
echo "  ./run.sh                  # Basic mode"
echo "  ./run.sh --auto-launch    # Auto-launch Tidal"
echo "  ./run.sh --debug          # Debug mode"
echo "  ./run.sh --test           # Test mode"
echo ""
echo "Or activate the virtual environment and run directly:"
echo "  source venv/bin/activate"
echo "  python src/main.py"
echo ""
echo "Press Ctrl+C to stop the plugin when running"