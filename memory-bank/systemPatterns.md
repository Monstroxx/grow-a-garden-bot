# System Patterns: Grow a Garden Stock Bot

## Architecture Overview
```
Web Scraper → Stock Analyzer → Role Dispatcher → Channel Manager → Notification Sender
     ↓              ↓              ↓              ↓              ↓
VulcanValues  → Item Categories → Target Roles → Target Channels → Discord Messages
```

## Key Technical Decisions

### 1. Multi-Channel Architecture
- **Decision**: Separate Channels für jede Hauptkategorie
- **Rationale**: Verhindert Spam, ermöglicht spezifische Benachrichtigungen
- **Implementation**: `CATEGORY_CHANNELS` Dictionary mapping

### 2. Dual-Role System
- **Decision**: Haupt-Rolle + Spezifische Rarität gleichzeitig erwähnen
- **Rationale**: Flexibilität für Benutzer (allgemein oder spezifisch)
- **Pattern**: `@seeds_stock_notify @divine_seeds_stock_notify`

### 3. Dropdown-basierte Rollenauswahl
- **Decision**: 4 separate Dropdown-Menüs statt Commands
- **Rationale**: Discord 25-Item-Limit umgehen, benutzerfreundlicher
- **Implementation**: Multiple `discord.ui.Select` Komponenten

### 4. Stock Change Detection
- **Decision**: Compare current vs. previous stock state
- **Rationale**: Nur bei tatsächlichen Änderungen benachrichtigen
- **Pattern**: `previous_stock` global variable

## Component Relationships

### Stock Monitor
- **Responsibility**: VulcanValues Website scraping
- **Frequency**: Alle 5 Minuten via `@tasks.loop`
- **Output**: Parsed item data mit Kategorien

### Role Manager
- **Responsibility**: Discord Rollen erstellen/verwalten
- **Commands**: `!setup`, `!resetroles`
- **Pattern**: Hierarchische Rollen (Haupt → Spezifisch)

### Channel Manager
- **Responsibility**: Kategorie-spezifische Channels erstellen
- **Command**: `!channelsetup`
- **Pattern**: Naming convention mit Kategorie-Prefix

### Emoji Manager
- **Responsibility**: Custom Emojis von Website laden
- **Command**: `!addemojis`, `!updateemojis`
- **Pattern**: Emoji-Name basiert auf Item-Name

## Critical Implementation Paths

### Stock Update Flow
1. `check_stock()` scraped VulcanValues
2. `analyze_stock_changes()` erkennt Änderungen
3. `notify_category()` sendet kategorisierte Updates
4. Custom Emojis und Rollen-Mentions eingebettet

### Rarität Detection
- Seeds: Wiki-basierte Rarität-Zuordnung
- Eggs: Preis-basierte Kategorisierung
- Gear: Item-Name Pattern Recognition
- Cosmetics: Preis-Tiers (Luxury > Premium > Basic > Cheap)

### Error Handling Pattern
- Try-catch für Website-Scraping
- Fallback bei fehlenden Emojis
- Graceful degradation bei Channel-Fehlern