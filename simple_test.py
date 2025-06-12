import aiohttp
import asyncio
import random
from datetime import datetime

async def test_vulcanvalues_simple():
    """Einfacher Test der VulcanValues Verbindung"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    # Realistische Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,de;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    print(f"Teste Verbindung zu: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        timeout = aiohttp.ClientTimeout(total=30)
        
        async with aiohttp.ClientSession(timeout=timeout) as session:
            async with session.get(url, headers=headers) as response:
                print(f"HTTP Status: {response.status}")
                print(f"Content-Type: {response.headers.get('content-type', 'unknown')}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"Erfolg! Erhaltene Daten: {len(content)} Zeichen")
                    print("Erste 200 Zeichen:")
                    print(content[:200])
                    return True
                    
                elif response.status == 403:
                    print("403 Forbidden - Website blockiert Bot-Requests!")
                    return False
                    
                elif response.status == 429:
                    print("429 Too Many Requests - Rate limiting aktiv")
                    return False
                    
                else:
                    print(f"HTTP Fehler: {response.status} - {response.reason}")
                    return False
                    
    except aiohttp.ClientError as e:
        print(f"Netzwerk Fehler: {e}")
        return False
        
    except Exception as e:
        print(f"Unerwarteter Fehler: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_vulcanvalues_simple())
    print(f"Test erfolgreich: {result}")
