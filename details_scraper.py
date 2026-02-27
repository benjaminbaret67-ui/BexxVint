# details_scraper.py
import requests
from bs4 import BeautifulSoup

def get_vinted_details(url):
    """Récupère vendeur et date d'ajout d'un item Vinted via requests + BS"""
    details = {"seller": "N/A", "date_added": "N/A"}
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/116.0.0.0 Safari/537.36"
        }
        resp = requests.get(url, headers=headers, timeout=15)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # vendeur
        seller_el = soup.select_one("div[data-testid='profile-link']")
        if seller_el:
            details["seller"] = seller_el.get_text(strip=True)

        # date
        date_el = soup.select_one("time")
        if date_el and date_el.has_attr("datetime"):
            details["date_added"] = date_el["datetime"]

    except Exception as e:
        print("❌ Erreur récupération détails :", e)

    return details
