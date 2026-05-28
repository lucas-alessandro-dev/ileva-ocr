#!/usr/bin/env bash
# Instala dependências do sistema e Python para o serviço de OCR.
# Execute uma única vez no servidor: bash install.sh

set -e

echo "==> Instalando dependências do sistema (poppler-utils, tesseract)..."
sudo apt-get update -y
sudo apt-get install -y --no-install-recommends \
    poppler-utils \
    tesseract-ocr \
    tesseract-ocr-por \
    tesseract-ocr-eng \
    python3 \
    python3-pip \
    python3-venv

echo "==> Criando ambiente virtual Python..."
python3 -m venv venv

echo "==> Instalando dependências Python..."
./venv/bin/pip install --no-cache-dir -r requirements.txt

echo "==> Iniciando serviço com PM2..."
pm2 start pm2.config.js

echo "==> Salvando configuração PM2 (reinício automático)..."
pm2 save

echo ""
echo "Serviço OCR iniciado em http://localhost:5500"
echo "Verifique com: curl http://localhost:5500/health"
