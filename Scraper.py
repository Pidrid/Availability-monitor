import re
import requests
from bs4 import BeautifulSoup

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/91.0.4472.124 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.google.com/",
    "DNT": "1",
}


def check_availability_and_price_on_amazon(url: str) -> tuple[bool, float]:
    if 'https://www.amazon.pl' not in url:
        raise ValueError("Incorrect URL, only Amazon URLs are supported.")

    response = requests.get(url, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')

    # Finding row with price
    price_row_pattern = r'<input id="priceValue" name="priceValue" type="hidden" value="([^"]*)"/>'
    match = re.search(price_row_pattern, bs.prettify())

    if match:
        try:
            price = float(match.group(1))
            return True, price
        except ValueError:
            pass  # If price is not a number, the product is unavailable and price is set to 0.0

    # If there is no price, the product is unavailable
    return False, 0.0


def check_availability_and_price_on_mediaexpert(url: str) -> tuple[bool, float]:
    if 'https://www.mediaexpert.pl' not in url:
        raise ValueError("Incorrect URL, only MediaExpert URLs are supported.")

    response = requests.get(url, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')

    # Finding row with price
    price_row_pattern = r'<meta content="([^"]*)" property="product:price:amount"/>'
    match = re.search(price_row_pattern, bs.prettify())

    price = 0.0
    if match:
        try:
            price = float(match.group(1))
        except ValueError:
            pass  # If price is not a number, it will be set to 0.0

    # Finding row with availability
    availability_row_pattern = r'<meta content="available" property="product:availability"/>'
    match = re.search(availability_row_pattern, bs.prettify())

    if match:
        return True, price

    return False, price