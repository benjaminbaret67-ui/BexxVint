import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
from scraper import get_vinted_items

# ==============================
# TOKEN DISCORD
# ==============================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("La variable d'environnement TOKEN n'est pas définie !")

# ==============================
# CHANNELS (MET TES VRAIS IDS)
# ==============================
CHANNELS = {
    "tshirt": 1476944679776944249,
    "sweat": 1476945026968981584,
    "doudoune": 1476945120669466664,
    "pantalon": 1476945217058766912,
    "chaussure": 1476945337829818421,
    "niketech": 1476945463306489868
}

# ==============================
# BOT CONFIG
# ==============================
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# ==============================
# LOAD SENT ITEMS
# ==============================
if os.path.exists("data.json"):
    with open("data.json", "r") as f:
        sent_items = json.load(f)
else:
    sent_items = []

# ==============================
# DISCORD BUTTONS
# ==============================
class VintedView(discord.ui.View):
    def __init__(self, item_url):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="📄 Voir l'article", url=item_url))

# ==============================
# CATEGORY DETECTION (AMÉLIORÉE)
# ==============================
def detect_category(title: str):
    title = title.lower()

    if any(word in title for word in ["t-shirt", "t shirt", "tee"]):
        return "tshirt"

    if any(word in title for word in ["sweat", "hoodie"]):
        return "sweat"

    if any(word in title for word in ["doudoune", "veste"]):
        return "doudoune"

    if "pantalon" in title:
        return "pantalon"

    if any(word in title for word in ["chaussure", "sneaker"]):
        return "chaussure"

    if "tech" in title:
        return "niketech"

    return None  # IMPORTANT

# ==============================
# MAIN LOOP
# ==============================
@tasks.loop(seconds=30)
async def monitor_vinted():
    global sent_items
    print("🔎 Recherche nouveaux items...")

    try:
        items = get_vinted_items()
    except Exception as e:
        print("❌ Erreur récupération Vinted :", e)
        return

    if not items:
        print("❌ Aucun item récupéré.")
        return

    for item in items:
        if item["id"] in sent_items:
            continue

        category = detect_category(item["title"])
        if not category:
            continue

        channel_id = CHANNELS.get(category)
        channel = bot.get_channel(channel_id)

        if not channel:
            print(f"⚠️ Channel introuvable pour {category}")
            continue

        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            color=0xff0000
        )

        if item.get("photo_url"):
            embed.set_image(url=item["photo_url"])

        embed.add_field(name="💰 Prix", value=item.get("price", "N/A"), inline=True)
        embed.add_field(name="📏 Taille", value=item.get("size", "N/A"), inline=True)
        embed.add_field(name="⚡ État", value=item.get("etat", "N/A"), inline=True)
        embed.add_field(name="👤 Vendeur", value=item.get("user", "N/A"), inline=True)

        embed.set_footer(text="🛍️ BexxVint Monitor")

        view = VintedView(item["url"])
        await channel.send(embed=embed, view=view)

        sent_items.append(item["id"])

        with open("data.json", "w") as f:
            json.dump(sent_items, f)

        await asyncio.sleep(1)

# ==============================
# READY
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    monitor_vinted.start()

bot.run(TOKEN)
