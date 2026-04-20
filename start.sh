#!/bin/bash

# Start backend
cd "$(dirname "$0")/backend"
/Users/nate/.venv/bin/uvicorn main:app --reload &
BACKEND_PID=$!

# Start frontend
cd "$(dirname "$0")/frontend"
npm run dev &
FRONTEND_PID=$!

echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo ""
echo "OceanDex running at http://localhost:5173"
echo "Press Ctrl+C to stop both servers."

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT
wait
