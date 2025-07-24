import os

def initializer():
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