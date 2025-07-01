############################################################################
#
# Main python file for scrapping app. Using libraries from requirement.txt
# Martin Hugo
# 2025
#
############################################################################

import pyfiglet
import time
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from datetime import date
import csv
import re
from urllib.parse import urljoin
import sqlite3

from window import App


# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }

# cursor.execute('''CREATE TABLE IF NOT EXISTS products (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     product_name TEXT NOT NULL,
#                     html_content TEXT,
#                     date_added DATE)''')

# response = requests.get(mainAddress, headers=headers)



if __name__ == "__main__":
    window = App(screenName="Scrapping")
    
    window.mainloop()

    # if hrefs == []:
    #     print("[Info] Unable to find products url on this site. If this error persist, maybe the website doesn't work with this script.")
    #     input("[Info] > Press enter to exit the program...")
    #     exit()

    nameBalise = input("\nHTML element for the product's name: ")
    nameKey = input("Select the class name of the product's title: ")
    priceBalise = input("\nHTML element for the product's price: ")
    priceKey = input("Select the class name of the price: ")
    descriptionBalise = input("\nHTML element for the product's description: ")
    descriptionKey = input("Select the class name of the description: ")
    
    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()

    # cursor.execute('''CREATE TABLE IF NOT EXISTS products (
    #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                     product_name TEXT NOT NULL,
    #                     html_content TEXT,
    #                     date_added DATE)''')
    # conn.commit()

    process_product_links(hrefs, "result.csv", nameBalise, nameKey, priceBalise, priceKey, descriptionBalise, descriptionKey)

    # conn.close()
    
    input("[Info] > Results were added to the result.csv file. Press enter to exit the program...")
