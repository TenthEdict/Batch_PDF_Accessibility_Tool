import cv2
import numpy as np
import os
import pytesseract
from PIL import Image

from src.accessibility_checker.ocr.processor import OCRProcessor
from src.accessibility_checker.utils.config import OCRConfig

def main():
    print("Testing Historical Document OCR Processing")
    
    # Setup paths
    input_file = "input/Henry Arthur Mosler (1963) - Pacer.pdf"
    output_dir = "output/ocr_results"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a basic OCR config
    ocr_config = OCRConfig(
        language="eng",
        psm=6,
        oem=3,
        char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}'\"-",
        additional_params={}
    )
    
    # Create OCR processor
    processor = OCRProcessor(config=ocr_config)
    
    # Test with a sample image - let's use a sample page from the PDF
    # For testing, we'll create a synthetic "historical" document image
    test_image = create_test_historical_image()
    
    print("Processing with standard OCR...")
    standard_text = processor.process_image(test_image)
    print(f"Standard OCR Result:\n{standard_text}\n")
    print(f"Confidence: {processor.get_last_confidence():.2f}%")
    
    # Enable historical mode
    processor.update_config({"document_mode": "historical"})
    
    print("\nProcessing with historical document mode...")
    historical_text = processor.process_image(test_image)
    print(f"Historical OCR Result:\n{historical_text}\n")
    print(f"Confidence: {processor.get_last_confidence():.2f}%")
    
    # Save processed images for comparison
    standard_img = processor.preprocess_image(test_image)
    cv2.imwrite(os.path.join(output_dir, "standard_processed.png"), standard_img)
    
    # Set to historical mode again (since preprocess_image might have reset it)
    processor.update_config({"document_mode": "historical"})
    historical_img = processor._preprocess_historical_document(cv2.cvtColor(test_image, cv2.COLOR_BGR2GRAY))
    cv2.imwrite(os.path.join(output_dir, "historical_processed.png"), historical_img)
    
    print(f"\nProcessed images saved to {output_dir}")
    print("Test completed.")

def create_test_historical_image():
    """Create a synthetic historical document image for testing"""
    # Create a yellowish background (simulating aged paper)
    height, width = 800, 600
    yellow_bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, 230, 240], dtype=np.uint8)
    
    # Add some noise and texture
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    yellow_bg = cv2.add(yellow_bg, noise)
    
    # Create a canvas to draw text
    canvas = yellow_bg.copy()
    
    # Add some text
    text = "This is a historical document from 1896."
    font = cv2.FONT_HERSHEY_SIMPLEX
    
    # Apply a slight blur to the text to simulate fading
    text_mask = np.zeros((height, width), dtype=np.uint8)
    cv2.putText(text_mask, text, (50, 300), font, 1, 255, 2)
    
    # Blur the text mask
    text_mask = cv2.GaussianBlur(text_mask, (3, 3), 1)
    
    # Invert the mask and reduce opacity (simulate fading)
    text_mask = 255 - text_mask
    text_mask = text_mask.astype(np.float32) * 0.7
    text_mask = text_mask.astype(np.uint8)
    
    # Apply the blurred text mask to all channels
    for c in range(3):
        canvas[:, :, c] = cv2.bitwise_and(canvas[:, :, c], text_mask)
    
    # Add some stains and spots
    for _ in range(10):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(5, 30)
        color = np.random.randint(180, 220)
        cv2.circle(canvas, (x, y), radius, (color, color, color), -1)
    
    # Add a slight skew
    rows, cols = canvas.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 1.5, 1)
    canvas = cv2.warpAffine(canvas, M, (cols, rows))
    
    # Save the synthetic image
    cv2.imwrite("output/ocr_results/synthetic_historical.png", canvas)
    
    return canvas

if __name__ == "__main__":
    main()