# scraper.py
import os
import requests
from bs4 import BeautifulSoup

API_TOKEN = os.environ["BRIGHT_API_KEY"]
UNLOCKER_ZONE = os.environ["BRIGHT_ZONE"]
TARGET_URL = os.environ["TARGET_URL"]

async def get_vinted_items():
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "zone": UNLOCKER_ZONE,
        "url": TARGET_URL,
        "format": "raw"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        print("STATUS:", response.status_code)
        print("BODY:", response.text[:500])
        response.raise_for_status()
    except Exception as e:
        print("❌ Bright Data Error:", e)
        return []

    data = response.json()
    html = data.get("body", "")

    if not html:
        print("❌ HTML vide")
        return []

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.new-item-box__overlay--clickable")

    items = []

    for card in cards:
        link = card.get("href", "")
        if link.startswith("/"):
            link = "https://www.vinted.fr" + link

        title = card.get("title", "N/A")

        img_tag = card.find("img")
        img_url = img_tag.get("src") if img_tag else ""

        item_id = link.split("/items/")[-1].split("-")[0]

        items.append({
            "id": item_id,
            "title": title,
            "price": "N/A",
            "url": link,
            "photo": {"url": img_url},
            "size_title": "N/A",
            "user": {"login": "N/A"},
            "created_at": "N/A"
        })

    print("✅ Items trouvés:", len(items))
    return items
