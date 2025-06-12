from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

def test_selenium_with_latest_driver():
    """Test mit automatisch heruntergeladenem ChromeDriver"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Selenium Test mit aktuellstem ChromeDriver: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
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
            print(f"Chrome gefunden: {path}")
            break
    
    if not chrome_path:
        print("Chrome nicht gefunden!")
        return False
    
    # Chrome Optionen
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    driver = None
    
    try:
        print("Lade aktuellsten ChromeDriver herunter...")
        
        # Force fresh download der aktuellen Version
        service = Service(ChromeDriverManager(cache_valid_range=1).install())
        
        print("Starte Chrome...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print(f"Navigiere zu: {url}")
        driver.get(url)
        
        print("Warte 5 Sekunden auf Initial Load...")
        time.sleep(5)
        
        # Get page source
        page_source = driver.page_source
        print(f"Page Source Length: {len(page_source)} Zeichen")
        
        # Check for Cloudflare challenge
        if "Just a moment" in page_source or "Checking your browser" in page_source:
            print("Cloudflare Challenge erkannt! Warte auf Completion...")
            
            # Wait for challenge to complete
            for i in range(15):  # Max 30 seconds
                time.sleep(2)
                current_source = driver.page_source
                
                # Check if challenge is done
                if ("Just a moment" not in current_source and 
                    "Checking your browser" not in current_source):
                    print(f"Challenge completed after {(i+1)*2} seconds!")
                    page_source = current_source
                    break
                
                print(f"Challenge still active... {(i+1)*2}s")
            else:
                print("Challenge timeout after 30 seconds")
        
        # Validate final content
        print(f"Final page length: {len(page_source)} Zeichen")
        
        # Look for success indicators
        indicators = ["grow", "stock", "seeds", "eggs", "gear", "price", "vulcan"]
        found = []
        
        for indicator in indicators:
            if indicator.lower() in page_source.lower():
                found.append(indicator)
        
        if found:
            print(f"SUCCESS! Found indicators: {found}")
            
            # Extract some meaningful content
            lines = page_source.split('\n')
            relevant_lines = []
            
            for line in lines:
                line = line.strip()
                if any(ind.lower() in line.lower() for ind in found) and len(line) > 20:
                    relevant_lines.append(line[:100])
                    if len(relevant_lines) >= 3:
                        break
            
            print("Relevant content found:")
            for line in relevant_lines:
                print(f"  {line}...")
            
            return page_source
        else:
            print("FAILED: No relevant content indicators found")
            print("Page start (first 300 chars):")
            print(page_source[:300])
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {type(e).__name__}: {error_msg}")
        
        if "This version of ChromeDriver only supports Chrome version" in error_msg:
            print("ChromeDriver version mismatch!")
            print("Losche WebDriver Cache und versuche erneut...")
            
            # Clear webdriver cache
            import shutil
            cache_dir = os.path.join(os.path.expanduser("~"), ".wdm")
            if os.path.exists(cache_dir):
                try:
                    shutil.rmtree(cache_dir)
                    print("WebDriver Cache geloscht")
                except:
                    print("Cache loschen fehlgeschlagen")
        
        return False
        
    finally:
        if driver:
            print("Schliesse Browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_selenium_with_latest_driver()
    success = result is not False
    print(f"\nTest Result: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print(f"Successfully retrieved {len(result)} characters")
