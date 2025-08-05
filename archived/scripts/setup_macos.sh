#!/bin/bash
# macOS Development Environment Setup for ePubs Accessibility Enhancement
# Optimized for Apple Silicon (M1/M2/M3/M4) and Intel Macs
# Run with: chmod +x setup_macos.sh && ./setup_macos.sh

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

# Detect platform
detect_platform() {
    log_info "Detecting macOS platform..."
    
    local machine=$(uname -m)
    local os_version=$(sw_vers -productVersion)
    
    echo "macOS Version: $os_version"
    echo "Architecture: $machine"
    
    if [[ "$machine" == "arm64" ]]; then
        export APPLE_SILICON=true
        local chip=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || echo "Apple Silicon")
        log_success "Apple Silicon detected: $chip"
    else
        export APPLE_SILICON=false
        log_info "Intel Mac detected"
    fi
}

# Check if Homebrew is installed
check_homebrew() {
    log_info "Checking Homebrew installation..."
    
    if command -v brew &> /dev/null; then
        log_success "Homebrew is already installed"
        local brew_version=$(brew --version | head -n1)
        echo "  $brew_version"
        return 0
    else
        log_warning "Homebrew not found. Installing..."
        install_homebrew
    fi
}

# Install Homebrew
install_homebrew() {
    log_info "Installing Homebrew..."
    
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    
    # Add Homebrew to PATH for Apple Silicon
    if [[ "$APPLE_SILICON" == "true" ]]; then
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    else
        echo 'eval "$(/usr/local/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/usr/local/bin/brew shellenv)"
    fi
    
    log_success "Homebrew installed successfully"
}

# Install system dependencies
install_system_deps() {
    log_info "Installing system dependencies via Homebrew..."
    
    # Core dependencies for PDF processing and OCR
    local deps=(
        "tesseract"           # OCR engine
        "tesseract-lang"      # Language data for Tesseract
        "poppler"             # PDF utilities
        "imagemagick"         # Image processing
        "ghostscript"         # PostScript/PDF interpreter  
        "python@3.11"         # Python 3.11
        "git"                 # Version control
        "cmake"               # Build system (needed for some Python packages)
        "pkg-config"          # Package configuration
        "jpeg"                # JPEG support
        "libpng"              # PNG support
        "libtiff"             # TIFF support
        "zlib"                # Compression library
    )
    
    # Apple Silicon specific dependencies
    if [[ "$APPLE_SILICON" == "true" ]]; then
        deps+=(
            "llvm"            # For better compilation on Apple Silicon
            "libomp"          # OpenMP for parallel processing
        )
        log_info "Adding Apple Silicon optimized dependencies"
    fi
    
    for dep in "${deps[@]}"; do
        log_info "Installing $dep..."
        if brew list "$dep" &>/dev/null; then
            log_success "$dep already installed"
        else
            brew install "$dep" || {
                log_error "Failed to install $dep"
                return 1
            }
        fi
    done
    
    log_success "System dependencies installed successfully"
}

# Configure Tesseract
configure_tesseract() {
    log_info "Configuring Tesseract OCR..."
    
    local tessdata_dir
    if [[ "$APPLE_SILICON" == "true" ]]; then
        tessdata_dir="/opt/homebrew/share/tessdata"
    else
        tessdata_dir="/usr/local/share/tessdata"
    fi
    
    # Verify Tesseract installation
    if command -v tesseract &> /dev/null; then
        local tess_version=$(tesseract --version 2>&1 | head -n1)
        log_success "Tesseract configured: $tess_version"
        echo "  Tessdata directory: $tessdata_dir"
        
        # List available languages
        local languages=$(tesseract --list-langs 2>/dev/null | tail -n +2 | tr '\n' ' ')
        echo "  Available languages: $languages"
    else
        log_error "Tesseract installation verification failed"
        return 1
    fi
    
    # Set environment variable for Python applications
    echo "export TESSDATA_PREFIX='$tessdata_dir'" >> ~/.zprofile
    export TESSDATA_PREFIX="$tessdata_dir"
}

