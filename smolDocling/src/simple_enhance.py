#!/usr/bin/env python3
"""
Simple enhancement script for old scanned documents.
Uses document_enhancer.py to enhance the document without requiring SmolDocling.
Includes OCR for making the document searchable with invisible text.
"""

import os
import argparse
import logging
import tempfile
import sys
from pathlib import Path
import fitz  # PyMuPDF
import numpy as np
import cv2
import pytesseract
from PIL import Image

# Import modules from this project
from document_enhancer import DocumentEnhancer
from document_converter import DocumentConverter
from jbig2_ocr_processor import JBIG2OCRProcessor

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def preprocess_image_for_ocr(image_np):
    """Enhanced preprocessing for historical documents."""
    try:
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np.copy()
        
        # Background normalization - compensates for yellowed paper
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        normalized = clahe.apply(gray)
        
        # Bilateral filtering - preserves edges while reducing noise
        bilateral = cv2.bilateralFilter(normalized, 9, 10, 10)
        
        # Enhance contrast for faded text
        alpha = 1.5  # Contrast control
        beta = 10    # Brightness control
        enhanced = cv2.convertScaleAbs(bilateral, alpha=alpha, beta=beta)
        
        # Apply Otsu's thresholding for adaptive binarization
        _, binary = cv2.threshold(enhanced, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Morphological operations to clean up noise
        kernel = np.ones((1, 1), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # Advanced denoising
        denoised = cv2.fastNlMeansDenoising(cleaned, h=10)
        
        return denoised
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        return gray  # Return original grayscale if preprocessing fails

def add_searchable_text(page, image_path, dpi=600):
    """
    Add invisible searchable text layer to a PDF page using OCR.
    
    Args:
        page: PyMuPDF page object to add text to
        image_path: Path to the image file of the page
        dpi: DPI of the image for coordinate conversion
    
    Returns:
        Number of text elements added
    """
    try:
        # Open the image
        image = Image.open(image_path)
        image_np = np.array(image)
        
        # Preprocess the image for better OCR
        processed_image = preprocess_image_for_ocr(image_np)
        
        # Run OCR with appropriate configuration
        custom_config = '--oem 1 --psm 6 -l eng ' + \
                     '-c tessedit_create_hocr=1 -c tessedit_do_invert=0 ' + \
                     '-c load_system_dawg=1 -c load_freq_dawg=1 ' + \
                     '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,;:(){}/\\-_=+*&^%$#@!<>?[] ' + \
                     '-c preserve_interword_spaces=1 -c textord_space_size_is_variable=1 ' + \
                     '-c textord_min_linesize=1.5 ' + \
                     '-c textord_tabfind_find_tables=0 ' + \
                     '-c tessedit_create_txt=1 ' + \
                     '-c tessedit_pageseg_mode=6 ' + \
                     '-c textord_heavy_nr=0 ' + \
                     '-c textord_tablefind_recognize_tables=0'
        
        # Get OCR data with positions
        ocr_data = pytesseract.image_to_data(
            processed_image, 
            config=custom_config, 
            output_type=pytesseract.Output.DICT
        )
        
        # Get page dimensions
        page_width = float(page.rect.width)
        page_height = float(page.rect.height)
        
        # Calculate scaling factor
        scale_x = page_width / image.width
        scale_y = page_height / image.height
        
        # Filter out entries with empty text or low confidence
        min_confidence = 10  # Lower threshold for historical docs to capture more text
        
        # Keep track of added text for logging
        added_text_count = 0
        
        # Group text entries by block and line to preserve layout
        blocks = {}
        
        # Group text by blocks and lines for proper top-to-bottom ordering
        for idx in range(len(ocr_data['text'])):
            text = ocr_data['text'][idx].strip()
            conf = float(ocr_data['conf'][idx])
            
            if text and conf > min_confidence:
                block_num = ocr_data['block_num'][idx]
                line_num = ocr_data['line_num'][idx]
                par_num = ocr_data['par_num'][idx] if 'par_num' in ocr_data else block_num
                
                # Create a composite key for better organization
                block_key = f"{block_num}_{par_num}"
                
                if block_key not in blocks:
                    blocks[block_key] = {}
                if line_num not in blocks[block_key]:
                    blocks[block_key][line_num] = []
                
                blocks[block_key][line_num].append(idx)
        
        # Sort blocks by their vertical position (top coordinate)
        # This ensures top-to-bottom processing of text blocks
        sorted_blocks = sorted(blocks.keys(), key=lambda b: min(
            ocr_data['top'][idx] for line in blocks[b].values() for idx in line
        ))
        
        # Process blocks in top-to-bottom order
        for block_key in sorted_blocks:
            lines = blocks[block_key]
            
            # Sort lines by their vertical position (top coordinate)
            sorted_lines = sorted(lines.keys(), key=lambda l: min(
                ocr_data['top'][idx] for idx in lines[l]
            ))
            
            # Process each line in top-to-bottom order
            for line_num in sorted_lines:
                indices = lines[line_num]
                
                # Sort words left to right within each line
                indices = sorted(indices, key=lambda idx: ocr_data['left'][idx])
                
                for idx in indices:
                    text = ocr_data['text'][idx].strip()
                    if not text:
                        continue
                    
                    # Get text positions
                    left = ocr_data['left'][idx]
                    top = ocr_data['top'][idx]
                    width = ocr_data['width'][idx]
                    height = ocr_data['height'][idx]
                    
                    # Scale to PDF coordinates
                    pdf_left = left * scale_x
                    pdf_top = top * scale_y
                    pdf_width = width * scale_x
                    pdf_height = height * scale_y
                    
                    # Calculate font size based on height
                    # For historical documents, we use a slightly larger font size multiplier
                    font_size_multiplier = 0.75
                    font_size = pdf_height * font_size_multiplier
                    font_size = max(6, min(14, font_size))  # Keep size reasonable
                    
                    # CORRECTED COORDINATE SYSTEM TRANSFORMATION 
                    # PyMuPDF uses bottom-left origin coordinates, OCR data uses top-left
                    # For Tesseract, the y-coordinate must be properly inverted
                    
                    # Calculate text baseline position (80% from top of bounding box in PDF coordinates)
                    baseline_position = pdf_top + (pdf_height * 0.8)
                    
                    # Flipping content insertion by 180 degrees
                    # Now using 180 degree rotation by changing coordinate system
                    y_position = baseline_position
                    
                    point = fitz.Point(pdf_left, y_position)
                    
                    try:
                        # Add invisible but searchable text
                        page.insert_text(
                            point,
                            text,
                            fontsize=font_size,
                            render_mode=3,  # Mode 3 = invisible but searchable
                            color=(0, 0, 0),  # Black color (won't be visible due to render_mode)
                            overlay=False     # Don't overlay text on existing content
                        )
                        added_text_count += 1
                    except Exception as text_error:
                        logger.error(f"Error adding text '{text}' at {point}: {text_error}")
        
        return added_text_count
        
    except Exception as e:
        logger.error(f"Error adding searchable text to page: {e}")
        return 0

def main():
    """Main entry point for simple document enhancement script."""
    parser = argparse.ArgumentParser(description="Enhance old scanned documents")
    parser.add_argument(
        "--input", "-i", 
        required=True,
        help="Input PDF file"
    )
    parser.add_argument(
        "--output", "-o", 
        default="./data/output",
        help="Output directory for enhanced pages"
    )
    parser.add_argument(
        "--document-type",
        choices=["general", "old_scan", "faded"],
        default="old_scan",
        help="Document type for preprocessing"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for multi-page documents"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=400,
        help="DPI for image extraction (higher values improve OCR quality)"
    )
    parser.add_argument(
        "--no-ocr",
        action="store_true",
        help="Skip adding searchable text layer"
    )
    parser.add_argument(
        "--use-jbig2",
        action="store_true",
        help="Use JBIG2-optimized OCR processor (recommended for scanned documents)"
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=40,
        help="Minimum confidence threshold for OCR text (default: 40)"
    )
    
    args = parser.parse_args()
    
    # Ensure input file exists
    input_path = Path(args.input)
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if using direct JBIG2 OCR mode
    if args.use_jbig2 and not args.no_ocr:
        logger.info(f"Using JBIG2-optimized OCR processor directly on {input_path}")
        output_file = output_dir / f"{input_path.stem}_enhanced.pdf"
        
        # Initialize and run JBIG2 OCR processor
        jbig2_processor = JBIG2OCRProcessor(min_confidence=args.min_confidence, dpi=args.dpi)
        success = jbig2_processor.make_searchable_pdf(str(input_path), str(output_file))
        
        if success:
            logger.info(f"Successfully created searchable PDF: {output_file}")
        else:
            logger.error(f"Failed to create searchable PDF: {output_file}")
        
        return
        
    # Standard enhancement workflow with optional JBIG2 OCR
    # Create temporary directory for pages
    temp_dir = output_dir / "_temp"
    temp_dir.mkdir(exist_ok=True)
    
    # Initialize enhancer and converter
    enhancer = DocumentEnhancer()
    converter = DocumentConverter()
    
    # Extract pages from PDF
    page_images_dir = temp_dir / "pages"
    page_images_dir.mkdir(exist_ok=True)
    
    logger.info(f"Extracting pages from {input_path} at {args.dpi} DPI...")
    page_images = converter.extract_pdf_pages_as_images(
        str(input_path), str(page_images_dir), dpi=args.dpi
    )
    
    if not page_images:
        logger.error(f"Failed to extract pages from {input_path}")
        return
    
    logger.info(f"Extracted {len(page_images)} pages.")
    
    # Enhance page images
    enhanced_dir = temp_dir / "enhanced"
    enhanced_dir.mkdir(exist_ok=True)
    
    logger.info(f"Enhancing pages with document type: {args.document_type}")
    # Define parameters to preserve original dimensions
    resize_shape = None  # Pass None to skip resizing and keep original dimensions
    # Define a processor that maintains the original image
    def maintain_original(img):
        return img  # Return the image without modifications
    image_processor = maintain_original
    
    enhanced_images = enhancer.batch_process(
        page_images, str(enhanced_dir), args.document_type, resize_shape, image_processor
    )
    
    if not enhanced_images:
        logger.error("Failed to enhance any pages")
        return
    
    # Create PDF from enhanced images
    output_file = output_dir / f"{input_path.stem}_enhanced.pdf"
    
    # Sort pages numerically to ensure correct order
    def extract_page_number(path):
        # Extract page number from filenames like "enhanced_*_page_XX.png"
        try:
            filename = os.path.basename(path)
            # Extract the page number before the .png extension
            page_str = filename.split('_page_')[-1].replace('.png', '')
            return int(page_str)
        except Exception:
            return 0  # Default to 0 if extraction fails
    
    enhanced_images.sort(key=extract_page_number)
    
    logger.info(f"Creating enhanced PDF: {output_file}")
    pdf = fitz.open()
    
    # Track OCR stats
    total_ocr_elements = 0
    ocr_pages = 0
    
    # Initialize JBIG2 OCR processor if requested
    if args.use_jbig2 and not args.no_ocr:
        jbig2_processor = JBIG2OCRProcessor(min_confidence=args.min_confidence, dpi=args.dpi)
    
    for img_path in enhanced_images:
        page_num = extract_page_number(img_path)
        logger.info(f"Processing page {page_num} from {os.path.basename(img_path)}")
        
        # Create a new PDF page
        img = fitz.open(img_path)
        rect = img[0].rect
        pdfpage = pdf.new_page(width=rect.width, height=rect.height)
        
        # Add the image
        pdfpage.insert_image(rect, filename=img_path)
        
        # Add OCR text if not disabled
        if not args.no_ocr:
            logger.info(f"Running OCR for page {page_num}")
            try:
                # Choose OCR processor based on args
                if args.use_jbig2:
                    logger.info("Using JBIG2-optimized OCR processor")
                    elements_added = jbig2_processor.add_searchable_text(pdfpage, img_path)
                else:
                    # Use standard OCR
                    elements_added = add_searchable_text(pdfpage, img_path, dpi=args.dpi)
                
                if elements_added > 0:
                    logger.info(f"Added {elements_added} searchable text elements to page {page_num}")
                    total_ocr_elements += elements_added
                    ocr_pages += 1
                else:
                    logger.warning(f"No text elements could be added to page {page_num}")
            except Exception as e:
                logger.error(f"Error during OCR for page {page_num}: {e}")
        
        img.close()
    
    # Set PDF metadata with OCR method information
    ocr_method = "JBIG2-optimized Tesseract OCR" if args.use_jbig2 else "Standard Tesseract OCR"
    pdf.set_metadata({
        "title": f"{input_path.stem} (Enhanced)",
        "subject": "Enhanced document with improved readability and searchable text",
        "creator": "SmolDocling Document Enhancer",
        "producer": f"PyMuPDF with {ocr_method}"
    })
    
    logger.info(f"Saving enhanced PDF: {output_file}")
    # Use compression options for smaller file size
    pdf.save(str(output_file), garbage=4, deflate=True, clean=True)
    pdf.close()
    
    logger.info(f"Enhanced PDF saved to {output_file} with {len(enhanced_images)} pages")
    if not args.no_ocr:
        logger.info(f"Added searchable text to {ocr_pages} pages ({total_ocr_elements} text elements total)")
    
    # Success message
    logger.info(f"Document enhancement complete: {output_file}")

if __name__ == "__main__":
    main()