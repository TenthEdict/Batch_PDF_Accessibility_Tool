#!/usr/bin/env python3
"""
Development Environment Validation Script for ePubs Accessibility Enhancement

This script validates that all required dependencies, configurations, and
optimizations are properly set up for both macOS and Ubuntu platforms.
"""

import json
import logging
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EnvironmentValidator:
    """Validates development environment setup."""
    
    def __init__(self):
        self.platform_system = platform.system()
        self.issues = []
        self.warnings = []
        self.successes = []
        
    def log_success(self, message: str):
        """Log a successful validation."""
        self.successes.append(message)
        print(f"✅ {message}")
        
    def log_warning(self, message: str):
        """Log a warning."""
        self.warnings.append(message)
        print(f"⚠️  {message}")
        
    def log_error(self, message: str):
        """Log an error."""
        self.issues.append(message)
        print(f"❌ {message}")
        
    def check_python_version(self) -> bool:
        """Check if Python 3.11+ is available."""
        print("\n🐍 Checking Python Version...")
        
        try:
            version = sys.version_info
            if version.major == 3 and version.minor >= 11:
                self.log_success(f"Python {version.major}.{version.minor}.{version.micro} is available")
                return True
            else:
                self.log_error(f"Python {version.major}.{version.minor}.{version.micro} found, but 3.11+ required")
                return False
        except Exception as e:
            self.log_error(f"Failed to check Python version: {e}")
            return False
    
    def check_virtual_environment(self) -> bool:
        """Check if running in virtual environment."""
        print("\n📦 Checking Virtual Environment...")
        
        venv_path = os.environ.get('VIRTUAL_ENV')
        if venv_path:
            self.log_success(f"Virtual environment active: {venv_path}")
            return True
        else:
            self.log_warning("Not running in virtual environment")
            return False
    
    def check_system_dependencies(self) -> bool:
        """Check system-level dependencies."""
        print("\n🔧 Checking System Dependencies...")
        
        # Common dependencies
        required_tools = {
            'tesseract': 'Tesseract OCR engine',
            'pdfinfo': 'PDF utilities (poppler)',
            'convert': 'ImageMagick',
            'gs': 'Ghostscript'
        }
        
        all_present = True
        for tool, description in required_tools.items():
            if self._check_command(tool):
                self.log_success(f"{description} is available")
            else:
                self.log_error(f"{description} is missing (command: {tool})")
                all_present = False
                
        return all_present
    
    def check_python_packages(self) -> bool:
        """Check required Python packages."""
        print("\n📚 Checking Python Packages...")
        
        required_packages = [
            'typer',
            'rich', 
            'PyPDF2',
            'pytesseract',
            'Pillow',
            'click'
        ]
        
        optional_packages = {
            'torch': 'PyTorch for ML features',
            'transformers': 'Hugging Face transformers',
            'mlx': 'Apple MLX framework (macOS only)'
        }
        
        all_required_present = True
        
        # Check required packages
        for package in required_packages:
            if self._check_python_package(package):
                self.log_success(f"Required package '{package}' is installed")
            else:
                self.log_error(f"Required package '{package}' is missing")
                all_required_present = False
        
        # Check optional packages
        for package, description in optional_packages.items():
            if self._check_python_package(package):
                self.log_success(f"Optional package '{package}' is installed ({description})")
            else:
                self.log_warning(f"Optional package '{package}' is missing ({description})")
                
        return all_required_present
    
    def check_project_structure(self) -> bool:
        """Check project directory structure."""
        print("\n📁 Checking Project Structure...")
        
        required_paths = [
            'pyproject.toml',
            'processor/unified_project/src/main.py',
            'processor/unified_project/src/enhancers/__init__.py',
            'processor/unified_project/src/services/enhancement_service.py',
            'processor/unified_project/src/utils/platform_detection.py'
        ]
        
        optional_paths = [
            'tests/',
            'venv/',
            '.git/',
            'README.md'
        ]
        
        all_present = True
        
        for path in required_paths:
            if Path(path).exists():
                self.log_success(f"Required path exists: {path}")
            else:
                self.log_error(f"Required path missing: {path}")
                all_present = False
                
        for path in optional_paths:
            if Path(path).exists():
                self.log_success(f"Optional path exists: {path}")
            else:
                self.log_warning(f"Optional path missing: {path}")
                
        return all_present
    
    def check_cache_directories(self) -> bool:
        """Check cache directory setup."""
        print("\n💾 Checking Cache Directories...")
        
        if self.platform_system == 'Darwin':  # macOS
            cache_dirs = [
                Path.home() / '.epubs' / 'cache',
                Path.home() / '.cache' / 'epubs' / 'ml_models',
                Path.home() / '.cache' / 'epubs' / 'apple_models'
            ]
        else:  # Ubuntu/Linux
            cache_dirs = [
                Path.home() / '.cache' / 'epubs',
                Path.home() / '.cache' / 'epubs' / 'ml_models',
                Path.home() / '.epubs' / 'logs'
            ]
        
        all_present = True
        for cache_dir in cache_dirs:
            if cache_dir.exists():
                self.log_success(f"Cache directory exists: {cache_dir}")
            else:
                self.log_warning(f"Cache directory missing: {cache_dir}")
                try:
                    cache_dir.mkdir(parents=True, exist_ok=True)
                    self.log_success(f"Created cache directory: {cache_dir}")
                except Exception as e:
                    self.log_error(f"Failed to create cache directory {cache_dir}: {e}")
                    all_present = False
                    
        return all_present
    
    def check_platform_optimizations(self) -> bool:
        """Check platform-specific optimizations."""
        print(f"\n🔧 Checking {self.platform_system} Optimizations...")
        
        if self.platform_system == 'Darwin':
            return self._check_macos_optimizations()
        elif self.platform_system == 'Linux':
            return self._check_ubuntu_optimizations()
        else:
            self.log_warning(f"Unknown platform: {self.platform_system}")
            return False
    
    def _check_macos_optimizations(self) -> bool:
        """Check macOS-specific optimizations."""
        optimizations_ok = True
        
        # Check for Apple Silicon
        try:
            from processor.unified_project.src.utils.platform_detection import (
                is_apple_silicon, get_apple_chip, get_platform_info
            )
            
            if is_apple_silicon():
                chip = get_apple_chip()
                self.log_success(f"Apple Silicon detected: {chip}")
                
                # Check MLX availability
                if self._check_python_package('mlx'):
                    self.log_success("MLX framework available for Apple Silicon acceleration")
                else:
                    self.log_warning("MLX framework not available - install with: pip install mlx mlx-vlm")
                    
            else:
                self.log_success("Intel Mac detected")
                
            # Check platform info
            platform_info = get_platform_info()
            self.log_success(f"Platform detection working: {platform_info.get('cpu_cores', 'unknown')} cores, {platform_info.get('memory_gb', 'unknown')} GB RAM")
            
        except ImportError as e:
            self.log_error(f"Platform detection module not available: {e}")
            optimizations_ok = False
        except Exception as e:
            self.log_error(f"Failed to check Apple Silicon optimizations: {e}")
            optimizations_ok = False
            
        # Check Homebrew
        if self._check_command('brew'):
            self.log_success("Homebrew is available")
        else:
            self.log_warning("Homebrew not found - some dependencies might be missing")
            
        return optimizations_ok
    
    def _check_ubuntu_optimizations(self) -> bool:
        """Check Ubuntu-specific optimizations."""
        optimizations_ok = True
        
        # Check for GPU
        if self._check_command('nvidia-smi'):
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'], 
                                      capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    gpu_name = result.stdout.strip()
                    self.log_success(f"NVIDIA GPU detected: {gpu_name}")
                    
                    # Check CUDA
                    if self._check_python_package('torch'):
                        try:
                            import torch
                            if torch.cuda.is_available():
                                self.log_success(f"CUDA available with {torch.cuda.device_count()} devices")
                            else:
                                self.log_warning("PyTorch installed but CUDA not available")
                        except Exception as e:
                            self.log_warning(f"Failed to check CUDA availability: {e}")
                else:
                    self.log_warning("nvidia-smi command failed")
            except Exception as e:
                self.log_warning(f"Failed to query GPU info: {e}")
        else:
            self.log_success("No NVIDIA GPU detected (CPU processing will be used)")
            
        # Check system package manager
        if self._check_command('apt'):
            self.log_success("APT package manager available")
        else:
            self.log_warning("APT not found - might not be Ubuntu/Debian")
            
        return optimizations_ok
    
    def check_basic_functionality(self) -> bool:
        """Test basic functionality."""
        print("\n🧪 Testing Basic Functionality...")
        
        try:
            # Test CLI help
            result = subprocess.run([
                sys.executable, '-m', 'processor.unified_project.src.main', '--help'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0 and 'Usage:' in result.stdout:
                self.log_success("CLI help command works")
            else:
                self.log_error("CLI help command failed")
                return False
                
        except Exception as e:
            self.log_error(f"Failed to test CLI functionality: {e}")
            return False
            
        # Test imports
        try:
            from processor.unified_project.src.enhancers import (
                OCREnhancer, PDFEnhancer, ML_ENHANCER_AVAILABLE, APPLE_ENHANCER_AVAILABLE
            )
            self.log_success("Core enhancers import successfully")
            
            if ML_ENHANCER_AVAILABLE:
                self.log_success("ML enhancer is available")
            else:
                self.log_warning("ML enhancer not available")
                
            if APPLE_ENHANCER_AVAILABLE:
                self.log_success("Apple optimized enhancer is available")
            else:
                self.log_warning("Apple optimized enhancer not available")
                
        except Exception as e:
            self.log_error(f"Failed to import core modules: {e}")
            return False
            
        return True
    
    def _check_command(self, command: str) -> bool:
        """Check if a command is available."""
        try:
            result = subprocess.run(['which', command], 
                                  capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False
    
    def _check_python_package(self, package: str) -> bool:
        """Check if a Python package is installed."""
        try:
            __import__(package)
            return True
        except ImportError:
            return False
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report."""
        return {
            'platform': {
                'system': self.platform_system,
                'machine': platform.machine(),
                'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            },
            'validation_results': {
                'successes': len(self.successes),
                'warnings': len(self.warnings),
                'errors': len(self.issues)
            },
            'details': {
                'successes': self.successes,
                'warnings': self.warnings,
                'errors': self.issues
            }
        }
    
    def run_full_validation(self) -> bool:
        """Run complete environment validation."""
        print("🔍 ePubs Accessibility Enhancement - Environment Validation")
        print("=" * 60)
        
        checks = [
            self.check_python_version,
            self.check_virtual_environment, 
            self.check_system_dependencies,
            self.check_python_packages,
            self.check_project_structure,
            self.check_cache_directories,
            self.check_platform_optimizations,
            self.check_basic_functionality
        ]
        
        results = []
        for check in checks:
            try:
                result = check()
                results.append(result)
            except Exception as e:
                self.log_error(f"Validation check failed: {e}")
                results.append(False)
                
        # Print summary
        print("\n" + "=" * 60)
        print("🏁 Validation Summary")
        print("=" * 60)
        
        print(f"✅ Successes: {len(self.successes)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.issues)}")
        
        if self.issues:
            print("\n❌ Issues that need attention:")
            for issue in self.issues:
                print(f"   • {issue}")
                
        if self.warnings:
            print("\n⚠️  Warnings (optional features):")
            for warning in self.warnings:
                print(f"   • {warning}")
        
        all_critical_passed = all(results[:6])  # First 6 checks are critical
        
        if all_critical_passed:
            print("\n🎉 Environment validation passed! Your setup is ready for development.")
        else:
            print("\n🔧 Some critical issues need to be resolved before development.")
            
        return all_critical_passed


def main():
    """Main validation function."""
    validator = EnvironmentValidator()
    
    # Run validation
    success = validator.run_full_validation()
    
    # Generate report
    report = validator.generate_report()
    
    # Save report
    report_path = Path('environment_validation_report.json')
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📋 Detailed report saved to: {report_path}")
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()