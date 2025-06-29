# PHOENIX KE ANALYTICS WEB SCRAPING MASTERCLASS

Notes and assignments for the Web Scraping Masterclass by PhoenixKE Analytics.

## Table of Contents
- [PHOENIX KE ANALYTICS WEB SCRAPING MASTERCLASS](#phoenix-ke-analytics-web-scraping-masterclass)
  - [Table of Contents](#table-of-contents)
  - [Assignment 1 - Intro to Web Scraping](#assignment-1---intro-to-web-scraping)
    - [Install \& Run](#install--run)
    - [How-To](#how-to)
  - [Assignment 2 - Multi-Page Web Scraping](#assignment-2---multi-page-web-scraping)
    - [Features:](#features)
    - [How-To:](#how-to-1)
  - [Assignment 2 Part 2 - Multi-Page Web Scraping on Jumia, with Selenium](#assignment-2-part-2---multi-page-web-scraping-on-jumia-with-selenium)

## Assignment 1 - Intro to Web Scraping

The notebook [`assignment_1.ipynb`](./assignment-1/assignment-1.ipynb) scrapes various classified ads from JIJI - [https://www.jiji.co.ke](https://www.jiji.co.ke) and saves the data to JSON files and a CSV file.

### Install & Run

1. Install requirements: `pip install -r requirements.txt`
2. Run the notebook: [`assignment_1.ipynb`](./assignment-1/assignment-1.ipynb)
3. Check the output files in the `output` directory.

### How-To

1. Scoped out webpages;
   - for this case, JIJI - [https://www.jiji.co.ke](https://www.jiji.co.ke) and subpages for vehicles, electronics, property, and home appliances. Each page has a number of classified ads.
2. Identified the data to scrape; for this case, the title, price, and description of each ad. Using browser developer tools, the HTML structure was inspected to find the relevant tags and classes. See screenshots in the [`screenshots/`](./assignment-1/screenshots/) directory.
3. Used BeautifulSoup to parse the HTML and extract the data. The code iterates through each ad, finds the relevant tags, and extracts the text.
4. Saved the data to JSON files and a CSV file in an `output` directory created in the current working directory.

## Assignment 2 - Multi-Page Web Scraping

The script [`webscraper-io.py`](./assignment-2/webscraper-io.py) scrapes book data from all 20 pages of [Web Scraper for Laptops Test Site](https://webscraper.io/test-sites/e-commerce/static/computers/laptops), extracting the **Title**, **Price**, and **Description** of each laptop.

### Features:

- Uses `httpx` and `BeautifulSoup` for fast, clean scraping.
- Handles errors gracefully using `try...except`.
- Includes `time.sleep()` delays to avoid overloading the server.
- Cleans all extracted text using `.strip()`.
- Saves results to a well-formatted CSV file: `my_books.csv`.

### How-To:

1. Scripts are in the [`assignment-2/`](./assignment-2/) directory.
2. Install requirements and setup in Step 1.
3. Run the script [`webscraper-io.py`](./assignment-2/webscraper-io.py)

## Assignment 2 Part 2 - Multi-Page Web Scraping on Jumia, with Selenium

The script [`jumia_scraper.py`](./assignment-2/jumia_scraper.py) is a advanced web scraper for extracting product data from Jumia Kenya's home appliances [`[link]`](https://www.jumia.co.ke/home-office-appliances/) section using Selenium WebDriver. Selenium handles dynamic JavaScript content that static scrapers can't access and automatically navigates through product listing pages.
The title, price, old price, discount, ratings, reviews, and shipping info are collected and saved.
Slight robots.txt compliance; includes rate limiting and respectful crawling practices.
