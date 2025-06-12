# Selenium-basierte Stock-Fetching Funktion für gag-aleart.py
# Diese Funktion ersetzt die aiohttp-basierte fetch_stock_data()

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

# Globale WebDriver-Instanz für Wiederverwendung
_webdriver_instance = None
_webdriver_lock = asyncio.Lock()

def setup_chrome_driver():
    """Erstellt und konfiguriert Chrome WebDriver"""
    global _webdriver_instance
    
    if _webdriver_instance is not None:
        try:
            # Test ob Driver noch funktioniert
            _webdriver_instance.current_url
            return _webdriver_instance
        except:
            # Driver ist tot, erstelle neuen
            _webdriver_instance = None
    
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
            break
    
    if not chrome_path:
        raise Exception("Chrome Browser nicht gefunden!")
    
    # Chrome Optionen
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")  # Headless für Production
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")  # Schneller ohne Bilder
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    # WebDriver erstellen
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    
    # Anti-Detection
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    _webdriver_instance = driver
    return driver

def selenium_fetch_stock_sync(url, max_wait_time=90):
    """Synchrone Selenium-basierte Stock-Daten-Abfrage"""
    driver = None
    
    try:
        print(f"🔍 Selenium: Hole Stock-Daten von {url}")
        driver = setup_chrome_driver()
        
        print("📡 Navigiere zur Stock-Seite...")
        driver.get(url)
        
        # Initial wait
        time.sleep(5)
        
        # Challenge-Detection und Wait
        challenge_start = time.time()
        
        while time.time() - challenge_start < max_wait_time:
            page_source = driver.page_source
            elapsed = int(time.time() - challenge_start)
            
            # Check für Challenge-Indikatoren
            challenge_active = any(indicator in page_source for indicator in [
                "Nur einen Moment", "Just a moment", "Checking your browser", 
                "DDoS protection", "cf-browser-verification"
            ])
            
            if not challenge_active and len(page_source) > 15000:
                # Check for real content indicators
                content_indicators = ["Seeds", "Eggs", "Gear", "shop", "price", "cost", "item"]
                real_content = any(ind.lower() in page_source.lower() for ind in content_indicators)
                
                if real_content:
                    print(f"✅ Echte Stock-Daten erhalten nach {elapsed}s")
                    return page_source
                else:
                    print(f"⏳ Challenge beendet, aber noch kein Stock-Content ({elapsed}s)")
            else:
                if elapsed % 10 == 0:  # Status alle 10 Sekunden
                    print(f"⏳ Cloudflare Challenge aktiv... {elapsed}s/{max_wait_time}s")
            
            time.sleep(3)
        
        # Timeout erreicht - trotzdem versuchen
        final_source = driver.page_source
        print(f"⚠️ Challenge-Timeout nach {max_wait_time}s - verwende vorhandenen Content")
        
        if len(final_source) > 10000:
            return final_source
        else:
            raise Exception("Keine brauchbaren Daten nach Challenge-Timeout")
    
    except Exception as e:
        print(f"❌ Selenium Fehler: {e}")
        raise e

