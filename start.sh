#!/bin/bash

# Start both backend and frontend services
echo "🚀 Starting Smart Document Assistant Services"

# Function to check if port is available
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null ; then
        echo "⚠️  Port $port is already in use"
        return 1
    fi
    return 0
}

# Check ports
if ! check_port 8000; then
    echo "❌ Backend port 8000 is busy. Please stop the existing service or use a different port."
    exit 1
fi

if ! check_port 8501; then
    echo "⚠️  Frontend port 8501 is busy. Streamlit will use a different port."
fi

# Start backend in background
echo "🔧 Starting Backend API..."
uvicorn backend.api:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Test backend health
echo "🧪 Testing backend health..."
curl -s http://localhost:8000/health > /dev/null
if [ $? -eq 0 ]; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend health check failed"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# Start frontend
echo "🎨 Starting Frontend..."
streamlit run frontend/app.py --server.port 8501 --server.address 0.0.0.0

# If we reach here, streamlit was stopped, so stop backend too
echo "🛑 Stopping services..."
kill $BACKEND_PID 2>/dev/null

