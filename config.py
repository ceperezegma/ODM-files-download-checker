import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# -------------------------------
# USER INPUT: Pick environment to work with
# -------------------------------
ENVIRONMENT = "PROD" # DEV or PROD


EXPECTED_FILES_PATH = "expected_files.json"
DOWNLOAD_DIR = "downloads/"

LOGIN_URL_DEV = "https://edp.dev.agiledrop.com/en/open-data-maturity/2024"
LOGIN_URL_PROD = "https://data.europa.eu/en/open-data-maturity/2024"  # Update with actual PROD URL

# Select URL based on environment
LOGIN_URL = LOGIN_URL_DEV if ENVIRONMENT == "DEV" else LOGIN_URL_PROD

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME_ODM_DEV") if ENVIRONMENT == "DEV" else os.getenv("USERNAME_ODM_PROD")
PASSWORD = os.getenv("PASSWORD_ODM_DEV") if ENVIRONMENT == "DEV" else os.getenv("PASSWORD_ODM_PROD")

# Validate credentials are available
if not USERNAME or not PASSWORD:
    raise ValueError("❌ Missing credentials: USERNAME and PASSWORD must be set in .env file")

# Validate environment
if ENVIRONMENT not in ["DEV", "PROD"]:
    raise ValueError(f"❌ Invalid ENVIRONMENT: {ENVIRONMENT}. Must be 'DEV' or 'PROD'")

print(f"🌍 Environment: {ENVIRONMENT}")
print(f"🔗 Login URL: {LOGIN_URL}")

# Show or not the browser on screen
HEADLESS = False  # Set to True for production
