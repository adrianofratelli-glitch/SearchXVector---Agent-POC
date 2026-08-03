#!/bin/bash
# start.sh — Launcher for the Marketplace POC (React + LeafyGreen + FastAPI)
# Usage: bash start.sh
#
# Configurable ports (override when reusing this template for another POC):
#   BACKEND_PORT  (default 8200)
#   FRONTEND_PORT (default 5273)
# Example: BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

BACKEND_PORT="${BACKEND_PORT:-8200}"
FRONTEND_PORT="${FRONTEND_PORT:-5273}"

echo "🍃 Starting the Search & Vector POC (LeafyGreen)…"
echo "   backend :$BACKEND_PORT · frontend :$FRONTEND_PORT"

# ── 1. Free the ports (kill only what is bound to them) ──────────────
lsof -ti:"$BACKEND_PORT"  2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:"$FRONTEND_PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# ── 2. FastAPI backend ───────────────────────────────────────────────
echo "→ starting backend (FastAPI :$BACKEND_PORT)…"
cd "$ROOT/backend"
if [ -d "$ROOT/.venv" ]; then source "$ROOT/.venv/bin/activate"; fi
UVICORN_BIN="$ROOT/.venv/bin/uvicorn"
[ -x "$UVICORN_BIN" ] || UVICORN_BIN="uvicorn"
# allow the frontend origin in CORS
export CORS_ORIGINS="http://localhost:$FRONTEND_PORT,http://127.0.0.1:$FRONTEND_PORT"
nohup "$UVICORN_BIN" main:app --host 0.0.0.0 --port "$BACKEND_PORT" > /tmp/poc-backend.log 2>&1 &

# ── 3. Vite frontend ─────────────────────────────────────────────────
echo "→ starting frontend (Vite :$FRONTEND_PORT)…"
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
# point the frontend at the backend and pin the Vite port
export VITE_API_URL="http://localhost:$BACKEND_PORT"
nohup npm run dev -- --host --port "$FRONTEND_PORT" --strictPort > /tmp/poc-frontend.log 2>&1 &

# ── 4. Wait and verify ───────────────────────────────────────────────
echo "→ waiting for the backend to become ready (LangGraph cold start)…"
OK_B="000"
for i in $(seq 1 20); do
  OK_B=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$BACKEND_PORT/health" 2>/dev/null || echo "000")
  [ "$OK_B" = "200" ] && break
  sleep 1
done
OK_F="000"
for i in $(seq 1 10); do
  OK_F=$(curl -s -o /dev/null -w "%{http_code}" "http://localhost:$FRONTEND_PORT" 2>/dev/null || echo "000")
  [ "$OK_F" = "200" ] && break
  sleep 1
done

echo ""
[ "$OK_B" = "200" ] && echo "✅ Backend:  http://localhost:$BACKEND_PORT  (docs at /docs)" || echo "❌ Backend failed — check: cat /tmp/poc-backend.log"
[ "$OK_F" = "200" ] && echo "✅ Frontend: http://localhost:$FRONTEND_PORT" || echo "❌ Frontend failed — check: cat /tmp/poc-frontend.log"
echo ""
echo "👉 Open:  http://localhost:$FRONTEND_PORT"
echo "   Stop everything:  lsof -ti:$BACKEND_PORT,$FRONTEND_PORT | xargs kill"
