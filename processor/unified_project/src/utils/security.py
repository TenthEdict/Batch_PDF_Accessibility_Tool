#!/usr/bin/env python3
"""
Security utilities for safe file and path operations.

This module provides security validation functions to prevent:
- Path traversal attacks
- Malicious filename processing
- Unsafe file operations
- File type validation bypass
"""

import os
import re
import logging
from pathlib import Path
from typing import Optional, List, Set

logger = logging.getLogger(__name__)

# Dangerous path components that could be used for traversal
DANGEROUS_PATH_COMPONENTS = {"..", "~", "//"}

# File extensions allowed for processing
ALLOWED_EXTENSIONS = {".pdf", ".PDF"}

# PDF magic numbers (file signatures)
PDF_MAGIC_NUMBERS = [
    b"%PDF-1.",  # PDF 1.x
    b"%PDF-2.",  # PDF 2.x
]

# Characters not allowed in filenames (platform-specific)
UNSAFE_FILENAME_CHARS = r'[<>:"|?*\x00-\x1f]'  # Windows + control chars

# Protected system directories (platform-specific)
PROTECTED_DIRECTORIES = {
    "/etc", "/sys", "/proc", "/dev", "/boot",  # Linux
    "C:\\Windows", "C:\\Program Files", "C:\\Program Files (x86)",  # Windows
    "/System", "/Library/System",  # macOS
}


def validate_pdf_file(
    file_path: Path,
    check_magic: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate that file is actually a PDF.
    
    Args:
        file_path: Path to file to validate
        check_magic: Whether to check magic numbers (slower but more secure)
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check file exists
        if not file_path.exists():
            return False, f"File does not exist: {file_path}"
        
        # Check file is not empty
        if file_path.stat().st_size == 0:
            return False, "File is empty"
        
        # Check file extension
        if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
            return False, f"Invalid file extension: {file_path.suffix}"
        
        # Optional: Check PDF magic number
        if check_magic:
            try:
                with open(file_path, 'rb') as f:
                    header = f.read(8)
                
                is_pdf = any(header.startswith(magic) for magic in PDF_MAGIC_NUMBERS)
                if not is_pdf:
                    return False, "File is not a valid PDF (magic number mismatch)"
            except Exception as e:
                return False, f"Cannot read file: {e}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"PDF validation error: {e}")
        return False, f"Validation failed: {e}"


def validate_output_path(
    output_path: Path,
    allowed_parent: Optional[Path] = None,
    allow_overwrite: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate output path for security and safety.
    
    Args:
        output_path: Path to validate
        allowed_parent: Optional parent directory to constrain outputs
        allow_overwrite: Whether to allow overwriting existing files
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Convert to absolute path and resolve symlinks
        output_path = output_path.resolve()
        
        # Check for path traversal attempts
        path_parts = output_path.parts
        for part in path_parts:
            if part in DANGEROUS_PATH_COMPONENTS:
                return False, f"Path contains dangerous component: {part}"
        
        # If parent directory specified, ensure output is within it
        if allowed_parent:
            allowed_parent = allowed_parent.resolve()
            try:
                output_path.relative_to(allowed_parent)
            except ValueError:
                return False, f"Output path outside allowed directory: {allowed_parent}"
        
        # Check if path points to protected system directory
        output_str = str(output_path)
        for protected_dir in PROTECTED_DIRECTORIES:
            if output_str.startswith(protected_dir):
                return False, f"Cannot write to protected directory: {protected_dir}"
        
        # Check file overwrite permission
        if not allow_overwrite and output_path.exists():
            return False, f"File already exists: {output_path}"
        
        # Validate parent directory exists or can be created
        parent = output_path.parent
        if not parent.exists():
            try:
                parent.mkdir(parents=True, exist_ok=True)
            except (PermissionError, OSError) as e:
                return False, f"Cannot create output directory: {e}"
        
        # Check write permissions
        if not os.access(parent, os.W_OK):
            return False, f"No write permission for directory: {parent}"
        
        return True, None
        
    except Exception as e:
        logger.error(f"Path validation error: {e}")
        return False, f"Path validation failed: {e}"


def sanitize_filename(filename: str, replacement: str = "_") -> str:
    """
    Sanitize filename by removing/replacing unsafe characters.
    
    Args:
        filename: Original filename
        replacement: Character to replace unsafe chars with
        
    Returns:
        Sanitized filename
    """
    # Remove path separators
    filename = os.path.basename(filename)
    
    # Replace unsafe characters
    sanitized = re.sub(UNSAFE_FILENAME_CHARS, replacement, filename)
    
    # Remove leading/trailing dots and spaces
    sanitized = sanitized.strip(". ")
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    # Limit filename length (255 is typical max, use 200 for safety)
    if len(sanitized) > 200:
        name, ext = os.path.splitext(sanitized)
        sanitized = name[:200-len(ext)] + ext
    
    return sanitized


def validate_input_directory(input_dir: Path) -> tuple[bool, Optional[str]]:
    """
    Validate input directory for batch processing.
    
    Args:
        input_dir: Directory to validate
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Check exists
        if not input_dir.exists():
            return False, f"Directory does not exist: {input_dir}"
        
        # Check is directory
        if not input_dir.is_dir():
            return False, f"Path is not a directory: {input_dir}"
        
        # Check readable
        if not os.access(input_dir, os.R_OK):
            return False, f"No read permission for directory: {input_dir}"
        
        return True, None
        
    except Exception as e:
        return False, f"Directory validation failed: {e}"


def validate_batch_input(
    input_dir: Path,
    output_dir: Path,
    allow_overwrite: bool = False
) -> tuple[bool, Optional[str]]:
    """
    Validate batch processing input and output directories.
    
    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        allow_overwrite: Whether to allow overwriting existing files
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Validate input directory
    is_valid, error = validate_input_directory(input_dir)
    if not is_valid:
        return False, f"Input directory invalid: {error}"
    
    # Validate output directory path
    try:
        output_dir = output_dir.resolve()
        
        # Check for protected directories
        output_str = str(output_dir)
        for protected_dir in PROTECTED_DIRECTORIES:
            if output_str.startswith(protected_dir):
                return False, f"Cannot write to protected directory: {protected_dir}"
        
        # Create output directory if it doesn't exist
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Check write permissions
        if not os.access(output_dir, os.W_OK):
            return False, f"No write permission for directory: {output_dir}"
        
        return True, None
        
    except Exception as e:
        return False, f"Output directory validation failed: {e}"


def check_file_overwrite_safety(
    output_path: Path,
    critical_extensions: Optional[Set[str]] = None
) -> tuple[bool, Optional[str]]:
    """
    Check if it's safe to overwrite a file.
    
    Args:
        output_path: Path to check
        critical_extensions: Extensions that should never be overwritten
        
    Returns:
        Tuple of (is_safe, warning_message)
    """
    if critical_extensions is None:
        critical_extensions = {".py", ".sh", ".bat", ".exe", ".dll", ".so"}
    
    # File doesn't exist - safe to write
    if not output_path.exists():
        return True, None
    
    # Check if file has critical extension
    if output_path.suffix.lower() in critical_extensions:
        return False, f"Cannot overwrite critical file type: {output_path.suffix}"
    
    # Check if file is in use
    try:
        # Try to open for writing (doesn't actually write)
        with open(output_path, 'ab'):
            pass
        return True, None
    except PermissionError:
        return False, "File is in use or locked"
    except Exception as e:
        return False, f"Cannot access file: {e}"
