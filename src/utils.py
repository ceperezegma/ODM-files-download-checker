# -*- coding: utf-8 -*-
"""
Download helper utilities.

This module provides functions that encapsulate the logic for downloading files
from two distinct UI areas:
- Resources section: follows direct resource links, downloading files or
  materializing placeholder PDFs when required.
- Charts section: iterates chart menus and triggers multiple export options
  (images/data) per chart.

These helpers are intended to be called by higher-level tab-specific workflows.
"""


import os
import re
from pathlib import PurePosixPath
from urllib.parse import urlparse
from config import ENVIRONMENT

########################################
# Retrieve ids for charts and resources
########################################
def retrieve_chart_menu_ids(page, tab_name):
    """
    Locate and collect chart menu locators and IDs for the current tab.

    Behavior:
    - Scans the active tab for chart components that expose a “Save & share” (or similar)
      menu.
    - Extracts a stable identifier per chart menu and the corresponding Playwright
      Locator for interacting with it.
    - Returns a structured mapping with per-tab categories used downstream:
        - 'open_data_in_europe': dict with 'menu_ids' and 'chart_menus'
        - 'dimensions': dict with 'menu_ids' and 'chart_menus'
        - 'country_profiles': dict with 'menu_ids' and 'chart_menus'
      Each dict contains:
        - menu_ids (list[str]): Unique IDs that help locate the per-chart listbox/menu.
        - chart_menus (list[playwright.sync_api.Locator]): Clickable menu locators.

    Parameters:
        page (playwright.sync_api.Page): Active Playwright page used to query and
            interact with chart menus.
        tab_name (str): The tab currently being processed; used to determine which
            chart group(s) to collect.

    Returns:
        dict: A mapping of category name to a dict with:
              {
                  "menu_ids": list[str],
                  "chart_menus": list[playwright.sync_api.Locator]
              }
              Only the category relevant to the given tab may be populated.

    Notes:
        - The returned structure aligns with download_from_charts(), which expects
          a dict containing 'menu_ids' and 'chart_menus'.
        - The order of items in 'menu_ids' and 'chart_menus' must match so that
          the i-th ID corresponds to the i-th menu locator.
        - Some charts may produce duplicate or auxiliary IDs; ensure the list is
          filtered or ordered so the correct IDs are provided for exports.

    Example:
        charts = retrieve_chart_menu_ids(page, "Open Data in Europe 2024")
        download_from_charts(page, tab_dir, charts["open_data_in_europe"])

    """
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
    """
    Discover resource links and their suggested download filenames for the current tab.

    Behavior:
    - Locates resource "Download" anchors in the active tab.
    - Selects a tab-specific slice of those anchors (index ranges vary per tab and
      may depend on the ENVIRONMENT setting).
    - Extracts:
        - href: absolute URL of the resource.
        - download: suggested filename provided by the anchor (may be None).
    - Returns two parallel lists (same order and length): URLs and download values.
      Duplicates may be present; use remove_duplicates_resources_id() to de-duplicate
      URLs while keeping the corresponding download values aligned.

    Parameters:
        page (playwright.sync_api.Page): Page used to query and read resource links.
        tab_name (str): The visible tab name used to determine which anchors to read.

    Returns:
        tuple[list[str], list[str|None]]:
            - resources_file_href_tab: list of absolute resource URLs (never None).
            - resources_file_download_tab: list of suggested filenames (can be None),
              aligned by index with the URLs list.

    Notes:
        - The two returned lists always have the same length.
        - URLs can contain duplicates; download values may be None for some items.
        - Downstream code may de-duplicate using remove_duplicates_resources_id()
          before initiating downloads.

    Example:
        urls, downloads = retrieve_resources_files_ids(page, "Dimensions")
        urls_dedup, downloads_dedup = remove_duplicates_resources_id(urls, downloads)
        # Proceed to download using the deduplicated, aligned lists.
    """
    resources_file_href_tab = []
    resources_file_download_tab = []

    print("[*] Searching for download buttons...")

    download_links = page.locator("a:has(span:has-text('Download'))")
    count = download_links.count()
    print(f"\n[i] Found {count} resources to download")

    match tab_name:
        case 'Open Data in Europe 2024':
            indices = range(0, 3)
            resources_file_href_tab = [download_links.nth(i).get_attribute('href') for i in indices]
            resources_file_download_tab = [download_links.nth(i).get_attribute('download') for i in indices]
        case 'Recommendations':
            indices = range(3, 4)
            resources_file_href_tab = [download_links.nth(i).get_attribute('href') for i in indices]
            resources_file_download_tab = [download_links.nth(i).get_attribute('download') for i in indices]
        case 'Dimensions':
            indices = range(3, 11) if ENVIRONMENT == 'DEV' else range(4, 12)
            resources_file_href_tab = [download_links.nth(i).get_attribute('href') for i in indices]
            resources_file_download_tab = [download_links.nth(i).get_attribute('download') for i in indices]
        case 'Country profiles':
            indices = range(11, 31) if ENVIRONMENT == 'DEV' else range(12, 80)
            resources_file_href_tab = [download_links.nth(i).get_attribute('href') for i in indices]
            resources_file_download_tab = [download_links.nth(i).get_attribute('download') for i in indices]
        case 'Method and resources':
            indices = range(31, 41) if ENVIRONMENT == 'DEV' else range(80, 91)
            resources_file_href_tab = [download_links.nth(i).get_attribute('href') for i in indices]
            resources_file_download_tab = [download_links.nth(i).get_attribute('download') for i in indices]

    return resources_file_href_tab, resources_file_download_tab



