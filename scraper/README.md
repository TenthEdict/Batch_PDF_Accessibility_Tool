# Document Acquisition Scraper

A specialized web scraping tool for downloading academic PDFs from Purdue University Library digital repositories, designed to integrate seamlessly with the ePubs accessibility enhancement pipeline.

## 🎯 Features

- **🔍 Automated PDF Discovery**: Intelligent parsing of Purdue Library document repositories
- **📁 Smart Organization**: Creates logical directory structures based on publication patterns
- **⚡ Parallel Downloads**: Multi-threaded processing for efficient batch operations
- **🔄 Robust Error Handling**: Automatic retries with exponential backoff and comprehensive logging
- **🌐 Cross-Platform**: WSL compatibility with proper drive mounting support
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

## 🏗️ Integration

### With Enhancement Pipeline

```bash
# Download and immediately process
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
- **Session reuse** for HTTP connections
- **Parallel processing** with worker pools
- **Memory-efficient** streaming downloads
- **Smart rate limiting** to avoid blocking

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
- **Single document**: ~2-5 seconds
- **Batch (10 documents)**: ~30-60 seconds
- **Large collections (100+)**: Scales linearly with workers

### Resource Usage
- **Memory**: ~50-100MB per worker
- **Network**: Respects server rate limits
- **Storage**: Minimal temporary files

## 🔗 Related Components

- **[Main Project](../README.md)**: Overall project documentation
- **[Processor](../processor/unified_project/README.md)**: Document enhancement engine
- **[Batch Processing](../advanced_batch_processor.py)**: Automated workflows

For integration with the complete accessibility enhancement pipeline, see the main project documentation.