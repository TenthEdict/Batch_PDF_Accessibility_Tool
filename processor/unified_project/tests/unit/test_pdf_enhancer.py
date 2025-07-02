#!/usr/bin/env python3
"""
Unit tests for the PDFEnhancer module.
"""

import os
import sys
import unittest
from pathlib import Path
import tempfile

# Add parent directory to path to allow importing modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent.parent))

from processor.unified_project.src.enhancers.pdf_enhancer import PDFEnhancer


class TestPDFEnhancer(unittest.TestCase):
    """Test cases for the PDFEnhancer module."""

    def setUp(self):
        """Set up test fixtures."""
        self.enhancer = PDFEnhancer()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test enhancer initialization."""
        self.assertIsInstance(self.enhancer, PDFEnhancer)

    def test_file_not_found(self):
        """Test handling of non-existent input file."""
        input_path = self.temp_path / "nonexistent.pdf"
        output_path = self.temp_path / "output.pdf"

        result = self.enhancer.enhance_pdf_accessibility(input_path, output_path)

        self.assertFalse(result)
        self.assertFalse(output_path.exists())


if __name__ == "__main__":
    unittest.main()
