#!/usr/bin/env python3
"""
Enhancement service for business logic related to document enhancement.

This service encapsulates all business operations related to document
enhancement and provides a clean interface for enhancement operations.
"""

import logging
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.service_container import ServiceContainer
from ..enhancers.ocr_enhancer import OCREnhancer
from ..enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer
from ..enhancers.compression_enhancer import CompressionEnhancer

# Optional ML enhancer imports
try:
    from ..enhancers.ml_enhancer import MLEnhancer
    ML_ENHANCER_AVAILABLE = True
except ImportError:
    MLEnhancer = None
    ML_ENHANCER_AVAILABLE = False

# Optional intelligent OCR enhancer import
try:
    from ..enhancers.intelligent_ocr_enhancer import IntelligentOCREnhancer
    INTELLIGENT_OCR_AVAILABLE = True
except ImportError:
    IntelligentOCREnhancer = None
    INTELLIGENT_OCR_AVAILABLE = False

logger = logging.getLogger(__name__)


class EnhancementService:
    """
    Service for coordinating document enhancement operations.
    """

    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the enhancement service.
        """
        self.container = container
        self.logger = logging.getLogger(__name__)
        self.ocr_enhancer = OCREnhancer()
        self.compression_enhancer = CompressionEnhancer()
        self.minimal_pdf_enhancer = MinimalPDFEnhancer()
        
        # Initialize optional ML enhancers
        self.ml_enhancer = None
        self.intelligent_ocr_enhancer = None
        
        # Try to initialize intelligent OCR enhancer
        if INTELLIGENT_OCR_AVAILABLE:
            try:
                self.intelligent_ocr_enhancer = IntelligentOCREnhancer()
                self.logger.info("Intelligent OCR enhancer initialized")
            except Exception as e:
                self.logger.warning(f"Could not initialize intelligent OCR enhancer: {e}")

    def enhance_document(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        mode: str = "academic",
        **kwargs,
    ) -> bool:
        """
        Enhance academic document with OCR, compression, and minimal accessibility features.
        
        Optimized pipeline for academic papers distributed on digital commons:
        1. OCR with aggressive web compression
        2. Additional image compression optimization
        3. Minimal PDF/UA-1 compliance (clean structure)
        
        Args:
            input_path: Path to the input document
            output_path: Path where the enhanced document should be saved
            mode: Processing mode (default: "academic")
            **kwargs: Additional enhancement parameters
            
        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)

        if not input_path.exists():
            self.logger.error(f"Input file not found: {input_path}")
            return False

        try:
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_path = Path(temp_dir)
                ocr_output_path = temp_path / "ocr_enhanced.pdf"
                compressed_output_path = temp_path / "compressed.pdf"

                # Step 1: Intelligent OCR Processing (Default for academic documents)
                if self.intelligent_ocr_enhancer:
                    self.logger.info("Step 1: Applying intelligent OCR with ML-enhanced processing for academic documents...")
                    ocr_success = self.intelligent_ocr_enhancer.enhance_file(
                        input_path, ocr_output_path
                    )
                    if ocr_success:
                        # Get processing statistics
                        stats = self.intelligent_ocr_enhancer.get_processing_statistics()
                        self.logger.info(f"Intelligent OCR completed. Success rate: {stats.get('success_rate', 0):.2%}")
                    else:
                        self.logger.warning("Intelligent OCR failed, falling back to standard OCR...")
                        ocr_success = self.ocr_enhancer.enhance_file(input_path, ocr_output_path)
                else:
                    self.logger.info("Step 1: Applying standard OCR with aggressive web compression...")
                    ocr_success = self.ocr_enhancer.enhance_file(
                        input_path, ocr_output_path
                    )
                
                if not ocr_success:
                    self.logger.error("OCR enhancement failed.")
                    return False
                self.logger.info("OCR enhancement completed successfully.")

                # Step 2: Additional Image Compression Optimization
                self.logger.info("Step 2: Applying additional image compression optimization...")
                compression_success = self.compression_enhancer.enhance_file(
                    ocr_output_path, compressed_output_path
                )
                if not compression_success:
                    self.logger.error("Compression enhancement failed.")
                    return False
                self.logger.info("Image compression optimization completed successfully.")

                # Step 3: Minimal PDF/UA-1 Compliance (Clean Structure)
                current_input_path = compressed_output_path
                self.logger.info("Step 3: Applying minimal PDF/UA-1 compliance with clean structure...")
                
                # Pass original filename and source path to preserve title
                pdf_kwargs = kwargs.copy()
                pdf_kwargs['original_filename'] = str(input_path)
                pdf_kwargs['source_path'] = str(input_path)  # Different name to avoid conflict with input_path parameter
                
                pdf_enhance_success = self.minimal_pdf_enhancer.enhance_file(
                    current_input_path, output_path, **pdf_kwargs
                )
                if not pdf_enhance_success:
                    self.logger.error("Minimal PDF enhancement failed.")
                    return False
                self.logger.info("Minimal PDF/UA-1 compliance completed successfully.")

            enhancement_summary = [
                "OCR with aggressive web compression and academic Tesseract settings",
                "Additional image compression optimization for web distribution",
                "Minimal PDF/UA-1 compliance with clean structure (no auto-tagging)"
            ]
            
            self.logger.info(f"Successfully enhanced academic paper with: {', '.join(enhancement_summary)}")
            self.logger.info(f"Enhanced document saved to: {output_path}")
            return True

        except Exception as e:
            self.logger.error(f"An error occurred during the enhancement pipeline: {e}", exc_info=True)
            return False

    def get_available_enhancers(self) -> Dict[str, bool]:
        """
        Get the availability status of all enhancers.
        
        Returns:
            Dict[str, bool]: Dictionary mapping enhancer names to availability status
        """
        return {
            "ocr_enhancer": True,           # Always available if class loads
            "compression_enhancer": True,   # Always available if class loads  
            "minimal_pdf_enhancer": True,   # Always available if class loads
            "ml_enhancer": ML_ENHANCER_AVAILABLE,
            "intelligent_ocr_enhancer": INTELLIGENT_OCR_AVAILABLE,
        }
    
    def get_enhancement_capabilities(self) -> Dict[str, List[str]]:
        """
        Get the capabilities of all available enhancers.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping enhancer names to their capabilities
        """
        capabilities = {
            "ocr_enhancer": self.ocr_enhancer.get_capabilities(),
            "compression_enhancer": self.compression_enhancer.get_capabilities(),
            "minimal_pdf_enhancer": self.minimal_pdf_enhancer.get_capabilities()
        }
        
        # Add optional enhancers if available
        if self.ml_enhancer:
            capabilities["ml_enhancer"] = self.ml_enhancer.get_capabilities()
        
        if self.intelligent_ocr_enhancer:
            capabilities["intelligent_ocr_enhancer"] = self.intelligent_ocr_enhancer.get_capabilities()
        
        return capabilities

    def _get_enhancement_pipeline(self, mode: str) -> List[str]:
        """
        Get the enhancement pipeline for a specific mode.
        
        Args:
            mode: Processing mode (academic, basic, etc.)
            
        Returns:
            List[str]: List of enhancement steps for the pipeline
            
        Raises:
            ValueError: If mode is not supported
        """
        pipelines = {
            "academic": ["ocr", "compression", "pdf_enhancement"],
            "basic": ["ocr", "pdf_enhancement"],
            "minimal": ["pdf_enhancement"]
        }
        
        if mode not in pipelines:
            raise ValueError(f"Unsupported processing mode: {mode}")
        
        return pipelines[mode]

    def _load_configuration(self, mode: str) -> Dict[str, Any]:
        """
        Load configuration for a specific mode.
        
        Args:
            mode: Processing mode
            
        Returns:
            Dict[str, Any]: Configuration dictionary
        """
        try:
            from ..config.config_manager import ConfigManager
            config_manager = ConfigManager()
            return config_manager.load_config(mode)
        except ImportError:
            # Fallback to default configuration
            return {
                "mode": mode,
                "language": "en-US",
                "enable_ocr": True,
                "enable_compression": True
            }

    def _validate_input_file(self, input_path: Path) -> bool:
        """
        Validate input file exists and is a PDF.
        
        Args:
            input_path: Path to input file
            
        Returns:
            bool: True if valid, False otherwise
        """
        if not input_path.exists():
            self.logger.error(f"Input file does not exist: {input_path}")
            return False
        
        if not input_path.suffix.lower() == '.pdf':
            self.logger.error(f"Input file is not a PDF: {input_path}")
            return False
        
        return True

    def _run_enhancement_pipeline(self, input_path: Path, output_path: Path, 
                                 pipeline: List[str], **kwargs) -> bool:
        """
        Run the enhancement pipeline.
        
        Args:
            input_path: Input file path
            output_path: Output file path
            pipeline: List of enhancement steps
            **kwargs: Additional parameters
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            current_input = input_path
            
            for step in pipeline:
                if step == "ocr":
                    temp_output = output_path.parent / f"temp_ocr_{output_path.name}"
                    if not self.ocr_enhancer.enhance_file(current_input, temp_output):
                        return False
                    current_input = temp_output
                
                elif step == "compression":
                    temp_output = output_path.parent / f"temp_comp_{output_path.name}"
                    if not self.compression_enhancer.enhance_file(current_input, temp_output):
                        return False
                    current_input = temp_output
                
                elif step == "pdf_enhancement":
                    if not self.minimal_pdf_enhancer.enhance_file(current_input, output_path, **kwargs):
                        return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Pipeline execution failed: {e}")
            return False
    
