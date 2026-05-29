#!/bin/bash

echo "=================================="
echo "  CardioRisk Predictor - Startup  "
echo "=================================="

# Start backend
echo "[1/2] Starting backend on http://127.0.0.1:8000..."
cd "$(dirname "$0")/backend"
source ../venv/bin/activate 2>/dev/null || true
pip install -q -r requirements.txt 2>/dev/null
uvicorn app:app --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Start frontend
echo "[2/2] Opening frontend..."
cd "$(dirname "$0")/frontend"
python3 -m http.server 3000 &
FRONTEND_PID=$!

sleep 2
echo ""
echo "  Frontend: http://127.0.0.1:3000"
echo "  Backend:  http://127.0.0.1:8000"
echo "  API Docs: http://127.0.0.1:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
