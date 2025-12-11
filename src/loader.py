import csv
import os

def load_countries(year):
    """
    Reads the participant_countries_{year}.csv file from the data folder
    and returns a list of tuples (Country Name, Country Code).
    """
    # Construct path relative to project root (assuming src/loader.py location)
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    file_path = os.path.join(base_dir, 'data', f'participant_countries_{year}.csv')

    countries = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # The CSV headers are country_code,country_name
                # We want tuples of (Country Name, Country Code)
                countries.append((row['country_name'], row['country_code']))
    except FileNotFoundError:
        print(f"❌ Error: File not found at {file_path}")
        return []

    return countries