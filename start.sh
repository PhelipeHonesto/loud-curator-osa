#!/bin/bash

# start.sh - Start backend and frontend concurrently
# Usage: ./start.sh
# Requires Python dependencies installed in backend and npm dependencies in frontend

# Start backend
( cd backend && uvicorn main:app --reload ) &
BACKEND_PID=$!
echo "Backend started with PID $BACKEND_PID"

# Start frontend
( cd frontend && npm run dev ) &
FRONTEND_PID=$!
echo "Frontend started with PID $FRONTEND_PID"

# Wait for both processes
trap 'kill $BACKEND_PID $FRONTEND_PID' INT TERM
wait $BACKEND_PID $FRONTEND_PID

