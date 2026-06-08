#!/bin/bash
# start.sh — Atalho da POC Marketplace (React + LeafyGreen + FastAPI)
# Uso: bash start.sh   (ou ./start.sh)

set -e
cd "$(dirname "$0")"
ROOT="$(pwd)"

echo "🍃 Iniciando POC Search × Vector (LeafyGreen)…"

# ── 1. Mata instâncias antigas ───────────────────────────────────────
pkill -f "uvicorn main:app" 2>/dev/null || true
pkill -f "vite" 2>/dev/null || true
sleep 1

# ── 2. Backend FastAPI (:8000) ───────────────────────────────────────
echo "→ subindo backend (FastAPI :8000)…"
cd "$ROOT/backend"
# usa o venv da raiz se existir
if [ -d "$ROOT/.venv" ]; then source "$ROOT/.venv/bin/activate"; fi
nohup uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/poc-backend.log 2>&1 &

# ── 3. Frontend Vite (:5173) ─────────────────────────────────────────
echo "→ subindo frontend (Vite :5173)…"
cd "$ROOT/frontend"
[ -d node_modules ] || npm install
nohup npm run dev -- --host > /tmp/poc-frontend.log 2>&1 &

# ── 4. Aguarda e valida ──────────────────────────────────────────────
sleep 6
OK_B=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health || echo "000")
OK_F=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173 || echo "000")

echo ""
[ "$OK_B" = "200" ] && echo "✅ Backend:  http://localhost:8000  (docs em /docs)" || echo "❌ Backend falhou — veja: cat /tmp/poc-backend.log"
[ "$OK_F" = "200" ] && echo "✅ Frontend: http://localhost:5173" || echo "❌ Frontend falhou — veja: cat /tmp/poc-frontend.log"
echo ""
echo "👉 Abra:  http://localhost:5173"
echo "   Parar tudo:  pkill -f 'uvicorn main:app'; pkill -f vite"
