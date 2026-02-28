import requests
import os

BRIGHT_HOST = os.getenv("BRIGHT_HOST")
BRIGHT_PORT = os.getenv("BRIGHT_PORT")
BRIGHT_USER = os.getenv("BRIGHT_USER")
BRIGHT_PASS = os.getenv("BRIGHT_PASS")

async def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items"

    params = {
        "search_text": "nike",
        "order": "newest_first",
        "per_page": 20
    }

    proxy_url = f"http://{BRIGHT_USER}:{BRIGHT_PASS}@{BRIGHT_HOST}:{BRIGHT_PORT}"

    proxies = {
        "http": proxy_url,
        "https": proxy_url
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
            proxies=proxies,
            timeout=30
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print(response.text[:200])
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
        print("❌ BrightData error:", e)
        return []
