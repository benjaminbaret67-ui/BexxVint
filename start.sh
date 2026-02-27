#!/bin/bash
# Installer les navigateurs Playwright à chaque lancement
python -m playwright install chromium

# Lancer le bot
python bot.py
