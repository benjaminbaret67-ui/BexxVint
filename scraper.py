# scraper.py
import requests
import json

def get_vinted_items():
    url = "https://www.vinted.fr/catalog?search_text=nike"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    try:
        resp = requests.get(url, headers=headers)
        resp.raise_for_status()
    except Exception as e:
        print("❌ Erreur récupération Vinted :", e)
        return []

    html = resp.text
    items = []

    try:
        parts = html.split('data-test-id="catalog-item"')
        for part in parts[1:]:
            try:
                id_str = part.split('data-id="')[1].split('"')[0]
                url_item = part.split('href="')[1].split('"')[0]
                title = part.split('title="')[1].split('"')[0]
                price = part.split('data-price="')[1].split('"')[0]
                etat = part.split('data-condition="')[1].split('"')[0]
                size = part.split('data-size="')[1].split('"')[0] if 'data-size=' in part else "N/A"
                user = part.split('data-user-login="')[1].split('"')[0]
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
                    "created_at": "N/A"
                })
            except:
                continue
    except:
        return []

    print(f"✅ Items trouvés: {len(items)}")
    return items
