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

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Bright Data:", e)
        return []

    html = response.text

    # On récupère le JSON interne de Vinted
    match = re.search(r'<script id="__NEXT_DATA__".*?>(.*?)</script>', html)

    if not match:
        print("❌ __NEXT_DATA__ non trouvé")
        return []

    try:
        data = json.loads(match.group(1))
        items = data["props"]["pageProps"]["catalogItems"]["items"]
    except Exception as e:
        print("❌ Erreur parsing JSON:", e)
        return []

    items_list = []

    for item in items:
        items_list.append({
            "id": str(item.get("id")),
            "title": item.get("title", "N/A"),
            "price": str(item.get("price", {}).get("amount", "N/A")) + "€",
            "size_title": item.get("size_title", "N/A"),
            "etat": item.get("status", "N/A"),
            "url": f"https://www.vinted.fr/items/{item.get('id')}",
            "photo": {"url": item.get("photo", {}).get("url", "")},
            "user": {"login": item.get("user", {}).get("login", "N/A")},
            "created_at": item.get("created_at", "N/A")
        })

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list
