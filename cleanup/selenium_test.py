from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime

def test_selenium_vulcanvalues():
    """Test VulcanValues mit Selenium WebDriver"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Selenium Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Chrome Optionen
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    
    driver = None
    
    try:
        # WebDriver initialisieren
        print("Starte Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Automation-Detection umgehen
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Lade Website...")
        driver.get(url)
        
        # Warte auf Cloudflare Challenge
        print("Warte auf Cloudflare Challenge...")
        
        # Prüfe verschiedene Szenarien
        wait = WebDriverWait(driver, 30)
        
        # Szenario 1: Challenge-Seite
        if "Just a moment" in driver.page_source or "Checking your browser" in driver.page_source:
            print("Cloudflare Challenge erkannt - warte...")
            time.sleep(10)  # Warte auf automatische Weiterleitung
            
            # Warte auf echte Seite
            try:
                wait.until(lambda d: "Just a moment" not in d.page_source)
                print("Challenge bestanden!")
            except:
                print("Challenge-Timeout")
                return False
        
        # Prüfe finalen Seiteninhalt
        final_source = driver.page_source
        print(f"Seitenlänge: {len(final_source)} Zeichen")
        
        # Suche nach Grow a Garden Inhalten
        success_indicators = ["grow", "stock", "seeds", "eggs", "gear"]
        found_indicators = [indicator for indicator in success_indicators if indicator.lower() in final_source.lower()]
        
        if found_indicators:
            print(f"SUCCESS! Gefundene Indikatoren: {found_indicators}")
            print("Erste 500 Zeichen der echten Seite:")
            print(final_source[:500])
            return True
        else:
            print("FEHLER: Keine Grow a Garden Inhalte gefunden")
            print("Erste 300 Zeichen:")
            print(final_source[:300])
            return False
            
    except Exception as e:
        print(f"Selenium Fehler: {type(e).__name__}: {e}")
        return False
        
    finally:
        if driver:
            print("Schließe Browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_selenium_vulcanvalues()
    print(f"\nSelenium Test: {'ERFOLG' if result else 'FEHLER'}")
