import json
import random
import smtplib
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from plyer import notification

from Product import Product


class Manager:
    def __init__(self, json_file: str, json_settings: str):
        self.__json_file = json_file
        self.__json_settings = json_settings
        self.__products = []
        self.__refresh_time = None
        self.__email_for_notifications = None
        self.__email_password = None
        self.__smtp_server = None
        self.__smtp_port = None
        self.__refresh_thread = None
        self.load_settings_from_json()
        self.load_products_from_json()
        self.errors = []

    def start_refresh_thread(self):
        self.__refresh_thread = threading.Thread(target=self.refresh_products_thread, daemon=True)
        self.__refresh_thread.start()

    def refresh_products_thread(self):
        while True:
            self.refresh_products()
            time.sleep(self.__refresh_time)

    def save_products_to_json(self):
        products_dictionary = [product.__dict__() for product in self.__products]

        with open(self.__json_file, 'w') as file:
            json.dump(products_dictionary, file, indent=4)

    def load_products_from_json(self):
        with open(self.__json_file, 'r') as file:
            try:
                products = json.load(file)
                for product in products:
                    self.__products.append(Product(product['name'], product['url'],
                                                   product['availability_system_notification'],
                                                   product['availability_email_notification'],
                                                   product['price_change_system_notification'],
                                                   product['price_change_email_notification'], product['email'],
                                                   product['price'], product['is_available'], product['price_history']))
            except json.JSONDecodeError:
                pass  # If the file is empty, it will be created with products saving

    def save_settings_to_json(self):
        settings = {
            "refresh_time": self.__refresh_time,
            "email_for_notifications": self.__email_for_notifications,
            "email_password": self.__email_password,
            "smtp_server": self.__smtp_server,
            "smtp_port": self.__smtp_port
        }
        with open(self.__json_settings, 'w') as file:
            json.dump(settings, file, indent=4)

    def load_settings_from_json(self):
        try:
            with open(self.__json_settings, 'r') as file:
                settings = json.load(file)
                self.__refresh_time = settings.get("refresh_time", self.__refresh_time)
                if self.__refresh_time < 30:
                    self.__refresh_time = 30
                    self.save_settings_to_json()
                self.__email_for_notifications = settings.get("email_for_notifications", self.__email_for_notifications)
                self.__email_password = settings.get("email_password", self.__email_password)
                self.__smtp_server = settings.get("smtp_server", self.__smtp_server)
                self.__smtp_port = settings.get("smtp_port", self.__smtp_port)
        except (json.JSONDecodeError, FileNotFoundError):
            raise FileNotFoundError("Settings file not found!")

    def refresh_products(self):
        for product in self.__products:
            is_available = product.is_available()
            price = product.get_price()
            try:
                product.update_price_and_availability()
            except ValueError as e:
                self.errors.append(f"{e} for product: {product.name}")
                continue

            # Checking if the product has changed its availability
            if product.is_available() != is_available:
                if product.availability_system_notification and product.is_available():
                    notification.notify(
                        title="Product is back in stock!",
                        message=f"{product.name} is available now!",
                        app_name="Monitor"
                    )
                if product.availability_email_notification and product.is_available():
                    msg = MIMEMultipart()
                    msg['From'] = self.__email_for_notifications
                    msg['To'] = product.email
                    msg['Subject'] = "Product is back in stock!"
                    msg.attach(MIMEText(f"{product.name} is available now!"))

                    try:
                        with smtplib.SMTP(self.__smtp_server, self.__smtp_port) as server:
                            server.starttls()
                            server.login(self.__email_for_notifications, self.__email_password)
                            server.sendmail(self.__email_for_notifications, msg['To'], msg.as_string())
                    except Exception as e:
                        self.errors.append(f"{e} for product: {product.name}")

                self.save_products_to_json()

            # Checking if the price has changed
            if product.get_price() != price:
                if product.get_price() < price:  # Checking if the price has been reduced
                    if product.price_change_system_notification:
                        notification.notify(
                            title="Product's price got reduced!",
                            message=f"{product.name} price has changed to {product.get_price()} PLN!",
                            app_name="Monitor"
                        )
                    if product.price_change_email_notification:
                        msg = MIMEMultipart()
                        msg['From'] = self.__email_for_notifications
                        msg['To'] = product.email
                        msg['Subject'] = "Product's price got reduced!"
                        msg.attach(MIMEText(f"{product.name} price has changed to {product.get_price()} PLN!"))

                        try:
                            with smtplib.SMTP(self.__smtp_server, self.__smtp_port) as server:
                                server.starttls()
                                server.login(self.__email_for_notifications, self.__email_password)
                                server.sendmail(self.__email_for_notifications, msg['To'], msg.as_string())
                        except Exception as e:
                            self.errors.append(f"{e} for product: {product.name}")

                self.save_products_to_json()

            random_number = random.uniform(0.5, 2)  # Avoiding being blocked by the website
            time.sleep(random_number)

    def add_product(self, name: str, url: str, availability_system_notification: bool = False,
                    availability_email_notification: bool = False, price_change_system_notification: bool = False,
                    price_change_email_notification: bool = False, email: str = "",
                    price: float = 0.0, is_available: bool = False, price_history: dict[str, float] = None):

        product = Product(name, url, availability_system_notification, availability_email_notification,
                          price_change_system_notification, price_change_email_notification,
                          email, price, is_available, price_history)
        try:
            product.update_price_and_availability()
        except ValueError as e:
            raise ValueError(f"{e}")

        self.__products.append(product)

        self.save_products_to_json()

    def remove_product(self, product: Product):
        self.__products.remove(product)

        self.save_products_to_json()

    def get_products(self) -> list[Product]:
        return self.__products

    def change_product_name(self, product: Product, new_name: str):
        product.name = new_name
        self.save_products_to_json()

    def change_product_email(self, product: Product, new_email: str):
        product.email = new_email
        self.save_products_to_json()

    def set_availability_system_notification(self, product: Product, notification_to_set: bool):
        product.availability_system_notification = notification_to_set
        self.save_products_to_json()

    def set_availability_email_notification(self, product: Product, notification_to_set: bool):
        product.availability_email_notification = notification_to_set
        self.save_products_to_json()

    def set_price_change_system_notification(self, product: Product, notification_to_set: bool):
        product.price_change_system_notification = notification_to_set
        self.save_products_to_json()

    def set_price_change_email_notification(self, product: Product, notification_to_set: bool):
        product.price_change_email_notification = notification_to_set
        self.save_products_to_json()

    def get_checking_frequency(self) -> int:
        return self.__refresh_time

    def set_checking_frequency(self, new_frequency: int):
        if new_frequency >= 30:
            self.__refresh_time = new_frequency
        else:
            raise ValueError("Refresh time must be at least 30 seconds!")
        self.save_settings_to_json()

    def get_email_for_notifications(self) -> str:
        return self.__email_for_notifications

    def get_email_password(self) -> str:
        return self.__email_password

    def set_email_for_notifications(self, new_email: str, new_password: str):
        self.__email_for_notifications = new_email
        self.__email_password = new_password
        self.save_settings_to_json()

    def get_smtp_server(self) -> str:
        return self.__smtp_server

    def get_smtp_port(self) -> int:
        return self.__smtp_port

    def set_smtp_server(self, new_server: str, new_port: int):
        self.__smtp_server = new_server
        self.__smtp_port = new_port
        self.save_settings_to_json()