async def fetch_stock_data_selenium():
    """
    Async Wrapper für Selenium-basierte Stock-Daten-Abfrage
    Ersetzt die originale fetch_stock_data() Funktion
    """
    async with _webdriver_lock:
        try:
            # Führe Selenium-Operation in Thread-Pool aus (da sync)
            loop = asyncio.get_event_loop()
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                html_content = await loop.run_in_executor(
                    executor, 
                    selenium_fetch_stock_sync, 
                    STOCK_URL,
                    90  # 90 Sekunden max wait
                )
            
            if not html_content:
                print("❌ Keine HTML-Daten von Selenium erhalten")
                return {}
            
            print(f"📊 Verarbeite {len(html_content)} Zeichen HTML-Content...")
            
            # BeautifulSoup für HTML-Parsing (wie im Original)
            soup = BeautifulSoup(html_content, 'html.parser')
            
            stock_data = {}
            
            print("🔍 Starte universelle Stock-Erkennung...")
            
            # Originale Parsing-Logik beibehalten
            all_items = soup.find_all('li', class_=lambda x: x and 'bg-gray-900' in str(x))
            print(f"📦 {len(all_items)} potentielle Items gefunden")
            
            if len(all_items) == 0:
                # Fallback: andere selectors versuchen
                print("🔄 Versuche alternative Item-Selectors...")
                all_items = soup.find_all('div', class_=lambda x: x and ('item' in str(x).lower() or 'stock' in str(x).lower()))
                print(f"📦 {len(all_items)} Items mit Fallback-Selector gefunden")
            
            # Bestimme Kategorie basierend auf Position/Context
            categories_found = {
                'Gear': [],
                'Eggs': [],
                'Seeds': [],
                'Honey': [],
                'Cosmetics': []
            }
            
            for item in all_items:
                try:
                    # Extrahiere Item-Daten (Original-Logik)
                    item_name = None
                    quantity = 1
                    img_src = ''
                    category = 'Unknown'
                    
                    # Methode 1: Span-Text analysieren
                    spans = item.find_all('span')
                    for span in spans:
                        span_text = span.get_text(strip=True)
                        if span_text and not span_text.startswith('x') and len(span_text) > 2:
                            if ' x' in span_text:
                                parts = span_text.split(' x')
                                item_name = parts[0].strip()
                                if len(parts) > 1:
                                    try:
                                        quantity = int(parts[1].strip())
                                    except:
                                        quantity = 1
                            else:
                                item_name = span_text
                            break
                    
                    # Kategorie bestimmen (vereinfacht)
                    if item_name:
                        item_lower = item_name.lower()
                        if any(seed in item_lower for seed in ['seed', 'grape', 'mushroom', 'coconut', 'dragon', 'watermelon', 'pumpkin', 'tomato', 'corn', 'blueberry', 'tulip', 'carrot', 'strawberry']):
                            category = 'Seeds'
                        elif any(egg in item_lower for egg in ['egg']):
                            category = 'Eggs'
                        elif any(gear in item_lower for gear in ['sprinkler', 'tool', 'pot', 'rod']):
                            category = 'Gear'
                        elif any(honey in item_lower for honey in ['honey', 'bee', 'flower']):
                            category = 'Honey'
                        else:
                            category = 'Cosmetics'
                        
                        categories_found[category].append({
                            'name': item_name,
                            'quantity': quantity,
                            'img_src': img_src
                        })
                        
                except Exception as e:
                    print(f"⚠️ Fehler beim Parsen eines Items: {e}")
                    continue
            
            # Zusammenfassung der gefundenen Items
            total_items = sum(len(items) for items in categories_found.values())
            print(f"✅ {total_items} Items erfolgreich kategorisiert:")
            for category, items in categories_found.items():
                if items:
                    print(f"  📁 {category}: {len(items)} Items")
            
            return categories_found
            
        except Exception as e:
            print(f"❌ fetch_stock_data_selenium Fehler: {e}")
            
            # Fallback zu alter Methode (optional)
            print("🔄 Versuche Fallback zu aiohttp...")
            try:
                return await fetch_stock_data_aiohttp_fallback()
            except:
                print("❌ Auch Fallback fehlgeschlagen")
                return {}

async def fetch_stock_data_aiohttp_fallback():
    """Fallback zur originalen aiohttp-Methode"""
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36'
            }
            async with session.get(STOCK_URL, headers=headers, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    print("✅ Fallback aiohttp erfolgreich")
                    return html
                else:
                    print(f"❌ Fallback HTTP Status: {response.status}")
                    return {}
    except Exception as e:
        print(f"❌ Fallback Fehler: {e}")
        return {}

def cleanup_webdriver():
    """Bereinigt WebDriver bei Bot-Shutdown"""
    global _webdriver_instance
    if _webdriver_instance:
        try:
            _webdriver_instance.quit()
            _webdriver_instance = None
            print("🧹 WebDriver cleanup erfolgreich")
        except Exception as e:
            print(f"⚠️ WebDriver cleanup Fehler: {e}")

# Diese Funktion muss in gag-aleart.py die bestehende fetch_stock_data() ersetzen
