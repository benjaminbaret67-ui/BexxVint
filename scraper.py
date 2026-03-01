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
        "format": "json"  # 🔥 IMPORTANT
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("❌ Erreur Bright Data :", e)
        return []

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
