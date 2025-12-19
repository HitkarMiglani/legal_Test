#!/bin/bash
# Run both Flask backend and Streamlit frontend

set -e

PROJECT_ROOT="$(dirname "$0")"
cd "$PROJECT_ROOT"

echo "🚀 Starting LuminaryAI..."

# Activate virtual environment if not already activated
env_path="venv/bin/activate"
if [ ! -f "$env_path" ]; then
    echo "❌ venv not found. Run ./setup.sh first!"
    exit 1
fi
source "$env_path"

PY_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')
export PYTHONWARNINGS="ignore"

# Use reloader only if not Python 3.13+
USE_RELOADER=""
if [ "$PY_MAJOR" -eq "3" ] && [ "$PY_MINOR" -ge "13" ]; then
    USE_RELOADER="--no-reload"
    echo "⛔ Python 3.13+ detected: Flask auto-reloader will be disabled. To use hot reload, downgrade python."
fi

# Start Flask backend in background
echo "\n🔧 Starting Flask backend..."
if [ "$USE_RELOADER" = "--no-reload" ]; then
    python app.py
else
    python app.py &
    BACKEND_PID=$!

    sleep 2
    echo "🎨 Starting Streamlit frontend..."
    streamlit run main.py &
    FRONTEND_PID=$!

    echo "\n✅ LuminaryAI is running!"
    echo "   Backend: http://localhost:5000"
    echo "   Frontend: http://localhost:8501"
    echo "\nPress Ctrl+C to stop both servers"

    trap "kill $BACKEND_PID $FRONTEND_PID; echo ''; echo '🛑 Servers stopped'; exit" INT
    wait
fi
