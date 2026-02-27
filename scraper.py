# scraper.py
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup  # Pour parser le HTML si besoin
import asyncio
import json

# ==============================
# ASYNC GET VINTED ITEMS
# ==============================

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            # Aller sur la page Vinted
            await page.goto(url, timeout=60000)
            await page.wait_for_timeout(3000)  # petit délai pour que JS charge

            # Récupérer le contenu
            content = await page.content()

            # Parser le HTML si nécessaire
            soup = BeautifulSoup(content, "html.parser")

            # Vinted charge ses items dans un <script type="application/json">
            scripts = soup.find_all("script", type="application/json")
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    # Vérifie si 'items' est présent dans le JSON
                    if "items" in data:
                        for item in data["items"]:
                            # On récupère juste ce qu'il nous faut
                            items_list.append({
                                "id": item.get("id"),
                                "title": item.get("title"),
                                "price": item.get("price") or "N/A",
                                "url": item.get("url"),
                                "photo": {"url": item.get("photo", {}).get("url", "")},
                                "user": {"login": item.get("user", {}).get("login", "N/A")},
                                "created_at": item.get("created_at", "N/A"),
                                "size_title": item.get("size_title", "N/A")
                            })
                except Exception:
                    continue

            await browser.close()

    except Exception as e:
        print("❌ Erreur Playwright scraper:", e)

    return items_list
