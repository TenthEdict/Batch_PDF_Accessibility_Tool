#!/usr/bin/env python3
"""
Document conversion utilities for SmolDocling.
Converts various document formats to PDF for processing.
"""

import os
import subprocess
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple

import fitz  # PyMuPDF
from PIL import Image


class DocumentConverter:
    """Utility class for converting various document formats to PDF."""
    
    SUPPORTED_OFFICE_FORMATS = {
        ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"
    }
    
    SUPPORTED_IMAGE_FORMATS = {
        ".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp"
    }

    def __init__(self, libreoffice_path: Optional[str] = None):
        """
        Initialize document converter.
        
        Args:
            libreoffice_path: Path to LibreOffice executable. If None, attempts to find it.
        """
        # Find LibreOffice executable
        self.libreoffice_path = libreoffice_path
        if self.libreoffice_path is None:
            for path in [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",  # macOS
                "/usr/bin/libreoffice",  # Linux
                "C:/Program Files/LibreOffice/program/soffice.exe",  # Windows
            ]:
                if os.path.exists(path):
                    self.libreoffice_path = path
                    break
    
    def detect_format(self, file_path: str) -> str:
        """
        Detect file format from extension.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            File format category: 'pdf', 'image', 'office', or 'unknown'.
        """
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return "pdf"
        elif ext in self.SUPPORTED_IMAGE_FORMATS:
            return "image"
        elif ext in self.SUPPORTED_OFFICE_FORMATS:
            return "office"
        else:
            return "unknown"
    
    def convert_office_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert Office documents to PDF using LibreOffice.
        
        Args:
            input_path: Path to the input Office document.
            output_path: Path to save the output PDF.
            
        Returns:
            True if conversion was successful, False otherwise.
        """
        if self.libreoffice_path is None:
            print("LibreOffice not found. Cannot convert Office documents.")
            return False
        
        # Create temporary directory for conversion
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Run LibreOffice to convert document to PDF
                cmd = [
                    self.libreoffice_path,
                    "--headless",
                    "--convert-to", "pdf",
                    "--outdir", temp_dir,
                    input_path
                ]
                
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Move the converted file to the output path
                input_filename = Path(input_path).stem
                temp_pdf = os.path.join(temp_dir, f"{input_filename}.pdf")
                
                if os.path.exists(temp_pdf):
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    os.rename(temp_pdf, output_path)
                    return True
                else:
                    print(f"Conversion failed: Output file not found at {temp_pdf}")
                    return False
            
            except subprocess.CalledProcessError as e:
                print(f"LibreOffice conversion failed: {e}")
                print(f"Error output: {e.stderr.decode() if e.stderr else 'None'}")
                return False
            except Exception as e:
                print(f"Error during Office conversion: {str(e)}")
                return False

    def convert_docx_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert DOCX to PDF using python-docx (fallback if LibreOffice is not available).
        This is a limited fallback and won't preserve all formatting.
        
        Args:
            input_path: Path to the input DOCX document.
            output_path: Path to save the output PDF.
            
        Returns:
            True if conversion was successful, False otherwise.
        """
        try:
            import docx
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Load DOCX document
            doc = docx.Document(input_path)
            
            # Create PDF document
            pdf_doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            flowables = []
            
            # Convert paragraphs
            for para in doc.paragraphs:
                if para.text:
                    p = Paragraph(para.text, styles["Normal"])
                    flowables.append(p)
                    flowables.append(Spacer(1, 6))
            
            # Build PDF
            pdf_doc.build(flowables)
            return True
            
        except ImportError:
            print("reportlab not found. Cannot convert DOCX to PDF.")
            return False
        except Exception as e:
            print(f"Error during DOCX conversion: {str(e)}")
            return False

    def convert_pptx_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert PPTX to PDF using python-pptx (fallback if LibreOffice is not available).
        This is a limited fallback and won't preserve all formatting.
        
        Args:
            input_path: Path to the input PPTX document.
            output_path: Path to save the output PDF.
            
        Returns:
            True if conversion was successful, False otherwise.
        """
        try:
            import pptx
            from reportlab.lib.pagesizes import letter, landscape
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
            from reportlab.lib.styles import getSampleStyleSheet
            
            # Load PPTX document
            presentation = pptx.Presentation(input_path)
            
            # Create PDF document
            pdf_doc = SimpleDocTemplate(output_path, pagesize=landscape(letter))
            styles = getSampleStyleSheet()
            flowables = []
            
            # Convert slides
            for slide in presentation.slides:
                for shape in slide.shapes:
                    if hasattr(shape, "text") and shape.text:
                        p = Paragraph(shape.text, styles["Normal"])
                        flowables.append(p)
                        flowables.append(Spacer(1, 12))
                
                # Add page break between slides
                flowables.append(Paragraph("<br/><br/>", styles["Normal"]))
            
            # Build PDF
            pdf_doc.build(flowables)
            return True
            
        except ImportError:
            print("reportlab not found. Cannot convert PPTX to PDF.")
            return False
        except Exception as e:
            print(f"Error during PPTX conversion: {str(e)}")
            return False

    def convert_image_to_pdf(self, input_path: str, output_path: str) -> bool:
        """
        Convert an image to PDF.
        
        Args:
            input_path: Path to the input image.
            output_path: Path to save the output PDF.
            
        Returns:
            True if conversion was successful, False otherwise.
        """
        try:
            # Open image with PIL
            img = Image.open(input_path).convert("RGB")
            
            # Save as PDF
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            img.save(output_path, "PDF")
            return True
            
        except Exception as e:
            print(f"Error during image conversion: {str(e)}")
            return False

    def convert_to_pdf(self, input_path: str, output_path: Optional[str] = None) -> Tuple[bool, str]:
        """
        Convert any supported document to PDF.
        
        Args:
            input_path: Path to the input document.
            output_path: Path to save the output PDF. If None, uses input path with .pdf extension.
            
        Returns:
            Tuple of (success, output_path)
        """
        # Determine output path if not provided
        if output_path is None:
            output_dir = os.path.dirname(input_path)
            output_filename = f"{Path(input_path).stem}.pdf"
            output_path = os.path.join(output_dir, output_filename)
        
        # If it's already a PDF, just copy it (or return the path if they're the same)
        if input_path.lower().endswith(".pdf"):
            if input_path != output_path:
                import shutil
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
                shutil.copy2(input_path, output_path)
            return True, output_path
        
        # Detect format and convert accordingly
        format_type = self.detect_format(input_path)
        success = False
        
        if format_type == "image":
            success = self.convert_image_to_pdf(input_path, output_path)
        elif format_type == "office":
            # Try LibreOffice first
            if self.libreoffice_path is not None:
                success = self.convert_office_to_pdf(input_path, output_path)
            
            # Fall back to Python libraries if LibreOffice fails or is not available
            if not success:
                if input_path.lower().endswith((".doc", ".docx")):
                    success = self.convert_docx_to_pdf(input_path, output_path)
                elif input_path.lower().endswith((".ppt", ".pptx")):
                    success = self.convert_pptx_to_pdf(input_path, output_path)
        else:
            print(f"Unsupported file format: {input_path}")
            return False, ""
        
        return success, output_path

    def extract_pdf_pages_as_images(self, pdf_path: str, output_dir: str, 
                                   dpi: int = 600) -> List[str]:
        """
        Extract pages from a PDF as images.
        
        Args:
            pdf_path: Path to the PDF.
            output_dir: Directory to save the images.
            dpi: Resolution for extracted images (default increased to 600 for better OCR).
            
        Returns:
            List of paths to the extracted images.
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Open PDF
            pdf = fitz.open(pdf_path)
            image_paths = []
            
            # Extract each page
            for i, page in enumerate(pdf):
                # Check if page has low contrast or JBIG2 compression issues
                has_jbig2 = False
                # Check page dictionary for JBIG2 decoders
                if "jbig2" in str(page).lower() or "jbig2decode" in str(page).lower():
                    has_jbig2 = True
                    print(f"JBIG2 compression detected on page {i+1}, using enhanced extraction")
                
                # Render page to image with higher resolution for better OCR
                # Increase resolution for JBIG2 compressed pages
                resolution = dpi * 1.5 if has_jbig2 else dpi
                pix = page.get_pixmap(matrix=fitz.Matrix(resolution/72, resolution/72))
                
                # Determine output path
                output_path = os.path.join(
                    output_dir, 
                    f"{Path(pdf_path).stem}_page_{i+1}.png"
                )
                
                # Save image
                pix.save(output_path)
                image_paths.append(output_path)
            
            return image_paths
            
        except Exception as e:
            print(f"Error extracting PDF pages: {str(e)}")
            return []


