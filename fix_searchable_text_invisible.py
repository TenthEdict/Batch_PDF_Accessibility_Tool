#!/usr/bin/env python3
"""
Final version of fix_searchable_text script with invisible but searchable text
Usage: python fix_searchable_text_invisible.py input.pdf output.pdf
"""

import os
import sys
import logging
import tempfile
import shutil
from pathlib import Path
import json
import pytesseract
from pdf2image import convert_from_path
import numpy as np
import cv2
import fitz  # PyMuPDF
import gc
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

# Path to historical config and resources
HISTORICAL_CONFIG_PATH = "/Users/broderickschipp/work/ePubs_AccProj/brodie_code/tessdata/configs/historical.config"
HISTORICAL_WORDS_DIR = "/Users/broderickschipp/work/ePubs_AccProj/brodie_code/src/accessibility_checker/ocr/historical_words"
HISTORICAL_PATTERNS = "/Users/broderickschipp/work/ePubs_AccProj/brodie_code/src/accessibility_checker/ocr/historical_patterns.txt"

def preprocess_image_historical(image_np):
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
        logger.error(f"Historical image preprocessing failed: {str(e)}")
        return gray  # Return original grayscale if preprocessing fails

def preprocess_image(image_np, historical_mode=False):
    """Preprocess image for better OCR results."""
    if historical_mode:
        return preprocess_image_historical(image_np)
    
    try:
        if len(image_np.shape) == 3:
            gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
        else:
            gray = image_np.copy()
        
        # Enhanced preprocessing for standard documents
        # Apply CLAHE for better contrast
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Apply adaptive thresholding with improved parameters
        binary = cv2.adaptiveThreshold(
            enhanced, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 15, 8
        )
        
        # Apply denoising with stronger parameters
        denoised = cv2.fastNlMeansDenoising(binary, h=10)
        
        return denoised
    except Exception as e:
        logger.error(f"Image preprocessing failed: {str(e)}")
        return gray  # Return original grayscale if preprocessing fails

def setup_historical_resources(tmp_dir):
    """Set up historical OCR resources in a temporary directory."""
    try:
        # Get system tessdata directory path
        import subprocess
        result = subprocess.run(["which", "tesseract"], capture_output=True, text=True)
        tesseract_bin = result.stdout.strip()
        system_tessdata_dir = None
        
        if os.path.exists("/opt/homebrew/share/tessdata"):
            system_tessdata_dir = "/opt/homebrew/share/tessdata"
        elif os.path.exists("/usr/share/tesseract-ocr/tessdata"):
            system_tessdata_dir = "/usr/share/tesseract-ocr/tessdata"
        elif os.path.exists("/usr/local/share/tessdata"):
            system_tessdata_dir = "/usr/local/share/tessdata"
        
        if not system_tessdata_dir:
            logger.warning("Could not find system tessdata directory, OCR may fail")
        else:
            logger.info(f"Found system tessdata directory: {system_tessdata_dir}")
        
        # Create directories
        tessdata_dir = os.path.join(tmp_dir, "tessdata")
        os.makedirs(tessdata_dir, exist_ok=True)
        configs_dir = os.path.join(tessdata_dir, "configs")
        os.makedirs(configs_dir, exist_ok=True)
        
        # Copy the eng.traineddata from system directory if available
        if system_tessdata_dir and os.path.exists(os.path.join(system_tessdata_dir, "eng.traineddata")):
            logger.info("Copying eng.traineddata from system directory")
            shutil.copy(
                os.path.join(system_tessdata_dir, "eng.traineddata"),
                os.path.join(tessdata_dir, "eng.traineddata")
            )
        
        # Copy historical config
        if os.path.exists(HISTORICAL_CONFIG_PATH):
            shutil.copy(HISTORICAL_CONFIG_PATH, os.path.join(configs_dir, "historical.config"))
        else:
            logger.warning(f"Historical config not found at {HISTORICAL_CONFIG_PATH}")
        
        # Setup historical patterns and word lists
        # First, create combined historical words file
        combined_words_path = os.path.join(tessdata_dir, "historical_words.txt")
        with open(combined_words_path, 'w') as combined_file:
            # Combine all historical word files into one
            for word_file in os.listdir(HISTORICAL_WORDS_DIR):
                if word_file.endswith('.txt'):
                    word_file_path = os.path.join(HISTORICAL_WORDS_DIR, word_file)
                    logger.info(f"Adding words from {word_file_path}")
                    with open(word_file_path, 'r') as f:
                        combined_file.write(f.read() + "\n")
        
        # Setup historical patterns file - ensure proper format
        patterns_path = os.path.join(tessdata_dir, "historical_patterns.txt")
        if os.path.exists(HISTORICAL_PATTERNS):
            # Copy but ensure each line has an equals sign for config var assignment
            with open(HISTORICAL_PATTERNS, 'r') as source:
                with open(patterns_path, 'w') as dest:
                    for line in source:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' not in line:
                            # Add equals sign if missing
                            dest.write(f"{line}={line}\n")
                        else:
                            dest.write(line + "\n")
            logger.info(f"Created formatted patterns file at {patterns_path}")
        
        # Return the TESSDATA_PREFIX path to use
        return tessdata_dir
    except Exception as e:
        logger.error(f"Error setting up historical resources: {e}")
        return None

