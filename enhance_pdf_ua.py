#!/usr/bin/env python3
"""
PDF Accessibility Enhancer - Standalone Script

Enhances PDFs with accessibility features, including:
1. Document tagging
2. Document structure
3. Language setting
4. Initial view setting
5. PDF/UA compliance

Usage: python enhance_pdf_ua.py <input_pdf> [<output_pdf>] [--title "Title"] [--author "Author"]
"""

import os
import sys
import logging
import argparse
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Import functions from post_processor
try:
    sys.path.append(str(Path(__file__).parent / 'brodie_code' / 'src'))
    from accessibility_checker.core.post_processor import (
        update_metadata,
        set_pdf_language,
        set_initial_view_title,
        mark_pdf_as_tagged,
        create_document_structure,
        ensure_fonts_embedded,
        append_xmp_to_multiple_pdfs
    )
    logger.info("Successfully imported accessibility functions")
except ImportError as e:
    logger.error(f"Error importing required modules: {e}")
    sys.exit(1)

def enhance_pdf(input_path, output_path=None, title=None, author=None):
    """
    Enhance a PDF with accessibility features
    
    Args:
        input_path: Path to input PDF
        output_path: Path to save enhanced PDF (if None, modifies input)
        title: Document title (optional)
        author: Document author (optional)
        
    Returns:
        Path to enhanced PDF
    """
    input_path = Path(input_path).resolve()
    
    if not input_path.exists():
        logger.error(f"Input file does not exist: {input_path}")
        return None
        
    # If output_path is not specified, create one in the same directory
    if output_path is None:
        output_path = input_path.parent / f"{input_path.stem}_accessible{input_path.suffix}"
    else:
        output_path = Path(output_path).resolve()
        
    # Create output directory if it doesn't exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Enhancing PDF accessibility:")
    logger.info(f"Input: {input_path}")
    logger.info(f"Output: {output_path}")
    
    try:
        # Create a copy if input and output paths are different
        if input_path != output_path:
            import pikepdf
            with pikepdf.open(input_path) as pdf:
                pdf.save(output_path)
            logger.info(f"Created copy at {output_path}")
        
        # Apply accessibility enhancements
        update_metadata(output_path, title, [author] if author else None)
        set_pdf_language(output_path)
        set_initial_view_title(output_path)
        mark_pdf_as_tagged(output_path)
        create_document_structure(output_path)
        ensure_fonts_embedded(output_path)
        
        # Find and add PDF/UA-ID.xmp
        xmp_paths = [
            Path(__file__).parent / 'brodie_code' / 'pdfUA-ID.xmp',
            Path('/Users/broderickschipp/work/ePubs_AccProj/brodie_code/pdfUA-ID.xmp')
        ]
        
        xmp_path = None
        for path in xmp_paths:
            if path.exists():
                xmp_path = path
                break
                
        if xmp_path:
            # Create temporary directory for PDF/UA processing
            temp_dir = output_path.parent / '.temp'
            temp_dir.mkdir(exist_ok=True)
            
            # Copy enhanced PDF to temp dir
            import shutil
            temp_pdf = temp_dir / output_path.name
            shutil.copy2(output_path, temp_pdf)
            
            # Apply PDF/UA metadata
            append_xmp_to_multiple_pdfs(str(temp_dir), str(xmp_path))
            
            # Copy back to original output path
            shutil.copy2(temp_pdf, output_path)
            
            # Clean up
            if temp_pdf.exists():
                temp_pdf.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
                
            logger.info("Added PDF/UA compliance metadata")
        else:
            logger.warning("PDF/UA XMP file not found, skipping PDF/UA compliance")
            
        logger.info(f"Successfully enhanced PDF accessibility: {output_path}")
        return output_path
            
    except Exception as e:
        logger.error(f"Error enhancing PDF: {e}")
        import traceback
        traceback.print_exc()
        return None

def main():
    parser = argparse.ArgumentParser(description='Enhance PDF with accessibility features')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', nargs='?', help='Path to save enhanced PDF (optional)')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    
    args = parser.parse_args()
    
    enhanced_pdf = enhance_pdf(
        args.input_pdf,
        args.output_pdf,
        args.title,
        args.author
    )
    
    if enhanced_pdf:
        logger.info(f"PDF successfully enhanced and saved to: {enhanced_pdf}")
        return 0
    else:
        logger.error("Failed to enhance PDF")
        return 1

if __name__ == "__main__":
    sys.exit(main())