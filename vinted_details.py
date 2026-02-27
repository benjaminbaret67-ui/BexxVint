# vinted_details.py
from playwright.async_api import async_playwright
import asyncio

async def get_item_details(url):
    details = {"user": "N/A", "created_at": "N/A"}

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("div[data-testid='profile-link']", timeout=5000)

            # Récupère le vendeur
            seller_el = await page.query_selector("div[data-testid='profile-link']")
            if seller_el:
                details["user"] = await seller_el.inner_text()

            # Récupère la date d'ajout
            date_el = await page.query_selector("time")
            if date_el:
                details["created_at"] = await date_el.get_attribute("datetime")

            await browser.close()

    except Exception as e:
        print("❌ Erreur récupération détails :", e)

    return details

# Exemple d'utilisation
if __name__ == "__main__":
    url = "https://www.vinted.fr/items/8274194264-chaussures-homme"
    details = asyncio.run(get_item_details(url))
    print(details)
