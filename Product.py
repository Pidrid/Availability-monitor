from datetime import datetime

import Scraper


class Product:
    def __init__(self, name: str, url: str, availability_system_notify: bool = False,
                 availability_email_notify: bool = False, price_change_system_notify: bool = False,
                 price_change_email_notify: bool = False, email: str = "",
                 price: float = 0.0, is_available: bool = False, price_history: dict[str, float] = None):
        self.name = name
        self.__url = url
        self.availability_system_notify = availability_system_notify
        self.availability_email_notify = availability_email_notify
        self.price_change_system_notify = price_change_system_notify
        self.price_change_email_notify = price_change_email_notify
        self.email = email
        self.__price = price
        self.__is_available = is_available
        if price_history is None:
            self.__price_history = {}
        else:
            self.__price_history = price_history

    def __dict__(self) -> dict:
        return {
            'name': self.name,
            'url': self.__url,
            'availability_system_notify': self.availability_system_notify,
            'availability_email_notify': self.availability_email_notify,
            'price_change_system_notify': self.price_change_system_notify,
            'price_change_email_notify': self.price_change_email_notify,
            'email': self.email,
            'price': self.__price,
            'is_available': self.__is_available,
            'price_history': self.__price_history
        }

    def update_price_and_availability(self):
        try:
            is_available = False
            price = 0.0

            if 'https://www.amazon.pl' in self.__url:
                is_available, price = Scraper.check_availability_and_price_on_amazon(self.__url)
            elif 'https://www.mediaexpert.pl' in self.__url:
                is_available, price = Scraper.check_availability_and_price_on_mediaexpert(self.__url)

            self.__is_available = is_available
            self.__price = price

        except ValueError as e:
            raise ValueError({e})

        # Updating price history if the price has changed
        if len(self.__price_history) == 0 or self.__price != list(self.__price_history.values())[-1]:
            self.__price_history[datetime.now().strftime("%Y-%m-%d %H:%M:%S")] = self.__price

    def get_price(self) -> float:
        return self.__price

    def get_price_history(self) -> dict[str, float]:
        return self.__price_history

    def is_available(self) -> bool:
        return self.__is_available

    def get_url(self) -> str:
        return self.__url
