#!/bin/bash
# setup.sh — Bootstrap completo para nova EC2 (Amazon Linux 2023)
# Uso: bash setup.sh
# Requer: IAM role com S3ReadOnly + SSMManagedInstanceCore

set -e

echo "===== 1. Python + pip ====="
sudo dnf install -y python3 python3-pip

echo "===== 2. Ollama ====="
curl -fsSL https://ollama.ai/install.sh | sh

echo "===== 3. Ollama performance config ====="
sudo mkdir -p /etc/systemd/system/ollama.service.d
sudo tee /etc/systemd/system/ollama.service.d/override.conf << 'EOF'
[Service]
Environment="OLLAMA_NUM_THREADS=8"
Environment="OLLAMA_FLASH_ATTENTION=1"
Environment="OLLAMA_NUM_PARALLEL=1"
EOF
sudo systemctl daemon-reload && sudo systemctl restart ollama

echo "===== 4. Modelo LLM ====="
ollama pull qwen2.5:3b

echo "===== 5. PATH ====="
echo 'export PATH=$PATH:/home/ssm-user/.local/bin' >> ~/.bashrc
source ~/.bashrc

echo "===== 6. Dependências Python ====="
pip3 install -r requirements.txt

echo "===== 7. App ====="
cp .env.example .env
echo ""
echo "IMPORTANTE: edite o arquivo .env com suas credenciais antes de iniciar!"
echo "  nano .env"
echo ""
echo "===== Setup concluído! ====="
echo "Para iniciar: bash start.sh"
