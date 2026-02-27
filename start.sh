#!/bin/bash
python -m playwright install chromium && pip install -r requirements.txt
python bot.py
