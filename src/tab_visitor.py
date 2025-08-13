# -*- coding: utf-8 -*-
"""
Utilities for locating and interacting with tab-scoped selector buttons.

This module provides helpers to:
- Build locators for dimension and country buttons based on provided labels.
- Click a specific button and log the interaction outcome.

These functions are intended to be used by higher-level navigation and download
workflows that iterate over dimensions or countries within a tab.
"""


def retrieve_buttons(page, labels, key):
    """
    Build and return a list of button locators for the given category.

    Behavior:
    - When key == 'dimensions':
        - Creates Playwright locators for the four dimension buttons (Policy, Portal,
          Quality, Impact) using predictable element attributes.
        - Prints how many dimension buttons were found.
    - When key == 'countries':
        - Expects labels as a list of tuples (country_name, country_code).
        - Creates Playwright locators for country buttons using the two-letter code and
          accessible labels.
        - Prints how many country buttons were found.

    Parameters:
        page (playwright.sync_api.Page): Active Playwright page.
        labels (list): For 'dimensions', a list of dimension names (str).
                       For 'countries', a list of (country_name, country_code) tuples.
        key (str): Either 'dimensions' or 'countries' to select the locator strategy.

    Returns:
        list: A list of Playwright Locator objects corresponding to the requested buttons.

    Raises:
        ValueError: If an unsupported key is provided.

    Example:
        dims = ['Policy', 'Portal', 'Quality', 'Impact']
        dim_buttons = retrieve_buttons(page, dims, 'dimensions')

        countries = [('France', 'FR'), ('Germany', 'DE')]
        country_buttons = retrieve_buttons(page, countries, 'countries')
    """
    match key:
        case 'dimensions':
            # Localizes the 4 dimensions buttons
            buttons = [page.locator(f"button[id='dimension_{dimension.lower()}'][aria-label='Select {dimension}']") for dimension in labels]

            print(f"[i] Found {len(buttons)} dimension buttons in the dimension tab")
        case 'countries':
            # Localizes the 34 countries buttons
            buttons = [page.locator(f"button[id='country_{country_code}'][aria-label='Select {country}']") for country, country_code in labels]

            print(f"[i] Found {len(buttons)} country buttons in the country profiles tab")
        case _:
            raise ValueError(f"Unsupported key: {key!r}. Expected 'dimensions' or 'countries'.")

    return buttons


def select_button(page, button, label):
    """
    Click the provided button and log the result.

    Behavior:
    - Attempts to click the given button locator.
    - Waits briefly to allow the page to update after the click.
    - Logs a success message tailored for dimension names or (country_name, code) tuples.
    - On failure, logs an error message with the exception context.

    Parameters:
        page (playwright.sync_api.Page): Active Playwright page.
        button (playwright.sync_api.Locator): The button to click.
        label (str|tuple): For dimensions, a string like 'Policy'.
                           For countries, a tuple (country_name, country_code).

    Returns:
        None

    Side Effects:
        - Performs a UI click on the page.
        - Prints diagnostic information to stdout.

    Example:
        select_button(page, dim_buttons[0], 'Policy')
        select_button(page, country_buttons[0], ('France', 'FR'))
    """
    # Clicks on a specific dimension button
    try:
        button.click()
        page.wait_for_timeout(1000)
        if label in ('Policy', 'Portal', 'Quality', 'Impact'):
            print(f"\n[*] Clicked on {label} button")
        else:
            print(f"\n[*] Clicked on {label[0]} button")

    except Exception as e:
        if label in ('Policy', 'Portal', 'Quality', 'Impact'):
            print(f"\n[❌] Failed to click on {label} button: {e}")
        else:
            print(f"\n[❌] Failed to click on {label[0]} button: {e}")
