def retrieve_buttons(page, labels, key):

    match key:
        case 'dimensions':
            # Localizes the 4 dimensions buttons
            buttons = [page.locator(f"button[id='dimension_{dimension.lower()}'][aria-label='Select {dimension}']") for dimension in labels]

            print(f"[i] Found {len(buttons)} dimension buttons in the dimension tab")
        case 'countries':
            # Localizes the 34 countries buttons
            buttons = [page.locator(f"button[id='country_{country_code}'][aria-label='Select {country}']") for country, country_code in labels]

            print(f"[i] Found {len(buttons)} country buttons in the country profiles tab")

    return buttons


def select_button(page, button, label):

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

