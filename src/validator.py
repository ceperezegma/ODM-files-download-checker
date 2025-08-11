import json
import os
from pathlib import Path
from config import DOWNLOAD_DIR

def validate_downloads(expected_files_path):
    """
    Validates downloaded files against expected files.
    
    Returns:
        dict: Comparison results showing missing, extra, and matched files
    """
    print(f"-------------------------------")
    print(f"[*] Validating downloaded files")
    print(f"-------------------------------")

    # Step 1: Read expected files from JSON
    with open(expected_files_path, 'r') as f:
        expected_files = json.load(f)
    
    # Step 2: Create folder name mapping
    folder_mapping = {
        "Open_Data_in_Europe_2024": "Open data in Europe 2024",
        "Recommendations": "Recommendations", 
        "Dimensions": "Dimensions",
        "Country_profiles": "Country profiles",
        "Method_and_resources": "Method and resources"
    }
    
    # Step 3: Scan downloaded files
    downloaded_files = {}
    
    for folder_name, expected_key in folder_mapping.items():
        folder_path = Path(DOWNLOAD_DIR) / folder_name
        downloaded_files[expected_key] = []
        
        if folder_path.exists():
            for file_path in folder_path.iterdir():
                if file_path.is_file():
                    file_info = {
                        "name": file_path.name,
                        "format": file_path.suffix[1:].lower(),  # Remove dot and lowercase
                        "size": file_path.stat().st_size
                    }
                    downloaded_files[expected_key].append(file_info)
    
    # Step 4: Compare files and create results
    comparison_results = {}
    
    for tab_name in expected_files.keys():
        expected_list = expected_files[tab_name]
        downloaded_list = downloaded_files.get(tab_name, [])
        
        # Create sets for comparison (using filename and format as key)
        expected_files_set = {(file.get("name", ""), file.get("format", "").lower()) for file in expected_list if file}
        downloaded_files_set = {(file["name"], file["format"]) for file in downloaded_list}
        
        # Find differences
        missing_files_list = [f"{name} ({fmt})" for name, fmt in expected_files_set - downloaded_files_set]
        extra_files_list = [f"{name} ({fmt})" for name, fmt in downloaded_files_set - expected_files_set]
        matched_files_list = [f"{name} ({fmt})" for name, fmt in expected_files_set & downloaded_files_set]
        
        # Find zero-size files
        # TODO: We assume that the PDFs are expected to be empty because created used as proxy to tell they exist in ODM
        zero_size_files = [file for file in downloaded_list if file["size"] == 0 and file["format"] != "pdf"]
        zero_size_file_names = [file["name"] for file in zero_size_files]

        comparison_results[tab_name] = {
            "expected_count": len(expected_files_set),
            "downloaded_count": len(downloaded_files_set),
            "matched_count": len(matched_files_list),
            "missing_files": missing_files_list,
            "extra_files": extra_files_list,
            "matched_files": matched_files_list,
            "zero_size_count": len(zero_size_files),
            "zero_size_files": zero_size_file_names,
            "downloaded_details": downloaded_list
        }
    
    return comparison_results