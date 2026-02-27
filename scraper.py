from playwright.async_api import async_playwright

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        await page.goto(url, timeout=60000)
        await page.wait_for_timeout(5000)

        content = await page.content()

        await browser.close()

    # Ici tu devras parser le HTML
    # Pour l’instant on retourne vide pour test
    return []
