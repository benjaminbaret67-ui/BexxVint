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

    # Bright Data renvoie un JSON avec body dedans
    data = response.json()

    if "body" not in data:
        print("❌ Pas de body dans la réponse Bright Data")
        return []

    html = data["body"]

    # On récupère le JSON NextJS de Vinted
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)

    if not match:
        print("❌ __NEXT_DATA__ non trouvé")
        return []

    try:
        json_data = json.loads(match.group(1))
    except Exception as e:
        print("❌ Erreur parsing JSON:", e)
        return []

    try:
        items = json_data["props"]["pageProps"]["catalog"]["items"]
    except Exception as e:
        print("❌ Structure JSON inconnue:", e)
        return []

    items_list = []

    for item in items:
        try:
            items_list.append({
                "id": item.get("id"),
                "title": item.get("title", "N/A"),
                "price": f"{item.get('price', {}).get('amount', 'N/A')}€",
                "size_title": item.get("size_title", "N/A"),
                "etat": item.get("status", "N/A"),
                "url": f"https://www.vinted.fr/items/{item.get('id')}",
                "photo": {"url": item.get("photo", {}).get("url", "")},
                "user": {"login": item.get("user", {}).get("login", "N/A")},
                "created_at": item.get("created_at_ts", "N/A")
            })
        except Exception:
            continue

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list
