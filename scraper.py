from playwright.sync_api import sync_playwright
import json
import re

def get_vinted_items():
    items = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.goto("https://www.vinted.fr/catalog?search_text=nike")
        page.wait_for_timeout(5000)

        content = page.content()

        match = re.search(r'window.__INITIAL_STATE__ = ({.*});', content)

        if match:
            data = json.loads(match.group(1))
            try:
                items = data["catalog"]["items"]
            except:
                items = []

        browser.close()

    return items
