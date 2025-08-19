#!/bin/bash
"""
Phase 2B Dependency Installer

This script installs the optional ML dependencies required for Phase 2B features:
- FAISS vector database for 10x faster similarity search
- Enhanced ML libraries for document pattern recognition  
- Additional scientific computing packages

Usage:
    bash install_phase2b.sh
    
Or run directly:
    chmod +x install_phase2b.sh
    ./install_phase2b.sh
"""

set -e  # Exit on any error

echo "🚀 Phase 2B Dependency Installer"
echo "=================================="
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | cut -d' ' -f2 | cut -d'.' -f1,2)
required_version="3.9"

echo "🐍 Checking Python version..."
if python3 -c "import sys; exit(0 if sys.version_info >= (3,9) else 1)" 2>/dev/null; then
    echo "   ✅ Python $python_version (compatible)"
else
    echo "   ❌ Python $python_version (requires 3.9+)"
    echo "   Please upgrade Python to 3.9 or later"
    exit 1
fi

# Check if pip is available
echo ""
echo "📦 Checking pip..."
if command -v pip3 >/dev/null 2>&1; then
    echo "   ✅ pip3 available"
    PIP_CMD="pip3"
elif command -v pip >/dev/null 2>&1; then
    echo "   ✅ pip available"
    PIP_CMD="pip"
else
    echo "   ❌ pip not found"
    echo "   Please install pip"
    exit 1
fi

# Check if we're in a virtual environment (recommended)
echo ""
echo "🔍 Checking virtual environment..."
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "   ✅ Virtual environment active: $VIRTUAL_ENV"
elif [[ "$CONDA_DEFAULT_ENV" != "" ]]; then
    echo "   ✅ Conda environment active: $CONDA_DEFAULT_ENV"
else
    echo "   ⚠️  No virtual environment detected"
    echo "   Consider using: python3 -m venv venv && source venv/bin/activate"
    echo ""
    read -p "   Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "   Installation cancelled"
        exit 0
    fi
fi

# Install Phase 2B dependencies
echo ""
echo "⚡ Installing Phase 2B dependencies..."
echo "   This may take a few minutes..."
echo ""

# Try to install with the [ml] extra first
echo "📥 Installing epubs-accessibility[ml]..."
if $PIP_CMD install -e ".[ml]" 2>/dev/null; then
    echo "   ✅ Successfully installed via [ml] extra"
else
    echo "   ⚠️  [ml] extra failed, installing individual packages..."
    
    # Install individual ML packages
    packages=(
        "faiss-cpu>=1.7.4"
        "scikit-learn>=1.3.0" 
        "joblib>=1.3.0"
        "numpy>=1.24.0"
        "scipy>=1.7.0"
    )
    
    for package in "${packages[@]}"; do
        echo "   Installing $package..."
        if $PIP_CMD install "$package"; then
            echo "     ✅ $package installed"
        else
            echo "     ❌ Failed to install $package"
            exit 1
        fi
    done
fi

# Verify installation
echo ""
echo "🔬 Verifying Phase 2B installation..."

# Test Python imports
python3 -c "
import sys
errors = []

print('   Testing imports...')

try:
    import faiss
    print('     ✅ FAISS imported successfully')
    try:
        gpu_count = faiss.get_num_gpus()
        print(f'     📊 FAISS GPU support: {gpu_count} GPUs detected')
    except:
        print('     📊 FAISS GPU support: CPU-only mode')
except ImportError:
    errors.append('FAISS')
    print('     ❌ FAISS import failed')

try:
    import sklearn
    print('     ✅ scikit-learn imported successfully')
except ImportError:
    errors.append('scikit-learn')
    print('     ❌ scikit-learn import failed')

try:
    import joblib
    print('     ✅ joblib imported successfully')
except ImportError:
    errors.append('joblib')
    print('     ❌ joblib import failed')

try:
    import numpy as np
    print('     ✅ numpy imported successfully')
except ImportError:
    errors.append('numpy')
    print('     ❌ numpy import failed')

if errors:
    print(f'\\n❌ Installation verification failed. Missing: {', '.join(errors)}')
    sys.exit(1)
else:
    print('\\n✅ All Phase 2B dependencies verified successfully!')
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 Phase 2B Installation Complete!"
    echo "=================================="
    echo ""
    echo "You can now use Phase 2B features:"
    echo "   • epubs batch-process input_dir/ output_dir/ --phase2b"
    echo "   • epubs validate-phase2b"
    echo ""
    echo "Expected performance improvements:"
    echo "   • 5-8x faster batch processing"
    echo "   • 10x faster similarity search"
    echo "   • 70-80% cache hit rates for similar documents"
    echo ""
    echo "Next steps:"
    echo "   1. Run validation: epubs validate-phase2b"
    echo "   2. Test with your documents: epubs batch-process --phase2b"
    echo "   3. Check setup guide: cat PHASE2B_SETUP.md"
else
    echo ""
    echo "❌ Installation verification failed"
    echo "Please check the error messages above and try again"
    exit 1
fi
