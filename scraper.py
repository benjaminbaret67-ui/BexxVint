# scraper.py
import os
import requests
import json

# ==============================
# Variables d'environnement (Railway ou local)
# ==============================
API_TOKEN = os.environ.get("BRIGHT_API_KEY")       # Votre clé Bright Data
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")      # Nom du proxy Unlocker (ex: vinted_unlocker_premium)
TARGET_URL = os.environ.get("TARGET_URL")          # URL catalogue Vinted, ex: "https://www.vinted.fr/catalog?search_text=nike"

if not all([API_TOKEN, UNLOCKER_ZONE, TARGET_URL]):
    raise ValueError("Les variables d'environnement BRIGHT_API_KEY, BRIGHT_ZONE et TARGET_URL doivent être définies !")

# ==============================
# Fonction principale pour récupérer les items
# ==============================
def get_vinted_items():
    """
    Récupère la page catalogue Vinted via Bright Data Unlocker Premium.
    Retourne une liste d'items avec : id, title, price, size_title, etat, url, photo, user, created_at
    """
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json"
    }

    # x-unblock-expect pour forcer rendu JS et attendre la grille d'items
    unblock_expect = {
        "element": ".feed-grid__item"
    }

    payload = {
        "zone": UNLOCKER_ZONE,
        "url": TARGET_URL,
        "format": "raw",
        "headers": {
            "x-unblock-expect": json.dumps(unblock_expect)
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
    except requests.HTTPError as e:
        print("❌ Erreur Bright Data :", e.response.status_code)
        print("BODY:", e.response.text[:1000])
        return []

    # Le HTML brut
    html = resp.text

    # ==============================
    # Parsing HTML simple pour les items
    # ==============================
    # On récupère les items via une méthode simple : recherche de blocs "<script id=__NEXT_DATA__>" ou regex
    # Ici, on fait un parse minimaliste pour les démonstrations

    items_list = []

    try:
        start_idx = html.index('<script id="__NEXT_DATA__" type="application/json">') + len('<script id="__NEXT_DATA__" type="application/json">')
        end_idx = html.index('</script>', start_idx)
        json_data = html[start_idx:end_idx]
        data = json.loads(json_data)
    except Exception:
        print("❌ __NEXT_DATA__ non trouvé, parse brut...")
        # Fallback : on pourrait utiliser BeautifulSoup, mais pour l'instant on renvoie vide
        return []

    # Parcours simplifié des items
    try:
        offers = data["props"]["pageProps"]["items"]  # structure Next.js typique
    except KeyError:
        print("❌ Clé items non trouvée dans __NEXT_DATA__")
        return []

    for offer in offers:
        item_id = offer.get("id")
        title = offer.get("title", "N/A")
        price = offer.get("price", "N/A")
        size_title = offer.get("size_title", "N/A")
        etat = offer.get("state_title", "N/A")       # état de l'article
        url = f"https://www.vinted.fr/{offer.get('url', '')}".replace("//www","www")
        photo_url = offer.get("photo", {}).get("url", "")
        user_login = offer.get("user", {}).get("login", "N/A")
        created_at = offer.get("created_at", "N/A")

        items_list.append({
            "id": item_id,
            "title": title,
            "price": price,
            "size_title": size_title,
            "etat": etat,
            "url": url,
            "photo": {"url": photo_url},
            "user": {"login": user_login},
            "created_at": created_at
        })

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list

# ==============================
# Test rapide en local
# ==============================
if __name__ == "__main__":
    items = get_vinted_items()
    for i, item in enumerate(items[:5]):
        print(f"{i+1}. {item['title']} - {item['price']} - {item['etat']}")
