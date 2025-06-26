# Requirements: bs4 (BeautifulSoup), selenium, webdriver-manager
# pip install beautifulsoup4 selenium webdriver-manager 

import csv
import time
from bs4 import BeautifulSoup
from typing import Any
import selenium
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# -- Selenium WebDriver: https://www.selenium.dev/documentation/webdriver/
# The WebDriver drives a browser natively, as a user would, either locally or 
# on a remote machine using the Selenium server. It marks a leap forward in 
# terms of browser automation.
# This helps with dynamic content that requires JavaScript execution, scrolling,
# pagination and other stuff...

def setup_driver() -> WebDriver:
    """Setup Chrome driver with options. https://www.selenium.dev/documentation/webdriver/browsers/chrome/"""
    options = selenium.webdriver.ChromeOptions() # https://www.selenium.dev/documentation/webdriver/browsers/chrome/
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    # Regular user agent; avoids detection as a bot, but doesn't respect Jumia's robots.txt
    options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36") # User-Agent: https://developer.chrome.com/docs/devtools/user-agent/

    # Custom user agent; identifies as a bot, respects Jumia's robots.txt
    # options.add_argument("--user-agent=JumiaScraperBot/1.0 (+https://yourwebsite.com/bot-info; contact@yourdomain.com)")

    
    driver = selenium.webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# --- Parsing the Jumia appliance's page
# This is a custom-made function based on the structure of https://www.jumia.co.ke/home-office-appliances/
# From inspection with dev tools, each product is contained within <article class="prd _fb _spn c-prd col" data-spon="true"></article>
# The product info is in a <div class="info"></div>

def parse_appliance_page(html: str) -> list:
    """Parse HTML and extract product information"""
    soup = BeautifulSoup(html, features='html.parser')
    products = []

    product_cards = soup.select("article.prd._fb.col.c-prd") # Extract all product cards
    print(f"Found {len(product_cards)} product cards on this page")

    for card in product_cards:
        try:
            info = card.select_one("div.info") # Extract the info div which contains product details
            if not info:
                continue
                
            # Extract title and price; every product card has these
            title_elem = info.select_one("h3.name")
            price_elem = info.select_one("div.prc")
            
            if not title_elem or not price_elem:
                continue
                
            title = title_elem.text.strip()
            price = price_elem.text.strip()

            # -- Extract optional fields; not identical for every product
            old_price = ""
            discount = ""
            badge = ""
            rating = ""
            num_reviews = ""
            shipping = ""

            old_div = info.select_one("div.old") # Old price
            if old_div:
                old_price = old_div.text.strip()

            discount_div = info.select_one("div.bdg._dsct._sm") # Discount
            if discount_div:
                discount = discount_div.text.strip()

            badge_div = info.select_one("div.bdg._mall._xs") # Badge (e.g. "Jumia Mall")
            if badge_div:
                badge = badge_div.text.strip()

            rev = info.select_one("div.rev") # Reviews section
            if rev:
                rating_div = rev.select_one("div.stars._s")
                if rating_div:
                    rating = rating_div.text.strip().split(" out")[0]
                
                # Extract number of reviews more safely
                rev_text = rev.get_text()
                if "(" in rev_text and ")" in rev_text:
                    try:
                        num_reviews = rev_text.split("(")[1].split(")")[0]
                    except IndexError:
                        num_reviews = ""

            if info.select_one("svg.ic.xprss"):
                shipping = "Express"

            products.append([title, price, old_price, discount, badge, rating, num_reviews, shipping])
        
        except Exception as e:
            print(f"[!] Skipping product due to error: {e}")
            continue

    return products

def save_to_csv(products, filename):
    """Save products to CSV file"""
    headers = ["Title", "Price", "Old Price", "Discount", "Badge", "Rating", "Number of Reviews", "Shipping"]
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(headers)
        writer.writerows(products)
    
    print(f"✅ Saved {len(products)} products to {filename}")

def main() -> None:
    import pathlib
    OUTPUT_DIR = pathlib.Path(__file__).parent / "output"
    OUTPUT_DIR.mkdir(exist_ok=True)  # Ensure output directory exists
    OUTPUT_FILE = OUTPUT_DIR / "jumia_appliances.csv"

    driver: WebDriver = setup_driver()
    all_products = [] 
    
    try:
        # Scrape multiple pages
        for page_num in range(1, 30):  # Scrape first 10 pages, adjust as needed
            url = f"https://www.jumia.co.ke/home-office-appliances/?page={page_num}#catalog-listing"
            print(f"🕷️  Scraping page {page_num}: {url}")
            
            driver.get(url) # equivalent to requests.get(url) or httpx.get(url) but with Selenium's browser automation
            time.sleep(3)  # Wait for page to load
            
            html: str = driver.page_source # Get the HTML after fully loading the page
            page_products = parse_appliance_page(html)
            
            if not page_products:
                print(f"No products found on page {page_num}, stopping...")
                break
            
            all_products.extend(page_products)
            print(f"Page {page_num}: Found {len(page_products)} products (Total: {len(all_products)})")
            
            # Delay to respect Jumia's rate limits: https://www.jumia.co.ke/robots.txt
            time.sleep(5)

            # Additional features to respect Jumia's robots.txt
            # TODO: rate limit by calculating request rate
            # TODO: check disallowed url patterns i.e *--*, /mobapi/, /en/, facets, paths, other pattern etc
            # TODO: update user agent to identify as a bot
            # TODO: implement error handling for CAPTCHA and HTTP 429 errors
    
    except Exception as e:
        print(f"Error during scraping: {e}")
    
    finally:
        driver.quit() # Close the browser
    
    if all_products:
        save_to_csv(products=all_products, filename=OUTPUT_FILE)
        print(f"✅ Scraping complete! Total products scraped: {len(all_products)}")
        
        # Display first few products as preview
        print("\n📋 Preview of scraped data:")
        for i, product in enumerate(all_products[:5]):
            print(f"{i+1}. {product[0]} - {product[1]}")
    else:
        print("❌ No products were scraped.")

if __name__ == "__main__":
    main()
    print("🐬 Scraping finished!")