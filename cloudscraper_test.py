# CloudScraper Lösung für VulcanValues
# Diese Bibliothek kann Cloudflare's Bot-Protection umgehen

"""
Installation:
pip install cloudscraper

Verwendung im Bot:
- Ersetze aiohttp mit cloudscraper
- Automatische Cloudflare Challenge-Lösung
"""

import cloudscraper
import asyncio
from datetime import datetime

def test_cloudscraper():
    """Test mit CloudScraper für Cloudflare-Umgehung"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"CloudScraper Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # CloudScraper Session erstellen
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )
        
        print("Führe Cloudflare Challenge durch...")
        
        # Request mit Cloudflare-Umgehung
        response = scraper.get(url, timeout=30)
        
        print(f"Status: {response.status_code}")
        print(f"Content-Length: {len(response.text)}")
        
        if response.status_code == 200:
            content = response.text
            
            # Prüfe ob es sich um echten Content handelt
            if "grow" in content.lower() or "stock" in content.lower():
                print("SUCCESS! Echte Website-Daten erhalten")
                print("Erste 300 Zeichen:")
                print(content[:300])
                return content
            else:
                print("Unerwarteter Content:")
                print(content[:500])
                return None
                
        else:
            print(f"HTTP Fehler: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"CloudScraper Fehler: {e}")
        return None

if __name__ == "__main__":
    result = test_cloudscraper()
    success = result is not None
    print(f"\nCloudScraper Test: {'ERFOLG' if success else 'FEHLER'}")
