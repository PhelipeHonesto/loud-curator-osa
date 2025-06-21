#!/usr/bin/env bash

# Start backend and frontend concurrently for development.

set -e

# Start backend server
pushd backend >/dev/null
if [ -f venv/bin/activate ]; then
    source venv/bin/activate
fi
uvicorn main:app --reload &
BACKEND_PID=$!
popd >/dev/null

# Start frontend server
pushd frontend >/dev/null
npm run dev &
FRONTEND_PID=$!
popd >/dev/null

trap "kill $BACKEND_PID $FRONTEND_PID" EXIT

echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:5173"
echo "Press Ctrl+C to stop both."

wait
