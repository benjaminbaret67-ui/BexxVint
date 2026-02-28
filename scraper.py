# scraper.py
import os
import requests
import json
from bs4 import BeautifulSoup

BRIGHT_API_KEY = os.getenv("BRIGHT_API_KEY")
BRIGHT_ZONE = os.getenv("BRIGHT_ZONE")
TARGET_URL = os.getenv("TARGET_URL")

async def get_vinted_items():
    try:
        response = requests.post(
            "https://api.brightdata.com/request",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {BRIGHT_API_KEY}"
            },
            json={
                "zone": BRIGHT_ZONE,
                "url": TARGET_URL,
                "format": "raw"
            },
            timeout=40
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ BrightData error:", response.text)
            return []

        html = response.text
        soup = BeautifulSoup(html, "html.parser")

        script_tag = soup.find("script", id="__NEXT_DATA__")
        if not script_tag:
            print("❌ __NEXT_DATA__ non trouvé")
            return []

        data = json.loads(script_tag.string)

        items = (
            data
            .get("props", {})
            .get("pageProps", {})
            .get("catalogItems", {})
            .get("items", [])
        )

        items_list = []

        for item in items:
            item_id = str(item["id"])

            items_list.append({
                "id": item_id,
                "title": item.get("title", "N/A"),
                "price": f'{item.get("price", "N/A")}€',
                "url": f"https://www.vinted.fr/items/{item_id}",
                "photo": {"url": item.get("photo", {}).get("url", "")},
                "user": {"login": item.get("user", {}).get("login", "N/A")},
                "created_at": item.get("createdAt", "N/A"),
                "size_title": item.get("size_title", "N/A")
            })

        print("✅ Items trouvés:", len(items_list))
        return items_list

    except Exception as e:
        print("❌ Erreur scraper:", e)
        return []
