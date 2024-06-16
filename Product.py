from datetime import datetime
import Scraper


class Produkt:
    def __init__(self, name: str, url: str, price: float = 0.0, availability_system_notify: bool = False,
                 availability_email_notify: bool = False, price_change_system_notify: bool = False,
                 price_change_email_notify: bool = False, email: str = "", is_available: bool = False):
        self.name = name
        self.url = url
        self.price = price
        self.availability_system_notify = availability_system_notify
        self.availability_email_notify = availability_email_notify
        self.price_change_system_notify = price_change_system_notify
        self.price_change_email_notify = price_change_email_notify
        self.email = email
        self.is_available = is_available
        self.price_history = {}

    def update_price_and_availability(self):
        try:
            is_available = False
            price = 0.0
            if 'https://www.amazon.pl' in self.url:
                is_available, price = Scraper.check_availability_and_price_on_amazon(self.url)
            self.is_available = is_available
            self.price = price
        except ValueError as e:
            print(e)

        # Updating price history if the price has changed
        if len(self.price_history) == 0 or self.price != self.price_history[list(self.price_history.values())[-1]]:
            self.price_history[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = self.price
