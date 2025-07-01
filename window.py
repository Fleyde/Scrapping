import tkinter as tk
from tkinter import ttk, messagebox


class App(tk.Tk):
    def __init__(self, screenName=None, baseName=None, className="Tk", useTk=True, sync=False, use=None):
        super().__init__(screenName, baseName, className, useTk, sync, use)

        self.geometry("1280x720")
        self.title("Scraper Configuration")

        self.create_widgets()

    def create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(expand=True)

        # Section: Main page info
        ttk.Label(main_frame, text="🧭 Main Page", font=("Helvetica", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky="w")

        self.mainAddress_var = tk.StringVar()
        self.productsKey_var = tk.StringVar()

        ttk.Label(main_frame, text="Main page URL:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.mainAddress_var, width=60).grid(row=1, column=1, pady=5)

        ttk.Label(main_frame, text="CSS class of product blocks:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        ttk.Entry(main_frame, textvariable=self.productsKey_var, width=60).grid(row=2, column=1, pady=5)

        # Section: Product info
        ttk.Label(main_frame, text="📦 Product Information", font=("Helvetica", 14, "bold")).grid(row=3, column=0, columnspan=2, pady=(20, 10), sticky="w")

        self.nameTag_var = tk.StringVar()
        self.nameClass_var = tk.StringVar()
        self.priceTag_var = tk.StringVar()
        self.priceClass_var = tk.StringVar()
        self.descriptionTag_var = tk.StringVar()
        self.descriptionClass_var = tk.StringVar()

        labels = [
            ("HTML tag for product name:", self.nameTag_var),
            ("CSS class for product name:", self.nameClass_var),
            ("HTML tag for product price:", self.priceTag_var),
            ("CSS class for product price:", self.priceClass_var),
            ("HTML tag for product description:", self.descriptionTag_var),
            ("CSS class for product description:", self.descriptionClass_var),
        ]

        for i, (label_text, var) in enumerate(labels):
            ttk.Label(main_frame, text=label_text).grid(row=4 + i, column=0, sticky="e", padx=5, pady=5)
            ttk.Entry(main_frame, textvariable=var, width=60).grid(row=4 + i, column=1, pady=5)

        # Submit button
        ttk.Button(main_frame, text="✅ Start scraping", command=self.on_submit).grid(
            row=10, column=0, columnspan=2, pady=30
        )

    def on_submit(self):
        data = {
            "mainAddress": self.mainAddress_var.get(),
            "productsKey": self.productsKey_var.get(),
            "nameTag": self.nameTag_var.get(),
            "nameClass": self.nameClass_var.get(),
            "priceTag": self.priceTag_var.get(),
            "priceClass": self.priceClass_var.get(),
            "descriptionTag": self.descriptionTag_var.get(),
            "descriptionClass": self.descriptionClass_var.get(),
        }

        if not data["mainAddress"] or not data["productsKey"]:
            messagebox.showwarning("Missing Fields", "Please fill in both the main page URL and the product block class.")
            return

        # Placeholder: Replace with your actual scraping logic
        print("[INFO] User input:")
        for key, value in data.items():
            print(f"{key}: {value}")


# If launched directly
if __name__ == "__main__":
    app = App()
    app.mainloop()
