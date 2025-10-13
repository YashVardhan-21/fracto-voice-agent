#!/bin/bash
# Development startup script

echo "🚀 Starting FRACTO development environment..."

# Start backend
echo "🐍 Starting backend services..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "⚛️  Starting frontend..."
cd ../frontend
npm start &
FRONTEND_PID=$!

echo "✅ Development servers started!"
echo "📱 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/api/docs"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID" INT
wait
