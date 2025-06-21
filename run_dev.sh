#!/bin/bash

# Script to run the development servers for both frontend and backend

echo "Starting OsaCurator development environment..."

# Function to clean up background processes
cleanup() {
    echo "Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID
    echo "Servers shut down."
    exit
}

# Trap SIGINT (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Start the backend server
echo "Starting backend server..."
cd backend
source venv/bin/activate
uvicorn main:app --reload &
BACKEND_PID=$!
cd ..

# Start the frontend server
echo "Starting frontend server..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "----------------------------------------"
echo "OsaCurator is running!"
echo "Backend available at http://localhost:8000"
echo "Frontend available at http://localhost:5173"
echo "Press Ctrl+C to shut down all servers."
echo "----------------------------------------"

# Wait for background processes to finish
wait
