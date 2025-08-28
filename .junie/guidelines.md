# Project Guidelines

This document summarizes the observed coding conventions, code organization, and current (or recommended) testing approaches for the ODM Downloads Checker project.

Last updated: 2025-08-28 16:11


## 1. Coding Conventions

- Language and version
  - Python 3.10+ (use of match/case, pathlib; type hints in places).
- File headers and encodings
  - Many modules start with `# -*- coding: utf-8 -*-` and a high‑level module docstring explaining purpose and behavior.
- Docstrings
  - Functions include thorough docstrings with sections such as Behavior, Parameters, Returns, Side Effects, Raises, and Example.
  - Style is close to Google-style sections, written as plain paragraphs with section headers.
- Naming
  - Modules: snake_case (e.g., validator.py, reporter.py).
  - Functions: snake_case (e.g., download_all_files, validate_downloads, retrieve_buttons).
  - Variables: snake_case.
  - Constants/config: UPPER_CASE in config.py (e.g., DOWNLOAD_DIR, LOGIN_URL, ENVIRONMENT, HEADLESS).
- Types
  - Selective use of type hints in docstrings; function signatures sometimes omit annotations. Mixed approach is acceptable in current code.
- Imports
  - Absolute imports from the `src` package (e.g., `from src.downloader import ...`) and from `config` at project root.
- Logging/diagnostics
  - Uses `print()` extensively with clear prefixes and emojis/icons (e.g., [*], ✅, ❌, ⚠️, ℹ️) for human‑readable console logs.
  - No formal logging framework is currently used.
- Error handling
  - Best‑effort try/except around UI interactions (Playwright steps) to keep flows resilient and continue processing.
- Formatting
  - Indentation with 4 spaces; line length is pragmatic (no enforced limit observed).
  - F‑strings preferred for string interpolation.
- External configuration
  - Environment is controlled via `config.py` and `.env` variables loaded through `python-dotenv`.
  - Credentials are expected in environment variables and validated at import time in `config.py`.


## 2. Code Organization and Package Structure

Top-level layout (key files/folders):

- main.py
  - Entry point orchestrating the end‑to‑end workflow: initialize -> authenticate -> visit tabs -> download -> validate -> report -> await exit.
- config.py
  - Central configuration and environment selection (DEV/PROD), URLs, credentials, paths, and the `HEADLESS` flag.
- expected_files.json
  - Manifest of expected downloads used by validator/reporting.
- downloads/
  - Output root for downloaded artifacts, with subfolders named per tab.
- src/
  - Application package with cohesive modules:
    - auth.py: Playwright startup/authentication helpers (`login_to_spa`).
    - navigator.py: High‑level tab navigation (`visit_all_tabs`).
    - downloader.py: Orchestrates per‑tab downloads (`download_all_files`); delegates to utils and tab_visitor.
    - tab_visitor.py: Locators and click helpers for dimensions and countries (`retrieve_buttons`, `select_button`).
    - utils.py: Lower‑level DOM/Playwright helpers for retrieving chart menu IDs, resource IDs, downloading charts/resources, and sorting keys (e.g., `build_key`).
    - validator.py: Compares files on disk to `expected_files.json` and returns structured results.
    - reporter.py: Renders human‑readable validation report from validator results.
    - startup.py: Workspace cleanup before runs (`initializer`).

Runtime data and outputs:
- downloads/<Tab_Name_With_Underscores>/ used by `downloader.py` and validated by `validator.py`.
- logs/ directory exists but is not referenced by code for structured logging.

External dependencies:
- playwright>=1.30.0
- python-dotenv>=0.19.0

Assumptions:
- Playwright Chromium is installed and browsers are set up (`playwright install`).
- `.env` contains the required USERNAME/PASSWORD variables for the selected ENVIRONMENT.


## 3. Testing Approaches

Current status:
- No unit or integration test files are present in the repository at the moment.

Recommended approach going forward:

- Unit tests (pytest)
  - Framework: pytest.
  - Scope: Pure logic and filesystem transformations that do not require a live browser.
    - Examples:
      - `validator.validate_downloads`: test comparison logic using temporary directories/files and small JSON manifests.
      - `reporter.format_file_size`: test size formatting edge cases (0 B, KB/MB/GB thresholds).
      - `utils.build_key`: test sort key grouping and ordering, including edge file name patterns.
  - Techniques:
    - Use `tmp_path` fixtures for creating ephemeral directories and files.
    - Provide small fixture JSON for `expected_files.json` cases.
    - Mock I/O where helpful (e.g., `Path.iterdir`, `.stat`) or write real small files.

- Integration tests (Playwright)
  - Scope: Browser flows that require navigating the live SPA and downloading files.
  - Environment:
    - Run in headless mode by setting `HEADLESS=True` (via config or environment override) to be CI‑friendly.
    - Use a dedicated test account configured via `.env` variables (e.g., `USERNAME_ODM_DEV`, `PASSWORD_ODM_DEV`).
  - Recommendations:
    - Create a thin test that exercises: `login_to_spa` -> `visit_all_tabs` for a narrow subset (e.g., a single tab) to limit runtime and flakiness.
    - Add waits/assertions for specific UI elements to confirm tab navigation.
    - Clean the downloads folder before the run (invoke `startup.initializer`).
    - Validate outputs by calling `validator.validate_downloads` with a small manifest for the tab under test.
  - Isolation and stability:
    - Mark browser tests as `@pytest.mark.slow` and/or `@pytest.mark.integration`.
    - Consider retry logic or Playwright’s `expect_*` utilities to reduce flakiness.

- Test organization proposal:
  - Create a `tests/` directory with subpackages:
    - `tests/unit/` for pure Python tests (validator, reporter, utils).
    - `tests/integration/` for Playwright browser flows.
  - Configure `pytest.ini` with markers (e.g., `integration`, `slow`) and to ignore downloads overflow if needed.

- CI considerations:
  - Add a GitHub Actions workflow (or other CI) to:
    - Set up Python, install deps, run `playwright install --with-deps` where appropriate.
    - Run unit tests on every push/PR.
    - Optionally run integration tests on a schedule or behind a label to control cost/flakiness.


## 4. Practical Tips for Contributors

- Before running main.py:
  - Ensure `.env` is populated with correct credentials (DEV/PROD), then select `ENVIRONMENT` in `config.py`.
  - Optionally set `HEADLESS=True` for unattended runs.
  - Consider running `startup.initializer()` to clean download folders.
- When adding modules:
  - Follow the existing docstring pattern (Behavior, Parameters, Returns, Side Effects, Raises, Example).
  - Prefer snake_case names and absolute imports from `src`.
  - Keep user‑visible console output consistent with current emoji‑based style.
- When adding tests:
  - Keep unit tests deterministic; isolate filesystem via `tmp_path`.
  - For Playwright tests, keep scope small and guarded with markers; use environment variables for secrets.
