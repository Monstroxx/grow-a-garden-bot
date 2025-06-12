# Test der Selenium-Integration im Bot
# Testet nur die fetch_stock_data Funktion ohne Discord

import asyncio
import sys
import os

# Füge das Bot-Verzeichnis zum Python-Path hinzu
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock Discord-spezifische Imports für Test
class MockBot:
    pass

class MockCommands:
    @staticmethod
    def Bot(*args, **kwargs):
        return MockBot()

# Mock Discord-Module
sys.modules['discord'] = MockBot()
sys.modules['discord.ext'] = MockBot()
sys.modules['discord.ext.commands'] = MockCommands()
sys.modules['discord.ext.tasks'] = MockBot()

# Jetzt importiere Bot-Funktionen
from dotenv import load_dotenv
load_dotenv()

# Setze STOCK_URL für Test
STOCK_URL = os.getenv('STOCK_URL', 'https://vulcanvalues.com/grow-a-garden/stock')

# Importiere die benötigten Funktionen
# Bot-Datei hat Bindestrich, verwende importlib
import importlib.util

# Verwende absoluten Pfad zur Bot-Datei
bot_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gag-aleart.py")
spec = importlib.util.spec_from_file_location("gag_aleart", bot_path)
gag_aleart = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gag_aleart)

# Verwende Funktionen aus dem Bot
fetch_stock_data = gag_aleart.fetch_stock_data
setup_chrome_driver = gag_aleart.setup_chrome_driver
cleanup_webdriver = gag_aleart.cleanup_webdriver

async def test_selenium_integration():
    """Testet die Selenium-Integration im Bot"""
    print("🧪 Teste Selenium-Integration im Bot...")
    print(f"📡 Stock URL: {STOCK_URL}")
    
    try:
        # Teste WebDriver Setup
        print("\n1️⃣ Teste Chrome WebDriver Setup...")
        driver = setup_chrome_driver()
        if driver:
            print("✅ Chrome WebDriver erfolgreich erstellt")
            driver.quit()  # Sofort schließen für Test
        else:
            print("❌ Chrome WebDriver Setup fehlgeschlagen")
            return False
        
        # Teste Stock-Daten-Abfrage
        print("\n2️⃣ Teste Stock-Daten-Abfrage...")
        stock_data = await fetch_stock_data()
        
        if stock_data:
            print(f"✅ Stock-Daten erfolgreich abgerufen!")
            print(f"📊 Gefundene Items: {len(stock_data)}")
            
            # Zeige erste 5 Items als Beispiel
            print("\n📋 Beispiel-Items:")
            for i, (key, data) in enumerate(list(stock_data.items())[:5]):
                display_name = data.get('display_name', key)
                category = data.get('category', 'Unknown')
                quantity = data.get('quantity', 1)
                print(f"  {i+1}. {display_name} ({category}) x{quantity}")
            
            if len(stock_data) > 5:
                print(f"  ... und {len(stock_data) - 5} weitere Items")
            
            # Kategorien-Statistik
            categories = {}
            for data in stock_data.values():
                cat = data.get('category', 'Unknown')
                categories[cat] = categories.get(cat, 0) + 1
            
            print(f"\n📊 Kategorien-Verteilung:")
            for cat, count in categories.items():
                print(f"  {cat}: {count} Items")
            
            return True
        else:
            print("❌ Keine Stock-Daten erhalten")
            return False
            
    except Exception as e:
        print(f"❌ Test fehlgeschlagen: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print("\n🧹 Cleanup...")
        cleanup_webdriver()

if __name__ == "__main__":
    print("🔥 Selenium-Integration Test")
    print("="*50)
    
    # Überprüfe Umgebungsvariablen
    if not STOCK_URL:
        print("❌ STOCK_URL nicht in .env gesetzt!")
        exit(1)
    
    # Führe Test aus
    result = asyncio.run(test_selenium_integration())
    
    print("\n" + "="*50)
    if result:
        print("🎉 TEST ERFOLGREICH!")
        print("✅ Selenium-Integration funktioniert")
        print("✅ Bot ist bereit für Discord-Betrieb")
    else:
        print("💥 TEST FEHLGESCHLAGEN!")
        print("❌ Probleme mit Selenium-Integration")
        print("🔧 Überprüfe Chrome-Installation und Netzwerk")
    
    print(f"\nTest abgeschlossen: {'SUCCESS' if result else 'FAILED'}")
