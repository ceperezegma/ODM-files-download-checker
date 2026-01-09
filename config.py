import os
import pandas as pd
from dotenv import load_dotenv


# Load environment variables from .env file
load_dotenv()

# -------------------------------
# USER INPUT: Pick environment to work with
# -------------------------------
ENVIRONMENT = "PROD" # DEV, H-PROD, or PROD
YEAR = "2025" # "2024", 2025, ...
# --------------------------------

EXPECTED_FILES_PATH = f"data/expected_files_{YEAR}.json"
DOWNLOAD_DIR = "downloads/"

# Load the hrefs indexes to use to properly target resources in each tab. It's required to handle changes from one year to another. E.g. change in participant countries from year to year
RESOURCE_INDEXES = pd.read_csv(os.path.join('data', 'resources_indexes.csv'), sep=';')
CHARTS_INDEXES = pd.read_csv(os.path.join('data', 'charts_indexes.csv'), sep=';')

LOGIN_URL_DEV = "https://edp.dev.agiledrop.com/en/open-data-maturity/" + YEAR
LOGIN_URL_H_PROD = "https://data.europa.eu/en/open-data-maturity/" + YEAR  # Actual PROD URL homepage behind credentials
URL_PROD = "https://data.europa.eu/en/open-data-maturity/" + YEAR       # Actual PROD URL homepage without credentials (public access)
# Starting link for the previous editions
URL_DEU_DEV = "https://edp.dev.agiledrop.com/en/open-data-maturity/"
URL_DEU_PROD = "https://data.europa.eu/en/open-data-maturity/"

# Select URL based on environment
LOGIN_URL = LOGIN_URL_DEV if ENVIRONMENT == "DEV" else LOGIN_URL_H_PROD if ENVIRONMENT == "H-PROD" else URL_PROD
LOGIN_URL_DEU = URL_DEU_DEV if ENVIRONMENT == "DEV" else URL_DEU_PROD

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME_ODM_DEV") if ENVIRONMENT == "DEV" else os.getenv("USERNAME_ODM_PROD") if ENVIRONMENT == "H-PROD" else None
PASSWORD = os.getenv("PASSWORD_ODM_DEV") if ENVIRONMENT == "DEV" else os.getenv("PASSWORD_ODM_PROD") if ENVIRONMENT == "H-PROD" else None

# Validate credentials are available
if (not USERNAME or not PASSWORD) and ENVIRONMENT != "PROD":
    raise ValueError("❌ Missing credentials: USERNAME and PASSWORD must be set in .env file")

# Validate environment
if ENVIRONMENT not in ['DEV', 'H-PROD', 'PROD']:
    raise ValueError(f"❌ Invalid ENVIRONMENT: {ENVIRONMENT}. Must be 'DEV' or 'PROD'")

print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🔗 Login URL: {LOGIN_URL}")

# Show or not the browser on screen
HEADLESS = False  # Set to True if you don't need to see interaction in the browser
