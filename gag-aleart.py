import discord
from discord.ext import commands, tasks
import aiohttp
import asyncio
from bs4 import BeautifulSoup
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

# Bot-Konfiguration aus Umgebungsvariablen
TOKEN = os.getenv('DISCORD_TOKEN')
ROLE_CHANNEL_ID = int(os.getenv('ROLE_CHANNEL_ID'))
STOCK_URL = os.getenv('STOCK_URL')

# Channel IDs für verschiedene Kategorien (werden beim Setup erstellt)
CATEGORY_CHANNELS = {
    'Seeds': None,
    'Gear': None, 
    'Eggs': None,
    'Honey': None,
    'Cosmetics': None
}

# Logging einrichten
logging.basicConfig(level=logging.INFO)

# Bot Setup
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Globale Variablen
previous_stock = {}
tracked_items = [
    'Seeds', 'Gear', 'Eggs', 'Honey', 'Cosmetics', 'Special Items'
]

# Erweiterte Rollen für spezifische Raritäten
detailed_roles = {
    # Pet/Egg Raritäten (basierend auf offiziellem Wiki)
    'common_egg': {'emoji': '🥚', 'color': discord.Color.light_grey(), 'category': 'Eggs'},
    'uncommon_egg': {'emoji': '🐣', 'color': discord.Color.green(), 'category': 'Eggs'},
    'rare_egg': {'emoji': '💎', 'color': discord.Color.blue(), 'category': 'Eggs'},
    'legendary_egg': {'emoji': '🏆', 'color': discord.Color.gold(), 'category': 'Eggs'},
    'mythical_egg': {'emoji': '🔮', 'color': discord.Color.purple(), 'category': 'Eggs'},
    'bug_egg': {'emoji': '🐛', 'color': discord.Color.from_rgb(139, 69, 19), 'category': 'Eggs'},
    'night_egg': {'emoji': '🌙', 'color': discord.Color.dark_blue(), 'category': 'Eggs'},
    
    # Seeds Raritäten (basierend auf offiziellem Wiki)
    'common_seeds': {'emoji': '🌱', 'color': discord.Color.light_grey(), 'category': 'Seeds'},
    'uncommon_seeds': {'emoji': '🌾', 'color': discord.Color.green(), 'category': 'Seeds'},
    'rare_seeds': {'emoji': '🌺', 'color': discord.Color.blue(), 'category': 'Seeds'},
    'legendary_seeds': {'emoji': '🏆', 'color': discord.Color.gold(), 'category': 'Seeds'},
    'mythical_seeds': {'emoji': '🔮', 'color': discord.Color.purple(), 'category': 'Seeds'},
    'divine_seeds': {'emoji': '✨', 'color': discord.Color.from_rgb(255, 215, 0), 'category': 'Seeds'},
    'prismatic_seeds': {'emoji': '🌈', 'color': discord.Color.from_rgb(255, 20, 147), 'category': 'Seeds'},
    
    # Gear Raritäten (basierend auf offiziellem Wiki)
    'common_gear': {'emoji': '🔧', 'color': discord.Color.light_grey(), 'category': 'Gear'},
    'rare_gear': {'emoji': '🌺', 'color': discord.Color.blue(), 'category': 'Gear'},
    'legendary_gear': {'emoji': '🏆', 'color': discord.Color.gold(), 'category': 'Gear'},
    'mythical_gear': {'emoji': '🔮', 'color': discord.Color.purple(), 'category': 'Gear'},
    'divine_gear': {'emoji': '✨', 'color': discord.Color.from_rgb(255, 215, 0), 'category': 'Gear'},
    
    # Spezifische Premium Gear Items (sehr selten und begehrt)
    'master_sprinkler': {'emoji': '💧', 'color': discord.Color.from_rgb(0, 191, 255), 'category': 'Gear'},      # Master Sprinkler
    'friendship_pot': {'emoji': '💖', 'color': discord.Color.from_rgb(255, 105, 180), 'category': 'Gear'},      # Friendship Pot/Favorite Tool
    
    # Honey Items
    'flower_items': {'emoji': '🌻', 'color': discord.Color.from_rgb(255, 215, 0), 'category': 'Honey'},
    'bee_items': {'emoji': '🐝', 'color': discord.Color.from_rgb(255, 193, 7), 'category': 'Honey'},
    'honey_items': {'emoji': '🍯', 'color': discord.Color.gold(), 'category': 'Honey'},
    
    # Cosmetics (basierend auf Preisstufen im Wiki)
    'cheap_cosmetics': {'emoji': '🎨', 'color': discord.Color.light_grey(), 'category': 'Cosmetics'},    # Unter 1M
    'basic_cosmetics': {'emoji': '🪑', 'color': discord.Color.green(), 'category': 'Cosmetics'},        # 1M-10M  
    'premium_cosmetics': {'emoji': '🏗️', 'color': discord.Color.blue(), 'category': 'Cosmetics'},      # 10M-50M
    'luxury_cosmetics': {'emoji': '💎', 'color': discord.Color.purple(), 'category': 'Cosmetics'},     # 50M+
    'crate_cosmetics': {'emoji': '📦', 'color': discord.Color.gold(), 'category': 'Cosmetics'}         # Aus Crates
}

class SeedsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Alle Seeds", description="Alle Samen-Updates", emoji="🌱", value="seeds_stock_notify"),
            discord.SelectOption(label="Prismatic Seeds", description="Nur Prismatic Seeds", emoji="🌈", value="prismatic_seeds_stock_notify"),
            discord.SelectOption(label="Divine Seeds", description="Nur Divine Seeds", emoji="✨", value="divine_seeds_stock_notify"),
            discord.SelectOption(label="Mythical Seeds", description="Nur Mythical Seeds", emoji="🔮", value="mythical_seeds_stock_notify"),
            discord.SelectOption(label="Legendary Seeds", description="Nur Legendary Seeds", emoji="🏆", value="legendary_seeds_stock_notify"),
            discord.SelectOption(label="Rare Seeds", description="Nur Rare Seeds", emoji="🌺", value="rare_seeds_stock_notify"),
            discord.SelectOption(label="Uncommon Seeds", description="Nur Uncommon Seeds", emoji="🌾", value="uncommon_seeds_stock_notify"),
            discord.SelectOption(label="Common Seeds", description="Nur Common Seeds", emoji="🌱", value="common_seeds_stock_notify")
        ]
        
        super().__init__(
            placeholder="🌱 Seeds-Benachrichtigungen wählen...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, self.values, "Seeds")

class GearDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Alle Gear", description="Alle Ausrüstungs-Updates", emoji="⚒️", value="gear_stock_notify"),
            discord.SelectOption(label="Master Sprinkler", description="🚨 ULTRA RARE - Master Sprinkler", emoji="💧", value="master_sprinkler_stock_notify"),
            discord.SelectOption(label="Friendship Pot", description="🚨 ULTRA RARE - Friendship Pot", emoji="💖", value="friendship_pot_stock_notify"),
            discord.SelectOption(label="Divine Gear", description="Nur Divine Gear", emoji="✨", value="divine_gear_stock_notify"),
            discord.SelectOption(label="Mythical Gear", description="Nur Mythical Gear", emoji="🔮", value="mythical_gear_stock_notify"),
            discord.SelectOption(label="Legendary Gear", description="Nur Legendary Gear", emoji="🏆", value="legendary_gear_stock_notify"),
            discord.SelectOption(label="Rare Gear", description="Nur Rare Gear", emoji="🌺", value="rare_gear_stock_notify"),
            discord.SelectOption(label="Common Gear", description="Nur Common Gear", emoji="🔧", value="common_gear_stock_notify")
        ]
        
        super().__init__(
            placeholder="⚒️ Gear-Benachrichtigungen wählen...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, self.values, "Gear")

class EggsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Alle Eggs", description="Alle Eier-Updates", emoji="🥚", value="eggs_stock_notify"),
            discord.SelectOption(label="Night Egg", description="Nur Night Egg", emoji="🌙", value="night_egg_stock_notify"),
            discord.SelectOption(label="Bug Egg", description="Nur Bug Egg", emoji="🐛", value="bug_egg_stock_notify"),
            discord.SelectOption(label="Mythical Egg", description="Nur Mythical Egg", emoji="🔮", value="mythical_egg_stock_notify"),
            discord.SelectOption(label="Legendary Egg", description="Nur Legendary Egg", emoji="🏆", value="legendary_egg_stock_notify"),
            discord.SelectOption(label="Rare Egg", description="Nur Rare Egg", emoji="💎", value="rare_egg_stock_notify"),
            discord.SelectOption(label="Uncommon Egg", description="Nur Uncommon Egg", emoji="🐣", value="uncommon_egg_stock_notify"),
            discord.SelectOption(label="Common Egg", description="Nur Common Egg", emoji="🥚", value="common_egg_stock_notify")
        ]
        
        super().__init__(
            placeholder="🥚 Eggs-Benachrichtigungen wählen...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, self.values, "Eggs")

class HoneyDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Alle Honey", description="Alle Honig-Updates", emoji="🍯", value="honey_stock_notify"),
            discord.SelectOption(label="Honey Items", description="Nur Honey Items", emoji="🍯", value="honey_items_stock_notify"),
            discord.SelectOption(label="Bee Items", description="Nur Bee Items", emoji="🐝", value="bee_items_stock_notify"),
            discord.SelectOption(label="Flower Items", description="Nur Flower Items", emoji="🌻", value="flower_items_stock_notify")
        ]
        
        super().__init__(
            placeholder="🍯 Honey-Benachrichtigungen wählen...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, self.values, "Honey")

class CosmeticsDropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Alle Cosmetics", description="Alle Kosmetik-Updates", emoji="🎨", value="cosmetics_stock_notify"),
            discord.SelectOption(label="Luxury Cosmetics", description="Nur Luxury Cosmetics (50M+)", emoji="💎", value="luxury_cosmetics_stock_notify"),
            discord.SelectOption(label="Premium Cosmetics", description="Nur Premium Cosmetics (10M-50M)", emoji="🏗️", value="premium_cosmetics_stock_notify"),
            discord.SelectOption(label="Basic Cosmetics", description="Nur Basic Cosmetics (1M-10M)", emoji="🪑", value="basic_cosmetics_stock_notify"),
            discord.SelectOption(label="Cheap Cosmetics", description="Nur Cheap Cosmetics (<1M)", emoji="🎨", value="cheap_cosmetics_stock_notify"),
            discord.SelectOption(label="Crate Cosmetics", description="Nur Crate Cosmetics", emoji="📦", value="crate_cosmetics_stock_notify")
        ]
        
        super().__init__(
            placeholder="🎨 Cosmetics-Benachrichtigungen wählen...",
            min_values=0,
            max_values=len(options),
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        await handle_role_selection(interaction, self.values, "Cosmetics")

async def handle_role_selection(interaction, selected_values, category_name):
    """Behandelt die Rollenauswahl für alle Dropdowns"""
    member = interaction.user
    guild = interaction.guild
    
    # Entferne alle relevanten Stock-Rollen des Users
    roles_to_remove = []
    for role in member.roles[:]:
        if role.name.endswith('_stock_notify'):
            # Nur Rollen der entsprechenden Kategorie entfernen
            if category_name == "Seeds" and any(x in role.name for x in ['seeds', 'prismatic', 'divine', 'mythical', 'legendary', 'rare', 'uncommon', 'common']):
                roles_to_remove.append(role)
            elif category_name == "Gear" and any(x in role.name for x in ['gear', 'divine_gear', 'mythical_gear', 'legendary_gear', 'rare_gear', 'common_gear', 'master_sprinkler', 'friendship_pot']):
                roles_to_remove.append(role)
            elif category_name == "Eggs" and any(x in role.name for x in ['egg', 'night_egg', 'bug_egg', 'mythical_egg', 'legendary_egg', 'rare_egg', 'uncommon_egg', 'common_egg']):
                roles_to_remove.append(role)
            elif category_name == "Honey" and any(x in role.name for x in ['honey', 'bee_items', 'flower_items', 'honey_items']):
                roles_to_remove.append(role)
            elif category_name == "Cosmetics" and any(x in role.name for x in ['cosmetics', 'luxury', 'premium', 'basic', 'cheap', 'crate']):
                roles_to_remove.append(role)
    
    for role in roles_to_remove:
        try:
            await member.remove_roles(role)
        except:
            pass
    
    # Neue Rollen hinzufügen
    added_roles = []
    for value in selected_values:
        role_name = value  # Bereits der vollständige Rolle-Name
        role = discord.utils.get(guild.roles, name=role_name)
        
        if not role:
            # Bestimme Farbe basierend auf Rolle
            color = discord.Color.default()
            
            # Hauptkategorien
            if role_name == 'seeds_stock_notify':
                color = discord.Color.green()
            elif role_name == 'gear_stock_notify':
                color = discord.Color.blue()
            elif role_name == 'eggs_stock_notify':
                color = discord.Color.orange()
            elif role_name == 'honey_stock_notify':
                color = discord.Color.gold()
            elif role_name == 'cosmetics_stock_notify':
                color = discord.Color.purple()
            else:
                # Detaillierte Rollen
                role_key = role_name.replace('_stock_notify', '')
                if role_key in detailed_roles:
                    color = detailed_roles[role_key]['color']
            
            try:
                role = await guild.create_role(
                    name=role_name,
                    mentionable=True,
                    color=color,
                    reason="Stock notification role"
                )
            except Exception as e:
                print(f"Fehler beim Erstellen der Rolle {role_name}: {e}")
                continue
        
        if role:
            try:
                await member.add_roles(role)
                added_roles.append(role.name)
            except Exception as e:
                print(f"Fehler beim Hinzufügen der Rolle {role.name}: {e}")
    
    if added_roles:
        role_list = ", ".join([f"`{role}`" for role in added_roles])
        await interaction.response.send_message(
            f"✅ **{category_name} Benachrichtigungen aktualisiert!**\nDeine neuen Rollen: {role_list}",
            ephemeral=True
        )
    else:
        await interaction.response.send_message(
            f"ℹ️ **{category_name} Benachrichtigungen entfernt!**\nDu erhältst keine {category_name}-Benachrichtigungen mehr.",
            ephemeral=True
        )

class SeedsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(SeedsDropdown())

class GearView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(GearDropdown())

class EggsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(EggsDropdown())

class HoneyView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(HoneyDropdown())

class CosmeticsView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(CosmeticsDropdown())

async def fetch_stock_data():
    """Holt die aktuellen Stock-Daten von der Website"""
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            async with session.get(STOCK_URL, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    stock_data = {}
                    
                    # Definiere die Shop-Kategorien
                    shop_categories = {
                        'GEAR STOCK': 'Gear',
                        'EGG STOCK': 'Eggs', 
                        'SEEDS STOCK': 'Seeds',
                        'HONEY STOCK': 'Honey',
                        'COSMETICS STOCK': 'Cosmetics'
                    }
                    
                    # Finde alle Stock-Sektionen
                    for category_name, category_type in shop_categories.items():
                        # Suche nach dem Header
                        header = soup.find('h2', string=category_name)
                        if header:
                            # Finde das Parent-Div der Kategorie
                            category_div = header.find_parent('div')
                            if category_div:
                                # Finde alle li-Elemente in dieser Kategorie
                                items = category_div.find_all('li', class_='bg-gray-900')
                                
                                for item in items:
                                    try:
                                        # Finde den span mit dem Item-Namen
                                        span = item.find('span')
                                        if span:
                                            # Extrahiere Item-Name (ohne die Anzahl in gray)
                                            item_text = span.get_text(strip=True)
                                            
                                            # Entferne die Anzahl (z.B. "x3") am Ende
                                            item_name = item_text.split(' x')[0].strip()
                                            
                                            # Extrahiere die Anzahl
                                            quantity_span = span.find('span', class_='text-gray-400')
                                            quantity = 1
                                            if quantity_span:
                                                qty_text = quantity_span.get_text(strip=True)
                                                if qty_text.startswith('x'):
                                                    try:
                                                        quantity = int(qty_text[1:])
                                                    except:
                                                        quantity = 1
                                            
                                            # Finde das Bild für zusätzliche Info
                                            img = item.find('img')
                                            img_src = img.get('src', '') if img else ''
                                            
                                            if item_name:
                                                stock_data[item_name] = {
                                                    'available': True,
                                                    'category': category_type,
                                                    'quantity': quantity,
                                                    'image': img_src,
                                                    'timestamp': datetime.now()
                                                }
                                    except Exception as e:
                                        print(f"Fehler beim Parsen von Item: {e}")
                                        continue
                    
                    print(f"Stock-Daten geladen: {len(stock_data)} Items gefunden")
                    for item, data in stock_data.items():
                        print(f"  - {item} ({data['category']}) x{data['quantity']}")
                    
                    return stock_data
                else:
                    print(f"HTTP Error: {response.status}")
                    return None
    except Exception as e:
        print(f"Fehler beim Abrufen der Stock-Daten: {e}")
        return None

@tasks.loop(minutes=5)
async def check_stock():
    """Überprüft alle 5 Minuten die Stock-Änderungen"""
    global previous_stock
    
    current_stock = await fetch_stock_data()
    if not current_stock:
        return
    
    # Gruppiere neue Items nach Kategorien
    new_items_by_category = {}
    
    for item_name, item_data in current_stock.items():
        if item_name not in previous_stock:
            category = item_data.get('category', 'Special Items')
            if category not in new_items_by_category:
                new_items_by_category[category] = []
            new_items_by_category[category].append((item_name, item_data))
    
    # Sende Benachrichtigungen für jede Kategorie
    for category, items in new_items_by_category.items():
        await send_category_stock_update(category, items)
    
    previous_stock = current_stock

@tasks.loop(hours=24)
async def daily_emoji_check():
    """Überprüft täglich auf neue Emojis von der Website"""
    print("🔄 Täglicher Emoji-Check...")
    downloaded = await auto_download_emojis()
    if downloaded:
        print(f"✅ {len(downloaded)} neue Emojis heruntergeladen")
    else:
        print("ℹ️ Keine neuen Emojis gefunden")

@bot.command(name='updateemojis')
async def update_emojis_command(ctx):
    """Manueller Command um neue Emojis herunterzuladen"""
    if ctx.author.guild_permissions.administrator:
        await ctx.send("🔄 Suche nach neuen Emojis...")
        downloaded = await auto_download_emojis()
        
        if downloaded:
            emoji_list = "\n".join([f"{emoji['emoji']} `{emoji['name']}`" for emoji in downloaded[:10]])
            if len(downloaded) > 10:
                emoji_list += f"\n... und {len(downloaded) - 10} weitere"
            
            await ctx.send(f"✅ **{len(downloaded)} neue Emojis heruntergeladen:**\n{emoji_list}")
        else:
            await ctx.send("ℹ️ Keine neuen Emojis gefunden. Alle verfügbaren Emojis sind bereits vorhanden.")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")
    """Überprüft alle 5 Minuten die Stock-Änderungen"""
    global previous_stock
    
    current_stock = await fetch_stock_data()
    if not current_stock:
        return
    
    # Gruppiere neue Items nach Kategorien
    new_items_by_category = {}
    
    for item_name, item_data in current_stock.items():
        if item_name not in previous_stock:
            category = item_data.get('category', 'Special Items')
            if category not in new_items_by_category:
                new_items_by_category[category] = []
            new_items_by_category[category].append((item_name, item_data))
    
    # Sende Benachrichtigungen für jede Kategorie
    for category, items in new_items_by_category.items():
        await send_category_stock_update(category, items)
    
    previous_stock = current_stock

async def send_category_stock_update(category, items):
    """Sendet eine kombinierte Stock-Update-Nachricht für eine Kategorie"""
    guild = bot.get_guild(bot.guilds[0].id) if bot.guilds else None
    if not guild:
        return
    
    # Finde den entsprechenden Channel für die Kategorie
    channel_name = f"gag-{category.lower()}-stock"
    channel = discord.utils.get(guild.channels, name=channel_name)
    
    if not channel:
        print(f"❌ Channel {channel_name} nicht gefunden! Verwende !channelsetup")
        return
    
    # Bestimme Emoji und Farbe
    emoji_map = {
        'Seeds': '🌱',
        'Gear': '⚒️',
        'Eggs': '🥚', 
        'Honey': '🍯',
        'Cosmetics': '🎨'
    }
    
    color_map = {
        'Seeds': discord.Color.green(),
        'Gear': discord.Color.blue(),
        'Eggs': discord.Color.orange(),
        'Honey': discord.Color.gold(),
        'Cosmetics': discord.Color.purple()
    }
    
    emoji = emoji_map.get(category, '🔔')
    color = color_map.get(category, discord.Color.green())
    
    # Sammle alle Rollen für Benachrichtigungen
    mentioned_roles = set()
    
    # Hauptkategorie-Rolle
    main_role = discord.utils.get(guild.roles, name=f"{category.lower()}_stock_notify")
    if main_role:
        mentioned_roles.add(main_role)
    
    # Erstelle Embed
    embed = discord.Embed(
        title=f"{emoji} {category} Stock Update!",
        description=f"Neue Items im {category} Shop verfügbar:",
        color=color,
        timestamp=datetime.now()
    )
    
    # Füge Items hinzu und sammle spezifische Rollen
    items_text = ""
    vip_items = []  # Sammle VIP Items für spezielle Behandlung
    
    for item_name, item_data in items:
        quantity = item_data.get('quantity', 1)
        
        # Bestimme spezifische Rarität
        detailed_rarity = determine_detailed_rarity(item_name, category)
        specific_role = discord.utils.get(guild.roles, name=f"{detailed_rarity}_stock_notify")
        if specific_role:
            mentioned_roles.add(specific_role)
        
        # Prüfe auf VIP Items (Master Sprinkler & Friendship Pot)
        if detailed_rarity in ['master_sprinkler', 'friendship_pot']:
            vip_items.append((item_name, item_data, detailed_rarity))
        
        # Suche nach Custom Emoji mit der neuen Funktion
        custom_emoji = get_item_emoji(guild, item_name)
        
        # Bestimme Rarität-Emoji
        rarity_emoji = detailed_roles.get(detailed_rarity, {}).get('emoji', emoji)
        
        item_display = str(custom_emoji) if custom_emoji else rarity_emoji
        items_text += f"{item_display} **{item_name}** (x{quantity}) - *{detailed_rarity.replace('_', ' ').title()}*\n"
    
    embed.add_field(name="Verfügbare Items:", value=items_text, inline=False)
    
    # Spezielle VIP-Behandlung
    if vip_items:
        vip_text = "🚨 **ULTRA RARE ALERT!** 🚨\n"
        for vip_name, vip_data, vip_rarity in vip_items:
            vip_emoji = detailed_roles.get(vip_rarity, {}).get('emoji', '🔥')
            vip_text += f"{vip_emoji} **{vip_name}** - SOFORT ZUSCHLAGEN!\n"
        embed.add_field(name="🔥 VIP ALERT:", value=vip_text, inline=False)
        
        # Verwende rote Farbe für VIP-Alerts
        embed.color = discord.Color.red()
    
    embed.set_footer(text="Grow a Garden Stock Bot")
    
    # Erstelle Mention-String
    mentions = " ".join([role.mention for role in mentioned_roles])
    
    # Extra @everyone für VIP Items
    if vip_items:
        mentions = "@everyone " + mentions
    
    await channel.send(content=mentions, embed=embed)

def determine_detailed_rarity(item_name, category):
    """Bestimmt die spezifische Rarität eines Items basierend auf offiziellem Wiki"""
    item_lower = item_name.lower()
    
    if category == 'Eggs':
        # Basierend auf offiziellem Pet Wiki
        if 'common' in item_lower:
            return 'common_egg'
        elif 'uncommon' in item_lower:
            return 'uncommon_egg'
        elif 'rare' in item_lower:
            return 'rare_egg'
        elif 'legendary' in item_lower:
            return 'legendary_egg'
        elif 'mythical' in item_lower:
            return 'mythical_egg'
        elif 'bug' in item_lower:
            return 'bug_egg'
        elif 'night' in item_lower:
            return 'night_egg'
        else:
            return 'common_egg'  # Fallback
    
    elif category == 'Seeds':
        # Basierend auf offiziellem Wiki - exakte Zuordnung
        
        # Prismatic (höchste Seltenheit)
        prismatic_crops = ['beanstalk']
        
        # Divine
        divine_crops = ['grape', 'mushroom', 'pepper', 'cacao', 'soul fruit', 'cursed fruit', 
                       'candy blossom', 'venus fly trap', 'lotus', 'moon blossom', 'cherry blossom']
        
        # Mythical  
        mythical_crops = ['coconut', 'cactus', 'dragon fruit', 'mango', 'pineapple', 'peach',
                         'banana', 'passionfruit', 'eggplant', 'blood banana', 'moon melon', 'moonglow']
        
        # Legendary
        legendary_crops = ['watermelon', 'pumpkin', 'apple', 'bamboo', 'papaya', 'easter egg',
                          'cranberry', 'durian', 'moonflower', 'starfruit']
        
        # Rare
        rare_crops = ['tomato', 'corn', 'daffodil', 'raspberry', 'pear', 'candy sunflower',
                     'glowshroom', 'mint']
        
        # Uncommon
        uncommon_crops = ['blueberry', 'orange tulip', 'red lollipop', 'nightshade']
        
        # Common (alles andere)
        common_crops = ['carrot', 'strawberry', 'chocolate carrot']
        
        if any(crop in item_lower for crop in prismatic_crops):
            return 'prismatic_seeds'
        elif any(crop in item_lower for crop in divine_crops):
            return 'divine_seeds'
        elif any(crop in item_lower for crop in mythical_crops):
            return 'mythical_seeds'
        elif any(crop in item_lower for crop in legendary_crops):
            return 'legendary_seeds'
        elif any(crop in item_lower for crop in rare_crops):
            return 'rare_seeds'
        elif any(crop in item_lower for crop in uncommon_crops):
            return 'uncommon_seeds'
        elif any(crop in item_lower for crop in common_crops):
            return 'common_seeds'
        else:
            return 'common_seeds'  # Fallback für unbekannte Seeds
    
    elif category == 'Gear':
        # Spezifische ultra-rare Gear Items (höchste Priorität)
        if 'master sprinkler' in item_lower:
            return 'master_sprinkler'
        elif 'favorite tool' in item_lower or 'friendship pot' in item_lower:
            return 'friendship_pot'
        
        # Basierend auf offiziellem Gear Wiki
        
        # Divine Gear
        divine_gear = ['harvest tool']
        
        # Mythical Gear  
        mythical_gear = ['lightning rod', 'godly sprinkler', 'chocolate sprinkler']
        
        # Legendary Gear
        legendary_gear = ['advanced sprinkler', 'night staff', 'star caller']
        
        # Rare Gear
        rare_gear = ['basic sprinkler']
        
        # Common Gear
        common_gear = ['trowel', 'watering can', 'recall wrench']
        
        if any(gear in item_lower for gear in divine_gear):
            return 'divine_gear'
        elif any(gear in item_lower for gear in mythical_gear):
            return 'mythical_gear'
        elif any(gear in item_lower for gear in legendary_gear):
            return 'legendary_gear'
        elif any(gear in item_lower for gear in rare_gear):
            return 'rare_gear'
        elif any(gear in item_lower for gear in common_gear):
            return 'common_gear'
        else:
            return 'common_gear'  # Fallback
    
    elif category == 'Honey':
        if 'bee' in item_lower:
            return 'bee_items'
        elif 'honey' in item_lower or 'comb' in item_lower:
            return 'honey_items'
        elif 'flower' in item_lower or 'lavender' in item_lower:
            return 'flower_items'
        else:
            return 'flower_items'  # Fallback
    
    elif category == 'Cosmetics':
        # Basierend auf Preisstufen aus dem Wiki
        
        # Luxury (50M+)
        luxury_items = ['brown well', 'red well', 'blue well', 'ring walkway', 'viney ring walkway', 
                       'red tractor', 'green tractor', 'large wood arbour', 'round metal arbour']
        
        # Premium (10M-50M)  
        premium_items = ['brown stone pillar', 'grey stone pillar', 'dark stone pillar', 
                        'small wood table', 'large wood table', 'curved canopy', 'flat canopy',
                        'campfire', 'cooking pot', 'clothesline', 'small wood arbour', 
                        'square metal arbour', 'bird bath', 'lamp post', 'metal wind chime',
                        'bamboo wind chimes']
        
        # Basic (1M-10M)
        basic_items = ['log', 'wood pile', 'torch', 'rock pile', 'red pottery', 'white pottery',
                      'rake', 'orange umbrella', 'yellow umbrella', 'brown bench', 'white bench',
                      'small stone table', 'medium stone table', 'long stone table', 'small wood flooring',
                      'medium wood flooring', 'large wood flooring', 'mini tv', 'viney beam',
                      'light on ground', 'bookshelf', 'axe stump', 'shovel grave', 'small stone lantern']
        
        # Crate Items
        crate_items = ['farmers gnome crate', 'sign crate', 'common gnome crate', 'classic gnome crate', 'fun crate']
        
        if any(item in item_lower for item in luxury_items):
            return 'luxury_cosmetics'
        elif any(item in item_lower for item in premium_items):
            return 'premium_cosmetics'  
        elif any(item in item_lower for item in basic_items):
            return 'basic_cosmetics'
        elif any(item in item_lower for item in crate_items):
            return 'crate_cosmetics'
        else:
            return 'cheap_cosmetics'  # Fallback für günstige Items
    
    # Fallback zu Hauptkategorie
    return category.lower().replace(' ', '_')

@bot.event
async def on_ready():
    print(f'{bot.user} ist online!')
    
    # Role-Setup-Nachricht senden
    channel = bot.get_channel(ROLE_CHANNEL_ID)
    if channel:
        embed = discord.Embed(
            title="🌱 Grow a Garden Stock Benachrichtigungen",
            description="Wähle die Items aus, für die du Benachrichtigungen erhalten möchtest:",
            color=discord.Color.green()
        )
        embed = discord.Embed(
            title="🌱 Grow a Garden Stock Benachrichtigungen",
            description="Wähle die Kategorien aus, für die du Benachrichtigungen erhalten möchtest:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Hauptkategorien:",
            value="• 🌱 **Alle Seeds** - Benachrichtigung für alle Samen\n• ⚒️ **Alle Gear** - Benachrichtigung für alle Ausrüstung\n• 🥚 **Alle Eggs** - Benachrichtigung für alle Eier\n• 🍯 **Alle Honey** - Benachrichtigung für alle Honig-Items\n• 🎨 **Alle Cosmetics** - Benachrichtigung für alle Kosmetik",
            inline=False
        )
        embed.add_field(
            name="⭐ Wichtigste Raritäten:",
            value="• **Seeds**: 🌈 Prismatic, ✨ Divine, 🔮 Mythical, 🏆 Legendary\n• **Eggs**: 🔮 Mythical, 🏆 Legendary, 🐛 Bug, 🌙 Night\n• **Gear**: 💧 Master Sprinkler, 💖 Friendship Pot, ✨ Divine, 🔮 Mythical\n• **Cosmetics**: 💎 Luxury, 📦 Crate Items\n• **Honey**: 🌻 Flower, 🐝 Bee, 🍯 Honey Items",
            inline=False
        )
@bot.event
async def on_ready():
    print(f'{bot.user} ist online!')
    
    # Automatischer Emoji-Download beim Start
    print("🔄 Starte automatischen Emoji-Download...")
    await auto_download_emojis()
    
    # Role-Setup-Nachrichten senden (alte Nachrichten löschen)
    channel = bot.get_channel(ROLE_CHANNEL_ID)
    if channel:
        # Lösche alte Bot-Nachrichten in diesem Channel
        print("🧹 Lösche alte Bot-Nachrichten...")
        try:
            async for message in channel.history(limit=100):
                if message.author == bot.user:
                    try:
                        await message.delete()
                        await asyncio.sleep(0.5)  # Rate limiting
                    except:
                        pass
        except Exception as e:
            print(f"⚠️ Konnte alte Nachrichten nicht löschen: {e}")
        
        print("📝 Sende neue Role-Setup-Nachrichten...")
        
        # Hauptnachricht
        embed = discord.Embed(
            title="🌱 Grow a Garden Stock Benachrichtigungen",
            description="Wähle die Kategorien aus, für die du Benachrichtigungen erhalten möchtest:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Hauptkategorien:",
            value="• 🌱 **Alle Seeds** - Benachrichtigung für alle Samen\n• ⚒️ **Alle Gear** - Benachrichtigung für alle Ausrüstung\n• 🥚 **Alle Eggs** - Benachrichtigung für alle Eier\n• 🍯 **Alle Honey** - Benachrichtigung für alle Honig-Items\n• 🎨 **Alle Cosmetics** - Benachrichtigung für alle Kosmetik",
            inline=False
        )
        embed.add_field(
            name="⭐ Wichtigste Raritäten:",
            value="• **Seeds**: 🌈 Prismatic, ✨ Divine, 🔮 Mythical, 🏆 Legendary\n• **Eggs**: 🔮 Mythical, 🏆 Legendary, 🐛 Bug, 🌙 Night\n• **Gear**: 💧 Master Sprinkler, 💖 Friendship Pot, ✨ Divine, 🔮 Mythical\n• **Cosmetics**: 💎 Luxury, 📦 Crate Items\n• **Honey**: 🌻 Flower, 🐝 Bee, 🍯 Honey Items",
            inline=False
        )
        embed.add_field(
            name="💡 Tipp:",
            value="Verwende `!listroles` um alle 40+ verfügbaren Rollen zu sehen!\n🚨 Master Sprinkler & Friendship Pot = @everyone Alert!\nCustom Emojis werden automatisch von der Website geladen.",
            inline=False
        )
        embed.set_footer(text="Wähle aus den Dropdown-Menüs unten aus")
        
        await channel.send(embed=embed)
        await asyncio.sleep(1)
        
        # Seeds Dropdown
        seeds_embed = discord.Embed(
            title="🌱 Seeds Benachrichtigungen",
            description="Wähle Seeds-Raritäten für Benachrichtigungen:",
            color=discord.Color.green()
        )
        await channel.send(embed=seeds_embed, view=SeedsView())
        await asyncio.sleep(1)
        
        # Gear Dropdown
        gear_embed = discord.Embed(
            title="⚒️ Gear Benachrichtigungen", 
            description="Wähle Gear-Raritäten für Benachrichtigungen:",
            color=discord.Color.blue()
        )
        await channel.send(embed=gear_embed, view=GearView())
        await asyncio.sleep(1)
        
        # Eggs Dropdown
        eggs_embed = discord.Embed(
            title="🥚 Eggs Benachrichtigungen",
            description="Wähle Egg-Raritäten für Benachrichtigungen:",
            color=discord.Color.orange()
        )
        await channel.send(embed=eggs_embed, view=EggsView())
        await asyncio.sleep(1)
        
        # Honey Dropdown
        honey_embed = discord.Embed(
            title="🍯 Honey Benachrichtigungen",
            description="Wähle Honey-Kategorien für Benachrichtigungen:",
            color=discord.Color.gold()
        )
        await channel.send(embed=honey_embed, view=HoneyView())
        await asyncio.sleep(1)
        
        # Cosmetics Dropdown
        cosmetics_embed = discord.Embed(
            title="🎨 Cosmetics Benachrichtigungen",
            description="Wähle Cosmetics-Kategorien für Benachrichtigungen:",
            color=discord.Color.purple()
        )
        await channel.send(embed=cosmetics_embed, view=CosmeticsView())
        
        print("✅ Role-Setup-Nachrichten gesendet!")
    
    # Stock-Überwachung starten
    if not check_stock.is_running():
        check_stock.start()
    
    # Täglicher Emoji-Check starten
    if not daily_emoji_check.is_running():
        daily_emoji_check.start()
    
    print("🚀 Bot vollständig gestartet und bereit!")

@bot.command(name='stock')
async def manual_stock_check(ctx):
    """Manueller Stock-Check Command"""
    if ctx.author.guild_permissions.administrator:
        await ctx.send("🔄 Überprüfe Stock...")
        await check_stock()
        await ctx.send("✅ Stock-Check abgeschlossen!")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")

@bot.command(name='setup')
async def setup_roles(ctx):
    """Setup-Command für Rollen"""
    if ctx.author.guild_permissions.administrator:
        guild = ctx.guild
        created_roles = []
        
        # Hauptkategorie-Rollen
        main_role_configs = {
            'seeds_stock_notify': {'emoji': '🌱', 'color': discord.Color.green()},
            'gear_stock_notify': {'emoji': '⚒️', 'color': discord.Color.blue()},
            'eggs_stock_notify': {'emoji': '🥚', 'color': discord.Color.orange()},
            'honey_stock_notify': {'emoji': '🍯', 'color': discord.Color.gold()},
            'cosmetics_stock_notify': {'emoji': '🎨', 'color': discord.Color.purple()}
        }
        
        # Erstelle Hauptkategorie-Rollen
        for role_name, config in main_role_configs.items():
            if not discord.utils.get(guild.roles, name=role_name):
                try:
                    role = await guild.create_role(
                        name=role_name,
                        mentionable=True,
                        color=config['color'],
                        reason="Main category stock notification role"
                    )
                    created_roles.append(f"{config['emoji']} {role.name}")
                except Exception as e:
                    print(f"Fehler beim Erstellen der Rolle {role_name}: {e}")
        
        # Erstelle detaillierte Rollen
        for role_key, role_data in detailed_roles.items():
            role_name = f"{role_key}_stock_notify"
            if not discord.utils.get(guild.roles, name=role_name):
                try:
                    role = await guild.create_role(
                        name=role_name,
                        mentionable=True,
                        color=role_data['color'],
                        reason="Detailed stock notification role"
                    )
                    created_roles.append(f"{role_data['emoji']} {role.name}")
                except Exception as e:
                    print(f"Fehler beim Erstellen der Rolle {role_name}: {e}")
        
        if created_roles:
            # Aufteilen in mehrere Messages falls zu lang
            chunks = [created_roles[i:i+10] for i in range(0, len(created_roles), 10)]
            for i, chunk in enumerate(chunks):
                if i == 0:
                    await ctx.send(f"✅ **Rollen erstellt** ({len(created_roles)} total):\n" + "\n".join(chunk))
                else:
                    await ctx.send("**Weitere Rollen:**\n" + "\n".join(chunk))
        else:
            await ctx.send("ℹ️ Alle Rollen existieren bereits.")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")

@bot.command(name='channelsetup')
async def setup_channels(ctx):
    """Erstellt separate Channels für jede Stock-Kategorie"""
    if ctx.author.guild_permissions.administrator:
        guild = ctx.guild
        created_channels = []
        
        # Erstelle oder finde Kategorie für Stock-Channels
        category = discord.utils.get(guild.categories, name="🌱 Grow a Garden Stock")
        if not category:
            try:
                category = await guild.create_category("🌱 Grow a Garden Stock")
                await ctx.send(f"✅ Kategorie erstellt: {category.name}")
            except Exception as e:
                await ctx.send(f"❌ Fehler beim Erstellen der Kategorie: {e}")
                return
        
        channel_configs = {
            'gag-seeds-stock': {'emoji': '🌱', 'description': 'Samen Stock Updates'},
            'gag-gear-stock': {'emoji': '⚒️', 'description': 'Ausrüstung Stock Updates'},
            'gag-eggs-stock': {'emoji': '🥚', 'description': 'Eier Stock Updates'},
            'gag-honey-stock': {'emoji': '🍯', 'description': 'Honig Stock Updates'},
            'gag-cosmetics-stock': {'emoji': '🎨', 'description': 'Kosmetik Stock Updates'}
        }
        
        for channel_name, config in channel_configs.items():
            existing_channel = discord.utils.get(guild.channels, name=channel_name)
            if not existing_channel:
                try:
                    channel = await guild.create_text_channel(
                        name=channel_name,
                        category=category,
                        topic=config['description']
                    )
                    created_channels.append(f"{config['emoji']} {channel.mention}")
                    await ctx.send(f"✅ Channel erstellt: {channel.mention}")
                except Exception as e:
                    await ctx.send(f"❌ Fehler beim Erstellen des Channels {channel_name}: {e}")
            else:
                await ctx.send(f"ℹ️ Channel {existing_channel.mention} existiert bereits")
        
        if created_channels:
            await ctx.send(f"🎉 **Setup abgeschlossen!**\nErstelle Channels:\n" + "\n".join(created_channels))
        else:
            await ctx.send("ℹ️ Alle Channels existieren bereits.")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")

async def auto_download_emojis():
    """Lädt automatisch alle verfügbaren Item-Emojis von der Website herunter"""
    guild = bot.guilds[0] if bot.guilds else None
    if not guild:
        return
    
    print("🔄 Automatischer Emoji-Download gestartet...")
    
    # Check Server-Emoji-Limit
    server_emoji_count = len(guild.emojis)
    if server_emoji_count >= 50:
        print(f"⚠️ Server-Emoji-Limit erreicht ({server_emoji_count}/50)")
        print("💡 Verwende Bot-eigene Emojis stattdessen...")
        return await download_bot_emojis()
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            async with session.get(STOCK_URL, headers=headers) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Finde alle img-Tags in den Stock-Listen
                    img_tags = soup.find_all('img', src=True)
                    
                    downloaded_emojis = []
                    failed_emojis = []
                    
                    for img in img_tags:
                        img_src = img.get('src', '')
                        
                        # Überspringe externe Bilder und Icons
                        if not img_src.startswith('/images/') or 'icon' in img_src.lower():
                            continue
                        
                        # Extrahiere Item-Namen aus dem Pfad
                        item_filename = img_src.split('/')[-1]
                        item_name = item_filename.replace('.png', '').replace('.jpg', '').replace('.webp', '')
                        emoji_name = item_name.lower().replace('-', '_').replace(' ', '_')
                        
                        # Überspringe wenn Emoji bereits existiert
                        if discord.utils.get(guild.emojis, name=emoji_name):
                            continue
                        
                        # Checke Server-Emoji-Limit
                        if len(guild.emojis) >= 50:
                            print(f"⚠️ Server-Emoji-Limit erreicht während Download")
                            break
                        
                        try:
                            # Download Bild
                            full_url = f"https://vulcanvalues.com{img_src}"
                            async with session.get(full_url, headers=headers) as img_response:
                                if img_response.status == 200:
                                    image_data = await img_response.read()
                                    
                                    # Erstelle Emoji
                                    emoji = await guild.create_custom_emoji(
                                        name=emoji_name,
                                        image=image_data,
                                        reason="Auto-downloaded from stock website"
                                    )
                                    downloaded_emojis.append({
                                        'name': emoji_name,
                                        'original': item_name,
                                        'emoji': emoji
                                    })
                                    print(f"✅ {emoji_name} -> {emoji}")
                                    
                                    # Kleine Pause um Rate-Limits zu vermeiden
                                    await asyncio.sleep(0.5)
                                    
                                else:
                                    failed_emojis.append(f"{item_name} (HTTP {img_response.status})")
                                    
                        except Exception as e:
                            failed_emojis.append(f"{item_name} ({str(e)[:50]})")
                    
                    print(f"🎉 Emoji-Download abgeschlossen: {len(downloaded_emojis)} erfolgreich, {len(failed_emojis)} fehlgeschlagen")
                    return downloaded_emojis
                    
    except Exception as e:
        print(f"❌ Fehler beim automatischen Emoji-Download: {e}")
        return []

async def download_bot_emojis():
    """Alternative: Verwendet Bot-Application-Emojis (wenn Server-Limit erreicht)"""
    print("🤖 Verwende Bot-eigene Emoji-Fallbacks...")
    
    # Erstelle ein Dictionary mit Item-Name-Mappings zu Standard-Emojis
    bot_emoji_mapping = {
        # Seeds
        'carrot': '🥕',
        'corn': '🌽', 
        'bamboo': '🎋',
        'strawberry': '🍓',
        'grape': '🍇',
        'tomato': '🍅',
        'blueberry': '🫐',
        'watermelon': '🍉',
        'pumpkin': '🎃',
        'apple': '🍎',
        'coconut': '🥥',
        'cactus': '🌵',
        'mushroom': '🍄',
        'pepper': '🌶️',
        'pineapple': '🍍',
        'peach': '🍑',
        'banana': '🍌',
        'lemon': '🍋',
        
        # Gear
        'trowel': '🛠️',
        'watering_can': '🚿',
        'harvest_tool': '⚒️',
        'lightning_rod': '⚡',
        'sprinkler': '💧',
        
        # Eggs
        'egg': '🥚',
        'rare_egg': '💎',
        'bug_egg': '🐛',
        'common_egg': '🥚',
        
        # Honey
        'honey': '🍯',
        'bee': '🐝',
        'flower': '🌻',
        'lavender': '💜',
        
        # Cosmetics
        'torch': '🔥',
        'bench': '🪑',
        'table': '🪑',
        'well': '🪣',
        'tree': '🌳',
        'stone': '🗿'
    }
    
    # Speichere das Mapping in einer globalen Variable
    global emoji_fallbacks
    emoji_fallbacks = bot_emoji_mapping
    
    print(f"✅ {len(bot_emoji_mapping)} Bot-Emoji-Fallbacks geladen")
    return []

def get_item_emoji(guild, item_name):
    """Findet das passende Emoji für ein Item (Server oder Bot-Fallback)"""
    if not guild:
        return get_fallback_emoji(item_name)
    
    # Verschiedene Varianten des Item-Namens ausprobieren
    search_variants = [
        item_name.lower().replace(' ', '_').replace('-', '_'),
        item_name.lower().replace(' ', '').replace('-', ''),
        item_name.lower().replace(' ', '-').replace('_', '-'),
        ''.join(item_name.lower().split()),
    ]
    
    # Erst Server-Emojis suchen
    for variant in search_variants:
        emoji = discord.utils.get(guild.emojis, name=variant)
        if emoji:
            return emoji
    
    # Fallback zu Bot-Emojis
    return get_fallback_emoji(item_name)

def get_fallback_emoji(item_name):
    """Gibt Fallback-Emojis für Items zurück"""
    global emoji_fallbacks
    if 'emoji_fallbacks' not in globals():
        return None
    
    # Suche nach passenden Fallback-Emojis
    item_lower = item_name.lower()
    
    # Direkte Mappings
    for key, emoji in emoji_fallbacks.items():
        if key in item_lower:
            return emoji
    
    # Fallback basierend auf Wort-Teilen
    for word in item_lower.split():
        for key, emoji in emoji_fallbacks.items():
            if word in key or key in word:
                return emoji
    
    return None

@bot.command(name='currentstock', aliases=['stocks', 'current'])
async def show_current_stock(ctx):
    """Zeigt alle aktuell verfügbaren Stocks an"""
    await ctx.send("🔄 Lade aktuelle Stock-Daten...")
    
    current_stock = await fetch_stock_data()
    
    if not current_stock:
        embed = discord.Embed(
            title="❌ Fehler beim Laden der Stock-Daten",
            description="Die Website konnte nicht erreicht werden oder die Daten konnten nicht gelesen werden.",
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)
        return
    
    if not current_stock:
        embed = discord.Embed(
            title="📦 Aktueller Stock",
            description="Keine Items im Stock gefunden.",
            color=discord.Color.orange()
        )
        await ctx.send(embed=embed)
        return
    
    # Items nach Kategorien sortieren
    categories = {
        'Seeds': [],
        'Gear': [],
        'Eggs': [],
        'Honey': [],
        'Cosmetics': [],
        'Special Items': []
    }
    
    for item_name, item_data in current_stock.items():
        category = item_data.get('category', 'Special Items')
        quantity = item_data.get('quantity', 1)
        
        categories[category].append(f"{item_name} (x{quantity})")
    
    # Erstelle Embed mit kategorisierten Items
    embed = discord.Embed(
        title="📦 Aktueller Grow a Garden Stock",
        description=f"Letztes Update: <t:{int(datetime.now().timestamp())}:R>",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    total_items = sum(len(items) for items in categories.values())
    embed.add_field(
        name="📊 Übersicht",
        value=f"**{total_items}** Items insgesamt verfügbar",
        inline=False
    )
    
    # Emoji-Mapping für Kategorien
    category_emojis = {
        'Seeds': '🌱',
        'Gear': '⚒️',
        'Eggs': '🥚',
        'Honey': '🍯',
        'Cosmetics': '🎨',
        'Special Items': '✨'
    }
    
    # Füge Kategorien mit Items hinzu
    for category, items in categories.items():
        if items:
            emoji = category_emojis.get(category, '📦')
            item_list = '\n'.join([f"• {item}" for item in items[:10]])  # Max 10 items per category
            
            if len(items) > 10:
                item_list += f"\n... und {len(items) - 10} weitere"
            
            embed.add_field(
                name=f"{emoji} {category} ({len(items)})",
                value=item_list if item_list else "Keine Items",
                inline=True
            )
    
    embed.set_footer(text="Stock Monitor Bot • Verwende !stock für manuellen Check")
    
    await ctx.send(embed=embed)

@bot.command(name='rawstock', aliases=['raw'])
async def show_raw_stock(ctx):
    """Zeigt die rohen Stock-Daten für Debugging"""
    if ctx.author.guild_permissions.administrator:
        await ctx.send("🔄 Lade rohe Stock-Daten...")
        
        current_stock = await fetch_stock_data()
        
        if not current_stock:
            await ctx.send("❌ Keine Daten empfangen.")
            return
        
        # Erstelle eine einfache Liste aller gefundenen Items
        items_text = "**Gefundene Items:**\n"
        for i, (item_name, item_data) in enumerate(current_stock.items(), 1):
            items_text += f"{i}. {item_name}\n"
            if len(items_text) > 1800:  # Discord character limit
                items_text += "... (weitere Items abgeschnitten)"
                break
        
        embed = discord.Embed(
            title="🔍 Rohe Stock-Daten (Debug)",
            description=items_text,
            color=discord.Color.blue()
        )
        embed.add_field(name="Anzahl Items", value=str(len(current_stock)), inline=True)
        embed.add_field(name="Timestamp", value=f"<t:{int(datetime.now().timestamp())}:F>", inline=True)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send("❌ Nur Administratoren können rohe Daten anzeigen.")

@bot.command(name='listroles')
async def list_roles(ctx):
    """Zeigt alle verfügbaren Stock-Rollen an"""
    guild = ctx.guild
    
    embed = discord.Embed(
        title="🎭 Verfügbare Stock-Rollen",
        description="Alle Rollen für Stock-Benachrichtigungen:",
        color=discord.Color.blue()
    )
    
    # Hauptkategorien
    main_roles = []
    for category in ['Seeds', 'Gear', 'Eggs', 'Honey', 'Cosmetics']:
        role_name = f"{category.lower()}_stock_notify"
        role = discord.utils.get(guild.roles, name=role_name)
        emoji_map = {'Seeds': '🌱', 'Gear': '⚒️', 'Eggs': '🥚', 'Honey': '🍯', 'Cosmetics': '🎨'}
        emoji = emoji_map[category]
        
        if role:
            main_roles.append(f"{emoji} {role.mention} - Alle {category}")
        else:
            main_roles.append(f"{emoji} `{role_name}` - ❌ Nicht erstellt")
    
    embed.add_field(
        name="📋 Hauptkategorien:",
        value="\n".join(main_roles),
        inline=False
    )
    
    # Detaillierte Rollen nach Kategorie gruppiert
    categories = {}
    for role_key, role_data in detailed_roles.items():
        category = role_data['category']
        if category not in categories:
            categories[category] = []
        
        role_name = f"{role_key}_stock_notify"
        role = discord.utils.get(guild.roles, name=role_name)
        emoji = role_data['emoji']
        
        if role:
            categories[category].append(f"{emoji} {role.mention}")
        else:
            categories[category].append(f"{emoji} `{role_name}` ❌")
    
    for category, roles in categories.items():
        embed.add_field(
            name=f"⭐ {category} Raritäten:",
            value="\n".join(roles[:5]),  # Limit to 5 per field
            inline=True
        )
        
        # If more than 5 roles, add another field
        if len(roles) > 5:
            embed.add_field(
                name=f"⭐ {category} (Fortsetzung):",
                value="\n".join(roles[5:]),
                inline=True
            )
    
    embed.set_footer(text="✅ = Rolle existiert | ❌ = Rolle fehlt (verwende !setup)")
    
    await ctx.send(embed=embed)
    """Testet die Benachrichtigungen für eine Kategorie"""
    if ctx.author.guild_permissions.administrator:
        if not category:
            await ctx.send("❌ Bitte gib eine Kategorie an: `seeds`, `gear`, `eggs`, `honey`, `cosmetics`")
            return
        
        category = category.capitalize()
        if category not in ['Seeds', 'Gear', 'Eggs', 'Honey', 'Cosmetics']:
            await ctx.send("❌ Ungültige Kategorie. Verfügbar: `seeds`, `gear`, `eggs`, `honey`, `cosmetics`")
            return
        
        # Erstelle Test-Item-Daten
        test_items = [
            ("Test Item 1", {'category': category, 'quantity': 5}),
            ("Test Item 2", {'category': category, 'quantity': 2})
        ]
        
        await send_category_stock_update(category, test_items)
        await ctx.send(f"✅ Test-Benachrichtigung für **{category}** gesendet!")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")

@bot.command(name='cleanup')
async def cleanup_messages(ctx):
    """Löscht alle Bot-Nachrichten im aktuellen Channel"""
    if ctx.author.guild_permissions.administrator:
        deleted_count = 0
        await ctx.send("🧹 Lösche Bot-Nachrichten...")
        
        try:
            async for message in ctx.channel.history(limit=100):
                if message.author == bot.user:
                    try:
                        await message.delete()
                        deleted_count += 1
                        await asyncio.sleep(0.5)  # Rate limiting
                    except:
                        pass
            
            await ctx.send(f"✅ {deleted_count} Bot-Nachrichten gelöscht!", delete_after=5)
            
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Löschen: {e}")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")

@bot.command(name='resetroles')  
async def reset_role_messages(ctx):
    """Löscht alte Role-Messages und sendet neue"""
    if ctx.author.guild_permissions.administrator:
        channel = bot.get_channel(ROLE_CHANNEL_ID)
        if not channel:
            await ctx.send("❌ Role-Channel nicht gefunden!")
            return
            
        await ctx.send("🔄 Aktualisiere Role-Setup-Nachrichten...")
        
        # Lösche alte Bot-Nachrichten im Role-Channel
        deleted_count = 0
        try:
            async for message in channel.history(limit=100):
                if message.author == bot.user:
                    try:
                        await message.delete()
                        deleted_count += 1
                        await asyncio.sleep(0.5)
                    except:
                        pass
        except Exception as e:
            await ctx.send(f"⚠️ Konnte nicht alle Nachrichten löschen: {e}")
        
        # Sende neue Messages
        # Hauptnachricht
        embed = discord.Embed(
            title="🌱 Grow a Garden Stock Benachrichtigungen",
            description="Wähle die Kategorien aus, für die du Benachrichtigungen erhalten möchtest:",
            color=discord.Color.green()
        )
        embed.add_field(
            name="📋 Hauptkategorien:",
            value="• 🌱 **Alle Seeds** - Benachrichtigung für alle Samen\n• ⚒️ **Alle Gear** - Benachrichtigung für alle Ausrüstung\n• 🥚 **Alle Eggs** - Benachrichtigung für alle Eier\n• 🍯 **Alle Honey** - Benachrichtigung für alle Honig-Items\n• 🎨 **Alle Cosmetics** - Benachrichtigung für alle Kosmetik",
            inline=False
        )
        embed.add_field(
            name="⭐ Wichtigste Raritäten:",
            value="• **Seeds**: 🌈 Prismatic, ✨ Divine, 🔮 Mythical, 🏆 Legendary\n• **Eggs**: 🔮 Mythical, 🏆 Legendary, 🐛 Bug, 🌙 Night\n• **Gear**: 💧 Master Sprinkler, 💖 Friendship Pot, ✨ Divine, 🔮 Mythical\n• **Cosmetics**: 💎 Luxury, 📦 Crate Items\n• **Honey**: 🌻 Flower, 🐝 Bee, 🍯 Honey Items",
            inline=False
        )
        embed.set_footer(text="Wähle aus den Dropdown-Menüs unten aus")
        
        await channel.send(embed=embed)
        await asyncio.sleep(1)
        
        # Dropdowns
        await channel.send(embed=discord.Embed(title="🌱 Seeds", color=discord.Color.green()), view=SeedsView())
        await asyncio.sleep(1)
        await channel.send(embed=discord.Embed(title="⚒️ Gear", color=discord.Color.blue()), view=GearView())
        await asyncio.sleep(1)
        await channel.send(embed=discord.Embed(title="🥚 Eggs", color=discord.Color.orange()), view=EggsView())
        await asyncio.sleep(1)
        await channel.send(embed=discord.Embed(title="🍯 Honey", color=discord.Color.gold()), view=HoneyView())
        await asyncio.sleep(1)
        await channel.send(embed=discord.Embed(title="🎨 Cosmetics", color=discord.Color.purple()), view=CosmeticsView())
        
        await ctx.send(f"✅ Role-Setup aktualisiert! {deleted_count} alte Nachrichten gelöscht.")
    else:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")
    """Zeigt alle verfügbaren Commands"""
    embed = discord.Embed(
        title="🤖 Grow a Garden Stock Bot Commands",
        description="Alle verfügbaren Befehle:",
        color=discord.Color.blue()
    )
    
    admin_commands = [
        "`!channelsetup` - Erstellt kategorie-spezifische Channels",
        "`!setup` - Erstellt alle Haupt-Rollen mit Farben",
        "`!updateemojis` - Lädt neue Custom Emojis von der Website",
        "`!cleanup` - Löscht alle Bot-Nachrichten im Channel",
        "`!resetroles` - Aktualisiert Role-Setup-Nachrichten",
        "`!rawstock` - Zeigt Debug-Informationen der Website",
        "`!testnotify <kategorie>` - Testet Benachrichtigungen"
    ]
    
    public_commands = [
        "`!currentstock` - Zeigt aktuelle Stocks kategorisiert",
        "`!listroles` - Übersicht aller verfügbaren Rollen",
        "`!help` - Zeigt diese Hilfe"
    ]
    
    embed.add_field(
        name="👑 Admin Commands:",
        value="\n".join(admin_commands),
        inline=False
    )
    
    embed.add_field(
        name="👥 Public Commands:",
        value="\n".join(public_commands),
        inline=False
    )
    
    embed.add_field(
        name="🤖 Automatische Features:",
        value="• Stock-Monitoring alle 5 Minuten\n• Automatischer Emoji-Download beim Start\n• Täglicher Check auf neue Emojis\n• Intelligente Emoji-Erkennung in Benachrichtigungen",
        inline=False
    )
    
    embed.set_footer(text="Grow a Garden Stock Bot • Automatisch und immer aktuell")
    
    await ctx.send(embed=embed)
    """Erstellt eine spezifische Rolle manuell"""
    if not ctx.author.guild_permissions.administrator:
        await ctx.send("❌ Du benötigst Administrator-Rechte für diesen Befehl.")
        return
    
    if not role_name:
        available_roles = list(detailed_roles.keys())
        chunk_size = 10
        chunks = [available_roles[i:i+chunk_size] for i in range(0, len(available_roles), chunk_size)]
        
        embed = discord.Embed(
            title="📝 Verfügbare Rollen",
            description="Verwende `!createrole <rolle>` um eine spezifische Rolle zu erstellen:",
            color=discord.Color.blue()
        )
        
        for i, chunk in enumerate(chunks):
            role_list = "\n".join([f"• `{role}`" for role in chunk])
            embed.add_field(
                name=f"Rollen {i*chunk_size+1}-{min((i+1)*chunk_size, len(available_roles))}:",
                value=role_list,
                inline=True
            )
        
        await ctx.send(embed=embed)
        return
    
    # Rolle erstellen
    role_key = role_name.lower().replace(' ', '_')
    full_role_name = f"{role_key}_stock_notify"
    
    guild = ctx.guild
    existing_role = discord.utils.get(guild.roles, name=full_role_name)
    
    if existing_role:
        await ctx.send(f"ℹ️ Rolle {existing_role.mention} existiert bereits!")
        return
    
    if role_key in detailed_roles:
        role_data = detailed_roles[role_key]
        try:
            role = await guild.create_role(
                name=full_role_name,
                mentionable=True,
                color=role_data['color'],
                reason=f"Spezifische Stock-Rolle erstellt von {ctx.author}"
            )
            await ctx.send(f"✅ Rolle erstellt: {role_data['emoji']} {role.mention}")
        except Exception as e:
            await ctx.send(f"❌ Fehler beim Erstellen der Rolle: {e}")
    else:
        await ctx.send(f"❌ Rolle `{role_key}` nicht gefunden! Verwende `!createrole` ohne Parameter für eine Liste.")

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    print(f"Command error: {error}")

# Bot starten
if __name__ == "__main__":
    bot.run(TOKEN)