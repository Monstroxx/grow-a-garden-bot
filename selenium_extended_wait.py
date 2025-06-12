from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
import os
from datetime import datetime

def test_selenium_with_longer_wait():
    """Test mit längerem Wait für Cloudflare Challenge"""
    url = "https://vulcanvalues.com/grow-a-garden/stock"
    
    print(f"Selenium Test mit erweitertem Challenge-Wait: {url}")
    print(f"Zeit: {datetime.now().strftime('%H:%M:%S')}")
    
    # Chrome finden
    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
    if not os.path.exists(chrome_path):
        chrome_path = r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
    
    if not os.path.exists(chrome_path):
        print("Chrome nicht gefunden!")
        return False
    
    print(f"Chrome: {chrome_path}")
    
    # Chrome Optionen (weniger aggressive für bessere Challenge-Behandlung)
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    driver = None
    
    try:
        print("Starte Chrome...")
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print(f"Navigiere zu: {url}")
        driver.get(url)
        
        print("Warte auf Seiten-Load...")
        time.sleep(8)  # Längere Initial-Wait
        
        # Check for challenge multiple times
        for attempt in range(6):  # 6 attempts = bis zu 60 Sekunden
            page_source = driver.page_source
            print(f"Attempt {attempt + 1}: Page length = {len(page_source)} Zeichen")
            
            # Check challenge indicators
            challenge_active = (
                "Nur einen Moment" in page_source or 
                "Just a moment" in page_source or
                "Checking your browser" in page_source or
                "DDoS protection" in page_source
            )
            
            if not challenge_active:
                print("Challenge completed or no challenge!")
                
                # Validate real content
                real_content_indicators = [
                    "Seeds", "Eggs", "Gear", "shop", "price", "cost",
                    "item", "buy", "purchase", "roblox"
                ]
                
                found_real = [ind for ind in real_content_indicators 
                             if ind.lower() in page_source.lower()]
                
                if found_real:
                    print(f"REAL CONTENT FOUND! Indicators: {found_real}")
                    
                    # Extract meaningful sections
                    print("\nContent analysis:")
                    lines = page_source.split('\n')
                    content_lines = []
                    
                    for line in lines:
                        line = line.strip()
                        if any(ind.lower() in line.lower() for ind in found_real):
                            if len(line) > 30 and len(line) < 200:
                                content_lines.append(line)
                                if len(content_lines) >= 5:
                                    break
                    
                    for i, line in enumerate(content_lines, 1):
                        print(f"  {i}: {line}")
                    
                    return page_source
                else:
                    print("Still challenge page content")
            else:
                print(f"Challenge still active (attempt {attempt + 1}/6)")
            
            if attempt < 5:  # Don't wait after last attempt
                print("Warte weitere 10 Sekunden...")
                time.sleep(10)
        
        print("Max wait time reached")
        
        # Final attempt - return what we have
        final_source = driver.page_source
        print(f"Final page length: {len(final_source)}")
        
        # Even if challenge, check for any useful content patterns
        if len(final_source) > 10000:  # Substantial content
            print("Returning substantial content despite possible challenge")
            return final_source
        
        return False
        
    except Exception as e:
        print(f"Error: {type(e).__name__}: {e}")
        return False
        
    finally:
        if driver:
            print("Closing browser...")
            driver.quit()

if __name__ == "__main__":
    result = test_selenium_with_longer_wait()
    success = result is not False
    
    print(f"\n{'='*50}")
    print(f"RESULT: {'SUCCESS' if success else 'FAILED'}")
    print(f"{'='*50}")
    
    if success:
        print(f"Retrieved {len(result)} characters")
        
        # Quick analysis
        challenge_indicators = ["Nur einen Moment", "Just a moment", "Checking your browser"]
        still_challenge = any(ind in result for ind in challenge_indicators)
        
        print(f"Still showing challenge: {'Yes' if still_challenge else 'No'}")
        
        if not still_challenge:
            print("SUCCESS: Real content retrieved!")
        else:
            print("PARTIAL: Challenge page, but some content found")
    else:
        print("FAILED: No useful content retrieved")
