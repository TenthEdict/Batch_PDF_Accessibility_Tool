import cv2
import numpy as np
import os
import pytesseract
from PIL import Image
import time
from typing import Dict
import json

from src.accessibility_checker.ocr.processor import OCRProcessor
from src.accessibility_checker.utils.config import OCRConfig
from src.accessibility_checker.ocr.adaptive_config import AdaptiveOCRConfig, DocumentCharacteristics

def main():
    print("Enhanced Historical Document OCR Processing Test")
    
    # Setup paths
    output_dir = "output/ocr_results"
    
    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)
    
    # Create test document types
    test_documents = {
        "modern": create_modern_document(),
        "historical_faded": create_historical_document(degradation="faded"),
        "historical_yellowed": create_historical_document(degradation="yellowed"),
        "historical_stained": create_historical_document(degradation="stained"),
        "manuscript": create_manuscript_document()
    }
    
    # Save test images
    for doc_type, img in test_documents.items():
        cv2.imwrite(os.path.join(output_dir, f"{doc_type}_original.png"), img)
    
    # Base OCR config
    base_config = OCRConfig(
        language="eng",
        psm=6,
        oem=3,
        char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}'\"-—",
        additional_params={}
    )
    
    # Create adaptive OCR config handler
    adaptive_config_handler = AdaptiveOCRConfig(base_config={})
    
    # Initialize result metrics
    results = {}
    
    # Test each document type
    for doc_type, img in test_documents.items():
        print(f"\n===== Testing {doc_type} document =====")
        
        # Convert to grayscale for document analysis
        if len(img.shape) == 3:
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        else:
            gray = img.copy()
            
        # Convert to PIL for document characteristic analysis
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB) if len(img.shape) == 3 else img)
        
        # Detect if document is historical
        is_historical = adaptive_config_handler._detect_historical_document(pil_img)
        print(f"Detected as historical: {is_historical}")
        
        # Standard processing
        processor_standard = OCRProcessor(config=base_config)
        
        start_time = time.time()
        standard_img = processor_standard.preprocess_image(img)
        standard_text = processor_standard.process_image(img)
        standard_time = time.time() - start_time
        standard_confidence = processor_standard.get_last_confidence()
        
        # Historical processing
        processor_historical = OCRProcessor(config=base_config)
        processor_historical.update_config({"document_mode": "historical"})
        
        start_time = time.time()
        historical_img = processor_historical._preprocess_historical_document(
            cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) if len(img.shape) == 3 else img
        )
        historical_text = processor_historical.process_image(img)
        historical_time = time.time() - start_time
        historical_confidence = processor_historical.get_last_confidence()
        
        # Print results
        print(f"\nStandard OCR Result ({standard_time:.2f}s):")
        print(f"Confidence: {standard_confidence:.2f}%")
        print(f"Text: {standard_text[:100]}..." if len(standard_text) > 100 else standard_text)
        
        print(f"\nHistorical OCR Result ({historical_time:.2f}s):")
        print(f"Confidence: {historical_confidence:.2f}%")
        print(f"Text: {historical_text[:100]}..." if len(historical_text) > 100 else historical_text)
        
        # Calculate improvement
        confidence_improvement = historical_confidence - standard_confidence
        print(f"\nConfidence improvement: {confidence_improvement:.2f}%")
        
        # Save processed images
        cv2.imwrite(os.path.join(output_dir, f"{doc_type}_standard.png"), standard_img)
        cv2.imwrite(os.path.join(output_dir, f"{doc_type}_historical.png"), historical_img)
        
        # Store results
        results[doc_type] = {
            "is_detected_as_historical": bool(is_historical),
            "standard": {
                "confidence": float(standard_confidence),
                "time": float(standard_time),
                "text_sample": standard_text[:200] if standard_text else ""
            },
            "historical": {
                "confidence": float(historical_confidence),
                "time": float(historical_time),
                "text_sample": historical_text[:200] if historical_text else ""
            },
            "improvement": {
                "confidence": float(confidence_improvement)
            }
        }
    
    # Save results to JSON
    with open(os.path.join(output_dir, "ocr_comparison_results.json"), "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\nResults saved to {os.path.join(output_dir, 'ocr_comparison_results.json')}")
    print("All test images saved to", output_dir)
    print("Test completed.")

def create_modern_document():
    """Create a synthetic modern document image for testing"""
    height, width = 1000, 800
    # White background
    bg = np.ones((height, width, 3), dtype=np.uint8) * 255
    
    # Add some text
    img = Image.fromarray(bg)
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        font = ImageFont.truetype("Arial", 24)
    except:
        font = ImageFont.load_default()
    
    text = [
        "This is a modern document with clear text.",
        "It has good contrast and clean background.",
        "The text should be easily recognized by OCR.",
        "There are no degradation issues here.",
        "Lines are evenly spaced and characters are clear."
    ]
    
    y_pos = 100
    for line in text:
        draw.text((50, y_pos), line, fill=(0, 0, 0), font=font)
        y_pos += 50
    
    return np.array(img)

