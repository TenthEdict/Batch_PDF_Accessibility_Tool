"""
Simple Historical OCR Test

Tests our historical document OCR enhancements with direct pytesseract calls.
"""

import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import tempfile
import re
from difflib import SequenceMatcher
from pathlib import Path

def create_historical_image(text, height=800, width=1200, period="19th_century"):
    """Create a synthetic historical document image with the given text"""
    # Create a yellowish background (simulating aged paper)
    yellow_bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, 230, 240], dtype=np.uint8)
    
    # Add noise and texture
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    yellow_bg = cv2.add(yellow_bg, noise)
    
    # Convert to PIL for better text rendering
    pil_img = Image.fromarray(cv2.cvtColor(yellow_bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Try to use a font
    try:
        font = ImageFont.truetype("Times New Roman", 36)
    except IOError:
        try:
            font = ImageFont.truetype("Georgia", 36)
        except IOError:
            font = ImageFont.load_default()
    
    # Add text
    draw.text((50, 300), text, fill=(50, 50, 50), font=font)
    
    # Convert back to OpenCV format
    canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Apply a slight blur to simulate fading
    canvas = cv2.GaussianBlur(canvas, (3, 3), 0.5)
    
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
    os.makedirs("output/ocr_results", exist_ok=True)
    image_path = f"output/ocr_results/historical_test.png"
    cv2.imwrite(image_path, canvas)
    
    return canvas, image_path

def process_with_historical_enhancements(image):
    """Apply our historical document preprocessing and then run OCR"""
    # Convert to grayscale
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 1. Enhance contrast for faded text
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 2. Invert colors before thresholding for better text detection
    inverted = cv2.bitwise_not(enhanced)
    
    # 3. Apply Otsu thresholding
    _, binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. Apply denoising
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    
    # 5. Apply sharpening
    kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # Save the processed image
    cv2.imwrite("output/ocr_results/processed_historical.png", sharpened)
    
    # Run OCR with historical-optimized settings - simplified for compatibility
    config = (
        "--psm 6 "
        "--oem 3 "  # Use default engine instead of legacy
    )
    
    return pytesseract.image_to_string(sharpened, lang="eng", config=config)

def main():
    print("Testing Historical Document OCR Processing")
    
    # Create output directory
    os.makedirs("output/ocr_results", exist_ok=True)
    
    # Sample historical texts
    historical_text = "Ye Olde Chronicles record that in ye year of our Lord seventeen hundred and ninety-ſix, there appeared a moſt ſingular phenomenon."
    
    # Create a historical document image
    image, image_path = create_historical_image(historical_text)
    
    # Process with standard OCR
    print("\nProcessing with standard OCR...")
    standard_config = "--psm 6"
    standard_text = pytesseract.image_to_string(image, lang="eng", config=standard_config)
    print(f"Standard OCR Result: {standard_text.strip()}")
    
    # Process with historical enhancements
    print("\nProcessing with historical document enhancements...")
    historical_text_result = process_with_historical_enhancements(image)
    print(f"Historical OCR Result: {historical_text_result.strip()}")
    
    print(f"\nProcessed images saved to output/ocr_results/")
    print("Test completed.")

if __name__ == "__main__":
    main()