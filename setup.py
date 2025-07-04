from pathlib import Path
from cx_Freeze import setup, Executable
import sys, shutil
from config import *


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
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    options={"build_exe": build_exe_options},
    executables=[Executable(APP_MAIN_FILE, base=base, icon=APP_ICON_PATH, target_name=APP_NAME)]
)
