import os
from pathlib import Path
from src.utils import retrieve_chart_menu_ids, download_from_resources, download_from_charts, retrieve_resources_files_ids, remove_duplicates_resources_id
from src.tab_visitor import retrieve_buttons, select_button
from config import DOWNLOAD_DIR

# TODO: Check plan
# todo 1: resources for country profiles and only the country fact sheets and questionnaire (2 files per country)
# todo 2: detect broken links in Dimensions > tables by dimension

def download_all_files(page, tab_name):
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
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
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
            for i in range(num_countries):
                select_button(page, country_buttons[i], countries[i])
                charts_menus_ids = retrieve_chart_menu_ids(page, tab_name)
                download_from_charts(page, tab_dir, charts_menus_ids['country_profiles'])

                resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
                resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
                download_from_resources(page, tab_dir, resources_urls_tabs_clean)
        case 'Method and resources':
            print(f"Nothing to check here for charts!")

            # Download resources
            resources_urls_tabs = retrieve_resources_files_ids(page, tab_name)
            resources_urls_tabs_clean = remove_duplicates_resources_id(resources_urls_tabs)
            download_from_resources(page, tab_dir, resources_urls_tabs_clean)

    print(f"\n[✅] Downloads complete for tab: {tab_name}\n")
