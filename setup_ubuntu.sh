#!/bin/bash
# Ubuntu Development Environment Setup for ePubs Accessibility Enhancement
# Supports Ubuntu 20.04, 22.04, and newer versions
# Run with: chmod +x setup_ubuntu.sh && ./setup_ubuntu.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Detect Ubuntu version and architecture
detect_platform() {
    log_info "Detecting Ubuntu platform..."
    
    local os_release
    if [[ -f /etc/os-release ]]; then
        source /etc/os-release
        log_success "Operating System: $NAME $VERSION"
        echo "Distribution ID: $ID"
        echo "Version ID: $VERSION_ID"
        
        # Check if it's actually Ubuntu
        if [[ "$ID" != "ubuntu" ]]; then
            log_warning "This script is designed for Ubuntu. Detected: $NAME"
            log_warning "Proceeding anyway, but some packages might not be available."
        fi
    else
        log_error "/etc/os-release not found. Cannot determine OS version."
        exit 1
    fi
    
    local machine=$(uname -m)
    echo "Architecture: $machine"
    
    # Check for GPU availability
    if command -v nvidia-smi &> /dev/null; then
        log_success "NVIDIA GPU detected"
        export GPU_AVAILABLE=true
    else
        log_info "No NVIDIA GPU detected"
        export GPU_AVAILABLE=false
    fi
}

# Update package lists
update_packages() {
    log_info "Updating package lists..."
    
    sudo apt update || {
        log_error "Failed to update package lists"
        exit 1
    }
    
    log_success "Package lists updated"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies..."
    
    # Core dependencies for PDF processing and OCR
    local deps=(
        "python3.11"              # Python 3.11
        "python3.11-venv"         # Virtual environment support
        "python3.11-dev"          # Python development headers
        "python3-pip"             # Python package manager
        "tesseract-ocr"           # OCR engine
        "tesseract-ocr-eng"       # English language data
        "tesseract-ocr-fra"       # French language data (common)
        "tesseract-ocr-deu"       # German language data (common)
        "tesseract-ocr-spa"       # Spanish language data (common)
        "poppler-utils"           # PDF utilities (pdfinfo, pdftotext, etc.)
        "imagemagick"             # Image processing
        "ghostscript"             # PostScript/PDF interpreter
        "libmagickwand-dev"       # ImageMagick development libraries
        "git"                     # Version control
        "build-essential"         # Compilation tools (gcc, make, etc.)
        "cmake"                   # Build system
        "pkg-config"              # Package configuration
        "libffi-dev"              # Foreign Function Interface library
        "libssl-dev"              # SSL development libraries
        "libjpeg-dev"             # JPEG development libraries
        "libpng-dev"              # PNG development libraries
        "libtiff-dev"             # TIFF development libraries
        "zlib1g-dev"              # Compression library
        "libxml2-dev"             # XML parsing library
        "libxslt1-dev"            # XSLT processing library
        "libcairo2-dev"           # Cairo graphics library
        "libgirepository1.0-dev"  # GObject introspection
        "libpoppler-dev"          # Poppler development libraries
        "libtesseract-dev"        # Tesseract development libraries
        "curl"                    # HTTP client
        "wget"                    # File downloader
        "unzip"                   # Archive extraction
    )
    
    # GPU-specific dependencies
    if [[ "$GPU_AVAILABLE" == "true" ]]; then
        deps+=(
            "nvidia-cuda-toolkit"     # CUDA toolkit
            "nvidia-cuda-dev"         # CUDA development
        )
        log_info "Adding GPU acceleration dependencies"
    fi
    
    # Version-specific packages
    if [[ "${VERSION_ID}" == "22.04" ]] || [[ "${VERSION_ID}" == "24.04" ]]; then
        deps+=(
            "python3.11-distutils"    # Distutils for newer Python
        )
    fi
    
    log_info "Installing ${#deps[@]} system packages..."
    
    # Install packages with retry logic
    local max_retries=3
    local retry_count=0
    
    while [[ $retry_count -lt $max_retries ]]; do
        if sudo apt install -y "${deps[@]}"; then
            log_success "System dependencies installed successfully"
            break
        else
            ((retry_count++))
            log_warning "Installation attempt $retry_count failed. Retrying..."
            if [[ $retry_count -eq $max_retries ]]; then
                log_error "Failed to install system dependencies after $max_retries attempts"
                return 1
            fi
            sleep 5
        fi
    done
}

