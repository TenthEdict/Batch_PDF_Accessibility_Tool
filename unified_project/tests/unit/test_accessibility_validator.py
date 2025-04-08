#!/usr/bin/env python3
"""
Unit tests for the AccessibilityValidator module.
"""

import os
import sys
import unittest
from pathlib import Path
import tempfile
import json

# Add parent directory to path to allow importing modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from src.validation.accessibility_validator import AccessibilityValidator

class TestAccessibilityValidator(unittest.TestCase):
    """Test cases for the AccessibilityValidator module."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.validator = AccessibilityValidator()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()
    
    def test_initialization(self):
        """Test validator initialization."""
        self.assertIsInstance(self.validator, AccessibilityValidator)
    
    def test_file_not_found(self):
        """Test handling of non-existent input file."""
        input_path = self.temp_path / "nonexistent.pdf"
        
        result = self.validator.validate_pdf(input_path)
        
        self.assertIsInstance(result, dict)
        self.assertEqual(result['filename'], "nonexistent.pdf")
        self.assertFalse(result['exists'])
    
    def test_generate_json_report(self):
        """Test JSON report generation."""
        validation_result = {
            'filename': 'test.pdf',
            'path': '/path/to/test.pdf',
            'exists': True,
            'overall_score': 75,
            'passes': False
        }
        
        output_path = self.temp_path / "report.json"
        
        result = self.validator.generate_json_report(validation_result, output_path)
        
        self.assertTrue(result)
        self.assertTrue(output_path.exists())
        
        # Verify JSON content
        with open(output_path, 'r') as f:
            loaded = json.load(f)
        
        self.assertEqual(loaded['filename'], 'test.pdf')
        self.assertEqual(loaded['overall_score'], 75)
        self.assertFalse(loaded['passes'])

if __name__ == "__main__":
    unittest.main()