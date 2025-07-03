############################################################################
#
# Main python file for scrapping app. Using libraries from requirement.txt
# EasyScrape - Not like gromoteur
# Use this file only to create the executable file for this application
# Martin Hugo
# 2025
#
############################################################################

from window import App
import os
import pathlib
import sys

if getattr(sys, 'frozen', False):
    base_path = os.path.dirname(sys.executable)
    os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(base_path, "ms-playwright")
else:
    base_path = os.path.dirname(os.path.abspath(__file__))


if __name__ == "__main__":
    window = App()
    window.mainloop()

    