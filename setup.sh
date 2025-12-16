#!/bin/bash

set -e

echo "🎬 ScribeStack Setup"
echo "===================="
echo ""

# Check Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8 or later."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
if [ -d ".venv" ]; then
    echo "   Virtual environment already exists. Skipping..."
else
    python3 -m venv .venv
    echo "✅ Virtual environment created"
fi

echo ""
echo "🔌 Activating virtual environment..."
source .venv/bin/activate
echo "✅ Virtual environment activated"

echo ""
echo "📚 Installing dependencies..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt > /dev/null 2>&1
echo "✅ Dependencies installed"

echo ""
echo "🔐 Setting up environment file..."
if [ -f ".env" ]; then
    echo "   .env already exists. Skipping..."
else
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✅ .env created from .env.example"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
        echo "   Run: nano .env (or your preferred editor)"
    else
        cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-openai-api-key-here
EOF
        echo "✅ .env created"
        echo ""
        echo "⚠️  IMPORTANT: Edit .env and add your OPENAI_API_KEY"
        echo "   Run: nano .env (or your preferred editor)"
    fi
fi

echo ""
echo "📁 Creating project directories..."
mkdir -p input output intermediate prompts
echo "✅ Directories ready"

echo ""
echo "=================================="
echo "✨ Setup complete!"
echo "=================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your OpenAI API key"
echo "2. Add chapter text files to input/<book-id>/"
echo "3. Run: make BOOK_ID=<book-id> BOOK_TITLE=\"<title>\" CH_NUM=01 chapter-all"
echo ""
echo "Example:"
echo "  make BOOK_ID=my-book BOOK_TITLE=\"My Textbook\" CH_NUM=01 chapter-all"
echo ""
