# 🚀 Raspberry Pi Update - Selenium ARM-Fix

## Problem gelöst
Der Bot versuchte x86-ChromeDriver auf ARM-Architektur zu verwenden → **Exec format error**

## Lösung implementiert
- ✅ **Plattform-Detection**: Automatische Erkennung Windows vs. Linux
- ✅ **ARM-kompatibel**: Verwendet System-ChromeDriver auf Raspberry Pi
- ✅ **Fallback-Mechanismus**: WebDriver-Manager als Backup
- ✅ **Optimierungen**: Raspberry Pi spezifische Chrome-Optionen

## Update-Befehle für Raspberry Pi

```bash
# 1. Bot stoppen
sudo systemctl stop discord-bot.service

# 2. Zum Bot-Verzeichnis
cd /home/stefan/grow-a-garden-bot

# 3. Git-Update
git fetch origin
git pull origin feat/selenium-cloudflare-fix

# 4. Bot testen
source venv/bin/activate
python3 gag-aleart.py
```

## Erwartete Ausgabe nach Update

```
🔧 Initialisiere Chrome WebDriver für Linux/Raspberry Pi...
✅ Chrome/Chromium gefunden: /usr/bin/chromium-browser
✅ ChromeDriver gefunden: /usr/bin/chromedriver
🔧 Verwende System-ChromeDriver: /usr/bin/chromedriver
✅ Chrome WebDriver erfolgreich initialisiert (Linux/Raspberry Pi)
```

## Nach erfolgreichem Test

```bash
# Bot als Service starten
sudo systemctl start discord-bot.service
sudo systemctl status discord-bot.service
```

## Troubleshooting

### Falls ChromeDriver fehlt:
```bash
sudo apt update
sudo apt install chromium-chromedriver
```

### Falls Chromium fehlt:
```bash
sudo apt install chromium-browser
```

### Bei Memory-Problemen:
```bash
# Swap-Datei vergrößern
sudo dphys-swapfile swapoff
sudo nano /etc/dphys-swapfile
# CONF_SWAPSIZE=1024
sudo dphys-swapfile setup
sudo dphys-swapfile swapon
```

---
**Status**: READY FOR RASPBERRY PI DEPLOYMENT ✅
