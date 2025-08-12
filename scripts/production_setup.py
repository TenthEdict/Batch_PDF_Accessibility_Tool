#!/usr/bin/env python3
"""
Production Setup and Validation Script for ePubs Accessibility Enhancement Project.

This script validates the production environment, checks dependencies,
and ensures all components are ready for production deployment.
"""

import sys
import subprocess
import platform
import importlib
import os
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ProductionValidator:
    """Validates production environment and dependencies."""
    
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.success_count = 0
        self.total_checks = 0
        
    def log_success(self, message: str):
        """Log a successful check."""
        logger.info(f"✅ {message}")
        self.success_count += 1
        self.total_checks += 1
        
    def log_warning(self, message: str):
        """Log a warning."""
        logger.warning(f"⚠️  {message}")
        self.warnings.append(message)
        self.total_checks += 1
        
    def log_error(self, message: str):
        """Log an error."""
        logger.error(f"❌ {message}")
        self.errors.append(message)
        self.total_checks += 1
        
    def check_python_version(self) -> bool:
        """Check Python version compatibility."""
        version = sys.version_info
        if version.major == 3 and version.minor >= 9:
            self.log_success(f"Python version {version.major}.{version.minor}.{version.micro} is compatible")
            return True
        else:
            self.log_error(f"Python version {version.major}.{version.minor}.{version.micro} is not compatible. Requires Python 3.9+")
            return False
            
    def check_system_dependencies(self) -> bool:
        """Check system dependencies (Tesseract, etc.)."""
        system = platform.system().lower()
        
        # Check Tesseract
        try:
            result = subprocess.run(['tesseract', '--version'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                self.log_success("Tesseract OCR is available")
            else:
                self.log_error("Tesseract OCR is not working properly")
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError):
            self.log_error("Tesseract OCR is not installed or not in PATH")
            return False
            
        # Platform-specific checks
        if system == "darwin":  # macOS
            try:
                result = subprocess.run(['brew', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("Homebrew is available")
                else:
                    self.log_warning("Homebrew not found (optional for macOS)")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_warning("Homebrew not found (optional for macOS)")
                
        elif system == "linux":
            try:
                result = subprocess.run(['apt', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("APT package manager is available")
                else:
                    self.log_warning("APT not found (optional for Ubuntu/Debian)")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_warning("APT not found (optional for Ubuntu/Debian)")
                
        elif system == "windows":
            try:
                result = subprocess.run(['choco', '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success("Chocolatey is available")
                else:
                    self.log_warning("Chocolatey not found (optional for Windows)")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_warning("Chocolatey not found (optional for Windows)")
                
        return True
        
    def check_python_dependencies(self) -> bool:
        """Check Python package dependencies."""
        required_packages = [
            'PyMuPDF',
            'pikepdf', 
            'ocrmypdf',
            'PIL',  # Pillow
            'typer',
            'yaml'  # pyyaml
        ]
        
        missing_packages = []
        
        for package in required_packages:
            try:
                # Handle special cases for package names
                if package == 'PIL':
                    importlib.import_module('PIL')
                else:
                    importlib.import_module(package.lower().replace('-', '_'))
                self.log_success(f"{package} is installed")
            except ImportError:
                missing_packages.append(package)
                self.log_error(f"{package} is not installed")
                
        if missing_packages:
            return False
        return True
        
    def check_project_structure(self) -> bool:
        """Check that project structure is correct."""
        required_dirs = [
            'processor/unified_project/src',
            'processor/unified_project/config',
            'tests',
            'scripts'
        ]
        
        required_files = [
            'pyproject.toml',
            'README.md',
            'processor/unified_project/src/main.py',
            'processor/unified_project/config/academic.yaml'
        ]
        
        for directory in required_dirs:
            if Path(directory).exists():
                self.log_success(f"Directory {directory} exists")
            else:
                self.log_error(f"Directory {directory} is missing")
                return False
                
        for file_path in required_files:
            if Path(file_path).exists():
                self.log_success(f"File {file_path} exists")
            else:
                self.log_error(f"File {file_path} is missing")
                return False
                
        return True
        
    def check_configuration_files(self) -> bool:
        """Check configuration files are valid."""
        config_dir = Path('processor/unified_project/config')
        
        if not config_dir.exists():
            self.log_error("Configuration directory not found")
            return False
            
        config_files = list(config_dir.glob('*.yaml'))
        if not config_files:
            self.log_error("No configuration files found")
            return False
            
        for config_file in config_files:
            try:
                import yaml
                with open(config_file, 'r') as f:
                    yaml.safe_load(f)
                self.log_success(f"Configuration file {config_file.name} is valid YAML")
            except Exception as e:
                self.log_error(f"Configuration file {config_file.name} is invalid: {e}")
                return False
                
        return True
        
    def check_test_environment(self) -> bool:
        """Check test environment setup."""
        try:
            import pytest
            self.log_success("pytest is available for testing")
        except ImportError:
            self.log_warning("pytest not installed (recommended for testing)")
            
        test_dir = Path('tests')
        if test_dir.exists():
            test_files = list(test_dir.rglob('test_*.py'))
            if test_files:
                self.log_success(f"Found {len(test_files)} test files")
            else:
                self.log_warning("No test files found")
        else:
            self.log_warning("Tests directory not found")
            
        return True
        
    def check_security_scanning(self) -> bool:
        """Check security scanning tools."""
        security_tools = ['bandit', 'safety']
        
        for tool in security_tools:
            try:
                result = subprocess.run([tool, '--version'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_success(f"{tool} is available for security scanning")
                else:
                    self.log_warning(f"{tool} not working properly")
            except (subprocess.TimeoutExpired, FileNotFoundError):
                self.log_warning(f"{tool} not installed (optional for security)")
                
        return True
        
    def check_performance_monitoring(self) -> bool:
        """Check performance monitoring setup."""
        try:
            import psutil
            self.log_success("psutil is available for performance monitoring")
        except ImportError:
            self.log_warning("psutil not installed (optional for performance monitoring)")
            
        return True
        
    def run_basic_functionality_test(self) -> bool:
        """Run a basic functionality test."""
        try:
            # Test CLI help - use the current Python interpreter
            result = subprocess.run([
                sys.executable, '-m', 'processor.unified_project.src.main', '--help'
            ], capture_output=True, text=True, timeout=30, env=dict(os.environ))
            
            if result.returncode == 0:
                self.log_success("CLI interface is working")
                return True
            else:
                self.log_error(f"CLI interface is not working: {result.stderr}")
                return False
                
        except Exception as e:
            self.log_error(f"Basic functionality test failed: {e}")
            return False
            
    def generate_report(self) -> Dict:
        """Generate a comprehensive validation report."""
        report = {
            'timestamp': str(Path.cwd()),
            'platform': platform.system(),
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'total_checks': self.total_checks,
            'success_count': self.success_count,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'success_rate': (self.success_count / self.total_checks * 100) if self.total_checks > 0 else 0,
            'errors': self.errors,
            'warnings': self.warnings,
            'production_ready': len(self.errors) == 0
        }
        
        return report
        
    def print_summary(self, report: Dict):
        """Print a summary of the validation results."""
        print("\n" + "="*60)
        print("PRODUCTION VALIDATION SUMMARY")
        print("="*60)
        print(f"Platform: {report['platform']}")
        print(f"Python Version: {report['python_version']}")
        print(f"Total Checks: {report['total_checks']}")
        print(f"Successful: {report['success_count']}")
        print(f"Errors: {report['error_count']}")
        print(f"Warnings: {report['warning_count']}")
        print(f"Success Rate: {report['success_rate']:.1f}%")
        
        if report['production_ready']:
            print("\n🎉 PRODUCTION READY! All critical checks passed.")
        else:
            print(f"\n❌ NOT PRODUCTION READY. {report['error_count']} critical errors found.")
            
        if report['warnings']:
            print(f"\n⚠️  Warnings ({report['warning_count']}):")
            for warning in report['warnings']:
                print(f"  - {warning}")
                
        if report['errors']:
            print(f"\n❌ Errors ({report['error_count']}):")
            for error in report['errors']:
                print(f"  - {error}")
                
        print("="*60)


def main():
    """Main validation function."""
    print("🔍 ePubs Production Environment Validation")
    print("="*50)
    
    validator = ProductionValidator()
    
    # Run all validation checks
    checks = [
        ("Python Version", validator.check_python_version),
        ("System Dependencies", validator.check_system_dependencies),
        ("Python Dependencies", validator.check_python_dependencies),
        ("Project Structure", validator.check_project_structure),
        ("Configuration Files", validator.check_configuration_files),
        ("Test Environment", validator.check_test_environment),
        ("Security Scanning", validator.check_security_scanning),
        ("Performance Monitoring", validator.check_performance_monitoring),
        ("Basic Functionality", validator.run_basic_functionality_test),
    ]
    
    for check_name, check_func in checks:
        print(f"\n🔍 Checking {check_name}...")
        try:
            check_func()
        except Exception as e:
            validator.log_error(f"Check '{check_name}' failed with exception: {e}")
    
    # Generate and display report
    report = validator.generate_report()
    validator.print_summary(report)
    
    # Save report to file
    report_file = Path('production_validation_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Detailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if report['production_ready']:
        print("\n✅ Production validation completed successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Production validation failed with {report['error_count']} errors.")
        print("Please fix the errors above before deploying to production.")
        sys.exit(1)


if __name__ == "__main__":
    main()
