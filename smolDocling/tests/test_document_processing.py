#!/usr/bin/env python3
"""
Test suite for SmolDocling document processing.
"""

import os
import unittest
from pathlib import Path
import tempfile
import shutil

import numpy as np
from PIL import Image

# Add parent directory to path
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.document_converter import DocumentConverter
from src.document_enhancer import DocumentEnhancer
from src.academic_processor import AcademicPaperProcessor


class TestDocumentConverter(unittest.TestCase):
    """Test the document converter module."""
    
    def setUp(self):
        """Set up test case."""
        self.converter = DocumentConverter()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after test case."""
        shutil.rmtree(self.temp_dir)
    
    def test_detect_format(self):
        """Test format detection."""
        self.assertEqual(self.converter.detect_format("test.pdf"), "pdf")
        self.assertEqual(self.converter.detect_format("test.docx"), "office")
        self.assertEqual(self.converter.detect_format("test.jpg"), "image")
        self.assertEqual(self.converter.detect_format("test.zip"), "unknown")
    
    def test_convert_image_to_pdf(self):
        """Test image to PDF conversion."""
        # Create a test image
        img_path = os.path.join(self.temp_dir, "test.jpg")
        img = Image.new("RGB", (100, 100), color=(255, 0, 0))
        img.save(img_path)
        
        # Convert to PDF
        pdf_path = os.path.join(self.temp_dir, "test.pdf")
        result = self.converter.convert_image_to_pdf(img_path, pdf_path)
        
        self.assertTrue(result)
        self.assertTrue(os.path.exists(pdf_path))


class TestDocumentEnhancer(unittest.TestCase):
    """Test the document enhancer module."""
    
    def setUp(self):
        """Set up test case."""
        self.enhancer = DocumentEnhancer()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after test case."""
        shutil.rmtree(self.temp_dir)
    
    def test_deskew(self):
        """Test image deskewing."""
        # Create a blank image
        img = np.ones((200, 200, 3), dtype=np.uint8) * 255
        
        # Draw a rotated rectangle (simulating skewed text)
        center = (100, 100)
        width, height = 100, 50
        angle = 15  # degrees
        rect = ((center[0], center[1]), (width, height), angle)
        box = np.int0(cv2.boxPoints(rect))
        cv2.drawContours(img, [box], 0, (0, 0, 0), -1)
        
        # Save skewed image
        skewed_path = os.path.join(self.temp_dir, "skewed.jpg")
        cv2.imwrite(skewed_path, img)
        
        # Load and deskew
        skewed_img = self.enhancer.load_image(skewed_path)
        angle = self.enhancer.detect_skew(skewed_img)
        
        # Check that we detected an angle close to 15 degrees
        self.assertAlmostEqual(abs(angle), 15.0, delta=5.0)
        
        # Deskew the image
        deskewed = self.enhancer.deskew(skewed_img, angle)
        
        # Save deskewed image
        deskewed_path = os.path.join(self.temp_dir, "deskewed.jpg")
        self.enhancer.save_image(deskewed, deskewed_path)
        
        # The deskewed image should exist
        self.assertTrue(os.path.exists(deskewed_path))
        
        # After deskewing, detected angle should be close to 0
        new_angle = self.enhancer.detect_skew(deskewed)
        self.assertAlmostEqual(abs(new_angle), 0.0, delta=5.0)


class TestAcademicProcessor(unittest.TestCase):
    """Test the academic processor module."""
    
    def setUp(self):
        """Set up test case."""
        self.processor = AcademicPaperProcessor()
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after test case."""
        shutil.rmtree(self.temp_dir)
    
    def test_detect_layout(self):
        """Test layout detection."""
        # Create a single-column image (just one text block)
        single_col = np.ones((500, 400, 3), dtype=np.uint8) * 255
        text_area = np.zeros((300, 300), dtype=np.uint8)
        single_col[100:400, 50:350, :] = 0  # Black text area in the middle
        
        # Save single-column image
        single_col_path = os.path.join(self.temp_dir, "single_col.jpg")
        cv2.imwrite(single_col_path, single_col)
        
        # Create a double-column image (two text blocks side by side)
        double_col = np.ones((500, 400, 3), dtype=np.uint8) * 255
        double_col[100:400, 50:150, :] = 0  # Left column
        double_col[100:400, 250:350, :] = 0  # Right column
        
        # Save double-column image
        double_col_path = os.path.join(self.temp_dir, "double_col.jpg")
        cv2.imwrite(double_col_path, double_col)
        
        # Test layout detection
        single_col_img = cv2.imread(single_col_path)
        single_layout = self.processor.detect_layout(single_col_img)
        self.assertEqual(single_layout, "single_column")
        
        double_col_img = cv2.imread(double_col_path)
        double_layout = self.processor.detect_layout(double_col_img)
        self.assertEqual(double_layout, "double_column")


if __name__ == "__main__":
    # Import OpenCV only if running tests
    try:
        import cv2
    except ImportError:
        print("OpenCV not installed. Skipping image processing tests.")
        sys.exit(0)
    
    unittest.main()