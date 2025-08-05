# Document Scraper

Web scraping tool for downloading academic PDFs from Purdue University Library repositories.

## Features

- Automated PDF discovery and download
- Cross-platform support (macOS/WSL)
- Duplicate detection and smart organization
- Authentication support

## Usage

```bash
# Single repository download
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va

# Batch processing from file
python -m scraper.purdue_downloader --file urls.txt

# With authentication
python -m scraper.purdue_downloader --url <repository_url> --username <purdue_id>
```

## Requirements

- Python 3.9+
- Chrome/Chromium browser
- ChromeDriver (auto-downloaded)

## Integration

Integrates with the processing pipeline for end-to-end document enhancement workflows.
