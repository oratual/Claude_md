#!/bin/bash
# Batman Installation Script

echo "🦇 Installing Batman Task Automation System..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
required_version="3.8"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then 
    echo "❌ Error: Python $required_version or higher is required (found $python_version)"
    exit 1
fi

echo "✓ Python $python_version detected"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Create directories
echo "📁 Creating directories..."
mkdir -p logs tasks outputs

# Create symlink for global access (optional)
if [ -w "/usr/local/bin" ]; then
    echo "🔗 Creating symlink..."
    ln -sf "$(pwd)/batman.py" /usr/local/bin/batman
    echo "✓ Batman installed globally"
else
    echo "⚠️  Cannot create global symlink (no write access to /usr/local/bin)"
    echo "   You can run Batman with: $(pwd)/batman.py"
fi

echo ""
echo "✅ Installation complete!"
echo ""
echo "🦇 To get started:"
echo "   1. Activate the virtual environment: source venv/bin/activate"
echo "   2. Run Batman: ./batman.py --help"
echo ""
echo "📚 Example usage:"
echo "   ./batman.py list tasks/example-maintenance.txt"
echo "   ./batman.py run tasks/example-maintenance.txt"
echo "   ./batman.py exec 'echo Hello Batman!'"
echo ""