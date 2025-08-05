#!/usr/bin/env python3
"""
Integration tests for the AdvancedBatchProcessor module.
"""

import sys
import unittest
from pathlib import Path
import tempfile

# Add project root to path to allow importing modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from processor.unified_project.src.batch.advanced_batch_processor import (
    AdvancedBatchProcessor,
    BatchProcessingConfiguration
)


class TestAdvancedBatchProcessor(unittest.TestCase):
    """Integration test cases for the AdvancedBatchProcessor module."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp_dir.name)
        
        # Create input and output directories
        self.input_dir = self.temp_path / "input"
        self.output_dir = self.temp_path / "output"
        self.input_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create test configuration
        self.config = BatchProcessingConfiguration(
            input_dir=str(self.input_dir),
            output_dir=str(self.output_dir)
        )

    def tearDown(self):
        """Tear down test fixtures."""
        self.temp_dir.cleanup()

    def test_initialization(self):
        """Test batch processor initialization."""
        processor = AdvancedBatchProcessor(self.config)
        self.assertIsInstance(processor, AdvancedBatchProcessor)
        self.assertEqual(processor.config, self.config)

    def test_empty_directory_processing(self):
        """Test processing with no PDF files in input directory."""
        processor = AdvancedBatchProcessor(self.config)
        
        # Should return False (no files to process) but not crash
        result = processor.process_batch()
        self.assertFalse(result)

    def test_configuration_validation(self):
        """Test configuration validation."""
        # Valid configuration should pass
        self.assertTrue(self.config.validate_configuration())
        
        # Invalid configuration (non-existent input dir) should fail
        invalid_config = BatchProcessingConfiguration(
            input_dir=str(self.temp_path / "nonexistent"),
            output_dir=str(self.output_dir)
        )
        self.assertFalse(invalid_config.validate_configuration())


if __name__ == "__main__":
    unittest.main()