############################################################################
#
# Main python file for scrapping app. Using libraries from requirement.txt
# EasyScrape - Not like gromoteur
# Martin Hugo
# 2025
#
############################################################################

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
    window = App()
    window.mainloop()
    
    # conn = sqlite3.connect('database.db')
    # cursor = conn.cursor()

    # cursor.execute('''CREATE TABLE IF NOT EXISTS products (
    #                     id INTEGER PRIMARY KEY AUTOINCREMENT,
    #                     product_name TEXT NOT NULL,
    #                     html_content TEXT,
    #                     date_added DATE)''')
    # conn.commit()

    # conn.close()
    