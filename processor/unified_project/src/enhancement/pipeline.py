#!/usr/bin/env python3
"""
Unified enhancement pipeline for document accessibility processing.

This module provides a centralized enhancement pipeline that orchestrates
multiple enhancers to improve document accessibility.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass

from ..core.interfaces import Enhancer, DocumentProcessor
from ..core.service_container import ServiceContainer
from ..enhancers.pdf_enhancer import PDFEnhancer
from ..enhancers.basic_enhancer import BasicEnhancer

logger = logging.getLogger(__name__)


@dataclass
class EnhancementConfig:
    """Configuration for the enhancement pipeline."""
    
    # Title extraction settings
    extract_title_from_h1: bool = True
    extract_title_from_filename: bool = True
    
    # Metadata settings
    add_pdfua_identifiers: bool = False
    display_doc_title: bool = True
    
    # Document metadata
    title: Optional[str] = None
    author: Optional[str] = None
    language: str = 'en-US'
    
    # Enhancement capabilities to apply
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            # Default capabilities to apply
            self.capabilities = [
                'metadata.title',
                'metadata.author', 
                'metadata.language',
                'viewer.display_title',
                'metadata.title_from_h1'
            ]


class EnhancementPipeline:
    """
    Unified enhancement pipeline that orchestrates multiple enhancers.
    
    This class provides a centralized way to apply accessibility enhancements
    to documents using a configurable pipeline of enhancers.
    """
    
    def __init__(self, 
                 container: Optional[ServiceContainer] = None,
                 environment: Optional[str] = None):
        """
        Initialize the enhancement pipeline.
        
        Args:
            container: Optional service container for dependency injection
            environment: Optional environment name for configuration
        """
        self.container = container
        self.environment = environment
        self.logger = logging.getLogger(__name__)
        
        # Registry of available enhancers
        self._enhancer_registry: Dict[str, Type[Enhancer]] = {
            'pdf': PDFEnhancer,
            'basic': BasicEnhancer,
        }
        
        # Cache for instantiated enhancers
        self._enhancer_cache: Dict[str, Enhancer] = {}
    
    def register_enhancer(self, name: str, enhancer_class: Type[Enhancer]):
        """
        Register a new enhancer type.
        
        Args:
            name: Identifier for the enhancer
            enhancer_class: Enhancer class to register
        """
        self._enhancer_registry[name] = enhancer_class
        self.logger.info(f"Registered enhancer: {name}")
    
    def get_enhancer(self, name: str) -> Enhancer:
        """
        Get an enhancer instance by name.
        
        Args:
            name: Enhancer identifier
            
        Returns:
            Enhancer instance
            
        Raises:
            ValueError: If enhancer is not registered
        """
        if name not in self._enhancer_registry:
            raise ValueError(f"Unknown enhancer: {name}")
        
        # Return cached instance if available
        if name in self._enhancer_cache:
            return self._enhancer_cache[name]
        
        # Create new instance
        enhancer_class = self._enhancer_registry[name]
        enhancer = enhancer_class(self.environment)
        self._enhancer_cache[name] = enhancer
        
        return enhancer
    
    def enhance_document(self, 
                        document: Any,
                        config: EnhancementConfig,
                        enhancer_types: Optional[List[str]] = None) -> Any:
        """
        Enhance a document using the specified enhancers.
        
        Args:
            document: Document to enhance
            config: Enhancement configuration
            enhancer_types: List of enhancer types to use (default: ['pdf'])
            
        Returns:
            Enhanced document
        """
        if enhancer_types is None:
            enhancer_types = ['pdf']
        
        enhanced_doc = document
        
        for enhancer_type in enhancer_types:
            try:
                enhancer = self.get_enhancer(enhancer_type)
                
                # Convert config to kwargs
                kwargs = self._config_to_kwargs(config)
                
                # Apply enhancement
                enhanced_doc = enhancer.enhance(enhanced_doc, **kwargs)
                
                self.logger.info(f"Applied {enhancer_type} enhancement")
                
            except Exception as e:
                self.logger.error(f"Error applying {enhancer_type} enhancement: {e}")
                raise
        
        return enhanced_doc
    
    def enhance_file(self,
                    input_path: Union[str, Path],
                    output_path: Union[str, Path],
                    config: EnhancementConfig,
                    enhancer_types: Optional[List[str]] = None) -> bool:
        """
        Enhance a document file using the pipeline.
        
        Args:
            input_path: Path to input document
            output_path: Path for output document
            config: Enhancement configuration
            enhancer_types: List of enhancer types to use
            
        Returns:
            True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            self.logger.error(f"Input file not found: {input_path}")
            return False
        
        # Add filename to config for title extraction
        config.filename = input_path.name
        
        try:
            # Determine enhancer types based on file extension
            if enhancer_types is None:
                enhancer_types = self._determine_enhancer_types(input_path)
            
            # Get the primary enhancer for file operations
            primary_enhancer = self.get_enhancer(enhancer_types[0])
            
            # Convert config to kwargs
            kwargs = self._config_to_kwargs(config)
            
            # Use the primary enhancer for file operations
            success = primary_enhancer.enhance_file(input_path, output_path, **kwargs)
            
            if success:
                self.logger.info(f"Successfully enhanced file: {output_path}")
            else:
                self.logger.error(f"Failed to enhance file: {input_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"Error enhancing file {input_path}: {e}")
            return False
    
    def get_available_capabilities(self, enhancer_types: Optional[List[str]] = None) -> List[str]:
        """
        Get all available enhancement capabilities.
        
        Args:
            enhancer_types: List of enhancer types to check (default: all)
            
        Returns:
            List of capability identifiers
        """
        if enhancer_types is None:
            enhancer_types = list(self._enhancer_registry.keys())
        
        capabilities = []
        for enhancer_type in enhancer_types:
            try:
                enhancer = self.get_enhancer(enhancer_type)
                capabilities.extend(enhancer.get_capabilities())
            except Exception as e:
                self.logger.warning(f"Error getting capabilities for {enhancer_type}: {e}")
        
        return list(set(capabilities))  # Remove duplicates
    
    def _determine_enhancer_types(self, file_path: Path) -> List[str]:
        """
        Determine appropriate enhancer types based on file extension.
        
        Args:
            file_path: Path to the file
            
        Returns:
            List of enhancer type identifiers
        """
        extension = file_path.suffix.lower()
        
        if extension == '.pdf':
            return ['pdf']
        else:
            # Default to basic enhancer for unknown types
            return ['basic']
    
    def _config_to_kwargs(self, config: EnhancementConfig) -> Dict[str, Any]:
        """
        Convert enhancement config to kwargs dict.
        
        Args:
            config: Enhancement configuration
            
        Returns:
            Dictionary of keyword arguments
        """
        kwargs = {
            'title': config.title,
            'author': config.author,
            'language': config.language,
            'extract_title_from_h1': config.extract_title_from_h1,
            'extract_title_from_filename': config.extract_title_from_filename,
            'display_doc_title': config.display_doc_title,
        }
        
        # Add filename if available
        if hasattr(config, 'filename'):
            kwargs['filename'] = config.filename
        
        return kwargs


class EnhancementOrchestrator(DocumentProcessor):
    """
    Document processor that uses the enhancement pipeline.
    
    This class implements the DocumentProcessor interface and delegates
    to the enhancement pipeline for actual processing.
    """
    
    def __init__(self, 
                 pipeline: Optional[EnhancementPipeline] = None,
                 environment: Optional[str] = None):
        """
        Initialize the enhancement orchestrator.
        
        Args:
            pipeline: Optional enhancement pipeline instance
            environment: Optional environment name
        """
        self.pipeline = pipeline or EnhancementPipeline(environment=environment)
        self.environment = environment
        self.logger = logging.getLogger(__name__)
    
    def process(self, 
               input_path: Union[str, Path], 
               output_path: Union[str, Path], 
               **kwargs) -> bool:
        """
        Process a document using the enhancement pipeline.
        
        Args:
            input_path: Path to input document
            output_path: Path for output document
            **kwargs: Processing parameters
            
        Returns:
            True if processing was successful, False otherwise
        """
        # Create enhancement config from kwargs
        config = EnhancementConfig(
            title=kwargs.get('title'),
            author=kwargs.get('author'),
            language=kwargs.get('language', 'en-US'),
            extract_title_from_h1=kwargs.get('extract_title_from_h1', True),
            extract_title_from_filename=kwargs.get('extract_title_from_filename', True),
            display_doc_title=kwargs.get('display_doc_title', True),
            add_pdfua_identifiers=kwargs.get('add_pdfua_identifiers', False)
        )
        
        # Determine enhancer types
        enhancer_types = kwargs.get('enhancer_types')
        
        return self.pipeline.enhance_file(input_path, output_path, config, enhancer_types)