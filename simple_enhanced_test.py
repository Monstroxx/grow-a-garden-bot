import aiohttp
import asyncio
import random
from datetime import datetime

async def test_vulcanvalues_with_enhanced_approach():
    """Test mit verbessertem Anti-Bot-Ansatz"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Enhanced Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Erweiterte Headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
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
        'Cache-Control': 'max-age=0'
    }
    
    max_retries = 3
    
    for attempt in range(max_retries):
        try:
            print(f"Versuch {attempt + 1}/{max_retries}")
            
            # Verzögerung zwischen Versuchen
            if attempt > 0:
                delay = 10 + random.uniform(5, 15)
                print(f"Warte {delay:.1f} Sekunden...")
                await asyncio.sleep(delay)
            
            timeout = aiohttp.ClientTimeout(total=30, connect=10)
            
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.get(url, headers=headers) as response:
                    print(f"HTTP Status: {response.status}")
                    
                    if response.status == 200:
                        content = await response.text()
                        print(f"Content Length: {len(content)} Zeichen")
                        
                        # Prüfe auf Challenge-Seite
                        if "Just a moment" in content or "Checking your browser" in content:
                            print("Challenge-Seite erhalten, kein echter Content")
                            continue
                        
                        # Prüfe auf echten Content
                        success_keywords = ["grow", "stock", "seeds", "eggs", "gear"]
                        found = [kw for kw in success_keywords if kw.lower() in content.lower()]
                        
                        if found:
                            print(f"SUCCESS! Keywords gefunden: {found}")
                            print("Content Preview (erste 300 Zeichen):")
                            print(content[:300])
                            return content
                        else:
                            print("Kein relevanter Content gefunden")
                            print("Content Preview:")
                            print(content[:200])
                            continue
                    
                    elif response.status == 403:
                        print("403 Forbidden - Cloudflare Protection aktiv")
                        continue
                    
                    elif response.status == 429:
                        print("429 Rate Limited")
                        await asyncio.sleep(30)
                        continue
                    
                    else:
                        print(f"HTTP Error: {response.status}")
                        continue
        
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print("Alle Versuche fehlgeschlagen")
    return None

if __name__ == "__main__":
    result = asyncio.run(test_vulcanvalues_with_enhanced_approach())
    print(f"\nTest Result: {'SUCCESS' if result else 'FAILED'}")
