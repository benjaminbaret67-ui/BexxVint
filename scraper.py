# scraper.py
import requests
from bs4 import BeautifulSoup
import json

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("div.feed-grid__item")  # cartes des items

            # récupérer toutes les cartes
            items = await page.query_selector_all("div.feed-grid__item")
            for it in items:
                title = await it.query_selector_eval("h3", "el => el.innerText")
                price = await it.query_selector_eval(".feed-grid__item-price", "el => el.innerText")
                link = await it.query_selector_eval("a", "el => el.href")
                img = await it.query_selector_eval("img", "el => el.src")
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

            await browser.close()
    except Exception as e:
        print("❌ Erreur Playwright scraper:", e)

    return items_list