def remove_duplicates_resources_id(resources_url_list, resources_download_list):
    """
    Remove duplicate URLs while keeping the first occurrence, and drop the
    corresponding entries from the download list to keep both lists aligned.

    Behavior:
    - Scans resources_url_list from left to right.
    - Keeps the first occurrence of each URL and discards subsequent duplicates.
    - For every discarded duplicate URL, its paired entry in resources_download_list
      (at the same index) is also discarded.
    - Preserves the original order of the first occurrences.
    - The resulting lists have the same length. Download values for retained URLs
      may be None.

    Parameters:
        resources_url_list (list[str]): List of resource URLs. Must not contain None.
        resources_download_list (list[str|None]): List of suggested download filenames
            (or None) aligned by index with resources_url_list.

    Returns:
        tuple[list[str], list[str|None]]: A pair of lists containing:
            - deduplicated URLs (first occurrences only, order preserved),
            - corresponding download values (may include None), aligned 1:1 with URLs.

    Raises:
        IndexError: If resources_download_list is shorter than resources_url_list,
            since items are paired by index.

    Example:
        urls = ["a.json", "b.json", "a.json"]
        downloads = ["a.json", "b.json", "a (1).json"]
        urls_out, downloads_out = remove_duplicates_resources_id(urls, downloads)
        # urls_out == ["a.json", "b.json"]
        # downloads_out == ["a.json", "b.json"]
    """

    seen = set()
    dedup_urls = []
    dedup_downloads = []
    for i, url in enumerate(resources_url_list):
        if url in seen:
            continue
        seen.add(url)
        download_val = resources_download_list[i]
        dedup_urls.append(url)
        dedup_downloads.append(download_val)

    return dedup_urls, dedup_downloads




################################
# Download charts and resources
################################
def download_from_resources(page, tab_dir, resources_urls, resources_download):
    """
    Download files referenced in the resources section for the current tab.

    Behavior:
    - Logs the total number of resources to process.
    - For each URL:
        - Determines the filename and extension.
        - If the resource is a PDF, creates an empty placeholder PDF file in the
          tab directory (some PDFs are proxied and represented by empty files).
        - Otherwise:
            - Locates the corresponding anchor element by exact href.
            - Clicks it within a page.expect_download context.
            - Saves the downloaded file to the tab directory using the suggested filename.
        - Logs success or a descriptive message if the link cannot be found.
    - Catches and logs exceptions per resource to continue processing the rest.

    Parameters:
        page (playwright.sync_api.Page): Active Playwright page to interact with links.
        tab_dir (str|pathlib.Path): Destination directory for the downloaded artifacts.
        resources_urls (list[str]): Absolute URLs pointing to resource files.

    Returns:
        None

    Side Effects:
        - Creates files in tab_dir (empty PDFs or downloaded artifacts).
        - Performs UI interactions and file I/O.
        - Prints diagnostic messages to stdout.

    Example:
        urls = ["https://example.test/file.json", "https://example.test/doc.pdf"]
        download_from_resources(page, tab_dir, urls)
    """
    print("\n[*] Downloading from resources section...")
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
                if resources_download[i] is not None:
                    filename = resources_download[i]
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


