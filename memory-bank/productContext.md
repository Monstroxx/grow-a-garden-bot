# Product Context: Grow a Garden Stock Bot

## Why This Project Exists
Die Grow a Garden Community verpasste regelmäßig wertvolle Items im Stock, da manuelle Überwachung zeitaufwendig und unzuverlässig war. VulcanValues zeigt Stock-Updates, aber ohne automatische Benachrichtigungen.

## Problems It Solves
1. **Verpasste seltene Items**: Prismatic/Divine Seeds sind extrem selten und schnell ausverkauft
2. **Manuelle Überwachung**: Ständige Website-Checks waren unpraktisch
3. **Überlastung**: Ein Channel für alle Updates war chaotisch
4. **Rollen-Management**: Benutzer wollten nur spezifische Rarität-Benachrichtigungen

## How It Should Work
### User Experience Flow
1. **Rollenauswahl**: Benutzer wählt gewünschte Kategorien/Raritäten über Dropdown-Menüs
2. **Automatische Überwachung**: Bot checkt alle 5 Minuten VulcanValues Stock
3. **Kategorisierte Benachrichtigungen**: Updates landen in entsprechenden Channels
4. **Doppelte Mentions**: Haupt-Rolle + spezifische Rarität werden erwähnt

### Stock Update Process
```
Website Check → Item Analysis → Rarität Detection → 
Channel Selection → Role Mention → Custom Emoji → Post Notification
```

## User Experience Goals
- **Einfache Rollenauswahl**: Dropdown-Menüs statt komplexe Commands
- **Relevante Benachrichtigungen**: Nur für gewählte Kategorien/Raritäten
- **Übersichtliche Updates**: Separate Channels verhindern Spam
- **Visuelle Klarheit**: Custom Emojis und kategorisierte Formatting

## Success Metrics
- Community nutzt aktiv die Rollenauswahl
- Keine Beschwerden über verpasste seltene Items
- Positive Feedback zur Kategorisierung
- Hohe Retention bei Rollenauswahl