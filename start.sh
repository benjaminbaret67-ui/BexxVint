#!/bin/bash
# ==============================
# Script de démarrage pour Railway
# Installe Playwright et ses navigateurs
# ==============================

# Installer Playwright Chromium (obligatoire)
python -m playwright install chromium

# Lancer le bot
python bot.py
