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


def check_availability_and_price_on_amazon(url):
    if 'https://www.amazon.pl' not in url:
        raise ValueError("Incorrect URL, only Amazon URLs are supported.")

    response = requests.get(url, headers=headers)
    bs = BeautifulSoup(response.text, 'html.parser')

    # Finding row with price
    regex_pattern = r'<input id="priceValue" name="priceValue" type="hidden" value="([^"]*)"/>'
    match = re.search(regex_pattern, bs.prettify())

    if match:
        value = match.group(1)
        if value.isdecimal():
            return True, float(value)

    # If there is no price, the product is unavailable
    return False, 0.0
