#!/usr/bin/env python3
"""
Purdue Digital Commons Collection Downloader

A unified, modern scraper for downloading manuscripts from any Purdue Digital Commons
collection (docs.lib.purdue.edu). Features:

- Generic collection support (works with any docs.lib.purdue.edu/* URL)
- Multi-URL input (single, multiple, or from text file)
- Rich terminal output with progress bars and color coding
- Direct HTTP downloads with browser fallback
- Intelligent authentication handling
- Cross-platform support (macOS, Linux, WSL)

Example usage:
    # Single collection
    python3 -m src.scraper.purdue_collection_downloader download \\
        --url "https://docs.lib.purdue.edu/roadschool/"

    # Multiple collections from file
    python3 -m src.scraper.purdue_collection_downloader download \\
        --url-file urls.txt --workers 2
"""

import os
import sys
import time
import platform
import subprocess
import re
import random
import configparser
import tempfile
import zipfile
import io
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set
from urllib.parse import urlparse, urljoin, parse_qs
from dataclasses import dataclass
from datetime import datetime

# Third-party imports
import requests
import typer
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn
from rich.table import Table
from rich.tree import Tree
from rich import print as rprint

# Selenium imports
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    ElementNotInteractableException,
    ElementClickInterceptedException
)

# =============================================================================
# CONFIGURATION
# =============================================================================

console = Console()

# Read configuration
DEFAULT_CONFIG = {
    'download_directory': str(Path.home() / 'Downloads' / 'purdue_collections'),
    'timeout': '30',
    'max_retries': '3',
    'concurrent_downloads': '2'
}

def load_config() -> Dict[str, str]:
    """Load configuration from config.ini or use defaults."""
    config = configparser.ConfigParser()
    config_path = Path(__file__).parent / 'config.ini'

    if config_path.exists():
        config.read(config_path)
        if 'PurdueDownloader' in config:
            return dict(config['PurdueDownloader'])

    return DEFAULT_CONFIG


# =============================================================================
# DATA STRUCTURES
# =============================================================================

@dataclass
class DownloadResult:
    """Result of a single file download."""
    url: str
    output_path: Optional[Path]
    success: bool
    error: Optional[str] = None
    size_bytes: int = 0
    duration_seconds: float = 0.0
    method: str = "unknown"  # "direct_http" or "browser"


@dataclass
class CollectionResult:
    """Result of processing a single collection."""
    collection_url: str
    total_documents: int
    successful: int
    failed: int
    total_size_bytes: int
    duration_seconds: float
    failed_urls: List[str]


# =============================================================================
# UTILITIES
# =============================================================================

class HTTPSessionManager:
    """Manages HTTP sessions with connection pooling and retry logic."""

    _session: Optional[requests.Session] = None

    @classmethod
    def get_session(cls) -> requests.Session:
        """Get or create optimized HTTP session."""
        if cls._session is None:
            session = requests.Session()

            # Configure retry strategy
            retry_strategy = Retry(
                total=3,
                backoff_factor=0.5,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["GET", "POST", "HEAD"]
            )

            # Configure connection pool
            adapter = HTTPAdapter(
                max_retries=retry_strategy,
                pool_connections=10,
                pool_maxsize=10
            )

            session.mount("http://", adapter)
            session.mount("https://", adapter)

            cls._session = session

        return cls._session


def is_wsl() -> bool:
    """Detect if running in Windows Subsystem for Linux."""
    if "microsoft" in platform.release().lower():
        return True

    if os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop'):
        return True

    try:
        with open('/proc/version', 'r') as f:
            if 'microsoft' in f.read().lower():
                return True
    except:
        pass

    return False


def get_chrome_version() -> str:
    """Get installed Chrome version or return default."""
    default_version = "136"

    try:
        version_output = subprocess.check_output(
            ["google-chrome", "--version"],
            text=True,
            stderr=subprocess.DEVNULL
        ).strip()

        match = re.search(r'Chrome\s+(\d+)\.', version_output)
        if match:
            return match.group(1)
    except:
        pass

    return default_version


