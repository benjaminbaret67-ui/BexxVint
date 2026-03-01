import os
import requests

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
        "format": "json"
    }

    response = requests.post(url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    data = response.json()

    print("===== DEBUG JSON =====")
    print(type(data))
    print(data.keys() if isinstance(data, dict) else "Not dict")
    print(str(data)[:1000])
    print("======================")

    return []
