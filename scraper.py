# scraper.py
import os
import requests
from bs4 import BeautifulSoup

# ==============================
# Variables d'environnement (Railway ou local)
# ==============================
API_TOKEN = os.environ.get("BRIGHT_API_KEY")
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")
TARGET_URL = os.environ.get("TARGET_URL")

if not all([API_TOKEN, UNLOCKER_ZONE, TARGET_URL]):
    raise ValueError("BRIGHT_API_KEY, BRIGHT_ZONE et TARGET_URL doivent être définies !")

# ==============================
# Fonction principale
# ==============================
def get_vinted_items():
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
        "x-unblock-expect": '{"element": ".feed-grid__item"}'
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
        print("BODY:", e.response.text[:1000])
        return []

    html = resp.text
    soup = BeautifulSoup(html, "html.parser")

    items_list = []

    # Récupère tous les items visibles
    for item_div in soup.select(".feed-grid__item"):
        try:
            title = item_div.select_one(".feed-grid__item-title")
            title_text = title.get_text(strip=True) if title else "N/A"

            price = item_div.select_one(".feed-grid__item-price")
            price_text = price.get_text(strip=True) if price else "N/A"

            etat = item_div.select_one(".feed-grid__item-condition")
            etat_text = etat.get_text(strip=True) if etat else "N/A"

            size = item_div.select_one(".feed-grid__item-size")
            size_text = size.get_text(strip=True) if size else "N/A"

            url_tag = item_div.select_one("a[href]")
            item_url = f"https://www.vinted.fr{url_tag['href']}" if url_tag else "N/A"

            photo_tag = item_div.select_one("img")
            photo_url = photo_tag["src"] if photo_tag else ""

            user_tag = item_div.select_one(".feed-grid__item-user")
            user_text = user_tag.get_text(strip=True) if user_tag else "N/A"

            created_tag = item_div.select_one(".feed-grid__item-date")
            created_text = created_tag.get_text(strip=True) if created_tag else "N/A"

            item_id = item_div.get("data-id", item_url)

            items_list.append({
                "id": item_id,
                "title": title_text,
                "price": price_text,
                "size_title": size_text,
                "etat": etat_text,
                "url": item_url,
                "photo": {"url": photo_url},
                "user": {"login": user_text},
                "created_at": created_text
            })
        except Exception as e:
            print("⚠️ Erreur parse item :", e)
            continue

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list

# ==============================
# Test rapide
# ==============================
if __name__ == "__main__":
    items = get_vinted_items()
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. {item['title']} - {item['price']} - {item['etat']} - {item['size_title']}")
