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
# CHANNELS
# ==============================
CHANNELS = {
    "tshirt": 1476944679776944249,
    "sweat": 1476945026968981584,
    "doudoune": 1476945120669466664,
    "pantalon": 1476945217058766912,
    "chaussure": 1476945337829818421,
    "niketech": 1476945463306489868,
    "autre": 1476945999999999999  # un channel debug pour items non catégorisés
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
try:
    with open("data.json", "r") as f:
        sent_items = json.load(f)
except:
    sent_items = []

# ==============================
# DISCORD VIEW (BOUTONS)
# ==============================
class VintedView(discord.ui.View):
    def __init__(self, item_url):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="📄 Détails", url=item_url))
        self.add_item(discord.ui.Button(label="💳 Paiement", url=item_url))
        self.add_item(discord.ui.Button(label="💬 Contacter", url=item_url))

# ==============================
# CATEGORY DETECTION
# ==============================
def detect_category(title: str):
    title = title.lower()
    if "t-shirt" in title:
        return "tshirt"
    elif "sweat" in title or "hoodie" in title:
        return "sweat"
    elif "doudoune" in title or "veste" in title:
        return "doudoune"
    elif "pantalon" in title:
        return "pantalon"
    elif "chaussure" in title:
        return "chaussure"
    elif "tech" in title:
        return "niketech"
    return "autre"  # on envoie tout ce qui ne correspond pas au channel debug

# ==============================
# MAIN LOOP
# ==============================
@tasks.loop(seconds=30)
async def monitor_vinted():
    global sent_items
    print("🔎 Recherche nouveaux items...")

    try:
        items = get_vinted_items()  # scraper.py retourne la liste
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
        channel_id = CHANNELS.get(category)
        channel = bot.get_channel(channel_id)

        if not channel:
            print(f"⚠️ Channel introuvable pour la catégorie {category} (ID: {channel_id})")
            continue

        # ==============================
        # EMBED DISCORD
        # ==============================
        embed = discord.Embed(
            title=f"🔥 {item['title']}",
            url=item["url"],
            color=0xff0000
        )

        if item["photo"]["url"]:
            embed.set_image(url=item["photo"]["url"])

        embed.add_field(name="💰 Prix", value=item.get("price", "N/A"), inline=True)
        embed.add_field(name="📏 Taille", value=item.get("size_title", "N/A"), inline=True)
        embed.add_field(name="⚡ État", value=item.get("etat", "N/A"), inline=True)
        embed.add_field(name="👤 Vendeur", value=item.get("user", {}).get("login", "N/A"), inline=True)
        embed.add_field(name="📅 Ajouté", value=item.get("created_at", "N/A"), inline=False)

        embed.set_footer(text="🛍️ BexxVint Nike Monitor")

        view = VintedView(item["url"])
        await channel.send(embed=embed, view=view)

        sent_items.append(item["id"])
        with open("data.json", "w") as f:
            json.dump(sent_items, f)

        await asyncio.sleep(1)

# ==============================
# READY EVENT
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    print("Channels accessibles par le bot :")
    for c in bot.get_all_channels():
        print(f"{c.name} ({c.id})")
    monitor_vinted.start()

# ==============================
# START BOT
# ==============================
bot.run(TOKEN)