def convert_documents(input_paths: List[str], output_dir: str) -> List[str]:
    """
    Convert multiple documents to PDF.
    
    Args:
        input_paths: List of paths to input documents.
        output_dir: Directory to save the converted PDFs.
        
    Returns:
        List of paths to the converted PDFs.
    """
    converter = DocumentConverter()
    pdf_paths = []
    
    for input_path in input_paths:
        # Determine output path
        output_filename = f"{Path(input_path).stem}.pdf"
        output_path = os.path.join(output_dir, output_filename)
        
        # Convert to PDF
        success, pdf_path = converter.convert_to_pdf(input_path, output_path)
        if success:
            pdf_paths.append(pdf_path)
    
    return pdf_paths


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert documents to PDF")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", default="./data/output", help="Output directory")
    
    args = parser.parse_args()
    
    # Process input (file or directory)
    input_path = Path(args.input)
    if input_path.is_file():
        # Single file
        convert_documents([str(input_path)], args.output)
    else:
        # Directory
        supported_extensions = DocumentConverter.SUPPORTED_OFFICE_FORMATS.union(
            DocumentConverter.SUPPORTED_IMAGE_FORMATS
        ).union({".pdf"})
        
        files = []
        for ext in supported_extensions:
            files.extend(list(input_path.glob(f"*{ext}")))
        
        if not files:
            print(f"No supported files found in {input_path}")
        else:
            convert_documents([str(path) for path in files], args.output)