# Configure Tesseract
configure_tesseract() {
    log_info "Configuring Tesseract OCR..."
    
    # Verify Tesseract installation
    if command -v tesseract &> /dev/null; then
        local tess_version=$(tesseract --version 2>&1 | head -n1)
        log_success "Tesseract configured: $tess_version"
        
        # Find tessdata directory
        local tessdata_dir=$(tesseract --print-parameters 2>/dev/null | grep tessdata-dir | cut -d' ' -f2 || echo "/usr/share/tesseract-ocr/4.00/tessdata")
        echo "  Tessdata directory: $tessdata_dir"
        
        # List available languages
        local languages=$(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' ' ')
        echo "  Available languages: $languages"
        
        # Set environment variable
        echo "export TESSDATA_PREFIX='$tessdata_dir'" >> ~/.bashrc
        export TESSDATA_PREFIX="$tessdata_dir"
    else
        log_error "Tesseract installation verification failed"
        return 1
    fi
}

# Setup Python environment
setup_python() {
    log_info "Setting up Python environment..."
    
    # Verify Python 3.11 installation
    if command -v python3.11 &> /dev/null; then
        local python_version=$(python3.11 --version)
        log_success "Python available: $python_version"
    else
        log_error "Python 3.11 not found. Installation may have failed."
        return 1
    fi
    
    # Create virtual environment
    log_info "Creating Python virtual environment..."
    python3.11 -m venv venv
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip setuptools wheel
    
    log_success "Python virtual environment created and activated"
}

# Install Python dependencies
install_python_deps() {
    log_info "Installing Python dependencies..."
    
    # Ensure virtual environment is activated
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_info "Activating virtual environment..."
        source venv/bin/activate
    fi
    
    # Install the package in development mode
    if [[ -f "pyproject.toml" ]]; then
        log_info "Installing package with optional dependencies..."
        
        # Choose install command based on GPU availability
        local install_cmd
        if [[ "$GPU_AVAILABLE" == "true" ]]; then
            install_cmd="pip install -e .[ml,advanced,dev]"
            log_info "Installing with GPU acceleration support"
        else
            install_cmd="pip install -e .[ml,advanced,dev]"
            log_info "Installing with CPU-only support"
        fi
        
        eval "$install_cmd" || {
            log_error "Failed to install Python dependencies"
            return 1
        }
        
        log_success "Python dependencies installed successfully"
    else
        log_error "pyproject.toml not found. Are you in the project directory?"
        return 1
    fi
}

# Configure GPU acceleration
configure_gpu_acceleration() {
    if [[ "$GPU_AVAILABLE" != "true" ]]; then
        log_info "Skipping GPU configuration (no NVIDIA GPU detected)"
        return 0
    fi
    
    log_info "Configuring GPU acceleration..."
    
    source venv/bin/activate
    
    # Install PyTorch with CUDA support
    log_info "Installing PyTorch with CUDA support..."
    
    # Detect CUDA version
    local cuda_version=""
    if command -v nvcc &> /dev/null; then
        cuda_version=$(nvcc --version | grep "release" | sed 's/.*release //' | sed 's/,.*//')
        log_info "CUDA version detected: $cuda_version"
    fi
    
    # Install PyTorch with appropriate CUDA version
    if [[ -n "$cuda_version" ]]; then
        if [[ "$cuda_version" == "11."* ]]; then
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
        elif [[ "$cuda_version" == "12."* ]]; then
            pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
        else
            log_warning "Unsupported CUDA version, installing CPU-only PyTorch"
            pip install torch torchvision torchaudio
        fi
    else
        log_warning "Could not detect CUDA version, installing CPU-only PyTorch"
        pip install torch torchvision torchaudio
    fi
    
    # Set environment variables for optimal GPU performance
    {
        echo ""
        echo "# GPU acceleration optimizations for ePubs processing"
        echo "export CUDA_VISIBLE_DEVICES=0"
        echo "export OMP_NUM_THREADS=4"
        echo "export MKL_NUM_THREADS=4"
        echo "export PYTORCH_CUDA_ALLOC_CONF=max_split_size_mb:128"
    } >> ~/.bashrc
    
    log_success "GPU acceleration configured"
}

# Configure system optimizations
configure_system_optimizations() {
    log_info "Configuring system optimizations..."
    
    # Set environment variables for optimal performance
    {
        echo ""
        echo "# System optimizations for ePubs processing"
        echo "export PYTHONUNBUFFERED=1"
        echo "export PYTHONDONTWRITEBYTECODE=1"
        echo "export OMP_NUM_THREADS=\$(nproc)"
        echo "export MKL_NUM_THREADS=\$(nproc)"
        echo "export OPENBLAS_NUM_THREADS=\$(nproc)"
    } >> ~/.bashrc
    
    log_success "System optimizations configured"
}

# Create cache directories
setup_cache_dirs() {
    log_info "Setting up cache directories..."
    
    local cache_dirs=(
        "$HOME/.cache/epubs"
        "$HOME/.cache/epubs/ml_models"
        "$HOME/.cache/epubs/temp"
        "$HOME/.epubs/logs"
    )
    
    for dir in "${cache_dirs[@]}"; do
        mkdir -p "$dir"
        log_success "Created cache directory: $dir"
    done
}

# Configure systemd service (optional)
setup_systemd_service() {
    log_info "Setting up systemd service template..."
    
    local service_dir="$HOME/.config/systemd/user"
    mkdir -p "$service_dir"
    
    cat > "$service_dir/epub-processor.service" << 'EOF'
[Unit]
Description=ePubs Accessibility Enhancement Watch Service
After=network.target

[Service]
Type=simple
WorkingDirectory=%h/work/ePubs_Main
Environment=PATH=%h/work/ePubs_Main/venv/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=%h/work/ePubs_Main/venv/bin/python -m processor.unified_project.src.main watch /path/to/input/directory
Restart=on-failure
RestartSec=5

[Install]
WantedBy=default.target
EOF
    
    log_success "Systemd service template created at ~/.config/systemd/user/epub-processor.service"
    log_info "To use: systemctl --user enable epub-processor.service"
}

# Verify installation
verify_installation() {
    log_info "Verifying installation..."
    
    local errors=0
    
    # Check system tools
    local tools=("tesseract" "pdfinfo" "convert" "gs" "python3.11")
    for tool in "${tools[@]}"; do
        if command -v "$tool" &> /dev/null; then
            log_success "$tool is available"
        else
            log_error "$tool is not available"
            ((errors++))
        fi
    done
    
    # Check Python packages
    source venv/bin/activate 2>/dev/null || {
        log_error "Virtual environment not found"
        ((errors++))
        return $errors
    }
    
    local python_packages=("tesseract" "PyPDF2" "typer" "rich")
    for package in "${python_packages[@]}"; do
        if python -c "import $package" 2>/dev/null; then
            log_success "Python package '$package' is available"
        else
            log_error "Python package '$package' is not available"
            ((errors++))
        fi
    done
    
    # Test GPU availability if configured
    if [[ "$GPU_AVAILABLE" == "true" ]]; then
        if python -c "import torch; print(f'CUDA available: {torch.cuda.is_available()}')" 2>/dev/null; then
            log_success "GPU acceleration test passed"
        else
            log_warning "GPU acceleration test failed (but CPU processing will work)"
        fi
    fi
    
    # Test basic functionality
    log_info "Testing basic functionality..."
    if python -c "from processor.unified_project.src.utils.platform_detection import get_platform_info; print('Platform detection working')" 2>/dev/null; then
        log_success "Platform detection working"
    else
        log_error "Platform detection failed"
        ((errors++))
    fi
    
    return $errors
}

# Print success message and next steps
print_success() {
    echo ""
    echo "🐧 Ubuntu development environment setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Reload shell configuration: source ~/.bashrc"
    echo "2. Activate the virtual environment: source venv/bin/activate"
    echo "3. Test the installation: python -m processor.unified_project.src.main --help"
    echo "4. Run platform detection: python -c \"from processor.unified_project.src.utils.platform_detection import get_platform_info; import json; print(json.dumps(get_platform_info(), indent=2))\""
    if [[ "$GPU_AVAILABLE" == "true" ]]; then
        echo "5. Test GPU acceleration: python -c \"import torch; print(f'CUDA available: {torch.cuda.is_available()}, Device count: {torch.cuda.device_count()}')\""
    fi
    echo ""
    echo "Configuration files updated:"
    echo "  ~/.bashrc - Environment variables and PATH"
    if [[ -f "$HOME/.config/systemd/user/epub-processor.service" ]]; then
        echo "  ~/.config/systemd/user/epub-processor.service - Systemd service template"
    fi
    echo ""
    echo "Cache directories created:"
    echo "  ~/.cache/epubs/ - ML models and temporary files"
    echo "  ~/.epubs/logs/ - Application logs"
    echo ""
}

# Main execution
main() {
    echo "🐧 ePubs Accessibility Enhancement - Ubuntu Setup"
    echo "=============================================="
    echo ""
    
    detect_platform
    update_packages
    install_system_deps
    configure_tesseract
    setup_python
    install_python_deps
    configure_gpu_acceleration
    configure_system_optimizations
    setup_cache_dirs
    setup_systemd_service
    
    local verification_errors
    verification_errors=$(verify_installation)
    
    if [[ $verification_errors -eq 0 ]]; then
        print_success
        exit 0
    else
        log_error "Setup completed with $verification_errors errors"
        echo ""
        echo "Please review the errors above and re-run the setup script if needed."
        exit 1
    fi
}

# Run main function
main "$@"