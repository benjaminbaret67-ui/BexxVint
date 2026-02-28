import os
import requests
from bs4 import BeautifulSoup
import json

API_TOKEN = os.environ["BRIGHT_API_KEY"]
UNLOCKER_PROXY_NAME = os.environ["BRIGHT_ZONE"]
TARGET_URL = "https://www.vinted.fr/catalog?search_text=nike"

def get_vinted_items():
    url = "https://api.brightdata.com/request"
    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "zone": UNLOCKER_PROXY_NAME,
        "url": TARGET_URL,
        "format": "raw",
        "extra": {
            "headers": {
                "x-unblock-expect": json.dumps({"element": ".feed-grid__item"})
            }
        }
    }

    resp = requests.post(url, headers=headers, json=payload, timeout=60)
    resp.raise_for_status()
    html = resp.json().get("body", "")

    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.new-item-box__overlay--clickable")
    items_list = []

    for card in cards:
        link = card.get("href")
        if link.startswith("/"):
            link = "https://www.vinted.fr" + link
        title = card.get("title", "N/A")
        img_tag = card.find("img")
        img_url = img_tag.get("src") if img_tag else ""
        price = "N/A"
        if "€" in title:
            price = title.split("€")[0].split(",")[-1].strip() + "€"

        items_list.append({
            "id": link.split("/items/")[-1].split("-")[0],
            "title": title,
            "price": price,
            "url": link,
            "photo": {"url": img_url},
            "size_title": "N/A",
            "user": {"login": "N/A"},
            "created_at": "N/A"
        })

    return items_list
