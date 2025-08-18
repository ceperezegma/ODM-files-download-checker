# -*- coding: utf-8 -*-
"""
Tab-aware download coordinator.

This module provides the orchestration logic to download artifacts from a given tab
in a browser-driven session. It delegates to specialized helpers to:
- Retrieve chart menu identifiers and trigger chart downloads.
- Gather resource URLs and download or materialize related files.
- Iterate through dimensions or country profiles when the tab requires sub-navigation.

It also ensures a tab-specific output directory exists before starting the process.
"""

import os
from pathlib import Path
from src.utils import retrieve_chart_menu_ids, download_from_resources, download_from_charts, retrieve_resources_files_ids, remove_duplicates_resources_id, build_key
from src.tab_visitor import retrieve_buttons, select_button
from config import DOWNLOAD_DIR

def download_all_files(page, tab_name):
    """
    Download all relevant files for the specified tab.

    Behavior:
    - Creates a tab-specific directory under the configured downloads root.
    - Based on the tab name, performs the following:
        - Open Data in Europe 2024:
            - Retrieves chart menu identifiers.
            - Downloads chart exports (images/data).
            - Collects and de-duplicates resource URLs, then downloads them.
        - Recommendations:
            - Skips charts.
            - Collects and de-duplicates resource URLs, then downloads them.
        - Dimensions (Policy, Portal, Quality, Impact):
            - Iterates over dimension buttons:
                - Selects each dimension.
                - Retrieves chart menu identifiers and downloads charts.
                - Collects, de-duplicates, and downloads resources per dimension.
        - Country profiles:
            - Iterates over available countries:
                - Selects each country.
                - Retrieves chart menu identifiers and downloads charts.
                - Collects, de-duplicates, and downloads resources per country.
        - Method and resources:
            - Skips charts.
            - Collects and de-duplicates resource URLs, then downloads them.
    - Prints progress and status messages for traceability.

    Parameters:
        page (playwright.sync_api.Page): The active Playwright page used to interact
            with the web UI, navigate tabs, and trigger downloads.
        tab_name (str): The visible name of the tab to process.

    Returns:
        None

    Side Effects:
        - Creates a tab-specific directory if it does not exist.
        - Triggers file downloads and writes files to disk.
        - Performs UI interactions (clicks, waits, scrolling) on the given page.
        - Writes diagnostic messages to stdout.

    Raises:
        - Any exceptions not handled by underlying helpers may propagate.
        - File system related errors can occur when creating directories or saving files.

    Example:
        # After navigating to a tab in the UI:
        download_all_files(page, "Open Data in Europe 2024")
    """
    print(f"[*] Starting download process for tab: {tab_name}")

    # Create tab-specific directory
    tab_dir = os.path.join(DOWNLOAD_DIR, tab_name.replace(" ", "_"))
    Path(tab_dir).mkdir(parents=True, exist_ok=True)

    resources_urls_tabs = []

    # Define what to download based on tab
    match tab_name:
        case 'Open Data in Europe 2024':
            # Retrieve tab ODM Save & share charts menu ids
            charts_menus_ids = retrieve_chart_menu_ids(page, tab_name)

            # Download charts in the tab
            download_from_charts(page, tab_dir, charts_menus_ids['open_data_in_europe'])

            # Download resources
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
            # Removes duplicates in ids
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            # Download resources
            download_from_resources(page, tab_dir, resources_urls_tabs_clean)
        case 'Recommendations':
            print(f"Nothing to check here for charts!")

            # Download resources
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name, )
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            download_from_resources(page, tab_dir, resources_urls_tabs_clean)
        case 'Dimensions':
            dimensions = ['Policy', 'Portal', 'Quality', 'Impact']

            # Retrieve dimension buttons in the tab
            dimension_buttons = retrieve_buttons(page, dimensions, 'dimensions')
            num_dimensions = len(dimensions)
            for i in range(num_dimensions):
                select_button(page, dimension_buttons[i], dimensions[i])
                charts_menus_ids = retrieve_chart_menu_ids(page, tab_name)
                download_from_charts(page, tab_dir, charts_menus_ids['dimensions'])

            # Download resources
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            download_from_resources(page, tab_dir, resources_urls_tabs_clean)
        case 'Country profiles':
            countries = combined = [
                ('Albania', 'AL'),
                ('Austria', 'AT'),
                ('Belgium', 'BE'),
                ('Bosnia and Herzegovina', 'BA'),
                ('Bulgaria', 'BG'),
                ('Croatia', 'HR'),
                ('Cyprus', 'CY'),
                ('Czechia', 'CZ'),
                ('Denmark', 'DK'),
                ('Estonia', 'EE'),
                ('Finland', 'FI'),
                ('France', 'FR'),
                ('Germany', 'DE'),
                ('Greece', 'EL'),
                ('Hungary', 'HU'),
                ('Iceland', 'IS'),
                ('Ireland', 'IE'),
                ('Italy', 'IT'),
                ('Latvia', 'LV'),
                ('Lithuania', 'LT'),
                ('Luxembourg', 'LU'),
                ('Malta', 'MT'),
                ('Netherlands', 'NL'),
                ('Norway', 'NO'),
                ('Poland', 'PL'),
                ('Portugal', 'PT'),
                ('Romania', 'RO'),
                ('Serbia', 'RS'),
                ('Slovakia', 'SK'),
                ('Slovenia', 'SI'),
                ('Spain', 'ES'),
                ('Sweden', 'SE'),
                ('Switzerland', 'CH'),
                ('Ukraine', 'UA')]

            country_buttons = retrieve_buttons(page, countries, 'countries')
            num_countries = len(country_buttons)

            # Retrieve URLs to download resources, remove duplicates and sort them to match the sorted list of countries in ODM
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            resources_urls_tab_sorted = sorted(resources_urls_tabs_clean, key=build_key)

            for i in range(num_countries):
                select_button(page, country_buttons[i], countries[i])
                charts_menus_ids = retrieve_chart_menu_ids(page, tab_name)
                download_from_charts(page, tab_dir, charts_menus_ids['country_profiles'])

                # Download resources
                download_from_resources(page, tab_dir, resources_urls_tab_sorted[i*2: i*2+2])
        case 'Method and resources':
            print(f"Nothing to check here for charts!")

            # Download resources
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            download_from_resources(page, tab_dir, resources_urls_tabs_clean)

    print(f"\n[✅] Downloads complete for tab: {tab_name}\n")
