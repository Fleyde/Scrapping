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
        self.headers = {}
        self.stop_event = threading.Event()
        self.pause_event = threading.Event()

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

        if self.forceScraping:
            self.headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

    def log(self, msg):
        if self.log_callback:
            self.log_callback(msg)
        else:
            print(msg)
    
    def update_progress(self, current, total):
        if self.progress_callback:
            self.progress_callback(current, total)

    def start_scraping_thread(self, hrefs):
        self.pause_event.set()
        thread = threading.Thread(
            target=self.process_product_links,
            args=(hrefs, self.stop_event, self.pause_event)
        )
        thread.daemon = True
        thread.start()

    def stop_scraping_thread(self):
        self.stop_event.set()
        self.pause_event.set()

    def pause_scraping_thread(self):
        self.pause_event.clear()

    def resume_scraping_thread(self):
        self.pause_event.set()

    def complete_url_with_base(self, url_address: str, hrefs: list) -> list:
        """Complete every addresses contained in **hrefs** list with the base url from `url_address` if needed and returns the modified list"""
        try:
            match = re.findall(r"http[s]?://[^/]+", url_address)
        except AttributeError:
            self.log(f"\n[ERROR] The given URL isn't valid : {url_address}")
            return []

        if not match:
            self.log(f"[INFO] Failed to extract the base URL from the address '{url_address}'.")


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
        try:
            response = requests.get(self.mainAddress, verify=False, headers=self.headers)     # Change the verify value !!! Just for test here
        except:
            self.log(f"\n[ERROR] The given URL isn't valid : {self.mainAddress}")
            return []

        if response.status_code != 200:
            self.log(f"\n[ERROR] This site does not allow scraping. Please check the status code for more information: {response.status_code}")
            return []
        
        soup = BeautifulSoup(response.content, "html.parser")
        hrefs = [a['href'] for a in soup.find_all('a', href=True, class_=self.productsKey)]
        hrefs = self.complete_url_with_base(self.mainAddress, hrefs)
        hrefs = list(set(hrefs))
        self.log(f"\n[INFO] Retrieving information from the main page: {len(hrefs)} links were found using the provided parameters.")

        return hrefs


    def process_product_links(self, hrefs: list, stop_event: threading.Event, pause_event: threading.Event, delay:float = 1) -> None:
        """
        Uses every parameter to extract informations about each product from `hrefs` list using the different parameters and saves it in the `filename`
        file. 
        """
        total = len(hrefs)
        errors_link_list = []
        count = 0

        # Creating databse access in the same thread as the processing function
        if self.dbPath:
            self.conn = sqlite3.connect(self.dbPath)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        product_name TEXT NOT NULL,
                        html_content TEXT,
                        date_added DATE)''')
            self.conn.commit()

        if self.excelPath:
            with open(self.excelPath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=";")

                file_empty = file.tell() == 0
                if file_empty:
                    writer.writerow(['Product Title', 'Price', 'Description', 'Product URL', 'Scrapping date'])

                for link in hrefs:
                    pause_event.wait() 
                    if stop_event.is_set():
                        self.log("\n[INFO] Scraping has been cancelled by the user.")
                        if self.dbPath:
                            self.conn.close()
                        break
                     
                    self.log(f"\n[INFO] Scraping URL : {link}")
                    response = requests.get(link, verify=False, headers=self.headers)

                    if response.status_code != 200:
                        count += 1
                        self.update_progress(count, total)
                        errors_link_list.append(link)
                        self.log(f"[ERROR] Unable to get the content of this page. Status code error : {response.status_code}")
                        continue
                    
                    soup = BeautifulSoup(response.content, "html.parser")
                    soup.prettify()

                    try:
                        productTitle = soup.find(self.nameTag, class_=self.nameClass).get_text(separator=' ', strip=True)
                        price = soup.find(self.priceTag, class_=self.priceClass).get_text(separator=' ', strip=True)
                        description = soup.find(self.descriptionTag, class_=self.descriptionClass).get_text(separator=' ', strip=True)

                        self.log(f"[INFO] Information found : ")
                        self.log(f"         → Product title : {productTitle}")
                        self.log(f"         → Product price : {price}")
                        self.log(f"         → Product description : {description[:500]}")

                        writer.writerow([productTitle, price, description, link, date.today().isoformat()])

                        if self.dbPath:
                            self.cursor.execute('''INSERT INTO products (product_name, html_content, date_added)
                                            VALUES (?, ?, ?)''', (productTitle, str(soup.body.get_text(" ", strip=True)), date.today().isoformat()))
                            self.conn.commit()

                    except AttributeError:
                        self.log("[ERROR] /!\\ Error with this link ...\n  →  You might need to handle it manually")
                        errors_link_list.append(link)
                        count += 1
                        self.update_progress(count, total)
                        continue

                    count += 1
                    self.update_progress(count, total)
                    time.sleep(delay)

        else:
            for link in hrefs:
                pause_event.wait() 
                if stop_event.is_set():
                    self.log("\n[INFO] Scraping has been cancelled by the user.")
                    if self.dbPath:
                        self.conn.close()
                    break
                
                self.log(f"\n[INFO] Scraping URL : {link}")
                response = requests.get(link, verify=False, headers=self.headers)

                if response.status_code != 200:
                    count += 1
                    self.update_progress(count, total)
                    errors_link_list.append(link)
                    self.log(f"[ERROR] Unable to get the content of this page. Status code error : {response.status_code}")
                    continue

                soup = BeautifulSoup(response.content, "html.parser")
                soup.prettify()

                try:
                    productTitle = soup.find(self.nameTag, class_=self.nameClass).get_text(separator=' ', strip=True)
                    price = soup.find(self.priceTag, class_=self.priceClass).get_text(separator=' ', strip=True)
                    description = soup.find(self.descriptionTag, class_=self.descriptionClass).get_text(separator=' ', strip=True)

                    self.log(f"[INFO] Information found : ")
                    self.log(f"         → Product title : {productTitle}")
                    self.log(f"         → Product price : {price}")
                    self.log(f"         → Product description : {description[:500]}")
                    
                    if self.dbPath:
                        self.cursor.execute('''INSERT INTO products (product_name, html_content, date_added)
                                        VALUES (?, ?, ?)''', (productTitle, str(soup.body.get_text(" ", strip=True)), date.today().isoformat()))
                        self.conn.commit()

                except AttributeError:
                    self.log("[ERROR] /!\\ Error with this link : unable to find informations on the page ... \n  →  You might need to handle it manually")
                    errors_link_list.append(link)
                    count += 1
                    self.update_progress(count, total)
                    continue

                count += 1
                self.update_progress(count, total)
                time.sleep(delay)

        if self.dbPath:
            self.conn.close()

        self.log(f"\n\n[INFO] Task completed successfully.")
        self.log(f"          → {len(errors_link_list)} errors were encountered out of {count} products.")
        for link in errors_link_list:
            self.log(f"                    → {link}")
        self.log("[INFO] Data has been automatically saved to the specified files. If no file was provided, nothing has been saved.")




