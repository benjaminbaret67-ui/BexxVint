# scraper.py
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import os
import requests
import json
import re

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
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "fr-FR,fr;q=0.9"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            timeout=25,
            verify=False
        )

        if response.status_code != 200:
            print("❌ Mauvais status:", response.status_code)
            return []

        html = response.text

        # ==============================
        # EXTRACTION JSON EMBARQUÉ
        # ==============================
        match = re.search(r"window\.__INITIAL_STATE__\s*=\s*(\{.*?\});", html)
        if not match:
            print("❌ JSON non trouvé")
            return []

        data = json.loads(match.group(1))

        items = data["catalog"]["items"]
        items_list = []

        for item in items:
            items_list.append({
                "id": str(item["id"]),
                "title": item["title"],
                "price": f'{item["price"]}€',
                "url": f'https://www.vinted.fr/items/{item["id"]}',
                "photo": {"url": item["photo"]["url"]},
                "user": {"login": item["user"]["login"]},
                "created_at": item["created_at"],
                "size_title": item.get("size_title", "N/A")
            })

        print("✅ Items trouvés:", len(items_list))
        return items_list

    except Exception as e:
        print("❌ Erreur scraper:", e)
        return []
