# scraper.py
import requests
from bs4 import BeautifulSoup
import json

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Sélecteur pour chaque item
        cards = soup.select("a.new-item-box__overlay--clickable")
        for card in cards:
            try:
                link = card["href"]
                if link.startswith("/"):
                    link = "https://www.vinted.fr" + link
                # Tout est dans l'attribut title
                info = card.get("title", "")
                # Exemple de parsing simple
                # "Chaussures homme, état: Neuf sans étiquette, taille: 43, 6,00 €, 7,00 € Protection acheteurs incluse"
                title = info.split(", état:")[0].strip()
                price = info.split(",")[-2].strip() if "," in info else "N/A"

                items_list.append({
                    "id": link.split("/")[-1],
                    "title": title,
                    "price": price,
                    "url": link,
                    "photo": {"url": ""},  # On peut ajouter l'image si besoin
                    "user": {"login": "N/A"},
                    "created_at": "N/A",
                    "size_title": "N/A"
                })
            except Exception:
                continue

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)

    return items_list
