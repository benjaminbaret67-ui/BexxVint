import discord
from discord.ext import commands, tasks
import requests
import json
import asyncio
import os

TOKEN = os.getenv("MTQ3Njg5MjgyNDc0NTE1MjU0Mg.GUwHGa.S0zlP-rF3Icx7J3qbPLUZ--bKk3j5bEMIFF0x4")

CHANNELS = {
    "tshirt": 1476944679776944249,
    "sweat": 1476945026968981584,
    "doudoune": 1476945120669466664,
    "pantalon": 1476945217058766912,
    "chaussure": 1476945337829818421,
    "niketech": 1476945463306489868
}

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

try:
    with open("data.json", "r") as f:
        sent_items = json.load(f)
except:
    sent_items = []

class VintedView(discord.ui.View):
    def __init__(self, item_url):
        super().__init__(timeout=None)

        self.add_item(discord.ui.Button(label="📄 Détails", url=item_url))
        self.add_item(discord.ui.Button(label="💳 Paiement", url=item_url))
        self.add_item(discord.ui.Button(label="💬 Contacter", url=item_url))

def get_vinted_items():
    url = "https://www.vinted.fr/api/v2/catalog/items?search_text=nike&order=newest_first"

    headers = {"User-Agent": "Mozilla/5.0"}

    r = requests.get(url, headers=headers)
    return r.json()["items"]

def detect_category(title):
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
    return None

@tasks.loop(seconds=30)
async def monitor_vinted():
    global sent_items
    items = get_vinted_items()

    for item in items:
        if item["id"] in sent_items:
            continue

        category = detect_category(item["title"])
        if not category:
            continue

        channel = bot.get_channel(CHANNELS[category])
        if not channel:
            continue

        embed = discord.Embed(
            title=f"🔥 {item['title']}",
            color=0xff0000
        )

        embed.add_field(name="💰 Prix", value=f"{item['price']} €", inline=True)
        embed.add_field(name="👤 Vendeur", value=item["user"]["login"], inline=True)
        embed.add_field(name="📏 Taille", value=item.get("size_title", "N/A"), inline=True)
        embed.add_field(name="📅 Ajouté", value=item["created_at"], inline=False)

        embed.set_image(url=item["photo"]["url"])
        embed.set_footer(text="🛍️ BexxVint Nike Monitor")

        view = VintedView(item["url"])

        await channel.send(embed=embed, view=view)

        sent_items.append(item["id"])

        with open("data.json", "w") as f:
            json.dump(sent_items, f)

        await asyncio.sleep(2)

@bot.event
async def on_ready():
    print(f"Connecté en tant que {bot.user}")
    monitor_vinted.start()


bot.run(TOKEN)
