# Scrapping
Scrapping application for research

install command 
````bash
pyinstaller --onedir --name EasyScrape --add-data="assets;assets" --icon=assets/icon.ico --noconsole .\window.py
````

with cx_Freeze
````bash
python .\setup.py build_exe --build-exe build/Scraping
````