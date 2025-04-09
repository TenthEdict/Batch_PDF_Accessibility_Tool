#!/usr/bin/env python3
"""
Standalone script to analyze if a document is historical.

This script examines a PDF document and determines whether it exhibits
characteristics of a historical document, providing detailed analysis.
"""

import argparse
import logging
import sys
import os
from pathlib import Path
import json
from pdf2image import convert_from_path
from PIL import Image

from .analyzer import HistoricalDocumentAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('historical_analyzer')

def analyze_document(pdf_path: str, output_format: str = 'text', output_file: str = None) -> dict:
    """
    Analyze a document to detect if it's historical.
    
    Args:
        pdf_path: Path to the PDF document
        output_format: Format for results ('text', 'json')
        output_file: Optional file to write results to
        
    Returns:
        Dictionary with analysis results
    """
    logger.info(f"Analyzing document: {pdf_path}")
    
    # Check if file exists
    if not os.path.exists(pdf_path):
        logger.error(f"File not found: {pdf_path}")
        return {"error": f"File not found: {pdf_path}"}
    
    try:
        # Convert first page to image
        pages = convert_from_path(pdf_path, first_page=1, last_page=1)
        if not pages:
            logger.error(f"Failed to convert PDF to image: {pdf_path}")
            return {"error": "Failed to convert PDF to image"}
        
        # Create analyzer
        analyzer = HistoricalDocumentAnalyzer()
        
        # Analyze first page
        characteristics = analyzer.analyze_image(pages[0])
        
        # Create result dictionary
        result = {
            "filename": os.path.basename(pdf_path),
            "is_historical": characteristics.is_historical,
            "estimated_age": characteristics.estimated_age,
            "historical_font_type": characteristics.historical_font_type,
            "metrics": {
                "paper_yellowing_score": characteristics.paper_yellowing_score,
                "faded_text_score": characteristics.faded_text_score,
                "text_density": characteristics.text_density,
                "layout_complexity": characteristics.layout_complexity,
                "skew_angle": characteristics.skew_angle
            }
        }
        
        # Output results
        if output_format == 'json':
            output = json.dumps(result, indent=2)
        else:
            # Text format
            output = f"Document Analysis: {os.path.basename(pdf_path)}\n"
            output += f"Is Historical: {characteristics.is_historical}\n"
            output += f"Estimated Age: {characteristics.estimated_age}\n"
            output += f"Historical Font Type: {characteristics.historical_font_type}\n\n"
            output += "Metrics:\n"
            output += f"  Paper Yellowing Score: {characteristics.paper_yellowing_score:.2f}\n"
            output += f"  Faded Text Score: {characteristics.faded_text_score:.2f}\n"
            output += f"  Text Density: {characteristics.text_density:.2f}\n"
            output += f"  Layout Complexity: {characteristics.layout_complexity:.2f}\n"
            output += f"  Skew Angle: {characteristics.skew_angle:.2f}\n"
        
        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(output)
            logger.info(f"Results written to {output_file}")
        else:
            print(output)
        
        return result
        
    except Exception as e:
        logger.error(f"Error analyzing document: {str(e)}")
        return {"error": str(e)}

def main():
    """Command line entry point."""
    parser = argparse.ArgumentParser(description="Analyze a document to detect if it's historical")
    parser.add_argument("pdf_path", help="Path to the PDF document to analyze")
    parser.add_argument("--format", choices=["text", "json"], default="text", 
                        help="Output format (text or json)")
    parser.add_argument("--output", help="Optional output file path")
    
    args = parser.parse_args()
    
    try:
        analyze_document(args.pdf_path, args.format, args.output)
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())