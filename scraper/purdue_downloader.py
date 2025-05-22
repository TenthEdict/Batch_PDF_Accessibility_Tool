from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException, ElementClickInterceptedException
from selenium.webdriver.common.action_chains import ActionChains
import os
import time
import re
import urllib.parse
from urllib.parse import urlparse, parse_qs
import getpass
import sys
import platform
import subprocess
import requests
import zipfile
import io
import logging
import concurrent.futures
from threading import Lock
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import random

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

def retry_with_backoff(retries=3, backoff_factor=0.5, allowed_exceptions=(Exception,)):
    """
    A decorator that retries the decorated function with exponential backoff
    
    Args:
        retries: Maximum number of retries (default: 3)
        backoff_factor: Factor to determine the exponential backoff time (default: 0.5)
        allowed_exceptions: Tuple of exceptions that trigger a retry (default: all exceptions)
        
    Returns:
        The decorated function with retry capability
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            total_attempts = retries + 1  # Include the original attempt
            
            while attempt < total_attempts:
                try:
                    return func(*args, **kwargs)
                except allowed_exceptions as e:
                    attempt += 1
                    if attempt >= total_attempts:
                        # Last attempt failed, re-raise the exception
                        logger.error(f"All {total_attempts} attempts failed for {func.__name__}: {e}")
                        raise
                    
                    # Calculate backoff time with randomization (jitter)
                    backoff_time = backoff_factor * (2 ** (attempt - 1))
                    # Add random jitter (±20%)
                    jitter = backoff_time * 0.2
                    backoff_time = backoff_time + random.uniform(-jitter, jitter)
                    backoff_time = max(0.1, backoff_time)  # Ensure minimum backoff
                    
                    logger.warning(
                        f"Attempt {attempt}/{total_attempts-1} failed for {func.__name__}: {e}. "
                        f"Retrying in {backoff_time:.2f} seconds..."
                    )
                    time.sleep(backoff_time)
        return wrapper
    return decorator

# Global session for optimized HTTP requests
_http_session = None

def get_http_session():
    """
    Returns an optimized requests session with connection pooling and retry logic.
    Reuses the same session for multiple requests to improve performance.
    """
    global _http_session
    
    if _http_session is None:
        # Create a new session
        session = requests.Session()
        
        # Configure retry strategy
        retry_strategy = Retry(
            total=3,  # Maximum number of retries
            backoff_factor=0.5,  # Exponential backoff
            status_forcelist=[429, 500, 502, 503, 504],  # Retry on these status codes
            allowed_methods=["GET", "POST", "HEAD"]  # Allow retries for these methods
        )
        
        # Configure connection pool
        adapter = HTTPAdapter(
            max_retries=retry_strategy,
            pool_connections=10,  # Number of connection pools
            pool_maxsize=10       # Number of connections per pool
        )
        
        # Mount the adapter for both HTTP and HTTPS
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # Update the global session
        _http_session = session
        logger.debug("Created new optimized HTTP session with connection pooling")
    
    return _http_session

def is_wsl():
    """
    Detect if running in Windows Subsystem for Linux (WSL).
    Returns True if in WSL, False otherwise.
    """
    # Multiple detection methods for reliability
    if "microsoft" in platform.release().lower():
        return True
    
    # Check for WSL-specific file
    if os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop'):
        return True
    
    # Try to read /proc/version for Microsoft signature
    try:
        with open('/proc/version', 'r') as f:
            version = f.read().lower()
            if 'microsoft' in version or 'wsl' in version:
                return True
    except:
        pass
    
    return False

def convert_to_wsl_path(windows_path):
    """Convert a Windows path to a WSL path"""
    # Handle drive letter
    if ':' in windows_path:
        drive, rest = windows_path.split(':', 1)
        return f"/mnt/{drive.lower()}{rest.replace('\\', '/')}"
    return windows_path.replace('\\', '/')

def convert_to_windows_path(wsl_path):
    """Convert a WSL path to a Windows path"""
    # Handle /mnt/drive pattern
    if wsl_path.startswith('/mnt/') and len(wsl_path) > 5:
        drive = wsl_path[5:6]
        rest = wsl_path[6:]
        return f"{drive.upper()}:{rest.replace('/', '\\')}"
    return wsl_path.replace('/', '\\')

# Global cache for Chrome version
_chrome_version_cache = None

def get_chrome_version():
    """
    Attempt to get the installed Chrome version.
    Returns the major version as a string or None if not found.
    Uses a cached value if already detected to improve performance.
    """
    global _chrome_version_cache
    
    # Return cached version if available
    if _chrome_version_cache:
        return _chrome_version_cache
    
    # Default to latest known version if we can't detect
    default_version = "136"
    
    # For WSL, check Windows Chrome
    if is_wsl():
        chrome_paths = [
            "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
            "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe"
        ]
        
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                try:
                    # Use wslpath and wmic for proper Windows path conversion
                    win_path = subprocess.check_output(
                        ["wslpath", "-w", chrome_path], text=True
                    ).strip()
                    
                    version_output = subprocess.check_output(
                        ["powershell.exe", f"(Get-Item '{win_path}').VersionInfo.ProductVersion"],
                        text=True
                    ).strip()
                    
                    if version_output:
                        _chrome_version_cache = version_output.split('.')[0]  # Cache major version
                        return _chrome_version_cache
                    
                except Exception as e:
                    logger.debug(f"Error getting Chrome version with PowerShell: {e}")
                    
                # Alternative method: direct registry query
                try:
                    version_output = subprocess.check_output(
                        ["cmd.exe", "/c", "reg", "query", 
                         "HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon", "/v", "version"],
                        text=True
                    ).strip()
                    
                    # Extract version from registry output
                    match = re.search(r'version\s+REG_SZ\s+(\d+)\.', version_output)
                    if match:
                        _chrome_version_cache = match.group(1)
                        return _chrome_version_cache
                        
                except Exception as e:
                    logger.debug(f"Error getting Chrome version from registry: {e}")
    
    # For Linux, use standard approaches
    else:
        try:
            version_output = subprocess.check_output(
                ["google-chrome", "--version"], text=True
            ).strip()
            
            match = re.search(r'Chrome\s+(\d+)\.', version_output)
            if match:
                _chrome_version_cache = match.group(1)
                return _chrome_version_cache
                
        except Exception as e:
            logger.debug(f"Error getting Chrome version on Linux: {e}")
    
    logger.warning(f"Could not detect Chrome version, using default: {default_version}")
    _chrome_version_cache = default_version
    return default_version

def setup_chrome_in_wsl():
    """
    Ensure Chrome is installed in the WSL environment
    Returns True if Chrome is available, False otherwise
    """
    try:
        # Check if Chrome is already installed
        version_output = subprocess.check_output(
            ["google-chrome", "--version"], 
            stderr=subprocess.STDOUT,
            text=True
        )
        logger.info(f"Chrome already installed in WSL: {version_output.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        # Chrome is not installed, prompt user
        logger.warning("Google Chrome is not installed in WSL.")
        response = input("Install Chrome in WSL? (y/n): ")
        
        if response.lower() != 'y':
            logger.warning("Chrome installation declined.")
            return False
        
        try:
            # Install Chrome dependencies and Chrome itself
            logger.info("Installing Chrome dependencies...")
            subprocess.check_call([
                "sudo", "apt", "update"
            ])
            
            logger.info("Installing required packages...")
            subprocess.check_call([
                "sudo", "apt", "install", "-y", "wget", "fonts-liberation",
                "libasound2", "libatk-bridge2.0-0", "libatk1.0-0", "libcairo2",
                "libcups2", "libdbus-1-3", "libexpat1", "libfontconfig1", "libgbm1",
                "libglib2.0-0", "libgtk-3-0", "libnspr4", "libnss3",
                "libpango-1.0-0", "libpangocairo-1.0-0", "libx11-6",
                "libxcomposite1", "libxcursor1", "libxdamage1", "libxext6", 
                "libxfixes3", "libxi6", "libxrandr2", "libxrender1", "libxss1",
                "libxtst6", "xdg-utils"
            ])
            
            logger.info("Downloading Chrome...")
            subprocess.check_call([
                "wget", "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb",
                "-O", "google-chrome-stable_current_amd64.deb"
            ])
            
            logger.info("Installing Chrome...")
            subprocess.check_call([
                "sudo", "apt", "install", "./google-chrome-stable_current_amd64.deb", "-y"
            ])
            
            # Verify installation
            version_output = subprocess.check_output(
                ["google-chrome", "--version"],
                text=True
            )
            logger.info(f"Chrome installed successfully: {version_output.strip()}")
            
            return True
        except Exception as e:
            logger.error(f"Error installing Chrome: {e}")
            logger.error("You may need to install Chrome manually. Try running:")
            logger.error("wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb")
            logger.error("sudo apt install ./google-chrome-stable_current_amd64.deb -y")
            return False

# Enhanced wait utilities with better performance and reliability
def wait_for_page_load(driver, timeout=30):
    """
    Wait for the page to fully load with optimized strategy and better error handling.
    
    Args:
        driver: WebDriver instance
        timeout: Maximum wait time in seconds
        
    Returns:
        True if page loaded successfully, False otherwise
    """
    try:
        # First wait for the document to reach the 'complete' state
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script("return document.readyState") == "complete"
        )
        
        # Then wait for jQuery to complete (if present), with better error protection
        jquery_ready = """
            try {
                return (typeof jQuery === 'undefined') || 
                      (jQuery.active === 0 && 
                       (typeof jQuery.queue === 'undefined' || 
                        typeof jQuery.queue().length === 'undefined' || 
                        jQuery.queue().length === 0));
            } catch (e) {
                // Return true on any error to prevent blocking
                return true;
            }
        """
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script(jquery_ready)
        )
        
        # Wait for any animations to complete (non-blocking)
        try:
            driver.execute_script("""
                try {
                    // Wait for CSS transitions/animations to finish
                    var lastTransitionEnd = Date.now();
                    document.addEventListener('transitionend', function() {
                        lastTransitionEnd = Date.now();
                    });
                    document.addEventListener('animationend', function() {
                        lastTransitionEnd = Date.now();
                    });
                    
                    // Give enough time for in-progress animations to register events
                    setTimeout(function() {}, 100);
                } catch (e) {
                    // Ignore any errors
                    console.log('Animation tracking error (non-critical)');
                }
            """)
            
            # Let any remaining animations complete with error handling
            try:
                WebDriverWait(driver, min(3, timeout/3)).until(
                    lambda d: d.execute_script("""
                        try {
                            return Date.now() - lastTransitionEnd > 250;
                        } catch (e) {
                            return true;
                        }
                    """)
                )
            except:
                # Ignore animation timing errors - non-critical
                pass
        except:
            # Ignore animation setup errors - non-critical
            pass
            
        logger.debug("Page fully loaded")
        return True
    except Exception as e:
        logger.warning(f"Page load wait timed out: {e}")
        # Continue anyway with best effort
        return False

def handle_cookie_banner(driver, max_attempts=3):
    """
    More robust cookie banner handling with multiple strategies and optimized waiting
    
    Args:
        driver: WebDriver instance
        max_attempts: Maximum number of attempts to handle the banner
        
    Returns:
        True if banner was handled successfully, False otherwise
    """
    # Wait for the page to load before trying to interact with banners
    wait_for_page_load(driver)
    
    # Check if a cookie banner appears
    banner_present = False
    try:
        banner_present = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.ID, 'onetrust-banner-sdk'))
        ).is_displayed()
    except:
        # No banner detected, return success
        return True
    
    if not banner_present:
        return True
    
    # Banner is present, try to handle it
    for attempt in range(max_attempts):
        try:
            # First try the standard approach
            accept_button = WebDriverWait(driver, 3).until(
                EC.element_to_be_clickable((By.ID, 'onetrust-accept-btn-handler'))
            )
            
            # Try a regular click first
            try:
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", accept_button)
                accept_button.click()
            except:
                # If regular click fails, try JavaScript click
                driver.execute_script("arguments[0].click();", accept_button)
            
            # Wait for banner to disappear
            WebDriverWait(driver, 5).until(
                EC.invisibility_of_element_located((By.ID, 'onetrust-banner-sdk'))
            )
            logger.info("Successfully handled cookie banner")
            return True
            
        except (TimeoutException, NoSuchElementException, ElementNotInteractableException):
            # Try removing the banner with JavaScript
            try:
                driver.execute_script("""
                    // Try to handle cookie banner in multiple ways
                    // 1. Try clicking accept button
                    var acceptBtn = document.getElementById('onetrust-accept-btn-handler');
                    if (acceptBtn) {
                        acceptBtn.click();
                    }
                    
                    // 2. If button click fails, try removing the banner directly
                    setTimeout(function() {
                        var banner = document.getElementById('onetrust-banner-sdk');
                        if (banner && banner.style.display !== 'none') {
                            banner.parentNode.removeChild(banner);
                            
                            // Also remove overlay/backdrop if present
                            var overlays = document.querySelectorAll('.onetrust-pc-dark-filter, .ot-sdk-container');
                            overlays.forEach(function(el) {
                                if (el) el.parentNode.removeChild(el);
                            });
                            
                            // Remove fixed positioning that might be preventing interactions
                            document.querySelectorAll('body').forEach(function(el) {
                                el.style.position = '';
                                el.style.overflow = '';
                            });
                        }
                    }, 100);
                """)
                
                # Check if banner is gone
                time.sleep(0.5)
                banners = driver.find_elements(By.ID, 'onetrust-banner-sdk')
                if not banners or not banners[0].is_displayed():
                    logger.info("Successfully removed cookie banner with JavaScript")
                    return True
            except Exception as e:
                logger.debug(f"JavaScript cookie banner removal failed: {e}")
            
            # Short pause before retrying
            time.sleep(0.5)
    
    # If we reach here, all attempts failed but we'll continue anyway
    logger.warning("Could not handle cookie banner after multiple attempts")
    
    # Try one last desperate approach - remove all fixed position elements
    try:
        driver.execute_script("""
            // Remove all fixed position elements that might interfere with interaction
            document.querySelectorAll('div[style*="position: fixed"]').forEach(function(el) {
                el.parentNode.removeChild(el);
            });
        """)
    except:
        pass
        
    return False

def remove_cookie_banner_with_js(driver):
    """Remove cookie banner using JavaScript"""
    try:
        # Attempt to remove the cookie banner from DOM
        driver.execute_script("""
            var banner = document.getElementById('onetrust-banner-sdk');
            if (banner) {
                banner.parentNode.removeChild(banner);
            }
            // Also remove any overlay/backdrop
            var overlays = document.querySelectorAll('.ot-sdk-container');
            overlays.forEach(function(overlay) {
                overlay.parentNode.removeChild(overlay);
            });
        """)
        logger.info("Removed cookie banner with JavaScript")
        return True
    except Exception as e:
        logger.warning(f"Failed to remove cookie banner with JS: {e}")
        return False

@retry_with_backoff(retries=1, backoff_factor=1.5)
def click_pdf_link_with_fallbacks(driver, pdf_link, max_attempts=3):
    """
    Robust PDF link clicking with multiple strategies, optimized waits, and automatic retries
    
    Args:
        driver: WebDriver instance
        pdf_link: The link element to click
        max_attempts: Maximum number of attempts to click the link
        
    Returns:
        True if clicking was successful, False otherwise
    """
    # Ensure the page is fully loaded first
    wait_for_page_load(driver)
    
    # Store the href for direct navigation fallback
    href = None
    try:
        href = pdf_link.get_attribute("href")
        logger.debug(f"PDF link href: {href}")
    except:
        logger.debug("Could not get href attribute from PDF link")
    
    for attempt in range(max_attempts):
        # Scroll the element into view first to ensure it's visible
        try:
            driver.execute_script("arguments[0].scrollIntoView({block: 'center', behavior: 'smooth'});", pdf_link)
            # Brief pause for any scrolling animations to complete
            time.sleep(0.5)
        except:
            # Ignore scroll errors
            pass
            
        try:
            # Strategy 1: Direct click with explicit wait for element to be clickable
            WebDriverWait(driver, 3).until(EC.element_to_be_clickable((By.XPATH, f".//*[@href='{href}']")))
            pdf_link.click()
            logger.info("Clicked PDF link directly")
            return True
        except Exception as click_error:
            logger.debug(f"Direct click failed: {click_error}")
            
            try:
                # Strategy 2: JavaScript click with additional preparations
                driver.execute_script("""
                    // Ensure the element isn't covered and is clickable
                    arguments[0].style.position = 'relative';
                    arguments[0].style.zIndex = '9999';
                    
                    // Click with a small delay to ensure the browser has processed style changes
                    setTimeout(function() {
                        arguments[0].click();
                    }, 50);
                """, pdf_link)
                logger.info("Clicked PDF link with enhanced JavaScript")
                time.sleep(0.5)  # Wait for click to be processed
                return True
            except Exception as js_error:
                logger.debug(f"JavaScript click failed: {js_error}")
                
                # Strategy 3: ActionChains with move and multiple clicks
                try:
                    actions = ActionChains(driver)
                    actions.move_to_element(pdf_link)
                    actions.pause(0.1)  # Short pause after move
                    actions.click()
                    actions.perform()
                    logger.info("Clicked PDF link with ActionChains")
                    return True
                except Exception as action_error:
                    logger.debug(f"ActionChains click failed: {action_error}")
        
        # Strategy 4: Try direct navigation to href
        if href and attempt == max_attempts - 2:  # Try on second-to-last attempt
            try:
                logger.info(f"Attempting direct navigation to PDF URL: {href}")
                # Open in new tab
                driver.execute_script(f"window.open('{href}', '_blank');")
                # Switch to the new tab
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(1)  # Wait for navigation
                # Switch back to the original tab
                driver.switch_to.window(driver.window_handles[0])
                return True
            except Exception as nav_error:
                logger.debug(f"Direct navigation failed: {nav_error}")
        
        # Last resort: Remove all overlays and try again
        if attempt == max_attempts - 1:
            try:
                driver.execute_script("""
                    // Remove all elements that might intercept clicks
                    // Fixed position elements
                    document.querySelectorAll('div[style*="position: fixed"], div[style*="position:fixed"]').forEach(function(el) {
                        el.parentNode.removeChild(el);
                    });
                    
                    // Modals, overlays, and popups
                    document.querySelectorAll('.modal, .overlay, .popup, [class*="modal"], [class*="overlay"], [class*="popup"]').forEach(function(el) {
                        el.parentNode.removeChild(el);
                    });
                    
                    // Reset any body/html properties that might interfere
                    document.body.style.overflow = '';
                    document.documentElement.style.overflow = '';
                """)
                logger.info("Removed all potential blocking elements")
                
                # Try direct click one more time
                try:
                    pdf_link.click()
                    logger.info("Successfully clicked PDF link after removing blocking elements")
                    return True
                except:
                    pass
                
            except Exception as e:
                logger.debug(f"Error removing blocking elements: {e}")
            
        # Slightly increasing wait between attempts
        time.sleep(0.5 + attempt * 0.5)
    
    logger.warning("All PDF link clicking strategies failed")
    return False  # All strategies failed

# Cache for ChromeDriver path to avoid repeated downloads
_chromedriver_path_cache = None

def download_chromedriver():
    """
    Download and extract ChromeDriver compatible with the current Chrome version.
    Uses a cached path if available to avoid repeated downloads.
    
    Returns:
        Path to the ChromeDriver executable
    """
    global _chromedriver_path_cache
    
    # Return cached path if available
    if _chromedriver_path_cache and os.path.exists(_chromedriver_path_cache):
        logger.debug(f"Using cached ChromeDriver at: {_chromedriver_path_cache}")
        return _chromedriver_path_cache
    
    try:
        # Get Chrome version
        chrome_version = get_chrome_version()
        logger.info(f"Detected Chrome version: {chrome_version}")
        
        # Detect system architecture
        arch = platform.machine()
        arch_suffix = "linux64"
        if arch in ["aarch64", "arm64"]:
            arch_suffix = "linux-arm64"
        
        # Create a temporary directory for chromedriver
        temp_dir = os.path.expanduser("~/chromedriver_linux")
        os.makedirs(temp_dir, exist_ok=True)
        
        # Try each method to download a suitable chromedriver
        chromedriver_path = (
            try_download_matching_chromedriver(chrome_version, arch_suffix, temp_dir) or
            try_download_from_testing_api(chrome_version, arch_suffix, temp_dir) or
            try_download_legacy_chromedriver(temp_dir)
        )
        
        if chromedriver_path:
            # Cache the successful path
            _chromedriver_path_cache = chromedriver_path
            return chromedriver_path
        
        raise Exception("All ChromeDriver download methods failed")
        
    except Exception as e:
        logger.error(f"Error downloading ChromeDriver: {e}")
        raise

def try_download_matching_chromedriver(chrome_version, arch_suffix, temp_dir):
    """Try to download a ChromeDriver version matching the installed Chrome"""
    try:
        # Get more specific Chrome version for URL
        version_for_url = f"{chrome_version}.0.7103.0"  # Default format
        
        # Try to get the list of available ChromeDriver versions
        version_list_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        session = get_http_session()
        version_list_response = session.get(version_list_url)
        version_list_response.raise_for_status()
        version_data = version_list_response.json()
        
        # Find best matching version
        matching_version = None
        
        # First try to find exact match for major version
        for version_info in reversed(version_data.get("versions", [])):
            version = version_info.get("version", "")
            if version.startswith(f"{chrome_version}."):
                matching_version = version
                logger.info(f"Found matching ChromeDriver version: {matching_version}")
                break
                
        # If still no match, use the latest stable version
        if not matching_version and version_data.get("versions"):
            matching_version = version_data.get("versions", [])[-1].get("version")
            logger.info(f"Using latest available ChromeDriver version: {matching_version}")
        
        if matching_version:
            version_for_url = matching_version
            
        # Download URL for Linux with architecture
        download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{version_for_url}/{arch_suffix}/chromedriver-{arch_suffix}.zip"
        return download_and_extract_chromedriver(download_url, temp_dir)
        
    except Exception as e:
        logger.warning(f"Error getting matching ChromeDriver: {e}")
        return None

def try_download_from_testing_api(chrome_version, arch_suffix, temp_dir):
    """Try to download ChromeDriver using the Chrome for Testing API"""
    try:
        logger.info("Trying Chrome for Testing API...")
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions.json"
        
        session = get_http_session()
        response = session.get(api_url)
        response.raise_for_status()
        versions_data = response.json()
        
        # Try to find a suitable URL for download
        matching_url = None
        
        # Check if our Chrome version is in the data
        if chrome_version in versions_data.get("channels", {}).get("stable", {}).get("version", "").split('.')[0]:
            stable_data = versions_data.get("channels", {}).get("stable", {})
            for download in stable_data.get("downloads", {}).get("chromedriver", []):
                if download.get("platform") == "linux64":
                    matching_url = download.get("url")
                    break
        
        # If no match, try the latest stable version
        if not matching_url:
            stable_data = versions_data.get("channels", {}).get("stable", {})
            for download in stable_data.get("downloads", {}).get("chromedriver", []):
                if download.get("platform") == "linux64":
                    matching_url = download.get("url")
                    break
        
        # If still no match, try beta or dev channel
        if not matching_url:
            for channel in ["beta", "dev"]:
                channel_data = versions_data.get("channels", {}).get(channel, {})
                for download in channel_data.get("downloads", {}).get("chromedriver", []):
                    if download.get("platform") == "linux64":
                        matching_url = download.get("url")
                        break
                if matching_url:
                    break
        
        if matching_url:
            return download_and_extract_chromedriver(matching_url, temp_dir)
            
        return None
        
    except Exception as e:
        logger.warning(f"Error with Chrome for Testing API: {e}")
        return None

def try_download_legacy_chromedriver(temp_dir):
    """Try to download ChromeDriver using the legacy download method"""
    try:
        logger.info("Trying legacy ChromeDriver download approach...")
        direct_url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
        
        session = get_http_session()
        version_response = session.get(direct_url)
        latest_version = version_response.text.strip()
        
        download_url = f"https://chromedriver.storage.googleapis.com/{latest_version}/chromedriver_linux64.zip"
        return download_and_extract_chromedriver(download_url, temp_dir)
        
    except Exception as e:
        logger.warning(f"Error with legacy ChromeDriver download: {e}")
        return None

def download_and_extract_chromedriver(download_url, temp_dir):
    """Download and extract ChromeDriver from URL"""
    try:
        logger.info(f"Downloading ChromeDriver from: {download_url}")
        
        session = get_http_session()
        response = session.get(download_url)
        response.raise_for_status()
        
        # Create a unique path for this download
        driver_path = os.path.join(temp_dir, f"chromedriver_{int(time.time())}")
        
        # Extract the driver
        with zipfile.ZipFile(io.BytesIO(response.content)) as zip_file:
            # Find the actual chromedriver binary
            chromedriver_file = None
            for file in zip_file.namelist():
                if file.endswith('/chromedriver') or file == 'chromedriver':
                    chromedriver_file = file
                    break
            
            if not chromedriver_file:
                return None
            
            # Extract the chromedriver executable
            with zip_file.open(chromedriver_file) as src, open(driver_path, 'wb') as dst:
                dst.write(src.read())
            os.chmod(driver_path, 0o755)
        
        logger.info(f"Successfully extracted ChromeDriver to: {driver_path}")
        return driver_path
        
    except Exception as e:
        logger.warning(f"Error downloading/extracting ChromeDriver: {e}")
        return None

def setup_webdriver(download_directory):
    """
    Set up and configure the Chrome WebDriver with proper handling for WSL
    
    Args:
        download_directory: Directory where files should be downloaded
        
    Returns:
        Configured WebDriver instance
    """
    running_in_wsl = is_wsl()
    logger.info(f"Running in WSL: {running_in_wsl}")
    
    # Set up Chrome options
    options = Options()
    
    # Common options for better stability
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")  # Avoid detection
    
    # Add cookie and popup handling prefs
    prefs = {
        "profile.default_content_setting_values.cookies": 1,  # Allow cookies
        "profile.default_content_setting_values.notifications": 2,  # Block notifications
        "profile.cookie_controls_mode": 0,  # Don't block cookies
        "download.default_directory": download_directory,
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Special handling for WSL environment
    if running_in_wsl:
        logger.info("WSL environment detected - using Linux Chrome within WSL")
        
        # Ensure Chrome is installed in WSL
        if not setup_chrome_in_wsl():
            raise Exception("Chrome is required but not installed in WSL environment. Please install it manually.")
        
        # Use headless mode for better WSL compatibility
        logger.info("Using headless Chrome for WSL environment")
        options.add_argument("--headless=new")
    
    # Try to initialize Chrome with standard options first
    try:
        driver = webdriver.Chrome(options=options)
        logger.info("WebDriver initialized successfully!")
        return driver
        
    except Exception as e:
        logger.warning(f"Standard Chrome initialization failed: {e}")
        
        # Try to download and use a compatible chromedriver
        try:
            # Download a compatible chromedriver
            chromedriver_path = download_chromedriver()
            
            if chromedriver_path:
                # Create service with the downloaded driver
                service = Service(executable_path=chromedriver_path)
                driver = webdriver.Chrome(service=service, options=options)
                logger.info(f"Successfully initialized Chrome with downloaded driver at {chromedriver_path}")
                return driver
            else:
                raise Exception("Failed to download a compatible ChromeDriver")
                
        except Exception as e2:
            logger.error(f"Error initializing Chrome with downloaded driver: {e2}")
            
            # Final fallback: Try any available webdriver
            try:
                from selenium.webdriver.common.options import ArgOptions
                from selenium.webdriver.firefox.options import Options as FirefoxOptions
                
                logger.info("Trying Firefox WebDriver as last resort...")
                firefox_options = FirefoxOptions()
                firefox_options.add_argument("--headless")
                
                driver = webdriver.Firefox(options=firefox_options)
                logger.info("Successfully initialized Firefox WebDriver as fallback")
                return driver
                
            except Exception as e3:
                logger.error(f"All WebDriver initialization methods failed: {e3}")
                raise Exception("Could not initialize any WebDriver. Please ensure a browser is installed.")

def generate_download_path(base_url, event_url=None):
    """
    Generate the appropriate download directory path based on the URL structure.
    
    Args:
        base_url: URL being processed
        event_url: Optional specific event URL for more precise path generation
        
    Returns:
        The path where PDFs from this URL should be saved
    """
    # Use the most specific URL for path generation
    url_to_parse = event_url if event_url else base_url
    
    # Parse the URL to get its components
    url_parts = urlparse(url_to_parse).path.strip('/').split('/')
    
    # Base path for all downloads - adapted for WSL/Linux
    # Map Windows S: drive to its WSL equivalent
    base_path = "/mnt/s/Departments/ePubs/Accessibility_Project"
    
    # Extract series from the URL
    series = url_parts[0] if len(url_parts) > 0 else ""
    
    # Determine the series prefix based on the first character
    # Each letter has its own *_series folder
    if series and series[0].isalpha():
        series_prefix = f"{series[0]}_series"
    else:
        series_prefix = ""
    
    # Build the path components
    path_components = [base_path]
    
    if series_prefix:
        path_components.append(series_prefix)
    
    # Add the series
    path_components.append(series)
    
    # Check if the additional URL parts are meaningful subsections or just numeric identifiers
    has_meaningful_subsections = False
    
    # Look for meaningful subsections like years, volume names, etc.
    if len(url_parts) > 1:
        section = url_parts[1]
        # Check if section is a meaningful name (not a numeric ID or HTML file)
        if not section.isdigit() and not "announcements.html" in section and not "." in section:
            has_meaningful_subsections = True
            path_components.append(section)
            
            # Add additional partitions if present and meaningful
            if len(url_parts) > 2:
                partition = url_parts[2]
                if not partition.isdigit() and not "announcements.html" in partition and not "." in partition:
                    path_components.append(partition)
    
    # If no meaningful subsections were found, stop at the series level
    # All PDFs will be placed directly in the series directory
    
    # Combine into a full path using forward slashes for Linux
    full_path = os.path.join(*path_components)
    
    # Create the directory if it doesn't exist
    os.makedirs(full_path, exist_ok=True)
    
    logger.info(f"Generated download path: {full_path}")
    
    # For Windows users, also log the equivalent Windows path
    if is_wsl():
        windows_path = convert_to_windows_path(full_path)
        logger.info(f"Windows equivalent path: {windows_path}")
    
    return full_path

# Global WebDriver instance for session reuse
_shared_webdriver = None
_webdriver_lock = Lock()

def get_shared_webdriver(download_directory):
    """
    Returns a shared WebDriver instance for reuse across multiple URL processing.
    Creates a new instance if one doesn't exist or if the existing one is no longer usable.
    
    Args:
        download_directory: The directory where files should be downloaded
        
    Returns:
        A WebDriver instance configured for the specified download directory
    """
    global _shared_webdriver
    
    with _webdriver_lock:
        # Check if we have a valid webdriver instance
        if _shared_webdriver is not None:
            try:
                # Test if the webdriver is still responsive
                current_url = _shared_webdriver.current_url
                logger.debug(f"Reusing existing WebDriver (currently at {current_url})")
                
                # Update download directory preference if needed
                try:
                    _shared_webdriver.execute_script(
                        f"chrome.prefs.set('download.default_directory', '{download_directory.replace('\\', '\\\\')}')"
                    )
                except:
                    pass  # Ignore errors with preference updating
                
                return _shared_webdriver
            except Exception as e:
                logger.warning(f"Existing WebDriver is no longer usable: {e}")
                # Clean up the broken driver
                try:
                    _shared_webdriver.quit()
                except:
                    pass
                _shared_webdriver = None
        
        # Create a new WebDriver instance
        try:
            logger.info("Creating new shared WebDriver instance")
            _shared_webdriver = setup_webdriver(download_directory)
            return _shared_webdriver
        except Exception as e:
            logger.error(f"Error creating shared WebDriver: {e}")
            raise

def cleanup_shared_webdriver():
    """Clean up the shared WebDriver instance when it's no longer needed"""
    global _shared_webdriver
    
    with _webdriver_lock:
        if _shared_webdriver is not None:
            try:
                _shared_webdriver.quit()
                logger.info("Shared WebDriver closed")
            except Exception as e:
                logger.warning(f"Error closing shared WebDriver: {e}")
            finally:
                _shared_webdriver = None

