# ePubs Scraper

A specialized document acquisition tool for downloading PDFs from Purdue University Library resources.

## Features

- **Automated PDF Downloading**: Downloads PDFs from Purdue Library document repositories
- **Intelligent Path Generation**: Creates appropriate directory structures based on URL patterns
- **Batch Processing**: Processes multiple URLs in parallel or sequentially
- **WSL Compatibility**: Special handling for Windows Subsystem for Linux environments
- **Robust Error Handling**: Automatic retries with exponential backoff and thorough logging
- **Session Management**: Optimized HTTP sessions for improved performance

## Installation

### Prerequisites

- Python 3.8 or higher
- Chrome browser (or supports Firefox as fallback)
- ChromeDriver (automatically downloaded if not present)

### Setup

1. Install dependencies:
   ```bash
   pip install selenium requests urllib3 tqdm
   ```

2. For WSL users, mount the S: drive if necessary:
   ```bash
   sudo mount -t drvfs S: /mnt/s
   ```

## Usage

### Single URL Processing

Download PDFs from a single URL:

```bash
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va
```

### Batch Processing

Process multiple URLs from a file:

```bash
python -m scraper.purdue_downloader --file urls.txt
```

### Custom Download Directory

Specify a custom download location:

```bash
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va --download-dir /path/to/downloads
```

### Parallel Processing

Control the number of parallel workers for batch processing:

```bash
python -m scraper.purdue_downloader --file urls.txt --workers 5
```

### Additional Options

- `--username` - Specify Purdue username for login
- `--shared-driver` - Use a shared WebDriver instance for sequential URL processing
- `--no-shared-driver` - Create a new WebDriver instance for each URL
- `--debug` - Enable debug logging

## File Structure

- **purdue_downloader.py**: Main script for downloading PDFs from Purdue Library
- **test_path.py**: Test script for path generation functionality
- **test_full_path.py**: Comprehensive test for full path generation and filename formats

## Integration with Automation

This scraper is designed to work with the automation workflow in the `/automation` directory. The automation scripts will call the scraper to download documents and then pass them to the processor for enhancement.

## Known Limitations

- Requires Chrome browser installation for optimal performance
- May require authentication for accessing some Purdue Library resources
- WSL users need to ensure proper mounting of Windows drives