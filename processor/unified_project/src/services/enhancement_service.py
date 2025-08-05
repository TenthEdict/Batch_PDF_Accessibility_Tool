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

# Optional ML enhancer import
try:
    from ..enhancers.ml_enhancer import MLEnhancer
    ML_ENHANCER_AVAILABLE = True
except ImportError:
    MLEnhancer = None
    ML_ENHANCER_AVAILABLE = False

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
        
        # Initialize optional ML enhancer (will be activated per processing mode)
        self.ml_enhancer = None

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

                # Step 1: OCR with Aggressive Web Compression
                self.logger.info("Step 1: Applying OCR with aggressive web compression for academic papers...")
                ocr_success = self.ocr_enhancer.enhance_file(
                    input_path, ocr_output_path
                )
                if not ocr_success:
                    self.logger.error("OCR enhancement failed.")
                    return False
                self.logger.info("OCR enhancement with web compression completed successfully.")

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
        }
    
    def get_enhancement_capabilities(self) -> Dict[str, List[str]]:
        """
        Get the capabilities of all available enhancers.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping enhancer names to their capabilities
        """
        return {
            "ocr_enhancer": self.ocr_enhancer.get_capabilities(),
            "compression_enhancer": self.compression_enhancer.get_capabilities(),
            "minimal_pdf_enhancer": self.minimal_pdf_enhancer.get_capabilities()
        }
    
