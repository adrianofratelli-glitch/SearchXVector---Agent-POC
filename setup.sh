#!/bin/bash
# setup.sh — Bootstrap para nova EC2 (Amazon Linux 2023)
# Uso: bash setup.sh

set -e

echo "===== 1. Python + pip ====="
sudo dnf install -y python3 python3-pip

echo "===== 2. PATH ====="
echo 'export PATH=$PATH:/home/ssm-user/.local/bin' >> ~/.bashrc
source ~/.bashrc

echo "===== 3. Dependências Python ====="
pip3 install -r requirements.txt

echo "===== 4. Env ====="
cp .env.example .env
echo ""
echo "IMPORTANTE: edite o .env com suas credenciais antes de iniciar!"
echo "  nano .env"
echo ""
echo "===== Setup concluído! ====="
echo "Para iniciar: bash start.sh"
