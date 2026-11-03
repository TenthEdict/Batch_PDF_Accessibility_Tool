#!/usr/bin/env python3
"""
Integration tests for batch processing functionality.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, Mock
import json

from processor.unified_project.src.batch.advanced_batch_processor import (
    AdvancedBatchProcessor,
    BatchProcessingConfiguration
)


class TestBatchProcessingIntegration:
    """Integration tests for batch processing workflows."""

    @pytest.fixture
    def batch_config(self, temp_workspace):
        """Provide batch processing configuration."""
        return BatchProcessingConfiguration(
            input_dir=str(temp_workspace / "input"),
            output_dir=str(temp_workspace / "output"),
            log_dir=str(temp_workspace / "logs"),
            enable_detailed_logging=True,
            enhancement_params={
                "mode": "academic",
                "title": "Batch Test Document"
            }
        )

    @pytest.fixture
    def sample_pdfs(self, temp_workspace):
        """Create sample PDF files for batch processing."""
        input_dir = temp_workspace / "input"
        input_dir.mkdir(exist_ok=True)
        
        # Create multiple test PDFs
        pdf_files = []
        for i in range(3):
            pdf_path = input_dir / f"test_document_{i}.pdf"
            # Create minimal PDF content
            pdf_path.write_bytes(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n")
            pdf_files.append(pdf_path)
        
        return pdf_files

    def test_batch_processor_initialization(self, batch_config):
        """Test batch processor initialization."""
        processor = AdvancedBatchProcessor(batch_config)
        
        assert processor is not None
        assert processor.config == batch_config
        assert hasattr(processor, 'process_batch')

    def test_batch_processing_empty_directory(self, batch_config):
        """Test batch processing with empty input directory."""
        processor = AdvancedBatchProcessor(batch_config)
        
        result = processor.process_batch()
        
        # Should return False when no files to process
        assert result is False

    @patch('processor.unified_project.src.services.enhancement_service.EnhancementService')
    def test_batch_processing_success(self, mock_enhancement_service, batch_config, sample_pdfs):
        """Test successful batch processing of multiple files."""
        # Mock the enhancement service
        mock_service = Mock()
        mock_service.enhance_document.return_value = True
        mock_enhancement_service.return_value = mock_service
        
        processor = AdvancedBatchProcessor(batch_config)
        
        result = processor.process_batch()
        
        # Should return True for successful processing
        assert result is True
        
        # Verify enhancement service was called for each PDF
        assert mock_service.enhance_document.call_count == len(sample_pdfs)

    @patch('processor.unified_project.src.services.enhancement_service.EnhancementService')
    def test_batch_processing_partial_failure(self, mock_enhancement_service, batch_config, sample_pdfs):
        """Test batch processing with some files failing."""
        # Mock the enhancement service to fail on some files
        mock_service = Mock()
        mock_service.enhance_document.side_effect = [True, False, True]
        mock_enhancement_service.return_value = mock_service
        
        processor = AdvancedBatchProcessor(batch_config)
        
        result = processor.process_batch()
        
        # Should still return True (batch processing continues despite individual failures)
        assert result is True
        
        # Verify enhancement service was called for each PDF
        assert mock_service.enhance_document.call_count == len(sample_pdfs)

    def test_batch_processing_output_file_naming(self, batch_config, sample_pdfs):
        """Test that output files are named correctly with _enhanced suffix."""
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Verify output file naming
            for i, pdf_path in enumerate(sample_pdfs):
                expected_output = Path(batch_config.output_dir) / f"test_document_{i}_enhanced.pdf"
                # Check that the enhancement service was called with correct output path
                calls = mock_enhancement.enhance_document.call_args_list
                assert any(str(expected_output) in str(call) for call in calls)

    def test_batch_processing_logging(self, batch_config, sample_pdfs):
        """Test that batch processing creates detailed logs."""
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Check that log directory was created
            log_dir = Path(batch_config.log_dir)
            assert log_dir.exists()
            
            # Check that log files were created
            log_files = list(log_dir.glob("*.log"))
            assert len(log_files) > 0

    def test_batch_processing_metrics_collection(self, batch_config, sample_pdfs):
        """Test that batch processing collects metrics."""
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Check that metrics were collected
            metrics = processor.metrics
            assert metrics is not None
            assert hasattr(metrics, 'get_summary')

    def test_batch_processing_error_handling(self, batch_config, sample_pdfs):
        """Test that batch processing handles errors gracefully."""
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            # Simulate an exception during processing
            mock_enhancement.enhance_document.side_effect = Exception("Processing error")
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            
            # Should not raise exception, should handle gracefully
            result = processor.process_batch()
            
            # Should return True (batch processing continues despite errors)
            assert result is True

    def test_batch_processing_configuration_validation(self):
        """Test batch processing configuration validation."""
        # Test with invalid configuration
        with pytest.raises(ValueError):
            BatchProcessingConfiguration(
                input_dir="",  # Invalid empty path
                output_dir="",
                log_dir=""
            )

    @patch('processor.unified_project.src.services.enhancement_service.EnhancementService')
    def test_batch_processing_with_custom_parameters(self, mock_enhancement_service, batch_config, sample_pdfs):
        """Test batch processing with custom enhancement parameters."""
        mock_service = Mock()
        mock_service.enhance_document.return_value = True
        mock_enhancement_service.return_value = mock_service
        
        # Add custom parameters to configuration
        batch_config.enhancement_params.update({
            "title": "Custom Title",
            "author": "Custom Author",
            "language": "en-US"
        })
        
        processor = AdvancedBatchProcessor(batch_config)
        processor.process_batch()
        
        # Verify custom parameters were passed to enhancement service
        calls = mock_service.enhance_document.call_args_list
        for call in calls:
            kwargs = call.kwargs
            assert kwargs.get("title") == "Custom Title"
            assert kwargs.get("author") == "Custom Author"
            assert kwargs.get("language") == "en-US"

    def test_batch_processing_file_filtering(self, batch_config, temp_workspace):
        """Test that batch processing only processes PDF files."""
        input_dir = temp_workspace / "input"
        input_dir.mkdir(exist_ok=True)
        
        # Create mixed file types
        pdf_file = input_dir / "test.pdf"
        txt_file = input_dir / "test.txt"
        doc_file = input_dir / "test.docx"
        
        pdf_file.write_bytes(b"%PDF-1.4\n")
        txt_file.write_text("This is a text file")
        doc_file.write_bytes(b"PK\x03\x04")  # Minimal DOCX header
        
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Should only process PDF files
            assert mock_enhancement.enhance_document.call_count == 1

    def test_batch_processing_output_directory_creation(self, batch_config, sample_pdfs):
        """Test that output directory is created if it doesn't exist."""
        # Remove output directory
        output_dir = Path(batch_config.output_dir)
        if output_dir.exists():
            shutil.rmtree(output_dir)
        
        with patch('processor.unified_project.src.services.enhancement_service.EnhancementService') as mock_service:
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Output directory should be created
            assert output_dir.exists()

    @patch('processor.unified_project.src.services.enhancement_service.EnhancementService')
    def test_batch_processing_performance_tracking(self, mock_enhancement_service, batch_config, sample_pdfs):
        """Test that batch processing tracks performance metrics."""
        with patch('processor.unified_project.src.monitoring.performance_tracker.PerformanceTracker') as mock_tracker:
            mock_performance = Mock()
            mock_tracker.return_value = mock_performance
            
            mock_enhancement = Mock()
            mock_enhancement.enhance_document.return_value = True
            mock_enhancement_service.return_value = mock_enhancement
            
            processor = AdvancedBatchProcessor(batch_config)
            processor.process_batch()
            
            # Verify performance tracking was used
            mock_performance.track_operation.assert_called()
