import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
import os
import requests
from bs4 import BeautifulSoup

async def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike&order=newest_first"

    proxy_user = os.getenv("BRIGHT_USER")
    proxy_pass = os.getenv("BRIGHT_PASS")
    proxy_host = os.getenv("BRIGHT_HOST")
    proxy_port = os.getenv("BRIGHT_PORT")

    proxy = f"http://{proxy_user}:{proxy_pass}@{proxy_host}:{proxy_port}"

    proxies = {
        "http": proxy,
        "https": proxy
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }

    try:
        response = requests.get(
        url,
        headers=headers,
        timeout=15,
        verify=False  # 👈 AJOUTE ÇA
        )

        print("STATUS CODE:", response.status_code)

        if response.status_code != 200:
            return []

        soup = BeautifulSoup(response.text, "html.parser")

        cards = soup.select("a.new-item-box__overlay--clickable")

        items_list = []

        for card in cards:
            link = card["href"]
            if link.startswith("/"):
                link = "https://www.vinted.fr" + link

            info = card.get("title", "")
            title = info.split(", état:")[0].strip()

            items_list.append({
                "id": link.split("/")[-1],
                "title": title,
                "price": "N/A",
                "url": link,
                "photo": {"url": ""},
                "user": {"login": "N/A"},
                "created_at": "N/A",
                "size_title": "N/A"
            })

        return items_list

    except Exception as e:
        print("❌ Erreur scraper Vinted:", e)
        return []
