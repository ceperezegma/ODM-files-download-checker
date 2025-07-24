from playwright.sync_api import sync_playwright
from config import LOGIN_URL, USERNAME, PASSWORD, HEADLESS

def login_to_spa():
    playwright = sync_playwright().start()
    browser = playwright.chromium.launch(
        headless=HEADLESS,
        args=["--start-maximized"]
    )

    # Create context with HTTP Basic Auth and full screen viewport
    context = browser.new_context(
        http_credentials={
            "username": USERNAME,
            "password": PASSWORD
        },
        viewport={"width": 1920, "height": 1080},
        no_viewport=True  # Use full screen
    )
    
    page = context.new_page()
    
    try:
        page.goto(LOGIN_URL)
        page.wait_for_load_state("networkidle")
        print(f"Successfully authenticated and loaded: {page.title()}")

        # Close newsletter popup if it appears
        try:
            # Wait up to 3 seconds for the close button to appear
            page.wait_for_selector("button.close", timeout=3000)
            page.click("button.close")
            print("✅ Newsletter banner closed.")
        except Exception:
            print("ℹ️ Newsletter banner not found or already dismissed.")

        # Accept only essential cookies if cookie banner is shown
        try:
            page.wait_for_selector("button:has-text('Accept only essential cookies')", timeout=3000)
            page.click("button:has-text('Accept only essential cookies')")
            print("✅ Cookie consent accepted (only essential cookies).")
        except Exception:
            print("ℹ️ Cookie banner not found or already handled.")

    except Exception as e:
        print(f"Authentication failed: {e}")
        print("Manual login may be required.")
    
    return browser, page
