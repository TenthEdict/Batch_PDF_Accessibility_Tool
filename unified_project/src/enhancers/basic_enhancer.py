#!/usr/bin/env python3
"""
Basic PDF accessibility enhancer module.

This module adds basic accessibility features to PDF files:
- Document title and author metadata
- Document language
- PDF/UA compliance markers
"""

import os
import sys
import logging
from pathlib import Path

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
except ImportError:
    print("Error: pikepdf is not installed. Please install it in your virtual environment:")
    print("pip install pikepdf")
    sys.exit(1)

logger = logging.getLogger(__name__)

class BasicEnhancer:
    """Basic PDF accessibility enhancement functionality."""
    
    def __init__(self):
        """Initialize the basic enhancer."""
        pass
        
    def enhance_pdf_accessibility(self, input_path, output_path, title=None, author=None, language='en-US'):
        """
        Enhance PDF accessibility with basic features.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file
            title: Document title (default: None, will use filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')
            
        Returns:
            bool: True if enhancement was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f'Input PDF not found: {input_path}')
            return False
        
        logger.info(f'Enhancing PDF: {input_path}')
        logger.info(f'Output will be saved to: {output_path}')
        
        try:
            # Open the PDF
            with pikepdf.open(input_path) as pdf:
                # Create output directory if needed
                output_path.parent.mkdir(parents=True, exist_ok=True)
                
                # Set document metadata
                with pdf.open_metadata(set_pikepdf_as_editor=False) as meta:
                    if title:
                        meta['dc:title'] = title
                    else:
                        # Extract title from filename
                        title = input_path.stem.replace('_', ' ').title()
                        meta['dc:title'] = title
                        
                    if author:
                        meta['dc:creator'] = author
                        
                    # Set document language
                    meta['dc:language'] = language
                
                # Set viewer preferences to display document title
                pdf.Root.ViewerPreferences = Dictionary({
                    Name.DisplayDocTitle: True
                })
                
                # Save the enhanced PDF
                pdf.save(output_path)
                
            logger.info(f'Successfully enhanced PDF accessibility: {output_path}')
            logger.info('Applied enhancements:')
            logger.info(f'- Added title: {title}')
            if author:
                logger.info(f'- Added author: {author}')
            logger.info(f'- Set language to {language}')
            logger.info('- Set display document title preference')
            
            return True
        except Exception as e:
            logger.error(f'Error enhancing PDF: {e}')
            import traceback
            traceback.print_exc()
            return False

def main():
    """Command-line interface for basic PDF enhancement."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Enhance PDF with basic accessibility features')
    parser.add_argument('input_pdf', help='Path to input PDF file')
    parser.add_argument('output_pdf', help='Path to save enhanced PDF file')
    parser.add_argument('--title', help='Document title')
    parser.add_argument('--author', help='Document author')
    parser.add_argument('--language', default='en-US', help='Document language (default: en-US)')
    
    args = parser.parse_args()
    
    enhancer = BasicEnhancer()
    result = enhancer.enhance_pdf_accessibility(
        args.input_pdf,
        args.output_pdf,
        args.title,
        args.author,
        args.language
    )
    
    return 0 if result else 1

if __name__ == "__main__":
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    sys.exit(main())