import time
from src.auth import login_to_spa
from src.navigator import visit_all_tabs
from src.startup import initializer

from src.validator import validate_downloads
from src.reporter import generate_report
from config import EXPECTED_FILES_PATH

def main():
    start_time = time.time()
    print("[*] Starting ODM File Checker...")

    # Make all the cleaning and setup to start the program from the right inital state
    initializer()

    # Step 1: Log in and get browser/page
    browser, page = login_to_spa()

    # Step 2: Navigate all tabs and download files
    visit_all_tabs(page)

    # Step 3: Validate downloaded files
    validation_results = validate_downloads(EXPECTED_FILES_PATH)

    # Step 4: Generate report
    generate_report(validation_results)

    # Calculate and display execution time
    end_time = time.time()
    execution_time = end_time - start_time
    minutes, seconds = divmod(execution_time, 60)
    print(f"\n[i] Total execution time: {int(minutes)} minutes and {seconds:.2f} seconds")
    
    # Keep browser open
    input("Press Enter to close browser and exit...")
    browser.close()

if __name__ == "__main__":
    main()
