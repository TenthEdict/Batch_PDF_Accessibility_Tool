#!/usr/bin/env python3
"""
Document enhancement module for SmolDocling.
Provides image preprocessing functions for improving scanned document quality.
"""

import os
import cv2
import numpy as np
from typing import Optional, Tuple, List
from pathlib import Path
from skimage import restoration, filters, exposure, morphology, transform


class DocumentEnhancer:
    """Document image enhancer for scanned documents."""
    
    def __init__(self):
        """Initialize the document enhancer."""
        pass
    
    def load_image(self, image_path: str) -> np.ndarray:
        """
        Load an image from file.
        
        Args:
            image_path: Path to the image file.
            
        Returns:
            Image as numpy array.
        """
        # Load with OpenCV (BGR format)
        img = cv2.imread(image_path)
        if img is None:
            raise ValueError(f"Failed to load image: {image_path}")
        return img
    
    def save_image(self, img: np.ndarray, output_path: str) -> None:
        """
        Save image to file.
        
        Args:
            img: Image as numpy array.
            output_path: Path to save the image.
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        cv2.imwrite(output_path, img)
    
    def detect_skew(self, img: np.ndarray) -> float:
        """
        Detect skew angle of a document image.
        
        Args:
            img: Document image.
            
        Returns:
            Skew angle in degrees.
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Apply threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Apply morphological operations to enhance text lines
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (30, 1))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Find contours and calculate their angles
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        angles = []
        for contour in contours:
            # Filter out very small contours
            if cv2.contourArea(contour) < 100:
                continue
                
            # Get minimum area rectangle
            rect = cv2.minAreaRect(contour)
            width, height = rect[1]
            angle = rect[2]
            
            # Adjust angle (OpenCV returns angles in the range [-90, 0])
            if width < height:
                angle = angle - 90
            
            angles.append(angle)
        
        # Return the median angle if angles were found, otherwise 0
        if angles:
            return np.median(angles)
        return 0.0
    
    def deskew(self, img: np.ndarray, angle: Optional[float] = None) -> np.ndarray:
        """
        Correct skew in a document image.
        
        Args:
            img: Document image.
            angle: Known skew angle. If None, it will be detected automatically.
            
        Returns:
            Deskewed image.
        """
        # Detect angle if not provided
        if angle is None:
            angle = self.detect_skew(img)
        
        # No need to deskew if angle is close to 0
        if abs(angle) < 0.5:
            return img
        
        # Get image center
        height, width = img.shape[:2]
        center = (width // 2, height // 2)
        
        # Get rotation matrix
        matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        
        # Apply rotation
        rotated = cv2.warpAffine(
            img, matrix, (width, height),
            flags=cv2.INTER_CUBIC,
            borderMode=cv2.BORDER_CONSTANT,
            borderValue=(255, 255, 255)
        )
        
        return rotated
    
    def remove_noise(self, img: np.ndarray, method: str = "gaussian") -> np.ndarray:
        """
        Remove noise from document image.
        
        Args:
            img: Document image.
            method: Noise reduction method ('gaussian', 'bilateral', 'nlm').
            
        Returns:
            Denoised image.
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        if method == "gaussian":
            # Simple Gaussian blur
            denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        elif method == "bilateral":
            # Bilateral filter (preserves edges better)
            denoised = cv2.bilateralFilter(gray, 9, 75, 75)
        elif method == "nlm":
            # Non-local means denoising (better for document images)
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
        else:
            raise ValueError(f"Unknown noise reduction method: {method}")
        
        # Return color image if input was color
        if len(img.shape) == 3:
            denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2BGR)
        
        return denoised
    
    def enhance_contrast(self, img: np.ndarray, method: str = "adaptive", auto_select: bool = True) -> np.ndarray:
        """
        Enhance contrast in a document image with adaptive method selection.
        
        Args:
            img: Document image.
            method: Contrast enhancement method ('clahe', 'adaptive', 'normalize').
            auto_select: Whether to automatically select the best method based on image characteristics.
            
        Returns:
            Contrast-enhanced image.
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Automatically select method based on image characteristics if requested
        if auto_select:
            # Analyze image histogram
            hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
            hist = hist.flatten() / (gray.shape[0] * gray.shape[1])  # Normalize
            
            # Calculate histogram spread and peaks
            non_zero_indices = np.where(hist > 0.001)[0]  # Significant bins
            if len(non_zero_indices) > 0:
                hist_spread = non_zero_indices[-1] - non_zero_indices[0]
            else:
                hist_spread = 0
                
            # Check if image is low contrast
            std_dev = np.std(gray)
            
            if std_dev < 40 or hist_spread < 100:  # Low contrast
                method = "clahe"  # Best for recovering details in low contrast
            elif np.mean(gray) < 100:  # Dark image
                method = "adaptive"  # Good for enhancing dark regions
            elif len(non_zero_indices) < 50:  # Limited color range
                method = "normalize"  # Expands the color range
            # else: use the provided method
        
        # Apply selected method
        if method == "clahe":
            # CLAHE (Contrast Limited Adaptive Histogram Equalization)
            # Adjust clip limit based on image contrast
            std_dev = np.std(gray)
            clip_limit = 3.0 if std_dev < 50 else 2.0  # More aggressive for lower contrast
            
            clahe = cv2.createCLAHE(clipLimit=clip_limit, tileGridSize=(8, 8))
            enhanced = clahe.apply(gray)
            
            # For extremely low contrast, apply twice with different parameters
            if std_dev < 30:
                clahe2 = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(16, 16))
                enhanced = clahe2.apply(enhanced)
                
        elif method == "adaptive":
            # Adaptive histogram equalization using scikit-image
            # Adjust clip limit based on image characteristics
            clip_limit = 0.01 if np.mean(gray) > 200 else 0.03
            enhanced = (exposure.equalize_adapthist(gray, clip_limit=clip_limit) * 255).astype(np.uint8)
            
        elif method == "normalize":
            # Simple normalization with potential pre-processing
            if np.std(gray) < 40:  # Very low contrast
                # Apply gamma correction before normalization
                gamma = 1.5  # Adjust gamma for better contrast
                gray = np.power(gray / 255.0, gamma) * 255.0
                gray = gray.astype(np.uint8)
            
            enhanced = cv2.normalize(gray, None, 0, 255, cv2.NORM_MINMAX)
            
        else:
            raise ValueError(f"Unknown contrast enhancement method: {method}")
        
        # Return color image if input was color
        if len(img.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)
        
        return enhanced
    
    def binarize(self, img: np.ndarray, method: str = "adaptive") -> np.ndarray:
        """
        Binarize document image (convert to black and white).
        
        Args:
            img: Document image.
            method: Binarization method ('otsu', 'adaptive', 'sauvola').
            
        Returns:
            Binarized image.
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        if method == "otsu":
            # Otsu's thresholding
            _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == "adaptive":
            # Adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                cv2.THRESH_BINARY, 11, 7
            )
        elif method == "sauvola":
            # Sauvola thresholding (good for degraded documents)
            binary = (filters.threshold_sauvola(gray, window_size=25) * 255).astype(np.uint8)
            binary = 255 - binary  # Invert to get black text on white background
        else:
            raise ValueError(f"Unknown binarization method: {method}")
        
        # Return color image if input was color
        if len(img.shape) == 3:
            binary = cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)
        
        return binary
    
    def remove_borders(self, img: np.ndarray) -> np.ndarray:
        """
        Remove black borders from scanned document.
        
        Args:
            img: Document image.
            
        Returns:
            Image with borders removed.
        """
        # Convert to grayscale if needed
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
        
        # Threshold to get binary image
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        
        # Find contours of the page
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Skip cropping if no significant contours found or if the largest contour is too small
        if not contours or cv2.contourArea(max(contours, key=cv2.contourArea)) < 0.1 * gray.shape[0] * gray.shape[1]:
            return img
            
        # Find largest contour (presumably the page)
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(largest_contour)
        
        # Only crop if the bounding rectangle is significantly smaller than the image
        if w < 0.8 * gray.shape[1] or h < 0.8 * gray.shape[0]:
            # Add small margin
            margin = 5
            x = max(0, x - margin)
            y = max(0, y - margin)
            w = min(gray.shape[1] - x, w + 2 * margin)
            h = min(gray.shape[0] - y, h + 2 * margin)
            
            # Crop image
            cropped = img[y:y+h, x:x+w]
            return cropped
        
        return img
    
    def detect_layout(self, img: np.ndarray) -> str:
        """
        Detect document layout (single column, double column, etc.).
        
        Args:
            img: Document image.
            
        Returns:
            Layout type ("single_column", "double_column").
        """
        # This is a simple heuristic approach - in a real application,
        # you might want a more sophisticated layout analysis
        
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
    
    def process_image(self, image_path: str, output_path: str, 
                     document_type: str = "general", resize_shape=None, image_processor=None) -> None:
        """
        Process a document image with appropriate enhancements.
        
        Args:
            image_path: Path to the input image.
            output_path: Path to save the enhanced image.
            document_type: Type of document ('general', 'old_scan', 'faded').
            resize_shape: Optional shape to resize the image to (defaults to None).
            image_processor: Optional additional image processor function (defaults to None).
        """
        # Load image
        img = self.load_image(image_path)
        
        # Apply different processing based on document type
        if document_type == "old_scan":
            # For old scanned documents - more aggressive processing
            img = self.deskew(img)
            # Skip border removal for this specific document type
            # img = self.remove_borders(img)
            img = self.remove_noise(img, method="nlm")
            img = self.enhance_contrast(img, method="clahe")
            
        elif document_type == "faded":
            # For faded documents - focus on contrast enhancement
            img = self.deskew(img)
            img = self.enhance_contrast(img, method="clahe")
            img = self.binarize(img, method="sauvola")
            
        else:  # general case
            # For general documents - basic enhancement
            img = self.deskew(img)
            img = self.remove_noise(img, method="gaussian")
            img = self.enhance_contrast(img, method="adaptive")
        
        # Apply resize if shape provided
        if resize_shape is not None:
            img = cv2.resize(img, resize_shape)
            
        # Apply additional processing if provided
        if image_processor is not None:
            img = image_processor(img)
        
        # Save processed image
        self.save_image(img, output_path)
    
    def batch_process(self, input_files: List[str], output_dir: str, 
                     document_type: str = "general", resize_shape=None, image_processor=None) -> List[str]:
        """
        Process multiple document images.
        
        Args:
            input_files: List of paths to input images.
            output_dir: Directory to save the enhanced images.
            document_type: Type of document ('general', 'old_scan', 'faded').
            resize_shape: Optional shape to resize the images to (defaults to None).
            image_processor: Optional additional image processor function (defaults to None).
            
        Returns:
            List of paths to the enhanced images.
        """
        os.makedirs(output_dir, exist_ok=True)
        output_files = []
        
        for input_file in input_files:
            # Determine output path
            filename = os.path.basename(input_file)
            output_path = os.path.join(output_dir, f"enhanced_{filename}")
            
            try:
                # Process image
                self.process_image(input_file, output_path, document_type, resize_shape, image_processor)
                output_files.append(output_path)
                print(f"Processed: {input_file} -> {output_path}")
            except Exception as e:
                print(f"Error processing {input_file}: {str(e)}")
        
        return output_files


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Enhance document images")
    parser.add_argument("--input", "-i", required=True, help="Input file or directory")
    parser.add_argument("--output", "-o", default="./data/output", help="Output directory")
    parser.add_argument(
        "--type", "-t", 
        choices=["general", "old_scan", "faded"],
        default="general",
        help="Document type"
    )
    
    args = parser.parse_args()
    
    enhancer = DocumentEnhancer()
    
    # Process input (file or directory)
    input_path = Path(args.input)
    if input_path.is_file():
        # Single file
        resize_shape = None
        def maintain_original(img):
            return img
        enhancer.batch_process([str(input_path)], args.output, args.type, resize_shape, maintain_original)
    else:
        # Directory
        image_files = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.tiff", "*.tif"]:
            image_files.extend(list(input_path.glob(ext)))
        
        if not image_files:
            print(f"No image files found in {input_path}")
        else:
            resize_shape = None
            def maintain_original(img):
                return img
            enhancer.batch_process([str(path) for path in image_files], args.output, args.type, resize_shape, maintain_original)