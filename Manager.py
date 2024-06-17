import json

from Product import Product


class Manager:
    def __init__(self, json_file: str):
        self.__json_file = json_file
        self.__products = []
        self.load_products_from_json()

    def save_products_to_json(self):
        products_dictionary = [product.__dict__() for product in self.__products]

        with open(self.__json_file, 'w') as file:
            json.dump(products_dictionary, file, indent=4)

    def load_products_from_json(self):
        with open(self.__json_file, 'r') as file:
            products = json.load(file)

        for product in products:
            self.__products.append(Product(product['name'], product['url'], product['availability_system_notify'],
                                           product['availability_email_notify'], product['price_change_system_notify'],
                                           product['price_change_email_notify'], product['email'], product['price'],
                                           product['is_available'], product['price_history']))

    def add_product(self, name: str, url: str, availability_system_notify: bool = False,
                    availability_email_notify: bool = False, price_change_system_notify: bool = False,
                    price_change_email_notify: bool = False, email: str = "",
                    price: float = 0.0, is_available: bool = False, price_history: dict[str, float] = None):

        product = Product(name, url, availability_system_notify, availability_email_notify, price_change_system_notify,
                          price_change_email_notify, email, price, is_available, price_history)
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

    # def load_products_from_csv(self):
    #     with open(self.csv_file, 'r') as file:
    #         for line in file:
    #
    #
