# Enhanced HTTP Client für Bot-Fix
import aiohttp
import asyncio
import random
import json
from datetime import datetime, timedelta

class AntiCloudflareClient:
    """
    Erweiterte HTTP-Client-Klasse zur Umgehung von Cloudflare Bot Protection
    """
    
    def __init__(self):
        self.session = None
        self.last_request_time = None
        self.request_count = 0
        
        # Realistische User-Agents (häufig rotiert)
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.2277.83',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        ]
    
    def get_enhanced_headers(self):
        """Generiert erweiterte, realistische Browser-Headers"""
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "Google Chrome";v="122"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Cache-Control': 'max-age=0',
            'Priority': 'u=0, i'
        }
    
    async def smart_delay(self):
        """Intelligente Verzögerung zwischen Requests"""
        if self.last_request_time:
            time_since_last = datetime.now() - self.last_request_time
            min_delay = 8 + random.uniform(2, 7)  # 8-15 Sekunden base delay
            
            if time_since_last.total_seconds() < min_delay:
                sleep_time = min_delay - time_since_last.total_seconds()
                print(f"🕒 Smart delay: {sleep_time:.1f}s")
                await asyncio.sleep(sleep_time)
        
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    async def fetch_with_anti_cloudflare(self, url, max_retries=5):
        """
        Erweiterte Fetch-Methode mit Anti-Cloudflare-Maßnahmen
        """
        for attempt in range(max_retries):
            try:
                await self.smart_delay()
                
                # Erweiterte Retry-Verzögerung
                if attempt > 0:
                    delay = min(30, (2 ** attempt) + random.uniform(1, 5))
                    print(f"⏳ Retry {attempt}/{max_retries} - Warte {delay:.1f}s")
                    await asyncio.sleep(delay)
                
                headers = self.get_enhanced_headers()
                
                # Session-Konfiguration
                timeout = aiohttp.ClientTimeout(total=45, connect=15)
                connector = aiohttp.TCPConnector(
                    ssl=False,  # Temporär für Tests
                    limit=1,
                    limit_per_host=1,
                    keepalive_timeout=30
                )
                
                if not self.session:
                    self.session = aiohttp.ClientSession(
                        timeout=timeout,
                        connector=connector
                    )
                
                print(f"📡 Request #{self.request_count} (Versuch {attempt + 1})")
                
                async with self.session.get(url, headers=headers) as response:
                    print(f"Status: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        print(f"✅ Erfolg: {len(content)} Zeichen erhalten")
                        
                        # Validiere Content (nicht nur Challenge-Seite)
                        if self.validate_content(content):
                            return content
                        else:
                            print("⚠️ Challenge-Seite erhalten, nicht echter Content")
                            continue
                    
                    elif response.status == 403:
                        print("🚫 403 Forbidden - Cloudflare blockiert")
                        
                        # Erweiterte Verzögerung bei 403
                        if attempt < max_retries - 1:
                            extended_delay = 30 + random.uniform(10, 30)
                            print(f"🔄 Erweiterte Pause: {extended_delay:.1f}s")
                            await asyncio.sleep(extended_delay)
                        continue
                    
                    elif response.status == 429:
                        print("⏱️ 429 Rate Limited")
                        rate_limit_delay = 60 + random.uniform(30, 60)
                        print(f"⏸️ Rate Limit Pause: {rate_limit_delay:.1f}s")
                        await asyncio.sleep(rate_limit_delay)
                        continue
                    
                    elif response.status in [503, 522, 524]:
                        print(f"🔧 {response.status} - Server/Cloudflare Problem")
                        continue
                    
                    else:
                        print(f"❌ HTTP {response.status}: {response.reason}")
                        continue
            
            except asyncio.TimeoutError:
                print(f"⏰ Timeout bei Versuch {attempt + 1}")
                continue
                
            except aiohttp.ClientError as e:
                print(f"🔌 Client Error: {e}")
                continue
                
            except Exception as e:
                print(f"💥 Unerwarteter Fehler: {e}")
                continue
        
        print(f"❌ Alle {max_retries} Versuche fehlgeschlagen")
        return None
    
    def validate_content(self, content):
        """Validiert ob Content echt ist (nicht Challenge-Seite)"""
        if not content:
            return False
        
        # Challenge-Seite Indikatoren
        challenge_indicators = [
            "Just a moment",
            "Checking your browser",
            "Please wait",
            "DDoS protection",
            "cf-browser-verification"
        ]
        
        for indicator in challenge_indicators:
            if indicator in content:
                return False
        
        # Echte Content-Indikatoren
        valid_indicators = ["grow", "stock", "seeds", "eggs", "gear"]
        return any(indicator.lower() in content.lower() for indicator in valid_indicators)
    
    async def close(self):
        """Session cleanup"""
        if self.session:
            await self.session.close()
            self.session = None

# Test-Funktion
async def test_enhanced_client():
    """Teste den erweiterten Client"""
    client = AntiCloudflareClient()
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    try:
        print(f"🧪 Teste Enhanced Client: {url}")
        content = await client.fetch_with_anti_cloudflare(url)
        
        if content:
            print("✅ Enhanced Client erfolgreich!")
            return content
        else:
            print("❌ Enhanced Client fehlgeschlagen")
            return None
    finally:
        await client.close()

if __name__ == "__main__":
    result = asyncio.run(test_enhanced_client())
    print(f"\nTest Resultat: {'ERFOLG' if result else 'FEHLER'}")
