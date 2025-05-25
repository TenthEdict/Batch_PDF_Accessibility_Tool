#!/usr/bin/env python3
"""
Enhancement service for business logic related to document enhancement.

This service encapsulates all business operations related to document
enhancement and provides a clean interface for enhancement operations.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.interfaces import Enhancer
from ..core.service_container import ServiceContainer
from ..enhancement.pipeline import EnhancementPipeline, EnhancementConfig

logger = logging.getLogger(__name__)


class EnhancementService:
    """
    Service for coordinating document enhancement operations.
    
    This service provides business logic for enhancing documents
    with accessibility features.
    """
    
    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the enhancement service.
        
        Args:
            container: Optional service container for dependency injection
        """
        self.container = container
        self.logger = logging.getLogger(__name__)
        
        # Initialize enhancement pipeline
        self.pipeline = EnhancementPipeline(container)
        
        # Mode configurations
        self._mode_configs = {
            'accessibility': {
                'extract_title_from_h1': True,
                'extract_title_from_filename': True,
                'add_pdfua_identifiers': False,
                'display_doc_title': True,
                'capabilities': [
                    'metadata.title',
                    'metadata.author', 
                    'metadata.language',
                    'viewer.display_title',
                    'metadata.title_from_h1'
                ]
            },
            'academic': {
                'extract_title_from_h1': True,
                'extract_title_from_filename': False,  # Academic papers have proper titles
                'add_pdfua_identifiers': True,
                'display_doc_title': True,
                'capabilities': [
                    'metadata.title',
                    'metadata.author', 
                    'metadata.language',
                    'viewer.display_title',
                    'metadata.title_from_h1',
                    'structure.academic',
                    'accessibility.pdf_ua'
                ]
            },
            'basic': {
                'extract_title_from_h1': False,
                'extract_title_from_filename': True,
                'add_pdfua_identifiers': False,
                'display_doc_title': False,
                'capabilities': [
                    'metadata.title',
                    'metadata.language'
                ]
            }
        }
    
    def enhance_document(self, 
                        input_path: Union[str, Path],
                        output_path: Union[str, Path],
                        mode: str = 'accessibility',
                        title: Optional[str] = None,
                        author: Optional[str] = None,
                        language: str = 'en-US',
                        **kwargs) -> bool:
        """
        Enhance a document with accessibility features.
        
        Args:
            input_path: Path to input document
            output_path: Path for output document
            mode: Enhancement mode (accessibility, academic, basic)
            title: Document title (optional)
            author: Document author (optional)
            language: Document language
            **kwargs: Additional enhancement parameters
            
        Returns:
            True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        try:
            # Get mode configuration
            mode_config = self._get_mode_config(mode)
            
            # Create enhancement configuration
            config = EnhancementConfig(
                title=title,
                author=author,
                language=language,
                extract_title_from_h1=kwargs.get('extract_title_from_h1', mode_config['extract_title_from_h1']),
                extract_title_from_filename=kwargs.get('extract_title_from_filename', mode_config['extract_title_from_filename']),
                add_pdfua_identifiers=kwargs.get('add_pdfua_identifiers', mode_config['add_pdfua_identifiers']),
                display_doc_title=kwargs.get('display_doc_title', mode_config['display_doc_title']),
                capabilities=kwargs.get('capabilities', mode_config['capabilities'])
            )
            
            # Determine enhancer types based on file extension and mode
            enhancer_types = self._determine_enhancer_types(input_path, mode)
            
            # Enhance the document
            success = self.pipeline.enhance_file(input_path, output_path, config, enhancer_types)
            
            if success:
                self.logger.info(f"Successfully enhanced document with mode '{mode}': {output_path}")
            else:
                self.logger.error(f"Failed to enhance document: {input_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enhancing document {input_path}: {e}")
            return False
    
    def get_enhancement_capabilities(self, mode: str = 'accessibility') -> List[str]:
        """
        Get available enhancement capabilities for a specific mode.
        
        Args:
            mode: Enhancement mode
            
        Returns:
            List of available capabilities
        """
        mode_config = self._get_mode_config(mode)
        enhancer_types = self._get_mode_enhancer_types(mode)
        
        # Get capabilities from pipeline
        pipeline_capabilities = self.pipeline.get_available_capabilities(enhancer_types)
        
        # Filter by mode capabilities
        mode_capabilities = mode_config.get('capabilities', [])
        
        # Return intersection of available and mode-specific capabilities
        return [cap for cap in pipeline_capabilities if cap in mode_capabilities]
    
    def validate_enhancement_request(self, 
                                   input_path: Union[str, Path],
                                   mode: str) -> Dict[str, Any]:
        """
        Validate an enhancement request and provide feedback.
        
        Args:
            input_path: Path to input document
            mode: Enhancement mode
            
        Returns:
            Dictionary with validation results
        """
        input_path = Path(input_path)
        
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'recommendations': []
        }
        
        # Check file exists
        if not input_path.exists():
            result['valid'] = False
            result['errors'].append(f"Input file not found: {input_path}")
            return result
        
        # Check file is readable
        if not input_path.is_file():
            result['valid'] = False
            result['errors'].append(f"Input path is not a file: {input_path}")
            return result
        
        # Check mode is supported
        if mode not in self._mode_configs:
            result['valid'] = False
            result['errors'].append(f"Unsupported mode: {mode}. Available: {', '.join(self._mode_configs.keys())}")
            return result
        
        # Check file format is supported
        enhancer_types = self._determine_enhancer_types(input_path, mode)
        if not enhancer_types:
            result['valid'] = False
            result['errors'].append(f"Unsupported file format: {input_path.suffix}")
            return result
        
        # Provide recommendations based on file and mode
        if mode == 'academic' and input_path.suffix.lower() != '.pdf':
            result['warnings'].append("Academic mode is optimized for PDF documents")
        
        if input_path.stat().st_size > 100 * 1024 * 1024:  # 100MB
            result['warnings'].append("Large file detected. Processing may take longer.")
        
        return result
    
    def get_supported_modes(self) -> List[str]:
        """
        Get list of supported enhancement modes.
        
        Returns:
            List of mode identifiers
        """
        return list(self._mode_configs.keys())
    
    def get_mode_description(self, mode: str) -> Dict[str, Any]:
        """
        Get description and configuration for an enhancement mode.
        
        Args:
            mode: Enhancement mode
            
        Returns:
            Dictionary with mode description and settings
        """
        if mode not in self._mode_configs:
            raise ValueError(f"Unknown mode: {mode}")
        
        descriptions = {
            'accessibility': {
                'name': 'Accessibility Enhancement',
                'description': 'General accessibility improvements for documents',
                'best_for': ['General documents', 'Web content', 'Basic PDFs']
            },
            'academic': {
                'name': 'Academic Document Processing', 
                'description': 'Specialized processing for academic papers and journals',
                'best_for': ['Research papers', 'Academic journals', 'Theses']
            },
            'basic': {
                'name': 'Basic Enhancement',
                'description': 'Minimal enhancements with basic metadata improvements',
                'best_for': ['Simple documents', 'Quick processing', 'Legacy content']
            }
        }
        
        result = descriptions.get(mode, {})
        result['configuration'] = self._mode_configs[mode].copy()
        
        return result
    
    def _get_mode_config(self, mode: str) -> Dict[str, Any]:
        """
        Get configuration for an enhancement mode.
        
        Args:
            mode: Enhancement mode
            
        Returns:
            Mode configuration dictionary
            
        Raises:
            ValueError: If mode is not supported
        """
        if mode not in self._mode_configs:
            raise ValueError(f"Unsupported mode: {mode}. Available: {', '.join(self._mode_configs.keys())}")
        
        return self._mode_configs[mode]
    
    def _get_mode_enhancer_types(self, mode: str) -> List[str]:
        """
        Get enhancer types for a specific mode.
        
        Args:
            mode: Enhancement mode
            
        Returns:
            List of enhancer type identifiers
        """
        # For now, all modes use the same enhancer types based on file format
        # This could be expanded to have mode-specific enhancer selection
        return ['pdf', 'basic']
    
    def _determine_enhancer_types(self, file_path: Path, mode: str) -> List[str]:
        """
        Determine appropriate enhancer types based on file and mode.
        
        Args:
            file_path: Path to the file
            mode: Enhancement mode
            
        Returns:
            List of enhancer type identifiers
        """
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return ['pdf']
        elif extension in ['.docx', '.doc']:
            return ['basic']  # Could add Word-specific enhancer in future
        elif extension in ['.txt', '.md']:
            return ['basic']
        else:
            # Unknown format, try basic enhancer
            return ['basic']