def make_pdf_searchable(input_path, output_path, historical_mode=True, dpi=600, force_reprocess=False):
    """Make PDF searchable by adding invisible searchable OCR text layer."""
    input_path = Path(input_path)
    output_path = Path(output_path)
    
    if not input_path.exists():
        logger.error(f"Input file not found: {input_path}")
        return False
    
    # Create output directory if needed
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Processing: {input_path}")
    logger.info(f"Output will be saved to: {output_path}")
    logger.info(f"Historical mode: {historical_mode}")
    logger.info(f"DPI: {dpi}")
    logger.info(f"Force reprocessing: {force_reprocess}")
    
    try:
        # First, copy the original PDF to the output path
        import shutil
        shutil.copy(input_path, output_path)
        logger.info(f"Created initial copy at {output_path}")
        
        # Create a temporary directory for OCR processing
        with tempfile.TemporaryDirectory() as tmp_dir:
            # Setup historical resources if needed
            tessdata_prefix = None
            original_tessdata_prefix = os.environ.get("TESSDATA_PREFIX", "")
            
            if historical_mode:
                tessdata_prefix = setup_historical_resources(tmp_dir)
                if tessdata_prefix:
                    os.environ["TESSDATA_PREFIX"] = tessdata_prefix
                    logger.info(f"Set TESSDATA_PREFIX to {tessdata_prefix}")
            
            # Get PDF page count
            with fitz.open(input_path) as pdf:
                total_pages = len(pdf)
            
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
                        image_np = np.array(image)
                        processed_image = preprocess_image(image_np, historical_mode=historical_mode)
                        
                        # Run OCR with appropriate configuration
                        logger.info(f"Running OCR on page {page_num+1}")
                        
                        if historical_mode:
                            # Enhanced historical document OCR configuration
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
                        else:
                            # Standard OCR configuration
                            custom_config = '--oem 1 --psm 3 -l eng'
                        
                        # Get OCR data with positions
                        ocr_data = pytesseract.image_to_data(
                            processed_image, 
                            config=custom_config, 
                            output_type=pytesseract.Output.DICT
                        )
                        
                        # Get PDF page for modification
                        page = output_doc[page_num]
                        
                        # Check if the page already has searchable text
                        existing_text = page.get_text("text").strip()
                        
                        # Skip pages that already have text unless forced to reprocess
                        if existing_text and not force_reprocess:
                            logger.info(f"Page {page_num+1} already has searchable text. Skipping. (Use --force to reprocess)")
                            continue
                        elif existing_text and force_reprocess:
                            logger.info(f"Page {page_num+1} already has searchable text. Force reprocessing.")
                            # We'll clean contents later before adding text
                        else:
                            logger.info(f"Page {page_num+1} has no searchable text. Adding OCR text.")
                        
                        # Get page dimensions
                        page_width = float(page.rect.width)
                        page_height = float(page.rect.height)
                        
                        # Calculate scaling factor
                        scale_x = page_width / image.width
                        scale_y = page_height / image.height
                        
                        # If force reprocessing and page has text, we need to clean it
                        if existing_text and force_reprocess:
                            try:
                                # Remove existing text content using clean_contents
                                # This method optimizes and cleans the content stream
                                # It should preserve images and other visual content while 
                                # removing text content to prevent duplication
                                page.clean_contents()
                                logger.info(f"Cleaned existing text content from page {page_num+1}")
                                
                                # Verify text was removed
                                if page.get_text("text").strip():
                                    logger.warning(f"Text content still exists after cleaning on page {page_num+1}")
                                    logger.info(f"Continuing without aggressive text removal to avoid hanging")
                                    # The redaction approach can cause the script to hang on large documents
                                    # Instead, we'll just continue and overlay our invisible text
                                    # Skipping redaction code that was here previously
                            except Exception as e:
                                logger.warning(f"Failed to clean contents on page {page_num+1}: {e}")
                        
                        # Filter out entries with empty text or low confidence
                        min_confidence = 10 if historical_mode else 30  # Much lower threshold for historical docs to capture more text
                        
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
                                    font_size_multiplier = 0.75 if historical_mode else 0.85
                                    font_size = pdf_height * font_size_multiplier
                                    font_size = max(6, min(14, font_size))  # Keep size reasonable
                                    
                                    # CORRECTED COORDINATE SYSTEM TRANSFORMATION
                                    # PyMuPDF uses bottom-left origin coordinates, OCR data uses top-left
                                    # Calculate baseline position (80% from top of bounding box)
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
                                            overlay=False,  # Don't overlay text on existing content
                                            morph=None      # Explicitly disable morphing to prevent error
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
                        
                        # Force garbage collection
                        gc.collect()
                    
                    # Save the document
                    output_doc.save(output_path)
            
            # Restore original TESSDATA_PREFIX if it was modified
            if original_tessdata_prefix:
                os.environ["TESSDATA_PREFIX"] = original_tessdata_prefix
            elif "TESSDATA_PREFIX" in os.environ:
                del os.environ["TESSDATA_PREFIX"]
                
            logger.info(f"Successfully created searchable PDF: {output_path}")
            return True
            
    except Exception as e:
        logger.error(f"Error making PDF searchable: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description='Final script to make PDFs searchable with invisible text')
    
    parser.add_argument('input_path', help='Input PDF file path')
    parser.add_argument('output_path', help='Output PDF file path')
    parser.add_argument('--historical', action='store_true', default=True, 
                      help='Enable historical document mode (default: True)')
    parser.add_argument('--standard', action='store_true',
                      help='Use standard document mode instead of historical')
    parser.add_argument('--dpi', type=int, default=600,
                      help='DPI for PDF conversion (default: 600, higher values improve text recognition but increase processing time)')
    parser.add_argument('--force', action='store_true',
                      help='Force reprocessing even if pages already have searchable text')
    
    args = parser.parse_args()
    
    # If standard mode is explicitly requested, disable historical mode
    historical_mode = args.historical and not args.standard
    
    logger.info(f"Processing PDF with historical_mode={historical_mode}, dpi={args.dpi}, force={args.force}")
    
    result = make_pdf_searchable(args.input_path, args.output_path, historical_mode=historical_mode, dpi=args.dpi, force_reprocess=args.force)
    return 0 if result else 1

if __name__ == "__main__":
    sys.exit(main())