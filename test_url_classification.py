#!/usr/bin/env python3
"""
Test URL classification for manuscript vs section pages
"""
import sys
sys.path.append('/home/schipp0/ePubs_Main')

from scraper.optimized_downloader import OptimizedDownloadStrategy

def test_url_classification():
    """Test the URL classification logic"""
    
    strategy = OptimizedDownloadStrategy()
    base_url = "https://docs.lib.purdue.edu/roadschool/"
    
    # Test cases
    test_urls = [
        # Should be SECTION pages (intermediate)
        ("https://docs.lib.purdue.edu/roadschool/2025", "SECTION"),
        ("https://docs.lib.purdue.edu/roadschool/2025/presentations/", "SECTION"),
        ("https://docs.lib.purdue.edu/roadschool/2025/opening/", "SECTION"),
        ("https://docs.lib.purdue.edu/roadschool/1924/proceedings/", "SECTION"),
        ("https://docs.lib.purdue.edu/roadschool/2011/pres/", "SECTION"),
        
        # Should be MANUSCRIPT pages (final)
        ("https://docs.lib.purdue.edu/roadschool/2025/presentations/22/", "MANUSCRIPT"),
        ("https://docs.lib.purdue.edu/roadschool/2025/opening/1/", "MANUSCRIPT"),
        ("https://docs.lib.purdue.edu/roadschool/1924/proceedings/1/", "MANUSCRIPT"),
        ("https://docs.lib.purdue.edu/roadschool/2011/pres/26/", "MANUSCRIPT"),
        
        # Should be NEITHER (base or invalid)
        ("https://docs.lib.purdue.edu/roadschool/", "NEITHER"),
        ("https://docs.lib.purdue.edu/roadschool/search", "NEITHER"),
        ("https://docs.lib.purdue.edu/roadschool/about", "NEITHER"),
        ("https://docs.lib.purdue.edu/roadschool/document.pdf", "NEITHER"),
    ]
    
    print("URL Classification Test Results:")
    print("=" * 80)
    
    for url, expected in test_urls:
        is_manuscript = strategy._is_manuscript_page_url(url, base_url)
        is_section = strategy._is_section_page_url(url, base_url)
        
        if is_manuscript:
            actual = "MANUSCRIPT"
        elif is_section:
            actual = "SECTION"
        else:
            actual = "NEITHER"
        
        status = "✅" if actual == expected else "❌"
        print(f"{status} {url}")
        print(f"    Expected: {expected}, Actual: {actual}")
        if actual != expected:
            print(f"    ⚠️  MISMATCH!")
        print()

if __name__ == "__main__":
    test_url_classification()