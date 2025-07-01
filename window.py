import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from scraper import Scraper

EXCEL_TYPE = [("CSV files", "*.csv")]
DATABASE_TYPE = [("Database files", "*.db")]

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.geometry("1280x720")
        self.title("Scraping")
        self.iconbitmap("assets/icon.ico")
        self.configure(padx=10, pady=10)

        self.create_widgets()

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

        ttk.Checkbutton(launch_row, text="Force scraping", variable=self.force_scraping_var, command=self._toogle_force).pack(side="left")
        self.start_button = ttk.Button(launch_row, text="✅ Start Scraping", command=self.on_submit)
        self.start_button.pack(side="left", padx=20)
        self.text_force = tk.Label(launch_row, text="Warning : you are currently using the 'force' option.", fg="orange", font=("Arial", 8))
        # self.text_force.pack(side="left", padx=(0, 10))

        # === Progress bar container (invisible at first) ===
        self.progress_container = ttk.Frame(launch_frame)
        # Not packing it yet

        self.progress = ttk.Progressbar(self.progress_container, orient="horizontal", mode="determinate", length=400)
        self.progress.pack(side="left", padx=(0, 10))

        self.progress_label = ttk.Label(self.progress_container, text="0 / 0")
        self.progress_label.pack(side="left")

        # === Logs ===
        log_frame = ttk.LabelFrame(container, text="📄 Logs", padding=10)
        log_frame.pack(fill="both", expand=True, pady=(15, 10))

        self.log_text = tk.Text(log_frame, state="disabled", background="#f4f4f4")
        self.log_text.pack(fill="both", expand=True)


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

    def _toogle_force(self):
        if self.force_scraping_var.get():
            self.text_force.pack(side="left", padx=(0, 10))
        else:
            self.text_force.pack_forget()


    def browse_file(self, var, type):
        file_path = filedialog.askopenfilename(filetypes=type)
        if file_path:
            var.set(file_path)

    def create_file(self, var, type):
        file_path = filedialog.asksaveasfilename(defaultextension=type[0][1][1:], filetypes=type)
        if file_path:
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
        self.start_button.config(state="disabled")
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

        self.log("[INFO] Scraping will start with the following configuration :")
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
                return

        scraper = Scraper(data=data, log=self.log, progress_callback=self.update_progress)

        hrefs = scraper.get_all_product_links()

        if hrefs == []:
            self.log("[ERROR] Unable to find product URLs on this site. If this error persists, the website may not be compatible with this script.")
            self.start_button.config(state="normal")
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
        scraper.start_scraping_thread(hrefs)


    def update_progress(self, current, total):
        def callback():
            self.progress["maximum"] = total
            self.progress["value"] = current
            self.progress_label.config(text=f"{current} / {total} products processed")

            if current >= total:
                self.start_button.config(state="normal")

        self.after(0, callback)


if __name__ == "__main__":
    app = App()
    app.mainloop()