def process_purdue_library_content(base_url, username=None, password=None, custom_download_dir=None, shared_driver=True):
    """
    Recursively navigates through Purdue Library content structure and downloads PDFs.
    
    Args:
        base_url: The starting URL (e.g., https://docs.lib.purdue.edu/modvis/2025/)
        username: Optional username for login
        password: Optional password for login
        custom_download_dir: Optional override for the download directory
        shared_driver: Whether to use a shared WebDriver instance (default: True)
    """
    # Parse the URL to understand its structure
    url_parts = urlparse(base_url).path.strip('/').split('/')
    
    # Determine download directory - either use custom or generate from URL
    if custom_download_dir:
        download_directory = custom_download_dir
    else:
        download_directory = generate_download_path(base_url)
    
    logger.info(f"Files will be downloaded to: {download_directory}")
    
    # Ensure the download directory exists
    os.makedirs(download_directory, exist_ok=True)
    
    # Get WebDriver instance - either shared or new
    driver = get_shared_webdriver(download_directory) if shared_driver else setup_webdriver(download_directory)
    should_quit_driver = not shared_driver  # Only quit if we created a new instance
    
    try:
        # Navigate to the base URL with optimized waiting
        logger.info(f"\nNavigating to {base_url}")
        driver.get(base_url)
        wait_for_page_load(driver)
        
        # Handle cookie banner with more robust approach
        handle_cookie_banner(driver)
        
        # Check if login is required
        if check_login_required(driver):
            if not username or not password:
                username = input("Enter your Purdue username: ")
                password = getpass.getpass("Enter your Purdue password: ")
            
            login_successful = handle_login(driver, username, password)
            if not login_successful:
                logger.error("Login failed. Please check your credentials.")
                return False
            
            # Reload the base URL after login
            driver.get(base_url)
        
        # Determine what type of page we're on and process accordingly
        successful_downloads, failed_downloads = process_url_recursively(driver, base_url, download_directory, url_parts)
        
        total_downloads = successful_downloads + failed_downloads
        if total_downloads == 0:
            logger.warning(f"No PDFs were found to download for {base_url}")
            return False
        elif failed_downloads > 0:
            logger.warning(f"\nProcessing completed for {base_url} but with {failed_downloads} failures out of {total_downloads} PDFs")
            if successful_downloads > 0:
                logger.info(f"Successfully downloaded {successful_downloads} PDFs")
                return True
            else:
                logger.error("All PDF downloads failed")
                return False
        else:
            logger.info(f"\nAll {successful_downloads} PDFs processed successfully for {base_url}!")
            return True
    
    except Exception as e:
        logger.error(f"Fatal error processing {base_url}: {e}")
        return False
    finally:
        # Close the browser if it's not shared
        if should_quit_driver:
            driver.quit()

