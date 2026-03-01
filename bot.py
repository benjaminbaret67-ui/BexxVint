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
    global sent_items
    print("🔎 Recherche nouveaux items...")

    items = get_vinted_items()

    print("Nombre d'items reçus:", len(items))

    for item in items:
        print("----")
        print("ID:", item.get("id"))
        print("Titre:", item.get("title"))

        if item.get("id") in sent_items:
            print("⏭ Déjà envoyé")
            continue

        category = detect_category(item.get("title", ""))
        print("Catégorie détectée:", category)

        channel_id = CHANNELS.get(category)
        print("Channel ID:", channel_id)

        channel = bot.get_channel(channel_id)
        print("Channel objet:", channel)

        if channel is None:
            print("❌ Channel introuvable")
            continue

        print("✅ ENVOI MESSAGE")

        embed = discord.Embed(
            title=item.get("title", "N/A"),
            url=item.get("url", ""),
            color=0xff0000
        )

        await channel.send(embed=embed)

        sent_items.append(item.get("id"))

    print("FIN LOOP")

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

