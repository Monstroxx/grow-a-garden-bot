# Direkter Test der Selenium-Funktionen ohne Bot-Import
import asyncio
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import os
from datetime import datetime
from dotenv import load_dotenv

# Lade Umgebungsvariablen
load_dotenv()

STOCK_URL = os.getenv('STOCK_URL', 'https://vulcanvalues.com/grow-a-garden/stock')

# Globale WebDriver-Instanz
_webdriver_instance = None

def setup_chrome_driver():
    """Erstellt Chrome WebDriver (Kopie der Funktion aus dem Bot)"""
    global _webdriver_instance
    
    if _webdriver_instance is not None:
        try:
            _webdriver_instance.current_url
            return _webdriver_instance
        except:
            try:
                _webdriver_instance.quit()
            except:
                pass
            _webdriver_instance = None
    
    print("🔧 Initialisiere Chrome WebDriver...")
    
    # Chrome-Pfad finden
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME'))
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            print(f"✅ Chrome gefunden: {path}")
            break
    
    if not chrome_path:
        raise Exception("❌ Chrome Browser nicht gefunden!")
    
    # Chrome Optionen
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        _webdriver_instance = driver
        print("✅ Chrome WebDriver erfolgreich initialisiert")
        return driver
        
    except Exception as e:
        print(f"❌ Chrome WebDriver Setup fehlgeschlagen: {e}")
        raise e

def selenium_fetch_stock_sync(url, max_wait_time=90):
    """Synchrone Selenium Stock-Fetch (Kopie aus dem Bot)"""
    driver = None
    
    try:
        print(f"Selenium: Hole Stock-Daten von {url}")
        driver = setup_chrome_driver()
        
        print("Navigiere zur VulcanValues Stock-Seite...")
        driver.get(url)
        
        time.sleep(5)
        
        challenge_start = time.time()
        challenge_detected = False
        
        while time.time() - challenge_start < max_wait_time:
            page_source = driver.page_source
            elapsed = int(time.time() - challenge_start)
            
            challenge_indicators = [
                "Nur einen Moment", "Just a moment", "Checking your browser", 
                "DDoS protection", "cf-browser-verification", "Please wait"
            ]
            
            challenge_active = any(indicator in page_source for indicator in challenge_indicators)
            
            if challenge_active and not challenge_detected:
                challenge_detected = True
                print("Cloudflare Challenge erkannt - warte auf automatische Lösung...")
            
            if not challenge_active and len(page_source) > 15000:
                content_indicators = [
                    "Seeds", "Eggs", "Gear", "shop", "price", "cost", 
                    "item", "buy", "purchase", "roblox", "vulcan"
                ]
                real_content = any(ind.lower() in page_source.lower() for ind in content_indicators)
                
                if real_content:
                    print(f"Cloudflare Challenge erfolgreich umgangen nach {elapsed}s")
                    print(f"Echte Stock-Daten erhalten ({len(page_source)} Zeichen)")
                    return page_source
                else:
                    if elapsed > 30:
                        print(f"Kein perfekter Content, aber Challenge beendet nach {elapsed}s")
                        return page_source
            
            if elapsed > 0 and elapsed % 15 == 0:
                if challenge_active:
                    print(f"Cloudflare Challenge läuft... {elapsed}s/{max_wait_time}s")
                else:
                    print(f"Warte auf vollständigen Content... {elapsed}s/{max_wait_time}s")
            
            time.sleep(3)
        
        final_source = driver.page_source
        print(f"Challenge-Timeout nach {max_wait_time}s")
        print(f"Verfügbarer Content: {len(final_source)} Zeichen")
        
        if len(final_source) > 10000:
            print("Verwende verfügbaren Content trotz Timeout")
            return final_source
        else:
            raise Exception("Keine brauchbaren Daten nach Challenge-Timeout")
    
    except Exception as e:
        print(f"Selenium Fetch Fehler: {e}")
        raise e

def cleanup_webdriver():
    """Bereinigt WebDriver"""
    global _webdriver_instance
    if _webdriver_instance:
        try:
            _webdriver_instance.quit()
            _webdriver_instance = None
            print("WebDriver erfolgreich bereinigt")
        except Exception as e:
            print(f"WebDriver Cleanup Fehler: {e}")

