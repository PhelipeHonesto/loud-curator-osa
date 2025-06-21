#!/usr/bin/env bash
# Simple helper script to run backend and frontend concurrently
# in development mode.

set -e

# Start backend
(
    cd backend
    if [ -f venv/bin/activate ]; then
        source venv/bin/activate
    fi
    uvicorn main:app --reload &
    BACKEND_PID=$!
)

# Start frontend
(
    cd frontend
    npm run dev &
    FRONTEND_PID=$!
)

# When this script is interrupted, stop both processes
trap 'kill $BACKEND_PID $FRONTEND_PID' INT

# Wait for both processes to finish
wait $BACKEND_PID $FRONTEND_PID
