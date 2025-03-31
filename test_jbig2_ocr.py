#!/usr/bin/env python3
import os
import sys
import cv2
import numpy as np
import pytesseract
from pdf2image import convert_from_path
import fitz  # PyMuPDF
import logging
import tempfile
import shutil
import subprocess
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def preprocess_image(image):
    """
    Apply enhanced preprocessing optimized for JBIG2 compressed documents
    """
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 1. Apply bilateral filtering with increased kernel size
    bilateral = cv2.bilateralFilter(gray, 11, 75, 75)
    
    # 2. Apply adaptive thresholding with parameters for JBIG2 compression
    binary = cv2.adaptiveThreshold(
        bilateral, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 13, 1
    )
    
    # 3. Apply stronger denoising
    denoised = cv2.fastNlMeansDenoising(binary, h=15)
    
    # 4. Apply morphological operations
    kernel = np.ones((2, 2), np.uint8)
    denoised = cv2.morphologyEx(denoised, cv2.MORPH_OPEN, kernel)
    
    return denoised

def extract_text_from_page(image):
    """
    Extract text from an image using enhanced OCR configuration
    """
    # Preprocess the image
    processed = preprocess_image(image)
    
    # Configure Tesseract with optimized parameters
    config = f"--oem 1 --psm 3 -c tessedit_do_invert=0 -c textord_min_linesize=1.25 -c preserve_interword_spaces=1"
    
    # Extract text
    text = pytesseract.image_to_string(
        processed, 
        lang='eng',
        config=config
    )
    
    return text

