# Tech Context: Grow a Garden Stock Bot

## Technology Stack
- **Language**: Python 3.7+
- **Framework**: discord.py 2.3.0+
- **Web Scraping**: BeautifulSoup4 + aiohttp
- **Environment**: python-dotenv für Konfiguration
- **Async**: asyncio für concurrent operations

## Development Setup
```bash
pip install -r requirements.txt
python gag-aleart.py
```

## Dependencies
```
discord.py>=2.3.0  # Discord API Integration
aiohttp>=3.8.0     # Async HTTP Requests  
beautifulsoup4>=4.11.0  # HTML Parsing
python-dotenv>=1.0.0    # Environment Variables
```

## Configuration Management
- **Environment Variables**: `.env` file
- **Required Vars**: `DISCORD_TOKEN`, `ROLE_CHANNEL_ID`, `STOCK_URL`
- **Security**: `.gitignore` schützt `.env`
- **Example Config**: `.env.example` als Template

## Discord Bot Setup
```python
intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True  
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)
```

## Technical Constraints
- **Discord Limits**: 25 Items pro Dropdown → 4 separate Dropdowns
- **Rate Limiting**: 5-Minuten Intervall für Stock-Checks
- **Memory Usage**: Global `previous_stock` für Change Detection
- **Emoji Limits**: Discord Server Emoji Limits beachten

## Web Scraping Approach
- **Target**: vulcanvalues.com/grow-a-garden/stock
- **Method**: aiohttp → BeautifulSoup parsing
- **Challenge**: Dynamic content, potential layout changes
- **Robustness**: Try-catch für Website-Änderungen

## Async Patterns
- **Stock Monitoring**: `@tasks.loop(minutes=5)`
- **HTTP Requests**: `async with aiohttp.ClientSession()`
- **Discord Operations**: Async message sending

## Error Handling Strategy
- Logging für Debugging
- Graceful degradation bei Website-Fehlern
- Fallback Emojis bei fehlenden Custom Emojis
- Try-catch um kritische Operations

## Performance Considerations
- **Memory**: Global state für previous_stock
- **Network**: Batch HTTP requests wo möglich
- **Discord API**: Rate limit awareness
- **Scraping**: Efficient BeautifulSoup selectors