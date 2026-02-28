# scraper.py
import os
import requests
from bs4 import BeautifulSoup

BRIGHT_API_KEY = os.environ["BRIGHT_API_KEY"]
BRIGHT_ZONE = os.environ["BRIGHT_ZONE"]
TARGET_URL = os.environ["TARGET_URL"]

def get_vinted_items():
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {BRIGHT_API_KEY}",
        "Content-Type": "application/json",
        # x-unblock-expect doit être ici directement
        "x-unblock-expect": '{"element": ".feed-grid__item"}'
    }

    payload = {
        "zone": BRIGHT_ZONE,
        "url": TARGET_URL,
        "format": "raw"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Bright Data :", e.response.status_code)
        print("BODY:", e.response.text[:500])
        return []

    data = response.json()
    html = data.get("body", "")
    if not html:
        print("❌ __NEXT_DATA__ ou body vide")
        return []

    # Parsing HTML
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.new-item-box__overlay--clickable")
    items_list = []

    for card in cards:
        try:
            link = card.get("href")
            if link and link.startswith("/"):
                link = "https://www.vinted.fr" + link

            info = card.get("title", "")
            if not info:
                continue

            title = info.split(", état:")[0].strip()
            size_title = "N/A"
            if "taille:" in info:
                try:
                    size_title = info.split("taille:")[1].split(",")[0].strip()
                except:
                    pass

            price = "N/A"
            parts = [p for p in info.split(",") if "€" in p]
            if parts:
                price = parts[-1].strip()

            img_tag = card.find("img")
            img_url = img_tag.get("src", "") if img_tag else ""

            item_id = link.split("/items/")[-1].split("-")[0]

            items_list.append({
                "id": item_id,
                "title": title,
                "price": price,
                "url": link,
                "photo": {"url": img_url},
                "user": {"login": "N/A"},
                "created_at": "N/A",
                "size_title": size_title
            })

        except Exception:
            continue

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list