def setup_webdriver() -> webdriver.Chrome:
    """
    Setup Chrome WebDriver with optimized options.

    Returns:
        Configured Chrome WebDriver instance
    """
    chrome_options = Options()

    # Performance optimizations
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Additional settings for reliability
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)

    # Set download preferences
    prefs = {
        "download.prompt_for_download": False,
        "plugins.always_open_pdf_externally": True,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True
    }
    chrome_options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(options=chrome_options)

    # Set page load timeout
    driver.set_page_load_timeout(30)

    return driver


def wait_for_page_load(driver: webdriver.Chrome, timeout: int = 10):
    """Wait for page to fully load."""
    try:
        WebDriverWait(driver, timeout).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )
    except TimeoutException:
        pass  # Continue anyway


def handle_cookie_banner(driver: webdriver.Chrome):
    """Dismiss cookie consent banners if present."""
    cookie_selectors = [
        "button.osano-cm-accept",
        "button#onetrust-accept-btn-handler",
        "button[aria-label='Accept cookies']",
        "button[aria-label='Accept all']"
    ]

    for selector in cookie_selectors:
        try:
            button = driver.find_element(By.CSS_SELECTOR, selector)
            button.click()
            time.sleep(0.5)
            return
        except:
            continue


def retry_with_backoff(retries: int = 3, backoff_factor: float = 0.5):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        retries: Maximum number of retry attempts
        backoff_factor: Factor for exponential backoff calculation
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            attempt = 0
            total_attempts = retries + 1

            while attempt < total_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    attempt += 1
                    if attempt >= total_attempts:
                        raise

                    # Calculate backoff with jitter
                    backoff_time = backoff_factor * (2 ** (attempt - 1))
                    jitter = backoff_time * 0.2
                    backoff_time = backoff_time + random.uniform(-jitter, jitter)
                    backoff_time = max(0.1, backoff_time)

                    if kwargs.get('verbose'):
                        console.print(f"[yellow]Retry {attempt}/{retries}:[/yellow] {e}")
                        console.print(f"[dim]Waiting {backoff_time:.1f}s...[/dim]")

                    time.sleep(backoff_time)

            return None
        return wrapper
    return decorator


# =============================================================================
# AUTHENTICATION
# =============================================================================

def check_login_required(driver: webdriver.Chrome) -> bool:
    """Check if login is required on current page."""
    indicators = [
        lambda: "login.cgi" in driver.current_url,
        lambda: driver.find_elements(By.ID, "username"),
        lambda: driver.find_elements(By.CSS_SELECTOR, "input[type='password']"),
        lambda: "authentication required" in driver.page_source.lower()
    ]

    for check in indicators:
        try:
            if check():
                return True
        except:
            continue

    return False


def handle_login(driver: webdriver.Chrome, username: str, password: str, verbose: bool = False) -> bool:
    """
    Handle authentication on Purdue login page.

    Args:
        driver: Selenium WebDriver instance
        username: Purdue username
        password: Purdue password
        verbose: Enable verbose output

    Returns:
        True if login successful, False otherwise
    """
    try:
        if verbose:
            console.print("[cyan]Authenticating...[/cyan]")

        # Wait for login form
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        )
        password_field = driver.find_element(By.ID, "password")

        # Enter credentials
        username_field.clear()
        username_field.send_keys(username)
        password_field.clear()
        password_field.send_keys(password)

        # Submit form
        submit_button = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
        submit_button.click()

        # Wait for redirect
        wait_for_page_load(driver)
        time.sleep(2)

        # Verify login success
        if "login.cgi" not in driver.current_url:
            if verbose:
                console.print("[green]✓ Authentication successful[/green]")
            return True
        else:
            console.print("[red]✗ Authentication failed[/red]")
            return False

    except Exception as e:
        console.print(f"[red]✗ Authentication error:[/red] {e}")
        return False


# =============================================================================
# URL MANAGEMENT
# =============================================================================