def download_from_charts(page, tab_dir, charts_menu_ids):
    """
    Iterate chart menus and trigger all supported export options for each chart.

    Behavior:
    - Defines a set of download options per chart (PNG, JPEG, XLSX, JSON).
    - Expects charts_menu_ids to contain:
        - 'menu_ids': a list of unique IDs per chart menu.
        - 'chart_menus': a list of corresponding Playwright Locator instances.
    - For each chart index:
        - Scrolls the chart into view.
        - Opens the menu and selects each export option within the chart’s listbox.
        - Uses page.expect_download to capture and save the file in tab_dir.
        - Prints success and error messages for traceability.
        - Closes menus and scrolls to reveal subsequent charts.
    - Continues even if individual downloads fail, logging errors per option or chart.

    Parameters:
        page (playwright.sync_api.Page): Active Playwright page to interact with chart UI.
        tab_dir (str|pathlib.Path): Destination directory for the chart exports.
        charts_menu_ids (dict): Structure with:
            - 'menu_ids' (list[str]): unique IDs for the chart menus.
            - 'chart_menus' (list[playwright.sync_api.Locator]): locators for those menus.

    Returns:
        None

    Side Effects:
        - Triggers multiple file downloads and writes them to disk.
        - Performs UI interactions (clicks, scrolls, waits).
        - Prints diagnostic messages to stdout.

    Example:
        download_from_charts(page, tab_dir, {
            "menu_ids": ["123-abc", "456-def"],
            "chart_menus": [locator1, locator2]
        })
    """
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

            print(f"\n[*] Downloading from {num_charts} chart(s)...")

            id_prefix = chart_menu_id.split('-')[0]  # Extract prefix like "795"
            
            print(f"\n[*] Processing chart {i + 1} with ID {chart_menu_id}")
            
            # Make sure the chart is visible
            chart_menu.scroll_into_view_if_needed()
            # page.wait_for_timeout(500)   To enable if you see is too fast for the browser interactions
            
            # Process each download option for this chart
            for option_text in download_options:
                try:
                    # Open the dropdown menu
                    chart_menu.click()
                    # page.wait_for_timeout(1000)    To enable if you see is too fast for the browser interactions
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
                                # page.wait_for_timeout(1500)    To enable if you see is too fast for the browser interactions
                            
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
                    # page.wait_for_timeout(500)    To enable if you see is too fast for the browser interactions
                    
                except Exception as e:
                    print(f"[❌] Error with option '{option_text}': {e}")
                    # Try to close any open menu
                    page.mouse.click(0, 0)
            
            # Scroll down to reveal next chart
            page.mouse.wheel(0, 1500)
            # page.wait_for_timeout(1000)    To enable if you see is too fast for the browser interactions
            
        except Exception as e:
            print(f"[❌] Failed for chart {i//2 + 1}: {e}")
            
        # Stop after processing 4 charts (indices 0, 2, 4, 6)
        if i > 8:
            break



################################
# Download helper functions
################################
def build_key(url: str):
    """
    Sort key: (country_slug, type_order)
    - country_slug: parsed from the filename, e.g. "albania", "bosnia_and_herzegovina"
    - type_order: 0 for factsheet, 1 for questionnaire (so factsheet comes first)
    """
    # last path segment (filename)
    name = PurePosixPath(urlparse(url).path or url).name  # e.g. "2024_odm_factsheet_austria_0.pdf"
    stem = name.rsplit(".", 1)[0]                         # e.g. "2024_odm_factsheet_austria_0"

    # match "YYYY_odm_(factsheet|questionnaire)_(country...)" with optional trailing "_0"
    m = re.match(r"^\d{4}_odm_(factsheet|questionnaire)_(.+)$", stem, flags=re.I)
    if not m:
        # Fallback: if pattern doesn't match, just use the whole stem and put it last
        return (stem.lower(), 2)

    doc_type = m.group(1).lower()         # "factsheet" or "questionnaire"
    country = m.group(2).lower()          # e.g. "austria_0" or "bosnia_and_herzegovina"

    # normalize trailing suffix like _0, _1, _a25, etc.
    country = re.sub(r'_[0-9a-zA-Z]+$', '', country)

    type_order = 0 if doc_type == "factsheet" else 1
    return (country, type_order)