# 🚀 Quick Setup Guide

## 1. Clone Repository
```bash
git clone <repository-url>
cd projekte
```

## 2. Install Dependencies
```bash
pip install -r requirements.txt
```

## 3. Configure Environment
1. Kopiere `.env.example` zu `.env`
2. Füge deinen Discord Bot Token ein
3. Setze die Channel ID für Rollenauswahl

```env
DISCORD_TOKEN=dein_bot_token_hier
ROLE_CHANNEL_ID=1234567890123456789
STOCK_URL=https://vulcanvalues.com/grow-a-garden/stock
```

## 4. Start Bot
```bash
python gag-aleart.py
```

## 5. Discord Setup
```discord
!channelsetup    # Erstellt Channels
!setup           # Erstellt Rollen
!addemojis       # Lädt Emojis
```

## ✅ Ready!
Der Bot überwacht jetzt automatisch Grow a Garden Stocks und sendet Benachrichtigungen in die entsprechenden Channels.
