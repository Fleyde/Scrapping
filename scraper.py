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
from playwright.sync_api import sync_playwright, BrowserContext


class Scraper():
    def __init__(self, data, context: BrowserContext, log: callable, progress_callback=None):
        self.context = context
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

    def fetch_links_in_thread(self):
        thread = threading.Thread(
            target=self.get_all_product_links,
        )
        thread.daemon = True
        thread.start()

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



    def get_all_product_links(self, headers=None) -> list:
        """
        This function returns all links for every product of the page corresponding to the `url_address`
        """
        try:
            page = self.context.new_page()
            page.route("**/*", lambda route, request: route.abort()
                        if request.resource_type in ["image", "stylesheet", "font"]
                        else route.continue_())

            if headers:
                    print("test")
                    page.set_extra_http_headers(headers)
            
            response = page.goto(self.mainAddress, wait_until="domcontentloaded", timeout=15000)
            if not response or response.status != 200:
                self.log(f"\n[ERROR] This site does not allow scraping. Please check the status code for more information: {response.status}")
                return []
            
            soup = BeautifulSoup(page.content(), 'html.parser')

            hrefs = [a['href'] for a in soup.find_all('a', href=True, class_=self.productsKey)]
            hrefs = self.complete_url_with_base(self.mainAddress, hrefs)
            hrefs = list(set(hrefs))
            self.log(f"\n[INFO] Retrieving information from the main page: {len(hrefs)} links were found using the provided parameters.")
            page.close()

            return hrefs
        
        except:
            self.log(f"\n[ERROR] The given URL isn't valid : {self.mainAddress}")
            return []
        

    def process_product_links(self, hrefs: list, stop_event: threading.Event, pause_event: threading.Event, delay: float = 1) -> None:
        """
        Extracts product information from each URL in `hrefs` and optionally saves it to a CSV and/or SQLite DB.
        """

        total = len(hrefs)
        count = 0
        error_links = []

        p = sync_playwright().start()
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # ───── 1. Setup database ─────
        if self.dbPath:
            self.conn = sqlite3.connect(self.dbPath)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    product_name TEXT NOT NULL,
                    html_content TEXT,
                    date_added DATE
                )
            ''')
            self.conn.commit()

        # ───── 2. Main loop ─────
        def process_link(link, writer=None):
            pause_event.wait()
            if stop_event.is_set():
                return False

            self.log(f"\n[INFO] Scraping URL: {link}")


            try:
                page = context.new_page()
                page.route("**/*", lambda route, request: route.abort()
                            if request.resource_type in ["image", "stylesheet", "font"]
                            else route.continue_())
                
                if self.headers:
                    page.set_extra_http_headers(self.headers)
                
                response = page.goto(link, wait_until="domcontentloaded", timeout=15000)
                if not response or response.status != 200:
                    self.log(f"[ERROR] Unable to get content (status {response.status})")
                    error_links.append(link)
                    return True
                
                soup = BeautifulSoup(page.content(), 'html.parser')
                title = price = desc = None
                try:
                    title = soup.find(self.nameTag, class_=self.nameClass).get_text(separator=' ', strip=True)
                except Exception as e:
                    self.log("[ERROR] /!\\ Failed to parse the page. Check selectors.")
                    self.log("         → Unbale to find product title")
                    error_links.append(link)
                    self.log(f"{e}")
                    return True
                try:
                    price = soup.find(self.priceTag, class_=self.priceClass).get_text(separator=' ', strip=True)
                except Exception as e:
                    self.log("[ERROR] /!\\ Failed to parse the page. Check selectors.")
                    self.log("         → Unbale to find product price")
                    error_links.append(link)
                    self.log(f"{e}")
                    return True
                try:
                    desc = soup.find(self.descriptionTag, class_=self.descriptionClass).get_text(separator=' ', strip=True)
                except Exception as e:
                    self.log("[ERROR] /!\\ Failed to parse the page. Check selectors.")
                    self.log("         → Unbale to find product description")
                    error_links.append(link)
                    self.log(f"{e}")
                    return True

                self.log("[INFO] Information found:")
                self.log(f"         → Product title: {title}")
                self.log(f"         → Product price: {price}")
                self.log(f"         → Product description: {desc[:500]}")

                # Write to CSV
                if writer:
                    writer.writerow([title, price, desc, link, date.today().isoformat()])

                # Write to DB
                if self.dbPath:
                    html = soup.body.get_text(" ", strip=True)
                    self.cursor.execute(
                        '''INSERT INTO products (product_name, html_content, date_added)
                        VALUES (?, ?, ?)''',
                        (title, html, date.today().isoformat())
                    )
                    self.conn.commit()

                page.close()
                return True

            except Exception as e:
                self.log(f"\n[ERROR] The given URL isn't valid : {link} \n{e}")
                return True
                
        # ───── 3. CSV + scraping ─────
        if self.excelPath:
            with open(self.excelPath, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter=';')

                if file.tell() == 0:
                    writer.writerow(['Product Title', 'Price', 'Description', 'Product URL', 'Scrapping date'])

                for link in hrefs:
                    if not process_link(link, writer):
                        self.log("\n[INFO] Scraping has been cancelled by the user.")
                        break
                    count += 1
                    self.update_progress(count, total)
                    time.sleep(delay)

        else:
            for link in hrefs:
                if not process_link(link, None):
                    self.log("\n[INFO] Scraping has been cancelled by the user.")
                    break
                count += 1
                self.update_progress(count, total)
                time.sleep(delay)

        # ───── 4. Cleanup ─────
        if self.dbPath:
            self.conn.close()

        # ───── 5. Summary ─────
        self.log("\n\n[INFO] Task completed successfully.")
        self.log(f"[INFO]   → {len(error_links)} errors encountered out of {count} processed URLs.")
        for link in error_links:
            self.log(f"          → {link}")
        self.log("[INFO] Data has been automatically saved to the specified files.")

