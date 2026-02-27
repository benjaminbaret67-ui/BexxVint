# scraper.py
from playwright.async_api import async_playwright
import asyncio
import json

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"
    items_list = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox"]
            )
            page = await browser.new_page()

            # Définit un User-Agent pour éviter le blocage par Vinted
            await page.set_user_agent(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/114.0.0.0 Safari/537.36"
            )

            await page.goto(url, timeout=60000)
            await page.wait_for_load_state("networkidle")
            await page.wait_for_timeout(3000)  # laisse le JS charger

            # Sélectionne toutes les cartes d'items
            items = await page.query_selector_all("div.feed-grid__item")
            for it in items:
                try:
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
                        "user": {"login": "N/A"},  # On peut récupérer si nécessaire
                        "created_at": "N/A",
                        "size_title": "N/A"
                    })
                except Exception as e:
                    print("⚠️ Erreur item:", e)
                    continue

            await browser.close()

    except Exception as e:
        print("❌ Erreur Playwright scraper:", e)

    print(f"✅ {len(items_list)} items récupérés")
    return items_list

# Test rapide si exécuté directement
if __name__ == "__main__":
    items = asyncio.run(get_vinted_items())
    print(json.dumps(items, indent=2, ensure_ascii=False))
