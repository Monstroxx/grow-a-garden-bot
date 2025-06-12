# Bot-Update Script für Raspberry Pi
# Dieses Script aktualisiert den Discord Bot mit der neuen Selenium-Version

Write-Host "🚀 Starte Bot-Update auf Raspberry Pi..."

# SSH-Konfiguration
$sshHost = "stefan@192.168.171.100"
$keyPath = "C:\Users\jonas\Desktop\ssh-keys\putty.privat.pihole.ppk"

# Versuche verschiedene SSH-Clients
$sshCommands = @(
    "# Bot-Status prüfen",
    "sudo systemctl status discord-bot.service --no-pager",
    "",
    "# Bot stoppen", 
    "sudo systemctl stop discord-bot.service",
    "",
    "# Bot-Verzeichnis aktualisieren",
    "cd /home/stefan",
    "ls -la | grep bot",
    "",
    "# Git Repository aktualisieren", 
    "cd grow-a-garden-bot",
    "git fetch origin",
    "git checkout feat/selenium-cloudflare-fix",
    "git pull origin feat/selenium-cloudflare-fix",
    "",
    "# Dependencies installieren",
    "pip3 install -r requirements.txt",
    "",
    "# Bot neu starten",
    "sudo systemctl start discord-bot.service",
    "sudo systemctl status discord-bot.service --no-pager"
)

Write-Host "SSH-Befehle die ausgeführt werden sollen:"
foreach ($cmd in $sshCommands) {
    if ($cmd -and !$cmd.StartsWith("#")) {
        Write-Host "  > $cmd"
    }
}

Write-Host ""
Write-Host "HINWEIS: Da SSH über PowerShell komplex ist, hier die manuellen Schritte:"
Write-Host ""
Write-Host "1. Öffne PuTTY manuell:"
Write-Host "   - Host: $sshHost"
Write-Host "   - Private Key: $keyPath"
Write-Host ""
Write-Host "2. Führe diese Befehle aus:"
foreach ($cmd in $sshCommands) {
    Write-Host $cmd
}

Write-Host ""
Write-Host "Alternativ: Soll ich einen anderen Ansatz versuchen? (plink, OpenSSH, etc.)"
