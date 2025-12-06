import os
import csv
import time
import sqlite3
import httpx
import pandas as pd
from bs4 import BeautifulSoup
from tenacity import retry, wait_fixed, stop_after_attempt
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

BASE_URL = "http://books.toscrape.com/"
OUTPUT_DIR = "output"
SLEEP_TIME = 1

chrome_options = Options()
chrome_options.add_argument("--headless=new")
driver = webdriver.Chrome(options=chrome_options)

@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def fetch_html(url):
    with httpx.Client(timeout=10.0) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text

def convert_star_rating(star_str):
    stars = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    return stars.get(star_str, 0)

def extract_product_info(product_el):
    title = product_el.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title").strip()
    rel_url = product_el.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("href")
    product_url = rel_url if "http" in rel_url else BASE_URL + "catalogue/" + rel_url.split('/')[-2] + "/index.html"

    price = product_el.find_element(By.CLASS_NAME, "price_color").text.strip().replace("£", "")
    availability = product_el.find_element(By.CLASS_NAME, "availability").text.strip()
    star_classes = product_el.get_attribute("class")
    for class_name in star_classes.split():
        if class_name in ["One", "Two", "Three", "Four", "Five"]:
            star_rating = convert_star_rating(class_name)
            break
    else:
        star_rating = 0

    return (title, float(price), availability, star_rating, product_url)

def get_category_urls():
    driver.get(BASE_URL)
    links = driver.find_elements(By.CSS_SELECTOR, ".side_categories ul li ul li a")
    return {link.text.strip(): link.get_attribute("href") for link in links}

def get_category_pages(category_url):
    driver.get(category_url)
    pages = [driver.current_url]
    try:
        pager = driver.find_element(By.CLASS_NAME, "current")
        total_pages = int(pager.text.strip().split()[-1])
        base = category_url.replace("index.html", "")
        pages = [f"{base}page-{i}.html" for i in range(1, total_pages + 1)]
    except:
        pass
    return pages

def scrape_category(name, url):
    print(f"[INFO] Scraping: {name}")
    all_data = []
    for page_url in get_category_pages(url):
        driver.get(page_url)
        time.sleep(SLEEP_TIME)
        products = driver.find_elements(By.CSS_SELECTOR, "article.product_pod")
        for p in products:
            try:
                data = extract_product_info(p)
                all_data.append(data)
            except Exception as e:
                print(f"[WARN] Skipping product due to: {e}")
    save_to_csv(name, all_data)
    return all_data

def save_to_csv(category, data):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, f"{category.replace(' ', '_').lower()}.csv")
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price", "Availability", "Star Rating", "URL"])
        writer.writerows(data)

def save_to_db(data, db_path, table_name):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY,
            title TEXT,
            price REAL,
            availability TEXT,
            star_rating INTEGER,
            url TEXT
        )
    """)
    cursor.executemany(f"""
        INSERT INTO {table_name} (title, price, availability, star_rating, url)
        VALUES (?, ?, ?, ?, ?)
    """, data)
    conn.commit()
    conn.close()

def scrape_site(db_path, limit=None):
    categories = get_category_urls()
    selected = list(categories.items())[:limit] if limit else categories.items()
    for name, url in selected:
        data = scrape_category(name, url)
        save_to_db(data, db_path, name.replace(" ", "_").lower())

if __name__ == "__main__":
    print("→ Scraping 5 categories into mini.db")
    scrape_site("mini.db", limit=5)

    print("\n→ Scraping ALL categories into full.db")
    scrape_site("full.db")

    driver.quit()