def make_searchable_pdf(input_path, output_path, dpi=300):
    """
    Process PDF file to create a searchable version with JBIG2-optimized OCR
    
    Args:
        input_path: Path to the input PDF file
        output_path: Path to save the searchable PDF
        dpi: DPI for image conversion (higher values improve quality but increase processing time)
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing: {input_path}")
    logger.info(f"Output will be saved to: {output_path}")
    logger.info(f"DPI: {dpi}")
    
    try:
        # First, copy the original PDF to the output path
        shutil.copy(input_path, output_path)
        logger.info(f"Created initial copy at {output_path}")
        
        # Create a temporary directory for OCR processing
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Get PDF page count
            with fitz.open(input_path) as doc:
                total_pages = len(doc)
            
            logger.info(f"PDF has {total_pages} pages")
            
            # Convert PDF to images for OCR processing
            logger.info(f"Converting PDF to images at {dpi} DPI...")
            images = convert_from_path(input_path, dpi=dpi)
            logger.info(f"Converted {len(images)} pages to images")
            
            # Process each page
            with fitz.open(input_path) as input_doc:
                with fitz.open() as output_doc:
                    # Copy pages from input
                    for i in range(len(input_doc)):
                        output_doc.insert_pdf(input_doc, from_page=i, to_page=i)
                    
                    # Process each page
                    for page_num, image in enumerate(images):
                        if page_num >= len(output_doc):
                            logger.warning(f"Skipping page {page_num+1} as it doesn't exist in the output document")
                            continue
                            
                        logger.info(f"Processing page {page_num+1}/{total_pages}")
                        
                        # Save image temporarily
                        img_path = f"{tmp_dir}/page_{page_num}.png"
                        image.save(img_path, "PNG")
                        
                        # Convert to numpy array for preprocessing
                        img_np = np.array(image)
                        
                        # Apply JBIG2-optimized preprocessing
                        processed_image = preprocess_image(img_np)
                        
                        # Run OCR with optimized configuration
                        logger.info(f"Running OCR on page {page_num+1}")
                        
                        # Configure Tesseract with optimized parameters for JBIG2
                        config = f"--oem 1 --psm 3 -c tessedit_do_invert=0 -c textord_min_linesize=1.25 -c preserve_interword_spaces=1"
                        
                        # Get OCR data with positions
                        ocr_data = pytesseract.image_to_data(
                            processed_image, 
                            lang='eng',
                            config=config, 
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # Get PDF page for modification
                        page = output_doc[page_num]
                        
                        # Get page dimensions
                        page_width = float(page.rect.width)
                        page_height = float(page.rect.height)
                        
                        # Calculate scaling factor
                        scale_x = page_width / image.width
                        scale_y = page_height / image.height
                        
                        # Filter out entries with empty text or low confidence
                        min_confidence = 40  # Confidence threshold for better quality
                        
                        # Keep track of added text for logging
                        added_text_count = 0
                        
                        # Group text entries by block and line to preserve layout
                        blocks = {}
                        
                        # Group text by blocks and lines for proper top-to-bottom ordering
                        for idx in range(len(ocr_data['text'])):
                            text = ocr_data['text'][idx].strip()
                            conf = float(ocr_data['conf'][idx])
                            
                            # Only include text with sufficient confidence
                            if text and conf > min_confidence:
                                # Get block and line numbers from OCR data for grouping
                                block_num = ocr_data['block_num'][idx]
                                line_num = ocr_data['line_num'][idx]
                                
                                # Organize by blocks and lines for proper text flow
                                if block_num not in blocks:
                                    blocks[block_num] = {}
                                if line_num not in blocks[block_num]:
                                    blocks[block_num][line_num] = []
                                
                                # Store index for later processing
                                blocks[block_num][line_num].append(idx)
                        
                        # Sort blocks by their vertical position (top coordinate)
                        # This ensures top-to-bottom processing of text blocks
                        sorted_blocks = sorted(blocks.keys(), key=lambda b: min(
                            ocr_data['top'][idx] for line in blocks[b].values() for idx in line
                        ))
                        
                        # Process blocks in top-to-bottom order
                        for block_num in sorted_blocks:
                            lines = blocks[block_num]
                            
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
                                    
                                    # Calculate font size based on the height of the text
                                    # Adaptive font sizing based on DPI and text height
                                    dpi_factor = dpi / 300.0  # Adjust for different DPI settings
                                    font_size = pdf_height * 0.85 * dpi_factor
                                    font_size = max(7, min(16, font_size))  # Keep size reasonable
                                    
                                    # Precise coordinate system transformation
                                    # PDF uses bottom-left origin, OCR uses top-left
                                    
                                    # CORRECT APPROACH:
                                    # 1. Calculate where the text baseline is in OCR coordinates
                                    #    (typically ~80% down from the top of the bounding box)
                                    # 2. Convert that position to PDF coordinates (flip y-axis)
                                    
                                    # Calculate baseline position in OCR coordinates (80% from top)
                                    baseline_position = pdf_top + (pdf_height * 0.8)
                                    
                                    # Transform from OCR coords (top-left) to PDF coords (bottom-left)
                                    y_position = page_height - baseline_position
                                    
                                    point = fitz.Point(pdf_left, y_position)
                                    
                                    try:
                                        # Add invisible but searchable text
                                        page.insert_text(
                                            point,
                                            text,
                                            fontsize=font_size,
                                            render_mode=3,  # Mode 3 = invisible but searchable
                                            color=(0, 0, 0),  # Black color (won't be visible due to render_mode)
                                            morph=None  # Explicitly disable morphing to prevent error
                                        )
                                        added_text_count += 1
                                    except Exception as text_error:
                                        logger.error(f"Error adding text '{text}' at {point}: {text_error}")
                        
                        logger.info(f"Added {added_text_count} invisible text elements to page {page_num+1}")
                        
                        # Remove temporary image
                        try:
                            os.remove(img_path)
                        except Exception as e:
                            logger.warning(f"Error removing temporary file: {e}")
                    
                    # Save the document
                    output_doc.save(output_path)
            
            logger.info(f"Successfully created searchable PDF: {output_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error making PDF searchable: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    import argparse
    
    # Set up command line arguments
    parser = argparse.ArgumentParser(description='Create searchable PDF with JBIG2-optimized OCR')
    parser.add_argument('--input', '-i', required=True, help='Path to input PDF file')
    parser.add_argument('--output', '-o', required=True, help='Path to output searchable PDF file')
    parser.add_argument('--dpi', type=int, default=300, help='DPI for image conversion (default: 300)')
    
    args = parser.parse_args()
    
    pdf_path = args.input
    output_path = args.output
    dpi = args.dpi
    
    if os.path.exists(pdf_path):
        logger.info(f"Processing PDF: {pdf_path}")
        success = make_searchable_pdf(pdf_path, output_path, dpi)
        sys.exit(0 if success else 1)
    else:
        logger.error(f"PDF file not found: {pdf_path}")
        sys.exit(1)