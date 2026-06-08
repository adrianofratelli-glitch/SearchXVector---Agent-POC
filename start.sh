#!/bin/bash
# start.sh — Atalho da POC Marketplace (React + LeafyGreen + FastAPI)
# Uso: bash start.sh
#
# Portas configuráveis (troque ao clonar o template p/ outra POC):
#   BACKEND_PORT  (default 8200)
#   FRONTEND_PORT (default 5273)
# Ex.: BACKEND_PORT=8201 FRONTEND_PORT=5274 bash start.sh

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

BACKEND_PORT="${BACKEND_PORT:-8200}"
FRONTEND_PORT="${FRONTEND_PORT:-5273}"

echo "🍃 Iniciando POC Search × Vector (LeafyGreen)…"
echo "   backend :$BACKEND_PORT · frontend :$FRONTEND_PORT"

# ── 1. Libera as portas (mata só o que está nelas) ───────────────────
lsof -ti:"$BACKEND_PORT"  2>/dev/null | xargs kill -9 2>/dev/null || true
lsof -ti:"$FRONTEND_PORT" 2>/dev/null | xargs kill -9 2>/dev/null || true
sleep 1

# ── 2. Backend FastAPI ───────────────────────────────────────────────
echo "→ subindo backend (FastAPI :$BACKEND_PORT)…"
cd "$ROOT/backend"
if [ -d "$ROOT/.venv" ]; then source "$ROOT/.venv/bin/activate"; fi
# libera o frontend no CORS
export CORS_ORIGINS="http://localhost:$FRONTEND_PORT,http://127.0.0.1:$FRONTEND_PORT"
nohup uvicorn main:app --host 0.0.0.0 --port "$BACKEND_PORT" > /tmp/poc-backend.log 2>&1 &

# ── 3. Frontend Vite ─────────────────────────────────────────────────
echo "→ subindo frontend (Vite :$FRONTEND_PORT)…"
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
# aponta o frontend p/ o backend e fixa a porta do Vite
export VITE_API_URL="http://localhost:$BACKEND_PORT"
nohup npm run dev -- --host --port "$FRONTEND_PORT" --strictPort > /tmp/poc-frontend.log 2>&1 &

# ── 4. Aguarda e valida ──────────────────────────────────────────────
echo "→ aguardando backend ficar pronto (cold start do LangGraph)…"
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
[ "$OK_B" = "200" ] && echo "✅ Backend:  http://localhost:$BACKEND_PORT  (docs em /docs)" || echo "❌ Backend falhou — veja: cat /tmp/poc-backend.log"
[ "$OK_F" = "200" ] && echo "✅ Frontend: http://localhost:$FRONTEND_PORT" || echo "❌ Frontend falhou — veja: cat /tmp/poc-frontend.log"
echo ""
echo "👉 Abra:  http://localhost:$FRONTEND_PORT"
echo "   Parar tudo:  lsof -ti:$BACKEND_PORT,$FRONTEND_PORT | xargs kill"
