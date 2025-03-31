#!/usr/bin/env python3
"""
Academic paper processing module for SmolDocling.
Provides specialized handling for academic papers with features like
two-column layout detection, metadata extraction, and formula preservation.
"""

import os
import re
import json
import fitz  # PyMuPDF
import cv2
import numpy as np
from typing import Dict, List, Optional, Tuple, Any
from pathlib import Path

from docling_core.types import DoclingDocument


class AcademicPaperProcessor:
    """Specialized processor for academic papers."""
    
    def __init__(self):
        """Initialize the academic paper processor."""
        pass

    def extract_metadata_from_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        Extract metadata from PDF (title, authors, abstract, etc.).
        
        Args:
            pdf_path: Path to the PDF.
            
        Returns:
            Dictionary containing extracted metadata.
        """
        metadata = {
            "title": None,
            "authors": [],
            "abstract": None,
            "keywords": [],
            "doi": None,
            "year": None,
        }
        
        try:
            # Open PDF
            doc = fitz.open(pdf_path)
            
            # Get document metadata
            doc_info = doc.metadata
            if doc_info:
                if "title" in doc_info and doc_info["title"]:
                    metadata["title"] = doc_info["title"]
                if "author" in doc_info and doc_info["author"]:
                    # Split authors string into list
                    authors = doc_info["author"].split(",")
                    metadata["authors"] = [a.strip() for a in authors]
            
            # Extract text from first page
            first_page = doc[0]
            text = first_page.get_text()
            
            # Try to extract abstract
            abstract_match = re.search(r"(?i)abstract[\s\n]*(.+?)(?:\n\n|\n[A-Z][a-z]+:|\nKeywords:|\nIndex Terms:)", text, re.DOTALL)
            if abstract_match:
                metadata["abstract"] = abstract_match.group(1).strip()
            
            # Try to extract keywords
            keywords_match = re.search(r"(?i)(keywords|index terms)[\s\n]*:[\s\n]*(.+?)(?:\n\n|\n[A-Z][a-z]+:)", text, re.DOTALL)
            if keywords_match:
                keywords_text = keywords_match.group(2)
                # Split by commas or semicolons
                keywords = re.split(r"[,;]", keywords_text)
                metadata["keywords"] = [k.strip() for k in keywords if k.strip()]
            
            # Try to extract DOI
            doi_match = re.search(r"(?i)(?:doi|DOI)[\s:]*(?:https?://doi\.org/|https?://dx\.doi\.org/|)([0-9.]+/[^\s]+)", text)
            if doi_match:
                metadata["doi"] = doi_match.group(1).strip()
            
            # Try to extract year
            year_match = re.search(r"(?:©|\(c\)|Copyright\s+)(?:\s*)[12][0-9]{3}", text)
            if year_match:
                year_text = year_match.group(0)
                year_only = re.search(r"[12][0-9]{3}", year_text)
                if year_only:
                    metadata["year"] = int(year_only.group(0))
            
            doc.close()
            
        except Exception as e:
            print(f"Error extracting metadata: {str(e)}")
        
        return metadata

    def detect_layout(self, img: np.ndarray) -> str:
        """
        Detect document layout (single column, double column, etc.).
        
        Args:
            img: Document image.
            
        Returns:
            Layout type ("single_column", "double_column").
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations to enhance text blocks
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Find contours of text blocks
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Analyze horizontal distribution of contours
        width = gray.shape[1]
        left_half_count = 0
        right_half_count = 0
        mid_count = 0
        
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            center_x = x + w/2
            
            # Count contours in left, middle, and right portions
            if center_x < width * 0.4:
                left_half_count += 1
            elif center_x > width * 0.6:
                right_half_count += 1
            else:
                mid_count += 1
        
        # If significant contours in both left and right sides with few in middle,
        # likely a double-column layout
        if (left_half_count > 2 and right_half_count > 2 and 
            mid_count < (left_half_count + right_half_count) / 2):
            return "double_column"
        else:
            return "single_column"

    def detect_tables(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect tables in document image.
        
        Args:
            img: Document image.
            
        Returns:
            List of detected tables with their bounding boxes.
        """
        tables = []
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations to detect table structures
        # Horizontal lines
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (50, 1))
        horizontal_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, horizontal_kernel, iterations=1)
        
        # Vertical lines
        vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 50))
        vertical_lines = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, vertical_kernel, iterations=1)
        
        # Combine lines
        table_mask = cv2.bitwise_or(horizontal_lines, vertical_lines)
        
        # Find contours of potential tables
        contours, _ = cv2.findContours(table_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and process contours
        height, width = img.shape[:2]
        min_area = 0.005 * height * width  # Minimum area threshold
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < min_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Normalize coordinates to [0, 1] range
            bbox = [
                x / width,
                y / height,
                (x + w) / width,
                (y + h) / height
            ]
            
            # Add table detection
            tables.append({
                "type": "table",
                "bbox": bbox,
                "confidence": float(area) / (height * width)  # Confidence based on area
            })
        
        return tables

    def detect_figures(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect figures in document image.
        
        Args:
            img: Document image.
            
        Returns:
            List of detected figures with their bounding boxes.
        """
        figures = []
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find text blocks
        text_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 5))
        text_mask = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, text_kernel, iterations=1)
        
        # Invert to get non-text regions
        non_text = cv2.bitwise_not(text_mask)
        
        # Find contours of potential figures
        contours, _ = cv2.findContours(non_text, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter and process contours
        height, width = img.shape[:2]
        min_area = 0.01 * height * width  # Minimum area threshold
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < min_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Simple check for aspect ratio
            aspect_ratio = w / h
            if aspect_ratio < 0.2 or aspect_ratio > 5:
                continue  # Skip extremely narrow or wide contours
            
            # Normalize coordinates to [0, 1] range
            bbox = [
                x / width,
                y / height,
                (x + w) / width,
                (y + h) / height
            ]
            
            # Check if this region likely contains a figure
            # (This is a simplistic approach - would need more sophisticated
            # image analysis for better figure detection)
            roi = gray[y:y+h, x:x+w]
            
            # Simple variance check to determine if the region has significant features
            std_dev = np.std(roi)
            if std_dev > 30:  # Threshold for variance
                figures.append({
                    "type": "figure",
                    "bbox": bbox,
                    "confidence": float(std_dev) / 255  # Confidence based on variance
                })
        
        return figures

    def detect_math_formulas(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect mathematical formulas in document image.
        
        Args:
            img: Document image.
            
        Returns:
            List of detected formulas with their bounding boxes.
        """
        # Note: This is a simplified method that attempts to detect formula regions
        # based on visual characteristics. For production use, ML-based detection
        # would be more reliable.
        
        formulas = []
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find potential formula regions
        # Look for regions with more vertical variance and certain density patterns
        height, width = img.shape[:2]
        
        # Apply morphological operations to enhance isolated symbols
        symbol_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        symbols = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, symbol_kernel, iterations=1)
        
        # Dilate to connect nearby symbols
        connect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 5))
        connected = cv2.dilate(symbols, connect_kernel, iterations=1)
        
        # Find contours
        contours, _ = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours
        min_area = 0.001 * height * width  # Minimum area threshold
        
        for contour in contours:
            area = cv2.contourArea(contour)
            
            # Skip very small contours
            if area < min_area:
                continue
            
            # Get bounding box
            x, y, w, h = cv2.boundingRect(contour)
            
            # Check aspect ratio
            aspect_ratio = w / h
            if aspect_ratio > 10 or aspect_ratio < 0.1:
                continue  # Skip very long or tall regions
            
            # Create region of interest
            roi = thresh[y:y+h, x:x+w]
            
            # Check density and pattern of symbols
            density = np.sum(roi) / (255 * roi.size)
            
            # Formula regions typically have moderate density
            if 0.05 < density < 0.4:
                # Normalize coordinates to [0, 1] range
                bbox = [
                    x / width,
                    y / height,
                    (x + w) / width,
                    (y + h) / height
                ]
                
                formulas.append({
                    "type": "formula",
                    "bbox": bbox,
                    "confidence": float(density) * 2  # Simple confidence metric
                })
        
        return formulas

    def detect_headers_footers(self, img: np.ndarray) -> List[Dict[str, Any]]:
        """
        Detect headers and footers in document image.
        
        Args:
            img: Document image.
            
        Returns:
            List of detected headers/footers with their bounding boxes.
        """
        headers_footers = []
        
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        height, width = gray.shape
        
        # Define regions for header and footer (top and bottom 10% of page)
        header_region = gray[:int(height * 0.1), :]
        footer_region = gray[int(height * 0.9):, :]
        
        # Apply threshold to both regions
        _, header_thresh = cv2.threshold(header_region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        _, footer_thresh = cv2.threshold(footer_region, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours in header
        header_contours, _ = cv2.findContours(header_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find contours in footer
        footer_contours, _ = cv2.findContours(footer_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Process header contours
        if header_contours:
            header_area = 0
            header_bbox = [width, height, 0, 0]  # Initialize with extreme values
            
            for contour in header_contours:
                x, y, w, h = cv2.boundingRect(contour)
                header_area += w * h
                
                # Update bounding box
                header_bbox[0] = min(header_bbox[0], x)
                header_bbox[1] = min(header_bbox[1], y)
                header_bbox[2] = max(header_bbox[2], x + w)
                header_bbox[3] = max(header_bbox[3], y + h)
            
            # Check if header area is significant
            if header_area > 100:
                # Normalize coordinates to [0, 1] range and adjust y-coordinates
                normalized_bbox = [
                    header_bbox[0] / width,
                    header_bbox[1] / height,
                    header_bbox[2] / width,
                    header_bbox[3] / height
                ]
                
                headers_footers.append({
                    "type": "header",
                    "bbox": normalized_bbox,
                    "confidence": 0.8
                })
        
        # Process footer contours
        if footer_contours:
            footer_area = 0
            footer_bbox = [width, height, 0, 0]  # Initialize with extreme values
            
            for contour in footer_contours:
                x, y, w, h = cv2.boundingRect(contour)
                # Adjust y-coordinate to account for footer region offset
                y += int(height * 0.9)
                footer_area += w * h
                
                # Update bounding box
                footer_bbox[0] = min(footer_bbox[0], x)
                footer_bbox[1] = min(footer_bbox[1], y)
                footer_bbox[2] = max(footer_bbox[2], x + w)
                footer_bbox[3] = max(footer_bbox[3], y + h)
            
            # Check if footer area is significant
            if footer_area > 100:
                # Normalize coordinates to [0, 1] range
                normalized_bbox = [
                    footer_bbox[0] / width,
                    footer_bbox[1] / height,
                    footer_bbox[2] / width,
                    footer_bbox[3] / height
                ]
                
                headers_footers.append({
                    "type": "footer",
                    "bbox": normalized_bbox,
                    "confidence": 0.8
                })
        
        return headers_footers

    def process_academic_paper(self, image_path: str, pdf_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an academic paper image with specialized handling.
        
        Args:
            image_path: Path to the document image.
            pdf_path: Optional path to the source PDF for metadata extraction.
            
        Returns:
            Dictionary with processing results.
        """
        # Load image
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        # Extract metadata if PDF is provided
        metadata = {}
        if pdf_path and os.path.exists(pdf_path):
            metadata = self.extract_metadata_from_pdf(pdf_path)
        
        # Detect layout
        layout = self.detect_layout(img)
        
        # Detect tables
        tables = self.detect_tables(img)
        
        # Detect figures
        figures = self.detect_figures(img)
        
        # Detect math formulas
        formulas = self.detect_math_formulas(img)
        
        # Detect headers/footers
        headers_footers = self.detect_headers_footers(img)
        
        # Combine results
        results = {
            "image_path": image_path,
            "metadata": metadata,
            "layout": layout,
            "elements": tables + figures + formulas + headers_footers
        }
        
        return results

    def enhance_docling_document(self, document: DoclingDocument, 
                               academic_results: Dict[str, Any]) -> DoclingDocument:
        """
        Enhance a DoclingDocument with academic paper specific information.
        
        Args:
            document: Original DoclingDocument from SmolDocling.
            academic_results: Results from academic paper processing.
            
        Returns:
            Enhanced DoclingDocument.
        """
        # Add metadata
        if "metadata" in academic_results and academic_results["metadata"]:
            document.metadata.update(academic_results["metadata"])
        
        # Add document layout information
        if "layout" in academic_results:
            document.metadata["layout"] = academic_results["layout"]
        
        # Function to check if an element overlaps with academic elements
        def get_overlapping_element(bbox, academic_elements, threshold=0.5):
            for elem in academic_elements:
                elem_bbox = elem["bbox"]
                
                # Calculate overlap
                x_overlap = max(0, min(bbox[2], elem_bbox[2]) - max(bbox[0], elem_bbox[0]))
                y_overlap = max(0, min(bbox[3], elem_bbox[3]) - max(bbox[1], elem_bbox[1]))
                
                overlap_area = x_overlap * y_overlap
                bbox_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
                
                # If significant overlap, return this academic element
                if overlap_area > threshold * bbox_area:
                    return elem
            
            return None
        
        # Enhance existing elements with academic information
        for element in document.elements:
            if "bbox" in element:
                bbox = element["bbox"]
                
                # Check for overlap with academic elements
                academic_elem = get_overlapping_element(bbox, academic_results.get("elements", []))
                
                if academic_elem:
                    # Update element type and add academic information
                    element["academic_type"] = academic_elem["type"]
                    element["confidence"] = academic_elem.get("confidence", 0.5)
        
        return document


if __name__ == "__main__":
    import argparse
    from PIL import Image
    
    parser = argparse.ArgumentParser(description="Process academic papers")
    parser.add_argument("--image", "-i", required=True, help="Input image file")
    parser.add_argument("--pdf", "-p", default=None, help="Optional source PDF file")
    parser.add_argument("--output", "-o", default="./data/output", help="Output directory")
    
    args = parser.parse_args()
    
    processor = AcademicPaperProcessor()
    
    try:
        # Process academic paper
        results = processor.process_academic_paper(args.image, args.pdf)
        
        # Save results
        os.makedirs(args.output, exist_ok=True)
        output_path = os.path.join(args.output, f"{Path(args.image).stem}_academic.json")
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"Academic paper processing results saved to {output_path}")
        
        # Create visualization
        img = cv2.imread(args.image)
        height, width = img.shape[:2]
        
        for elem in results["elements"]:
            bbox = elem["bbox"]
            x0 = int(bbox[0] * width)
            y0 = int(bbox[1] * height)
            x1 = int(bbox[2] * width)
            y1 = int(bbox[3] * height)
            
            # Different color for different element types
            if elem["type"] == "table":
                color = (0, 0, 255)  # Red
            elif elem["type"] == "figure":
                color = (0, 255, 0)  # Green
            elif elem["type"] == "formula":
                color = (255, 0, 0)  # Blue
            elif elem["type"] in ["header", "footer"]:
                color = (255, 255, 0)  # Cyan
            else:
                color = (128, 128, 128)  # Gray
            
            cv2.rectangle(img, (x0, y0), (x1, y1), color, 2)
            cv2.putText(img, elem["type"], (x0, y0-5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
        
        # Save visualization
        viz_path = os.path.join(args.output, f"{Path(args.image).stem}_visualization.png")
        cv2.imwrite(viz_path, img)
        print(f"Visualization saved to {viz_path}")
        
    except Exception as e:
        print(f"Error processing academic paper: {str(e)}")