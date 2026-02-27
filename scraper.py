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

                # L'attribut title contient toutes les infos
                # Exemple : "Chaussures homme, état: Neuf sans étiquette, taille: 43, 6,00 €, 7,00 € Protection acheteurs incluse"
                info = card.get("title", "")

                # Titre
                title = info.split(", état:")[0].strip()

                # Taille (si "taille:" présent)
                size_title = "N/A"
                if "taille:" in info:
                    try:
                        size_title = info.split("taille:")[1].split(",")[0].strip()
                    except:
                        size_title = "N/A"

                # Prix (on prend le dernier montant avant "€ Protection")
                price = "N/A"
                parts = [p for p in info.split(",") if "€" in p]
                if parts:
                    price = parts[-1].split("€")[0].strip()

                items_list.append({
                    "id": link.split("/")[-1],
                    "title": title,
                    "price": price,
                    "url": link,
                    "photo": {"url": ""},  # Pour l'instant vide, on peut extraire l'image si nécessaire
                    "user": {"login": "N/A"},  # Impossible à obtenir sans JS
                    "created_at": "N/A",       # Impossible à obtenir sans JS
                    "size_title": size_title
                })
            except Exception:
                continue

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)

    return items_list
