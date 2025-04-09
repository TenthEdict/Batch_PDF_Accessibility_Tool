#!/usr/bin/env python3
"""
Local academic paper processing script.

This script processes academic papers without requiring Docker,
using the same underlying code as the containerized version.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import glob
import yaml
from tqdm import tqdm

# Add project paths
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT))
sys.path.append(str(PROJECT_ROOT / "unified_project"))

# Import needed modules
try:
    from unified_project.src.academic.processor import AcademicProcessor, AcademicPaperConfig
    from unified_project.src.enhancers.basic_enhancer import BasicEnhancer
    import pikepdf
    import cv2
    import pytesseract
    import numpy as np
    from PIL import Image
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Please make sure you have installed the required dependencies:")
    print("pip install pikepdf pytesseract opencv-python pillow numpy tqdm")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("academic_processor_local")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Local Academic Paper Accessibility Processor"
    )
    
    parser.add_argument(
        "input",
        type=str,
        help="Input PDF file or directory containing PDF files"
    )
    
    parser.add_argument(
        "output",
        type=str,
        help="Output PDF file or directory for processed PDFs"
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Process a batch of documents from input directory"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default="unified_project/config/academic.yaml",
        help="Path to configuration file"
    )
    
    parser.add_argument(
        "--timeout",
        type=int,
        default=1800,
        help="Processing timeout in seconds per file"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    return parser.parse_args()

def load_config(config_path):
    """Load configuration from YAML file."""
    if not os.path.exists(config_path):
        logger.warning(f"Config file not found: {config_path}")
        return {}
    
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        return {}

def process_pdf(input_path, output_path, config):
    """Process a single PDF file."""
    logger.info(f"Processing: {input_path}")
    
    try:
        # Create academic paper config
        academic_config = AcademicPaperConfig(
            language=config.get('ocr', {}).get('language', 'eng'),
            psm=config.get('ocr', {}).get('psm', 3),
            oem=config.get('ocr', {}).get('oem', 3),
            enhance_contrast=config.get('academic', {}).get('preprocessing', {}).get('enhance_contrast', True),
            denoise=config.get('academic', {}).get('preprocessing', {}).get('denoise', False),
            sharpen=config.get('academic', {}).get('preprocessing', {}).get('sharpen', True),
            math_detection=config.get('content_detection', {}).get('formulas', True),
            table_detection=config.get('content_detection', {}).get('tables', True),
            citation_detection=config.get('content_detection', {}).get('citations', True),
        )
        
        # Initialize processor
        processor = AcademicProcessor(academic_config)
        
        # Initialize enhancer
        enhancer = BasicEnhancer()
        
        # Process the PDF
        with pikepdf.open(input_path) as pdf:
            # Process each page
            for page_num, page in enumerate(pdf.pages):
                logger.info(f"Processing page {page_num+1} of {len(pdf.pages)}")
                
                # Extract page as image
                # This is a simplified approach - in production you'd use a more robust method
                try:
                    # Read PDF page to image using renderer in pikepdf or alternative
                    # For demonstration, we'll use a placeholder for the actual rendering
                    # In a real implementation, you would extract the page as an image
                    
                    # Process academic content
                    # Note: In a real implementation, you would process the actual page image
                    # Here we're only implementing the enhancement part for simplicity
                    pass
                    
                except Exception as e:
                    logger.error(f"Error processing page {page_num+1}: {e}")
            
            # Enhance the PDF with basic accessibility features
            # Set extract_title_from_h1 to True to use H1 tag for title extraction
            # Pass filename as a fallback option
            enhanced_pdf = enhancer.enhance(
                pdf, 
                filename=Path(input_path).name,
                extract_title_from_h1=True,
                extract_title_from_filename=False,  # Only use filename as fallback
                language="en-US"
            )
            
            # Save the enhanced PDF
            enhanced_pdf.save(output_path)
            
        logger.info(f"Successfully processed: {input_path} -> {output_path}")
        return True
        
    except Exception as e:
        logger.error(f"Error processing {input_path}: {e}")
        return False

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Load configuration
    config = load_config(args.config)
    
    # Print banner
    print("\n=======================================================")
    print("  Academic Paper Accessibility Processor (Local Mode)")
    print("=======================================================\n")
    
    print("Processing with settings:")
    print(f"  Mode:     Academic papers")
    print(f"  Timeout:  {args.timeout}s")
    print(f"  Batch:    {args.batch}")
    print(f"  Config:   {args.config}")
    print()
    
    # Create output directory if needed
    output_path = Path(args.output)
    if args.batch:
        output_path.mkdir(parents=True, exist_ok=True)
    else:
        output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Process files
    if args.batch:
        # Find all PDF files in input directory
        input_dir = Path(args.input)
        pdf_files = list(input_dir.glob("**/*.pdf"))
        
        print(f"Processing batch:")
        print(f"  Input directory:  {args.input}")
        print(f"  Output directory: {args.output}")
        print(f"Found {len(pdf_files)} PDF files to process")
        
        # Process each file
        success_count = 0
        for input_file in tqdm(pdf_files, desc="Processing files"):
            # Create relative path for output
            rel_path = input_file.relative_to(input_dir)
            output_file = output_path / rel_path
            
            # Create output directory if needed
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Process the file
            if process_pdf(input_file, output_file, config):
                success_count += 1
        
        print(f"Successfully processed {success_count} of {len(pdf_files)} files")
        
    else:
        # Process single file
        process_pdf(args.input, args.output, config)
    
    print("\n✓ Processing complete")
    return 0

if __name__ == "__main__":
    sys.exit(main())