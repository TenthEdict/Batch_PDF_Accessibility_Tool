#!/usr/bin/env python3
"""
Utility script to visualize DoclingDocument results from SmolDocling processing.
"""

import os
import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from docling.core import DoclingDocument


def load_document(json_path: str) -> DoclingDocument:
    """
    Load a DoclingDocument from a JSON file.
    
    Args:
        json_path: Path to the JSON file.
    
    Returns:
        DoclingDocument instance.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)
    
    return DoclingDocument.from_dict(data)


def visualize_document(document: DoclingDocument, image_path: str, output_path: str) -> None:
    """
    Visualize a DoclingDocument by drawing bounding boxes on the original image.
    
    Args:
        document: DoclingDocument instance.
        image_path: Path to the original image.
        output_path: Path to save the visualization.
    """
    # Load image
    img = Image.open(image_path).convert("RGB")
    draw = ImageDraw.Draw(img)
    
    # Try to get a font
    try:
        font = ImageFont.truetype("Arial", 12)
    except:
        font = ImageFont.load_default()
    
    # Colors for different element types
    colors = {
        "text": (255, 0, 0, 128),  # Red for text
        "title": (0, 0, 255, 128),  # Blue for titles
        "list": (0, 255, 0, 128),   # Green for lists
        "table": (255, 0, 255, 128),  # Purple for tables
        "image": (255, 255, 0, 128),  # Yellow for images
        "default": (200, 200, 200, 128)  # Gray for other elements
    }
    
    # Draw bounding boxes for all elements
    for element in document.elements:
        element_type = element.get("type", "default")
        bbox = element.get("bbox", None)
        
        if bbox:
            x0, y0, x1, y1 = bbox
            
            # Scale bbox if needed
            width, height = img.size
            x0 = int(x0 * width)
            y0 = int(y0 * height)
            x1 = int(x1 * width)
            y1 = int(y1 * height)
            
            # Draw rectangle
            color = colors.get(element_type, colors["default"])
            draw.rectangle([x0, y0, x1, y1], outline=color[:3], width=2)
            
            # Draw label
            text = element.get("text", "")
            if text:
                text = text[:20] + "..." if len(text) > 20 else text
                draw.text((x0, y0 - 15), f"{element_type}: {text}", fill=color[:3], font=font)
    
    # Save visualization
    img.save(output_path)
    print(f"Visualization saved to {output_path}")


def main():
    """Main entry point for the visualization script."""
    parser = argparse.ArgumentParser(description="Visualize DoclingDocument results")
    parser.add_argument(
        "--document", "-d", 
        required=True,
        help="Path to the DoclingDocument JSON file"
    )
    parser.add_argument(
        "--image", "-i", 
        required=True,
        help="Path to the original image"
    )
    parser.add_argument(
        "--output", "-o", 
        default=None,
        help="Output path for visualization (default: adds '_viz' suffix to original image)"
    )
    
    args = parser.parse_args()
    
    # Set default output path if not provided
    if args.output is None:
        image_path = Path(args.image)
        output_path = str(image_path.parent / f"{image_path.stem}_viz{image_path.suffix}")
    else:
        output_path = args.output
    
    # Load document
    document = load_document(args.document)
    
    # Visualize
    visualize_document(document, args.image, output_path)


if __name__ == "__main__":
    main()