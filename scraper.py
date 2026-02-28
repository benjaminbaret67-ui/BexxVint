# scraper.py
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import requests

# ==============================
# BRIGHTDATA ENV
# ==============================
BRIGHT_HOST = os.getenv("BRIGHT_HOST")
BRIGHT_PORT = os.getenv("BRIGHT_PORT")
BRIGHT_USER = os.getenv("BRIGHT_USER")
BRIGHT_PASS = os.getenv("BRIGHT_PASS")

proxies = {
    "http": f"http://{BRIGHT_USER}:{BRIGHT_PASS}@{BRIGHT_HOST}:{BRIGHT_PORT}",
    "https": f"http://{BRIGHT_USER}:{BRIGHT_PASS}@{BRIGHT_HOST}:{BRIGHT_PORT}"
}

# ==============================
# MAIN FUNCTION
# ==============================
async def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items"

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "Referer": "https://www.vinted.fr/"
    }

    params = {
        "search_text": "nike",
        "order": "newest_first",
        "per_page": 50,
        "page": 1
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            proxies=proxies,
            timeout=25,
            verify=False
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ Mauvais status code")
            return []

        data = response.json()

        if "items" not in data:
            print("❌ Structure JSON inattendue")
            return []

        items_list = []

        for item in data["items"]:
            try:
                item_id = str(item["id"])
                title = item.get("title", "N/A")
                price = f'{item.get("price", "N/A")}€'
                url_item = item.get("url", f"https://www.vinted.fr/items/{item_id}")

                # IMAGE HD
                photo_url = ""
                if item.get("photo"):
                    photo_url = item["photo"].get("url", "")

                # VENDEUR
                seller = "N/A"
                if item.get("user"):
                    seller = item["user"].get("login", "N/A")

                # DATE
                created_at = item.get("created_at_ts", "N/A")

                # TAILLE
                size_title = item.get("size_title", "N/A")

                items_list.append({
                    "id": item_id,
                    "title": title,
                    "price": price,
                    "url": url_item,
                    "photo": {"url": photo_url},
                    "user": {"login": seller},
                    "created_at": str(created_at),
                    "size_title": size_title
                })

            except Exception:
                continue

        print("✅ Items trouvés:", len(items_list))
        return items_list

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)
        return []
