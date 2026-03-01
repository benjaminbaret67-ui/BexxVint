import discord
from discord.ext import commands, tasks
import asyncio
import os
import json
from scraper import get_vinted_items

TOKEN = os.environ.get("TOKEN")

if not TOKEN:
    raise ValueError("TOKEN manquant")

CHANNELS = {
    "tshirt": 1476944679776944249,
    "sweat": 1476945026968981584,
    "doudoune": 1476945120669466664,
    "pantalon": 1476945217058766912,
    "chaussure": 1476945337829818421,
    "niketech": 1476945463306489868,
}

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

sent_items = set()

class VintedView(discord.ui.View):
    def __init__(self, url):
        super().__init__(timeout=None)
        self.add_item(discord.ui.Button(label="📄 Voir l'annonce", url=url))

def detect_category(title: str):
    title = title.lower()

    if "t-shirt" in title:
        return "tshirt"
    if "sweat" in title or "hoodie" in title:
        return "sweat"
    if "doudoune" in title or "veste" in title:
        return "doudoune"
    if "pantalon" in title:
        return "pantalon"
    if "chaussure" in title:
        return "chaussure"
    if "tech" in title:
        return "niketech"

    return None

@tasks.loop(seconds=30)
async def monitor_vinted():
    print("🔎 Recherche nouveaux items...")

    items = get_vinted_items()

    if not items:
        return

    for item in items:
        item_id = str(item["id"])

        if item_id in sent_items:
            continue

        category = detect_category(item["title"])

        if not category:
            continue

        channel_id = CHANNELS.get(category)
        channel = bot.get_channel(channel_id)

        if not channel:
            continue

        embed = discord.Embed(
            title=item["title"],
            url=item["url"],
            color=0xff0000
        )

        if item["photo"]["url"]:
            embed.set_image(url=item["photo"]["url"])

        embed.add_field(name="💰 Prix", value=item["price"], inline=True)
        embed.add_field(name="📏 Taille", value=item["size_title"], inline=True)
        embed.add_field(name="⚡ État", value=item["etat"], inline=True)
        embed.add_field(name="👤 Vendeur", value=item["user"]["login"], inline=True)

        embed.set_footer(text="🛍️ BexxVint Monitor")

        view = VintedView(item["url"])

        await channel.send(embed=embed, view=view)

        sent_items.add(item_id)

        await asyncio.sleep(1)

@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    monitor_vinted.start()

bot.run(TOKEN)
