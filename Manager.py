import json
import random
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from plyer import notification

from Product import Product


class Manager:
    def __init__(self, json_file: str, refresh_time: int, email_for_notifications: str, email_password: str,
                 smtp_server: str, smtp_port: int):
        self.__json_file = json_file
        self.__products = []
        self.__refresh_time = refresh_time
        self.__email_for_notifications = email_for_notifications
        self.__email_password = email_password
        self.__smtp_server = smtp_server
        self.__smtp_port = smtp_port
        self.load_products_from_json()

    def save_products_to_json(self):
        products_dictionary = [product.__dict__() for product in self.__products]

        with open(self.__json_file, 'w') as file:
            json.dump(products_dictionary, file, indent=4)

    def load_products_from_json(self):
        with open(self.__json_file, 'r') as file:
            try:
                products = json.load(file)
            except json.JSONDecodeError:
                return  # If the file is empty, it will be created with products saving

            for product in products:
                self.__products.append(Product(product['name'], product['url'],
                                               product['availability_system_notification'],
                                               product['availability_email_notification'],
                                               product['price_change_system_notification'],
                                               product['price_change_email_notification'], product['email'],
                                               product['price'], product['is_available'], product['price_history']))

    def refresh_products(self):
        for product in self.__products:
            is_available = product.is_available()
            price = product.get_price()

            product.update_price_and_availability()

            # Checking if the product is back in stock
            if product.is_available() and not is_available:
                if product.availability_system_notification:
                    notification.notify(
                        title="Product is back in stock!",
                        message=f"{product.name} is available now!",
                        app_name="Monitor"
                    )
                if product.availability_email_notification:
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
                        raise Exception(f"{e}")

                self.save_products_to_json()

            # Checking if the price has changed
            if product.get_price() != price:
                if product.price_change_system_notification:
                    notification.notify(
                        title="Product got price change!",
                        message=f"{product.name} price has changed to {product.get_price()} PLN!",
                        app_name="Monitor"
                    )
                if product.price_change_email_notification:
                    msg = MIMEMultipart()
                    msg['From'] = self.__email_for_notifications
                    msg['To'] = product.email
                    msg['Subject'] = "Product got price change!"
                    msg.attach(MIMEText(f"{product.name} price has changed to {product.get_price()} PLN!"))

                    try:
                        with smtplib.SMTP(self.__smtp_server, self.__smtp_port) as server:
                            server.starttls()
                            server.login(self.__email_for_notifications, self.__email_password)
                            server.sendmail(self.__email_for_notifications, msg['To'], msg.as_string())
                    except Exception as e:
                        raise Exception(f"{e}")

                self.save_products_to_json()

            random_number = random.uniform(0.5, 2.5)  # Avoiding being blocked by the website
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
