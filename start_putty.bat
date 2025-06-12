@echo off
echo 🚀 Starte PuTTY für Raspberry Pi Bot-Update...
echo.
echo Konfiguration:
echo - Host: stefan@192.168.171.100:22
echo - Key: putty.privat.pihole.ppk
echo.
echo Nach dem Verbinden, führe diese Befehle aus:
echo.
echo 1. Bot-Status prüfen:
echo    sudo systemctl status discord-bot.service
echo.
echo 2. Bot stoppen:
echo    sudo systemctl stop discord-bot.service
echo.
echo 3. Zum Bot-Verzeichnis:
echo    cd grow-a-garden-bot
echo.
echo 4. Git-Update:
echo    git fetch origin
echo    git checkout feat/selenium-cloudflare-fix
echo    git pull origin feat/selenium-cloudflare-fix
echo.
echo 5. Dependencies installieren:
echo    pip3 install -r requirements.txt
echo.
echo 6. Bot starten:
echo    sudo systemctl start discord-bot.service
echo    sudo systemctl status discord-bot.service
echo.
echo Drücke eine Taste um PuTTY zu starten...
pause >nul

start "" "C:\Users\jonas\Desktop\putty.exe" -ssh stefan@192.168.171.100 -i "C:\Users\jonas\Desktop\ssh-keys\putty.privat.pihole.ppk"
