#!/usr/bin/env python3
"""
Test script for web scraper URL discovery functionality.
Tests that the scraper can take a base URL and find sub-pages as intended.
"""

import sys
import os
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time

# Add scraper directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'scraper'))

# Import the scraper
from scraper.optimized_downloader import OptimizedDownloadStrategy

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def test_url_discovery(base_url: str, headless: bool = True):
    """
    Test the URL discovery functionality of the web scraper.
    
    Args:
        base_url: The base collection URL to test
        headless: Whether to run browser in headless mode
    """
    print(f"\n{'='*60}")
    print(f"Testing URL Discovery for: {base_url}")
    print(f"{'='*60}")
    
    # Set up Chrome options
    chrome_options = Options()
    if headless:
        chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    driver = None
    try:
        # Initialize driver
        try:
            driver = webdriver.Chrome(options=chrome_options)
            logger.info("✅ Chrome WebDriver initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Chrome WebDriver: {e}")
            return False
        
        # Initialize the downloader
        downloader = OptimizedDownloadStrategy()
        
        # Test 1: Navigate to base URL
        print(f"\n🔍 Test 1: Navigating to base URL...")
        try:
            driver.get(base_url)
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            logger.info(f"✅ Successfully navigated to: {base_url}")
            logger.info(f"   Page title: {driver.title}")
            print(f"   Current URL: {driver.current_url}")
        except TimeoutException:
            logger.error(f"❌ Timeout loading page: {base_url}")
            return False
        except Exception as e:
            logger.error(f"❌ Error navigating to base URL: {e}")
            return False
        
        # Test 2: Extract document page URLs
        print(f"\n🔍 Test 2: Extracting document page URLs...")
        try:
            document_links = downloader.extract_document_pages_from_collection(driver, base_url)
            
            if not document_links:
                logger.warning("⚠️  No document links found")
                print("   This could indicate:")
                print("   - The page structure has changed")
                print("   - The collection is empty")
                print("   - The CSS selectors need updating")
                return False
            
            logger.info(f"✅ Found {len(document_links)} document page links")
            print(f"   Total document links discovered: {len(document_links)}")
            
            # Display first few links for verification
            print(f"\n📝 Sample document links found:")
            for i, link in enumerate(document_links[:5]):  # Show first 5
                print(f"   {i+1}. {link['url']}")
                if link['text']:
                    print(f"      Title: {link['text']}")
                if link['title']:
                    print(f"      Alt Title: {link['title']}")
            
            if len(document_links) > 5:
                print(f"   ... and {len(document_links) - 5} more")
            
        except Exception as e:
            logger.error(f"❌ Error extracting document URLs: {e}")
            return False
        
        # Test 3: Validate discovered URLs
        print(f"\n🔍 Test 3: Validating discovered URLs...")
        try:
            valid_urls = 0
            pdf_urls = 0
            collection_urls = 0
            other_urls = 0
            
            for link in document_links:
                url = link['url']
                
                # Check if it's a valid document page URL
                if downloader._is_document_page_url(url, base_url):
                    valid_urls += 1
                elif '.pdf' in url.lower():
                    pdf_urls += 1
                elif url == base_url:
                    collection_urls += 1
                else:
                    other_urls += 1
            
            print(f"   ✅ Valid document page URLs: {valid_urls}")
            print(f"   📄 Direct PDF URLs: {pdf_urls}")
            print(f"   📁 Collection URLs: {collection_urls}")
            print(f"   🔗 Other URLs: {other_urls}")
            
            if valid_urls > 0:
                logger.info(f"✅ URL validation successful - {valid_urls} valid document pages")
            else:
                logger.warning("⚠️  No valid document page URLs found")
                
        except Exception as e:
            logger.error(f"❌ Error validating URLs: {e}")
            return False
        
        # Test 4: Test a sample document page (optional)
        if document_links and len(document_links) > 0:
            print(f"\n🔍 Test 4: Testing sample document page access...")
            try:
                sample_url = document_links[0]['url']
                driver.get(sample_url)
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.TAG_NAME, "body"))
                )
                logger.info(f"✅ Successfully accessed sample document page")
                print(f"   Sample page title: {driver.title}")
                print(f"   Sample page URL: {sample_url}")
            except Exception as e:
                logger.warning(f"⚠️  Could not access sample document page: {e}")
        
        print(f"\n{'='*60}")
        print(f"✅ URL Discovery Test PASSED")
        print(f"   Base URL: {base_url}")
        print(f"   Document links found: {len(document_links)}")
        print(f"   Valid document pages: {valid_urls}")
        print(f"{'='*60}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Unexpected error during testing: {e}")
        return False
    
    finally:
        if driver:
            driver.quit()
            logger.info("🔄 WebDriver closed")

def main():
    """Main function to run the URL discovery test."""
    
    # Test URLs (you can modify these)
    test_urls = [
        "https://docs.lib.purdue.edu/roadschool/",
        "https://docs.lib.purdue.edu/roadschool/2024",
        "https://docs.lib.purdue.edu/roadschool/2023"
    ]
    
    print("🧪 Web Scraper URL Discovery Test")
    print("=" * 60)
    
    # Use default test URLs for automated testing
    print(f"Using default test URLs...")
    
    success_count = 0
    total_tests = len(test_urls)
    
    for i, url in enumerate(test_urls, 1):
        print(f"\n🔄 Running test {i}/{total_tests}")
        
        try:
            if test_url_discovery(url, headless=True):
                success_count += 1
            else:
                print(f"❌ Test failed for: {url}")
        except KeyboardInterrupt:
            print(f"\n⏹️  Test interrupted by user")
            break
        except Exception as e:
            print(f"❌ Test error for {url}: {e}")
    
    print(f"\n📊 Test Summary:")
    print(f"   Tests run: {success_count}/{total_tests}")
    print(f"   Success rate: {(success_count/total_tests)*100:.1f}%")
    
    if success_count == total_tests:
        print(f"🎉 All tests PASSED!")
        return 0
    else:
        print(f"⚠️  Some tests FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())