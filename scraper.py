import os
import requests

TARGET_URL = os.environ.get("TARGET_URL")

if not TARGET_URL:
    raise ValueError("TARGET_URL doit être définie !")


def get_vinted_items():
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    # On transforme ton URL catalogue en appel API
    api_url = TARGET_URL.replace(
        "https://www.vinted.fr/catalog",
        "https://www.vinted.fr/api/v2/catalog/items"
    )

    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("❌ Erreur API Vinted :", e)
        return []

    items = []

    for item in data.get("items", []):
        items.append({
            "id": item["id"],
            "title": item["title"],
            "price": f"{item['price']} {item['currency']}",
            "size_title": item.get("size_title", "N/A"),
            "etat": item.get("status", "N/A"),
            "url": item["url"],
            "photo": {"url": item["photo"]["url"] if item.get("photo") else ""},
            "user": {"login": item["user"]["login"] if item.get("user") else "N/A"},
            "created_at": item.get("created_at", "N/A")
        })

    print(f"✅ Items trouvés: {len(items)}")
    return items
