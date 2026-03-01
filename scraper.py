import requests

# URL catalogue Vinted (France)
API_URL = "https://www.vinted.fr/api/v2/catalog/items"

PARAMS = {
    "page": 1,
    "per_page": 50,
    "order": "newest_first"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

def get_vinted_items():
    try:
        response = requests.get(API_URL, headers=HEADERS, params=PARAMS, timeout=30)
        response.raise_for_status()
    except Exception as e:
        print("❌ Erreur requête Vinted:", e)
        return []

    data = response.json()

    if "items" not in data:
        print("❌ Pas de items dans la réponse")
        return []

    items_list = []

    for item in data["items"]:
        try:
            items_list.append({
                "id": item.get("id"),
                "title": item.get("title"),
                "price": f"{item.get('price', {}).get('amount')}€",
                "size_title": item.get("size_title", "N/A"),
                "etat": item.get("status", "N/A"),
                "url": item.get("url"),
                "photo": {
                    "url": item.get("photo", {}).get("url", "")
                },
                "user": {
                    "login": item.get("user", {}).get("login", "N/A")
                },
                "created_at": item.get("created_at_ts", "N/A")
            })
        except:
            continue

    print(f"✅ Items trouvés: {len(items_list)}")
    return items_list
