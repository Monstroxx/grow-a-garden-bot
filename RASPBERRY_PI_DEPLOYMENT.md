# Deployment Guide für Grow a Garden Bot auf Raspberry Pi

## 🚀 Schritt-für-Schritt Deployment

### 1. SSH-Verbindung zum Pi herstellen
```bash
# Öffne PuTTY oder verwende:
ssh stefan@192.168.171.100
```

### 2. Aktuellen Bot-Status prüfen
```bash
sudo systemctl status discord-bot.service
sudo systemctl stop discord-bot.service
```

### 3. Backup des alten Bots erstellen
```bash
cd /home/stefan
cp -r grow-a-garden-bot grow-a-garden-bot-backup-$(date +%Y%m%d)
```

### 4. Neue Bot-Version hochladen
**Auf Windows (lokale Maschine):**
```bash
# Verwende WinSCP oder
scp -r C:\Users\jonas\Desktop\projekte\grow-a-garden-bot stefan@192.168.171.100:/home/stefan/grow-a-garden-bot-new
```

### 5. Chrome installieren (falls nicht vorhanden)
```bash
# Auf Raspberry Pi:
wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt update
sudo apt install google-chrome-stable -y

# Oder Chromium (empfohlen für Pi):
sudo apt update
sudo apt install chromium-browser chromium-chromedriver -y
```

### 6. Dependencies installieren
```bash
cd /home/stefan/grow-a-garden-bot-new
pip3 install -r requirements.txt

# Falls Probleme mit Selenium:
pip3 install selenium webdriver-manager --upgrade
```

### 7. Konfiguration übertragen
```bash
# Kopiere .env vom alten Bot
cp /home/stefan/grow-a-garden-bot/.env /home/stefan/grow-a-garden-bot-new/.env
```

### 8. Bot-Service aktualisieren
```bash
# Stoppe alten Service
sudo systemctl stop discord-bot.service

# Backup der Service-Datei
sudo cp /etc/systemd/system/discord-bot.service /etc/systemd/system/discord-bot.service.backup

# Aktualisiere Service-Pfad (falls nötig)
sudo nano /etc/systemd/system/discord-bot.service

# Content sollte sein:
[Unit]
Description=Grow a Garden Discord Bot
After=network.target

[Service]
Type=simple
User=stefan
WorkingDirectory=/home/stefan/grow-a-garden-bot-new
Environment=PYTHONPATH=/home/stefan/grow-a-garden-bot-new
ExecStart=/usr/bin/python3 /home/stefan/grow-a-garden-bot-new/gag-aleart.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 9. Service neustarten
```bash
sudo systemctl daemon-reload
sudo systemctl start discord-bot.service
sudo systemctl enable discord-bot.service
sudo systemctl status discord-bot.service
```

### 10. Logs überwachen
```bash
# Live-Logs ansehen
sudo journalctl -u discord-bot.service -f

# Letzten Logs
sudo journalctl -u discord-bot.service -n 50
```

## 🔧 Chromium-Konfiguration für Raspberry Pi

Falls Chrome/Chromium-Probleme auftreten, editiere `gag-aleart.py`:

```python
# In setup_chrome_driver() Funktion:
chrome_paths = [
    "/usr/bin/chromium-browser",  # Raspberry Pi
    "/usr/bin/google-chrome",     # Standard Chrome
    "/usr/bin/chromium",          # Alternative
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",  # Windows
]
```

## 🐛 Troubleshooting

### Selenium-Probleme:
```bash
# Chromium manuell testen
chromium-browser --version
which chromium-browser

# ChromeDriver testen
chromedriver --version
```

### Service-Probleme:
```bash
# Detaillierte Logs
sudo journalctl -u discord-bot.service --since "1 hour ago"

# Manual test
cd /home/stefan/grow-a-garden-bot-new
python3 gag-aleart.py
```

### Selenium auf Pi optimieren:
In `gag-aleart.py` zusätzliche Optionen:
```python
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage") 
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--remote-debugging-port=9222")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--disable-plugins")
chrome_options.add_argument("--disable-images")
chrome_options.add_argument("--memory-pressure-off")
```

## ✅ Erfolgreich deployed!

Nach dem Deployment sollte der Bot:
- ✅ Automatisch alle 5 Minuten Stock-Updates checken
- ✅ Cloudflare-Challenges umgehen
- ✅ Discord-Benachrichtigungen senden
- ✅ Bei Problemen automatisch restarten
