# scraper.py
import os
import requests
import json

# Variables d'environnement (Railway ou local)
API_TOKEN = os.environ.get("BRIGHT_API_KEY")
UNLOCKER_ZONE = os.environ.get("BRIGHT_ZONE")
TARGET_URL = os.environ.get("TARGET_URL", "https://www.vinted.fr/catalog?search_text=nike")

def get_vinted_items():
    """
    Récupère les items du catalogue Vinted via Bright Data Unlocker API.
    Retourne une liste de dictionnaires avec :
    id, title, url, price, etat, size_title, user, photo, created_at
    """
    url = "https://api.brightdata.com/request"

    headers = {
        "Authorization": f"Bearer {API_TOKEN}",
        "Content-Type": "application/json",
    }

    # On demande à Unlocker d'attendre qu'un élément typique de la grille produits soit présent
    unblock_expect = {"element": ".feed-grid__item"}

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
    except Exception as e:
        print("❌ Erreur Bright Data :", e)
        return []

    html = resp.text

    # Parsing simplifié : Vinted a un HTML/JS complexe, on extrait les items du titre
    items = []
    try:
        # Exemple très simple : on split le HTML pour récupérer les cards
        parts = html.split('data-test-id="catalog-item"')
        for part in parts[1:]:
            try:
                # ID
                id_str = part.split('data-id="')[1].split('"')[0]
                # URL
                url_item = part.split('href="')[1].split('"')[0]
                # Title
                title = part.split('title="')[1].split('"')[0]
                # Prix
                price = part.split('data-price="')[1].split('"')[0]
                # État
                etat = part.split('data-condition="')[1].split('"')[0]
                # Taille
                size = part.split('data-size="')[1].split('"')[0] if 'data-size=' in part else "N/A"
                # Vendeur
                user = part.split('data-user-login="')[1].split('"')[0]
                # Photo
                photo = part.split('src="')[1].split('"')[0]

                items.append({
                    "id": id_str,
                    "title": title,
                    "url": url_item,
                    "price": price,
                    "etat": etat,
                    "size_title": size,
                    "user": {"login": user},
                    "photo": {"url": photo},
                    "created_at": "N/A"  # impossible à récupérer facilement depuis HTML brut
                })
            except:
                continue
    except Exception as e:
        print("❌ __NEXT_DATA__ non trouvé, parse brut...")
        return []

    print(f"✅ Items trouvés: {len(items)}")
    return items

# Version async pour Discord bot
import asyncio
async def get_vinted_items_async():
    return await asyncio.to_thread(get_vinted_items)
