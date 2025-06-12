# Raspberry Pi Selenium Fix für gag-aleart.py
# Füge diese Funktion in den Bot ein, um den System-ChromeDriver zu verwenden

def setup_chrome_driver_raspberry_pi():
    """Erstellt Chrome WebDriver für Raspberry Pi mit System-ChromeDriver"""
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
    
    print("🔧 Initialisiere Chrome WebDriver für Raspberry Pi...")
    
    # Chrome-Pfad für Raspberry Pi
    chrome_paths = [
        "/usr/bin/chromium-browser",
        "/usr/bin/chromium",
        "/usr/bin/google-chrome",
        "/usr/bin/chrome"
    ]
    
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            print(f"✅ Chrome gefunden: {path}")
            break
    
    if not chrome_path:
        raise Exception("❌ Chrome/Chromium Browser nicht gefunden!")
    
    # ChromeDriver-Pfad für Raspberry Pi (System-Installation)
    chromedriver_paths = [
        "/usr/bin/chromedriver",
        "/usr/local/bin/chromedriver",
        "/usr/lib/chromium-browser/chromedriver"
    ]
    
    chromedriver_path = None
    for path in chromedriver_paths:
        if os.path.exists(path):
            chromedriver_path = path
            print(f"✅ ChromeDriver gefunden: {path}")
            break
    
    if not chromedriver_path:
        raise Exception("❌ ChromeDriver nicht gefunden! Installiere mit: sudo apt install chromium-chromedriver")
    
    # Chrome Optionen für Raspberry Pi
    chrome_options = Options()
    chrome_options.binary_location = chrome_path
    chrome_options.add_argument("--headless")  
    chrome_options.add_argument("--no-sandbox") 
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--disable-features=VizDisplayCompositor")
    # Raspberry Pi spezifische Optimierungen
    chrome_options.add_argument("--memory-pressure-off")
    chrome_options.add_argument("--max_old_space_size=4096")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (X11; Linux armv7l) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36")
    
    try:
        # Verwende System-ChromeDriver statt WebDriver-Manager
        service = Service(chromedriver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        # Anti-Detection Maßnahmen
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        _webdriver_instance = driver
        print("✅ Chrome WebDriver erfolgreich initialisiert (Raspberry Pi)")
        return driver
        
    except Exception as e:
        print(f"❌ Chrome WebDriver Setup fehlgeschlagen: {e}")
        raise e

# Ersetze in der setup_chrome_driver() Funktion den Code mit:
# return setup_chrome_driver_raspberry_pi()
