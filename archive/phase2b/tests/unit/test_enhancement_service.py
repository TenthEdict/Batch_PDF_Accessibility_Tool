#!/usr/bin/env python3
"""
Unit tests for the EnhancementService module.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil

from processor.unified_project.src.services.enhancement_service import EnhancementService


class TestEnhancementService:
    """Test cases for the EnhancementService module."""

    @pytest.fixture
    def service(self):
        """Provide EnhancementService instance for testing."""
        return EnhancementService()

    @pytest.fixture
    def temp_workspace(self):
        """Provide temporary workspace for tests."""
        temp_dir = tempfile.mkdtemp()
        workspace = Path(temp_dir)
        
        # Create standard directory structure
        (workspace / "input").mkdir()
        (workspace / "output").mkdir()
        
        yield workspace
        
        # Cleanup
        shutil.rmtree(temp_dir)

    def test_initialization(self, service):
        """Test service initialization."""
        assert service is not None
        assert hasattr(service, 'enhance_document')

    def test_enhance_document_success(self, service, temp_workspace, sample_pdf_path):
        """Test successful document enhancement."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            result = service.enhance_document(input_path, output_path, mode="academic")
            
            assert result is True
            mock_pipeline.assert_called_once()

    def test_enhance_document_file_not_found(self, service, temp_workspace):
        """Test enhancement with non-existent input file."""
        input_path = temp_workspace / "nonexistent.pdf"
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        result = service.enhance_document(input_path, output_path, mode="academic")
        
        assert result is False

    def test_enhance_document_invalid_mode(self, service, temp_workspace, sample_pdf_path):
        """Test enhancement with invalid processing mode."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        result = service.enhance_document(input_path, output_path, mode="invalid_mode")
        
        assert result is False

    def test_enhance_document_output_directory_creation(self, service, temp_workspace, sample_pdf_path):
        """Test that output directory is created if it doesn't exist."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "new_dir" / "subdir" / "enhanced.pdf"
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            result = service.enhance_document(input_path, output_path, mode="academic")
            
            assert result is True
            assert output_path.parent.exists()

    @patch('processor.unified_project.src.services.enhancement_service.logging')
    def test_enhance_document_logging(self, mock_logging, service, temp_workspace, sample_pdf_path):
        """Test that enhancement operations are properly logged."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            service.enhance_document(input_path, output_path, mode="academic")
            
            # Verify logging calls
            mock_logging.getLogger.assert_called()

    def test_get_enhancement_pipeline_academic_mode(self, service):
        """Test getting enhancement pipeline for academic mode."""
        pipeline = service._get_enhancement_pipeline("academic")
        
        assert pipeline is not None
        assert len(pipeline) > 0

    def test_get_enhancement_pipeline_basic_mode(self, service):
        """Test getting enhancement pipeline for basic mode."""
        pipeline = service._get_enhancement_pipeline("basic")
        
        assert pipeline is not None
        assert len(pipeline) > 0

    def test_get_enhancement_pipeline_invalid_mode(self, service):
        """Test getting enhancement pipeline for invalid mode."""
        with pytest.raises(ValueError):
            service._get_enhancement_pipeline("invalid_mode")

    @patch('processor.unified_project.src.services.enhancement_service.ConfigManager')
    def test_load_configuration(self, mock_config_manager, service):
        """Test configuration loading."""
        mock_config = Mock()
        mock_config.load_config.return_value = {"test": "config"}
        mock_config_manager.return_value = mock_config
        
        config = service._load_configuration("academic")
        
        assert config is not None
        mock_config.load_config.assert_called_once_with("academic")

    def test_validate_input_file_exists(self, service, sample_pdf_path):
        """Test input file validation with existing file."""
        result = service._validate_input_file(sample_pdf_path)
        assert result is True

    def test_validate_input_file_not_exists(self, service, temp_workspace):
        """Test input file validation with non-existent file."""
        input_path = temp_workspace / "nonexistent.pdf"
        result = service._validate_input_file(input_path)
        assert result is False

    def test_validate_input_file_not_pdf(self, service, temp_workspace):
        """Test input file validation with non-PDF file."""
        input_path = temp_workspace / "input" / "test.txt"
        input_path.write_text("This is not a PDF")
        
        result = service._validate_input_file(input_path)
        assert result is False

    @patch('processor.unified_project.src.services.enhancement_service.PerformanceTracker')
    def test_performance_tracking(self, mock_performance_tracker, service, temp_workspace, sample_pdf_path):
        """Test that performance tracking is used during enhancement."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        mock_tracker = Mock()
        mock_performance_tracker.return_value = mock_tracker
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            service.enhance_document(input_path, output_path, mode="academic")
            
            # Verify performance tracking was used
            mock_tracker.track_operation.assert_called()

    def test_enhancement_parameters_passing(self, service, temp_workspace, sample_pdf_path):
        """Test that enhancement parameters are properly passed through."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            # Test with custom parameters
            custom_params = {
                "title": "Test Document",
                "author": "Test Author",
                "language": "en-US"
            }
            
            service.enhance_document(
                input_path, 
                output_path, 
                mode="academic",
                **custom_params
            )
            
            # Verify parameters were passed to pipeline
            mock_pipeline.assert_called_once()
            call_args = mock_pipeline.call_args
            assert call_args is not None

    @patch('processor.unified_project.src.services.enhancement_service.CacheService')
    def test_cache_integration(self, mock_cache_service, service, temp_workspace, sample_pdf_path):
        """Test that cache service is used during enhancement."""
        input_path = sample_pdf_path
        output_path = temp_workspace / "output" / "enhanced.pdf"
        
        mock_cache = Mock()
        mock_cache_service.return_value = mock_cache
        
        # Mock the enhancement pipeline
        with patch.object(service, '_run_enhancement_pipeline') as mock_pipeline:
            mock_pipeline.return_value = True
            
            service.enhance_document(input_path, output_path, mode="academic")
            
            # Verify cache service was used
            mock_cache.get.assert_called()
            mock_cache.set.assert_called()
