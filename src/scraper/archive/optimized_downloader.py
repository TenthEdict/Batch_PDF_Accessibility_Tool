#!/usr/bin/env python3
"""
Optimized document downloader with prioritized direct HTTP downloads.

This module provides enhanced download strategies with better cross-platform support
and improved reliability for both macOS and WSL environments.
"""

import os
import time
import logging
import platform
import requests
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from urllib.parse import urlparse, urljoin, parse_qs
import tempfile
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Import existing components
from .purdue_downloader import (
    get_http_session,
    setup_webdriver,
    wait_for_page_load,
    handle_cookie_banner,
    retry_with_backoff,
    check_login_required,
    handle_login
)

logger = logging.getLogger(__name__)


class OptimizedDownloadStrategy:
    """
    Enhanced download strategy that prioritizes direct HTTP downloads
    over browser automation for better reliability and performance.
    """
    
    def __init__(self, session=None):
        self.session = session or get_http_session()
        self.download_stats = {
            "direct_http_success": 0,
            "browser_fallback_success": 0,
            "total_failures": 0
        }
    
    @retry_with_backoff(retries=2, backoff_factor=1.0)
    def download_pdf_direct(self, pdf_url: str, output_path: Path, 
                           cookies: Optional[Dict] = None, 
                           referer: Optional[str] = None) -> bool:
        """
        Download PDF directly via HTTP with optimized headers and error handling.
        
        Args:
            pdf_url: Direct URL to the PDF
            output_path: Where to save the PDF
            cookies: Browser cookies for authentication
            referer: Referer header to include
            
        Returns:
            True if download was successful, False otherwise
        """
        try:
            # Prepare headers for better compatibility
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*;q=0.9',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
            }
            
            if referer:
                headers['Referer'] = referer
            
            logger.info(f"Attempting direct HTTP download: {pdf_url}")
            
            # Make the request with streaming for large files
            response = self.session.get(
                pdf_url,
                headers=headers,
                cookies=cookies,
                stream=True,
                timeout=60,
                allow_redirects=True
            )
            
            # Check response
            if response.status_code != 200:
                logger.warning(f"HTTP {response.status_code} for {pdf_url}")
                return False
            
            # Verify content type
            content_type = response.headers.get('Content-Type', '').lower()
            
            # More flexible content type checking
            if not any(ct in content_type for ct in ['application/pdf', 'application/octet-stream', 'binary/octet-stream']):
                # Check if it might be a PDF despite content type
                first_chunk = next(response.iter_content(chunk_size=1024), b'')
                if not first_chunk.startswith(b'%PDF'):
                    logger.warning(f"Content type '{content_type}' doesn't appear to be PDF")
                    return False
                else:
                    logger.info(f"Content type '{content_type}' but starts with PDF header - proceeding")
            
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Download the file
            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0
            
            with open(output_path, 'wb') as f:
                # Write the first chunk if we read it for validation
                if 'first_chunk' in locals():
                    f.write(first_chunk)
                    downloaded_size += len(first_chunk)
                
                # Continue with the rest
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Log progress for large files
                        if total_size > 0 and downloaded_size % (1024 * 1024) == 0:  # Every MB
                            progress = (downloaded_size / total_size) * 100
                            logger.debug(f"Download progress: {progress:.1f}%")
            
            # Verify download
            if output_path.exists() and output_path.stat().st_size > 0:
                logger.info(f"✅ Successfully downloaded PDF directly: {output_path.name} ({downloaded_size:,} bytes)")
                self.download_stats["direct_http_success"] += 1
                return True
            else:
                logger.warning(f"Downloaded file is empty or doesn't exist: {output_path}")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"HTTP request failed for {pdf_url}: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error downloading {pdf_url}: {e}")
            return False
    
    def extract_document_pages_from_collection(self, driver, base_url: str) -> List[Dict]:
        """
        Extract individual document page URLs from a collection page with hierarchical navigation.
        
        This handles the hierarchical structure:
        1. Collection page (e.g., /roadschool/)
        2. Year/section pages (e.g., /roadschool/2025/presentations/)
        3. Individual manuscript pages (e.g., /roadschool/2025/presentations/22/)
        
        Returns:
            List of dictionaries with 'url', 'text', 'title' information for document pages
        """
        document_links = []
        
        try:
            # First, try to find manuscript pages directly (ends with number)
            manuscript_links = self._find_manuscript_pages(driver, base_url)
            if manuscript_links:
                logger.info(f"✅ Found {len(manuscript_links)} manuscript pages directly on base page")
                return manuscript_links
            
            # If no manuscript pages found, look for intermediate section/year pages
            section_links = self._find_section_pages(driver, base_url)
            if section_links:
                logger.info(f"🔍 Found {len(section_links)} section pages to explore hierarchically")
                # Navigate to each section and extract manuscript pages
                for i, section_url in enumerate(section_links):
                    logger.info(f"📁 Exploring section {i+1}/{len(section_links)}: {section_url}")
                    driver.get(section_url)
                    wait_for_page_load(driver)
                    handle_cookie_banner(driver)
                    
                    # Find manuscript pages in this section
                    section_manuscripts = self._find_manuscript_pages(driver, section_url)
                    
                    # If no manuscripts found, look for sub-sections to explore deeper
                    if not section_manuscripts:
                        logger.info(f"  📄 Found 0 manuscripts in this section - looking for sub-sections")
                        sub_section_links = self._find_section_pages(driver, section_url)
                        if sub_section_links:
                            logger.info(f"  🔍 Found {len(sub_section_links)} sub-sections to explore")
                            for j, sub_section_url in enumerate(sub_section_links):
                                logger.info(f"    📁 Exploring sub-section {j+1}/{len(sub_section_links)}: {sub_section_url}")
                                driver.get(sub_section_url)
                                wait_for_page_load(driver)
                                handle_cookie_banner(driver)
                                
                                # Find manuscript pages in this sub-section
                                sub_section_manuscripts = self._find_manuscript_pages(driver, sub_section_url)
                                document_links.extend(sub_section_manuscripts)
                                logger.info(f"      📄 Found {len(sub_section_manuscripts)} manuscripts in this sub-section")
                        else:
                            logger.info(f"  📄 No sub-sections found in {section_url}")
                    else:
                        document_links.extend(section_manuscripts)
                        logger.info(f"  📄 Found {len(section_manuscripts)} manuscripts in this section")
                    
                    # Return to base URL for next iteration
                    driver.get(base_url)
                    wait_for_page_load(driver)
            
            # Remove duplicates while preserving order
            unique_links = []
            seen_urls = set()
            for link in document_links:
                if link['url'] not in seen_urls:
                    unique_links.append(link)
                    seen_urls.add(link['url'])
            
            logger.info(f"Found {len(unique_links)} total document page links")
            return unique_links
            
        except Exception as e:
            logger.warning(f"Error extracting document page URLs: {e}")
            return []
    
    def _find_manuscript_pages(self, driver, base_url: str) -> List[Dict]:
        """
        Find individual manuscript pages that end with a number (e.g., /22/, /1/).
        These are the final pages where we can find Edit Event buttons.
        """
        manuscript_links = []
        
        try:
            # Look for links that end with a number (manuscript pages)
            # These selectors target manuscript pages specifically
            manuscript_selectors = [
                # Standard manuscript page patterns
                "a[href*='docs.lib.purdue.edu']",
                "a[href^='/']",
                "a[href^='https://docs.lib.purdue.edu']"
            ]
            
            for selector in manuscript_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and self._is_manuscript_page_url(href, base_url):
                            if href not in [link['url'] for link in manuscript_links]:
                                manuscript_links.append({
                                    'url': href,
                                    'text': element.text.strip(),
                                    'title': element.get_attribute("title") or "",
                                    'class': element.get_attribute("class") or ""
                                })
                except:
                    continue
            
            # Convert relative URLs to absolute
            for link in manuscript_links:
                if link['url'].startswith('/'):
                    link['url'] = urljoin(base_url, link['url'])
            
            return manuscript_links
            
        except Exception as e:
            logger.warning(f"Error finding manuscript pages: {e}")
            return []
    
    def _find_section_pages(self, driver, base_url: str) -> List[str]:
        """
        Find intermediate section/year pages (e.g., /roadschool/2025/presentations/).
        These contain links to individual manuscript pages.
        """
        section_links = []
        
        try:
            # Look for links that represent sections/years but not manuscripts
            section_selectors = [
                "a[href*='docs.lib.purdue.edu']",
                "a[href^='/']",
                "a[href^='https://docs.lib.purdue.edu']"
            ]
            
            for selector in section_selectors:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        href = element.get_attribute("href")
                        if href and self._is_section_page_url(href, base_url):
                            if href not in section_links:
                                # Convert relative to absolute
                                if href.startswith('/'):
                                    href = urljoin(base_url, href)
                                section_links.append(href)
                except:
                    continue
            
            return section_links
            
        except Exception as e:
            logger.warning(f"Error finding section pages: {e}")
            return []
    
    def _is_manuscript_page_url(self, url: str, base_url: str) -> bool:
        """
        Check if URL is a manuscript page (ends with a number).
        
        Examples:
        - /roadschool/2025/presentations/22/ → True (manuscript page)
        - /roadschool/2025/presentations/ → False (section page)
        - /roadschool/ → False (collection page)
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Must be from the same domain
            if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
                return False
            
            path = parsed_url.path.strip('/')
            base_path = parsed_base.path.strip('/')
            
            # Skip if it's the same as base URL
            if path == base_path:
                return False
            
            # Skip direct PDF URLs
            if '.pdf' in path.lower() or 'viewcontent' in path.lower():
                return False
                
            # Skip admin/system URLs
            if any(skip in path.lower() for skip in ['search', 'browse', 'about', 'contact', 'admin', 'cgi']):
                return False
            
            # Must be longer than base path (more specific)
            if not path.startswith(base_path):
                return False
                
            # Check if it ends with a number (manuscript page)
            path_parts = path.split('/')
            if path_parts and path_parts[-1].isdigit():
                # Additional check: make sure it's not just a year (should be more specific)
                # Years are typically 4 digits, manuscript numbers are usually shorter
                # and there should be more path components for a real manuscript page
                last_part = path_parts[-1]
                if len(last_part) == 4 and last_part.isdigit() and int(last_part) > 1900:
                    # This looks like a year, not a manuscript number
                    # Need at least one more level (e.g., /roadschool/2025/presentations/22/)
                    return False
                return True
                
            return False
            
        except Exception as e:
            logger.debug(f"Error checking manuscript page URL {url}: {e}")
            return False
    
    def _is_section_page_url(self, url: str, base_url: str) -> bool:
        """
        Check if URL is a section/year page (intermediate level).
        
        Examples:
        - /roadschool/2025/presentations/ → True (section page)
        - /roadschool/2025/presentations/22/ → False (manuscript page)
        - /roadschool/ → False (collection page)
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Must be from the same domain
            if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
                return False
            
            path = parsed_url.path.strip('/')
            base_path = parsed_base.path.strip('/')
            
            # Skip if it's the same as base URL
            if path == base_path:
                return False
            
            # Skip direct PDF URLs
            if '.pdf' in path.lower() or 'viewcontent' in path.lower():
                return False
                
            # Skip admin/system URLs
            if any(skip in path.lower() for skip in ['search', 'browse', 'about', 'contact', 'admin', 'cgi']):
                return False
            
            # Must be longer than base path (more specific)
            if not path.startswith(base_path):
                return False
                
            # Check if it's a section page (doesn't end with number, or ends with year)
            path_parts = path.split('/')
            if path_parts:
                last_part = path_parts[-1]
                
                # Case 1: Doesn't end with number at all (e.g., /roadschool/2025/presentations/)
                if not last_part.isdigit():
                    base_parts = base_path.split('/') if base_path else []
                    if len(path_parts) > len(base_parts):
                        return True
                
                # Case 2: Ends with a 4-digit year (e.g., /roadschool/2025)
                elif (len(last_part) == 4 and last_part.isdigit() and 
                      int(last_part) > 1900 and int(last_part) < 2100):
                    base_parts = base_path.split('/') if base_path else []
                    if len(path_parts) > len(base_parts):
                        return True
                    
            return False
            
        except Exception as e:
            logger.debug(f"Error checking section page URL {url}: {e}")
            return False
    
    def _is_document_page_url(self, url: str, base_url: str) -> bool:
        """
        Check if a URL is a document page (not a direct PDF or collection page).
        
        Document pages typically have patterns like:
        - /chempubs/2016/1/
        - /agroenviron/2016/Abstracts/1/
        """
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)
            
            # Must be from the same domain
            if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
                return False
            
            path = parsed_url.path.strip('/')
            base_path = parsed_base.path.strip('/')
            
            # Skip if it's the same as base URL (collection page)
            if path == base_path:
                return False
            
            # Skip direct PDF URLs
            if '.pdf' in path.lower() or 'viewcontent' in path.lower():
                return False
            
            # Skip non-document URLs
            if any(skip in path.lower() for skip in ['search', 'browse', 'about', 'contact', 'admin']):
                return False
            
            # Document pages typically have the collection path as prefix
            # and end with a number (document ID)
            if base_path and not path.startswith(base_path):
                return False
            
            # Check if path ends with a number (document ID)
            path_parts = path.split('/')
            if path_parts and path_parts[-1].isdigit():
                return True
            
            # Some documents may have additional path components
            # Accept if it's longer than base path and looks like a document
            if len(path.split('/')) > len(base_path.split('/')):
                return True
            
            return False
            
        except Exception:
            return False
    
    def process_document_page_for_manuscript(self, driver, document_url: str, username: str = None, password: str = None) -> Optional[str]:
        """
        Process a document page using Edit Event → View Revisions workflow to get manuscript PDF URL.
        
        Args:
            driver: Selenium WebDriver instance
            document_url: URL of the document page
            
        Returns:
            Manuscript PDF URL if found, None otherwise
        """
        try:
            logger.info(f"Processing document page: {document_url}")
            
            # Navigate to the document page
            driver.get(document_url)
            wait_for_page_load(driver)
            handle_cookie_banner(driver)
            
            # Check if login is required on this document page
            logger.info(f"🔍 Checking login requirements on document page: {driver.current_url}")
            doc_login_required = check_login_required_fixed(driver)
            
            # Also check if redirected to login
            if "login.cgi" in driver.current_url:
                doc_login_required = True
                logger.info(f"Document page redirected to login: {driver.current_url}")
            
            if doc_login_required:
                if not username or not password:
                    logger.error("Login required on document page but no credentials available")
                    return None
                
                logger.info("🔐 Login required on document page - authenticating")
                login_successful = handle_login_fixed(driver, username, password, manual_login=False)
                if not login_successful:
                    logger.error("❌ Login failed on document page")
                    return None
                
                logger.info("✅ Login successful on document page")
                # Reload the document page after login
                driver.get(document_url)
                wait_for_page_load(driver)
            
            # Try to find and click Edit Event or Edit Submission button
            edit_event_successful = False
            edit_button_found = None
            
            # Debug: List all available links to help troubleshoot
            try:
                all_links = driver.find_elements(By.CSS_SELECTOR, "a")
                edit_related_links = [link for link in all_links if "edit" in link.text.lower() or "editor.cgi" in (link.get_attribute('href') or "")]
                if edit_related_links:
                    logger.info("Found edit-related links on page:")
                    for link in edit_related_links[:5]:  # Show first 5
                        logger.info(f"  Text: '{link.text}' | href: '{link.get_attribute('href')}'")
            except:
                pass
            
            # Primary selectors - look for Edit Event first (most specific)
            edit_event_selectors = [
                ("xpath", "//a[text()='Edit Event' and not(contains(text(), 'Manage'))]"),  # Exact match first
                ("xpath", "//a[contains(text(), 'Edit Event') and not(contains(text(), 'Manage'))]"),  # Contains match
                ("css", "a[href*='editor.cgi'][href*='window=abstract']"),
                ("xpath", "//a[contains(@href, 'editor.cgi') and contains(@href, 'window=abstract') and not(contains(text(), 'Manage'))]")
            ]
            
            # Try Edit Event selectors first
            for selector_type, selector in edit_event_selectors:
                try:
                    by_method = By.XPATH if selector_type == "xpath" else By.CSS_SELECTOR
                    edit_button = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    # Verify it's not a manage button
                    button_text = edit_button.text.lower()
                    if ("manage" not in button_text and 
                        ("edit event" in button_text or "edit" in button_text)):
                        edit_button_found = edit_button
                        logger.info(f"Found Edit Event button: '{edit_button.text}'")
                        break
                except:
                    continue
            
            # If Edit Event not found, try Edit Submission selectors (more specific)
            if not edit_button_found:
                logger.info("Edit Event not found, looking for Edit Submission...")
                edit_submission_selectors = [
                    ("xpath", "//a[text()='Edit Submission' or text()='Edit submission']"),
                    ("xpath", "//a[contains(text(), 'Edit Submission') and not(contains(text(), 'Manage'))]"),
                    ("xpath", "//header//a[contains(text(), 'Edit') and not(contains(text(), 'Manage'))]"),
                    ("css", "header a[href*='editor.cgi']:not([href*='manage'])")
                ]
                
                for selector_type, selector in edit_submission_selectors:
                    try:
                        by_method = By.XPATH if selector_type == "xpath" else By.CSS_SELECTOR
                        edit_button = WebDriverWait(driver, 3).until(
                            EC.element_to_be_clickable((by_method, selector))
                        )
                        # Double-check it's not a manage button
                        button_text = edit_button.text.lower()
                        href = edit_button.get_attribute('href') or ""
                        
                        if ("manage" not in button_text and 
                            "manage" not in href.lower() and
                            ("edit submission" in button_text or "edit" in button_text)):
                            edit_button_found = edit_button
                            logger.info(f"Found Edit Submission button: '{edit_button.text}'")
                            break
                    except:
                        continue
            
            # Fallback: try user-destinations menu (but exclude Manage buttons)
            if not edit_button_found:
                logger.info("Trying user-destinations menu for edit options...")
                try:
                    user_destination_links = driver.find_elements(By.CSS_SELECTOR, "#user-destinations ul li a")
                    for link in user_destination_links:
                        text = link.text.lower()
                        href = link.get_attribute('href') or ""
                        if (("edit" in text or "editor.cgi" in href) and 
                            "manage" not in text and 
                            "manage" not in href.lower()):
                            edit_button_found = link
                            logger.info(f"Found edit button in user menu: '{link.text}'")
                            break
                except:
                    pass
            
            # Click the found button
            if edit_button_found:
                try:
                    button_text = edit_button_found.text or edit_button_found.get_attribute('title') or 'Edit button'
                    logger.info(f"Clicking {button_text}...")
                    
                    # Try click with JavaScript fallback
                    try:
                        edit_button_found.click()
                    except:
                        driver.execute_script("arguments[0].click();", edit_button_found)
                    
                    edit_event_successful = True
                    logger.info(f"Successfully clicked {button_text}")
                    
                    # Wait for editor page to load
                    WebDriverWait(driver, 10).until(
                        lambda d: "editor.cgi" in d.current_url
                    )
                    
                except Exception as e:
                    logger.error(f"Failed to click edit button: {e}")
                    edit_event_successful = False
            
            if not edit_event_successful:
                logger.warning("Could not find or click Edit Event or Edit Submission button")
                return None
            
            # Now try to find and click View Revisions
            revisions_successful = False
            revision_selectors = [
                ("xpath", "//a[contains(text(), 'View Revisions')]"),
                ("xpath", "//a[contains(text(), 'Revisions')]"),
                ("css", "a[href*='pickvers']"),
                ("xpath", "//div[@id='MenuSidebar']//a[contains(text(), 'Revisions')]")
            ]
            
            for selector_type, selector in revision_selectors:
                try:
                    by_method = By.XPATH if selector_type == "xpath" else By.CSS_SELECTOR
                    revisions_link = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((by_method, selector))
                    )
                    
                    # Try click with JavaScript fallback
                    try:
                        revisions_link.click()
                    except:
                        driver.execute_script("arguments[0].click();", revisions_link)
                    
                    revisions_successful = True
                    logger.info(f"Successfully clicked View Revisions link")
                    
                    # Wait for revisions page to load
                    WebDriverWait(driver, 10).until(
                        lambda d: "pickvers" in d.current_url
                    )
                    break
                    
                except:
                    continue
            
            if not revisions_successful:
                logger.warning("Could not find or click View Revisions link")
                return None
            
            # Extract PDF URL from the revision history table (most recent)
            pdf_url = None
            pdf_selectors = [
                "table[id*='revision'] tr:first-child a[href*='viewcontent']",
                "table tr:first-child a[href*='viewcontent']",
                "a[href*='viewcontent']"
            ]
            
            for selector in pdf_selectors:
                try:
                    pdf_element = driver.find_element(By.CSS_SELECTOR, selector)
                    pdf_url = pdf_element.get_attribute("href")
                    if pdf_url:
                        logger.info(f"Found manuscript PDF URL: {pdf_url}")
                        break
                except:
                    continue
            
            return pdf_url
            
        except Exception as e:
            logger.error(f"Error processing document page {document_url}: {e}")
            return None
    
    def download_with_fallback(self, pdf_url: str, output_path: Path, 
                              driver=None, cookies: Optional[Dict] = None,
                              referer: Optional[str] = None) -> bool:
        """
        Download PDF with direct HTTP first, browser fallback second.
        
        Args:
            pdf_url: URL of the PDF to download
            output_path: Where to save the PDF
            driver: Selenium WebDriver for fallback
            cookies: Browser cookies for authentication
            referer: Referer header
            
        Returns:
            True if download successful, False otherwise
        """
        # Strategy 1: Direct HTTP download
        if self.download_pdf_direct(pdf_url, output_path, cookies, referer):
            return True
        
        # Strategy 2: Browser fallback (if driver available)
        if driver:
            return self._browser_download_fallback(pdf_url, output_path, driver)
        
        logger.error(f"All download strategies failed for {pdf_url}")
        self.download_stats["total_failures"] += 1
        return False
    
    def _browser_download_fallback(self, pdf_url: str, output_path: Path, driver) -> bool:
        """Browser-based download fallback strategy."""
        try:
            logger.info(f"Attempting browser fallback download for {pdf_url}")
            
            # Navigate to PDF URL
            driver.get(pdf_url)
            
            # Wait for page load
            wait_for_page_load(driver)
            
            # Handle cookie banners
            handle_cookie_banner(driver)
            
            # Check if PDF is displayed in browser
            time.sleep(3)  # Allow time for PDF to load
            
            # Try to trigger download via JavaScript
            try:
                driver.execute_script("""
                    // Try to trigger download
                    var link = document.createElement('a');
                    link.href = window.location.href;
                    link.download = '';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                """)
            except:
                pass
            
            # Check for successful download
            # Note: This is simplified - in practice you'd monitor the download directory
            time.sleep(5)
            
            logger.info("Browser fallback download initiated")
            self.download_stats["browser_fallback_success"] += 1
            return True
            
        except Exception as e:
            logger.error(f"Browser fallback failed: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get download statistics."""
        total_attempts = sum(self.download_stats.values())
        
        return {
            **self.download_stats,
            "total_attempts": total_attempts,
            "direct_success_rate": (
                self.download_stats["direct_http_success"] / max(total_attempts, 1) * 100
            ),
            "overall_success_rate": (
                (self.download_stats["direct_http_success"] + 
                 self.download_stats["browser_fallback_success"]) / max(total_attempts, 1) * 100
            )
        }


class CrossPlatformChromeManager:
    """
    Enhanced Chrome management for both macOS and WSL environments.
    """
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.is_wsl = self._detect_wsl()
        self._driver_cache = {}
    
    def _detect_wsl(self) -> bool:
        """Detect WSL environment."""
        try:
            if "microsoft" in platform.release().lower():
                return True
            if os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop'):
                return True
            with open('/proc/version', 'r') as f:
                if 'microsoft' in f.read().lower():
                    return True
        except:
            pass
        return False
    
    def get_optimized_chrome_options(self, download_dir: str, manual_login: bool = False) -> Options:
        """Get optimized Chrome options for the current platform."""
        options = Options()
        
        # Common options
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-blink-features=AutomationControlled")
        
        # Platform-specific optimizations
        if self.is_wsl:
            # WSL-specific optimizations
            if not manual_login:
                options.add_argument("--headless=new")
                options.add_argument("--disable-extensions")
                options.add_argument("--disable-plugins")
            else:
                # Manual login mode - use visible browser
                logger.info("Manual login mode - using visible browser in WSL")
                logger.info("Using Linux Chrome for manual login in WSL")
                
                # Allow extensions and plugins for better manual browsing experience
                # Don't disable extensions/plugins in manual mode
                
                # Explicitly set Chrome binary path for WSL
                chrome_paths = [
                    "/usr/bin/google-chrome",
                    "/usr/bin/google-chrome-stable",
                    "/opt/google/chrome/google-chrome"
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        logger.info(f"Setting Chrome binary path to: {chrome_path}")
                        options.binary_location = chrome_path
                        break
                
                # Set up X11 forwarding for WSL browser display
                if not os.environ.get('DISPLAY'):
                    os.environ['DISPLAY'] = ':0'
        elif self.platform == "darwin":
            # macOS-specific optimizations
            # Use visible browser for better compatibility with some sites
            pass
        
        # Download preferences
        prefs = {
            "profile.default_content_setting_values.cookies": 1,
            "profile.default_content_setting_values.notifications": 2,
            "profile.cookie_controls_mode": 0,
            "download.default_directory": download_dir,
            "download.prompt_for_download": False,
            "plugins.always_open_pdf_externally": True,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": False
        }
        options.add_experimental_option("prefs", prefs)
        
        return options
    
    def create_driver(self, download_dir: str, manual_login: bool = False) -> webdriver.Chrome:
        """Create an optimized Chrome driver for the current platform."""
        options = self.get_optimized_chrome_options(download_dir, manual_login)
        
        try:
            # Try standard initialization first
            driver = webdriver.Chrome(options=options)
            logger.info(f"✅ Chrome driver created successfully on {self.platform}")
            return driver
        except Exception as e:
            logger.warning(f"Standard Chrome initialization failed: {e}")
            
            # Try with downloaded ChromeDriver
            try:
                from scraper.purdue_downloader import download_chromedriver
                chromedriver_path = download_chromedriver()
                if chromedriver_path:
                    from selenium.webdriver.chrome.service import Service
                    service = Service(executable_path=chromedriver_path)
                    driver = webdriver.Chrome(service=service, options=options)
                    logger.info(f"✅ Chrome driver created with downloaded driver at {chromedriver_path}")
                    return driver
                else:
                    raise Exception("Failed to download ChromeDriver")
            except Exception as e2:
                logger.warning(f"ChromeDriver download failed: {e2}")
                
                # For manual login mode, don't use fallback that might be incompatible
                if manual_login:
                    logger.error("Manual login mode requires working Chrome setup")
                    raise Exception("Cannot initialize Chrome for manual login mode")
                # Fallback to existing setup_webdriver function for non-manual mode
                return setup_webdriver(download_dir)


def check_login_required_fixed(driver):
    """
    Fixed version of check_login_required that doesn't use invalid CSS selectors.
    """
    try:
        # Look for common login indicators with valid CSS selectors
        login_elements = driver.find_elements(By.CSS_SELECTOR, "input[type='password'], form[action*='login']")
        
        # Also check for login links using XPath
        try:
            login_links = driver.find_elements(By.XPATH, "//a[contains(text(), 'login') or contains(text(), 'Login')]")
            if login_links:
                login_elements.extend(login_links)
        except:
            pass
        
        if login_elements:
            logger.info("🔍 Found login indicators on page")
            return True
        
        # Check if the Edit Event button is missing when it should be there
        edit_buttons = driver.find_elements(By.CSS_SELECTOR, "#user-destinations ul li:nth-child(3) a")
        
        # If we're on an event page and the edit button is not found, login is likely required
        event_indicators = driver.find_elements(By.CSS_SELECTOR, "div.event-detail")
        
        if event_indicators and not edit_buttons:
            logger.info("🔍 Edit Event button missing - login likely required")
            return True
        
        # Check for specific Purdue library authentication indicators
        if "docs.lib.purdue.edu" in driver.current_url:
            # Look for missing user menu which indicates not logged in
            user_menu = driver.find_elements(By.CSS_SELECTOR, "#user-destinations, .user-menu")
            if not user_menu:
                logger.info("🔍 User menu missing - login likely required")
                return True
            
        return False
    except Exception as e:
        logger.warning(f"Error checking login requirements: {e}")
        return False


@retry_with_backoff(retries=2, backoff_factor=2.0)
def handle_login_fixed(driver, username, password, manual_login=False):
    """
    Fixed version of handle_login that doesn't use invalid CSS selectors.
    If manual_login=True, pauses to allow manual credential entry.
    """
    try:
        logger.info("🔐 Starting login process...")
        logger.info(f"Current URL: {driver.current_url}")
        
        # If we're not on a login page and no login form is visible, navigate to login
        if "login.cgi" not in driver.current_url:
            username_inputs = driver.find_elements(By.CSS_SELECTOR, 
                "input[name='username'], input[id='username'], input[name='user'], input[id='user'], input[name='auth_email'], input[id='auth_email']")
            if not username_inputs:
                logger.info("No login form found, navigating to Purdue login page...")
                login_url = "https://docs.lib.purdue.edu/cgi/login.cgi?return_to=https%3A%2F%2Fdocs.lib.purdue.edu%2Fcgi%2Fmyaccount.cgi%3Fcontext%3D&context=https://docs.lib.purdue.edu"
                driver.get(login_url)
                wait_for_page_load(driver)
        
        # Check if we're already on the login page with a form
        # Look for both email and username field patterns
        login_inputs = driver.find_elements(By.CSS_SELECTOR, 
            "input[name='username'], input[id='username'], input[name='user'], input[id='user'], input[name='email'], input[type='email'], input[name='auth_email'], input[id='auth_email']")
        
        if not login_inputs:
            logger.info("No login fields found, checking if we need to navigate to login form...")
            
            # Don't click any links - we should already be on the login page
            # The direct URL navigation should have taken us there
            logger.info("Direct navigation to login URL should have worked - checking page content")
            
            # Wait a moment for page to fully load
            time.sleep(2)
            
            # Check again for login fields after waiting
            login_inputs = driver.find_elements(By.CSS_SELECTOR, 
                "input[name='username'], input[id='username'], input[name='user'], input[id='user'], input[name='email'], input[type='email'], input[name='auth_email'], input[id='auth_email']")
            
            if not login_inputs:
                logger.warning("Still no login fields found after direct navigation")
                logger.info(f"Current page title: {driver.title}")
                logger.info(f"Current URL: {driver.current_url}")
            else:
                logger.info("Login fields found after waiting")
        else:
            logger.info("Login form already visible on current page")
        
        # Manual login option - pause for user to enter credentials
        if manual_login:
            print("\n" + "="*60)
            print("🔐 MANUAL LOGIN MODE")
            print("="*60)
            print(f"Browser is currently on: {driver.current_url}")
            
            # Check if we ended up on reset password page
            if "reset" in driver.current_url.lower() or "forgot" in driver.current_url.lower():
                print("⚠️  NOTICE: Browser navigated to password reset page.")
                print("Please navigate back to the main login page if needed.")
                print("You can manually navigate to: https://docs.lib.purdue.edu/cgi/login.cgi")
            
            print("Please manually enter your Purdue credentials in the browser window.")
            print("Navigate to the correct login page if necessary.")
            print("Press ENTER here when you have completed login and are ready to continue...")
            print("="*60)
            
            # Handle input more robustly for different environments
            try:
                input()  # Wait for user to press enter
            except EOFError:
                # If no stdin available, wait for a period and check login status
                logger.info("No stdin available, waiting 30 seconds for manual login...")
                time.sleep(30)
                
                # Check if login was successful by looking for user menu
                if check_login_required(driver):
                    logger.warning("Login may not be complete. Waiting additional 30 seconds...")
                    time.sleep(30)
            except KeyboardInterrupt:
                logger.info("User interrupted manual login process")
                return False
            
            # Verify login was successful
            time.sleep(2)  # Give page time to redirect
            current_url = driver.current_url.lower()
            if "login" in current_url or "reset" in current_url or "forgot" in current_url:
                logger.warning(f"Still on login/reset page: {driver.current_url}")
                print("⚠️  It appears you may still be on a login or reset page.")
                print("Would you like to continue anyway? (y/n): ")
                
                # Handle input more robustly for different environments
                try:
                    response = input().lower().strip()
                    if response.startswith('y'):
                        logger.info("User chose to continue despite being on login page")
                        return True
                    else:
                        logger.info("User chose not to continue from login page")
                        return False
                except EOFError:
                    # If no stdin available, assume user wants to continue
                    logger.info("No stdin available, assuming user wants to continue")
                    return True
                except KeyboardInterrupt:
                    logger.info("User interrupted login process")
                    return False
            else:
                logger.info("✅ Manual login appears successful - continuing with scraping")
                return True
        
        # Try different login form patterns
        logger.info("Looking for username field...")
        
        # First, let's debug what's on the page
        try:
            logger.info("Debugging page content...")
            inputs = driver.find_elements(By.TAG_NAME, "input")
            logger.info(f"Found {len(inputs)} input elements on page")
            for i, inp in enumerate(inputs[:10]):  # Show first 10 inputs
                try:
                    name = inp.get_attribute("name") or "no-name"
                    id_attr = inp.get_attribute("id") or "no-id"
                    type_attr = inp.get_attribute("type") or "no-type"
                    logger.info(f"Input {i}: name='{name}', id='{id_attr}', type='{type_attr}'")
                except:
                    pass
        except:
            pass
        
        # Try broader selectors including email fields for Purdue login
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 
                "input[name='username'], input[id='username'], input[name='user'], input[id='user'], input[name='email'], input[type='email'], input[name='login_name'], input[id='login_name'], input[name='auth_email'], input[id='auth_email']"))
        )
        logger.info("Found username field, entering credentials...")
        username_field.clear()
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.CSS_SELECTOR, 
            "input[name='password'], input[id='password'], input[type='password'], input[name='auth_password'], input[id='auth_password']")
        password_field.clear()
        password_field.send_keys(password)
        
        # Find and click login button using valid selectors
        login_button = None
        
        # Try common submit button patterns
        button_selectors = [
            "input[type='submit']",
            "button[type='submit']",
            "input[value*='Login']",
            "input[value*='login']",
            "button[name='submit']"
        ]
        
        for selector in button_selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                break
            except:
                continue
        
        # Try XPath for login buttons
        if not login_button:
            try:
                login_buttons = driver.find_elements(By.XPATH, 
                    "//button[contains(text(), 'Login') or contains(text(), 'login')] | //input[@type='submit']")
                if login_buttons:
                    login_button = login_buttons[0]
            except:
                pass
        
        if not login_button:
            logger.error("Could not find login button")
            return False
        
        logger.info("Clicking login button...")
        login_button.click()
        
        # Wait for login to complete
        try:
            WebDriverWait(driver, 15).until_not(
                EC.presence_of_element_located((By.CSS_SELECTOR, "form[action*='login']"))
            )
        except:
            # Alternative: wait for URL change or specific element indicating successful login
            pass
        
        # Check if login was successful by looking for user indicators
        time.sleep(2)  # Give page time to load
        
        # Check if we're still on a login page
        if "login" in driver.current_url.lower():
            logger.error("Still on login page after attempting login")
            return False
        
        # Check for user menu or other indicators of successful login
        user_indicators = driver.find_elements(By.CSS_SELECTOR, 
            "#user-destinations, .user-menu, .logout, a[href*='logout']")
        
        if user_indicators:
            logger.info("✅ Login successful - found user menu")
            return True
        
        logger.warning("Login status unclear - proceeding optimistically")
        return True
        
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False


