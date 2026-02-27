#!/bin/bash
# ==============================
# Start script pour Railway
# ==============================

# Activer l'arrêt en cas d'erreur
set -e

echo "📦 Installation des dépendances..."
pip install -r requirements.txt

echo "🌐 Installation de Chromium pour Playwright..."
python -m playwright install chromium

echo "🚀 Démarrage du bot..."
python bot.py
