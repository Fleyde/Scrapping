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


# date = date.today()
# conn = sqlite3.connect('database.db')
# cursor = conn.cursor()

# headers = {
#     'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
# }

# cursor.execute('''CREATE TABLE IF NOT EXISTS products (
#                     id INTEGER PRIMARY KEY AUTOINCREMENT,
#                     product_name TEXT NOT NULL,
#                     html_content TEXT,
#                     date_added DATE)''')
# conn.commit()

# response = requests.get(mainAddress, headers=headers)

# conn.close()



def complete_url_with_base(url_address: str, hrefs: list) -> list:
    """Complete every addresses contained in **hrefs** list with the base url from `url_address` if needed and returns the modified list"""
    match = re.findall(r"http[s]?://[^/]+", url_address)

    if not match:
        print(f"[Info] Error while extracting the base URL from the address '{url_address}'.")

    url_base = re.findall(r"http[s]?://[^/]+", url_address)[0]

    links = [
        link if url_base in link else urljoin(url_base, link)
        for link in hrefs
    ]

    return links



def get_all_product_links(url_adress: str, productsKey) -> list:
    """
    This function returns all links for every product of the page corresponding to the `url_address`
    """
    response = requests.get(url_adress)

    if response.status_code != 200:
        print(f"\n[Info] Error, this site doesn't allow scrapping. Please check the status code for more informations : {response.status_code}")
        return []
    
    soup = BeautifulSoup(response.content, "html.parser")
    hrefs = [a['href'] for a in soup.find_all('a', href=True, class_=productsKey)]
    hrefs = complete_url_with_base(url_adress, hrefs)

    return hrefs


def process_product_links(hrefs: list, filename: str, nameBalise: str, nameKey: str, 
                          priceBalise: str, priceKey: str, descBalise: str, descKey: str) -> None:
    """
    Uses every parameter to extract informations about each product from `hrefs` list using the different parameters and saves it in the `filename`
    file. 
    """
    links_error = []
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file, delimiter=";")

        file_empty = file.tell() == 0
        if file_empty:
            writer.writerow(['Product Title', 'Price', 'Description', 'Product URL', 'Scrapping date'])

        for link in tqdm(hrefs, desc=f"Extraction des données", unit="products", ncols=100):
            response = requests.get(link)

            if response.status_code != 200:
                continue

            soup = BeautifulSoup(response.content, "html.parser")
            soup.prettify()

            try:
                productTitle = soup.find(nameBalise, class_=nameKey).get_text(separator=' ', strip=True)
                price = soup.find(priceBalise, class_=priceKey).get_text(separator=' ', strip=True)
                description = soup.find(descBalise, class_=descKey).get_text(separator=' ', strip=True)

                writer.writerow([productTitle, price, description, link, date.today().isoformat()])

                # cursor.execute('''INSERT INTO products (product_name, html_content, date_added)
                #                   VALUES (?, ?, ?)''', (productTitle, str(soup), date))
                # conn.commit()

            except AttributeError:
                links_error.append(link)
                continue

            time.sleep(1)

    for link in links_error:
        print(f"[Info] Error with the link {link}. You might have to do it manually")

    print("[Info] Task complete. {len(links_error)} errors were detected.")
    
    return 


if __name__ == "__main__":
    print(pyfiglet.figlet_format("Web Scrapping"))

    mainAddress = input("Select URL of the main page: ")
    productsKey = input("Select the class name of each products on the main page: ")

    hrefs = get_all_product_links(mainAddress, productsKey)
    if hrefs == []:
        print("[Info] Unable to find products url on this site. If this error persist, maybe the website doesn't work with this script.")
        input("[Info] > Press enter to exit the program...")
        exit()

    nameBalise = input("\nHTML element for the product's name: ")
    nameKey = input("Select the class name of the product's title: ")
    priceBalise = input("\nHTML element for the product's price: ")
    priceKey = input("Select the class name of the price: ")
    descriptionBalise = input("\nHTML element for the product's description: ")
    descriptionKey = input("Select the class name of the description: ")

    process_product_links(hrefs, "result.csv", nameBalise, nameKey, priceBalise, priceKey, descriptionBalise, descriptionKey)

    input("[Info] > Results were added to the result.csv file. Press enter to exit the program...")
