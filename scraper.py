import os
import requests
from bs4 import BeautifulSoup

API_TOKEN = os.environ.get("BRIGHT_API_KEY")
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")
TARGET_URL = os.environ.get("TARGET_URL")

if not all([API_TOKEN, UNLOCKER_ZONE, TARGET_URL]):
    raise ValueError("BRIGHT_API_KEY, BRIGHT_ZONE et TARGET_URL doivent être définies !")

def get_vinted_items():
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
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Bright Data :", e.response.status_code)
        print("BODY:", e.response.text[:500])
        return []

    soup = BeautifulSoup(resp.text, "html.parser")

    items = []

    for item_div in soup.select(".feed-grid__item"):
        try:
            title = item_div.select_one(".feed-grid__item-title")
            price = item_div.select_one(".feed-grid__item-price")
            size = item_div.select_one(".feed-grid__item-size")
            etat = item_div.select_one(".feed-grid__item-condition")
            link = item_div.select_one("a[href]")
            img = item_div.select_one("img")

            item_url = f"https://www.vinted.fr{link['href']}" if link else None
            item_id = link["href"] if link else None

            if not item_id:
                continue

            items.append({
                "id": item_id,
                "title": title.get_text(strip=True) if title else "N/A",
                "price": price.get_text(strip=True) if price else "N/A",
                "size": size.get_text(strip=True) if size else "N/A",
                "etat": etat.get_text(strip=True) if etat else "N/A",
                "url": item_url,
                "photo_url": img["src"] if img else None,
                "user": "N/A"
            })

        except Exception as e:
            print("⚠️ Erreur parse item :", e)
            continue

    print(f"✅ Items trouvés: {len(items)}")
    return items
