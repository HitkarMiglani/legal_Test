#!/bin/bash
# Run both Flask backend and Streamlit frontend

echo "🚀 Starting LuminaryAI..."

# Activate virtual environment if not already activated
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Activating virtual environment..."
    source venv/bin/activate
fi

# Start Flask backend in background
echo ""
echo "🔧 Starting Flask backend..."
python app.py &
BACKEND_PID=$!

sleep 2

# Start Streamlit frontend in background
echo "🎨 Starting Streamlit frontend..."
streamlit run main.py &
FRONTEND_PID=$!

echo ""
echo "✅ LuminaryAI is running!"
echo "   Backend: http://localhost:5000"
echo "   Frontend: http://localhost:8501"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; echo ''; echo '🛑 Servers stopped'; exit" INT
wait
