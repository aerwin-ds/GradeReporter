#!/bin/bash
# Quick setup script for GradeReporter

set -e

echo "🚀 Setting up GradeReporter..."

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the GradeReporter root directory"
    exit 1
fi

# Create virtual environment
echo "📦 Creating virtual environment..."
python -m venv .venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
if [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
    source .venv/Scripts/activate
else
    source .venv/bin/activate
fi

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Copy .env.example to .env if .env doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️  Creating .env file..."
    cp .env.example .env
    echo "✏️  Please edit .env with your configuration"
fi

# Create data directory
echo "📁 Creating data directory..."
mkdir -p data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env file with your configuration"
echo "2. Copy your databases to the data/ directory:"
echo "   cp /path/to/school_system.db data/"
echo "   cp /path/to/after_hours.db data/"
echo "3. Run the application:"
echo "   streamlit run app.py"
echo ""
