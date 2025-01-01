import csv
from time import sleep
from datetime import datetime
from random import random
from selenium.common import exceptions
# from msedge.selenium_tools import Edge, EdgeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
from selenium import webdriver
from bs4 import BeautifulSoup

def generate_filename(search_term):
    timestamp = datetime.now().strftime("%Y%m%d%H%S%M")
    stem = path = '_'.join(search_term.split(' '))
    filename = stem + '_' + timestamp + '.csv'
    return filename


def save_data_to_csv(record, filename, new_file=False):
    header = ['description', 'price', 'rating', 'review_count', 'url']
    if new_file:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
    else:
        with open(filename, 'a+', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(record)


# def create_webdriver() -> Edge:
#     options = EdgeOptions()
#     options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
#     options.use_chromium = True
#     options.headless = True
#     driver = Edge(options=options)
#     return driver

def create_webdriver() -> webdriver.Firefox:
    options = Options()
    # Set user agent
    options.set_preference("general.useragent.override", 
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    options.headless = True  # Enable headless mode

    # Initialize the Firefox driver
    driver = webdriver.Firefox(options=options, executable_path="D:\Python\scraping\Amazon\geckodriver.exe")
    return driver


def generate_url(search_term, page):
    base_template = 'https://www.amazon.com/s?k={}&ref=nb_sb_noss_1'
    search_term = search_term.replace(' ', '+')
    stem = base_template.format(search_term)
    url_template = stem + '&page={}'
    if page == 1:
        return stem
    else:
        return url_template.format(page)

def extract_card_data(item):
    atag = item.find("h2", class_="a-size-medium")
    
    description = atag.text.strip() if atag else None
    print(description)
    try:
        # product price
        price_tag = item.find("span", class_="a-offscreen")
        price = price_tag.text.strip() if price_tag else None
    except AttributeError:
        return
    
    try:
        # review count
        review_tag = item.find("span", class_="a-size-base")
        review_count = review_tag.text.strip() if review_tag else None

        # Product URL
        url_tag = item.find("a", class_="a-link-normal")
        url = f"https://www.amazon.com{url_tag['href']}" if url_tag else None

        rating_tag = item.find("i", class_="a-icon-star-small")
        rating = rating_tag.find("span", class_="a-icon-alt").text.strip() if rating_tag else None
    except AttributeError:
        rating = ''
        review_count = ''
        
    result = (description, price, rating, review_count, url)
    return result

def collect_product_cards_from_page(driver):
    cards = driver.find_elements_by_xpath('//div[@data-component-type="s-search-result"]')
    return cards


def sleep_for_random_interval():
    time_in_seconds = random() * 2
    sleep(time_in_seconds)


def run(search_term):
    """Run the Amazon webscraper"""
    filename = generate_filename(search_term)
    save_data_to_csv(None, filename, new_file=True)  # initialize a new file
    driver = create_webdriver()
    num_records_scraped = 0

    for page in range(1, 21):  # max of 20 pages
        # load the next page
        search_url = generate_url(search_term, page)
        driver.get(search_url.format(page))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        cards = soup.find_all('div', {'data-component-type': 's-search-result'})
        for card in cards:
            record = extract_card_data(card)
            if record:
                save_data_to_csv(record, filename)
                num_records_scraped += 1
        sleep_for_random_interval()

    # shut down and report results
    driver.quit()
    print(f"Scraped {num_records_scraped:,d} for the search term: {search_term}")


if __name__ == '__main__':
    term = 'hp laptop'
    run(term)