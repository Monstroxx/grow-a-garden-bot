import aiohttp
import asyncio
import ssl
from datetime import datetime

async def test_with_ssl_debug():
    """Test mit SSL-Debugging"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"SSL Debug Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # SSL Context erstellen
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }
    
    try:
        # Connector mit SSL-Optionen
        connector = aiohttp.TCPConnector(
            ssl=ssl_context,
            use_dns_cache=False,
            ttl_dns_cache=300,
            limit=30
        )
        
        timeout = aiohttp.ClientTimeout(total=30, connect=10)
        
        async with aiohttp.ClientSession(
            connector=connector,
            timeout=timeout,
            headers=headers
        ) as session:
            
            print("Verbindung wird aufgebaut...")
            
            async with session.get(url) as response:
                print(f"Status: {response.status}")
                print(f"Headers: {dict(response.headers)}")
                
                if response.status == 200:
                    content = await response.text()
                    print(f"Erfolg! {len(content)} Zeichen")
                    
                    if "grow" in content.lower() or "stock" in content.lower():
                        print("Inhalt sieht korrekt aus!")
                        return True
                    else:
                        print("Inhalt scheint nicht korrekt zu sein")
                        print("Erste 300 Zeichen:")
                        print(content[:300])
                        return False
                        
                elif response.status == 403:
                    print("403 Forbidden - Cloudflare/Bot-Protection aktiv")
                    content = await response.text()
                    print("Response Content (erste 500 Zeichen):")
                    print(content[:500])
                    return False
                    
                elif response.status in [503, 522, 524]:
                    print(f"{response.status} - Cloudflare/Server Problem")
                    return False
                    
                else:
                    print(f"HTTP {response.status}: {response.reason}")
                    content = await response.text()
                    print("Response (erste 200 Zeichen):")
                    print(content[:200])
                    return False
                    
    except asyncio.TimeoutError:
        print("Timeout - Verbindung zu langsam")
        return False
        
    except aiohttp.ClientConnectorError as e:
        print(f"Verbindungsfehler: {e}")
        return False
        
    except aiohttp.ClientError as e:
        print(f"HTTP Client Fehler: {e}")
        return False
        
    except Exception as e:
        print(f"Unerwarteter Fehler: {type(e).__name__}: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_with_ssl_debug())
    print(f"\nTest Ergebnis: {'ERFOLG' if result else 'FEHLER'}")
