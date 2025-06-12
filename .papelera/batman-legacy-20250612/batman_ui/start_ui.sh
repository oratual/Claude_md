#!/bin/bash

# Batman Enhanced UI Startup Script

echo "🦇 Starting Batman Enhanced UI..."

# Colors
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo -e "${RED}Error: app.py not found. Please run this script from the batman_ui directory.${NC}"
    exit 1
fi

# Check for Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is required but not installed.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install -q flask pyyaml

# Create necessary directories
mkdir -p static/css static/js static/img

# Check if Batman Enhanced is properly configured
BATMAN_CONFIG="$HOME/.batman/enhanced_config.yaml"
if [ ! -f "$BATMAN_CONFIG" ]; then
    echo -e "${YELLOW}⚠️  Batman Enhanced configuration not found.${NC}"
    echo -e "${YELLOW}   Run the wizard after starting the UI to configure.${NC}"
fi

# Start the Flask app
echo -e "${GREEN}✅ Batman Enhanced UI is starting...${NC}"
echo -e "${GREEN}   Access the interface at: ${YELLOW}http://localhost:5000${NC}"
echo -e "${GREEN}   Press Ctrl+C to stop the server${NC}"
echo ""

# ASCII art
cat << "EOF"
    |\                  /|
    | \                / |
    |  \      /\      /  |
    |   \    /  \    /   |
     \   \  /    \  /   /
      \   \/  /\  \/   /
       \     /  \     /
        \   / ** \   /
         \_/  **  \_/
              **
        BATMAN ENHANCED
       UI Server Running
EOF

echo ""

# Run the Flask app
export FLASK_APP=app.py
export FLASK_ENV=development
python3 -m flask run --host=0.0.0.0 --port=5000