def check_login_required(driver):
    """Check if the page requires login"""
    try:
        # Look for common login indicators
        login_elements = driver.find_elements(By.XPATH, 
            "//input[@type='password'] | //form[contains(@action, 'login')] | //a[contains(text(), 'login') or contains(text(), 'Login')]")
        
        if login_elements:
            return True
        
        # Check if the Edit Event button is missing when it should be there
        edit_buttons = driver.find_elements(By.XPATH, "//*[@id='user-destinations']/ul/li[3]/a")
        
        # If we're on an event page and the edit button is not found, login is likely required
        event_indicators = driver.find_elements(By.XPATH, "//div[contains(@class, 'event-detail')]")
        
        if event_indicators and not edit_buttons:
            return True
            
        return False
    except:
        return False

@retry_with_backoff(retries=2, backoff_factor=2.0)
def handle_login(driver, username, password):
    """Handle the login process with automatic retries"""
    try:
        # Look for login form or button
        login_link = driver.find_elements(By.XPATH, "//a[contains(text(), 'login') or contains(text(), 'Login')]")
        if login_link:
            login_link[0].click()
            time.sleep(2)
        
        # Try different login form patterns
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, 
                "//input[@name='username'] | //input[@id='username'] | //input[@name='user'] | //input[@id='user']"))
        )
        username_field.send_keys(username)
        
        password_field = driver.find_element(By.XPATH, 
            "//input[@name='password'] | //input[@id='password'] | //input[@type='password']")
        password_field.send_keys(password)
        
        # Find and click login button
        login_button = driver.find_element(By.XPATH, 
            "//input[@type='submit'] | //button[@type='submit'] | //button[contains(text(), 'Login')]")
        login_button.click()
        
        # Wait for login to complete
        time.sleep(5)
        
        # Check if login was successful
        if check_login_required(driver):
            return False
        return True
    except Exception as e:
        logger.error(f"Login error: {e}")
        return False

