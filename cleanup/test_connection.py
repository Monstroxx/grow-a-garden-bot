# Enhanced HTTP Client für VulcanValues Anti-Bot Umgehung
import aiohttp
import asyncio
import random
from datetime import datetime

class EnhancedHTTPClient:
    """
    Verbesserter HTTP Client zur Umgehung von Anti-Bot-Maßnahmen
    """
    
    def __init__(self):
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        ]
    
    def get_realistic_headers(self):
        """Generiert realistische Browser-Headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
    
    async def fetch_with_retry(self, url, max_retries=3, delay_range=(1, 3)):
        """
        Holt URL mit Retry-Logic und Anti-Bot-Maßnahmen
        """
        for attempt in range(max_retries):
            try:
                # Zufällige Verzögerung zwischen Requests
                if attempt > 0:
                    delay = random.uniform(*delay_range)
                    print(f"⏳ Warte {delay:.1f}s vor Retry {attempt}...")
                    await asyncio.sleep(delay)
                
                headers = self.get_realistic_headers()
                
                # Timeout und SSL-Konfiguration
                timeout = aiohttp.ClientTimeout(total=30, connect=10)
                connector = aiohttp.TCPConnector(ssl=False)  # Temporär SSL-Checks deaktivieren
                
                async with aiohttp.ClientSession(
                    timeout=timeout,
                    connector=connector,
                    headers=headers
                ) as session:
                    
                    async with session.get(url) as response:
                        print(f"📡 HTTP Status: {response.status}")
                        
                        if response.status == 200:
                            content = await response.text()
                            print(f"✅ Erfolgreich {len(content)} Zeichen erhalten")
                            return content
                        
                        elif response.status == 403:
                            print(f"🚫 403 Forbidden - Anti-Bot-Schutz aktiv (Versuch {attempt + 1}/{max_retries})")
                            continue
                        
                        elif response.status == 429:
                            print(f"⏱️ 429 Rate Limited - Warte länger (Versuch {attempt + 1}/{max_retries})")
                            await asyncio.sleep(random.uniform(5, 10))
                            continue
                        
                        else:
                            print(f"❌ HTTP {response.status}: {response.reason}")
                            continue
            
            except aiohttp.ClientError as e:
                print(f"🔌 Netzwerk-Fehler (Versuch {attempt + 1}/{max_retries}): {e}")
                continue
            
            except Exception as e:
                print(f"💥 Unerwarteter Fehler (Versuch {attempt + 1}/{max_retries}): {e}")
                continue
        
        print(f"❌ Alle {max_retries} Versuche fehlgeschlagen")
        return None

# Test-Funktion
async def test_vulcanvalues():
    """Testet die Verbindung zu VulcanValues"""
    client = EnhancedHTTPClient()
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"🧪 Teste Verbindung zu {url}")
    print(f"⏰ Zeitpunkt: {datetime.now().strftime('%H:%M:%S')}")
    
    content = await client.fetch_with_retry(url)
    
    if content:
        print(f"✅ Erfolgreich! Erste 200 Zeichen:")
        print(content[:200])
        print("...")
        return True
    else:
        print("❌ Verbindung fehlgeschlagen")
        return False

if __name__ == "__main__":
    asyncio.run(test_vulcanvalues())
