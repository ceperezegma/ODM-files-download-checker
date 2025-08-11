import os

########################################
# Retrieve ids for charts and resources
########################################
def retrieve_chart_menu_ids(page, tab_name):

    save_and_share_ids_tab = {
        'open_data_in_europe': {'menu_ids': [], 'chart_menus': []},
        'dimensions': {'menu_ids': [], 'chart_menus': []},
        'country_profiles': {'menu_ids': [], 'chart_menus': []}
    }

    # Retrieves all Save & share menus divs by their role and aria-label.
    # TODO: The result includes more than the Save & share menus in a specif tab -> Needed positional filtering
    chart_menus = page.locator("div[role='combobox'][aria-label='Save & share']")
    total_menus = chart_menus.count()

    print(f"[i] Found {total_menus} 'Save & share' dropdowns.")
    # List valid ids or all charts in ODM to download

    # Save the Save & share menus corresponding to each ODM tab with charts
    if tab_name == 'Open Data in Europe 2024':
        # Get indices 0, 2, 4, 6 (first 4 charts)
        indices = range(0, 7, 2)
        
        # Get all menu IDs and chart menus at once
        save_and_share_ids_tab['open_data_in_europe']['menu_ids'] = [chart_menus.nth(i).get_attribute("id") for i in indices]
        save_and_share_ids_tab['open_data_in_europe']['chart_menus'] = [chart_menus.nth(i) for i in indices]

        tab = list(save_and_share_ids_tab.keys())[0]
        print_label = 'Open Data in Europe 2024'
    elif tab_name == 'Dimensions':
        indices = range(8, 11, 2)
        save_and_share_ids_tab['dimensions']['menu_ids'] = [chart_menus.nth(i).get_attribute("id") for i in indices]
        save_and_share_ids_tab['dimensions']['chart_menus'] = [chart_menus.nth(i) for i in indices]

        tab = list(save_and_share_ids_tab.keys())[1]
        print_label = 'Dimensions'
    elif tab_name == 'Country profiles':
        indices = range(12, 15, 2)
        # Get indices for Country profiles tab (11-15)
        save_and_share_ids_tab['country_profiles']['menu_ids'] = [chart_menus.nth(i).get_attribute("id") for i in indices]
        save_and_share_ids_tab['country_profiles']['chart_menus'] = [chart_menus.nth(i) for i in indices]

        tab = list(save_and_share_ids_tab.keys())[2]
        print_label = 'Country profiles'

    # Print chart info
    for idx, chart_id in enumerate(save_and_share_ids_tab[tab]['menu_ids']):
        print(f"{print_label} - Chart {idx + 1}: {chart_id}")

    return save_and_share_ids_tab


def retrieve_resources_files_ids(page, tab_name):
    resources_file_ids_tab = []

    print("[*] Searching for download buttons...")

    download_links = page.locator("a:has(span:has-text('Download'))")
    count = download_links.count()
    print(f"\n[i] Found {count} resources to download")

    match tab_name:
        case 'Open Data in Europe 2024':
            indices = range(0, 3)
            resources_file_ids_tab = [download_links.nth(i).get_attribute('href') for i in indices]
        case 'Recommendations':
            # 🚨TODO: To implement to download resources when in PROD
            indices = range(3, 11)
            # resources_file_ids_tab = [download_links.nth(i).get_attribute('href') for i in indices]
        case 'Dimensions':
            indices = range(3, 11)
            resources_file_ids_tab = [download_links.nth(i).get_attribute('href') for i in indices]
        case 'Country profiles':
            indices = range(11, 31)
            resources_file_ids_tab = [download_links.nth(i).get_attribute('href') for i in indices]
        case 'Method and resources':
            indices = range(31, 41)
            resources_file_ids_tab = [download_links.nth(i).get_attribute('href') for i in indices]

    return resources_file_ids_tab

def remove_duplicates_resources_id(resources_list):
    # Remove duplicate strings while preserving order
    return list(dict.fromkeys(resources_list))



