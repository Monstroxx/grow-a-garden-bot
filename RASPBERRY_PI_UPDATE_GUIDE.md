# 🚀 Raspberry Pi Bot-Update Anleitung

## Schritt-für-Schritt Anleitung

### 1. PuTTY öffnen
1. Starte PuTTY: `C:\Users\jonas\Desktop\putty.exe`
2. Konfiguration:
   - **Host Name**: `stefan@192.168.171.100`
   - **Port**: `22`
   - **Connection Type**: `SSH`
3. SSH -> Auth -> Private key: `C:\Users\jonas\Desktop\ssh-keys\putty.privat.pihole.ppk`
4. Klicke **Open**

### 2. Bot-Status prüfen
```bash
sudo systemctl status discord-bot.service
```

### 3. Alten Bot stoppen
```bash
sudo systemctl stop discord-bot.service
```

### 4. Zum Bot-Verzeichnis navigieren
```bash
cd /home/stefan
ls -la | grep bot
cd grow-a-garden-bot
```

### 5. GitHub Repository aktualisieren
```bash
# Hole neueste Änderungen
git fetch origin

# Wechsle zum Feature-Branch
git checkout feat/selenium-cloudflare-fix

# Hole Updates
git pull origin feat/selenium-cloudflare-fix
```

### 6. Dependencies installieren
```bash
pip3 install -r requirements.txt
```

### 7. Bot neu starten
```bash
sudo systemctl start discord-bot.service
```

### 8. Status prüfen
```bash
sudo systemctl status discord-bot.service
```

## 🔧 Erwartete Ausgaben

### Bei `git checkout feat/selenium-cloudflare-fix`:
```
Switched to branch 'feat/selenium-cloudflare-fix'
```

### Bei `pip3 install -r requirements.txt`:
```
Installing collected packages: selenium, webdriver-manager
Successfully installed selenium-4.x.x webdriver-manager-4.x.x
```

### Bei `systemctl status discord-bot.service`:
```
● discord-bot.service - Discord Stock Bot
   Loaded: loaded
   Active: active (running)
```

## ⚠️ Mögliche Probleme

### 1. Chrome nicht installiert
Falls Fehler mit Chrome WebDriver:
```bash
# Chrome installieren
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable
```

### 2. Selenium-Dependencies fehlen
```bash
sudo apt install chromium-chromedriver
```

### 3. Bot startet nicht
```bash
# Logs anschauen
sudo journalctl -u discord-bot.service -f
```

## 🎯 Nach dem Update

Der Bot wird dann:
- ✅ Cloudflare-Protection umgehen
- ✅ Stock-Updates von VulcanValues holen
- ✅ Discord-Benachrichtigungen senden
- ⏱️ Längere Wartezeiten (60-90s statt 5s)

## 🔄 Rollback falls Probleme

Falls der neue Bot nicht funktioniert:
```bash
# Zurück zum alten Branch
git checkout master
sudo systemctl restart discord-bot.service
```

---
**Tipp**: Führe die Befehle einzeln aus und prüfe die Ausgaben!