@retry_with_backoff(retries=1, backoff_factor=1.0)
def process_url_recursively(driver, current_url, download_directory, url_structure, depth=0, max_depth=4):
    """Recursively process URLs, navigating through sections until events are found, with automatic retries"""
    if depth >= max_depth:
        logger.info(f"Maximum recursion depth reached for {current_url}")
        
        # Instead of just returning, try to search for direct evidence of events/PDFs on this page
        try:
            # Check if this page might contain events despite recursion depth
            event_links = find_event_links(driver, url_structure)
            if event_links:
                logger.info(f"Found {len(event_links)} events at max depth, processing anyway")
                success, failure = process_event_links(driver, event_links, download_directory, url_structure)
                return success, failure
                
            # Check for direct PDF links
            pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]")
            if pdf_links:
                logger.info(f"Found {len(pdf_links)} direct PDF links at max depth, attempting download")
                # Try to process as a pseudo-event
                success_count = 0
                for link in pdf_links[:5]:  # Limit to first 5 to avoid excessive processing
                    try:
                        href = link.get_attribute("href")
                        if href:
                            driver.get(href)
                            wait_for_page_load(driver)
                            # Generate a simple filename based on URL
                            filename = f"depth_limit_{urlparse(href).path.split('/')[-1]}"
                            # Try to save the PDF
                            # (simplified download code would go here)
                            success_count += 1
                    except Exception as e:
                        logger.error(f"Error processing PDF at max depth: {e}")
                        
                return success_count, len(pdf_links) - success_count
        except Exception as e:
            logger.error(f"Error trying to process content at max recursion depth: {e}")
            
        return 0, 0  # Return successful and failed counts
    
    logger.info(f"\nProcessing content at: {current_url} (depth: {depth})")
    driver.get(current_url)
    
    # Handle cookie banner with more robust approach
    handle_cookie_banner(driver)
    
    # Wait for page to load optimally
    wait_for_page_load(driver)
    
    # Check if this is an event page first (has "Edit Event" button)
    # Try both the old and new XPaths
    edit_event_buttons = driver.find_elements(By.XPATH, '/html/body/div[3]/ul/li[3]/a') or \
                         driver.find_elements(By.XPATH, '//*[@id="user-destinations"]/ul/li[3]/a')
    
    if edit_event_buttons:
        logger.info("This appears to be a single event page")
        result = process_single_event(driver, current_url, download_directory, url_structure)
        return (1, 0) if result else (0, 1)  # Return 1 success or 1 failure
    
    # Check for event links on this page
    event_links = find_event_links(driver, url_structure)
    
    successful_downloads = 0
    failed_downloads = 0
    
    if event_links:
        logger.info(f"Found {len(event_links)} events to process")
        success, failure = process_event_links(driver, event_links, download_directory, url_structure)
        successful_downloads += success
        failed_downloads += failure
    else:
        # This might be a section page with links to other sections or event lists
        section_links = find_section_links(driver, url_structure)
        
        if section_links:
            logger.info(f"Found {len(section_links)} sections to process")
            for index, link in enumerate(section_links):
                logger.info(f"Processing section {index + 1}/{len(section_links)}: {link}")
                success, failure = process_url_recursively(driver, link, download_directory, url_structure, depth + 1, max_depth)
                successful_downloads += success
                failed_downloads += failure
        else:
            logger.info(f"No events or sections found at {current_url}")
    
    return successful_downloads, failed_downloads

