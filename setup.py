from pathlib import Path
from cx_Freeze import setup, Executable
import sys, shutil

# VAR
APP_NAME = "EasyScrape"
VERSION = "2.3.2"

playwright_browser_path = str(Path.home() / "AppData" / "Local" / "ms-playwright")

build_exe_options = {
    "packages": ["playwright", "asyncio", "tkinter", "playwright._impl"], 
    "include_files": [
        ("assets", "assets"),
        (playwright_browser_path, "ms-playwright")  
    ],
    "excludes": ["tkinter"] 
}

base = "Win32GUI" if sys.platform == "win32" else None

setup(
    name=APP_NAME,
    version=VERSION,
    description="Application created to scrape websites and get informations about articles",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=base, icon="assets/icon.ico", target_name=APP_NAME)]
)
