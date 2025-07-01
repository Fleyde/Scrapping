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
from datetime import date
import csv
import re
from urllib.parse import urljoin
import sqlite3
import tkinter as tk
from window import App



if __name__ == "__main__":
    window = App(screenName="Scrapping")
    
    window.mainloop()