def parse_url_file(file_path: Path) -> List[str]:
    """
    Parse URLs from text file.

    Args:
        file_path: Path to text file with URLs

    Returns:
        List of valid URLs (comments and blank lines removed)
    """
    urls = []

    try:
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and blank lines
                if not line or line.startswith('#'):
                    continue

                # Validate URL
                if line.startswith('http'):
                    urls.append(line)
    except Exception as e:
        console.print(f"[red]Error reading URL file:[/red] {e}")

    return urls


def validate_purdue_url(url: str) -> bool:
    """Validate that URL is a Purdue Digital Commons collection."""
    try:
        parsed = urlparse(url)
        return (
            'docs.lib.purdue.edu' in parsed.netloc and
            len(parsed.path.strip('/')) > 0
        )
    except:
        return False


def deduplicate_urls(urls: List[str]) -> List[str]:
    """Remove duplicate URLs while preserving order."""
    seen = set()
    result = []

    for url in urls:
        # Normalize URL (remove trailing slash for comparison)
        normalized = url.rstrip('/')
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)

    return result


# =============================================================================
# DOCUMENT DISCOVERY
# =============================================================================

class DocumentDiscovery:
    """Handles document discovery within collections."""

    def __init__(self, driver: webdriver.Chrome, verbose: bool = False):
        self.driver = driver
        self.verbose = verbose

    def discover_manuscripts(self, collection_url: str) -> List[Dict[str, str]]:
        """
        Discover all manuscript pages in a collection.

        Args:
            collection_url: Base URL of the collection

        Returns:
            List of dictionaries with manuscript information
        """
        self.driver.get(collection_url)
        wait_for_page_load(self.driver)
        handle_cookie_banner(self.driver)

        # Try to find manuscripts directly
        manuscripts = self._find_manuscript_pages(collection_url)
        if manuscripts:
            return manuscripts

        # If no manuscripts found, look for intermediate section pages
        section_urls = self._find_section_pages(collection_url)

        all_manuscripts = []
        for section_url in section_urls:
            self.driver.get(section_url)
            wait_for_page_load(self.driver)

            section_manuscripts = self._find_manuscript_pages(section_url)
            if section_manuscripts:
                all_manuscripts.extend(section_manuscripts)
            else:
                # Go deeper - look for sub-sections
                sub_sections = self._find_section_pages(section_url)
                for sub_url in sub_sections:
                    self.driver.get(sub_url)
                    wait_for_page_load(self.driver)
                    sub_manuscripts = self._find_manuscript_pages(sub_url)
                    all_manuscripts.extend(sub_manuscripts)

        # Remove duplicates
        unique_manuscripts = []
        seen_urls = set()
        for manuscript in all_manuscripts:
            if manuscript['url'] not in seen_urls:
                unique_manuscripts.append(manuscript)
                seen_urls.add(manuscript['url'])

        return unique_manuscripts

    def _find_manuscript_pages(self, base_url: str) -> List[Dict[str, str]]:
        """Find manuscript pages (end with number)."""
        manuscripts = []

        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")

            for link in links:
                href = link.get_attribute("href")
                if href and self._is_manuscript_url(href, base_url):
                    manuscripts.append({
                        'url': href,
                        'text': link.text.strip(),
                        'title': link.get_attribute("title") or ""
                    })
        except:
            pass

        return manuscripts

    def _find_section_pages(self, base_url: str) -> List[str]:
        """Find intermediate section pages."""
        sections = []

        try:
            links = self.driver.find_elements(By.CSS_SELECTOR, "a[href]")

            for link in links:
                href = link.get_attribute("href")
                if href and self._is_section_url(href, base_url):
                    sections.append(href)
        except:
            pass

        return list(set(sections))  # Deduplicate

    def _is_manuscript_url(self, url: str, base_url: str) -> bool:
        """Check if URL is a manuscript page."""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            # Must be same domain
            if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
                return False

            path = parsed_url.path.strip('/')
            base_path = parsed_base.path.strip('/')

            # Skip if same as base
            if path == base_path:
                return False

            # Skip PDFs and system URLs
            if any(skip in path.lower() for skip in ['.pdf', 'viewcontent', 'search', 'browse', 'about', 'admin']):
                return False

            # Must be more specific than base
            if not path.startswith(base_path):
                return False

            # Check if ends with number (manuscript ID)
            path_parts = path.split('/')
            if path_parts and path_parts[-1].isdigit():
                # Filter out years (4 digits > 1900)
                last_part = path_parts[-1]
                if len(last_part) == 4 and int(last_part) > 1900:
                    return False
                return True

            return False
        except:
            return False

    def _is_section_url(self, url: str, base_url: str) -> bool:
        """Check if URL is a section page."""
        try:
            parsed_url = urlparse(url)
            parsed_base = urlparse(base_url)

            if parsed_url.netloc and parsed_url.netloc != parsed_base.netloc:
                return False

            path = parsed_url.path.strip('/')
            base_path = parsed_base.path.strip('/')

            if path == base_path:
                return False

            if any(skip in path.lower() for skip in ['.pdf', 'viewcontent', 'search', 'browse', 'about', 'admin']):
                return False

            if not path.startswith(base_path):
                return False

            # Section pages don't end with manuscript numbers
            path_parts = path.split('/')
            if path_parts:
                last_part = path_parts[-1]
                if not last_part.isdigit():
                    return len(path_parts) > len(base_path.split('/'))
                # Allow years as section identifiers
                elif len(last_part) == 4 and 1900 < int(last_part) < 2100:
                    return True

            return False
        except:
            return False