def create_historical_document(degradation="faded"):
    """Create a synthetic historical document with specified degradation"""
    height, width = 1000, 800
    
    if degradation == "yellowed":
        # Yellowish background (simulating aged paper)
        bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, 230, 240], dtype=np.uint8)
        degradation_text = "yellowed paper from the 19th century"
    elif degradation == "stained":
        # Light background with stains
        bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([235, 235, 230], dtype=np.uint8)
        degradation_text = "stained manuscript from 1850"
    else:  # faded
        # Light gray background
        bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([240, 240, 240], dtype=np.uint8)
        degradation_text = "faded text from an 1820 document"
    
    # Add texture and noise
    noise = np.random.randint(0, 15, (height, width, 3), dtype=np.uint8)
    bg = cv2.add(bg, noise)
    
    # Create a canvas to draw text
    canvas = bg.copy()
    
    # Historical-style text content
    historical_text = [
        f"This historical document has {degradation_text}.",
        "Ye olde printing press hath produced this text.",
        "These pages contain accounts from yesteryear.",
        "Many such documents are difficult to transcribe.",
        "The characters herein may prove challenging to discern."
    ]
    
    # Create a mask for text
    text_mask = np.ones((height, width), dtype=np.uint8) * 255
    
    # Add text with a historical-looking font
    font = cv2.FONT_HERSHEY_SCRIPT_COMPLEX
    y_pos = 100
    
    for line in historical_text:
        cv2.putText(text_mask, line, (50, y_pos), font, 0.8, 0, 2)
        y_pos += 70
    
    # Apply degradation effects
    if degradation == "faded":
        # Simulate faded text by reducing contrast
        text_mask = cv2.GaussianBlur(text_mask, (3, 3), 0)
        text_mask = cv2.multiply(text_mask, 1.3)  # Lighten the text
        
        # Apply the mask with reduced opacity
        for c in range(3):
            canvas[:, :, c] = cv2.add(
                cv2.multiply(canvas[:, :, c], text_mask.astype(float) / 255),
                cv2.multiply(np.zeros_like(canvas[:, :, c]), (255 - text_mask).astype(float) / 255)
            ).astype(np.uint8)
            
    elif degradation == "yellowed":
        # For yellowed paper, we add a bit more contrast to text
        text_mask = 255 - text_mask  # Invert so text is white (255)
        
        # Apply the text mask
        for c in range(3):
            canvas[:, :, c] = np.where(text_mask == 255, 
                                      np.minimum(0, canvas[:, :, c] - 170),  # Darker text
                                      canvas[:, :, c])
    
    elif degradation == "stained":
        # For stained paper, add splotches and uneven coloring
        for _ in range(15):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            radius = np.random.randint(10, 50)
            color = np.random.randint(180, 220)
            cv2.circle(canvas, (x, y), radius, (color, color, color), -1)
        
        # Apply text with uneven darkness
        text_mask = 255 - text_mask  # Invert so text is white (255)
        uneven_mask = np.random.randint(150, 220, text_mask.shape, dtype=np.uint8)
        text_mask = np.minimum(text_mask, uneven_mask)
        
        # Apply the uneven text
        for c in range(3):
            canvas[:, :, c] = np.where(text_mask > 200, 
                                      np.maximum(0, canvas[:, :, c] - text_mask // 2),
                                      canvas[:, :, c])
    
    # Add a slight skew (common in historical scans)
    rows, cols = canvas.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 1.5, 1)
    canvas = cv2.warpAffine(canvas, M, (cols, rows), borderMode=cv2.BORDER_REPLICATE)
    
    return canvas

def create_manuscript_document():
    """Create a synthetic handwritten manuscript document"""
    height, width = 1000, 800
    
    # Aged parchment background
    bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([230, 225, 200], dtype=np.uint8)
    
    # Add parchment texture
    texture = np.random.randint(0, 20, (height, width, 3), dtype=np.uint8)
    bg = cv2.add(bg, texture)
    
    # Create canvas
    canvas = bg.copy()
    
    # Add various handwriting-like marks and curves
    for _ in range(40):
        # Generate random curved lines resembling handwriting
        points = []
        x, y = np.random.randint(50, width-100), np.random.randint(100, height-100)
        points.append((x, y))
        
        # Generate a few more points along a line with small variations
        for i in range(5):
            x += np.random.randint(15, 40)
            y += np.random.randint(-10, 10)
            points.append((x, y))
        
        # Draw the curve
        points = np.array(points)
        cv2.polylines(canvas, [points], False, (0, 0, 0), 2)
    
    # Add some "handwritten text" by simulating ink strokes
    # This is very simplified and won't look like real text, just for testing
    y_pos = 100
    for _ in range(5):
        x_pos = 50
        for _ in range(np.random.randint(5, 15)):
            # Simulate a letter
            letter_height = np.random.randint(20, 35)
            letter_width = np.random.randint(10, 25)
            
            # Random pattern for "letter"
            for i in range(np.random.randint(1, 4)):
                start_x = x_pos + np.random.randint(0, 5)
                start_y = y_pos + np.random.randint(0, 5)
                end_x = start_x + np.random.randint(5, letter_width)
                end_y = start_y + np.random.randint(5, letter_height)
                cv2.line(canvas, (start_x, start_y), (end_x, end_y), (0, 0, 0), 2)
            
            x_pos += letter_width + np.random.randint(5, 15)
        
        y_pos += 65 + np.random.randint(0, 20)
    
    # Add some ink blotches and smudges
    for _ in range(10):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        size = np.random.randint(5, 20)
        cv2.circle(canvas, (x, y), size, (0, 0, 0), -1)
        
        # Add smudge
        smudge_dir_x = np.random.randint(-15, 15)
        smudge_dir_y = np.random.randint(-15, 15)
        for i in range(5):
            alpha = 0.7 - (i * 0.15)
            if alpha <= 0:
                break
            cv2.circle(
                canvas, 
                (x + smudge_dir_x * i, y + smudge_dir_y * i), 
                max(2, size - i * 3), 
                (0, 0, 0),
                -1
            )
    
    # Add a slight skew
    rows, cols = canvas.shape[:2]
    M = cv2.getRotationMatrix2D((cols/2, rows/2), 1.0, 1)
    canvas = cv2.warpAffine(canvas, M, (cols, rows), borderMode=cv2.BORDER_REPLICATE)
    
    return canvas

if __name__ == "__main__":
    main()