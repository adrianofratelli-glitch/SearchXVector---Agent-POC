#!/bin/bash
# start.sh — Inicia a POC Marketplace

export PATH=$PATH:/home/ssm-user/.local/bin

pkill -f streamlit 2>/dev/null || true
sleep 1

cd "$(dirname "$0")"

nohup streamlit run app_marketplace.py \
  --server.port 8501 \
  --server.address 0.0.0.0 \
  > ~/streamlit.log 2>&1 &

sleep 3

if curl -s localhost:8501 | grep -q "DOCTYPE"; then
  PUBLIC_IP=$(curl -s ifconfig.me)
  echo "✅ POC rodando em: http://${PUBLIC_IP}:8501"
else
  echo "❌ Erro ao iniciar. Verifique: cat ~/streamlit.log"
fi