# Install Python and create virtual environment
setup_python() {
    log_info "Setting up Python environment..."
    
    # Verify Python 3.11 installation
    if command -v python3.11 &> /dev/null; then
        local python_version=$(python3.11 --version)
        log_success "Python available: $python_version"
    else
        log_error "Python 3.11 not found. Please install via Homebrew"
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
        log_info "Installing package with all optional dependencies..."
        
        # Install base package with all optional dependencies for macOS
        local install_cmd="pip install -e ."
        if [[ "$APPLE_SILICON" == "true" ]]; then
            install_cmd="pip install -e .[ml,apple,advanced,dev]"
            log_info "Installing with Apple Silicon optimizations"
        else
            install_cmd="pip install -e .[ml,advanced,dev]"
            log_info "Installing with Intel Mac optimizations"
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

# Configure Apple Silicon optimizations
configure_apple_silicon() {
    if [[ "$APPLE_SILICON" != "true" ]]; then
        log_info "Skipping Apple Silicon optimizations (Intel Mac detected)"
        return 0
    fi
    
    log_info "Configuring Apple Silicon optimizations..."
    
    # Set environment variables for optimal performance
    {
        echo ""
        echo "# Apple Silicon optimizations for ePubs processing"
        echo "export PYTORCH_ENABLE_MPS_FALLBACK=1"
        echo "export OMP_NUM_THREADS=6"  # Optimal for M-series chips
        echo "export MKL_NUM_THREADS=6"
        echo "export VECLIB_MAXIMUM_THREADS=6"
        echo "export MLX_METAL_DEBUG=0"  # Disable debug for performance
    } >> ~/.zprofile
    
    # Try to install MLX if available
    log_info "Attempting to install MLX for Apple Silicon acceleration..."
    source venv/bin/activate
    
    # MLX installation for Apple Silicon
    if pip install mlx mlx-vlm 2>/dev/null; then
        log_success "MLX installed for Apple Silicon acceleration"
    else
        log_warning "MLX installation failed - will fall back to CPU processing"
    fi
    
    log_success "Apple Silicon optimizations configured"
}

# Create cache directories
setup_cache_dirs() {
    log_info "Setting up cache directories..."
    
    local cache_dirs=(
        "$HOME/.epubs/cache"
        "$HOME/.cache/epubs/ml_models"
        "$HOME/.cache/epubs/apple_models"
        "$HOME/.epubs/logs"
    )
    
    for dir in "${cache_dirs[@]}"; do
        mkdir -p "$dir"
        log_success "Created cache directory: $dir"
    done
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
    
    # Test basic functionality
    log_info "Testing basic functionality..."
    if python -c "from processor.unified_project.src.utils.platform_detection import is_apple_silicon, get_apple_chip; print(f'Apple Silicon: {is_apple_silicon()}, Chip: {get_apple_chip()}')" 2>/dev/null; then
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
    echo "🎉 macOS development environment setup completed!"
    echo ""
    echo "Next steps:"
    echo "1. Activate the virtual environment: source venv/bin/activate"
    echo "2. Test the installation: python -m processor.unified_project.src.main --help"
    echo "3. Run platform detection: python -c \"from processor.unified_project.src.utils.platform_detection import get_platform_info; import json; print(json.dumps(get_platform_info(), indent=2))\""
    if [[ "$APPLE_SILICON" == "true" ]]; then
        echo "4. Test Apple Silicon optimizations: python -c \"from processor.unified_project.src.enhancers import APPLE_ENHANCER_AVAILABLE; print(f'Apple enhancer available: {APPLE_ENHANCER_AVAILABLE}')\""
    fi
    echo ""
    echo "Configuration files updated:"
    echo "  ~/.zprofile - Environment variables and PATH"
    echo ""
    echo "Cache directories created:"
    echo "  ~/.epubs/cache - Local file cache"
    echo "  ~/.cache/epubs/ - ML models and temporary files"
    echo ""
}

# Main execution
main() {
    echo "🍎 ePubs Accessibility Enhancement - macOS Setup"
    echo "=============================================="
    echo ""
    
    detect_platform
    check_homebrew
    install_system_deps
    configure_tesseract
    setup_python
    install_python_deps
    configure_apple_silicon
    setup_cache_dirs
    
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