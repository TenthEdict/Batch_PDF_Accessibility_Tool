# ePubs Accessibility Enhancement Project

A comprehensive toolkit for enhancing document accessibility across academic and historical publications. The system provides specialized tools for PDF processing, OCR enhancement, and accessibility compliance validation.

## Quick Start

### Windows Users

1. **Install Required Software**
   ```powershell
   # Option 1: Using Chocolatey (easiest)
   # First install Chocolatey from https://chocolatey.org/install
   choco install python tesseract

   # Option 2: Manual installation
   # Download Python from python.org
   # Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. **Set Up the Project**
   ```powershell
   # Clone the repository
   git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
   cd ePubs_Main

   # Create virtual environment
   python -m venv venv
   .\venv\Scripts\activate

   # Install the toolkit
   pip install -e .[all]
   ```

### Mac/Linux Users

1. **Install Required Software**
   ```bash
   # macOS (using Homebrew)
   brew install python tesseract poppler

   # Ubuntu/Debian
   sudo apt-get install python3 python3-pip tesseract-ocr poppler-utils
   ```

2. **Set Up the Project**
   ```bash
   # Clone the repository
   git clone https://github.itap.purdue.edu/schipp0/ePubs_Main.git
   cd ePubs_Main

   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate

   # Install the toolkit
   pip install -e .[all]
   ```

## System Requirements

- **Python**: Version 3.9 or newer
- **Tesseract OCR**: For text recognition in images and scanned PDFs
- **Poppler** (Mac/Linux only): For PDF processing utilities


## Quick Test

After installation, test that everything works:

```bash
# Test the installation
epubs --help

# Test with a sample PDF (if you have one)
epubs enhance sample.pdf
```

## Batch Processing

To process multiple files at once, use the batch processing command:

### Mac/Linux
```bash
python -m processor.unified_project.src.main batch-process data/input data/output --verbose
```

### Windows
```powershell
python -m processor.unified_project.src.main batch-process data/input data/output --verbose
```

## Common Issues

### Windows

**"tesseract not found" error:**
- Make sure Tesseract is installed and added to your PATH
- Try restarting your command prompt after installation
- If using manual installation, add the Tesseract folder to your Windows PATH environment variable

**Permission errors when creating virtual environment:**
- Run PowerShell as Administrator
- Or try: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

### All Platforms

**"pip install" fails:**
- Make sure you're using Python 3.9 or newer: `python --version`
- Try updating pip first: `pip install --upgrade pip`
- On some systems, use `python3` instead of `python`

**Out of memory errors:**
- Large PDFs require significant RAM
- Try processing smaller files first
- Consider closing other applications

## Need Help?

- Check the project documentation for detailed guides
- Submit issues on the project repository
- Make sure all system requirements are properly installed