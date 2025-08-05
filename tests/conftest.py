"""
Shared pytest fixtures and configuration for ePubs Accessibility Tests.

This module provides common test fixtures, mock objects, and configuration
that can be used across all test modules.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator


@pytest.fixture
def temp_directory() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test files.
    
    Yields:
        Path: Temporary directory path that will be cleaned up after test
    """
    temp_dir = tempfile.mkdtemp()
    try:
        yield Path(temp_dir)
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_pdf_path(temp_directory: Path) -> Path:
    """
    Create a mock PDF file for testing (empty file with .pdf extension).
    
    Args:
        temp_directory: Temporary directory from temp_directory fixture
        
    Returns:
        Path: Path to the mock PDF file
    """
    pdf_path = temp_directory / "sample.pdf"
    pdf_path.touch()  # Create empty file
    return pdf_path


@pytest.fixture
def project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: Project root directory
    """
    return Path(__file__).parent.parent


@pytest.fixture
def config_directory(project_root: Path) -> Path:
    """
    Get the configuration directory path.
    
    Args:
        project_root: Project root from project_root fixture
        
    Returns:
        Path: Configuration directory path
    """
    return project_root / "processor" / "unified_project" / "config"