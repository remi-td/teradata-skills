#!/usr/bin/env bash
# Single-command dev launcher — starts backend (uvicorn) and frontend (vite) together.
# Usage: ./start.sh
# Stop: Ctrl-C (both processes are killed automatically via the trap below).
set -euo pipefail

REPO="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$REPO/backend"
FRONTEND="$REPO/frontend"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-5173}"

cleanup() {
  echo ""
  echo "Stopping..."
  kill "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# --- Backend ---
if [ ! -d "$BACKEND/.venv" ]; then
  echo "Creating Python venv..."
  python3 -m venv "$BACKEND/.venv"
fi
"$BACKEND/.venv/bin/pip" install -q -r "$BACKEND/requirements.txt"

# NOTE: use (cd "$BACKEND" && uvicorn ...) — not --app-dir.
# --app-dir sets sys.path but does NOT change CWD, so pydantic-settings
# cannot find the relative .env file.
(cd "$BACKEND" && ".venv/bin/uvicorn" app.main:app --port "$BACKEND_PORT" --reload) &
BACKEND_PID=$!
echo "Backend started (PID $BACKEND_PID) → http://localhost:$BACKEND_PORT"

# --- Frontend ---
if [ ! -d "$FRONTEND/node_modules" ]; then
  echo "Installing npm dependencies..."
  npm --prefix "$FRONTEND" install --silent
fi

npm --prefix "$FRONTEND" run dev &
FRONTEND_PID=$!
echo "Frontend started (PID $FRONTEND_PID) → http://localhost:$FRONTEND_PORT"

sleep 3 && open "http://localhost:$FRONTEND_PORT" 2>/dev/null || true &

wait
