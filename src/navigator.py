from src.downloader import download_all_files

def visit_all_tabs(page):
    tabs = {
        'Open Data in Europe 2024': '#open-data-in-europe-2024',
        'Recommendations': '#recommendations',
        'Dimensions': '#dimensions',
        'Country profiles': '#country-profiles',
        'Method and resources': '#method-and-resources'
    }

    for tab_name, tab_selector in tabs.items():
        print(f"\n---------------------------------")
        print(f"[*] Navigating to tab: {tab_name}")
        print(f"---------------------------------")

        # Find the tab element using multiple strategies
        clicked = False
        
        # Strategy 1: Try href selector
        try:
            tab_element = page.locator(f"a[href='{tab_selector}']")
            if tab_element.count() > 0:
                tab_element.nth(0).click()
                print(f"[+] Clicked on tab using href: {tab_name}")
                clicked = True
        except Exception as e:
            print(f"[!] Href strategy failed for {tab_name}: {e}")
        
        # Strategy 2: Try text match if href failed
        if not clicked:
            try:
                page.click(f"text={tab_name}")
                print(f"[+] Clicked on tab using text: {tab_name}")
                clicked = True
            except Exception as e:
                print(f"[!] Text strategy failed for {tab_name}: {e}")
        
        if not clicked:
            print(f"[❌] Could not click tab '{tab_name}' with any strategy")
            continue

        # Wait for tab-specific content to load
        page.wait_for_timeout(1000)  # Short buffer
        
        # Verify we're on the correct tab by checking URL
        current_url = page.url
        if tab_selector not in current_url:
            print(f"[⚠️] Warning: Expected '{tab_selector}' in URL but got: {current_url}")
            print(f"[!] Tab navigation may have failed for: {tab_name}")

        # Add logic to confirm content changed (by checking unique element)
        download_all_files(page, tab_name)


