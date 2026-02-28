import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

async def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items"

    params = {
        "search_text": "nike",
        "order": "newest_first",
        "per_page": 20
    }

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            timeout=15,
            verify=False
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ Mauvais status code")
            return []

        data = response.json()

        items_list = []

        for item in data.get("items", []):
            items_list.append({
                "id": item["id"],
                "title": item["title"],
                "price": item["price"]["amount"] + " €",
                "url": item["url"],
                "photo": {"url": item["photo"]["url"] if item.get("photo") else ""},
                "user": {"login": item["user"]["login"]},
                "created_at": item["created_at_ts"],
                "size_title": item.get("size_title", "N/A")
            })

        return items_list

    except Exception as e:
        print("❌ Erreur API Vinted:", e)
        return []
