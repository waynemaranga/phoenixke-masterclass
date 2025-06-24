# PHOENIXKE ANALYTICS WEB SCRAPING MASTERCLASS
## Assignment 1 - Intro to Web Scraping

The notebook [`assignment_1.ipynb`](./assignment-1/assignment-1.ipynb) scrapes various classified ads from JIJI - [https://www.jiji.co.ke](https://www.jiji.co.ke) and saves the data to JSON files and a CSV file.

## Install & Run
1. Install requirements: `pip install -r requirements.txt`
2. Run the notebook: [`assignment_1.ipynb`](./assignment-1/assignment-1.ipynb)
3. Check the output files in the `output` directory.

## How-To
1. Scoped out webpages;
   - for this case, JIJI - [https://www.jiji.co.ke](https://www.jiji.co.ke) and subpages for vehicles, electronics, property, and home appliances. Each page has a number of classified ads.
2. Identified the data to scrape; for this case, the title, price, and description of each ad. Using browser developer tools, the HTML structure was inspected to find the relevant tags and classes. See screenshots in the [`screenshots`](./assignment-1/screenshots/) directory.
3. Used BeautifulSoup to parse the HTML and extract the data. The code iterates through each ad, finds the relevant tags, and extracts the text.
4. Saved the data to JSON files and a CSV file in an `output` directory created in the current working directory.
5. *TODO: Use Selenium to beat pagination*