#!/bin/bash
# Start both frontend and backend for local development.
# Usage: ./scripts/dev.sh

set -e

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

cleanup() {
    echo ""
    echo "Shutting down..."
    kill 0
    exit 0
}
trap cleanup SIGINT SIGTERM

echo "Starting Stride dev servers..."
echo ""

# backend
echo "[backend] Starting FastAPI on :8000"
(cd "$ROOT/backend" && uvicorn app.main:app --reload --port 8000) &

# frontend
echo "[frontend] Starting Vite on :5173"
(cd "$ROOT/frontend" && npm run dev) &

echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both."

wait
