def generate_report(validation_results):
    """
    Display validation results in a formatted, readable way
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
        print(f"   ✅ Matched:  {matched:3d} files")
        print(f"   ❌ Missing:  {missing:3d} files")
        print(f"   ➕ Extra:    {extra:3d} files")
        print(f"   ⚠️  Zero size: {zero_size:3d} files")

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

        # Show zero-size files if any
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
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"

    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"