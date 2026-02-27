# scraper.py
import requests
from bs4 import BeautifulSoup
import json

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            print("❌ Erreur HTTP :", response.status_code)
            return items_list

        soup = BeautifulSoup(response.text, "html.parser")

        # Vinted charge ses items dans un <script type="application/json">
        scripts = soup.find_all("script", type="application/json")
        for script in scripts:
            try:
                data = json.loads(script.string)
                if "items" in data:
                    for item in data["items"]:
                        items_list.append({
                            "id": item.get("id"),
                            "title": item.get("title"),
                            "price": item.get("price") or "N/A",
                            "url": item.get("url"),
                            "photo": {"url": item.get("photo", {}).get("url", "")},
                            "user": {"login": item.get("user", {}).get("login", "N/A")},
                            "created_at": item.get("created_at", "N/A"),
                            "size_title": item.get("size_title", "N/A")
                        })
            except Exception:
                continue

    except Exception as e:
        print("❌ Erreur scraper :", e)

    return items_list