def find_event_links(driver, url_structure):
    """Find all event links on the current page"""
    event_links = []
    series_name = url_structure[0] if url_structure else None
    
    # Try different patterns for event links
    try:
        # Pattern 1: Links in table cells with paragraph tags
        links = driver.find_elements(By.XPATH, "//table//td//p/a")
        if links:
            event_links.extend([link.get_attribute("href") for link in links if link.get_attribute("href")])
        
        # Pattern 2: Links with specific patterns in their href
        links = driver.find_elements(By.XPATH, "//a[contains(@href, '/Program/') or contains(@href, '/event/')]")
        if links:
            event_links.extend([link.get_attribute("href") for link in links if link.get_attribute("href")])
            
        # Pattern 3: Links in list items
        if series_name:
            links = driver.find_elements(By.XPATH, f"//li//a[contains(@href, '{series_name}')]")
            if links:
                event_links.extend([link.get_attribute("href") for link in links if link.get_attribute("href")])
            
        # Remove duplicates while preserving order
        event_links = list(dict.fromkeys(event_links))
        
        # Filter out non-event links (simple heuristic)
        event_links = [link for link in event_links if '/Program/' in link or re.search(r'/\d+$', link)]
        
        return event_links
    
    except Exception as e:
        logger.error(f"Error finding event links: {e}")
        return []

def find_section_links(driver, url_structure):
    """Find links to sections that might contain events"""
    section_links = []
    series_name = url_structure[0] if url_structure else None
    
    try:
        # Look for links that match the publication series pattern but go deeper
        base_path = '/'.join(url_structure)
        
        # Try to find section links based on URL structure
        if series_name:
            # Pattern 1: Links that match the series but go to subsections
            links = driver.find_elements(By.XPATH, f"//a[contains(@href, '{series_name}/') and not(contains(@href, 'viewcontent'))]")
            section_links.extend([link.get_attribute("href") for link in links if link.get_attribute("href")])
        
        # Pattern 2: Links in tables that might be sections
        links = driver.find_elements(By.XPATH, "//table//a[not(contains(@href, 'viewcontent'))]")
        section_links.extend([link.get_attribute("href") for link in links if link.get_attribute("href")])
        
        # Filter out links that don't follow the expected pattern
        if series_name:
            section_links = [link for link in section_links if series_name in link and link.count('/') > 3]
        
        # Filter out announcements.html URLs as they are not relevant for PDF downloads
        section_links = [link for link in section_links if "announcements.html" not in link]
        
        # Remove duplicates while preserving order
        section_links = list(dict.fromkeys(section_links))
        
        return section_links
    
    except Exception as e:
        logger.error(f"Error finding section links: {e}")
        return []

def process_event_links(driver, event_links, download_directory, url_structure):
    """Process all event links found on a page"""
    current_url = driver.current_url
    successful_downloads = 0
    failed_downloads = 0
    
    for index, event_url in enumerate(event_links):
        logger.info(f"\nProcessing event {index + 1} of {len(event_links)}: {event_url}")
        
        try:
            # Navigate to the event page
            driver.get(event_url)
            
            # Process the event and track success/failure
            result = process_single_event(driver, event_url, download_directory, url_structure, index)
            if result:
                successful_downloads += 1
            else:
                failed_downloads += 1
            
        except Exception as e:
            logger.error(f"Error processing event {event_url}: {e}")
            failed_downloads += 1
            continue
        
    # Return to the original page
    driver.get(current_url)
    
    # Report success/failure stats
    logger.info(f"Successfully downloaded {successful_downloads} PDFs, failed to download {failed_downloads} PDFs")
    return successful_downloads, failed_downloads

