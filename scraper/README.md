# Document Acquisition Scraper

A specialized web scraping tool for downloading academic PDFs from Purdue University Library digital repositories, designed to integrate seamlessly with the ePubs accessibility enhancement pipeline.

## 🎯 Features

- **🔍 Automated PDF Discovery**: Intelligent parsing of Purdue Library document repositories
- **📁 Smart Organization**: Creates logical directory structures based on publication patterns
- **⚡ Optimized Downloads**: Prioritized direct HTTP downloads with browser fallback for 3-5x speed improvement
- **🌐 Cross-Platform**: Full macOS and WSL support with S: drive coordination
- **🔄 Robust Error Handling**: Automatic retries with exponential backoff and comprehensive logging
- **🚫 Duplicate Detection**: Intelligent tracking to avoid redownloading existing documents
- **🔐 Authentication Support**: Handles Purdue login requirements automatically

## 🚀 Installation

### Prerequisites

- **Python 3.9+** (matches main project requirements)
- **Chrome/Chromium browser** (Firefox fallback available)
- **ChromeDriver** (auto-downloaded if missing)

### Setup

```bash
# Install as part of the main project
pip install -e .[web]

# Or install scraper dependencies directly
pip install selenium requests urllib3 tqdm beautifulsoup4
```

### WSL Configuration (Windows Users)

```bash
# Mount network drives if needed
sudo mount -t drvfs S: /mnt/s
```

## 💻 Usage

### CLI Interface

```bash
# Single repository download
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va

# Using the module directly
python -m scraper.purdue_downloader --url https://docs.lib.purdue.edu/modvis/2024/va
```

### Batch Processing

```bash
# Process multiple URLs from file
epubs-scrape --file urls.txt

# Parallel processing with custom workers
epubs-scrape --file urls.txt --workers 8

# Custom download directory
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va --download-dir ./downloads
```

### Authentication

```bash
# With Purdue credentials
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va --username your_username

# Interactive login prompt will appear if credentials needed
```

### Advanced Options

```bash
# Debug mode with verbose logging
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va --debug

# Shared driver for sequential processing (memory efficient)
epubs-scrape --file urls.txt --shared-driver

# New driver per URL (more stable for parallel)
epubs-scrape --file urls.txt --no-shared-driver --workers 4
```

### Document Access Workflow

The scraper uses an enhanced workflow to access manuscript PDFs:

1. **Collection Page**: Navigate to the document collection page
2. **Authentication**: Handle Purdue login requirements (manual or automatic)
3. **Document Pages**: Extract individual document page URLs from collections
4. **Edit Access**: Click "Edit Event" or "Edit Submission" buttons (adaptive detection)
5. **View Revisions**: Navigate to revision history via editor interface
6. **Manuscript Download**: Extract and download manuscript PDFs (not cover pages)
7. **Smart Naming**: Generate filenames using manuscript numbers: `manuscriptNumber_series_pathComponents.pdf`

This workflow ensures access to the actual manuscript content rather than just cover pages or abstracts.

## 🏗️ Integration

### With Enhancement Pipeline

```bash
# Unified pipeline: scrape and process in one command
python processor/unified_project/src/orchestration/scrape_and_process.py \
  --url https://docs.lib.purdue.edu/modvis/2024/va \
  --mode academic

# Traditional approach: download then process
epubs-scrape --url https://docs.lib.purdue.edu/modvis/2024/va
python advanced_batch_processor.py  # Auto-detects downloaded files

# Or use the cloud batch processor
./cloud_batch_process.sh  # Includes download step
```

### Project Integration

The scraper integrates with:
- **Main CLI** (`epubs-scrape` command)
- **Batch Processors** (automatic file detection)
- **Cloud Workflows** (via batch scripts)
- **Directory Processing** (outputs to standard locations)

## 📂 Directory Structure

```
scraper/
├── purdue_downloader.py    # Main downloader implementation
├── test_path.py           # Path generation testing
├── test_full_path.py      # Comprehensive path testing
├── config.ini             # Configuration settings
└── README.md              # This file
```

### Output Structure

```
downloads/
├── modvis/2024/va/        # Organized by publication hierarchy
│   ├── document1.pdf
│   ├── document2.pdf
│   └── ...
└── other_collections/
```

## ⚙️ Configuration

### config.ini

```ini
[scraper]
default_workers = 4
retry_attempts = 3
download_timeout = 300
user_agent = ePubs-Scraper/2.0

[paths]
default_download_dir = ./downloads
temp_dir = ./temp

[selenium]
implicit_wait = 10
page_load_timeout = 30
```

## 🔧 Technical Details

### Error Handling
- **Exponential backoff** for transient failures
- **Automatic retries** with configurable attempts
- **Graceful degradation** for authentication issues
- **Comprehensive logging** for troubleshooting

### Performance Optimizations
- **Direct HTTP Priority**: Downloads prioritize direct HTTP requests over browser automation (3-5x faster)
- **Cross-Platform ChromeDriver**: Optimized driver management for macOS and WSL environments
- **Session reuse** for HTTP connections with connection pooling
- **Parallel processing** with configurable worker pools
- **Memory-efficient** streaming downloads with progress tracking
- **Smart rate limiting** to avoid blocking
- **Intelligent duplicate detection** to prevent redownloading existing files
- **S: Drive coordination** for seamless cross-platform file management

### Browser Automation
- **Headless operation** by default
- **Multiple browser support** (Chrome primary, Firefox fallback)
- **Dynamic element waiting** for reliable interaction
- **Cookie/session management** for authentication

## 🧪 Testing

```bash
# Test path generation
python scraper/test_path.py

# Full integration test
python scraper/test_full_path.py

# Run with pytest
pytest scraper/ -v
```

## 🔍 Troubleshooting

### Common Issues

**ChromeDriver not found:**
```bash
# The scraper auto-downloads, but manual installation:
pip install webdriver-manager
```

**Authentication failures:**
```bash
# Ensure correct Purdue credentials
epubs-scrape --url <url> --username <purdue_id> --debug
```

**WSL path issues:**
```bash
# Verify drive mounting
ls /mnt/s  # Should show Windows S: drive contents
```

### Debug Mode

```bash
# Enable detailed logging
epubs-scrape --url <url> --debug
```

## 📊 Performance

### Benchmarks
- **Single document (Direct HTTP)**: ~2-5 seconds
- **Single document (Browser fallback)**: ~10-15 seconds
- **Batch (10 documents)**: ~20-50 seconds (with optimized downloads)
- **Large collections (100+)**: Scales linearly with workers
- **Duplicate detection lookup**: <100ms per file

### Resource Usage
- **Memory**: ~50-100MB per worker
- **Network**: Respects server rate limits
- **Storage**: Minimal temporary files

## 🔗 Related Components

- **[Main Project](../README.md)**: Overall project documentation
- **[Processor](../processor/unified_project/README.md)**: Document enhancement engine
- **[Batch Processing](../advanced_batch_processor.py)**: Automated workflows

For integration with the complete accessibility enhancement pipeline, see the main project documentation.