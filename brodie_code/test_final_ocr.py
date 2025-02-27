import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import tempfile

def main():
    print("Testing Historical Document OCR Processing")
    
    # Create output directory
    os.makedirs("output/ocr_results", exist_ok=True)
    
    # Create a synthetic test image
    img = create_test_image()
    
    # Process with standard OCR
    print("Processing with standard OCR...")
    standard_text = pytesseract.image_to_string(img)
    print(f"Standard OCR Result: {standard_text.strip()}")
    
    # Try basic binarization without our custom preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    cv2.imwrite("output/ocr_results/standard_binary.png", binary)
    standard_binary_text = pytesseract.image_to_string(binary)
    print(f"Standard Binary OCR Result: {standard_binary_text.strip()}")
    
    # Process with our custom preprocessing - fixed version
    print("\nProcessing with historical document preprocessing...")
    processed = preprocess_historical_fixed(img)
    
    # Save processed image
    cv2.imwrite("output/ocr_results/processed_historical_fixed.png", processed)
    
    # Run OCR on processed image
    historical_text = pytesseract.image_to_string(processed)
    print(f"Historical OCR Result: {historical_text.strip()}")
    
    print(f"\nProcessed images saved to output/ocr_results/")
    print("Test completed.")

def create_test_image():
    """Create a synthetic historical document image for testing"""
    # Create a yellowish background (simulating aged paper)
    height, width = 800, 600
    yellow_bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, 230, 240], dtype=np.uint8)
    
    # Add some noise and texture
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    yellow_bg = cv2.add(yellow_bg, noise)
    
    # Convert to PIL for better text rendering
    pil_img = Image.fromarray(cv2.cvtColor(yellow_bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Attempt to use a font
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Add faded text (use lighter color for fading effect)
    text = "This is a historical document from 1896."
    draw.text((50, 300), text, fill=(120, 120, 120), font=font)
    
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
    cv2.imwrite("output/ocr_results/synthetic_historical.png", canvas)
    
    return canvas

def preprocess_historical_fixed(image):
    """
    Apply historical document preprocessing - fixed version
    """
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 1. Enhance contrast to bring out faded text
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 2. Invert colors - we want text to be black on white background
    # This fixes the text inversion problem
    inverted = cv2.bitwise_not(enhanced)
    
    # 3. Apply Otsu thresholding 
    _, binary = cv2.threshold(inverted, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    
    # 4. Apply denoising
    denoised = cv2.fastNlMeansDenoising(binary, h=10)
    
    # 5. Sharpen to improve character definition
    kernel = np.array([[-1, -1, -1], 
                       [-1, 9, -1], 
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # 6. Correct skew if needed
    coords = np.column_stack(np.where(sharpened > 0))
    if len(coords) > 0:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        
        # Rotate if skewed
        if abs(angle) > 0.5:
            h, w = sharpened.shape
            center = w // 2, h // 2
            M = cv2.getRotationMatrix2D(center, angle, 1.0)
            processed = cv2.warpAffine(sharpened, M, (w, h), 
                                    flags=cv2.INTER_CUBIC,
                                    borderMode=cv2.BORDER_REPLICATE)
        else:
            processed = sharpened
    else:
        processed = sharpened
    
    # 7. Apply a second round of adaptive thresholding for better text separation
    final = cv2.adaptiveThreshold(
        processed, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 11, 2
    )
    
    return final

if __name__ == "__main__":
    main()