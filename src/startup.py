# -*- coding: utf-8 -*-
"""
Startup housekeeping helpers.

This module provides utilities to prepare the workspace before executing the main flow.
"""

import os


def initializer():
    """
    Prepare the local workspace by cleaning predefined download folders.

    Behavior:
    - Defines a set of target directories expected to contain previously downloaded files.
    - For each existing directory:
        - Iterates through its contents.
        - Deletes regular files (non-recursive).
        - Skips directories and prints a message for non-file entries.
    - Prints diagnostic messages indicating actions taken (deleted, skipped, or errors).

    Notes:
    - Missing directories are reported but not created by this function.
    - This function is intended to reset the environment to a clean state before
      starting a new run that downloads fresh artifacts.

    Side Effects:
    - Deletes files within the specified directories.
    - Writes status messages to stdout.

    Example:
        # Clean up residual files from previous runs
        initializer()
    """
    folders = [
        "downloads/Country_profiles",
        "downloads/Recommendations",
        "downloads/Dimensions",
        "downloads/Method_and_resources",
        "downloads/Open_Data_in_Europe_2024"
    ]

    for folder in folders:
        if not os.path.exists(folder):
            print(f"Folder does not exist: {folder}")
            continue

        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            if os.path.isfile(file_path):
                try:
                    os.remove(file_path)
                    print(f"✅ Deleted: {file_path}")
                except Exception as e:
                    print(f"❌ Error deleting {file_path}: {e}")
            else:
                print(f"⏭️ Skipped (not a file): {file_path}")