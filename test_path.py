from purdue_downloader import generate_download_path, is_wsl, convert_to_windows_path

# Test with example URLs
urls = [
    'https://docs.lib.purdue.edu/modvis/2024/va',
    'https://docs.lib.purdue.edu/modvis/2024/cmec'
]

for url in urls:
    print(f"Generated path for {url}:")
    path = generate_download_path(url)
    print(f"Linux path: {path}")
    if is_wsl():
        print(f"Windows path: {convert_to_windows_path(path)}")
    print()