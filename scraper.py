# scraper.py
import requests
from bs4 import BeautifulSoup
import json
import asyncio

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/116.0.0.0 Safari/537.36"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Chaque item est dans div.feed-grid__item
        cards = soup.select("div.feed-grid__item")
        for card in cards:
            try:
                title_el = card.select_one("h3")
                price_el = card.select_one(".feed-grid__item-price")
                link_el = card.select_one("a")
                img_el = card.select_one("img")

                title = title_el.get_text(strip=True) if title_el else "N/A"
                price = price_el.get_text(strip=True) if price_el else "N/A"
                link = link_el["href"] if link_el else "#"
                if link.startswith("/"):
                    link = "https://www.vinted.fr" + link
                img = img_el["src"] if img_el else ""

                items_list.append({
                    "id": link.split("/")[-1],
                    "title": title,
                    "price": price,
                    "url": link,
                    "photo": {"url": img},
                    "user": {"login": "N/A"},
                    "created_at": "N/A",
                    "size_title": "N/A"
                })
            except Exception:
                continue

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)

    return items_list
