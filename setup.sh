#!/bin/bash
# Setup script for LuminaryAI
set -e

PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

# Check Python version
PY_VER=$(python -c 'import sys; print("%d.%d" % (sys.version_info.major, sys.version_info.minor))')
PY_MAJOR=$(echo $PY_VER | cut -d. -f1)
PY_MINOR=$(echo $PY_VER | cut -d. -f2)

if [ "$PY_MAJOR" != "3" ]; then
    echo "❌ Python 3.x is required."
    exit 1
fi

if [ "$PY_MINOR" -lt 9 ]; then
    echo "❌ Python 3.9 or newer is required."
    exit 1
fi

# Create venv if absent
if [ ! -d "venv" ]; then
    echo "🟠 Creating virtual environment... (venv)"
    python -m venv venv
fi
source venv/bin/activate

# Upgrade essential tools
pip install --upgrade pip setuptools wheel

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "🟢 Installing dependencies from requirements.txt ..."
    pip install -r requirements.txt || true
    echo "\n(Note: Some dependency conflicts are normal and described in requirements.txt comments.)\n"
else
    echo "❌ requirements.txt not found!"
    exit 1
fi

if [ "$PY_MINOR" -ge 13 ]; then
    echo "⚠️  WARNING: Python 3.13+ may break reloading and some dependencies! For a smoother experience, use Python 3.12."
fi

echo "✔️  Setup complete! To start the app: ./run.sh"
