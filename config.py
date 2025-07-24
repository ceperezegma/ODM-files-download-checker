import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

EXPECTED_FILES_PATH = "expected_files.json"
DOWNLOAD_DIR = "downloads/"
LOGIN_URL = "https://edp.dev.agiledrop.com/en/open-data-maturity/2024"

# Get credentials from environment variables
USERNAME = os.getenv("USERNAME_ODM")
PASSWORD = os.getenv("PASSWORD_ODM")

# Validate credentials are available
if not USERNAME or not PASSWORD:
    raise ValueError("❌ Missing credentials: USERNAME and PASSWORD must be set in .env file")

# Show or not the browser on screen
HEADLESS = False  # Set to True for production
