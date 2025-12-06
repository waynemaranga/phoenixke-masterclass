# PHOENIX KE ANALYTICS WEB SCRAPING MASTERCLASS

Notes and assignments for the Web Scraping Masterclass by PhoenixKE Analytics.

## Table of Contents
- [PHOENIX KE ANALYTICS WEB SCRAPING MASTERCLASS](#phoenix-ke-analytics-web-scraping-masterclass)
  - [Table of Contents](#table-of-contents)
  - [Assignment 1 - Intro to Web Scraping](#assignment-1---intro-to-web-scraping)
    - [Install \& Run](#install--run)
    - [How-To](#how-to)
  - [Assignment 2 - Multi-Page Web Scraping](#assignment-2---multi-page-web-scraping)
    - [Features](#features)
    - [How-To](#how-to-1)
  - [Assignment 2 Part 2 - Multi-Page Web Scraping on Jumia, with Selenium](#assignment-2-part-2---multi-page-web-scraping-on-jumia-with-selenium)
  - [Assignment 3 - Capstone Project](#assignment-3---capstone-project)
    - [Features:](#features-1)
    - [How-To:](#how-to-2)
    - [`Capstone_Project_Group_7_FINAL`: Detailed function documentation](#capstone_project_group_7_final-detailed-function-documentation)
      - [`get_soup(url: str) -> Optional[BeautifulSoup]`](#get_soupurl-str---optionalbeautifulsoup)
      - [`extract_product_info(article: bs4.element.Tag) -> dict`](#extract_product_infoarticle-bs4elementtag---dict)
      - [`get_categories() -> list[str]`](#get_categories---liststr)
      - [`get_category_pages(category_url: str) -> list[str]`](#get_category_pagescategory_url-str---liststr)
      - [`scrape_category(category_url: str, delay: int = 1) -> list[dict]`](#scrape_categorycategory_url-str-delay-int--1---listdict)


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

### Features

- Uses `httpx` and `BeautifulSoup` for fast, clean scraping.
- Handles errors gracefully using `try...except`.
- Includes `time.sleep()` delays to avoid overloading the server.
- Cleans all extracted text using `.strip()`.
- Saves results to a well-formatted CSV file: `my_books.csv`.

### How-To

1. Scripts are in the [`assignment-2/`](./assignment-2/) directory.
2. Install requirements and setup in Step 1.
3. Run the script [`webscraper-io.py`](./assignment-2/webscraper-io.py)

## Assignment 2 Part 2 - Multi-Page Web Scraping on Jumia, with Selenium

The script [`jumia_scraper.py`](./assignment-2/jumia_scraper.py) is a advanced web scraper for extracting product data from Jumia Kenya's home appliances [`[link]`](https://www.jumia.co.ke/home-office-appliances/) section using Selenium WebDriver. Selenium handles dynamic JavaScript content that static scrapers can't access and automatically navigates through product listing pages.
The title, price, old price, discount, ratings, reviews, and shipping info are collected and saved.
Slight robots.txt compliance; includes rate limiting and respectful crawling practices.

## Assignment 3 - Capstone Project

The notebook [`Capstone_Project_Group_7.ipynb`](./assignment-3/Capstone_Project_Group_7.ipynb) scrapes book data from [http://books.toscrape.com/](http://books.toscrape.com/). It navigates through multiple book categories and handles pagination within each category.

After scraping, the notebook performs data analysis and visualization on the collected data.

### Features:

- Scrapes data by category and handles multi-page navigation within each.
- Extracts **Title**, **Price**, **Availability**, and **Star Rating** for each book.
- Saves the scraped data into separate CSV files for each category (e.g., `travel.csv`, `mystery.csv`).
- Uses `pandas` for data aggregation and analysis.
- Utilizes `matplotlib` and `seaborn` to generate several visualizations:
  - Bar charts for book counts and average prices per category.
  - Box plots for price and rating distributions.
  - A heatmap showing star rating distributions across categories.

### How-To:

1. Scripts are in the [`assignment-3/`](./assignment-3/) directory.
3. Run the notebook: [`Capstone_Project_Group_7.ipynb`](./assignment-3/Capstone_Project_Group_7.ipynb)
4. Check the `output` directory for the generated CSV files and plots.


### [`Capstone_Project_Group_7_FINAL`](./Capstone_Project_Group_7_FINAL.ipynb): Detailed function documentation

This is the core scraping logic for `BooksToScrape.com` as implemented in the notebook.

---
#### `get_soup(url: str) -> Optional[BeautifulSoup]`

Safely fetch HTML content from a URL and parse it using `BeautifulSoup`.Takes a `url` (`str`) for the target webpage and returns either a `BeautifulSoup` object (if the request succeeds) or `None` if the request fails or raises an exception. Performs an HTTP GET request using `requests.get()` with custom headers (`HEADERS`). On success, parses the HTML using:

  ```python
  BeautifulSoup(response.text, "html.parser")
  ```

If an exception is thrown (e.g., timeout, 404), it's caught by:

  ```python
  except requests.exceptions.RequestException as e
  ```

---

#### `extract_product_info(article: bs4.element.Tag) -> dict`

Extracts individual product details from an HTML `<article>` tag. Takes a single `<article class="product_pod">` element representing a book and returns a dictionary with the book's title, price, availability, and rating.

Returns a  `dict` with
  * `'title'`: Title of the book from `article.h3.a["title"]`.
  * `'price'`: Price as string from `article.select_one(".price_color").text.strip()`.
  * `'availability'`: Raw availability text from `article.select_one(".availability").text.strip()`.
  * `'rating'`: Numeric rating from `convert_star_rating(article.select_one("p.star-rating")["class"][1])`.

HTML structure is assumed to be consistent with the website's design. The function uses CSS selectors to extract data. The `convert_star_rating()` function is called to convert the star rating string into an integer.

---

#### `get_categories() -> list[str]`

Scrape all category page links from the homepage.
Returns a list of full category URLs (e.g., `"http://books.toscrape.com/catalogue/category/books/.../"`) Calls `get_soup(BASE_URL)` to fetch the homepage HTML then it locates all category links via:

  ```python
  soup.select("ul.nav-list ul li a")
  ```
It constructs full URLs using a loop:

  ```python
  for link in category_links:
      urljoin(BASE_URL, link["href"])
  ```

> **Loop Highlight**:
>
> * `link`: each `<a>` tag in the category sidebar.
> * Loop aggregates full URLs from relative paths.

---

#### `get_category_pages(category_url: str) -> list[str]`

Return a list of all paginated URLs within a category. Takes parameter `category_url` (`str`) the base URL of a category and returns a list of full URLs for each page in that category e.g `["http://books.toscrape.com/catalogue/category/books/travel_2/page-1.html", ...]`.

**Loop & Iterator**:

* Starts with `next_url = category_url`
* Uses a `while True:` loop to iterate pages.
* On each loop:

  * Calls `get_soup(next_url)`
  * Appends current page to `pages`
  * Checks for `.next > a["href"]`:

    ```python
    next_page = soup.select_one("li.next a")
    ```

    If found, constructs `next_url`; else breaks.

> **Loop Variables**:
>
> * `pages`: Accumulates URLs.
> * `next_page`: HTML anchor tag to next page.
> * `next_url`: updated URL pointing to the next page.

---

#### `scrape_category(category_url: str, delay: int = 1) -> list[dict]`

Scrapes all books in a given category and return as structured data. Parameters are `category_url` the tarting URL for the category and `delay` the delay (in seconds) between requests. Defaults to `1`. Returns a `list[dict]`: All books scraped from the category.

**Core Logic**:

1. Calls `get_category_pages()` to get all paginated URLs.
2. For each page in `pages`:

   ```python
   for page_url in pages:
       soup = get_soup(page_url)
       for article in soup.select("article.product_pod"):
           extract_product_info(article)
   ```

> **Loop Highlights**:
>
> * Outer loop: `page_url` in `pages`.
> * Inner loop: `article` elements on each page.
> * Appends each product dict to `products`.

---
