# Windows Setup Script for ePubs Accessibility Enhancement Project
# Run this script in PowerShell to set up the project

Write-Host "Setting up ePubs Accessibility Enhancement Project..." -ForegroundColor Green

# Check if Python is installed
Write-Host "Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "Found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "Python not found! Please install Python 3.9+ from https://python.org" -ForegroundColor Red
    exit 1
}

# Check if Tesseract is available
Write-Host "Checking Tesseract installation..." -ForegroundColor Yellow
try {
    $tesseractVersion = tesseract --version 2>&1 | Select-Object -First 1
    Write-Host "Found: $tesseractVersion" -ForegroundColor Green
} catch {
    Write-Host "Tesseract not found!" -ForegroundColor Red
    Write-Host "Install options:" -ForegroundColor Yellow
    Write-Host "1. Chocolatey: choco install tesseract" -ForegroundColor Cyan
    Write-Host "2. Manual: https://github.com/UB-Mannheim/tesseract/wiki" -ForegroundColor Cyan
    $continue = Read-Host "Continue anyway? (y/N)"
    if ($continue -ne "y" -and $continue -ne "Y") {
        exit 1
    }
}

# Create virtual environment
Write-Host "Creating virtual environment..." -ForegroundColor Yellow
if (Test-Path "venv") {
    Write-Host "Virtual environment already exists, using existing one." -ForegroundColor Cyan
} else {
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Install dependencies
Write-Host "Installing project dependencies..." -ForegroundColor Yellow
pip install --upgrade pip
pip install -e .[all]

if ($LASTEXITCODE -eq 0) {
    Write-Host "" -ForegroundColor Green
    Write-Host "Setup completed successfully!" -ForegroundColor Green
    Write-Host "" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Test the installation: epubs --help" -ForegroundColor Cyan
    Write-Host "2. Try with a sample PDF: epubs enhance sample.pdf" -ForegroundColor Cyan
    Write-Host "" -ForegroundColor Green
    Write-Host "To use the project in the future:" -ForegroundColor Yellow
    Write-Host "1. Navigate to project directory" -ForegroundColor Cyan
    Write-Host "2. Activate environment: .\venv\Scripts\Activate.ps1" -ForegroundColor Cyan
    Write-Host "3. Use epubs commands" -ForegroundColor Cyan
} else {
    Write-Host "Installation failed! Check the error messages above." -ForegroundColor Red
    exit 1
}