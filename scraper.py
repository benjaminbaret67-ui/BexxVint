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
        "format": "json"
    }

    try:
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Bright Data:", e)
        return []

    data = response.json()

    if "body" not in data:
        print("❌ Pas de body dans la réponse")
        return []

    html = data["body"]

    soup = BeautifulSoup(html, "html.parser")

    items_list = []

    cards = soup.select("a.new-item-box__overlay--clickable")

    for card in cards:
        try:
            link = card.get("href")
            if not link:
                continue

            if link.startswith("/"):
                link = "https://www.vinted.fr" + link

            info = card.get("title", "")
            if not info:
                continue

            title = info.split(", état:")[0].strip()

            size = "N/A"
            if "taille:" in info:
                try:
                    size = info.split("taille:")[1].split(",")[0].strip()
                except:
                    pass

            price = "N/A"
            parts = [p for p in info.split(",") if "€" in p]
            if parts:
                price = parts[-1].split("€")[0].strip() + "€"

            img_tag = card.find("img")
            img_url = img_tag["src"] if img_tag and img_tag.get("src") else ""

            item_id = link.split("/items/")[-1].split("-")[0]

            items_list.append({
                "id": item_id,
                "title": title,
                "price": price,
                "size_title": size,
                "etat": "N/A",
                "url": link,
                "photo": {"url": img_url},
                "user": {"login": "N/A"},
                "created_at": "N/A"
            })

        except Exception:
            continue

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list
