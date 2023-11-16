import datetime
import os

# files
LOGS_SAVE_PATH = "logs"
if not os.path.exists(LOGS_SAVE_PATH):
    os.mkdir(LOGS_SAVE_PATH)
LOGS_FILE = os.path.join(LOGS_SAVE_PATH, f"logs_{datetime.datetime.now().strftime('%d_%m_%Y__%H_%M_%S')}.log")

FILES_SAVE_PATH = "data"
if not os.path.exists(FILES_SAVE_PATH):
    os.mkdir(FILES_SAVE_PATH)
CATS_SAVE_PATH = os.path.join(FILES_SAVE_PATH, "categories.csv")
PR_URL_SAVE_PATH = os.path.join(FILES_SAVE_PATH, "product_urls.csv")
PR_SAVE_PATH = os.path.join(FILES_SAVE_PATH, f"products.csv")

PR_URL_SAVE_PATH_EXTRA = os.path.join(FILES_SAVE_PATH, "product_urls_full.csv")
CATS_SAVE_PATH_EXTRA = os.path.join(FILES_SAVE_PATH, "categories_full.csv")

# connector
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
}
PROXY = None

