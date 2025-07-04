import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from scraper import Scraper
import requests
from playwright.sync_api import sync_playwright
from config import *


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1280x720")
        self.title("Scraping")
        self.iconbitmap("assets/icon.ico")
        self.configure(padx=10, pady=10)
        self.scraper = None
        self.is_pause = False

        self.create_widgets()
        self.log("[INFO] Welcome to EasySrape, a scraping application designed for shopping websites.")
        self.log(f"[INFO] You can find the source code at the following URL : {APP_REPOT_LINK}")

        # Setting up browser for scraping requests
        self.p = sync_playwright().start()
        self.browser = self.p.chromium.launch(headless=True)
        self.context = self.browser.new_context()
        self.check_latest_version()

        self.log("")


    def check_latest_version(self):
        self.log("[INFO] Checking for updates ...")
        try:
            response = requests.get("https://api.github.com/repos/Fleyde/Scrapping/releases/latest")
            if response.status_code != 200:
                self.log(f"\n[ERROR] Unable to check for lastest version on https://github.com/Fleyde/Scrapping/releases: {response.status_code}")
                return
            latest_version = response.json()['tag_name'][1:]
            if latest_version != APP_VERSION:
                new_version_message = "A new version is availabe on GitHub : https://github.com/Fleyde/Scrapping/releases"
                self.log("[INFO] " + new_version_message)
                messagebox.showinfo("Update available", message=new_version_message)
                return
            self.log("[INFO] Your application is up to date.")
        except Exception as e:
            self.log(f"[INFO] Impossible de vérifier la version : {e}")
            

    def create_widgets(self):
        container = ttk.Frame(self)
        container.pack(fill="both", expand=True)

        # === TOP main area with 2 columns ===
        main_frame = ttk.Frame(container)
        main_frame.pack(fill="x", expand=True)

        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # === Left: Page & Product Info ===
        info_frame = ttk.LabelFrame(main_frame, text="📄 HTML Configuration", padding=15)
        info_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # LEFT: Main page fields
        self.mainAddress_var = tk.StringVar()
        self.productsKey_var = tk.StringVar()
        self._add_labeled_entry(info_frame, 0, "Main page URL:", self.mainAddress_var)
        self._add_labeled_entry(info_frame, 1, "CSS class for product blocks:", self.productsKey_var)

        # LEFT: Product fields
        self.nameTag_var = tk.StringVar()
        self.nameClass_var = tk.StringVar()
        self.priceTag_var = tk.StringVar()
        self.priceClass_var = tk.StringVar()
        self.descriptionTag_var = tk.StringVar()
        self.descriptionClass_var = tk.StringVar()

        product_fields = [
            ("HTML tag for product name:", self.nameTag_var),
            ("CSS class for product name:", self.nameClass_var),
            ("HTML tag for product price:", self.priceTag_var),
            ("CSS class for product price:", self.priceClass_var),
            ("HTML tag for product description:", self.descriptionTag_var),
            ("CSS class for product description:", self.descriptionClass_var),
        ]
        for i, (label, var) in enumerate(product_fields, start=2):
            self._add_labeled_entry(info_frame, i, label, var)

        # === Right: File configuration ===
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        file_frame = ttk.LabelFrame(right_frame, text="📂 Files Configuration", padding=15)
        file_frame.pack(fill="x", expand=True)

        self.db_path = tk.StringVar()
        self.excel_path = tk.StringVar()

        self._add_file_selector(file_frame, 0, "Database file (.db):", self.db_path, DATABASE_TYPE)
        self._add_file_selector(file_frame, 1, "CSV data file (.csv):", self.excel_path, EXCEL_TYPE)

        # === New: Launch configuration frame ===
        launch_frame = ttk.LabelFrame(right_frame, text="🚀 Starting Configuration", padding=15)
        launch_frame.pack(fill="x", expand=True, pady=(10, 0))

        self.force_scraping_var = tk.BooleanVar()
        launch_row = ttk.Frame(launch_frame)
        launch_row.pack(fill="x", pady=(0, 10))

        ttk.Checkbutton(launch_row, text="Force scraping", variable=self.force_scraping_var, command=self._toogle_force).pack(side="left", padx=(0,10))
        self.start_button = ttk.Button(launch_row, text="✅ Start Scraping", command=self.on_submit)
        self.start_button.pack(side="left", padx=5)

        self.pause_button = ttk.Button(launch_row, text="⏸️ Pause Scraping", command=self.handle_pause)
        self.pause_button.pack(side="left", padx=5)
        self.pause_button.config(state="disabled")

        self.stop_button = ttk.Button(launch_row, text="❌ Stop Scraping", command=self.handle_cancel)
        self.stop_button.pack(side="left", padx=5)
        self.stop_button.config(state="disabled")

        warn_message_container = tk.Frame(launch_frame, height=20)
        warn_message_container.pack(fill='x')
        self.text_force = tk.Label(warn_message_container, text="Warning : you are currently using the 'force' option.", fg="orange", font=("Arial", 8))

        # === Progress bar container (invisible at first) ===
        self.progress_container = ttk.Frame(launch_frame)
        self.progress_container.pack(fill="x", pady=(5, 0))
        # Not packing it yet

        self.progress = ttk.Progressbar(self.progress_container, orient="horizontal", mode="determinate", length=400)
        self.progress.pack(side="left", padx=(0, 10))

        self.progress_label = ttk.Label(self.progress_container, text="0 / 0")
        self.progress_label.pack(side="left")

        # === Logs ===
        log_frame = ttk.LabelFrame(container, text="📄 Logs", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(15, 10))

        log_container = ttk.Frame(log_frame)
        log_container.pack(fill="both", expand=True)

        scrollbar = ttk.Scrollbar(log_container, orient="vertical")
        scrollbar.pack(side="right", fill="y")

        self.log_text = tk.Text(log_container, state="disabled", background="#f4f4f4", yscrollcommand=scrollbar.set)
        self.log_text.pack(side="left", fill="both", expand=True)

        scrollbar.config(command=self.log_text.yview)


    def _add_labeled_entry(self, parent, row, label_text, variable):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", pady=5, padx=5)
        entry = ttk.Entry(parent, textvariable=variable, width=45)
        entry.grid(row=row, column=1, pady=5, padx=5)

        info_btn = ttk.Button(parent, text="  ℹ️", width=3, command=self._show_info)
        info_btn.grid(row=row, column=2, padx=5)

    def _add_file_selector(self, parent, row, label_text, variable, type):
        ttk.Label(parent, text=label_text).grid(row=row, column=0, sticky="e", pady=5, padx=5)
        entry = ttk.Entry(parent, textvariable=variable, width=50, state="readonly")
        entry.grid(row=row, column=1, pady=5, padx=5)

        btn_frame = ttk.Frame(parent)
        btn_frame.grid(row=row, column=2, padx=5)

        ttk.Button(btn_frame, text="📂 Browse", command=lambda: self.browse_file(variable, type)).pack(side="left", padx=(0, 5))
        ttk.Button(btn_frame, text="➕ Create", command=lambda: self.create_file(variable, type)).pack(side="left")
        ttk.Button(btn_frame, text="✖", width=3, command=lambda: self.clear_file(variable)).pack(side="left")
        
    def clear_file(self, var:tk.StringVar):
        var.set('')    

    def _toogle_force(self):
        if self.force_scraping_var.get():
            self.text_force.pack(side="left", padx=(0, 10), pady=0)
        else:
            self.text_force.pack_forget()

    def browse_file(self, var:tk.StringVar, type):
        file_path = filedialog.askopenfilename(filetypes=type)
        if file_path:
            var.set(file_path)

    def create_file(self, var:tk.StringVar, type):
        file_path = filedialog.asksaveasfilename(defaultextension=type[0][1][1:], filetypes=type)
        if file_path:
            with open(file_path, 'w+'): pass
            var.set(file_path)



    def _show_info(self):
        top = tk.Toplevel(self)
        top.title("Informations")
        ttk.Label(top, text="Detailed information to be filled in...").pack(padx=20, pady=20)


    def log(self, message):
        self.log_text.configure(state="normal")
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
        self.log_text.configure(state="disabled")



    def on_submit(self):
        if (self.excel_path.get() != ''):
            try:
                with open(self.excel_path.get(), 'r+'):
                    pass
            except IOError as io:
                self.log(f"[ERROR] The CSV file that you want to use is already open or is unavailabe.\n{io}")
                return

        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.pause_button.config(state="normal")
        data = {
            "mainAddress": self.mainAddress_var.get(),
            "productsKey": self.productsKey_var.get(),
            "nameTag": self.nameTag_var.get(),
            "nameClass": self.nameClass_var.get(),
            "priceTag": self.priceTag_var.get(),
            "priceClass": self.priceClass_var.get(),
            "descriptionTag": self.descriptionTag_var.get(),
            "descriptionClass": self.descriptionClass_var.get(),
            "dbPath": self.db_path.get(),
            "excelPath": self.excel_path.get(),
            "forceScraping": self.force_scraping_var.get()
        }

        self.log("\n[INFO] Scraping will start with the following configuration :")
        for key, value in data.items():
            if key == "forceScraping":
                if value:
                    self.log(f"  → {key}: {value}")
                    self.log("\n[WARNING] You are using the ForceScraping option. Make sure you know what you are doing.")
                else:
                    value = False
                    self.log(f"  → {key}: {value}")
            elif value:
                self.log(f"  → {key}: {value}")
            elif key == "dbPath" or key == "excelPath":
                self.log(f"  → {key}: -- Not specified. The data will not be saved to this file. --")
            else:
                self.log(f"\n[ERROR] Missing field. You forgot to specify '{key}'. Please check the configuration.")
                messagebox.showwarning("Field required", "Please enter all required information before starting the program.")
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")
                self.pause_button.config(state="disabled")
                return

        self.scraper = Scraper(data=data, context=self.context, log=self.log, progress_callback=self.update_progress)

        hrefs = self.scraper.get_all_product_links()

        if hrefs == []:
            self.log("[ERROR] Unable to find product URLs on this site. If this error persists, the website may not be compatible with this script.")
            self.start_button.config(state="normal")
            self.stop_button.config(state="disabled")
            self.pause_button.config(state="disabled")
            return
        
        # Setup progress
        self.total_steps = len(hrefs)
        self.current_step = 0
        self.progress["maximum"] = self.total_steps
        self.progress["value"] = 0
        self.progress_label.config(text=f"0 / {self.total_steps} products processed")

        # Show progress UI
        self.progress_container.pack(fill="x", pady=(5, 0))

        self.log("[INFO] Starting scraping ...")
        self.scraper.start_scraping_thread(hrefs)


    def handle_cancel(self):
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        self.pause_button.config(state="disabled")
        self.pause_button.config(text="⏸️ Pause Scraping")
        self.scraper.stop_scraping_thread()

    def handle_pause(self):
        if (self.is_pause):
           self.pause_button.config(text="⏸️ Pause Scraping")
           self.scraper.resume_scraping_thread()
        else:
            self.pause_button.config(text="⏸️ Resume Scraping")
            self.scraper.pause_scraping_thread()
        self.is_pause = not self.is_pause

    def update_progress(self, current, total):
        def callback():
            self.progress["maximum"] = total
            self.progress["value"] = current
            self.progress_label.config(text=f"{current} / {total} products processed")

            if current >= total:
                self.start_button.config(state="normal")
                self.stop_button.config(state="disabled")

        self.after(0, callback)


if __name__ == "__main__":
    app = App()
    app.mainloop()
