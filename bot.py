# bot.py
import discord
from discord.ext import commands, tasks
import json
import asyncio
import os
from scraper import get_vinted_items  # scraper async

# ==============================
# IMPORT POUR VENDEUR & DATE
# ==============================
from playwright.async_api import async_playwright

async def get_item_details(url):
    details = {"user": "N/A", "created_at": "N/A"}
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, timeout=60000)
            await page.wait_for_selector("div[data-testid='profile-link']", timeout=5000)

            # vendeur
            seller_el = await page.query_selector("div[data-testid='profile-link']")
            if seller_el:
                details["user"] = await seller_el.inner_text()

            # date d'ajout
            date_el = await page.query_selector("time")
            if date_el:
                details["created_at"] = await date_el.get_attribute("datetime")

            await browser.close()
    except Exception as e:
        print("❌ Erreur récupération détails :", e)
    return details

# ==============================
# TOKEN
# ==============================
TOKEN = os.getenv("TOKEN")
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
try:
    with open("data.json", "r") as f:
        sent_items = json.load(f)
except:
    sent_items = []

# ==============================
# DISCORD VIEW
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
    return None

# ==============================
# MAIN LOOP
# ==============================
@tasks.loop(seconds=30)
async def monitor_vinted():
    global sent_items
    print("🔎 Recherche nouveaux items...")

    try:
        items = await get_vinted_items()
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

        channel = bot.get_channel(CHANNELS[category])
        if not channel:
            continue

        # ==============================
        # Récupération vendeur & date
        # ==============================
        details = await get_item_details(item["url"])
        item["user"]["login"] = details.get("user", "N/A")
        item["created_at"] = details.get("created_at", "N/A")

        embed = discord.Embed(
            title=f"🔥 {item['title']}",
            color=0xff0000
        )
        embed.add_field(name="💰 Prix", value=f"{item['price']}", inline=True)
        embed.add_field(name="👤 Vendeur", value=item["user"]["login"], inline=True)
        embed.add_field(name="📏 Taille", value=item.get("size_title", "N/A"), inline=True)
        embed.add_field(name="📅 Ajouté", value=item["created_at"], inline=False)
        if item["photo"]["url"]:
            embed.set_image(url=item["photo"]["url"])
        embed.set_footer(text="🛍️ BexxVint Nike Monitor")

        view = VintedView(item["url"])
        await channel.send(embed=embed, view=view)

        sent_items.append(item["id"])
        with open("data.json", "w") as f:
            json.dump(sent_items, f)

        await asyncio.sleep(2)

# ==============================
# READY EVENT
# ==============================
@bot.event
async def on_ready():
    print(f"✅ Connecté en tant que {bot.user}")
    monitor_vinted.start()

# ==============================
# START BOT
# ==============================
bot.run(TOKEN)
