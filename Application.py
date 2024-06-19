import sys
import threading
import time

from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import *

from Manager import Manager
from Product import Product


def main():
    try:
        app = QApplication(sys.argv)
        window = QWidget()
        window.resize(1280, 720)
        window.setWindowTitle('Monitor')

        # Creating a manager object and initializing the threads
        manager = Manager('products.json', 'settings.json')
        threading.Thread(target=looking_for_errors_thread, args=(manager,), daemon=True).start()
        manager.start_refresh_thread()

        layout = QVBoxLayout()

        # Settings button
        settings_button = QPushButton('Settings')
        settings_button.clicked.connect(lambda: open_settings_window(manager))
        layout.addWidget(settings_button)

        # Refresh button
        refresh_button = QPushButton('Refresh')
        refresh_button.clicked.connect(lambda: refresh_products_table(manager, products_table))
        layout.addWidget(refresh_button)

        # Table with products
        products_table = QTableWidget()
        products_table.setColumnCount(6)
        products_table.setHorizontalHeaderLabels(
            ['Name', 'Price', 'Availability', 'Settings', 'Remove', 'Price history'])
        products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        products_table.setSelectionMode(QAbstractItemView.SingleSelection)
        products_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(products_table)

        refresh_products_table(manager, products_table)

        # New product button
        new_product_button = QPushButton('New product')
        new_product_button.clicked.connect(lambda: open_new_product_window(manager, products_table))
        layout.addWidget(new_product_button)

        window.setLayout(layout)

        window.show()
        sys.exit(app.exec_())

    except Exception as e:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setText(f"An error occurred: {e}")
        error_message.setWindowTitle("Error")
        error_message.exec_()


def looking_for_errors_thread(manager: Manager):
    while True:
        while manager.errors:
            error_message = QMessageBox()
            error_message.setIcon(QMessageBox.Critical)
            error_message.setText(f"An error occurred: {manager.errors.pop(0)}")
            error_message.setWindowTitle("Error")
            error_message.exec_()

        time.sleep(10)


def refresh_products_table(manager: Manager, products_table: QTableWidget):
    products_table.setRowCount(0)  # Clearing the table

    for product in manager.get_products():
        row_position = products_table.rowCount()
        products_table.insertRow(row_position)

        # Name column
        name_widget = QWidget()
        name_layout = QHBoxLayout(name_widget)
        name_label = QLabel(product.name)
        copy_button = QPushButton('Copy URL')
        copy_button.clicked.connect(lambda _, p=product: QApplication.clipboard().setText(p.get_url()))
        name_layout.addWidget(name_label)
        name_layout.addWidget(copy_button)
        name_layout.setContentsMargins(0, 0, 0, 0)
        name_widget.setLayout(name_layout)
        products_table.setCellWidget(row_position, 0, name_widget)

        # Price column
        price_item = QTableWidgetItem(f"{product.get_price()} PLN")
        products_table.setItem(row_position, 1, price_item)

        # Availability column
        availability_item = QTableWidgetItem('Available' if product.is_available() else 'Not available')
        availability_item.setForeground(QColor('green') if product.is_available() else QColor('red'))
        products_table.setItem(row_position, 2, availability_item)

        # Settings column
        settings_button = QPushButton('Settings')
        settings_button.clicked.connect(lambda _, p=product: open_product_settings_window(manager, products_table, p))
        products_table.setCellWidget(row_position, 3, settings_button)

        # Remove column
        remove_button = QPushButton('Remove')
        remove_button.clicked.connect(lambda _, p=product: remove_product(manager, products_table, p))
        products_table.setCellWidget(row_position, 4, remove_button)

        # Price history column
        price_history_button = QPushButton('Show price history')
        price_history_button.clicked.connect(lambda _, p=product: show_price_history(p))
        products_table.setCellWidget(row_position, 5, price_history_button)


def open_settings_window(manager: Manager):
    dialog = QDialog()
    dialog.setWindowTitle("Settings")
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    # Input for SMP server
    smtp_label = QLabel("SMTP Server:")
    smtp_input = QLineEdit(manager.get_smtp_server())
    layout.addWidget(smtp_label)
    layout.addWidget(smtp_input)

    # Input for SMTP port
    smtp_port_label = QLabel("SMTP port:")
    smtp_port_input = QLineEdit(str(manager.get_smtp_port()))
    layout.addWidget(smtp_port_label)
    layout.addWidget(smtp_port_input)

    # Input for email
    email_label = QLabel("Email:")
    email_input = QLineEdit(manager.get_email_for_notifications())
    layout.addWidget(email_label)
    layout.addWidget(email_input)

    # Input for password
    password_label = QLabel("Password:")
    password_input = QLineEdit(manager.get_email_password())
    password_input.setEchoMode(QLineEdit.Password)
    layout.addWidget(password_label)
    layout.addWidget(password_input)

    # Input for checking frequency
    checking_frequency_label = QLabel("Checking frequency (seconds):")
    checking_frequency_input = QLineEdit(str(manager.get_checking_frequency()))
    layout.addWidget(checking_frequency_label)
    layout.addWidget(checking_frequency_input)

    # Save button
    save_button = QPushButton("Save")
    save_button.clicked.connect(
        lambda: save_settings(manager, dialog, smtp_input, smtp_port_input, email_input, password_input,
                              checking_frequency_input))
    layout.addWidget(save_button)

    dialog.setLayout(layout)
    dialog.exec_()