def generate_flexible_filename(pdf_url: str, document_url: str, index: int = 1) -> str:
    """
    Generate dynamic filename from document URL hierarchy: manuscriptNumber_series_pathComponents.pdf
    
    Args:
        pdf_url: The PDF download URL (e.g., viewcontent.cgi?article=1026&context=chempubs)
        document_url: The document page URL (e.g., https://docs.lib.purdue.edu/roadschool/2025/presentations/22/)
        index: Fallback index if manuscript number cannot be extracted
    
    Returns:
        Filename string with .pdf extension
    
    Examples:
        - /roadschool/2025/presentations/22/ → 1026_roadschool_2025_presentations.pdf
        - /roadschool/1924/proceedings/1/ → 1027_roadschool_1924_proceedings.pdf
        - /roadschool/2011/pres/26/ → 1028_roadschool_2011_pres.pdf
    """
    try:
        # Extract manuscript number from PDF URL
        article_number = None
        if "article=" in pdf_url:
            query_params = parse_qs(urlparse(pdf_url).query)
            if 'article' in query_params:
                article_number = query_params['article'][0]
        
        if not article_number:
            # Fallback to regex extraction
            article_match = re.search(r'article=(\d+)', pdf_url)
            if article_match:
                article_number = article_match.group(1)
        
        if not article_number:
            # Final fallback to index
            article_number = str(index).zfill(4)
        
        # Extract series and path components from document URL (not base URL)
        parsed_doc = urlparse(document_url)
        path_parts = [part for part in parsed_doc.path.strip('/').split('/') if part]
        
        # Remove docs.lib.purdue.edu prefix if present
        if 'docs.lib.purdue.edu' in path_parts:
            docs_index = path_parts.index('docs.lib.purdue.edu')
            path_parts = path_parts[docs_index + 1:]
        
        if not path_parts:
            # Fallback to extracting from context parameter
            if "context=" in pdf_url:
                context_params = parse_qs(urlparse(pdf_url).query)
                if 'context' in context_params:
                    series = context_params['context'][0]
                    filename_parts = [article_number.zfill(4), series]
                else:
                    filename_parts = [article_number.zfill(4), "unknown"]
            else:
                filename_parts = [article_number.zfill(4), "unknown"]
        else:
            # Use path components from document URL
            series = path_parts[0]
            filename_parts = [article_number.zfill(4), series]
            
            # Add remaining path components (excluding the final document number)
            if len(path_parts) > 1:
                for component in path_parts[1:-1]:  # Exclude the last part (document number)
                    # Clean component: lowercase, remove special chars
                    cleaned = re.sub(r'[^\w]', '', component.lower())
                    if cleaned and (not cleaned.isdigit() or len(cleaned) == 4):  # Allow 4-digit years
                        filename_parts.append(cleaned)
        
        # Join all parts with underscores
        filename = "_".join(filename_parts)
        
        # Clean the filename to remove any remaining invalid characters
        filename = re.sub(r'[\\/*?:"<>|]', "_", filename)
        
        # Add .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename = f"{filename}.pdf"
        
        logger.info(f"Generated flexible filename: {filename} from document URL: {document_url}")
        return filename
        
    except Exception as e:
        logger.error(f"Error generating flexible filename: {e}")
        # Fallback to simple naming
        return f"{article_number.zfill(4) if article_number else str(index).zfill(4)}_document.pdf"


