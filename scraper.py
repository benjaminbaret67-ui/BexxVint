import os
import requests
import json
import re

API_TOKEN = os.environ.get("BRIGHT_API_KEY")
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")
TARGET_URL = os.environ.get("TARGET_URL")

if not all([API_TOKEN, UNLOCKER_ZONE, TARGET_URL]):
    raise ValueError("BRIGHT_API_KEY, BRIGHT_ZONE et TARGET_URL doivent être définies !")


def get_vinted_items():
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "zone": UNLOCKER_ZONE,
        "url": TARGET_URL,
        "format": "raw"
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)

    print("STATUS:", response.status_code)

    data = response.json()

    print("KEYS:", data.keys())

    if "body" in data:
        print("BODY PREVIEW:")
        print(data["body"][:1000])  # affiche les 1000 premiers caractères

    return []
