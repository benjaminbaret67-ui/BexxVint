# details_scraper.py
import requests
from bs4 import BeautifulSoup

def get_vinted_details(item_url):
    """
    Récupère le vendeur et la date d'ajout d'un item Vinted donné.
    """
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                          "(KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }

        response = requests.get(item_url, headers=headers, timeout=15)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Récupération du vendeur
        seller_el = soup.select_one("a[href^='/member/']")
        seller = seller_el.get_text(strip=True) if seller_el else "N/A"

        # Récupération de la date d'ajout
        date_el = soup.select_one("div[data-testid='item-listing-created-date']")
        date_added = date_el.get_text(strip=True) if date_el else "N/A"

        return {"seller": seller, "date_added": date_added}

    except Exception as e:
        print(f"❌ Erreur récupération détails : {e}")
        return {"seller": "N/A", "date_added": "N/A"}


# Test rapide
if __name__ == "__main__":
    url = "https://www.vinted.fr/items/8274194264-chaussures-homme?referrer=catalog"
    details = get_vinted_details(url)
    print(details)