def optimize_purdue_download(base_url: str, download_dir: str, 
                           username: Optional[str] = None, 
                           password: Optional[str] = None,
                           use_optimized_strategy: bool = True,
                           manual_login: bool = False) -> Tuple[int, int]:
    """
    Optimized version of Purdue document download with enhanced strategies.
    
    Args:
        base_url: URL to process
        download_dir: Where to save downloads
        username: Optional username
        password: Optional password
        use_optimized_strategy: Whether to use optimized download strategy
        
    Returns:
        Tuple of (successful_downloads, failed_downloads)
    """
    if not use_optimized_strategy:
        # Fall back to original implementation
        from purdue_downloader import process_purdue_library_content
        result = process_purdue_library_content(
            base_url, username, password, download_dir
        )
        return (1, 0) if result else (0, 1)
    
    chrome_manager = CrossPlatformChromeManager()
    download_strategy = OptimizedDownloadStrategy()
    
    driver = None
    try:
        # Create optimized driver
        driver = chrome_manager.create_driver(download_dir, manual_login)
        
        # Navigate to the base URL
        logger.info(f"🚀 Starting optimized download for: {base_url}")
        driver.get(base_url)
        
        # Wait for page load and handle cookies
        wait_for_page_load(driver)
        handle_cookie_banner(driver)
        
        # Check if login is required and handle authentication
        logger.info(f"🔍 Checking login requirements on: {driver.current_url}")
        login_required = check_login_required_fixed(driver)
        logger.info(f"🔍 Login required check result: {login_required}")
        
        # Also check if we're redirected to login page
        if "login.cgi" in driver.current_url:
            login_required = True
            logger.info(f"Detected login page redirect: {driver.current_url}")
        
        # Force login if credentials are provided (for testing)
        if not login_required and username and password:
            logger.info("🔍 Credentials provided - attempting proactive login")
            login_required = True
        
        if login_required:
            if manual_login:
                logger.info("🔐 Manual login mode enabled")
                login_successful = handle_login_fixed(driver, username, password, manual_login=True)
            else:
                if not username or not password:
                    logger.error("Login is required but no credentials provided")
                    logger.error("Please provide --username and --password parameters or use --manual-login")
                    return 0, 1
                
                logger.info("🔐 Login required - authenticating with Purdue credentials")
                login_successful = handle_login_fixed(driver, username, password, manual_login=False)
            
            if not login_successful:
                logger.error("❌ Login failed. Please check your credentials.")
                if not manual_login:
                    logger.error("Make sure you're using your Purdue username and password")
                return 0, 1
            
            logger.info("✅ Login successful")
            # Reload the base URL after login
            driver.get(base_url)
            wait_for_page_load(driver)
        
        # Extract individual document page URLs from the collection page
        document_links = download_strategy.extract_document_pages_from_collection(driver, base_url)
        
        if not document_links:
            logger.warning("No document page links found on the page")
            return 0, 1
        
        # Get cookies for authenticated downloads
        cookies = {cookie['name']: cookie['value'] for cookie in driver.get_cookies()}
        
        successful = 0
        failed = 0
        
        for i, doc_info in enumerate(document_links):
            document_url = doc_info['url']
            logger.info(f"Processing document {i+1}/{len(document_links)}: {document_url}")
            
            # Use Edit Event → View Revisions workflow to get manuscript PDF URL
            manuscript_pdf_url = download_strategy.process_document_page_for_manuscript(driver, document_url, username, password)
            
            if not manuscript_pdf_url:
                logger.warning(f"Could not extract manuscript PDF URL from {document_url}")
                failed += 1
                continue
            
            # Generate proper filename using manuscript number and document URL
            filename = generate_flexible_filename(manuscript_pdf_url, document_url, i + 1)
            output_path = Path(download_dir) / filename
            
            logger.info(f"Downloading manuscript PDF {i+1}/{len(document_links)}: {manuscript_pdf_url}")
            logger.info(f"Saving as: {filename}")
            
            if download_strategy.download_with_fallback(
                manuscript_pdf_url, output_path, driver, cookies, base_url
            ):
                successful += 1
            else:
                failed += 1
        
        # Log statistics
        stats = download_strategy.get_stats()
        logger.info(f"📊 Download Statistics: {stats}")
        
        return successful, failed
        
    except Exception as e:
        logger.error(f"Optimized download failed: {e}")
        return 0, 1
    finally:
        if driver:
            try:
                driver.quit()
            except:
                pass


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    test_url = "https://docs.lib.purdue.edu/modvis/2024/va"
    test_download_dir = "/tmp/test_downloads"
    
    os.makedirs(test_download_dir, exist_ok=True)
    
    success, failed = optimize_purdue_download(test_url, test_download_dir)
    print(f"Results: {success} successful, {failed} failed")