def save_settings(manager: Manager, dialog: QDialog, smtp_input: QLineEdit, smtp_port_input: QLineEdit,
                  email_input: QLineEdit, password_input: QLineEdit, checking_frequency_input: QLineEdit):
    try:
        new_smtp = smtp_input.text()
        new_port = int(smtp_port_input.text())
        new_email = email_input.text()
        new_password = password_input.text()
        new_frequency = int(checking_frequency_input.text())

        manager.set_smtp_server(new_smtp, new_port)
        manager.set_email_for_notifications(new_email, new_password)
        manager.set_checking_frequency(new_frequency)

        dialog.accept()
    except ValueError as e:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setText(f"An error occurred: {e}")
        error_message.setWindowTitle("Error")
        error_message.exec_()


def open_product_settings_window(manager: Manager, products_table: QTableWidget, product: Product):
    dialog = QDialog()
    dialog.setWindowTitle(f"Settings for {product.name}")
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    # input for name
    name_label = QLabel("Name:")
    name_input = QLineEdit(product.name)
    layout.addWidget(name_label)
    layout.addWidget(name_input)

    # showing url
    url_label = QLabel("URL:")
    url_label_value = QLineEdit(product.get_url())
    url_label_value.setReadOnly(True)
    url_label_value.setFrame(False)
    url_label_value.setStyleSheet("background: transparent;")
    layout.addWidget(url_label)
    layout.addWidget(url_label_value)

    # Checkbox for availability system notification
    availability_system_notification_label = QLabel("Availability System Notification:")
    availability_system_notification_input = QCheckBox()
    availability_system_notification_input.setChecked(product.availability_system_notification)
    layout.addWidget(availability_system_notification_label)
    layout.addWidget(availability_system_notification_input)

    # Checkbox for availability email notification
    availability_email_notification_label = QLabel("Availability Email Notification:")
    availability_email_notification_input = QCheckBox()
    availability_email_notification_input.setChecked(product.availability_email_notification)
    layout.addWidget(availability_email_notification_label)
    layout.addWidget(availability_email_notification_input)

    # Checkbox for price change system notification
    price_change_system_notification_label = QLabel("Price Change System Notification:")
    price_change_system_notification_input = QCheckBox()
    price_change_system_notification_input.setChecked(product.price_change_system_notification)
    layout.addWidget(price_change_system_notification_label)
    layout.addWidget(price_change_system_notification_input)

    # Checkbox for price change email notification
    price_change_email_notification_label = QLabel("Price Change Email Notification:")
    price_change_email_notification_input = QCheckBox()
    price_change_email_notification_input.setChecked(product.price_change_email_notification)
    layout.addWidget(price_change_email_notification_label)
    layout.addWidget(price_change_email_notification_input)

    # input for email
    email_label = QLabel("Email:")
    email_input = QLineEdit(product.email)
    layout.addWidget(email_label)
    layout.addWidget(email_input)

    # Save button
    save_button = QPushButton("Save")
    save_button.clicked.connect(lambda: save_product_settings(manager, product, products_table, dialog,
                                                              name_input,
                                                              availability_system_notification_input,
                                                              availability_email_notification_input,
                                                              price_change_system_notification_input,
                                                              price_change_email_notification_input,
                                                              email_input))
    layout.addWidget(save_button)

    dialog.setLayout(layout)
    dialog.exec_()


def save_product_settings(manager: Manager, product: Product, products_table: QTableWidget, dialog: QDialog,
                          name_input: QLineEdit,
                          availability_system_notification_input: QCheckBox,
                          availability_email_notification_input: QCheckBox,
                          price_change_system_notification_input: QCheckBox,
                          price_change_email_notification_input: QCheckBox,
                          email_input: QLineEdit):
    product.name = name_input.text()
    product.availability_system_notification = availability_system_notification_input.isChecked()
    product.availability_email_notification = availability_email_notification_input.isChecked()
    product.price_change_system_notification = price_change_system_notification_input.isChecked()
    product.price_change_email_notification = price_change_email_notification_input.isChecked()
    product.email = email_input.text()

    manager.save_products_to_json()

    refresh_products_table(manager, products_table)
    dialog.accept()


