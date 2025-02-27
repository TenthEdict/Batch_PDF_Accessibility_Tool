import cv2
import numpy as np
import os
import pytesseract
from PIL import Image, ImageDraw, ImageFont
import tempfile

def main():
    print("Testing Historical Document OCR Processing")
    
    # Create a synthetic test image
    img = create_test_image()
    
    # Save the image to a temporary file
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
        tmp_path = tmp.name
        cv2.imwrite(tmp_path, img)
    
    # Process with standard OCR
    print("Processing with standard OCR...")
    text = pytesseract.image_to_string(img)
    print(f"OCR Result: {text.strip()}")
    
    # Process with our custom preprocessing
    print("\nProcessing with historical document preprocessing...")
    processed = preprocess_historical(img)
    
    # Save processed image
    processed_path = "output/ocr_results/processed_historical.png"
    os.makedirs(os.path.dirname(processed_path), exist_ok=True)
    cv2.imwrite(processed_path, processed)
    
    # Run OCR on processed image
    text = pytesseract.image_to_string(processed)
    print(f"OCR Result: {text.strip()}")
    
    print(f"\nProcessed image saved to {processed_path}")
    print("Test completed.")
    
    # Clean up temporary file
    os.unlink(tmp_path)

def create_test_image():
    """Create a synthetic historical document image for testing"""
    # Create a yellowish background (simulating aged paper)
    height, width = 800, 600
    yellow_bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, 230, 240], dtype=np.uint8)
    
    # Add some noise and texture
    noise = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    yellow_bg = cv2.add(yellow_bg, noise)
    
    # Create a canvas to draw text
    canvas = yellow_bg.copy()
    
    # Convert to PIL for better text rendering
    pil_img = Image.fromarray(cv2.cvtColor(canvas, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Attempt to use a font
    try:
        font = ImageFont.truetype("Arial", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Add text
    text = "This is a historical document from 1896."
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
    cv2.imwrite("output/ocr_results/synthetic_historical.png", canvas)
    
    return canvas

def preprocess_historical(image):
    """
    Apply historical document preprocessing
    """
    # Convert to grayscale if not already
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # 1. Enhance contrast to bring out faded text
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    # 2. Normalize to remove yellowing/stains
    _, threshold = cv2.threshold(
        enhanced, 0, 255, 
        cv2.THRESH_BINARY + cv2.THRESH_OTSU
    )
    
    # 3. Apply denoising
    denoised = cv2.fastNlMeansDenoising(threshold, h=13)
    
    # 4. Sharpen to improve character definition
    kernel = np.array([[-1, -1, -1], 
                       [-1, 9, -1], 
                       [-1, -1, -1]])
    sharpened = cv2.filter2D(denoised, -1, kernel)
    
    # 5. Correct skew 
    # Calculate skew angle
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
    
    # 6. Apply adaptive binarization
    final = cv2.adaptiveThreshold(
        processed, 255, 
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
        cv2.THRESH_BINARY, 9, 2
    )
    
    return final

if __name__ == "__main__":
    main()