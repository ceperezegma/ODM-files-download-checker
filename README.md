# ODM Downloads Checker

A small utility to automatically navigate the Open Data Maturity (ODM) Single Page Application (SPA) on the [EU open data portal](https://data.europa.eu/en), download all relevant artifacts (chart exports and linked resources) per tab, and validate that everything expected has been downloaded. It finishes by generating a human‑readable report of the results.

This tool is useful for:
- Verifying that all downloadable assets in the ODM 2024 pages are present and accessible.
- Producing a repeatable validation report for QA or content audits.
- Keeping a local archive of per‑tab downloads for further analysis.


## Table of Contents
- Overview
- Project Structure
- How It Works (High‑Level Flow)
- Requirements
- Setup
- Configuration
- Running the Application
- Outputs
- Troubleshooting
- Notes on Testing (Recommended)


## Overview
The application uses Playwright (Chromium) to:
1) Start a browser and authenticate into the selected environment (DEV, H-PROD, or PROD).
2) Visit each relevant ODM tab (Open Data in Europe, Recommendations, Dimensions, Country profiles, Method and resources, Previous editions).
3) For each tab, download chart exports and related resources.
4) Validate the files against the manifests in `data/`.
5) Generate a concise report of what was found/missing.


## Project Structure
At a glance (key files/folders):

- main.py — Entry point orchestrating the full workflow: initialize → authenticate → navigate → download → validate → report → await exit.
- config.py — Central configuration and environment selection (DEV, H-PROD, or PROD), URLs, credentials, and flags like HEADLESS. Also defines YEAR and various data paths.
- data/ — Folder containing the expected files manifests and index CSVs:
  - expected_files_2024.json, expected_files_2025.json — Manifests for different years.
  - expected_files_previous_editions.json — Manifest for the Previous Editions tab.
  - resources_indexes.csv, charts_indexes.csv — Index mapping for targeting resources.
- downloads/ — Output root where downloaded artifacts are written. Subfolders are named after tabs with spaces replaced by underscores.
- src/ — Application package:
  - auth.py — Playwright startup and login helper (login_to_spa).
  - navigator.py — High-level tab navigation (visit_all_tabs).
  - downloader.py — Per-tab download orchestration (download_all_files), delegating to utils and tab_visitor.
  - tab_visitor.py — Locators and click helpers for dimensions and countries (retrieve_buttons, select_button).
  - utils.py — DOM/Playwright helpers for chart menu IDs, resource IDs, downloading charts/resources, and sorting (build_key, etc.).
  - validator.py — Compares on-disk files to expected manifests and returns structured results.
  - reporter.py — Produces a human-readable validation report from validator results.
  - startup.py — Workspace cleanup before runs (initializer).
- logs/ — Folder present for potential future use; not used for structured logging by the current code.

Note: The repository may also contain a "downloads backup" folder with example outputs for reference; it is not used at runtime.


## How It Works (High‑Level Flow)
- main.py calls:
  1. startup.initializer() — Cleans/sets up the downloads workspace.
  2. auth.login_to_spa() — Launches Playwright Chromium, loads the ODM page, and authenticates.
  3. navigator.visit_all_tabs(page) — Visits each tab and delegates to downloader.download_all_files() per tab.
  4. validator.validate_downloads() — Compares disk artifacts with expected manifests in `data/`.
  5. reporter.generate_report(results) — Prints a human‑readable report to the console (and/or file, depending on implementation).
  6. Waits for the user to press Enter before closing the browser.

- downloader.py logic adapts to the current tab:
  - Open Data in Europe: downloads charts and resources.
  - Recommendations: downloads resources only.
  - Dimensions (Policy, Portal, Quality, Impact): iterates dimension buttons, downloads per-dimension charts and resources.
  - Country profiles: iterates countries, downloads charts and country-specific resources in a sorted, predictable order.
  - Method and resources: downloads resources only.
  - Previous editions: downloads charts and resources.


## Requirements
- Windows or other OS supported by Playwright (this project is commonly run on Windows; paths in examples use backslashes).
- Python 3.10+
- Playwright >= 1.30.0 (Chromium browser installed)
- python-dotenv >= 0.19.0

All Python dependencies are listed in requirements.txt.


## Setup
1) Create and activate a virtual environment (optional but recommended).

2) Install dependencies:
   pip install -r requirements.txt

3) Install Playwright browsers:
   playwright install

4) Create a .env file at the project root with credentials for the chosen environment:
   For DEV:
   USERNAME_ODM_DEV=your_dev_username
   PASSWORD_ODM_DEV=your_dev_password

   For PROD:
   USERNAME_ODM_PROD=your_prod_username
   PASSWORD_ODM_PROD=your_prod_password

Keep this file private and never commit real credentials.


## Configuration
Open config.py to set or review:
- ENVIRONMENT: "DEV", "H-PROD", or "PROD". This selects the login URL and which environment variables to read.
- YEAR: "2024", "2025", etc. Determines which data manifest to use and the target URL.
- HEADLESS: True to run the browser without a visible window (recommended for automation/CI), False to see the browser.
- DOWNLOAD_DIR: Root folder for downloaded files (default: "downloads/").

On import, config.py validates that the appropriate USERNAME and PASSWORD are present in the environment (via .env). It also prints the selected environment and login URL.


## Running the Application
- Ensure the .env is configured and config.py’s ENVIRONMENT matches the credentials you set.
- Optionally set HEADLESS=True in config.py (or expose a mechanism to override via environment variables, if added later).
- From the project root, run:
  python main.py

The script will:
- Clean and prepare the workspace.
- Launch a browser and authenticate.
- Visit each tab and trigger downloads into downloads/<Tab_Name_With_Underscores>/.
- Validate the results against expected_files.json.
- Generate and print a summary report.
- Wait for you to press Enter before closing the browser.


## Outputs
- Downloaded files under downloads/ arranged by tab:
  - downloads/Open_Data_in_Europe/
  - downloads/Recommendations/
  - downloads/Dimensions/
  - downloads/Country_profiles/
  - downloads/Method_and_resources/
  - downloads/Previous_editions/

- A console report indicating which expected files were found or missing. The exact format depends on reporter.generate_report.


## Troubleshooting
- Missing credentials error at startup:
  Ensure .env contains the correct variables for the selected ENVIRONMENT, e.g., USERNAME_ODM_PROD and PASSWORD_ODM_PROD for PROD.

- Playwright errors or timeouts:
  Run playwright install again. Ensure network access to the selected URL. Consider toggling HEADLESS or slowing steps if needed.

- Nothing appears in downloads/:
  Verify you can log into the ODM SPA manually. Check that the tab names and locators still match the site’s UI (site updates may require code adjustments).

- Validation failures:
  Review expected manifest files in `data/` and the files produced under downloads/. Update the manifests if the source content legitimately changed.


## Notes on Testing (Recommended)
This repository currently doesn’t include tests. A recommended approach:
- Unit tests (pytest):
  - validator.validate_downloads with temporary directories and small JSON manifests.
  - reporter helpers (e.g., file size formatting) with edge cases.
  - utils.build_key and any sorting/key generation logic.

- Integration tests (Playwright):
  - Headless browser flow exercising login_to_spa and a minimal subset of navigation (e.g., one tab), guarded with pytest markers like @pytest.mark.integration.

See Project Guidelines (in .junie/guidelines.md or equivalent) for more detailed recommendations.