def remove_product(manager: Manager, products_table: QTableWidget, product: Product):
    confirmation_box = QMessageBox()
    confirmation_box.setIcon(QMessageBox.Question)
    confirmation_box.setWindowTitle("Confirmation")
    confirmation_box.setText(f"Are you sure that you want to remove {product.name}?")
    confirmation_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    confirmation_box.setDefaultButton(QMessageBox.No)
    response = confirmation_box.exec_()

    if response == QMessageBox.Yes:
        manager.remove_product(product)
        refresh_products_table(manager, products_table)


def show_price_history(product: Product):
    dialog = QDialog()
    dialog.setWindowTitle(f"Price history for {product.name}")
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    price_history_table = QTableWidget()
    price_history_table.setColumnCount(2)
    price_history_table.setHorizontalHeaderLabels(['Date', 'Price'])
    price_history_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
    price_history_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    for date, price in product.get_price_history().items():
        row_position = price_history_table.rowCount()
        price_history_table.insertRow(price_history_table.rowCount())
        date_item = QTableWidgetItem(date)
        price_item = QTableWidgetItem(f"{price} PLN")
        price_history_table.setItem(row_position, 0, date_item)
        price_history_table.setItem(row_position, 1, price_item)

    layout.addWidget(price_history_table)

    dialog.setLayout(layout)
    dialog.exec_()


def open_new_product_window(manager: Manager, products_table: QTableWidget):
    dialog = QDialog()
    dialog.setWindowTitle("Add Product")
    dialog.resize(400, 300)

    layout = QVBoxLayout()

    # Input for name
    name_label = QLabel("Name:")
    name_input = QLineEdit()
    layout.addWidget(name_label)
    layout.addWidget(name_input)

    # Input for url
    url_label = QLabel("URL:")
    url_input = QLineEdit()
    layout.addWidget(url_label)
    layout.addWidget(url_input)

    # Checkbox for availability system notification
    availability_system_notification_label = QLabel("Availability System Notification:")
    availability_system_notification_input = QCheckBox()
    layout.addWidget(availability_system_notification_label)
    layout.addWidget(availability_system_notification_input)

    # Checkbox for availability email notification
    availability_email_notification_label = QLabel("Availability Email Notification:")
    availability_email_notification_input = QCheckBox()
    layout.addWidget(availability_email_notification_label)
    layout.addWidget(availability_email_notification_input)

    # Checkbox for price change system notification
    price_change_system_notification_label = QLabel("Price Change System Notification:")
    price_change_system_notification_input = QCheckBox()
    layout.addWidget(price_change_system_notification_label)
    layout.addWidget(price_change_system_notification_input)

    # Checkbox for price change email notification
    price_change_email_notification_label = QLabel("Price Change Email Notification:")
    price_change_email_notification_input = QCheckBox()
    layout.addWidget(price_change_email_notification_label)
    layout.addWidget(price_change_email_notification_input)

    # Input for email
    email_label = QLabel("Email:")
    email_input = QLineEdit()
    layout.addWidget(email_label)
    layout.addWidget(email_input)

    # Add button
    add_button = QPushButton("Add")
    add_button.clicked.connect(lambda: add_product(manager, products_table, dialog,
                                                   name_input,
                                                   url_input,
                                                   availability_system_notification_input,
                                                   availability_email_notification_input,
                                                   price_change_system_notification_input,
                                                   price_change_email_notification_input,
                                                   email_input))

    layout.addWidget(add_button)

    dialog.setLayout(layout)
    dialog.exec_()


def add_product(manager: Manager, products_table: QTableWidget, dialog: QDialog, name_input: QLineEdit,
                url_input: QLineEdit, availability_system_notification_input: QCheckBox,
                availability_email_notification_input: QCheckBox, price_change_system_notification_input: QCheckBox,
                price_change_email_notification_input: QCheckBox, email_input: QLineEdit):
    try:
        manager.add_product(
            name_input.text(),
            url_input.text(),
            availability_system_notification_input.isChecked(),
            availability_email_notification_input.isChecked(),
            price_change_system_notification_input.isChecked(),
            price_change_email_notification_input.isChecked(),
            email_input.text())
    except ValueError as e:
        error_message = QMessageBox()
        error_message.setIcon(QMessageBox.Critical)
        error_message.setText(f"An error occurred: {e}")
        error_message.setWindowTitle("Error")
        error_message.exec_()

    refresh_products_table(manager, products_table)
    dialog.accept()


if __name__ == "__main__":
    main()
