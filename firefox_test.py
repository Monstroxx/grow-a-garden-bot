from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from webdriver_manager.firefox import GeckoDriverManager
import time
from datetime import datetime

def test_firefox_vulcanvalues():
    """Test VulcanValues mit Firefox WebDriver"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Firefox Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Firefox Optionen
    firefox_options = Options()
    firefox_options.add_argument("--headless")  # Headless mode
    firefox_options.set_preference("general.useragent.override", 
                                   "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0")
    
    driver = None
    
    try:
        # WebDriver initialisieren
        print("Starte Firefox WebDriver...")
        service = Service(GeckoDriverManager().install())
        driver = webdriver.Firefox(service=service, options=firefox_options)
        
        print("Lade Website...")
        driver.get(url)
        
        # Kurz warten für Initial Load
        time.sleep(3)
        
        # Prüfe auf Cloudflare Challenge
        initial_source = driver.page_source
        
        if "Just a moment" in initial_source or "Checking your browser" in initial_source:
            print("Cloudflare Challenge erkannt - warte 15 Sekunden...")
            time.sleep(15)
            
            # Refresh page source
            final_source = driver.page_source
        else:
            print("Keine Challenge erkannt")
            final_source = initial_source
        
        print(f"Finale Seitenlänge: {len(final_source)} Zeichen")
        
        # Prüfe auf erfolgreiche Inhalte
        success_keywords = ["grow", "stock", "seeds", "eggs", "gear", "vulcan"]
        found_keywords = []
        
        for keyword in success_keywords:
            if keyword.lower() in final_source.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"SUCCESS! Keywords gefunden: {found_keywords}")
            
            # Zeige relevante Teile der Seite
            lines = final_source.split('\n')
            relevant_lines = [line.strip() for line in lines if any(kw in line.lower() for kw in found_keywords)][:5]
            
            print("Relevante Zeilen:")
            for line in relevant_lines:
                if line:
                    print(f"  {line[:100]}...")
            
            return final_source
        else:
            print("FEHLER: Keine relevanten Keywords gefunden")
            print("Seitenanfang (erste 400 Zeichen):")
            print(final_source[:400])
            return None
            
    except Exception as e:
        print(f"Firefox Fehler: {type(e).__name__}: {e}")
        return None
        
    finally:
        if driver:
            print("Schließe Firefox...")
            driver.quit()

if __name__ == "__main__":
    result = test_firefox_vulcanvalues()
    success = result is not None
    print(f"\nFirefox Test: {'ERFOLG' if success else 'FEHLER'}")
    
    if success:
        print(f"Erhaltene Daten: {len(result)} Zeichen")
