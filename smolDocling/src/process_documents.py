#!/usr/bin/env python3
"""
SmolDocling document processing script for Apple Silicon.
Uses the SmolDocling-256M-preview-mlx-bf16 model to process document images.
Includes document format conversion, enhancement, and specialized academic paper processing.
"""

import os
import argparse
import multiprocessing
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple

import numpy as np
import cv2
from PIL import Image
from tqdm import tqdm
from huggingface_hub import hf_hub_download

# These will be installed with the requirements
from docling_core.types import DoclingDocument
import mlx_vlm

# Import local modules
from document_converter import DocumentConverter
from document_enhancer import DocumentEnhancer
from academic_processor import AcademicPaperProcessor


class DocumentProcessor:
    """Document processor using SmolDocling model optimized for Apple Silicon."""
    
    MODEL_ID = "ds4sd/SmolDocling-256M-preview-mlx-bf16"
    
    def __init__(self, model_path: Optional[str] = None, max_size: int = 1024, 
                 document_type: str = "general", process_academic: bool = False,
                 parallel: bool = False):
        """
        Initialize the document processor.
        
        Args:
            model_path: Path to model weights. If None, downloads from HuggingFace Hub.
            max_size: Maximum image dimension for processing.
            document_type: Type of document ('general', 'old_scan', 'faded').
            process_academic: Whether to apply specialized academic paper processing.
            parallel: Whether to use parallel processing for multi-page documents.
        """
        self.max_size = max_size
        self.document_type = document_type
        self.process_academic = process_academic
        self.parallel = False  # Always disable parallel processing
        self.num_cpus = min(multiprocessing.cpu_count(), 4)  # Limit to 4 CPUs max
        
        # Initialize converter and enhancer
        self.converter = DocumentConverter()
        self.enhancer = DocumentEnhancer()
        
        # Initialize academic processor if needed
        if process_academic:
            self.academic_processor = AcademicPaperProcessor()
        
        # Load model
        if model_path is None:
            print("Loading SmolDocling model from HuggingFace Hub...")
            model_path = self.MODEL_ID
        
        self.model, self.tokenizer = mlx_vlm.load(model_path)
        print(f"Model loaded from {model_path}")
    
    def preprocess_image(self, image_path: str) -> np.ndarray:
        """
        Preprocess image for model input with enhanced handling for document characteristics.
        
        Args:
            image_path: Path to input image.
        
        Returns:
            Preprocessed image as numpy array.
        """
        img = Image.open(image_path).convert("RGB")
        
        # Resize if needed while maintaining aspect ratio
        width, height = img.size
        if width > self.max_size or height > self.max_size:
            if width > height:
                new_width = self.max_size
                new_height = int(height * (self.max_size / width))
            else:
                new_height = self.max_size
                new_width = int(width * (self.max_size / height))
            img = img.resize((new_width, new_height), Image.LANCZOS)  # Use LANCZOS for better quality
        
        # Convert to numpy array
        img_array = np.array(img)
        
        # Check for low contrast and apply contrast enhancement if needed
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
        min_val, max_val, _, _ = cv2.minMaxLoc(gray)
        if (max_val - min_val) < 100:  # Low contrast threshold
            print(f"Low contrast detected in {image_path}, applying contrast enhancement")
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            # Convert back to RGB
            img_array = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        return img_array
    
    def _create_adaptive_prompt(self, image_path: str, img_array: np.ndarray) -> str:
        """
        Create an adaptive prompt based on document characteristics.
        
        Args:
            image_path: Path to the image file.
            img_array: Processed image as numpy array.
            
        Returns:
            Customized prompt for the document.
        """
        # Start with base prompt
        base_prompt = "Extract all text from this document, preserving layout and structure. Maintain paragraph breaks, columns, headers, and formatting."
        
        # Check file name for clues about document type
        filename = os.path.basename(image_path).lower()
        
        # Determine document characteristics
        is_old = any(term in filename for term in ["old", "historic", "ancient", "19"])
        is_scan = "scan" in filename
        is_academic = any(term in filename for term in ["paper", "journal", "academic", "research", "thesis"])
        
        # Add document-specific instructions
        adaptations = []
        
        # Handle document age
        if is_old:
            adaptations.append("This appears to be a historical document. Pay special attention to older typography and formatting.")
        
        # Handle scan quality
        if is_scan:
            adaptations.append("This is a scanned document that may have artifacts or noise. Focus on extracting the actual text content.")
        
        # Detect if document has multiple columns using simple heuristic
        gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY) if len(img_array.shape) == 3 else img_array
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Check for columns using vertical projection profile
        h, w = binary.shape
        vertical_projection = np.sum(binary, axis=0) / 255
        
        # Find potential column separators (vertical areas with few black pixels)
        potential_separators = []
        window_size = w // 10  # 10% of width
        for i in range(w - window_size):
            window_sum = np.sum(vertical_projection[i:i+window_size])
            if window_sum < 0.1 * h * window_size:  # Less than 10% of possible black pixels
                potential_separators.append(i + window_size//2)
        
        # If we find potential column separators in the middle section of the document
        has_columns = any(w//4 < sep < 3*w//4 for sep in potential_separators)
        
        if has_columns:
            adaptations.append("This document appears to have a multi-column layout. Make sure to correctly order the text from each column.")
        elif is_academic:
            adaptations.append("This appears to be an academic document. Pay attention to formulas, citations, and references.")
        
        # Check for rotated text
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=w//4)  # Threshold based on image width
        
        has_rotated_text = False
        if lines is not None:
            for line in lines:
                for rho, theta in line:
                    # Check for lines that are not horizontal or vertical (within tolerance)
                    if (0.1 < theta < 1.47) or (1.67 < theta < 3.04):  # Not close to 0, π/2, π, 3π/2
                        has_rotated_text = True
                        break
        
        if has_rotated_text:
            adaptations.append("This document contains rotated or diagonal text. Be sure to capture text in all orientations.")
        
        # Combine base prompt with adaptations
        if adaptations:
            full_prompt = base_prompt + " " + " ".join(adaptations)
        else:
            full_prompt = base_prompt
            
        return full_prompt
        
    def process_document(self, image_path: str, pdf_path: Optional[str] = None) -> DoclingDocument:
        """
        Process a document image and return a DoclingDocument.
        
        Args:
            image_path: Path to input image.
            pdf_path: Optional path to source PDF for metadata extraction.
        
        Returns:
            DoclingDocument containing structured document data.
        """
        img_array = self.preprocess_image(image_path)
        
        # Run model inference using mlx_vlm utilities
        image = Image.fromarray(img_array)
        image_inputs = mlx_vlm.process_image(image)
        
        # Create an adaptive prompt based on document characteristics
        adaptive_prompt = self._create_adaptive_prompt(image_path, img_array)
        result = mlx_vlm.generate(self.model, self.tokenizer, adaptive_prompt, image_inputs=image_inputs)
        
        # Create a DoclingDocument from the model output
        document = DoclingDocument()
        document.elements = []
        
        # Add a text element with the model's description
        document.elements.append({
            "type": "text",
            "text": result.text,
            "bbox": [0.1, 0.1, 0.9, 0.9],
            "confidence": 0.9
        })
        
        # Apply specialized academic paper processing if enabled
        if self.process_academic:
            academic_results = self.academic_processor.process_academic_paper(image_path, pdf_path)
            document = self.academic_processor.enhance_docling_document(document, academic_results)
        
        return document
    
    def process_file(self, input_file: str, output_dir: str, temp_dir: str) -> Optional[str]:
        """
        Process a single file by converting, enhancing, and running SmolDocling.
        
        Args:
            input_file: Path to input file (any supported format).
            output_dir: Directory to save the processed document.
            temp_dir: Directory for temporary files.
            
        Returns:
            Path to the output JSON file, or None if processing failed.
        """
        try:
            # Step 1: Convert to PDF if needed
            file_format = self.converter.detect_format(input_file)
            pdf_path = None
            
            if file_format == "pdf":
                pdf_path = input_file
            elif file_format in ["image", "office"]:
                pdf_dir = os.path.join(temp_dir, "pdfs")
                os.makedirs(pdf_dir, exist_ok=True)
                
                success, pdf_path = self.converter.convert_to_pdf(
                    input_file, 
                    os.path.join(pdf_dir, f"{Path(input_file).stem}.pdf")
                )
                
                if not success:
                    print(f"Failed to convert {input_file} to PDF")
                    return None
            else:
                print(f"Unsupported file format: {input_file}")
                return None
            
            # Step 2: Extract pages as images
            page_images_dir = os.path.join(temp_dir, "pages")
            os.makedirs(page_images_dir, exist_ok=True)
            
            page_images = self.converter.extract_pdf_pages_as_images(
                pdf_path, page_images_dir, dpi=300
            )
            
            if not page_images:
                print(f"Failed to extract pages from {pdf_path}")
                return None
            
            # Step 3: Enhance page images if needed
            if self.document_type in ["old_scan", "faded"]:
                enhanced_dir = os.path.join(temp_dir, "enhanced")
                os.makedirs(enhanced_dir, exist_ok=True)
                
                # Define parameters to preserve original dimensions
                resize_shape = None  # Pass None to skip resizing and keep original dimensions
                # Define a processor that maintains the original image
                def maintain_original(img):
                    return img  # Return the image without modifications
                image_processor = maintain_original
                
                enhanced_images = self.enhancer.batch_process(
                    page_images, enhanced_dir, self.document_type, resize_shape, image_processor
                )
                
                if enhanced_images:
                    page_images = enhanced_images
            
            # Step 4: Process pages with SmolDocling
            documents = []
            
            if self.parallel and len(page_images) > 1:
                # Process pages in parallel
                with multiprocessing.Pool(self.num_cpus) as pool:
                    # Create processing function for pool
                    def process_page(page_img):
                        try:
                            return self.process_document(page_img, pdf_path)
                        except Exception as e:
                            print(f"Error processing page {page_img}: {str(e)}")
                            return None
                    
                    # Process in parallel
                    documents = list(
                        tqdm(
                            pool.imap(process_page, page_images),
                            total=len(page_images),
                            desc="Processing pages in parallel"
                        )
                    )
                    # Filter out failed documents
                    documents = [doc for doc in documents if doc is not None]
            else:
                # Process pages sequentially
                for page_img in tqdm(page_images, desc="Processing pages"):
                    try:
                        document = self.process_document(page_img, pdf_path)
                        documents.append(document)
                    except Exception as e:
                        print(f"Error processing page {page_img}: {str(e)}")
            
            # Step 5: Combine pages into a single document (simple approach)
            if not documents:
                print(f"No pages processed successfully for {input_file}")
                return None
            
            # Combine documents (simple approach - just merge elements)
            combined_doc = documents[0]
            for doc in documents[1:]:
                combined_doc.elements.extend(doc.elements)
            
            # Add metadata
            combined_doc.metadata["source_file"] = input_file
            combined_doc.metadata["num_pages"] = len(page_images)
            combined_doc.metadata["document_type"] = self.document_type
            
            # Step 6: Save combined document
            os.makedirs(output_dir, exist_ok=True)
            output_path = os.path.join(output_dir, f"{Path(input_file).stem}.json")
            combined_doc.save(output_path)
            
            print(f"Saved processed document to {output_path}")
            return output_path
            
        except Exception as e:
            print(f"Error processing {input_file}: {str(e)}")
            return None
    
    def process_batch(self, input_files: List[str], output_dir: str) -> List[str]:
        """
        Process a batch of document files.
        
        Args:
            input_files: List of paths to input files.
            output_dir: Directory to save processed documents.
        
        Returns:
            List of paths to the processed document JSON files.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # Create temporary directory
        temp_dir = os.path.join(output_dir, "_temp")
        os.makedirs(temp_dir, exist_ok=True)
        
        output_files = []
        
        for input_file in tqdm(input_files, desc="Processing documents"):
            output_path = self.process_file(input_file, output_dir, temp_dir)
            if output_path:
                output_files.append(output_path)
        
        return output_files


def main():
    """Main entry point for document processing script."""
    parser = argparse.ArgumentParser(description="Process documents with SmolDocling")
    parser.add_argument(
        "--input", "-i", 
        required=True,
        help="Input directory containing documents or single document file"
    )
    parser.add_argument(
        "--output", "-o", 
        default="./data/output",
        help="Output directory for processed documents"
    )
    parser.add_argument(
        "--max-size", 
        type=int, 
        default=1024,
        help="Maximum image dimension"
    )
    parser.add_argument(
        "--document-type",
        choices=["general", "old_scan", "faded"],
        default="general",
        help="Document type for preprocessing"
    )
    parser.add_argument(
        "--academic",
        action="store_true",
        help="Apply specialized academic paper processing"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Use parallel processing for multi-page documents"
    )
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = DocumentProcessor(
        max_size=args.max_size,
        document_type=args.document_type,
        process_academic=args.academic,
        parallel=args.parallel
    )
    
    # Process input (file or directory)
    input_path = Path(args.input)
    if input_path.is_file():
        # Single file
        processor.process_batch([str(input_path)], args.output)
    else:
        # Directory - find all supported files
        converter = DocumentConverter()
        supported_extensions = (
            converter.SUPPORTED_OFFICE_FORMATS.union(
                converter.SUPPORTED_IMAGE_FORMATS
            ).union({".pdf"})
        )
        
        files = []
        for ext in supported_extensions:
            files.extend(list(input_path.glob(f"*{ext}")))
        
        if not files:
            print(f"No supported files found in {input_path}")
            return
        
        processor.process_batch([str(path) for path in files], args.output)


if __name__ == "__main__":
    main()