#!/usr/bin/env python3
"""
PDF Metadata Editor module.

This module provides functionality to update PDF metadata including:
- Document title, author, and language
- PDF/UA compliance markers
- Initial view settings
"""

import os
import sys
import logging
from pathlib import Path
import pandas as pd

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array, Object
except ImportError:
    print("Error: pikepdf is not installed. Please install it in your virtual environment:")
    print("pip install pikepdf")
    sys.exit(1)

logger = logging.getLogger(__name__)

class MetadataEditor:
    """PDF metadata editor for enhancing document accessibility."""
    
    def __init__(self):
        """Initialize the metadata editor."""
        pass
    
    def update_metadata(self, input_path, output_path, title=None, author=None, 
                       language='en-US', mark_as_tagged=True, 
                       add_pdfua_identifier=True):
        """
        Update PDF metadata to enhance accessibility.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path to output PDF file
            title: Document title (default: None, will use filename)
            author: Document author (default: None)
            language: Document language (default: 'en-US')
            mark_as_tagged: Mark document as tagged (default: True)
            add_pdfua_identifier: Add PDF/UA identifier (default: True)
            
        Returns:
            bool: True if update was successful, False otherwise
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f'Input PDF not found: {input_path}')
            return False
        
        logger.info(f'Updating metadata for PDF: {input_path}')
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
                    
                    # Add PDF/UA identifier if requested
                    if add_pdfua_identifier:
                        meta['pdfaid:part'] = '1'
                        meta['pdfaid:conformance'] = 'A'
                
                # Set viewer preferences to display document title
                pdf.Root.ViewerPreferences = Dictionary({
                    Name.DisplayDocTitle: True
                })
                
                # Set initial view settings for better accessibility
                pdf.Root.PageMode = Name.UseOutlines  # Show bookmarks panel
                
                # Mark document as tagged if requested
                if mark_as_tagged:
                    if Name.MarkInfo not in pdf.Root:
                        pdf.Root.MarkInfo = Dictionary({
                            Name.Marked: True
                        })
                    else:
                        pdf.Root.MarkInfo[Name.Marked] = True
                
                # Save the updated PDF
                pdf.save(output_path)
                
            logger.info(f'Successfully updated PDF metadata: {output_path}')
            logger.info('Applied updates:')
            logger.info(f'- Set title: {title}')
            if author:
                logger.info(f'- Set author: {author}')
            logger.info(f'- Set language to {language}')
            logger.info('- Set display document title preference')
            if mark_as_tagged:
                logger.info('- Marked document as tagged')
            if add_pdfua_identifier:
                logger.info('- Added PDF/UA identifier')
            
            return True
        except Exception as e:
            logger.error(f'Error updating PDF metadata: {e}')
            import traceback
            traceback.print_exc()
            return False
    
    def batch_update_from_excel(self, excel_path, input_dir, output_dir, 
                               mark_as_tagged=True, add_pdfua_identifier=True):
        """
        Update metadata for multiple PDFs based on Excel spreadsheet data.
        
        Args:
            excel_path: Path to Excel spreadsheet with metadata
            input_dir: Directory containing input PDF files
            output_dir: Directory to save output PDF files
            mark_as_tagged: Mark documents as tagged (default: True)
            add_pdfua_identifier: Add PDF/UA identifier (default: True)
            
        Returns:
            int: Number of successfully processed PDFs
        """
        excel_path = Path(excel_path)
        input_dir = Path(input_dir)
        output_dir = Path(output_dir)
        
        if not excel_path.exists():
            logger.error(f'Excel file not found: {excel_path}')
            return 0
        
        if not input_dir.exists() or not input_dir.is_dir():
            logger.error(f'Input directory not found: {input_dir}')
            return 0
        
        # Create output directory if needed
        output_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Read metadata from Excel spreadsheet
            logger.info(f'Reading metadata from Excel: {excel_path}')
            df = pd.read_excel(excel_path)
            
            required_columns = ['filename']
            optional_columns = ['title', 'author', 'language']
            
            # Check for required columns
            missing_columns = [col for col in required_columns if col not in df.columns]
            if missing_columns:
                logger.error(f'Missing required columns in Excel: {", ".join(missing_columns)}')
                return 0
            
            # Process each PDF file
            success_count = 0
            total_count = len(df)
            
            for index, row in df.iterrows():
                filename = row['filename']
                input_path = input_dir / filename
                output_path = output_dir / filename
                
                if not input_path.exists():
                    logger.warning(f'Input PDF not found: {input_path}')
                    continue
                
                # Extract metadata from Excel
                title = row.get('title') if 'title' in df.columns else None
                author = row.get('author') if 'author' in df.columns else None
                language = row.get('language') if 'language' in df.columns else 'en-US'
                
                # Update PDF metadata
                logger.info(f'Processing ({index+1}/{total_count}): {filename}')
                result = self.update_metadata(
                    input_path,
                    output_path,
                    title,
                    author,
                    language,
                    mark_as_tagged,
                    add_pdfua_identifier
                )
                
                if result:
                    success_count += 1
            
            logger.info(f'Batch processing complete: {success_count}/{total_count} PDFs successfully processed')
            return success_count
            
        except Exception as e:
            logger.error(f'Error in batch processing: {e}')
            import traceback
            traceback.print_exc()
            return 0

def main():
    """Command-line interface for PDF metadata updates."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Update PDF metadata for accessibility')
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # Single PDF command
    single_parser = subparsers.add_parser('single', help='Update metadata for a single PDF')
    single_parser.add_argument('input_pdf', help='Path to input PDF file')
    single_parser.add_argument('output_pdf', help='Path to save output PDF file')
    single_parser.add_argument('--title', help='Document title')
    single_parser.add_argument('--author', help='Document author')
    single_parser.add_argument('--language', default='en-US', help='Document language (default: en-US)')
    single_parser.add_argument('--no-tag', action='store_true', help='Do not mark document as tagged')
    single_parser.add_argument('--no-pdfua', action='store_true', help='Do not add PDF/UA identifier')
    
    # Batch command
    batch_parser = subparsers.add_parser('batch', help='Update metadata for multiple PDFs using Excel data')
    batch_parser.add_argument('excel', help='Path to Excel spreadsheet with metadata')
    batch_parser.add_argument('input_dir', help='Directory containing input PDF files')
    batch_parser.add_argument('output_dir', help='Directory to save output PDF files')
    batch_parser.add_argument('--no-tag', action='store_true', help='Do not mark documents as tagged')
    batch_parser.add_argument('--no-pdfua', action='store_true', help='Do not add PDF/UA identifier')
    
    args = parser.parse_args()
    
    editor = MetadataEditor()
    
    if args.command == 'single':
        result = editor.update_metadata(
            args.input_pdf,
            args.output_pdf,
            args.title,
            args.author,
            args.language,
            not args.no_tag,
            not args.no_pdfua
        )
        return 0 if result else 1
    
    elif args.command == 'batch':
        success_count = editor.batch_update_from_excel(
            args.excel,
            args.input_dir,
            args.output_dir,
            not args.no_tag,
            not args.no_pdfua
        )
        return 0 if success_count > 0 else 1
    
    else:
        parser.print_help()
        return 1

if __name__ == "__main__":
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )
    sys.exit(main())