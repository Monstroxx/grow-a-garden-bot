# 🌱 Grow a Garden Stock Bot

Ein Discord Bot, der automatisch Stock-Updates von Grow a Garden überwacht und Benachrichtigungen sendet.

## 🚀 Features

- **Automatisches Stock-Monitoring**: Überprüft alle 5 Minuten die Website auf neue Items
- **40+ Raritäts-Rollen**: Von Common bis Prismatic Seeds, alle Egg-Typen, Gear-Raritäten
- **Kategorisierte Channels**: Separate Channels für Seeds, Gear, Eggs, Honey, Cosmetics
- **Intelligente Benachrichtigungen**: Mehrfach-Mentions für Haupt- und Spezial-Rollen
- **Custom Emojis**: Lädt Item-Bilder von der Website als Server-Emojis
- **Mehrfach-Dropdowns**: 4 separate Dropdown-Menüs für einfache Rollenauswahl

## 📋 Setup

### 1. Dependencies installieren
```bash
pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren
Erstelle eine `.env` Datei:
```env
DISCORD_TOKEN=dein_bot_token_hier
ROLE_CHANNEL_ID=channel_id_für_rollen_auswahl
STOCK_URL=https://vulcanvalues.com/grow-a-garden/stock
```

### 3. Bot starten
```bash
python gag-aleart.py
```

### 4. Discord Setup Commands
```discord
!channelsetup    # Erstellt 5 kategorie-spezifische Channels
!setup           # Erstellt alle Haupt-Rollen
!addemojis       # Lädt 30+ Custom Emojis von der Website
```

## 🎭 Verfügbare Rollen

### Seeds (7 Raritäten)
- 🌈 Prismatic Seeds (Beanstalk)
- ✨ Divine Seeds (Grape, Mushroom, etc.)
- 🔮 Mythical Seeds (Coconut, Dragon Fruit, etc.)
- 🏆 Legendary Seeds (Watermelon, Pumpkin, etc.)
- 🌺 Rare Seeds (Tomato, Corn, etc.)
- 🌾 Uncommon Seeds (Blueberry, Tulip, etc.)
- 🌱 Common Seeds (Carrot, Strawberry)

### Eggs (7 Raritäten)
- 🌙 Night Egg (Event-exklusiv)
- 🐛 Bug Egg (50M¢, 3% Stock-Chance)
- 🔮 Mythical Egg (8M¢, 7% Stock-Chance)
- 🏆 Legendary Egg (3M¢, 12% Stock-Chance)
- 💎 Rare Egg (600k¢, 24% Stock-Chance)
- 🐣 Uncommon Egg (150k¢, 54% Stock-Chance)
- 🥚 Common Egg (50k¢, 99% Stock-Chance)

### Gear (5 Raritäten)
- ✨ Divine Gear (Harvest Tool, Master Sprinkler, etc.)
- 🔮 Mythical Gear (Lightning Rod, Godly Sprinkler, etc.)
- 🏆 Legendary Gear (Advanced Sprinkler, Star Caller, etc.)
- 🌺 Rare Gear (Basic Sprinkler)
- 🔧 Common Gear (Trowel, Watering Can, etc.)

### Cosmetics (5 Kategorien)
- 💎 Luxury Cosmetics (50M+¢ Items wie Wells, Tractors)
- 🏗️ Premium Cosmetics (10M-50M¢ Items)
- 🪑 Basic Cosmetics (1M-10M¢ Items)
- 🎨 Cheap Cosmetics (Unter 1M¢)
- 📦 Crate Cosmetics (Gnome/Sign/Fun Crates)

### Honey (3 Kategorien)
- 🍯 Honey Items (Honey Comb, etc.)
- 🐝 Bee Items (Bee Chair, etc.)
- 🌻 Flower Items (Flower Seed Pack, Lavender, etc.)

## 🔧 Commands

### Admin Commands
- `!channelsetup` - Erstellt kategorie-spezifische Channels
- `!setup` - Erstellt alle Haupt-Rollen
- `!addemojis` - Lädt Custom Emojis von der Website
- `!rawstock` - Zeigt Debug-Informationen
- `!testnotify <kategorie>` - Testet Benachrichtigungen
- `!resetroles` - Role-Messages aktualisieren
- `!stock` - Manueller Stock-Check
+ `!updateemojis` - Emojis herunterladen

### Public Commands
- `!currentstock` - Zeigt aktuelle Stocks kategorisiert
- `!listroles` - Zeigt alle verfügbaren Rollen
- `!help` - Hilfe anzeigen

## 🏗️ Architektur

- **Stock-Monitoring**: Scraping der vulcanvalues.com Website alle 5 Minuten
- **Kategorisierte Channels**: Separate Channels für jede Hauptkategorie
- **Intelligente Rarität-Erkennung**: Basierend auf offiziellem Grow a Garden Wiki
- **Doppelte Benachrichtigungen**: Haupt-Rolle + Spezifische Rarität gleichzeitig erwähnt
- **Mehrfach-Dropdown-System**: 4 separate Dropdowns um Discord's 25-Item-Limit zu umgehen

## 📊 Stock Update Beispiel

```
In #gag-seeds-stock:
@seeds_stock_notify @divine_seeds_stock_notify

🌱 Seeds Stock Update!
Neue Items im Seeds Shop verfügbar:

✨ Grape (x3) - Divine Seeds
🔮 Dragon Fruit (x1) - Mythical Seeds
```

## 🔐 Sicherheit

- Token in `.env` Datei (nicht im Code)
- `.gitignore` schützt sensible Daten
- Kein Hardcoding von Credentials

## 🌐 Links

- [Grow a Garden Official](https://growagarden.gg/)
- [VulcanValues Stock](https://vulcanvalues.com/grow-a-garden/stock)
- [Grow a Garden Wiki](https://growagarden.fandom.com/wiki/Grow_a_Garden_Wiki)