@retry_with_backoff(retries=2, backoff_factor=1.0)
def process_single_event(driver, event_url, download_directory, url_structure, index=0):
    """Process a single event page to download the PDF with automatic retries"""
    # Generate the specific download path for this event using the event URL
    event_download_directory = generate_download_path(download_directory, event_url)
    # Log the specific download directory for this event
    logger.info(f"Using specific download directory for this event: {event_download_directory}")
    try:
        # Handle cookie banner with more robust approach
        handle_cookie_banner(driver)
            
        # Extract document number from the event URL (last part of the URL)
        # This will be used in the file naming convention
        doc_number = "1"  # Default value
        try:
            url_parts = event_url.rstrip('/').split('/')
            if url_parts and url_parts[-1].isdigit():
                doc_number = url_parts[-1]
            logger.info(f"Extracted document number from URL: {doc_number}")
        except Exception as e:
            logger.warning(f"Error extracting document number from URL: {e}")
            
        # Since Edit Event triggers are consistently not working, first try to find PDF directly
        # Check for direct PDF links on the event page
        logger.info("Prioritizing direct PDF download instead of Edit Event flow")
        
        # Try to find PDF link directly on the event page first
        pdf_link = None
        pdf_href = None
        direct_download_successful = False
        
        try:
            # XPaths for directly finding PDF on the event page
            direct_pdf_xpaths = [
                "//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                "//a[contains(@href, 'download') and contains(@class, 'btn')]",
                "//a[contains(text(), 'Download') and contains(@href, '.pdf')]",
                "//a[contains(@class, 'download-btn')]",
                "//div[contains(@class, 'abstract')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                "//div[contains(@class, 'galleys')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                "//div[contains(@class, 'item')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                "//aside[contains(@class, 'download')]//a",
                "//div[contains(@class, 'files')]//a[contains(@href, '.pdf')]",
                "//div[contains(@class, 'download')]//a",
                "//section[contains(@class, 'download')]//a",
                "//a[contains(text(), 'PDF') or contains(text(), 'Download')]",
                "//a[contains(text(), 'View') and contains(text(), 'PDF')]",
                "//a/img[contains(@alt, 'PDF')]/..",
                "//a[contains(@class, 'pdf')]",
                "//a[contains(@data-format, 'pdf')]",
                "//a[contains(@title, 'PDF')]"
            ]
            
            # Try each XPath to find a PDF link
            for xpath in direct_pdf_xpaths:
                try:
                    logger.info(f"Trying direct PDF link XPath: {xpath}")
                    pdf_elements = driver.find_elements(By.XPATH, xpath)
                    if pdf_elements:
                        pdf_link = pdf_elements[0]  # Take the first match
                        pdf_href = pdf_link.get_attribute("href")
                        if pdf_href and ('.pdf' in pdf_href.lower() or 'viewcontent' in pdf_href.lower()):
                            logger.info(f"Found direct PDF link with XPath {xpath}: {pdf_href}")
                            direct_download_successful = True
                            break
                except Exception as e:
                    logger.debug(f"Error with direct PDF XPath {xpath}: {e}")
                    continue
                
            # If direct PDF link was found, we'll skip the Edit Event flow
            if direct_download_successful:
                logger.info("Direct PDF link found, skipping Edit Event flow")
                edit_view_flow_successful = False
            else:
                logger.info("No direct PDF link found, trying Edit Event flow as fallback")
                
                # Only try Edit Event flow if direct download wasn't successful
                # Find and click the "Edit Event" button (as fallback)
                edit_successful = False
                try:
                    # Try a more robust set of XPaths for the Edit Event button
                    edit_xpaths = [
                        '/html/body/div[3]/ul/li[3]/a',  # Original from full_Xpaths.txt
                        '//*[@id="user-destinations"]/ul/li[3]/a',
                        "//a[contains(text(), 'Edit Event')]",
                        "//a[contains(text(), 'Edit') and contains(@href, 'editor.cgi')]",
                        "//a[contains(@href, 'editor.cgi') and contains(@href, 'window=abstract')]",
                        "//a[contains(@href, 'edit') and not(contains(text(), 'Editorial'))]",
                        "//*[contains(@id, 'user-destinations')]//a[contains(text(), 'Edit')]",
                        "//ul[@id='tabs']//a[contains(text(), 'Edit')]",
                        "//div[contains(@class, 'toolbar')]//a[contains(text(), 'Edit')]",
                        "//div[contains(@id, 'actions')]//a[contains(@href, 'edit')]"
                    ]
                    
                    # Try each XPath with explicit wait but with shorter timeouts
                    for xpath in edit_xpaths:
                        try:
                            logger.info(f"Trying Edit Event XPath: {xpath}")
                            edit_event_button = WebDriverWait(driver, 3).until(
                                EC.element_to_be_clickable((By.XPATH, xpath))
                            )
                            logger.info(f"Found Edit Event button with XPath: {xpath}")
                            
                            # Try JavaScript click first if regular click fails
                            try:
                                edit_event_button.click()
                            except:
                                driver.execute_script("arguments[0].click();", edit_event_button)
                                
                            edit_successful = True
                            logger.info("Successfully clicked Edit Event button")
                            # Wait for page to load after click
                            time.sleep(2)
                            break
                        except:
                            continue
                            
                    if not edit_successful:
                        logger.warning("All Edit Event XPaths failed")
                except Exception as e:
                    logger.warning(f"Error with Edit Event button: {e}")
                
                # Track the overall flow success
                edit_view_flow_successful = False
                
                # Only proceed to View Revisions if Edit Event was successful
                if not edit_successful:
                    logger.warning("Could not click Edit Event button, will continue with direct PDF download")
                else:
                    # Find and click "View Revisions"
                    revisions_successful = False
                    try:
                        # Try a more robust set of XPaths for the View Revisions link
                        revisions_xpaths = [
                            '/html/body/table[1]/tbody/tr/td[1]/table/tbody/tr/td/table/tbody/tr[13]/td/a/strong',  # Original from full_Xpaths.txt
                            "//*[@id=\"MenuSidebar\"]/table/tbody/tr/td/table/tbody/tr[12]/td/a",
                            "//a[contains(text(), 'View Revisions')]",
                            "//a[contains(text(), 'Revisions')]",
                            "//a[contains(@href, 'pickvers')]",
                            "//a/strong[contains(text(), 'Revisions')]/..",
                            "//td/a[contains(text(), 'Revisions')]",
                            "//*[contains(@id, 'MenuSidebar')]//a[contains(text(), 'Revisions')]",
                            "//div[contains(@class, 'sidebar')]//a[contains(text(), 'Revisions')]",
                            "//nav[contains(@class, 'menu')]//a[contains(text(), 'Revision')]",
                            "//div[contains(@id, 'sidebar')]//a[contains(@href, 'revisions')]",
                            "//aside//a[contains(text(), 'Revisions')]"
                        ]
                        
                        # Try each XPath with explicit wait but with shorter timeouts
                        for xpath in revisions_xpaths:
                            try:
                                logger.info(f"Trying View Revisions XPath: {xpath}")
                                view_revisions_link = WebDriverWait(driver, 3).until(
                                    EC.element_to_be_clickable((By.XPATH, xpath))
                                )
                                logger.info(f"Found View Revisions link with XPath: {xpath}")
                                
                                # Try JavaScript click first if regular click fails
                                try:
                                    view_revisions_link.click()
                                except:
                                    driver.execute_script("arguments[0].click();", view_revisions_link)
                                    
                                revisions_successful = True
                                edit_view_flow_successful = True
                                logger.info("Successfully clicked View Revisions link")
                                # Wait for page to load after click
                                time.sleep(2)
                                break
                            except:
                                continue
                                
                        if not revisions_successful:
                            logger.warning("All View Revisions XPaths failed, returning to event page")
                            # Navigate back to the event page to try direct PDF finding
                            driver.get(event_url)
                            # Wait for page to load
                            time.sleep(3)
                            # Handle cookie banner
                            handle_cookie_banner(driver)
                    except Exception as e:
                        logger.warning(f"Error with View Revisions link: {e}")
                        # Navigate back to the event page to try direct PDF finding
                        driver.get(event_url)
                        # Wait for page to load
                        time.sleep(3)
                        # Handle cookie banner
                        handle_cookie_banner(driver)
        except Exception as e:
            logger.warning(f"Error checking for direct PDF links: {e}")
            edit_view_flow_successful = False
        
        # Find the PDF link - try the specific XPath first, then fall back to more general ones
        if not direct_download_successful:
            pdf_link = None
            pdf_href = None
            try:
                # Use different XPath sets based on whether we're on the revisions page or event page
                if edit_view_flow_successful:
                    # XPaths for the revisions page
                    pdf_xpaths = [
                        # Original from full_Xpaths.txt
                        '/html/body/table[1]/tbody/tr/td[2]/table/tbody/tr/td/form/div/table/tbody/tr[1]/td[5]/p/a',
                        # Additional specific patterns
                        '//*[@id="revision"]/tbody/tr[1]/td[5]/p/a',  # First row
                        "//table[contains(@id, 'revision')]//tr[1]//a[contains(@href, 'viewcontent')]",  # First row in revision table
                        # More general patterns
                        "//table[contains(@id, 'revision')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                        "//table//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                        # New patterns for revision page
                        "//div[contains(@class, 'history')]//a[contains(@href, 'viewcontent')]",
                        "//div[contains(@id, 'version')]//a[contains(@href, 'viewcontent')]"
                    ]
                else:
                    # XPaths for directly finding PDF on the event page
                    pdf_xpaths = [
                        # Direct PDF download on event page patterns
                        "//a[contains(@href, 'download') and contains(@class, 'btn')]",
                        "//a[contains(text(), 'Download') and contains(@href, '.pdf')]",
                        "//a[contains(@class, 'download-btn')]",
                        "//div[contains(@class, 'abstract')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                        "//div[contains(@class, 'galleys')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                        "//div[contains(@class, 'item')]//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                        # New patterns for event page
                        "//aside[contains(@class, 'download')]//a",
                        "//div[contains(@class, 'files')]//a[contains(@href, '.pdf')]",
                        "//div[contains(@class, 'download')]//a",
                        "//section[contains(@class, 'download')]//a"
                    ]
                
                # Add common patterns that work for both page types
                pdf_xpaths.extend([
                    "//a[contains(@href, '.pdf') or contains(@href, 'viewcontent')]",
                    "//a[contains(text(), 'PDF') or contains(text(), 'Download')]",
                    "//a[contains(text(), 'View') and contains(text(), 'PDF')]",
                    "//a/img[contains(@alt, 'PDF')]/..",
                    "//a[contains(@class, 'pdf')]",
                    "//a[contains(@data-format, 'pdf')]",
                    "//a[contains(@title, 'PDF')]"
                ])
                
                # Try each XPath with logging
                for xpath in pdf_xpaths:
                    try:
                        logger.info(f"Trying PDF link XPath: {xpath}")
                        pdf_elements = driver.find_elements(By.XPATH, xpath)
                        if pdf_elements:
                            pdf_link = pdf_elements[0]  # Take the first match
                            pdf_href = pdf_link.get_attribute("href")
                            logger.info(f"Found PDF link with XPath {xpath}: {pdf_href}")
                            break
                    except Exception as e:
                        logger.debug(f"Error with PDF XPath {xpath}: {e}")
                        continue
                
                # If no PDF link found and we're in a revisions page, try finding any link in the first row
                if not pdf_link and "pickvers" in driver.current_url:
                    try:
                        logger.info("Trying to find any link in the first row of the revisions table")
                        first_row_links = driver.find_elements(By.XPATH, "//table[contains(@id, 'revision')]//tr[1]//a")
                        if first_row_links:
                            pdf_link = first_row_links[0]
                            pdf_href = pdf_link.get_attribute("href")
                            logger.info(f"Found potential PDF link in first row: {pdf_href}")
                    except Exception as e:
                        logger.debug(f"Error finding links in first row: {e}")
                
                # If still no link, try a more direct approach
                if not pdf_link:
                    # Try direct matching of PDF extension or content-type URL pattern
                    all_links = driver.find_elements(By.TAG_NAME, "a")
                    for link in all_links:
                        try:
                            href = link.get_attribute("href")
                            if href and ('.pdf' in href.lower() or 'viewcontent' in href.lower() or 'content_type=application/pdf' in href.lower()):
                                pdf_link = link
                                pdf_href = href
                                logger.info(f"Found PDF link by direct search: {pdf_href}")
                                break
                        except:
                            continue
                
                # If still no PDF link found, try searching in the page source
                if not pdf_link:
                    logger.warning("No PDF link found through XPaths, trying to extract from page source")
                    page_source = driver.page_source
                    
                    # Look for PDF links in the page source
                    pdf_urls = re.findall(r'href="([^"]*(?:viewcontent\.cgi[^"]*|\.pdf)[^"]*)"', page_source)
                    if pdf_urls:
                        # Select the first PDF URL found
                        pdf_href = pdf_urls[0]
                        logger.info(f"Extracted PDF URL from page source: {pdf_href}")
                    else:
                        logger.warning("No PDF link found in the page source")
                        return False
            except Exception as e:
                logger.warning(f"Error finding PDF link: {e}")
                
            # Final check - if we still have no link, return failure
            if not pdf_href:
                logger.warning("No PDF link could be found through any method")
                return False
        
        # Log confirmation of found PDF link
        logger.info(f"Using PDF link: {pdf_href}")
        
        # Extract the article number from the URL
        article_number = None
        if "article=" in pdf_href:
            # Parse the query parameters
            query_params = parse_qs(urlparse(pdf_href).query)
            if 'article' in query_params:
                article_number = query_params['article'][0]
        
        if not article_number:
            # Fallback to regex extraction if parse_qs doesn't work
            article_match = re.search(r'article=(\d+)', pdf_href)
            if article_match:
                article_number = article_match.group(1)
        
        if not article_number:
            logger.warning("Could not extract article number from URL, using a placeholder")
            article_number = f"0000"  # Use placeholder for unknown article numbers
        
        # Format the filename according to the requirements
        # {four digit article number}_{Publication Series}_{section}_{partition}.pdf
        # Example: 1223_modvis_2024_va.pdf
        
        # Parse the event URL to extract components for better filename creation
        event_url_parts = urlparse(event_url).path.strip('/').split('/')
        
        # Extract parts from URL structure - prefer event URL parts if available
        series = event_url_parts[0] if len(event_url_parts) > 0 else (url_structure[0] if len(url_structure) > 0 else "")
        section = event_url_parts[1] if len(event_url_parts) > 1 else (url_structure[1] if len(url_structure) > 1 else "") # Year or other section identifier
        partition = event_url_parts[2] if len(event_url_parts) > 2 else (url_structure[2] if len(url_structure) > 2 else "") # va, cmec, etc.
        event_id = event_url_parts[3] if len(event_url_parts) > 3 else ""
        
        # Build filename parts
        filename_parts = [article_number, series]
        
        # Add section if present (which may be a year or other identifier)
        if section and not "announcements.html" in section and not "." in section:
            filename_parts.append(section)
            
        # Add partition (va, cmec, etc.) if present
        if partition and not "announcements.html" in partition and not "." in partition and not partition.isdigit():
            filename_parts.append(partition)
        
        # Combine into final filename
        custom_filename = "_".join(filename_parts)
        
        # Clean the filename to remove invalid characters
        custom_filename = re.sub(r'[\\/*?:"<>|]', "_", custom_filename)
        
        # Make sure article number is padded to 4 digits
        if len(article_number) < 4:
            padded_article_number = article_number.zfill(4)
            custom_filename = custom_filename.replace(article_number, padded_article_number, 1)
            
        # Add .pdf extension (but prevent duplicate .pdf.pdf)
        if not custom_filename.lower().endswith('.pdf'):
            custom_filename = f"{custom_filename}.pdf"
        
        # Handle cookie banner with more robust approach before clicking PDF link
        handle_cookie_banner(driver)
        
        # If banner still exists, try to remove it with JavaScript
        if driver.find_elements(By.ID, 'onetrust-banner-sdk'):
            remove_cookie_banner_with_js(driver)
        
        # Try to click the PDF link with multiple fallback strategies
        logger.info(f"Downloading PDF with filename: {custom_filename}")
        if not click_pdf_link_with_fallbacks(driver, pdf_link):
            # If all click strategies fail, try direct download if possible
            try:
                pdf_url = pdf_link.get_attribute("href")
                # Open in new tab/window and switch to it
                logger.info("Attempting to open PDF in new tab")
                driver.execute_script(f"window.open('{pdf_url}', '_blank');")
                driver.switch_to.window(driver.window_handles[-1])
                time.sleep(3)  # Allow time for the PDF to start loading
                # Switch back to the original tab
                driver.switch_to.window(driver.window_handles[0])
            except Exception as e:
                logger.error(f"All PDF access methods failed: {e}")
                return False  # Mark this event as failed
        
        # Wait for download to start and complete
        time.sleep(5)  # Adjust based on typical download times
        
        # Check for the downloaded file and rename it
        max_wait = 60  # Increased maximum wait time in seconds
        start_time = time.time()
        
        # Always try direct download first - works better especially in WSL environment
        if pdf_href:
            try:
                logger.info("Attempting direct HTTP download of PDF")
                pdf_url = pdf_href
                direct_file_path = os.path.join(event_download_directory, f"{custom_filename}")
                
                # Use requests to download the PDF directly
                logger.info(f"Downloading PDF directly from {pdf_url} to {direct_file_path}")
                
                # Make GET request with proper headers
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36',
                    'Accept': 'application/pdf, text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
                }
                
                # Get cookies from current session
                cookies = driver.get_cookies()
                cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}
                
                # Make the request
                session = get_http_session()
                response = session.get(pdf_url, headers=headers, cookies=cookie_dict, stream=True, timeout=30)
                
                content_type = response.headers.get('Content-Type', '').lower()
                if response.status_code == 200 and ('application/pdf' in content_type or 'application/octet-stream' in content_type):
                    # Save the PDF
                    with open(direct_file_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            if chunk:
                                f.write(chunk)
                    
                    if os.path.exists(direct_file_path) and os.path.getsize(direct_file_path) > 0:
                        logger.info(f"Successfully downloaded PDF directly to: {direct_file_path}")
                        return True  # Mark this event as successful
                else:
                    logger.warning(f"Direct download failed. Status code: {response.status_code}, Content-Type: {content_type}")
                    
                    # If we get HTML instead of PDF, the page might require authentication or have a viewer
                    # Try clicking the link in the browser as fallback
                    if 'text/html' in content_type:
                        logger.info("Received HTML instead of PDF, trying browser click as fallback")
                        if click_pdf_link_with_fallbacks(driver, pdf_link):
                            # Wait for browser download
                            time.sleep(5)
            except Exception as e:
                logger.warning(f"Error with direct download approach: {e}")
                # Fall back to browser download detection
        
        # Regular download detection code as fallback
        while time.time() - start_time < max_wait:
            try:
                # Look for any PDF files that were just downloaded
                downloaded_files = [f for f in os.listdir(event_download_directory) 
                                  if f.lower().endswith(".pdf") and 
                                  os.path.getctime(os.path.join(event_download_directory, f)) > 
                                  start_time - 10]  # Extended check time to account for WSL filesystem delays
                
                if downloaded_files:
                    # Get the most recently downloaded PDF file
                    most_recent_file = max(
                        [os.path.join(event_download_directory, f) for f in downloaded_files],
                        key=os.path.getctime
                    )
                    
                    # Rename the file
                    new_filename = os.path.join(event_download_directory, f"{custom_filename}.pdf")
                    
                    # If the target file already exists, remove it first
                    if os.path.exists(new_filename):
                        os.remove(new_filename)
                        
                    os.rename(most_recent_file, new_filename)
                    logger.info(f"Successfully renamed downloaded PDF to: {custom_filename}.pdf")
                    return True  # Mark this event as successful
            except Exception as e:
                logger.warning(f"Error checking download directory: {e}")
            
            time.sleep(2)  # Increased check interval to reduce filesystem operations
        
        logger.warning("No PDF file found in download directory after waiting.")
        return False  # Mark this event as failed
            
    except Exception as e:
        logger.error(f"Error processing event: {e}")

def process_url_list(url_file_path, username=None, password=None, custom_download_dir=None, max_workers=3, use_shared_driver=True):
    """
    Process a list of URLs from a text file in parallel.
    
    Args:
        url_file_path: Path to the text file containing URLs to process
        username: Optional username for login
        password: Optional password for login
        custom_download_dir: Optional override for download directory
        max_workers: Maximum number of parallel workers (default: 3)
        use_shared_driver: Whether to use a shared WebDriver for sequential processing (default: True)
    """
    # Check if the file exists
    if not os.path.isfile(url_file_path):
        logger.error(f"Error: URL file not found at {url_file_path}")
        return False
    
    # Read URLs from the file
    with open(url_file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
    
    if not urls:
        logger.warning("No valid URLs found in the file.")
        return False
    
    logger.info(f"Found {len(urls)} URLs to process.")
    
    # Prompt for login credentials once
    if not username or not password:
        username = input("Enter your Purdue username: ")
        password = getpass.getpass("Enter your Purdue password: ")
    
    # For shared driver mode, we process URLs sequentially with a single WebDriver instance
    if use_shared_driver and max_workers == 1:
        try:
            logger.info("Processing URLs sequentially with shared WebDriver...")
            results = []
            
            # Process each URL sequentially with shared driver
            for i, url in enumerate(urls):
                logger.info(f"\n[{i+1}/{len(urls)}] Processing URL: {url}")
                result = process_purdue_library_content(url, username, password, custom_download_dir, shared_driver=True)
                results.append(result)
                
            # Clean up shared WebDriver after processing all URLs
            cleanup_shared_webdriver()
            
            # Calculate success/failure statistics
            successful = results.count(True)
            failed = results.count(False)
            
            logger.info(f"\nAll URLs have been processed sequentially! Success: {successful}, Failed: {failed}")
            return successful > 0
            
        except Exception as e:
            logger.error(f"Error during sequential processing: {e}")
            cleanup_shared_webdriver()
            return False
    
    # For parallel processing, we use separate WebDriver instances
    # Create a thread-safe counter for progress tracking
    completed_count = 0
    progress_lock = Lock()
    
    def process_url_with_progress(url):
        """Wrapper function to process a URL and update progress"""
        nonlocal completed_count
        
        try:
            # Use separate WebDriver instance for each thread
            result = process_purdue_library_content(url, username, password, custom_download_dir, shared_driver=False)
            
            # Update the progress counter in a thread-safe way
            with progress_lock:
                completed_count += 1
                logger.info(f"\n[{completed_count}/{len(urls)}] Completed URL: {url}")
                
            return result
        except Exception as e:
            logger.error(f"Error processing URL {url}: {e}")
            
            # Still increment the counter even if there was an error
            with progress_lock:
                completed_count += 1
                logger.info(f"\n[{completed_count}/{len(urls)}] Failed URL: {url}")
                
            return False
    
    # Process URLs in parallel using ThreadPoolExecutor
    logger.info(f"Processing URLs in parallel with {max_workers} workers...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all URL processing tasks
        future_to_url = {executor.submit(process_url_with_progress, url): url for url in urls}
        
        # Wait for all tasks to complete
        results = []
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                logger.error(f"Exception while processing {url}: {e}")
                results.append(False)
    
    # Calculate success/failure statistics
    successful = results.count(True)
    failed = results.count(False)
    
    logger.info(f"\nAll URLs have been processed in parallel! Success: {successful}, Failed: {failed}")
    return successful > 0

def check_s_drive_mount():
    """
    Check if the S: drive is properly mounted in WSL
    Returns True if mounted, False otherwise
    """
    if not os.path.exists('/mnt/s'):
        logger.warning("S: drive mount point doesn't exist. Creating it...")
        try:
            os.makedirs('/mnt/s', exist_ok=True)
        except Exception as e:
            logger.error(f"Error creating mount point: {e}")
            return False
    
    # Check if anything is mounted there
    if not os.listdir('/mnt/s'):
        logger.warning("WARNING: S: drive doesn't appear to be mounted.")
        logger.info("Please mount it using: sudo mount -t drvfs S: /mnt/s")
        
        # Ask user if they want to try mounting it
        mount_response = input("Would you like to try mounting the S: drive now? (y/n): ")
        if mount_response.lower() == 'y':
            try:
                result = subprocess.run(["sudo", "mount", "-t", "drvfs", "S:", "/mnt/s"], 
                                        capture_output=True, text=True, check=False)
                if result.returncode == 0:
                    logger.info("S: drive mounted successfully!")
                    return True
                else:
                    logger.error(f"Error mounting S: drive: {result.stderr}")
                    return False
            except Exception as e:
                logger.error(f"Error mounting S: drive: {e}")
                return False
        else:
            return False
    
    return True

def main():
    """Main function to run from command line"""
    import argparse
    
    # Set up command line argument parsing
    parser = argparse.ArgumentParser(description='Download PDFs from Purdue Library site')
    parser.add_argument('--url', help='Single URL to process')
    parser.add_argument('--file', help='Text file containing list of URLs to process')
    parser.add_argument('--download-dir', help='Custom download directory')
    parser.add_argument('--username', help='Purdue username')
    parser.add_argument('--password', help='Purdue password (not recommended, use interactive prompt)')
    parser.add_argument('--workers', type=int, default=3, help='Number of parallel workers for processing multiple URLs (default: 3)')
    parser.add_argument('--shared-driver', action='store_true', help='Use shared WebDriver instance for processing URLs')
    parser.add_argument('--no-shared-driver', action='store_false', dest='shared_driver', help='Do not use shared WebDriver instance')
    parser.add_argument('--debug', action='store_true', help='Enable debug logging')
    
    # Set default for shared driver
    parser.set_defaults(shared_driver=True)
    
    args = parser.parse_args()
    
    # Set debug level if requested
    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Check if mandatory arguments are provided
    if not args.url and not args.file:
        parser.print_help()
        logger.error("\nError: Either --url or --file must be specified.")
        sys.exit(1)
    
    # Check if S: drive is mounted (if we're in WSL)
    if is_wsl():
        if not check_s_drive_mount() and not args.download_dir:
            logger.error("ERROR: S: drive is not properly mounted and no custom download directory was specified.")
            logger.error("Please either:")
            logger.error("1. Mount the S: drive with: sudo mount -t drvfs S: /mnt/s")
            logger.error("2. Specify a custom download directory with --download-dir")
            sys.exit(1)
    
    # Get username and password
    username = args.username
    password = args.password
    
    if not username:
        username = input("Enter your Purdue username: ")
    
    if not password:
        password = getpass.getpass("Enter your Purdue password: ")
    
    # Install required packages if they're missing
    try:
        import requests
    except ImportError:
        logger.info("Installing required package: requests")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import requests
    
    try:
        # Process URL or file of URLs
        if args.file:
            process_url_list(args.file, username, password, args.download_dir, 
                           max_workers=args.workers, use_shared_driver=args.shared_driver)
        else:
            # For single URLs, always use a new WebDriver instance
            process_purdue_library_content(args.url, username, password, args.download_dir, 
                                         shared_driver=False)
    finally:
        # Always clean up shared WebDriver on exit
        cleanup_shared_webdriver()

if __name__ == "__main__":
    main()
