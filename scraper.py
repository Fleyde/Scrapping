############################################################################
#
# Scraper file containing every function relative to web scraping tools
#
############################################################################

import time
from bs4 import BeautifulSoup
import requests
from datetime import date
import csv
import re
from urllib.parse import urljoin
import sqlite3
import threading


class Scraper():
    def __init__(self, data, log: callable, progress_callback=None):
        self.log_callback = log
        self.progress_callback = progress_callback
        # self.cursor = cursor

        self.mainAddress = data["mainAddress"]
        self.productsKey = data["productsKey"]
        self.nameTag = data["nameTag"]
        self.nameClass = data["nameClass"]
        self.priceTag = data["priceTag"]
        self.priceClass = data["priceClass"]
        self.descriptionTag = data["descriptionTag"]
        self.descriptionClass = data["descriptionClass"]
        self.dbPath = data["dbPath"]
        self.excelPath = data["excelPath"]
        self.forceScraping = data["forceScraping"]

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)
    
    def update_progress(self, current, total):
        if self.progress_callback:
            self.progress_callback(current, total)

    def start_scraping_thread(self, hrefs):
        thread = threading.Thread(
            target=self.process_product_links,
            args=(hrefs,)
        )
        thread.daemon = True
        thread.start()

    def complete_url_with_base(self, url_address: str, hrefs: list) -> list:
        """Complete every addresses contained in **hrefs** list with the base url from `url_address` if needed and returns the modified list"""
        match = re.findall(r"http[s]?://[^/]+", url_address)

        if not match:
            self.log(f"[Info] Error while extracting the base URL from the address '{url_address}'.")

        url_base = re.findall(r"http[s]?://[^/]+", url_address)[0]

        links = [
            link if url_base in link else urljoin(url_base, link)
            for link in hrefs
        ]

        return links



    def get_all_product_links(self) -> list:
        """
        This function returns all links for every product of the page corresponding to the `url_address`
        """
        response = requests.get(self.mainAddress, verify=False)     # Change the verify value !!! Just for test here

        if response.status_code != 200:
            self.log("[ERROR] This site doesn't allow scrapping. Please check the status code for more informations : {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        hrefs = [a['href'] for a in soup.find_all('a', href=True, class_=self.productsKey)]
        hrefs = self.complete_url_with_base(self.mainAddress, hrefs)
        hrefs = list(set(hrefs))
        self.log(f"\n[INFO] Getting informations from the main page : {len(hrefs)} links were found on this page according to the given parameters")

        return hrefs


    def process_product_links(self, hrefs: list, delay:float = 1) -> None:
        """
        Uses every parameter to extract informations about each product from `hrefs` list using the different parameters and saves it in the `filename`
        file. 
        """
        links_error_count = 0
        total = len(hrefs)
        count = 0


        if self.excelPath:
            with open(self.excelPath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")

                file_empty = file.tell() == 0
                if file_empty:
                    writer.writerow(['Product Title', 'Price', 'Description', 'Product URL', 'Scrapping date'])

                for link in hrefs:
                    response = requests.get(link, verify=False)

                    if response.status_code != 200:
                        count += 1
                        self.update_progress(count, total)
                        continue
                    
                    soup = BeautifulSoup(response.content, "html.parser")
                    soup.prettify()

                    try:
                        productTitle = soup.find(self.nameTag, class_=self.nameClass).get_text(separator=' ', strip=True)
                        price = soup.find(self.priceTag, class_=self.priceClass).get_text(separator=' ', strip=True)
                        description = soup.find(self.descriptionTag, class_=self.descriptionClass).get_text(separator=' ', strip=True)

                        writer.writerow([productTitle, price, description, link, date.today().isoformat()])

                        # if self.dbPath:
                        #     self.cursor.execute('''INSERT INTO products (product_name, html_content, date_added)
                        #                     VALUES (?, ?, ?)''', (productTitle, str(soup.body.get_text(" ", strip=True)), date.today().isoformat()))
                        #     self.conn.commit()

                    except AttributeError:
                        self.log("[INFO] Error with the link {link}\n  → You might have to do it manually")
                        links_error_count += 1
                        continue

                    count += 1
                    self.update_progress(count, total)
                    time.sleep(delay)

        else:
            for link in hrefs:
                response = requests.get(link, verify=False)

                if response.status_code != 200:
                    count += 1
                    self.update_progress(count, total)
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                soup.prettify()

                try:
                    productTitle = soup.find(self.nameTag, class_=self.nameClass).get_text(separator=' ', strip=True)
                    price = soup.find(self.priceTag, class_=self.priceClass).get_text(separator=' ', strip=True)
                    description = soup.find(self.descriptionTag, class_=self.descriptionClass).get_text(separator=' ', strip=True)

                    # if self.dbPath:
                    #     self.cursor.execute('''INSERT INTO products (product_name, html_content, date_added)
                    #                     VALUES (?, ?, ?)''', (productTitle, str(soup.body.get_text(" ", strip=True)), date.today().isoformat()))
                    #     self.conn.commit()

                except AttributeError:
                    self.log("[INFO] Error with the link {link}\n  → You might have to do it manually")
                    links_error_count += 1
                    continue

                count += 1
                self.update_progress(count, total)
                time.sleep(delay)


        self.log(f"[Info] Task complete successfully")
        self.log(f"[Info]    → {links_error_count} errors were detected. ")
        self.log("Data were automatically save in the provided files. If no file were precised, nothing has been saved.")




