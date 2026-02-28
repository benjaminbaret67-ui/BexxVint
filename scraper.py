# scraper.py
import os
import requests
from bs4 import BeautifulSoup

# ==============================
# BRIGHTDATA ENV VARIABLES
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
    items_list = []

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            proxies=proxies,
            timeout=25,
            verify=False
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            print("❌ Mauvais status code")
            return []

        soup = BeautifulSoup(response.text, "html.parser")

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

                # =========================
                # Titre
                # =========================
                title = info.split(", état:")[0].strip()

                # =========================
                # Taille
                # =========================
                size_title = "N/A"
                if "taille:" in info:
                    try:
                        size_title = info.split("taille:")[1].split(",")[0].strip()
                    except:
                        pass

                # =========================
                # Prix
                # =========================
                price = "N/A"
                parts = [p for p in info.split(",") if "€" in p]
                if parts:
                    price = parts[-1].split("€")[0].strip() + "€"

                # =========================
                # Image
                # =========================
                img_tag = card.find("img")
                img_url = img_tag["src"] if img_tag and img_tag.get("src") else ""

                # =========================
                # Item ID
                # =========================
                item_id = link.split("/items/")[-1].split("-")[0]

                items_list.append({
                    "id": item_id,
                    "title": title,
                    "price": price,
                    "url": link,
                    "photo": {"url": img_url},
                    "user": {"login": "N/A"},   # On ne scrape plus le vendeur (trop lourd)
                    "created_at": "N/A",
                    "size_title": size_title
                })

            except Exception:
                continue

        print("✅ Items trouvés:", len(items_list))
        return items_list

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)
        return []
