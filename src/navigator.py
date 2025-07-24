from src.downloader import download_all_files

def visit_all_tabs(page):
    tabs = [
        'Open Data in Europe 2024',
        'Recommendations',
        'Dimensions',
        'Country profiles',
        'Method and resources'
    ]

    for tab_name in tabs:
        print(f"---------------------------------")
        print(f"[*] Navigating to tab: {tab_name}")
        print(f"---------------------------------")

        # Find the tab element using text match
        try:
            tab_element = page.locator(f"role=tab[name='{tab_name}']")
            tab_element.click()
            print(f"[+] Clicked on tab: {tab_name}")
        except Exception:
            try:
                # Fallback: try clicking on visible text directly
                page.click(f"text={tab_name}")
                print(f"[+] Fallback: Clicked on tab using text={tab_name}")
            except Exception as e:
                print(f"[❌] Could not click tab '{tab_name}': {e}")
                continue

        # Wait for tab-specific content to load
        page.wait_for_timeout(1000)  # Short buffer

        # Add logic to confirm content changed (by checking unique element)
        download_all_files(page, tab_name)

        print(f"[✅] Loaded tab: {tab_name}\n")