# =============================================================================
# DOWNLOAD STRATEGIES
# =============================================================================

class DirectHTTPDownloader:
    """Download PDFs directly via HTTP (fastest method)."""

    def __init__(self, verbose: bool = False):
        self.session = HTTPSessionManager.get_session()
        self.verbose = verbose

    @retry_with_backoff(retries=2)
    def download(self, pdf_url: str, output_path: Path, cookies: Optional[Dict] = None) -> DownloadResult:
        """
        Download PDF directly via HTTP.

        Args:
            pdf_url: Direct URL to PDF
            output_path: Where to save the file
            cookies: Optional browser cookies for authentication

        Returns:
            DownloadResult with success status
        """
        start_time = time.time()

        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
                'Accept': 'application/pdf,application/octet-stream,*/*',
            }

            response = self.session.get(
                pdf_url,
                headers=headers,
                cookies=cookies,
                stream=True,
                timeout=60,
                allow_redirects=True
            )

            if response.status_code != 200:
                return DownloadResult(
                    url=pdf_url,
                    output_path=None,
                    success=False,
                    error=f"HTTP {response.status_code}",
                    duration_seconds=time.time() - start_time
                )

            # Verify content type
            content_type = response.headers.get('Content-Type', '').lower()
            if 'pdf' not in content_type and 'octet-stream' not in content_type:
                # Check PDF header
                first_chunk = next(response.iter_content(1024), b'')
                if not first_chunk.startswith(b'%PDF'):
                    return DownloadResult(
                        url=pdf_url,
                        output_path=None,
                        success=False,
                        error="Not a PDF file",
                        duration_seconds=time.time() - start_time
                    )

            # Download file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            downloaded_size = 0

            with open(output_path, 'wb') as f:
                if 'first_chunk' in locals():
                    f.write(first_chunk)
                    downloaded_size += len(first_chunk)

                for chunk in response.iter_content(8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

            # Verify download
            if output_path.exists() and output_path.stat().st_size > 0:
                return DownloadResult(
                    url=pdf_url,
                    output_path=output_path,
                    success=True,
                    size_bytes=downloaded_size,
                    duration_seconds=time.time() - start_time,
                    method="direct_http"
                )
            else:
                return DownloadResult(
                    url=pdf_url,
                    output_path=None,
                    success=False,
                    error="Empty file",
                    duration_seconds=time.time() - start_time
                )

        except Exception as e:
            return DownloadResult(
                url=pdf_url,
                output_path=None,
                success=False,
                error=str(e),
                duration_seconds=time.time() - start_time
            )


class BrowserDownloader:
    """Download PDFs using browser automation (fallback method)."""

    def __init__(self, driver: webdriver.Chrome, verbose: bool = False):
        self.driver = driver
        self.verbose = verbose

    def download(self, manuscript_url: str, output_path: Path, username: Optional[str] = None, password: Optional[str] = None) -> DownloadResult:
        """
        Download PDF using browser automation.

        Args:
            manuscript_url: URL of manuscript page
            output_path: Where to save the file
            username: Optional Purdue username
            password: Optional Purdue password

        Returns:
            DownloadResult with success status
        """
        start_time = time.time()

        try:
            # Navigate to manuscript page
            self.driver.get(manuscript_url)
            wait_for_page_load(self.driver)
            handle_cookie_banner(self.driver)

            # Check if login required
            if check_login_required(self.driver):
                if not username or not password:
                    return DownloadResult(
                        url=manuscript_url,
                        output_path=None,
                        success=False,
                        error="Authentication required but no credentials provided",
                        duration_seconds=time.time() - start_time
                    )

                if not handle_login(self.driver, username, password, self.verbose):
                    return DownloadResult(
                        url=manuscript_url,
                        output_path=None,
                        success=False,
                        error="Authentication failed",
                        duration_seconds=time.time() - start_time
                    )

                # Reload manuscript page after login
                self.driver.get(manuscript_url)
                wait_for_page_load(self.driver)

            # Find PDF download link
            pdf_url = self._find_pdf_url()

            if not pdf_url:
                return DownloadResult(
                    url=manuscript_url,
                    output_path=None,
                    success=False,
                    error="PDF download link not found",
                    duration_seconds=time.time() - start_time
                )

            # Use direct HTTP downloader with browser cookies
            http_downloader = DirectHTTPDownloader(self.verbose)
            cookies = {cookie['name']: cookie['value'] for cookie in self.driver.get_cookies()}

            result = http_downloader.download(pdf_url, output_path, cookies)
            result.method = "browser"

            return result

        except Exception as e:
            return DownloadResult(
                url=manuscript_url,
                output_path=None,
                success=False,
                error=str(e),
                duration_seconds=time.time() - start_time
            )

    def _find_pdf_url(self) -> Optional[str]:
        """Find PDF download URL on current page."""
        # Try multiple selectors
        selectors = [
            "a[href*='.pdf']",
            "a[href*='viewcontent']",
            "a.download",
            "a[title*='Download']"
        ]

        for selector in selectors:
            try:
                links = self.driver.find_elements(By.CSS_SELECTOR, selector)
                for link in links:
                    href = link.get_attribute('href')
                    if href and ('.pdf' in href or 'viewcontent' in href):
                        return href
            except:
                continue

        return None


# =============================================================================
# MAIN DOWNLOADER
# =============================================================================

class PurdueCollectionDownloader:
    """Main orchestrator for downloading Purdue Digital Commons collections."""

    def __init__(self, output_dir: Path, username: Optional[str] = None, password: Optional[str] = None, verbose: bool = False):
        self.output_dir = output_dir
        self.username = username
        self.password = password
        self.verbose = verbose
        self.driver = None

        # Statistics
        self.stats = {
            'collections_processed': 0,
            'total_documents': 0,
            'successful_downloads': 0,
            'failed_downloads': 0,
            'total_bytes': 0,
            'start_time': None,
            'end_time': None
        }

    def download_collections(self, collection_urls: List[str]) -> List[CollectionResult]:
        """
        Download all manuscripts from multiple collections.

        Args:
            collection_urls: List of collection URLs to process

        Returns:
            List of CollectionResult objects
        """
        self.stats['start_time'] = time.time()
        results = []

        try:
            # Setup WebDriver
            console.print("[cyan]Initializing browser...[/cyan]")
            self.driver = setup_webdriver()

            # Process each collection
            for idx, url in enumerate(collection_urls, 1):
                console.print(f"\n[bold cyan][{idx}/{len(collection_urls)}] {url}[/bold cyan]")

                result = self._process_collection(url)
                results.append(result)

                self.stats['collections_processed'] += 1
                self.stats['total_documents'] += result.total_documents
                self.stats['successful_downloads'] += result.successful
                self.stats['failed_downloads'] += result.failed
                self.stats['total_bytes'] += result.total_size_bytes

        finally:
            if self.driver:
                self.driver.quit()

            self.stats['end_time'] = time.time()

        return results

    def _process_collection(self, collection_url: str) -> CollectionResult:
        """Process a single collection."""
        start_time = time.time()

        # Discovery phase
        console.print("  [cyan]├─ Discovering documents...[/cyan]")
        discovery = DocumentDiscovery(self.driver, self.verbose)
        manuscripts = discovery.discover_manuscripts(collection_url)

        console.print(f"  [cyan]│  └─ 📄 Found {len(manuscripts)} manuscripts[/cyan]")

        if not manuscripts:
            return CollectionResult(
                collection_url=collection_url,
                total_documents=0,
                successful=0,
                failed=0,
                total_size_bytes=0,
                duration_seconds=time.time() - start_time,
                failed_urls=[]
            )

        # Download phase
        console.print("  [cyan]├─ Downloading...[/cyan]")

        successful = 0
        failed = 0
        total_bytes = 0
        failed_urls = []

        # Create downloaders
        http_downloader = DirectHTTPDownloader(self.verbose)
        browser_downloader = BrowserDownloader(self.driver, self.verbose)

        # Progress bar
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("  │  ", total=len(manuscripts))

            for manuscript in manuscripts:
                # Generate output filename
                filename = self._generate_filename(manuscript['url'], manuscript.get('title', ''))
                output_path = self.output_dir / filename

                # Try direct HTTP first
                result = http_downloader.download(manuscript['url'], output_path)

                # Fallback to browser if needed
                if not result.success:
                    result = browser_downloader.download(
                        manuscript['url'],
                        output_path,
                        self.username,
                        self.password
                    )

                # Update statistics
                if result.success:
                    successful += 1
                    total_bytes += result.size_bytes
                else:
                    failed += 1
                    failed_urls.append(manuscript['url'])

                progress.update(task, advance=1)

        # Summary
        if successful > 0:
            console.print(f"  [green]└─ ✓ Complete:[/green] {successful}/{len(manuscripts)} successful")
        else:
            console.print(f"  [red]└─ ✗ Failed:[/red] No downloads successful")

        return CollectionResult(
            collection_url=collection_url,
            total_documents=len(manuscripts),
            successful=successful,
            failed=failed,
            total_size_bytes=total_bytes,
            duration_seconds=time.time() - start_time,
            failed_urls=failed_urls
        )

    def _generate_filename(self, url: str, title: str) -> str:
        """Generate safe filename from URL and title."""
        # Extract document ID from URL
        parsed = urlparse(url)
        path_parts = parsed.path.strip('/').split('/')
        doc_id = path_parts[-1] if path_parts else 'unknown'

        # Sanitize title
        if title:
            safe_title = re.sub(r'[^\w\s-]', '', title)[:50]
            safe_title = re.sub(r'[-\s]+', '_', safe_title)
            return f"{doc_id}_{safe_title}.pdf"

        return f"{doc_id}.pdf"

    def print_summary(self, results: List[CollectionResult]):
        """Print overall download summary."""
        console.print("\n[bold]Overall Summary:[/bold]")

        # Create summary table
        table = Table(show_header=False, box=None, padding=(0, 2))

        duration = self.stats['end_time'] - self.stats['start_time']
        duration_str = f"{duration/60:.1f}m" if duration > 60 else f"{duration:.1f}s"
        size_mb = self.stats['total_bytes'] / (1024 * 1024)

        table.add_row("Collections:", str(self.stats['collections_processed']))
        table.add_row("Total files:", str(self.stats['total_documents']))
        table.add_row("[green]Successful:[/green]", f"[green]{self.stats['successful_downloads']}[/green]")
        table.add_row("[red]Failed:[/red]", f"[red]{self.stats['failed_downloads']}[/red]")
        table.add_row("Total size:", f"{size_mb:.1f}MB")
        table.add_row("Duration:", duration_str)

        console.print(table)

        if self.stats['successful_downloads'] > 0:
            console.print(f"\n[green]✓ Download complete![/green]")
            console.print(f"Files saved to: {self.output_dir}")
        else:
            console.print(f"\n[red]✗ No files downloaded successfully[/red]")


# =============================================================================
# CLI
# =============================================================================

app = typer.Typer(
    name="purdue-collection-downloader",
    help="Download manuscripts from Purdue Digital Commons collections",
    add_completion=False
)


@app.command()
def download(
    url: Optional[List[str]] = typer.Option(None, "--url", "-u", help="Collection URL(s) to download"),
    url_file: Optional[Path] = typer.Option(None, "--url-file", "-f", help="Text file containing URLs"),
    output: Path = typer.Option(None, "--output", "-o", help="Output directory"),
    username: Optional[str] = typer.Option(None, "--username", help="Purdue username for authentication"),
    password: Optional[str] = typer.Option(None, "--password", help="Purdue password for authentication"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be downloaded without downloading"),
):
    """
    Download manuscripts from Purdue Digital Commons collections.

    Examples:
        # Single collection
        download --url "https://docs.lib.purdue.edu/roadschool/"

        # Multiple collections
        download --url "https://docs.lib.purdue.edu/etd/" --url "https://docs.lib.purdue.edu/chempubs/"

        # From file
        download --url-file urls.txt --output ~/Downloads
    """
    console.print("\n[bold]Purdue Digital Commons Downloader[/bold]\n")

    # Collect URLs
    all_urls = []

    if url:
        all_urls.extend(url)

    if url_file:
        if not url_file.exists():
            console.print(f"[red]Error: URL file not found: {url_file}[/red]")
            raise typer.Exit(code=1)

        file_urls = parse_url_file(url_file)
        all_urls.extend(file_urls)

    if not all_urls:
        console.print("[red]Error: No URLs provided. Use --url or --url-file[/red]")
        raise typer.Exit(code=1)

    # Deduplicate and validate
    all_urls = deduplicate_urls(all_urls)
    valid_urls = [u for u in all_urls if validate_purdue_url(u)]

    if not valid_urls:
        console.print("[red]Error: No valid Purdue Digital Commons URLs found[/red]")
        raise typer.Exit(code=1)

    # Determine output directory
    if not output:
        config = load_config()
        output = Path(config.get('download_directory', DEFAULT_CONFIG['download_directory']))

    output.mkdir(parents=True, exist_ok=True)

    # Display configuration
    console.print(f"Collections: {len(valid_urls)} URL(s)")
    console.print(f"Output:      {output}")
    if dry_run:
        console.print("[yellow]Mode:        DRY RUN (no downloads)[/yellow]")
    console.print()

    # Dry run mode
    if dry_run:
        console.print("[bold]URLs to process:[/bold]")
        for idx, u in enumerate(valid_urls, 1):
            console.print(f"  {idx}. {u}")
        console.print("\n[yellow]Dry run complete. Use without --dry-run to download.[/yellow]")
        return

    # Download
    try:
        downloader = PurdueCollectionDownloader(
            output_dir=output,
            username=username,
            password=password,
            verbose=verbose
        )

        results = downloader.download_collections(valid_urls)
        downloader.print_summary(results)

    except KeyboardInterrupt:
        console.print("\n[yellow]Download interrupted by user[/yellow]")
        raise typer.Exit(code=130)
    except Exception as e:
        console.print(f"\n[red]Error:[/red] {e}")
        if verbose:
            import traceback
            console.print(traceback.format_exc())
        raise typer.Exit(code=1)


@app.command()
def version():
    """Show version information."""
    console.print("\n[bold]Purdue Digital Commons Downloader[/bold]")
    console.print("Version: 2.0.0 (Consolidated)")
    console.print("\nFeatures:")
    console.print("  • Generic collection support")
    console.print("  • Multi-URL processing")
    console.print("  • Rich terminal output")
    console.print("  • Direct HTTP + browser fallback")
    console.print("  • Cross-platform (macOS, Linux, WSL)\n")


def main():
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
