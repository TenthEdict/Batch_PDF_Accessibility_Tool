"""
Historical OCR Accuracy Test

This script tests the accuracy of our historical OCR implementation
by comparing it with standard OCR on historical document samples.
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

from src.accessibility_checker.ocr.processor import OCRProcessor
from src.accessibility_checker.utils.config import OCRConfig

# Sample historical texts with known transcriptions
HISTORICAL_SAMPLES = [
    {
        "text": "Ye Olde Chronicles doth record that in ye year of our Lord seventeen hundred and ninety-six, there appeared a most singular phenomenon in ye heavens.",
        "period": "pre_1800", 
        "features": ["archaic_spelling", "long_s"]
    },
    {
        "text": "The æther, that subtil fluid, hath properties not yet fully comprehended by natural philosophers, though many treatises have been published on ye subject.",
        "period": "pre_1800",
        "features": ["ligature", "archaic_spelling"]
    },
    {
        "text": "The railway carriages of the Metropolitan line conveyed paſſengers with great rapidity, though the ſmoke and vapour were moſt diſagreeable to sensitive conſtitutions.",
        "period": "19th_century",
        "features": ["long_s", "period_terminology"]
    },
    {
        "text": "The æroplane, that marvel of modern engineering, achieved a top ſpeed of ſixty miles per hour during its demonstration at the Grand Exhibition.",
        "period": "early_20th_century",
        "features": ["period_terminology", "long_s", "ligature"]
    }
]

def create_historical_image(text, period="19th_century", features=None, height=800, width=1200):
    """Create a synthetic historical document image with the given text"""
    # Create a yellowed background (simulating aged paper)
    yellow_level = {
        "pre_1800": 230,
        "19th_century": 220,
        "early_20th_century": 215
    }.get(period, 220)
    
    yellow_bg = np.ones((height, width, 3), dtype=np.uint8) * np.array([210, yellow_level, 240], dtype=np.uint8)
    
    # Add noise texture that varies by period
    noise_level = {
        "pre_1800": 25,
        "19th_century": 20,
        "early_20th_century": 15
    }.get(period, 20)
    
    noise = np.random.randint(0, noise_level, (height, width, 3), dtype=np.uint8)
    yellow_bg = cv2.add(yellow_bg, noise)
    
    # Convert to PIL for text rendering
    pil_img = Image.fromarray(cv2.cvtColor(yellow_bg, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(pil_img)
    
    # Try to use a font that resembles historical typography
    try:
        if "pre_1800" in period:
            font = ImageFont.truetype("Times New Roman", 36)
        elif "19th_century" in period:
            font = ImageFont.truetype("Georgia", 36)
        else:
            font = ImageFont.truetype("Courier New", 36)
    except IOError:
        font = ImageFont.load_default()
    
    # Text color depends on period and features
    text_color = (60, 60, 60)  # default dark gray
    
    # Adjust text position and wrap text
    x_pos = 100
    y_pos = 300
    
    # Add text with period-appropriate degradation
    draw.text((x_pos, y_pos), text, fill=text_color, font=font)
    
    # Convert back to OpenCV format
    canvas = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    
    # Apply period-specific degradation
    if "pre_1800" in period or "faded" in features:
        # Strong fading for pre-1800
        canvas = cv2.convertScaleAbs(canvas, alpha=0.85, beta=30)
    elif "19th_century" in period:
        # Moderate fading for 19th century
        canvas = cv2.convertScaleAbs(canvas, alpha=0.9, beta=20)
    else:
        # Mild fading for early 20th century
        canvas = cv2.convertScaleAbs(canvas, alpha=0.95, beta=10)
    
    # Apply a blur to simulate aging/fading
    canvas = cv2.GaussianBlur(canvas, (3, 3), 0.8)
    
    # Add stains based on period
    stain_count = {
        "pre_1800": 15,
        "19th_century": 10,
        "early_20th_century": 5
    }.get(period, 10)
    
    for _ in range(stain_count):
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        radius = np.random.randint(5, 30)
        color = np.random.randint(180, 220)
        cv2.circle(canvas, (x, y), radius, (color, color, color), -1)
    
    # Add a slight skew
    rows, cols = canvas.shape[:2]
    skew_angle = np.random.uniform(0.5, 2.5)
    M = cv2.getRotationMatrix2D((cols/2, rows/2), skew_angle, 1)
    canvas = cv2.warpAffine(canvas, M, (cols, rows))
    
    # Save the synthetic image
    os.makedirs("output/ocr_results", exist_ok=True)
    image_path = f"output/ocr_results/historical_{period}.png"
    cv2.imwrite(image_path, canvas)
    
    return canvas, image_path

def calculate_accuracy(ground_truth, ocr_result):
    """Calculate word-level accuracy between ground truth and OCR result"""
    # Normalize text for comparison
    def normalize(text):
        text = text.lower()
        text = re.sub(r'[^\w\s]', '', text)
        return text.strip()
    
    norm_truth = normalize(ground_truth)
    norm_ocr = normalize(ocr_result)
    
    # Calculate word accuracy
    truth_words = set(norm_truth.split())
    ocr_words = set(norm_ocr.split())
    
    if not truth_words:
        return 0.0
    
    # Words correctly recognized
    correct_words = truth_words.intersection(ocr_words)
    word_accuracy = len(correct_words) / len(truth_words)
    
    # Calculate string similarity as a second metric
    string_similarity = SequenceMatcher(None, norm_truth, norm_ocr).ratio()
    
    return (word_accuracy + string_similarity) / 2

def test_ocr_accuracy():
    """Test standard vs. historical OCR accuracy on sample texts"""
    print("\n=== Historical OCR Accuracy Test ===\n")
    
    # Create output directory
    os.makedirs("output/ocr_results", exist_ok=True)
    
    # Set up OCR processors
    standard_config = OCRConfig(
        language="eng",
        psm=6,
        oem=3,
        char_whitelist="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,;:()[]{}'\"-",
        additional_params={}
    )
    
    # Create Standard OCR processor
    standard_processor = OCRProcessor(config=standard_config)
    
    # Create Historical OCR processor (identical but with historical mode)
    historical_processor = OCRProcessor(config=standard_config)
    historical_processor.update_config({"document_mode": "historical"})
    
    # Results table
    results = []
    
    # Process each sample
    print(f"{'Period':<15} {'Standard Acc.':<15} {'Historical Acc.':<15} {'Improvement':<10}")
    print("-" * 55)
    
    for idx, sample in enumerate(HISTORICAL_SAMPLES):
        # Create historical image
        image, image_path = create_historical_image(
            sample["text"], 
            sample["period"], 
            sample.get("features", [])
        )
        
        # Process with standard OCR
        standard_text = standard_processor.process_image(image)
        standard_accuracy = calculate_accuracy(sample["text"], standard_text)
        
        # Process with historical OCR
        historical_text = historical_processor.process_image(image)
        historical_accuracy = calculate_accuracy(sample["text"], historical_text)
        
        # Calculate improvement
        improvement = (historical_accuracy - standard_accuracy) * 100
        
        # Save results
        results.append({
            "period": sample["period"],
            "standard_accuracy": standard_accuracy,
            "historical_accuracy": historical_accuracy,
            "improvement": improvement
        })
        
        # Print result row
        print(f"{sample['period']:<15} {standard_accuracy:.2%} {historical_accuracy:.2%} {improvement:+.1f}%")
        
        # Save results to file for detailed analysis
        with open(f"output/ocr_results/result_{idx+1}.txt", "w") as f:
            f.write(f"Period: {sample['period']}\n")
            f.write(f"Features: {', '.join(sample.get('features', []))}\n\n")
            f.write(f"Original text:\n{sample['text']}\n\n")
            f.write(f"Standard OCR result:\n{standard_text}\n\n")
            f.write(f"Historical OCR result:\n{historical_text}\n\n")
            f.write(f"Standard accuracy: {standard_accuracy:.2%}\n")
            f.write(f"Historical accuracy: {historical_accuracy:.2%}\n")
            f.write(f"Improvement: {improvement:+.1f}%\n")
    
    # Calculate and print average improvement
    avg_improvement = sum(r["improvement"] for r in results) / len(results)
    print("-" * 55)
    print(f"{'Average':<15} {'':<15} {'':<15} {avg_improvement:+.1f}%")
    
    print(f"\nDetailed results saved to output/ocr_results/\n")

if __name__ == "__main__":
    test_ocr_accuracy()