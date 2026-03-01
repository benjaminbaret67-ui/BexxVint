import discord
from discord.ext import commands, tasks
import requests
import json
import os

TOKEN = "TON_TOKEN_ICI"

# ==============================
# CONFIGURATION
# ==============================

SEARCH_URL = "https://www.vinted.fr/api/v2/catalog/items"

PARAMS = {
    "search_text": "nike",
    "order": "newest_first",
    "currency": "EUR",
    "per_page": 50
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json"
}

CATEGORY_CHANNELS = {
    "tshirt": 1476944679776944249,
    "pull": 1476945026968981584,
    "veste": 1476945120669466664,
    "pantalon": 1476945217058766912,
    "chaussure": 1476945337829818421,
    "nike-tech": 1476945463306489868,
    "autre": 1476944679776944249
}

# ==============================
# DISCORD SETUP
# ==============================

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# ==============================
# LOAD DATA
# ==============================

try:
    with open("data.json", "r") as f:
        sent_items = set(json.load(f))
except:
    sent_items = set()

# ==============================
# CATEGORY DETECTION
# ==============================

def detect_category(title):
    title = title.lower()

    if "t-shirt" in title:
        return "tshirt"
    elif "pull" in title or "sweat" in title:
        return "pull"
    elif "veste" in title or "doudoune" in title:
        return "veste"
    elif "pantalon" in title or "jogging" in title:
        return "pantalon"
    elif "chaussure" in title or "sneaker" in title:
        return "chaussure"
    elif "tech" in title:
        return "nike-tech"
    else:
        return "autre"

# ==============================
# BUTTON VIEW
# ==============================

class VintedView(discord.ui.View):
    def __init__(self, item_url):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="🔎 Voir l'annonce", url=item_url))

# ==============================
# MONITOR TASK
# ==============================

@tasks.loop(seconds=30)
async def monitor_vinted():
    print("🔎 Recherche nouveaux items...")

    try:
        response = requests.get(SEARCH_URL, headers=HEADERS, params=PARAMS)
        data = response.json()
        items = data.get("items", [])

        print(f"✅ Items trouvés: {len(items)}")

        for item in items:

            item_id = str(item["id"])

            if item_id in sent_items:
                continue

            title = item.get("title", "N/A")
            price = item.get("price", "N/A")
            url = item.get("url", "")
            photo = item.get("photo", {}).get("url", None)
            size = item.get("size_title", "N/A")
            status = item.get("status", "N/A")

            category = detect_category(title)
            channel_id = CATEGORY_CHANNELS.get(category)

            if not channel_id:
                print("❌ Channel introuvable")
                continue

            channel = bot.get_channel(channel_id)

            if not channel:
                print("❌ Channel object introuvable")
                continue

            embed = discord.Embed(
                title=f"🔥 {title}",
                url=url,
                color=0xff0000
            )

            embed.add_field(name="💰 Prix", value=f"{price} €", inline=True)
            embed.add_field(name="📏 Taille", value=size, inline=True)
            embed.add_field(name="⚡ État", value=status, inline=True)

            if photo:
                embed.set_image(url=photo)

            embed.set_footer(text="🛍️ BexxVint Nike Monitor")

            view = VintedView(url)

            await channel.send(embed=embed, view=view)

            print("✅ ENVOYÉ :", title)

            sent_items.add(item_id)

        with open("data.json", "w") as f:
            json.dump(list(sent_items), f)

    except Exception as e:
        print("❌ Erreur :", e)

# ==============================
# EVENTS
# ==============================

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    monitor_vinted.start()

# ==============================
# START
# ==============================

bot.run(TOKEN)
