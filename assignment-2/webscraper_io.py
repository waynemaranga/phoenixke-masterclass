import httpx
from bs4 import BeautifulSoup
import csv
import time
from typing import Any, Optional
import pathlib

BASE_URL = "https://webscraper.io/test-sites/e-commerce/static/computers/laptops?page={}"
OUTPUT_DIR: pathlib.Path = pathlib.Path(__file__).parent / "output"
OUTPUT_DIR.mkdir(exist_ok=True)  # Ensure output directory exists
OUTPUT: pathlib.Path = OUTPUT_DIR / "my_laptops.csv"

def scrape_page(page_num: int) -> Optional[list[Any]]:
    url: str = BASE_URL.format(page_num)
    try:
        response: httpx.Response = httpx.get(url, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"[!] Failed to fetch page {page_num}: {e}")
        return []  # Continue even if page fails
    
    soup = BeautifulSoup(response.text, features="html.parser")

    items = []
    for box in soup.select(".thumbnail"):
        try:
            title = box.select_one(".title")["title"].strip() # type: ignore
            price = box.select_one(".price").text.strip() # type: ignore
            description = box.select_one(".description").text.strip() # type: ignore
            items.append([title, price, description])
        except Exception:
            continue
    return items

def main() -> None:
    all_items = []
    page = 1
    while True:
        print(f"- Scraping page {page}")
        data = scrape_page(page)
        if not data:
            break
        all_items.extend(data)
        page += 1
        time.sleep(1)

    with open(OUTPUT, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Description"])
        writer.writerows(all_items)

    print(f"✅ Scraped {len(all_items)} items into {OUTPUT}")

if __name__ == "__main__":
    main()
