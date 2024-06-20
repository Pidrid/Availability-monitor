# Availability monitor
Author - [Piotr Schubert](https://github.com/Pidrid)

This project was developed for academic purposes as part of Języki Skryptowe (Scripting Languages) course at Wrocław University of Science and Technology.

## Application Description
Availability montior is an application, where user can add products from amazon.pl or mediaexpert.pl to check their availability and price. When the product is back to stock or got reduced price, user can get notification via email or system.

## Application Architecture
The application consists 4 python and 2 json files: 
- `Scraper.py` responsible for scraping content from websites and checking availability and price.
- `Product.py` containing Product class
- `Manager.py` containing Manager class with all the logic behind application
- `Application.py` responsible for GUI
- `products.json` with all the products stored
- `settings.json` with application settings

## Application Features
- User can see table with products with: product name, price, availability
- User can refresh the table with products
- User can add products.
- User can change product settings: name, email and notifications
- User can remove product
- User can copy url of product
- User can see price history of product
- User can change settings: smpt server, smpt port, email for notifications (with password), checking frequency


## Technologies
- Python
- BeautifulSoup
- plyer
- PyQt5

## Launch
To run the application, execute the `Application.py` script.  
Application settings can be changed directly within the application or through the `settings.json` file.
