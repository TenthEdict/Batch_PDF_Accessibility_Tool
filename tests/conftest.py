#!/usr/bin/env python3
"""
Test configuration and shared fixtures for ePubs Accessibility Enhancement Project.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
import logging

# Configure test logging
logging.basicConfig(level=logging.WARNING)


@pytest.fixture(scope="session")
def test_data_dir() -> Path:
    """Provide test data directory."""
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def sample_pdfs_dir(test_data_dir) -> Path:
    """Provide directory with sample PDF files for testing."""
    pdf_dir = test_data_dir / "sample_pdfs"
    pdf_dir.mkdir(exist_ok=True)
    return pdf_dir


@pytest.fixture
def temp_workspace() -> Generator[Path, None, None]:
    """Provide temporary workspace for tests."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)
    
    # Create standard directory structure
    (workspace / "input").mkdir()
    (workspace / "output").mkdir()
    (workspace / "logs").mkdir()
    (workspace / "cache").mkdir()
    
    yield workspace
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def mock_config() -> Dict[str, Any]:
    """Provide mock configuration for testing."""
    return {
        "ocr": {
            "language": "eng",
            "intelligent_ocr": True,
            "text_threshold": 100,
            "sample_pages": 3
        },
        "compression": {
            "adobe_compatible": True,
            "target_dpi": 150
        },
        "performance": {
            "max_workers": 2,
            "timeout": 300
        }
    }


@pytest.fixture
def sample_pdf_path(sample_pdfs_dir) -> Path:
    """Provide path to a sample PDF for testing."""
    # Create a minimal test PDF if none exists
    test_pdf = sample_pdfs_dir / "test_document.pdf"
    if not test_pdf.exists():
        # Create a simple test PDF using reportlab
        try:
            from reportlab.pdfgen import canvas
            from reportlab.lib.pagesizes import letter
            
            c = canvas.Canvas(str(test_pdf), pagesize=letter)
            c.drawString(100, 750, "Test Document for ePubs Processing")
            c.drawString(100, 700, "This is a sample PDF for testing purposes.")
            c.save()
        except ImportError:
            # Fallback: create empty file
            test_pdf.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
    
    return test_pdf


@pytest.fixture
def mock_enhancement_service():
    """Provide mock enhancement service for testing."""
    from unittest.mock import Mock
    service = Mock()
    service.enhance_document.return_value = True
    return service


@pytest.fixture
def mock_performance_tracker():
    """Provide mock performance tracker for testing."""
    from unittest.mock import Mock
    tracker = Mock()
    tracker.track_operation.return_value.__enter__ = Mock()
    tracker.track_operation.return_value.__exit__ = Mock(return_value=None)
    return tracker


# Platform-specific test markers
def pytest_configure(config):
    """Configure custom test markers."""
    config.addinivalue_line(
        "markers", "macos: mark test as macOS specific"
    )
    config.addinivalue_line(
        "markers", "windows: mark test as Windows specific"
    )
    config.addinivalue_line(
        "markers", "linux: mark test as Linux specific"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )
    config.addinivalue_line(
        "markers", "ocr: mark test as requiring OCR engine"
    )


# Skip tests based on platform
def pytest_collection_modifyitems(config, items):
    """Skip platform-specific tests on incompatible platforms."""
    import platform
    
    current_platform = platform.system().lower()
    
    for item in items:
        if "macos" in item.keywords and current_platform != "darwin":
            item.add_marker(pytest.mark.skip(reason="macOS specific test"))
        elif "windows" in item.keywords and current_platform != "windows":
            item.add_marker(pytest.mark.skip(reason="Windows specific test"))
        elif "linux" in item.keywords and current_platform != "linux":
            item.add_marker(pytest.mark.skip(reason="Linux specific test"))