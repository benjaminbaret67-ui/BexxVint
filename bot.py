import discord
from discord.ext import commands, tasks
import asyncio
import os
from scraper import get_vinted_items

# ==============================
# TOKEN DISCORD
# ==============================
TOKEN = os.environ.get("TOKEN")
if not TOKEN:
    raise ValueError("La variable TOKEN n'est pas définie !")

# ==============================
# CHANNELS (TES VRAIS IDs)
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
bot = commands.Bot(command_prefix="!", intents=intents)

# On garde les IDs en mémoire seulement
sent_items = set()

# ==============================
# CATEGORY DETECTION
# ==============================
def detect_category(title: str):
    title = title.lower()

    if "t-shirt" in title or "tee" in title:
        return "tshirt"
    if "sweat" in title or "hoodie" in title or "pull" in title:
        return "sweat"
    if "doudoune" in title or "veste" in title:
        return "doudoune"
    if "pantalon" in title or "jogger" in title:
        return "pantalon"
    if "chaussure" in title or "sneaker" in title:
        return "chaussure"
    if "tech" in title:
        return "niketech"

    return None

# ==============================
# MAIN LOOP
# ==============================
@tasks.loop(seconds=30)
async def monitor_vinted():
    print("🔎 Recherche nouveaux items...")

    items = get_vinted_items()

    if not items:
        print("❌ Aucun item récupéré.")
        return

    for item in items:

        # Skip si déjà envoyé pendant cette session
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

        if item["photo"]["url"]:
            embed.set_image(url=item["photo"]["url"])

        embed.add_field(name="💰 Prix", value=item.get("price", "N/A"), inline=True)
        embed.add_field(name="📏 Taille", value=item.get("size_title", "N/A"), inline=True)
        embed.add_field(name="⚡ État", value=item.get("etat", "N/A"), inline=True)
        embed.add_field(name="👤 Vendeur", value=item.get("user", {}).get("login", "N/A"), inline=True)
        embed.add_field(name="📅 Ajouté", value=item.get("created_at", "N/A"), inline=False)

        embed.set_footer(text="🛍️ BexxVint Monitor")

        await channel.send(embed=embed)

        sent_items.add(item["id"])

        await asyncio.sleep(1)

# ==============================
# READY
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    monitor_vinted.start()

# ==============================
# START
# ==============================
bot.run(TOKEN)
