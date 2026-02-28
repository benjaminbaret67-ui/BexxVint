import requests
import asyncio

async def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items"
    
    params = {
        "search_text": "nike",
        "order": "newest_first",
        "per_page": 20
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json, text/plain, */*",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.vinted.fr/",
        "Origin": "https://www.vinted.fr"
    }

    items_list = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)

        # 🔎 Debug si Vinted bloque
        if "application/json" not in response.headers.get("Content-Type", ""):
            print("⚠️ Vinted bloque la requête (pas du JSON)")
            print(response.text[:300])
            return []

        data = response.json()

        for item in data.get("items", []):
            items_list.append({
                "id": str(item.get("id")),
                "title": item.get("title", "N/A"),
                "price": item.get("price", {}).get("amount", "N/A"),
                "url": item.get("url"),
                "photo": {"url": item.get("photo", {}).get("url", "")},
                "user": {"login": item.get("user", {}).get("login", "N/A")},
                "created_at": item.get("created_at_ts", "N/A"),
                "size_title": item.get("size_title", "N/A")
            })

    except Exception as e:
        print("❌ Erreur API Vinted:", e)

    return items_list
