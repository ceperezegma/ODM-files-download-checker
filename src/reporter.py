# -*- coding: utf-8 -*-
"""
Reporting utilities for download validation.

This module prints a human-readable report summarizing validation results
returned by the validator component, including counts, success rates, lists of
missing/extra/zero-size files, and basic size/format statistics.
"""


def generate_report(validation_results):
    """
    Render a formatted report of download validation results.

    Behavior:
    - Iterates over tabs in the provided results and prints:
        - Expected, downloaded, matched, missing, extra, and zero-size counts.
        - Success rate (matched/expected) when expected > 0.
        - Detailed lists of missing, extra, and zero-size files when present.
        - Aggregate totals (bytes) and average file size for downloaded files.
        - A breakdown by file format/extension.
    - Uses simple console output with clear section headers and icons.

    Parameters:
        validation_results (dict): Structured results per tab. Expected keys per tab:
            - expected_count (int)
            - downloaded_count (int)
            - matched_count (int)
            - missing_files (list[str])
            - extra_files (list[str])
            - zero_size_count (int)
            - zero_size_files (list[str])
            - downloaded_details (list[dict]): each item contains:
                - size (int): size in bytes
                - format (str|None): file extension without dot or None

    Returns:
        None

    Side Effects:
        - Prints a multi-section report to stdout.

    Example:
        results = {
            "Open Data in Europe 2024": {
                "expected_count": 10,
                "downloaded_count": 9,
                "matched_count": 9,
                "missing_files": ["file_a.json"],
                "extra_files": [],
                "zero_size_count": 1,
                "zero_size_files": ["file_b.pdf"],
                "downloaded_details": [{"size": 1024, "format": "json"}]
            }
        }
        generate_report(results)
    """
    print("\n" + "=" * 80)
    print("📊 DOWNLOAD VALIDATION REPORT")
    print("=" * 80)

    for tab_name, results in validation_results.items():
        print(f"\n📁 {tab_name}")
        print("-" * 60)

        # Summary statistics
        expected = results['expected_count']
        downloaded = results['downloaded_count']
        matched = results['matched_count']
        missing = len(results['missing_files'])
        extra = len(results['extra_files'])
        zero_size = results['zero_size_count']

        print(f"   Expected:   {expected:3d} files")
        print(f"   Downloaded: {downloaded:3d} files")
        print(f"   ✅ Matched: {matched:3d} files")
        print(f"   ❌ Missing: {missing:3d} files")
        print(f"   ➕ Extra:   {extra:3d} files")
        print(f"   ⚠️  Zero size: {zero_size:3d} files - excluding proxy PDF files created for PDF resources")

        # Success rate
        if expected > 0:
            success_rate = (matched / expected) * 100
            print(f"   📈 Success:  {success_rate:.1f}%")

        # Show missing files if any
        if results['missing_files']:
            print(f"\n   ❌ Missing files ({len(results['missing_files'])}):")
            for i, file in enumerate(results['missing_files'], 1):
                print(f"      {i}. {file}")

        # Show extra files if any
        if results['extra_files']:
            print(f"\n   ➕ Extra files ({len(results['extra_files'])}):")
            for i, file in enumerate(results['extra_files'], 1):
                print(f"      {i}. {file}")

        # Show zero-size files if any (exclude PDFs as they're expected to be empty)
        if results['zero_size_files']:
            print(f"\n   ⚠️  Zero-size files ({len(results['zero_size_files'])}):")
            for i, file in enumerate(results['zero_size_files'], 1):
                print(f"      {i}. {file}")

        # Show file size summary for downloaded files
        if results['downloaded_details']:
            total_size = sum(file['size'] for file in results['downloaded_details'])
            avg_size = total_size / len(results['downloaded_details'])
            print(f"\n   💾 Total size: {format_file_size(total_size)}")
            print(f"   📏 Avg size:   {format_file_size(avg_size)}")

            # Show format breakdown
            format_counts = {}
            for file in results['downloaded_details']:
                fmt = file['format'] or 'no extension'
                format_counts[fmt] = format_counts.get(fmt, 0) + 1

            if format_counts:
                print(f"\n   📋 Format breakdown:")
                # Calculate max format name length for alignment
                display_formats = [(fmt if fmt != 'zip' else 'zip/json', count) for fmt, count in format_counts.items()]
                max_fmt_len = max(len(fmt) for fmt, _ in display_formats)
                
                for fmt, count in sorted(display_formats):
                    print(f"      {fmt + ':':<{max_fmt_len + 1}} {count:3d} files")

    print("\n" + "=" * 80)


def format_file_size(size_bytes):
    """
    Convert a byte count into a human-readable size string.

    Parameters:
        size_bytes (int|float): The size in bytes.

    Returns:
        str: A string with an appropriate unit, e.g., "0 B", "1.5 KB", "2.0 MB",
        "3.1 GB", or "4.0 TB".

    Notes:
        - Uses a 1024-based progression for units.
        - Rounds to one decimal place.

    Example:
        format_file_size(1536) -> "1.5 KB"
    """
    if size_bytes == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"