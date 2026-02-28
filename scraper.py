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
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Referer": "https://www.vinted.fr/catalog?search_text=nike"
    }

    items_list = []

    try:
        response = requests.get(url, headers=headers, params=params, timeout=15)

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ Mauvais status code")
            return []

        data = response.json()

        if "items" not in data:
            print("❌ Pas de clé 'items' dans la réponse")
            print(data)
            return []

        for item in data["items"]:
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
