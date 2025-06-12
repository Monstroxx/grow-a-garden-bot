from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

def find_chrome_path():
    """Findet Chrome-Installation auf Windows"""
    possible_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Users\{}\AppData\Local\Google\Chrome\Application\chrome.exe".format(os.getenv('USERNAME')),
        r"C:\Program Files\Google\Chrome Beta\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome Beta\Application\chrome.exe"
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Chrome gefunden: {path}")
            return path
    
    print("Chrome nicht gefunden in Standard-Pfaden")
    return None

def test_selenium_chrome_with_path():
    """Test mit explizitem Chrome-Pfad"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Selenium Chrome Test: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Finde Chrome
    chrome_path = find_chrome_path()
    if not chrome_path:
        print("FEHLER: Chrome nicht gefunden!")
        return False
    
    # Chrome Optionen
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")  # Headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--allow-running-insecure-content")
    
    driver = None
    
    try:
        # WebDriver initialisieren
        print("Starte Chrome WebDriver...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-Detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        print("Lade Website...")
        driver.get(url)
        
        # Initial wait
        time.sleep(3)
        
        # Prüfe auf Cloudflare Challenge
        page_source = driver.page_source
        print(f"Initial page length: {len(page_source)} characters")
        
        if "Just a moment" in page_source or "Checking your browser" in page_source:
            print("Cloudflare Challenge detected - waiting...")
            
            # Warte auf Challenge completion
            max_wait = 30
            wait_time = 0
            
            while wait_time < max_wait:
                time.sleep(2)
                wait_time += 2
                current_source = driver.page_source
                
                if "Just a moment" not in current_source and "Checking your browser" not in current_source:
                    print(f"Challenge completed after {wait_time} seconds!")
                    page_source = current_source
                    break
                    
                print(f"Still waiting... ({wait_time}s/{max_wait}s)")
            
            if wait_time >= max_wait:
                print("Challenge timeout!")
                return False
        
        # Analyse final content
        print(f"Final page length: {len(page_source)} characters")
        
        # Check for success indicators
        success_keywords = ["grow", "stock", "seeds", "eggs", "gear", "vulcan"]
        found_keywords = []
        
        for keyword in success_keywords:
            if keyword.lower() in page_source.lower():
                found_keywords.append(keyword)
        
        if found_keywords:
            print(f"SUCCESS! Found keywords: {found_keywords}")
            
            # Show some relevant content
            print("Sample content (first 400 chars):")
            print(page_source[:400])
            print("...")
            
            return page_source
        else:
            print("FAILED: No relevant content found")
            print("Page content sample:")
            print(page_source[:300])
            return False
            
    except Exception as e:
        print(f"Selenium error: {type(e).__name__}: {e}")
        return False
        
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_selenium_chrome_with_path()
    success = result is not False
    print(f"\nSelenium Chrome Test: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print(f"Retrieved {len(result)} characters of data")
