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
from ..enhancers.pdf_enhancer import PDFEnhancer

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
        self.pdf_enhancer = PDFEnhancer()
        

    def enhance_document(
        self,
        input_path: Union[str, Path],
        output_path: Union[str, Path],
        mode: str = "academic",
        **kwargs,
    ) -> bool:
        """
        Enhance a document with OCR and accessibility features.
        
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

                # Step 1: OCR and Font Embedding
                self.logger.info("Step 1: Applying OCR and Font Embedding...")
                ocr_success = self.ocr_enhancer.enhance_file(
                    input_path, ocr_output_path
                )
                if not ocr_success:
                    self.logger.error("OCR enhancement failed.")
                    return False
                self.logger.info("OCR enhancement completed successfully.")

                # Step 2: Local PDF Metadata and Accessibility Enhancements
                current_input_path = ocr_output_path
                self.logger.info("Step 2: Applying local PDF metadata and accessibility enhancements...")
                
                pdf_enhance_success = self.pdf_enhancer.enhance_file(
                    current_input_path, output_path, **kwargs
                )
                if not pdf_enhance_success:
                    self.logger.error("PDF metadata enhancement failed.")
                    return False
                self.logger.info("PDF metadata enhancement completed successfully.")

            enhancement_summary = [
                "OCR and font embedding",
                "Local PDF metadata and accessibility features"
            ]
            
            self.logger.info(f"Successfully enhanced document with: {', '.join(enhancement_summary)}")
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
            "ocr_enhancer": True,  # Always available if class loads
            "pdf_enhancer": True,  # Always available if class loads
        }
    
    def get_enhancement_capabilities(self) -> Dict[str, List[str]]:
        """
        Get the capabilities of all available enhancers.
        
        Returns:
            Dict[str, List[str]]: Dictionary mapping enhancer names to their capabilities
        """
        return {
            "ocr_enhancer": self.ocr_enhancer.get_capabilities(),
            "pdf_enhancer": self.pdf_enhancer.get_capabilities()
        }
    
