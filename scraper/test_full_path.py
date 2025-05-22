from scraper.purdue_downloader import generate_download_path, is_wsl, convert_to_windows_path
import os
from urllib.parse import urlparse

# Test scenarios
test_cases = [
    {
        'url': 'https://docs.lib.purdue.edu/modvis/2024/va/1',
        'article_number': '1223',
        'doc_number': '1',
        'expected_dir': '/mnt/s/Departments/ePubs/Accessibility_Project/m_series/modvis/2024/va',
        'expected_filename': '1223_modvis_2024_va.pdf'
    },
    {
        'url': 'https://docs.lib.purdue.edu/modvis/2024/cmec/2',
        'article_number': '1333',
        'doc_number': '2',
        'expected_dir': '/mnt/s/Departments/ePubs/Accessibility_Project/m_series/modvis/2024/cmec',
        'expected_filename': '1333_modvis_2024_cmec.pdf'
    }
]

print("Testing download paths and filenames:")
print("=====================================")

def simulate_filename_generation(article_number, url_structure, doc_number):
    """Simulate the filename generation logic from process_single_event function"""
    series = url_structure[0] if len(url_structure) > 0 else ""
    section = url_structure[1] if len(url_structure) > 1 else "" # Year or other section identifier
    partition = url_structure[2] if len(url_structure) > 2 else "" # va, cmec, etc.
    
    # Build filename parts
    filename_parts = [article_number, series]
    
    # Add section if present (which may be a year or other identifier)
    if section:
        filename_parts.append(section)
        
    # Add partition (va, cmec, etc.) if present
    if partition:
        filename_parts.append(partition)
    
    # Combine into final filename
    custom_filename = "_".join(filename_parts)
    
    # Pad article number to 4 digits
    if len(article_number) < 4:
        padded_article_number = article_number.zfill(4)
        custom_filename = custom_filename.replace(article_number, padded_article_number, 1)
        
    # No document number in filename as the article number is unique
    return f"{custom_filename}.pdf"

for i, test in enumerate(test_cases):
    print(f"\nTest Case {i+1}:")
    print(f"URL: {test['url']}")
    
    # Get the generated directory path
    download_dir = generate_download_path(test['url'])
    print(f"Generated directory: {download_dir}")
    print(f"Expected directory: {test['expected_dir']}")
    
    # Get URL parts for filename simulation - properly parse the URL
    parsed_url = urlparse(test['url'])
    url_structure = parsed_url.path.strip('/').split('/')
    
    # Simulate filename generation
    filename = simulate_filename_generation(test['article_number'], url_structure, test['doc_number'])
    print(f"Generated filename: {filename}")
    print(f"Expected filename: {test['expected_filename']}")
    
    # Check if paths match expectations
    full_path = os.path.join(download_dir, filename)
    print(f"Full Linux path: {full_path}")
    
    if is_wsl():
        windows_path = convert_to_windows_path(full_path)
        print(f"Full Windows path: {windows_path}")
        
    # Evaluate test result
    dir_correct = download_dir == test['expected_dir']
    filename_correct = filename == test['expected_filename']
    
    if dir_correct and filename_correct:
        print("✓ Test PASSED")
    else:
        print("✗ Test FAILED")
        if not dir_correct:
            print(f"  Directory path doesn't match expected value")
        if not filename_correct:
            print(f"  Filename doesn't match expected value")