import requests

async def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items"
    params = {
        "search_text": "nike",
        "order": "newest_first",
        "per_page": 20
    }

    items_list = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, params=params, headers=headers, timeout=15)
        data = response.json()

        for item in data.get("items", []):
            items_list.append({
                "id": str(item["id"]),
                "title": item["title"],
                "price": item["price"]["amount"],
                "url": item["url"],
                "photo": {
                    "url": item["photo"]["url"] if item.get("photo") else ""
                },
                "user": {
                    "login": item["user"]["login"]
                },
                "created_at": item["created_at"],
                "size_title": item.get("size_title", "N/A")
            })

    except Exception as e:
        print("❌ Erreur API Vinted:", e)

    return items_list
