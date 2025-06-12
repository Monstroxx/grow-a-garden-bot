# Bot-Upload zum Raspberry Pi Script
# Dieses Script lädt den neuen Bot auf den Pi hoch

Write-Host "🚀 Uploading Grow a Garden Bot to Raspberry Pi..."

# Konfiguration
$localPath = "C:\Users\jonas\Desktop\projekte\grow-a-garden-bot"
$remotePath = "/home/stefan/grow-a-garden-bot-new"
$piHost = "stefan@192.168.171.100"
$keyPath = "C:\Users\jonas\Desktop\ssh-keys\putty.privat.pihole.ppk"

Write-Host "📁 Local Path: $localPath"
Write-Host "🏠 Remote Path: $remotePath"
Write-Host "🔗 Pi Host: $piHost"

# Prüfe ob WinSCP installiert ist
$winscpPath = "C:\Program Files (x86)\WinSCP\WinSCP.exe"
if (-not (Test-Path $winscpPath)) {
    $winscpPath = "WinSCP.exe"  # Try from PATH
}

if (Get-Command $winscpPath -ErrorAction SilentlyContinue) {
    Write-Host "✅ WinSCP gefunden, starte Upload..."
    
    # WinSCP Script erstellen
    $scriptContent = @"
open sftp://$piHost -privatekey="$keyPath"
mkdir $remotePath
put -delete $localPath\* $remotePath\
close
exit
"@
    
    $scriptPath = "$env:TEMP\winscp_upload.txt"
    $scriptContent | Out-File -FilePath $scriptPath -Encoding ASCII
    
    # WinSCP ausführen
    & $winscpPath /script=$scriptPath
    
    Remove-Item $scriptPath
    
    Write-Host "✅ Upload abgeschlossen!"
    
} else {
    Write-Host "❌ WinSCP nicht gefunden!"
    Write-Host ""
    Write-Host "🔧 Alternative: Manueller Upload"
    Write-Host "1. Öffne WinSCP manuell"
    Write-Host "2. Host: 192.168.171.100"
    Write-Host "3. User: stefan"
    Write-Host "4. Private Key: $keyPath"
    Write-Host "5. Upload: $localPath -> $remotePath"
    Write-Host ""
    Write-Host "🔗 Oder verwende PuTTY PSCP:"
    Write-Host "pscp -i `"$keyPath`" -r `"$localPath\*`" $piHost`:$remotePath/"
}

Write-Host ""
Write-Host "📋 Nächste Schritte:"
Write-Host "1. SSH zum Pi: ssh $piHost"
Write-Host "2. Bot installieren: cd $remotePath && pip3 install -r requirements.txt"
Write-Host "3. Konfiguation kopieren: cp /home/stefan/grow-a-garden-bot/.env $remotePath/"
Write-Host "4. Service updaten: sudo systemctl stop discord-bot.service"
Write-Host "5. Service starten: sudo systemctl start discord-bot.service"
Write-Host ""
Write-Host "📖 Detaillierte Anleitung: RASPBERRY_PI_DEPLOYMENT.md"
