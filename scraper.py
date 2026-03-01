import os
import requests
import re
import json

API_TOKEN = os.environ.get("BRIGHT_API_KEY")
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")
TARGET_URL = os.environ.get("TARGET_URL")

if not all([API_TOKEN, UNLOCKER_ZONE, TARGET_URL]):
    raise ValueError("BRIGHT_API_KEY, BRIGHT_ZONE et TARGET_URL doivent être définies !")


def get_vinted_items():
    bright_url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "zone": UNLOCKER_ZONE,
        "url": TARGET_URL,
        "format": "raw"
    }

    response = requests.post(bright_url, headers=headers, json=payload, timeout=60)
    response.raise_for_status()

    html = response.text

    # 🔥 On récupère le JSON __NEXT_DATA__
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)

    if not match:
        print("❌ __NEXT_DATA__ non trouvé")
        return []

    data = json.loads(match.group(1))

    items = []

    try:
        catalog_items = data["props"]["pageProps"]["catalogItems"]

        for item in catalog_items:
            items.append({
                "id": item["id"],
                "title": item["title"],
                "price": f"{item['price']['amount']} {item['price']['currency_code']}",
                "size_title": item.get("size_title", "N/A"),
                "etat": item.get("status", "N/A"),
                "url": f"https://www.vinted.fr/items/{item['id']}",
                "photo": {"url": item["photo"]["url"] if item.get("photo") else ""},
                "user": {"login": item["user"]["login"] if item.get("user") else "N/A"},
                "created_at": item.get("created_at_ts", "N/A")
            })

    except Exception as e:
        print("❌ Erreur parsing JSON:", e)
        return []

    print(f"✅ Items trouvés: {len(items)}")
    return items