################################
# Download charts and resources
################################
def download_from_charts(page, tab_dir, charts_menu_ids):
    download_options = [
        'Download image - PNG',
        'Download image - JPEG',
        'Download data - XLSX',
        'Download data - JSON'
    ]

    num_charts = len(charts_menu_ids['menu_ids'])

    # Process only even-indexed menus (0, 2, 4, 6) as per your comment
    # The search for Save & share retrieves 2 ids per chart. The actual id per chart is at even positions of the retrieved ids.
    # So, we need to iterate over even positions starting from 0
    for i in range(num_charts):
        try:
            # Get the current chart menu
            chart_menu = charts_menu_ids['chart_menus'][i]
            chart_menu_id = charts_menu_ids['menu_ids'][i]

            print(f"[*] Downloading from {num_charts} chart(s)...")

            id_prefix = chart_menu_id.split('-')[0]  # Extract prefix like "795"
            
            print(f"\n[*] Processing chart {i + 1} with ID {chart_menu_id}")
            
            # Make sure the chart is visible
            chart_menu.scroll_into_view_if_needed()
            page.wait_for_timeout(500)
            
            # Process each download option for this chart
            for option_text in download_options:
                try:
                    # Open the dropdown menu
                    chart_menu.click()
                    page.wait_for_timeout(1000)
                    print(f"    [→] Clicking on: {option_text}")
                    
                    # Find the listbox that appears when menu is clicked
                    listbox_id = f"{id_prefix}-listbox1"
                    listbox = page.locator(f"ul[id='{listbox_id}']")
                    
                    if listbox.count() > 0:
                        # Find and click the specific option in this listbox
                        option = listbox.locator(f"li:has-text('{option_text}')")
                        
                        if option.count() > 0:
                            # Click with download expectation
                            with page.expect_download() as download_info:
                                option.click()
                                # page.wait_for_timeout(1500)
                            
                            # Process the download
                            download = download_info.value
                            filename = download.suggested_filename
                            filepath = os.path.join(tab_dir, filename)
                            download.save_as(filepath)
                            print(f"    [✅] Downloaded: {filename}")
                        else:
                            print(f"    [❌] Option '{option_text}' not found in listbox")
                    else:
                        print(f"    [❌] Listbox with ID '{listbox_id}' not found")
                        
                    # Close the menu by clicking elsewhere
                    page.mouse.click(0, 0)
                    page.wait_for_timeout(500)
                    
                except Exception as e:
                    print(f"[❌] Error with option '{option_text}': {e}")
                    # Try to close any open menu
                    page.mouse.click(0, 0)
            
            # Scroll down to reveal next chart
            page.mouse.wheel(0, 1500)
            page.wait_for_timeout(1000)
            
        except Exception as e:
            print(f"[❌] Failed for chart {i//2 + 1}: {e}")
            
        # Stop after processing 4 charts (indices 0, 2, 4, 6)
        if i > 8:
            break


def download_from_resources(page, tab_dir, resources_urls):
    print("[*] Downloading from resources section...")
    total_resources = len(resources_urls)
    print(f"Total resources to download: {total_resources}")

    for i, url in enumerate(resources_urls):
        try:
            # Parse URL to get filename and extension
            filename = os.path.basename(url)
            name, ext = os.path.splitext(filename)
            ext = ext.lower()
            
            print(f"    [→] Processing resource {i+1}: {filename}")
            
            if ext == '.pdf':
                # Create empty PDF file
                filepath = os.path.join(tab_dir, filename)
                os.makedirs(tab_dir, exist_ok=True)  # Ensure directory exists
                with open(filepath, 'w') as f:
                    pass  # Create empty file
                print(f"    [✅] Created empty PDF: {filename}")
            else:
                # Find and click the download link
                link_locator = page.locator(f"a[href='{url}']")
                
                if link_locator.count() > 0:
                    with page.expect_download() as download_info:
                        link_locator.first.click()
                    
                    download = download_info.value
                    filepath = os.path.join(tab_dir, download.suggested_filename)
                    download.save_as(filepath)
                    print(f"    [✅] Downloaded: {download.suggested_filename}")
                else:
                    print(f"    [❌] Link not found for: {filename}")
                    
        except Exception as e:
            print(f"    [❌] Failed to process resource {i+1}: {e}")