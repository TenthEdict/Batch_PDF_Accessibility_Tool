#!/usr/bin/env python3
"""
Dependency Migration Script for ePubs Accessibility Project

This script helps migrate from the old requirements.txt system to the new pyproject.toml
system and validates that all dependencies are properly resolved.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

class DependencyMigrator:
    """Handles migration from requirements.txt to pyproject.toml"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.old_requirements_files = [
            "requirements.txt",
            "processor/unified_project/requirements.txt"
        ]
        self.old_setup_files = [
            "processor/setup.py",
            "processor/unified_project/setup.py"
        ]
        
    def backup_old_files(self) -> None:
        """Create backups of old dependency files"""
        logger.info("Creating backups of old dependency files...")
        backup_dir = self.project_root / "dependency_backups"
        backup_dir.mkdir(exist_ok=True)
        
        # Backup requirements files
        for req_file in self.old_requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                backup_path = backup_dir / f"{req_file.replace('/', '_')}.backup"
                shutil.copy2(req_path, backup_path)
                logger.info(f"Backed up {req_file} to {backup_path}")
        
        # Backup setup.py files
        for setup_file in self.old_setup_files:
            setup_path = self.project_root / setup_file
            if setup_path.exists():
                backup_path = backup_dir / f"{setup_file.replace('/', '_')}.backup"
                shutil.copy2(setup_path, backup_path)
                logger.info(f"Backed up {setup_file} to {backup_path}")
    
    def validate_pyproject_toml(self) -> bool:
        """Validate that pyproject.toml is properly formatted"""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            logger.error("pyproject.toml not found!")
            return False
        
        try:
            import tomllib
        except ImportError:
            try:
                import tomli as tomllib
            except ImportError:
                logger.warning("tomllib/tomli not available, skipping TOML validation")
                return True
        
        try:
            with open(pyproject_path, "rb") as f:
                config = tomllib.load(f)
            
            # Check required sections
            required_sections = ["build-system", "project"]
            for section in required_sections:
                if section not in config:
                    logger.error(f"Missing required section: {section}")
                    return False
            
            # Check project metadata
            project = config["project"]
            required_fields = ["name", "version", "description", "dependencies"]
            for field in required_fields:
                if field not in project:
                    logger.error(f"Missing required project field: {field}")
                    return False
            
            logger.info("pyproject.toml validation passed")
            return True
            
        except Exception as e:
            logger.error(f"Error validating pyproject.toml: {e}")
            return False
    
    def test_installation(self, use_virtual_env: bool = True) -> bool:
        """Test installation of dependencies in a clean environment"""
        logger.info("Testing dependency installation...")
        
        if use_virtual_env:
            # Create temporary virtual environment
            test_venv = self.project_root / "test_venv"
            if test_venv.exists():
                shutil.rmtree(test_venv)
            
            try:
                # Create virtual environment
                subprocess.run([
                    sys.executable, "-m", "venv", str(test_venv)
                ], check=True, capture_output=True)
                
                # Get python executable in venv
                if os.name == "nt":  # Windows
                    python_exe = test_venv / "Scripts" / "python.exe"
                    pip_exe = test_venv / "Scripts" / "pip.exe"
                else:  # Unix-like
                    python_exe = test_venv / "bin" / "python"
                    pip_exe = test_venv / "bin" / "pip"
                
                # Upgrade pip
                subprocess.run([
                    str(pip_exe), "install", "--upgrade", "pip"
                ], check=True, capture_output=True)
                
                # Install core dependencies
                result = subprocess.run([
                    str(pip_exe), "install", "-e", ".[test]"
                ], cwd=str(self.project_root), capture_output=True, text=True)
                
                if result.returncode == 0:
                    logger.info("Core dependencies installed successfully")
                    
                    # Test import of key modules
                    test_imports = [
                        "import PyMuPDF as fitz",
                        "import pikepdf", 
                        "import pdf2image",
                        "import PIL",
                        "import cv2",
                        "import pytesseract",
                        "import numpy",
                        "import pandas",
                        "import yaml"
                    ]
                    
                    for test_import in test_imports:
                        import_result = subprocess.run([
                            str(python_exe), "-c", test_import
                        ], capture_output=True, text=True)
                        
                        if import_result.returncode != 0:
                            logger.error(f"Failed to import: {test_import}")
                            logger.error(f"Error: {import_result.stderr}")
                            return False
                    
                    logger.info("All core imports successful")
                    return True
                else:
                    logger.error("Failed to install dependencies")
                    logger.error(f"Error: {result.stderr}")
                    return False
                    
            except subprocess.CalledProcessError as e:
                logger.error(f"Installation test failed: {e}")
                return False
            finally:
                # Cleanup test environment
                if test_venv.exists():
                    shutil.rmtree(test_venv)
        else:
            logger.warning("Skipping virtual environment test")
            return True
    
    def update_documentation(self) -> None:
        """Update documentation to reflect new installation process"""
        logger.info("Updating documentation...")
        
        # Update CLAUDE.md
        claude_md_path = self.project_root / "CLAUDE.md"
        if claude_md_path.exists():
            with open(claude_md_path, "r") as f:
                content = f.read()
            
            # Replace old pip install commands
            old_install = "pip install -r processor/unified_project/requirements.txt"
            new_install = "pip install -e ."
            
            if old_install in content:
                content = content.replace(old_install, new_install)
                
                with open(claude_md_path, "w") as f:
                    f.write(content)
                logger.info("Updated CLAUDE.md with new installation instructions")
        
        # Create installation guide
        install_guide = self.project_root / "INSTALLATION.md"
        with open(install_guide, "w") as f:
            f.write("""# Installation Guide - ePubs Accessibility

## Quick Installation

```bash
# Clone the repository
git clone <repository_url>
cd ePubs_Main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# venv\\Scripts\\activate   # Windows

# Install core dependencies
pip install -e .

# Install optional dependencies as needed
pip install -e .[web]      # Web scraping
pip install -e .[docs]     # Document format support
pip install -e .[ml]       # Machine learning features
pip install -e .[dev]      # Development tools
pip install -e .[all]      # All optional dependencies
```

## Dependency Groups

- **Core**: Essential dependencies for PDF processing and OCR
- **web**: Selenium and web scraping tools
- **docs**: Additional document format support (Word, PowerPoint, Excel)
- **ml**: Machine learning and AI features (heavy dependencies)
- **dev**: Development tools (testing, linting, formatting)
- **test**: Testing dependencies only
- **all**: All optional dependencies

## System Dependencies

On Ubuntu/Debian:
```bash
sudo apt-get install -y poppler-utils tesseract-ocr
```

On macOS:
```bash
brew install poppler tesseract
```

## Development Setup

For development work:
```bash
pip install -e .[dev]
pre-commit install  # Set up git hooks
```

## Troubleshooting

### Common Issues

1. **OpenCV Installation**: If opencv-python fails, try:
   ```bash
   pip install opencv-python-headless
   ```

2. **Tesseract not found**: Install tesseract-ocr system package
3. **Permission errors**: Use `--user` flag or virtual environment

### Docker Installation

```bash
docker build -t epubs-accessibility .
docker run -v /path/to/data:/data epubs-accessibility
```
""")
        logger.info("Created INSTALLATION.md")
    
    def migrate(self) -> bool:
        """Execute the full migration process"""
        logger.info("Starting dependency migration...")
        
        # Step 1: Validate pyproject.toml
        if not self.validate_pyproject_toml():
            logger.error("pyproject.toml validation failed")
            return False
        
        # Step 2: Backup old files
        self.backup_old_files()
        
        # Step 3: Test installation
        if not self.test_installation():
            logger.error("Installation test failed")
            return False
        
        # Step 4: Update documentation
        self.update_documentation()
        
        # Step 5: Mark old files for removal (but don't delete yet)
        self.mark_old_files_for_removal()
        
        logger.info("Migration completed successfully!")
        logger.info("Next steps:")
        logger.info("1. Test the new installation process")
        logger.info("2. Update CI/CD pipelines if any")
        logger.info("3. Remove old requirements files when confident")
        
        return True
    
    def mark_old_files_for_removal(self) -> None:
        """Mark old dependency files for removal (rename with .deprecated)"""
        logger.info("Marking old dependency files for removal...")
        
        for req_file in self.old_requirements_files:
            req_path = self.project_root / req_file
            if req_path.exists():
                deprecated_path = req_path.with_suffix(".deprecated")
                if not deprecated_path.exists():
                    req_path.rename(deprecated_path)
                    logger.info(f"Marked {req_file} as deprecated")
        
        # Create README in processor directory explaining changes
        processor_readme = self.project_root / "processor" / "DEPENDENCY_MIGRATION.md"
        with open(processor_readme, "w") as f:
            f.write("""# Dependency Migration Notice

This directory previously contained separate dependency management files.
These have been consolidated into the root `pyproject.toml` file.

## Old Files (now deprecated):
- `requirements.txt` → Use `pip install -e .` from project root
- `unified_project/requirements.txt` → Use `pip install -e .` from project root  
- `setup.py` → Use `pyproject.toml` from project root

## New Installation Process:
```bash
cd /path/to/ePubs_Main
pip install -e .
```

See `/INSTALLATION.md` for complete installation guide.
""")

def main():
    """Main entry point"""
    project_root = Path(__file__).parent
    migrator = DependencyMigrator(project_root)
    
    try:
        success = migrator.migrate()
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()