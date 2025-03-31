#!/usr/bin/env python3
"""
Accessibility processor for SmolDocling.
Enhances PDFs with OCR text for screen readers and WCAG/PDF-UA compliance.
"""

import os
import argparse
import logging
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any

import cv2
import numpy as np
import fitz  # PyMuPDF
from PIL import Image
from tqdm import tqdm
from transformers import TrOCRProcessor, VisionEncoderDecoderModel

# Import local modules for document enhancement
from document_enhancer import DocumentEnhancer
from document_converter import DocumentConverter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class OCRProcessor:
    """OCR processor using Hugging Face TrOCR models."""
    
    def __init__(self, model_name: str = "microsoft/trocr-base-printed"):
        """
        Initialize OCR processor.
        
        Args:
            model_name: Name of the HuggingFace TrOCR model to use.
        """
        logger.info(f"Loading OCR model: {model_name}")
        self.processor = TrOCRProcessor.from_pretrained(model_name)
        self.model = VisionEncoderDecoderModel.from_pretrained(model_name)
        logger.info("OCR model loaded successfully")
    
    def extract_text(self, image: np.ndarray) -> str:
        """
        Extract text from an image using OCR.
        
        Args:
            image: Image as numpy array.
            
        Returns:
            Extracted text.
        """
        # Convert to RGB if grayscale
        if len(image.shape) == 2:
            image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        elif len(image.shape) == 3 and image.shape[2] == 3:
            # BGR to RGB if color
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        pil_image = Image.fromarray(image)
        
        # Process image
        pixel_values = self.processor(pil_image, return_tensors="pt").pixel_values
        
        # Generate text
        generated_ids = self.model.generate(pixel_values)
        generated_text = self.processor.batch_decode(
            generated_ids, skip_special_tokens=True
        )[0]
        
        return generated_text
    
    def process_blocks(self, image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Process image to extract text blocks with positions.
        
        Args:
            image: Image as numpy array.
            
        Returns:
            List of dictionaries with text and position data.
        """
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Threshold image
        _, thresh = cv2.threshold(
            gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
        )
        
        # Find contours of text regions
        contours, _ = cv2.findContours(
            thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Sort contours from top to bottom
        contours = sorted(
            contours,
            key=lambda c: cv2.boundingRect(c)[1]
        )
        
        # Process each contour
        text_blocks = []
        for i, contour in enumerate(contours):
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter out very small contours
            if w < 10 or h < 10:
                continue
            
            # Extract ROI (Region of Interest)
            roi = image[y:y+h, x:x+w]
            
            # Perform OCR on ROI
            try:
                text = self.extract_text(roi)
                if text.strip():
                    text_blocks.append({
                        "text": text,
                        "bbox": (x, y, x+w, y+h),
                        "page_idx": None  # Will be set when added to PDF
                    })
            except Exception as e:
                logger.warning(f"Error during OCR for block {i}: {e}")
        
        return text_blocks


class AccessibilityProcessor:
    """
    Processor for creating accessible PDFs by adding OCR text to content stream
    and ensuring WCAG and PDF-UA compatibility.
    """
    
    def __init__(self, ocr_model: str = "microsoft/trocr-base-printed",
                document_type: str = "old_scan"):
        """
        Initialize accessibility processor.
        
        Args:
            ocr_model: Name of the OCR model to use.
            document_type: Type of document for preprocessing ('general', 'old_scan', 'faded').
        """
        self.ocr_processor = OCRProcessor(model_name=ocr_model)
        self.document_type = document_type
        self.enhancer = DocumentEnhancer()
        self.converter = DocumentConverter()
    
    def process_pdf(self, input_pdf: str, output_pdf: str, 
                   enhance_pages: bool = True, add_metadata: bool = True) -> bool:
        """
        Process PDF to make it accessible.
        
        Args:
            input_pdf: Path to input PDF.
            output_pdf: Path to output accessible PDF.
            enhance_pages: Whether to enhance page images before OCR.
            add_metadata: Whether to add accessibility metadata to PDF.
            
        Returns:
            True if processing was successful, False otherwise.
        """
        try:
            # Create temporary directory
            temp_dir = os.path.join(os.path.dirname(output_pdf), "_temp")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Step 1: Extract pages from PDF
            pages_dir = os.path.join(temp_dir, "pages")
            logger.info(f"Extracting pages from {input_pdf}")
            page_images = self.converter.extract_pdf_pages_as_images(
                input_pdf, pages_dir, dpi=300
            )
            
            if not page_images:
                logger.error(f"Failed to extract pages from {input_pdf}")
                return False
            
            logger.info(f"Extracted {len(page_images)} pages")
            
            # Step 2: Enhance pages if requested
            if enhance_pages:
                enhanced_dir = os.path.join(temp_dir, "enhanced")
                logger.info(f"Enhancing pages with document type: {self.document_type}")
                
                # Define parameters to preserve original dimensions
                resize_shape = None  # Pass None to skip resizing and keep original dimensions
                # Define a processor that maintains the original image
                def maintain_original(img):
                    return img  # Return the image without modifications
                
                enhanced_images = self.enhancer.batch_process(
                    page_images, enhanced_dir, self.document_type, resize_shape, maintain_original
                )
                
                if enhanced_images:
                    page_images = enhanced_images
            
            # Step 3: Open input PDF with PyMuPDF
            pdf_doc = fitz.open(input_pdf)
            
            # Step 4: Process each page
            for i, img_path in enumerate(tqdm(page_images, desc="Processing pages with OCR")):
                # Load image
                img = cv2.imread(img_path)
                
                # Extract text blocks with positions
                text_blocks = self.ocr_processor.process_blocks(img)
                
                # Get PDF page
                page = pdf_doc[i]
                
                # Add text blocks to PDF page
                self._add_text_to_page(page, text_blocks, img.shape[1], img.shape[0])
            
            # Step 5: Add accessibility metadata if requested
            if add_metadata:
                self._add_accessibility_metadata(pdf_doc)
            
            # Step 6: Save output PDF
            pdf_doc.save(output_pdf)
            pdf_doc.close()
            
            logger.info(f"Saved accessible PDF to {output_pdf}")
            return True
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return False
    
    def _add_text_to_page(self, page: fitz.Page, text_blocks: List[Dict[str, Any]], 
                         img_width: int, img_height: int) -> None:
        """
        Add text blocks to PDF page as invisible text for accessibility.
        
        Args:
            page: PyMuPDF page object.
            text_blocks: List of text blocks with positions.
            img_width: Width of the original image.
            img_height: Height of the original image.
        """
        # Calculate scaling factors between image and PDF page
        page_rect = page.rect
        scale_x = page_rect.width / img_width
        scale_y = page_rect.height / img_height
        
        # Add each text block to the page
        for block in text_blocks:
            x0, y0, x1, y1 = block["bbox"]
            
            # Scale coordinates to PDF page
            pdf_x0 = x0 * scale_x
            pdf_y0 = y0 * scale_y
            pdf_x1 = x1 * scale_x
            pdf_y1 = y1 * scale_y
            
            # Create rectangle for text
            rect = fitz.Rect(pdf_x0, pdf_y0, pdf_x1, pdf_y1)
            
            # Add invisible text (use fill_opacity=0 to make text invisible but selectable)
            page.insert_textbox(
                rect,
                block["text"],
                fontname="helv",
                fontsize=11,
                align=0,  # left aligned
                fill_opacity=0  # invisible but selectable
            )
    
    def _add_accessibility_metadata(self, pdf_doc: fitz.Document) -> None:
        """
        Add accessibility metadata to PDF for WCAG and PDF-UA compliance.
        
        Args:
            pdf_doc: PyMuPDF document object.
        """
        # Set PDF version to 1.7 (required for PDF/UA compliance)
        pdf_doc.set_pdf_version("1.7")
        
        # Set document metadata
        pdf_doc.set_metadata({
            "format": "PDF/UA",
            "title": Path(pdf_doc.name).stem,
            "creator": "SmolDocling Accessibility Processor",
            "producer": "SmolDocling with PyMuPDF",
            "trapped": "False"
        })
        
        # Add XMP metadata for PDF/UA compliance
        xmp_metadata = f"""
        <?xpacket begin='ï»¿' id='W5M0MpCehiHzreSzNTczkc9d'?>
        <x:xmpmeta xmlns:x="adobe:ns:meta/">
          <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
            <rdf:Description rdf:about="" xmlns:pdfuaid="http://www.aiim.org/pdfua/ns/id/">
              <pdfuaid:part>1</pdfuaid:part>
            </rdf:Description>
            <rdf:Description rdf:about="" xmlns:pdf="http://ns.adobe.com/pdf/1.3/">
              <pdf:Producer>SmolDocling with PyMuPDF</pdf:Producer>
            </rdf:Description>
            <rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/">
              <dc:title>
                <rdf:Alt>
                  <rdf:li xml:lang="x-default">{Path(pdf_doc.name).stem}</rdf:li>
                </rdf:Alt>
              </dc:title>
              <dc:creator>
                <rdf:Seq>
                  <rdf:li>SmolDocling Accessibility Processor</rdf:li>
                </rdf:Seq>
              </dc:creator>
            </rdf:Description>
          </rdf:RDF>
        </x:xmpmeta>
        <?xpacket end='w'?>
        """
        
        pdf_doc.set_xml_metadata(xmp_metadata)
        
        # Add document structure (required for PDF/UA)
        # This is a simplified version, a full implementation would add more structure
        pdf_doc.init_doc_js(
            f"""
            var docTree = this.createDSC();
            var rootNode = docTree.createNode("Document");
            docTree.addRoot(rootNode);
            
            // Add each page to the document structure
            for (var i = 0; i < this.numPages; i++) {{
                var pageNode = docTree.createNode("Page");
                rootNode.appendChild(pageNode);
                pageNode.setAttribute("PageID", i + 1);
            }}
            
            // Apply document structure
            this.setDSC(docTree);
            """
        )


def main():
    """Main function for accessibility processing."""
    parser = argparse.ArgumentParser(
        description="Process PDFs for accessibility with OCR and WCAG/PDF-UA compliance"
    )
    parser.add_argument(
        "--input", "-i", required=True, help="Input PDF file"
    )
    parser.add_argument(
        "--output", "-o", default=None, help="Output PDF file"
    )
    parser.add_argument(
        "--model",
        default="microsoft/trocr-base-printed",
        help="HuggingFace TrOCR model to use for OCR"
    )
    parser.add_argument(
        "--document-type",
        choices=["general", "old_scan", "faded"],
        default="old_scan",
        help="Document type for preprocessing"
    )
    parser.add_argument(
        "--no-enhance",
        action="store_true",
        help="Skip page enhancement before OCR"
    )
    parser.add_argument(
        "--no-metadata",
        action="store_true",
        help="Skip adding accessibility metadata"
    )
    
    args = parser.parse_args()
    
    # Determine output path if not provided
    if args.output is None:
        output_dir = os.path.dirname(args.input)
        if not output_dir:
            output_dir = "."
        output_path = os.path.join(
            output_dir, f"{Path(args.input).stem}_accessible.pdf"
        )
    else:
        output_path = args.output
    
    # Initialize processor
    processor = AccessibilityProcessor(
        ocr_model=args.model,
        document_type=args.document_type
    )
    
    # Process PDF
    processor.process_pdf(
        args.input,
        output_path,
        enhance_pages=not args.no_enhance,
        add_metadata=not args.no_metadata
    )


if __name__ == "__main__":
    main()