#!/usr/bin/env python3
"""
Secure temporary file management utilities.

This module provides secure temporary file creation and cleanup
to prevent security vulnerabilities from temp file handling.
"""

import os
import tempfile
import shutil
import logging
import atexit
from pathlib import Path
from typing import Optional, List
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Track temp files/dirs for cleanup
_TEMP_FILES: List[Path] = []
_TEMP_DIRS: List[Path] = []


def _cleanup_temp_files():
    """
    Cleanup all tracked temporary files and directories.
    
    Called automatically at program exit via atexit.
    """
    # Clean up temp files
    for temp_file in _TEMP_FILES[:]:
        try:
            if temp_file.exists():
                temp_file.unlink()
                logger.debug(f"Cleaned up temp file: {temp_file.name}")
            _TEMP_FILES.remove(temp_file)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file: {e}")
    
    # Clean up temp directories
    for temp_dir in _TEMP_DIRS[:]:
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir.name}")
            _TEMP_DIRS.remove(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temp directory: {e}")


# Register cleanup function
atexit.register(_cleanup_temp_files)


def create_secure_temp_file(
    suffix: str = "",
    prefix: str = "epubs_",
    dir: Optional[Path] = None,
    auto_cleanup: bool = True
) -> Path:
    """
    Create a secure temporary file.
    
    Args:
        suffix: File suffix (e.g., ".pdf")
        prefix: File prefix
        dir: Optional directory for temp file
        auto_cleanup: Whether to automatically cleanup on exit
        
    Returns:
        Path to temporary file
    """
    try:
        # Create temp file with secure permissions (0o600)
        fd, temp_path = tempfile.mkstemp(
            suffix=suffix,
            prefix=prefix,
            dir=dir,
            text=False
        )
        
        # Close file descriptor (we just need the path)
        os.close(fd)
        
        temp_file = Path(temp_path)
        
        # Set secure permissions (owner read/write only)
        temp_file.chmod(0o600)
        
        # Track for cleanup if requested
        if auto_cleanup:
            _TEMP_FILES.append(temp_file)
        
        logger.debug(f"Created secure temp file: {temp_file.name}")
        return temp_file
        
    except Exception as e:
        logger.error(f"Failed to create secure temp file: {e}")
        raise


def create_secure_temp_dir(
    prefix: str = "epubs_",
    dir: Optional[Path] = None,
    auto_cleanup: bool = True
) -> Path:
    """
    Create a secure temporary directory.
    
    Args:
        prefix: Directory prefix
        dir: Optional parent directory
        auto_cleanup: Whether to automatically cleanup on exit
        
    Returns:
        Path to temporary directory
    """
    try:
        # Create temp directory with secure permissions (0o700)
        temp_path = tempfile.mkdtemp(
            prefix=prefix,
            dir=dir
        )
        
        temp_dir = Path(temp_path)
        
        # Set secure permissions (owner access only)
        temp_dir.chmod(0o700)
        
        # Track for cleanup if requested
        if auto_cleanup:
            _TEMP_DIRS.append(temp_dir)
        
        logger.debug(f"Created secure temp directory: {temp_dir.name}")
        return temp_dir
        
    except Exception as e:
        logger.error(f"Failed to create secure temp directory: {e}")
        raise


@contextmanager
def secure_temp_file(
    suffix: str = "",
    prefix: str = "epubs_",
    dir: Optional[Path] = None
):
    """
    Context manager for secure temporary file with guaranteed cleanup.
    
    Usage:
        with secure_temp_file(suffix=".pdf") as temp_file:
            # Use temp_file
            process_pdf(temp_file)
        # File automatically deleted here
    
    Args:
        suffix: File suffix
        prefix: File prefix
        dir: Optional directory
        
    Yields:
        Path to temporary file
    """
    temp_file = None
    try:
        temp_file = create_secure_temp_file(
            suffix=suffix,
            prefix=prefix,
            dir=dir,
            auto_cleanup=False  # Manual cleanup in finally
        )
        yield temp_file
    finally:
        if temp_file and temp_file.exists():
            try:
                temp_file.unlink()
                logger.debug(f"Cleaned up temp file: {temp_file.name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp file: {e}")


@contextmanager
def secure_temp_dir(
    prefix: str = "epubs_",
    dir: Optional[Path] = None
):
    """
    Context manager for secure temporary directory with guaranteed cleanup.
    
    Usage:
        with secure_temp_dir() as temp_dir:
            # Use temp_dir
            process_files(temp_dir)
        # Directory automatically deleted here
    
    Args:
        prefix: Directory prefix
        dir: Optional parent directory
        
    Yields:
        Path to temporary directory
    """
    temp_dir = None
    try:
        temp_dir = create_secure_temp_dir(
            prefix=prefix,
            dir=dir,
            auto_cleanup=False  # Manual cleanup in finally
        )
        yield temp_dir
    finally:
        if temp_dir and temp_dir.exists():
            try:
                shutil.rmtree(temp_dir)
                logger.debug(f"Cleaned up temp directory: {temp_dir.name}")
            except Exception as e:
                logger.warning(f"Failed to cleanup temp directory: {e}")


def cleanup_temp_file(temp_file: Path) -> bool:
    """
    Manually cleanup a temporary file.
    
    Args:
        temp_file: Path to temp file
        
    Returns:
        True if successful
    """
    try:
        if temp_file.exists():
            temp_file.unlink()
        
        # Remove from tracking list
        if temp_file in _TEMP_FILES:
            _TEMP_FILES.remove(temp_file)
        
        logger.debug(f"Cleaned up temp file: {temp_file.name}")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to cleanup temp file: {e}")
        return False


def cleanup_temp_dir(temp_dir: Path) -> bool:
    """
    Manually cleanup a temporary directory.
    
    Args:
        temp_dir: Path to temp directory
        
    Returns:
        True if successful
    """
    try:
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        
        # Remove from tracking list
        if temp_dir in _TEMP_DIRS:
            _TEMP_DIRS.remove(temp_dir)
        
        logger.debug(f"Cleaned up temp directory: {temp_dir.name}")
        return True
        
    except Exception as e:
        logger.warning(f"Failed to cleanup temp directory: {e}")
        return False


def get_temp_file_count() -> int:
    """
    Get count of tracked temp files.
    
    Returns:
        Number of temp files being tracked
    """
    return len(_TEMP_FILES)


def get_temp_dir_count() -> int:
    """
    Get count of tracked temp directories.
    
    Returns:
        Number of temp directories being tracked
    """
    return len(_TEMP_DIRS)


def force_cleanup_all():
    """
    Force cleanup of all tracked temporary files and directories.
    
    Use with caution - this will delete all tracked temp files
    even if they're still in use.
    """
    logger.info("Forcing cleanup of all temp files and directories")
    _cleanup_temp_files()