async def test_selenium_stock_fetch():
    """Testet die komplette Selenium Stock-Fetch-Funktionalität"""
    print("TEST: Selenium Stock-Fetch...")
    
    try:
        # Test 1: WebDriver Setup
        print("\n1. Teste Chrome WebDriver Setup...")
        driver = setup_chrome_driver()
        if driver:
            print("SUCCESS: Chrome WebDriver erfolgreich erstellt")
        else:
            print("ERROR: Chrome WebDriver Setup fehlgeschlagen")
            return False
        
        # Test 2: Stock-Daten-Abfrage mit Thread Pool
        print("\n2. Teste Stock-Daten-Abfrage...")
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
            html_content = await loop.run_in_executor(
                executor, 
                selenium_fetch_stock_sync, 
                STOCK_URL,
                90
            )
        
        if not html_content:
            print("ERROR: Keine HTML-Daten erhalten")
            return False
        
        print(f"SUCCESS: HTML-Content erhalten: {len(html_content)} Zeichen")
        
        # Test 3: HTML-Parsing
        print("\n3. Teste HTML-Parsing...")
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Einfache Item-Erkennung
        all_items = soup.find_all('li', class_=lambda x: x and 'bg-gray-900' in str(x))
        print(f"Items gefunden: {len(all_items)} potentielle Items")
        
        if len(all_items) == 0:
            # Fallback-Selectors
            fallback_selectors = [
                ('div', lambda x: x and ('item' in str(x).lower() or 'stock' in str(x).lower())),
                ('li', lambda x: x and 'item' in str(x).lower()),
                ('div', lambda x: x and 'bg-' in str(x).lower())
            ]
            
            for tag, class_filter in fallback_selectors:
                all_items = soup.find_all(tag, class_=class_filter)
                if len(all_items) > 0:
                    print(f"Fallback: {len(all_items)} Items mit {tag}-Fallback gefunden")
                    break
        
        # Parse erste 5 Items als Test
        parsed_items = []
        for i, item in enumerate(all_items[:5]):
            try:
                spans = item.find_all('span')
                for span in spans:
                    span_text = span.get_text(strip=True)
                    if span_text and len(span_text) > 2:
                        parsed_items.append({
                            'name': span_text,
                            'index': i
                        })
                        break
            except:
                continue
        
        print(f"SUCCESS: {len(parsed_items)} Items erfolgreich geparst")
        
        # Zeige Beispiel-Items
        if parsed_items:
            print("\nBeispiel-Items:")
            for item in parsed_items:
                print(f"  {item['index'] + 1}. {item['name']}")
        
        # Test 4: Content-Validierung
        print("\n4. Teste Content-Validierung...")
        content_indicators = ["Seeds", "Eggs", "Gear", "shop", "price", "vulcan", "roblox"]
        found_indicators = [ind for ind in content_indicators if ind.lower() in html_content.lower()]
        
        if found_indicators:
            print(f"SUCCESS: Content-Indikatoren gefunden: {found_indicators}")
            
            # Check für Challenge-Seite
            challenge_indicators = ["Nur einen Moment", "Just a moment", "Checking your browser"]
            still_challenge = any(ind in html_content for ind in challenge_indicators)
            
            if still_challenge:
                print("WARNING: Immer noch Challenge-Seite, aber Content-Indikatoren vorhanden")
            else:
                print("SUCCESS: Echte Stock-Seite (keine Challenge-Indikatoren)")
            
            return True
        else:
            print("ERROR: Keine relevanten Content-Indikatoren gefunden")
            print("Sample content (erste 300 Zeichen):")
            print(html_content[:300])
            return False
            
    except Exception as e:
        print(f"ERROR: Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        print("\nCleanup...")
        cleanup_webdriver()

if __name__ == "__main__":
    print("SELENIUM STOCK-FETCH TEST")
    print("="*60)
    print(f"Stock URL: {STOCK_URL}")
    
    if not STOCK_URL:
        print("ERROR: STOCK_URL nicht in .env gesetzt!")
        exit(1)
    
    result = asyncio.run(test_selenium_stock_fetch())
    
    print("\n" + "="*60)
    if result:
        print("TEST ERFOLGREICH!")
        print("SUCCESS: Selenium kann Cloudflare umgehen")
        print("SUCCESS: Stock-Daten werden erfolgreich abgerufen")
        print("SUCCESS: Bot-Integration ist ready!")
    else:
        print("TEST FEHLGESCHLAGEN!")
        print("ERROR: Probleme mit Selenium oder Cloudflare")
        print("FIX: Überprüfe Chrome-Installation und Netzwerk")
        print("INFO: Möglicherweise verstärkte Cloudflare-Protection")
    
    print(f"\nFinal Result: {'SUCCESS' if result else 'FAILED'}")
