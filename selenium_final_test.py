from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
import shutil
from datetime import datetime

def clear_webdriver_cache():
    """Löscht den WebDriver Cache für frischen Download"""
    cache_dirs = [
        os.path.join(os.path.expanduser("~"), ".wdm"),
        os.path.join(os.path.expanduser("~"), ".cache", "selenium"),
        os.path.join(os.getenv('LOCALAPPDATA', ''), "webdriver_manager")
    ]
    
    for cache_dir in cache_dirs:
        if os.path.exists(cache_dir):
            try:
                shutil.rmtree(cache_dir)
                print(f"Cache gelöscht: {cache_dir}")
            except Exception as e:
                print(f"Cache löschen fehlgeschlagen: {e}")

def test_selenium_fresh():
    """Test mit frischem ChromeDriver Download"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Selenium Test mit frischem ChromeDriver: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Cache löschen für fresh download
    print("Lösche WebDriver Cache...")
    clear_webdriver_cache()
    
    # Chrome finden
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
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    
    # Aktuelle User-Agent für Chrome 137
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    driver = None
    
    try:
        print("Lade ChromeDriver herunter (kann eine Weile dauern)...")
        
        # Fresh ChromeDriver download
        service = Service(ChromeDriverManager().install())
        
        print("Starte Chrome Browser...")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Maximize detection evasion
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36"
        })
        
        print(f"Navigiere zu: {url}")
        driver.get(url)
        
        print("Initial wait (5 Sekunden)...")
        time.sleep(5)
        
        # Check page source
        page_source = driver.page_source
        print(f"Initial page length: {len(page_source)} Zeichen")
        
        # Detect and handle Cloudflare challenge
        if "Just a moment" in page_source or "Checking your browser" in page_source:
            print("Cloudflare Challenge detected! Waiting for completion...")
            
            challenge_start = time.time()
            max_wait = 45  # 45 seconds max wait
            
            while time.time() - challenge_start < max_wait:
                time.sleep(3)
                current_source = driver.page_source
                elapsed = int(time.time() - challenge_start)
                
                if ("Just a moment" not in current_source and 
                    "Checking your browser" not in current_source and
                    len(current_source) > len(page_source)):  # Content changed
                    
                    print(f"Challenge completed after {elapsed} seconds!")
                    page_source = current_source
                    break
                
                print(f"Challenge still running... {elapsed}s/{max_wait}s")
            else:
                print(f"Challenge timeout after {max_wait} seconds")
        else:
            print("No Cloudflare challenge detected")
        
        # Final analysis
        print(f"Final page length: {len(page_source)} Zeichen")
        
        # Check for VulcanValues content
        content_indicators = [
            "grow", "stock", "seeds", "eggs", "gear", 
            "price", "vulcan", "roblox", "value"
        ]
        
        found_indicators = []
        for indicator in content_indicators:
            if indicator.lower() in page_source.lower():
                found_indicators.append(indicator)
        
        if found_indicators:
            print(f"SUCCESS! Content indicators found: {found_indicators}")
            
            # Show some sample content
            print("\nSample content (first 500 chars):")
            print(page_source[:500])
            print("\n" + "="*50)
            
            return page_source
        else:
            print("FAILED: No VulcanValues content indicators found")
            
            # Show what we got instead
            print("Received content sample:")
            print(page_source[:400])
            
            # Check if it's still a challenge page
            if "cloudflare" in page_source.lower():
                print("Still appears to be a Cloudflare page")
            
            return False
            
    except Exception as e:
        print(f"Selenium Error: {type(e).__name__}: {e}")
        return False
        
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_selenium_fresh()
    success = result is not False
    
    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {'SUCCESS' if success else 'FAILED'}")
    print(f"{'='*60}")
    
    if success:
        print(f"Successfully retrieved {len(result)} characters of stock data!")
        print("Ready to integrate into bot!")
    else:
        print("Could not bypass Cloudflare protection")
        print("May need to try different approach or manual verification")
