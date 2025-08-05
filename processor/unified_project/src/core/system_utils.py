"""
Cross-platform system utilities for Windows compatibility.
Provides automatic detection and configuration for Windows-specific paths and settings.
"""

import os
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Optional, Dict, Any
import tempfile


class SystemDetection:
    """Detects system configuration and provides platform-specific defaults."""
    
    @staticmethod
    def is_windows() -> bool:
        """Check if running on Windows."""
        return platform.system() == "Windows"
    
    @staticmethod
    def is_macos() -> bool:
        """Check if running on macOS."""
        return platform.system() == "Darwin"
    
    @staticmethod
    def is_linux() -> bool:
        """Check if running on Linux."""
        return platform.system() == "Linux"
    
    @staticmethod
    def get_platform_name() -> str:
        """Get human-readable platform name."""
        system = platform.system()
        if system == "Windows":
            return "Windows"
        elif system == "Darwin":
            return "macOS"
        elif system == "Linux":
            return "Linux"
        else:
            return system


class WindowsPaths:
    """Windows-specific path utilities and configurations."""
    
    @staticmethod
    def get_tesseract_path() -> Optional[str]:
        """
        Automatically detect Tesseract installation on Windows.
        Returns the path to tesseract.exe if found.
        """
        if not SystemDetection.is_windows():
            return "tesseract"  # Assume it's in PATH on non-Windows
        
        # Check if tesseract is in PATH first
        if shutil.which("tesseract"):
            return "tesseract"
        
        # Common Windows installation paths
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            r"C:\Tools\tesseract\tesseract.exe",
            r"C:\tesseract\tesseract.exe",
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None
    
    @staticmethod
    def get_temp_directory() -> str:
        """Get appropriate temporary directory for the platform."""
        if SystemDetection.is_windows():
            # Use Windows TEMP directory
            return os.path.expandvars(r"%TEMP%\epubs_temp")
        else:
            # Use system temp directory
            return str(Path(tempfile.gettempdir()) / "epubs_temp")
    
    @staticmethod
    def get_user_documents_dir() -> str:
        """Get user's Documents directory."""
        if SystemDetection.is_windows():
            return os.path.expandvars(r"%USERPROFILE%\Documents")
        else:
            return str(Path.home() / "Documents")
    
    @staticmethod
    def get_default_input_dir() -> str:
        """Get default input directory for PDFs."""
        docs = WindowsPaths.get_user_documents_dir()
        return str(Path(docs) / "ePubs" / "Input")
    
    @staticmethod
    def get_default_output_dir() -> str:
        """Get default output directory for processed PDFs."""
        docs = WindowsPaths.get_user_documents_dir()
        return str(Path(docs) / "ePubs" / "Output")


class CrossPlatformConfig:
    """Generates platform-specific configuration settings."""
    
    @staticmethod
    def get_platform_defaults() -> Dict[str, Any]:
        """Get platform-specific default configuration."""
        config = {
            "system": {
                "platform": SystemDetection.get_platform_name(),
                "temp_directory": WindowsPaths.get_temp_directory(),
                "default_input_dir": WindowsPaths.get_default_input_dir(),
                "default_output_dir": WindowsPaths.get_default_output_dir(),
            },
            "ocr": {
                "tesseract_cmd": WindowsPaths.get_tesseract_path() or "tesseract",
            }
        }
        
        # Windows-specific settings
        if SystemDetection.is_windows():
            config["system"].update({
                "path_separator": "\\",
                "shell": "powershell",
                "memory_limit": "auto",
                "max_processes": "auto",
            })
        else:
            config["system"].update({
                "path_separator": "/",
                "shell": "bash",
            })
        
        return config
    
    @staticmethod
    def verify_dependencies() -> Dict[str, bool]:
        """Verify that required dependencies are available."""
        results = {}
        
        # Check Python version
        try:
            import sys
            version = sys.version_info
            results["python"] = version >= (3, 9)
        except:
            results["python"] = False
        
        # Check Tesseract
        tesseract_path = WindowsPaths.get_tesseract_path()
        if tesseract_path:
            try:
                result = subprocess.run([tesseract_path, "--version"], 
                                      capture_output=True, text=True, timeout=5)
                results["tesseract"] = result.returncode == 0
            except:
                results["tesseract"] = False
        else:
            results["tesseract"] = False
        
        # Check if we can create temp directory
        try:
            temp_dir = Path(WindowsPaths.get_temp_directory())
            temp_dir.mkdir(parents=True, exist_ok=True)
            results["temp_directory"] = True
        except:
            results["temp_directory"] = False
        
        return results


def setup_platform_environment():
    """
    Set up platform-specific environment and return configuration.
    Call this during application startup.
    """
    platform_config = CrossPlatformConfig.get_platform_defaults()
    dependency_status = CrossPlatformConfig.verify_dependencies()
    
    # Create necessary directories
    try:
        for dir_key in ["temp_directory", "default_input_dir", "default_output_dir"]:
            dir_path = Path(platform_config["system"][dir_key])
            dir_path.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create directories: {e}")
    
    return {
        "config": platform_config,
        "dependencies": dependency_status,
        "platform": SystemDetection.get_platform_name()
    }


if __name__ == "__main__":
    # Quick test of the system detection
    print("System Detection Results:")
    print(f"Platform: {SystemDetection.get_platform_name()}")
    print(f"Tesseract Path: {WindowsPaths.get_tesseract_path()}")
    print(f"Temp Directory: {WindowsPaths.get_temp_directory()}")
    print(f"Dependencies: {CrossPlatformConfig.verify_dependencies()}")
