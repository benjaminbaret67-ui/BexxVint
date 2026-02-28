# scraper.py
import os
import requests
import json
from bs4 import BeautifulSoup

# ==============================
# VARIABLES D'ENVIRONNEMENT
# ==============================
BRIGHT_API_KEY = os.environ.get("BRIGHT_API_KEY")
BRIGHT_ZONE = os.environ.get("BRIGHT_ZONE")  # ex: vinted_unlocker_premium
TARGET_URL = os.environ.get("TARGET_URL", "https://www.vinted.fr/catalog?search_text=nike&order=newest_first")

if not BRIGHT_API_KEY or not BRIGHT_ZONE:
    raise ValueError("BRIGHT_API_KEY ou BRIGHT_ZONE non défini !")

# ==============================
# FONCTION PRINCIPALE
# ==============================
def get_vinted_html():
    """Récupère le HTML du catalogue Vinted via Bright Data Unlocker API"""
    url = "https://api.brightdata.com/request"
    headers = {
        "Authorization": f"Bearer {BRIGHT_API_KEY}",
        "Content-Type": "application/json",
    }

    unblock_expect = {"element": ".feed-grid__item"}  # attend que la grille d'items soit rendue JS

    payload = {
        "zone": BRIGHT_ZONE,
        "url": TARGET_URL,
        "format": "raw",
        "extra": {
            "headers": {
                "x-unblock-expect": json.dumps(unblock_expect)
            }
        }
    }

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        html = data.get("body", "")
        return html
    except Exception as e:
        print("❌ Erreur récupération Vinted :", e)
        return ""

# ==============================
# PARSING DES ITEMS
# ==============================
def parse_vinted_items(html):
    """Parse le HTML et retourne une liste d'items prêts pour Discord"""
    items_list = []
    soup = BeautifulSoup(html, "html.parser")
    cards = soup.select("a.new-item-box__overlay--clickable")

    for card in cards:
        try:
            link = card.get("href")
            if not link:
                continue
            if link.startswith("/"):
                link = "https://www.vinted.fr" + link

            title_full = card.get("title", "")
            if not title_full:
                continue

            # ===== Titre =====
            title = title_full.split(", état:")[0].strip()

            # ===== État =====
            etat = "N/A"
            if "état:" in title_full:
                try:
                    etat = title_full.split("état:")[1].split(",")[0].strip()
                except:
                    pass

            # ===== Taille =====
            taille = "N/A"
            if "taille:" in title_full:
                try:
                    taille = title_full.split("taille:")[1].split(",")[0].strip()
                except:
                    pass

            # ===== Prix =====
            prix = "N/A"
            parts = [p for p in title_full.split(",") if "€" in p]
            if parts:
                prix = parts[-1].strip()

            # ===== Image =====
            img_tag = card.find("img")
            img_url = img_tag.get("src") if img_tag and img_tag.get("src") else ""

            # ===== Item ID =====
            item_id = link.split("/items/")[-1].split("-")[0]

            items_list.append({
                "id": item_id,
                "title": title,
                "etat": etat,
                "size_title": taille,
                "price": prix,
                "url": link,
                "photo": {"url": img_url},
                "user": {"login": "N/A"},  # pas dispo sans JS ou API interne
                "created_at": "N/A"
            })

        except Exception:
            continue

    print("✅ Items trouvés:", len(items_list))
    return items_list

# ==============================
# FONCTION ASYNC
# ==============================
async def get_vinted_items():
    html = get_vinted_html()
    if not html:
        return []
    return parse_vinted_items(html)
