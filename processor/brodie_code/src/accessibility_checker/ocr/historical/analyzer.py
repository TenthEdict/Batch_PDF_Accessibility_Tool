"""
Historical document analyzer module.

This module provides specialized analysis for historical documents, identifying
characteristics like paper yellowing, faded text, historical fonts, etc.
"""

import cv2
import numpy as np
import logging
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
import pytesseract
from PIL import Image

@dataclass
class HistoricalCharacteristics:
    """Stores analyzed characteristics of a historical document"""
    is_historical: bool
    historical_font_type: str
    paper_yellowing_score: float
    faded_text_score: float
    text_density: float
    layout_complexity: float
    skew_angle: float
    estimated_age: str  # "pre_1800", "19thC", "early_20thC", "modern"

class HistoricalDocumentAnalyzer:
    """Analyzer for historical document characteristics."""
    
    def __init__(self):
        """Initialize the historical document analyzer."""
        self.logger = logging.getLogger(__name__)
    
    def analyze_image(self, image: Image.Image) -> HistoricalCharacteristics:
        """
        Analyze a document image for historical characteristics.
        
        Args:
            image: PIL Image to analyze
            
        Returns:
            HistoricalCharacteristics object with analysis results
        """
        # Convert to numpy for OpenCV processing
        img_np = np.array(image)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(img_hsv)
        
        # Calculate basic metrics
        text_density = self._calculate_text_density(img_gray)
        layout_complexity = self._calculate_layout_complexity(img_gray)
        skew_angle = self._calculate_skew_angle(img_gray)
        
        # Calculate historical indicators
        yellowing_score = self._measure_paper_yellowing(image)
        faded_text_score = self._measure_faded_text(image)
        
        # Determine if historical and font type
        is_historical = self._detect_historical_document(image)
        historical_font = ""
        if is_historical:
            historical_font = self._detect_historical_font(image)
        
        # Estimate document age
        estimated_age = self._estimate_document_age(yellowing_score, faded_text_score, historical_font)
        
        return HistoricalCharacteristics(
            is_historical=is_historical,
            historical_font_type=historical_font,
            paper_yellowing_score=yellowing_score,
            faded_text_score=faded_text_score,
            text_density=text_density,
            layout_complexity=layout_complexity,
            skew_angle=skew_angle,
            estimated_age=estimated_age
        )
    
    def _calculate_text_density(self, image: np.ndarray) -> float:
        """Calculate the text density of the document."""
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return np.sum(binary == 0) / binary.size
    
    def _calculate_layout_complexity(self, image: np.ndarray) -> float:
        """Calculate layout complexity score."""
        _, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(image), connectivity=8)
        if len(stats) < 2:
            return 0.0
        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        positions = stats[1:, [cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP]]
        size_variance = np.var(heights) + np.var(widths)
        position_variance = np.var(positions, axis=0).sum()
        size_score = min(1.0, size_variance / (image.shape[0] * image.shape[1]))
        position_score = min(1.0, position_variance / (image.shape[0] * image.shape[1]))
        return (size_score + position_score) / 2
    
    def _calculate_skew_angle(self, image: np.ndarray) -> float:
        """Calculate document skew angle."""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 2:
            return 0.0
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle
    
    def _detect_historical_document(self, image: Image.Image) -> bool:
        """
        Enhanced detection of historical documents based on visual characteristics.
        
        Args:
            image: PIL Image object to analyze
            
        Returns:
            Boolean indicating if the document appears to be historical
        """
        # Convert to numpy array for OpenCV processing
        img_np = np.array(image)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(img_hsv)
        
        # 1. Check for paper aging characteristics
        # Yellowing detection: analyze hue distribution in yellow/sepia range
        yellow_mask = cv2.inRange(h, 15, 40)  # Expanded yellow/sepia hue range
        yellow_ratio = np.sum(yellow_mask) / (yellow_mask.shape[0] * yellow_mask.shape[1])
        
        # Secondary yellowing check: focus on light areas that should be white in modern docs
        light_areas = cv2.inRange(v, 180, 255)  # Light/paper areas
        if np.sum(light_areas) > 0:
            # Check saturation in what should be white areas
            paper_saturation = np.mean(s[light_areas > 0]) / 255.0
            # Check hue in light areas - should be neutral in modern docs
            paper_hue_values = h[light_areas > 0]
            yellow_hue_in_paper = np.sum((paper_hue_values >= 15) & (paper_hue_values <= 40)) / (paper_hue_values.size or 1)
        else:
            paper_saturation = 0
            yellow_hue_in_paper = 0
        
        # 2. Check for staining and aging patterns
        # Detect non-uniform patterns in background (stains, foxing, etc.)
        if np.sum(light_areas) > 0:
            # Calculate local variance in background areas
            local_var = cv2.Laplacian(v, cv2.CV_64F)
            light_var = np.std(local_var[light_areas > 0])
            normalized_light_var = min(1.0, light_var / 50)
        else:
            normalized_light_var = 0
        
        # 3. Text appearance analysis
        # Binarize the image to isolate text
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text_mask = binary == 0  # Text pixels are black (0)
        
        # Check for text fading (common in historical documents)
        if np.sum(text_mask) > 0:
            text_intensity = img_gray[text_mask]
            # Higher values indicate more fading
            text_fading_score = np.mean(text_intensity) / 255.0
            
            # Calculate text-to-background contrast (lower in historical documents)
            bg_intensity = np.mean(img_gray[~text_mask]) if np.sum(~text_mask) > 0 else 127
            text_intensity_mean = np.mean(text_intensity) if text_intensity.size > 0 else 0
            contrast_ratio = 1.0 - (abs(bg_intensity - text_intensity_mean) / 255.0)
        else:
            text_fading_score = 0.5
            contrast_ratio = 0.5
        
        # 4. Typography analysis
        components = cv2.connectedComponentsWithStats(cv2.bitwise_not(binary), 8)
        
        # Initialize typography scores
        normalized_spacing_var = 0
        letterpress_impression_score = 0
        
        if len(components[2]) > 10:  # If we have enough components for analysis
            # Extract character component stats
            stats = components[2][1:]  # Skip background component
            positions_x = stats[:, cv2.CC_STAT_LEFT]
            positions_y = stats[:, cv2.CC_STAT_TOP]
            widths = stats[:, cv2.CC_STAT_WIDTH]
            heights = stats[:, cv2.CC_STAT_HEIGHT]
            
            # Filter out noise and outliers
            valid_indices = (widths > 3) & (heights > 5) & (widths < np.mean(widths) * 5) & (heights < np.mean(heights) * 5)
            if np.sum(valid_indices) > 5:
                # Analyze character spacing (more irregular in historical prints)
                valid_positions_x = positions_x[valid_indices]
                line_positions_y = self._cluster_line_positions(positions_y[valid_indices])
                
                line_spacing_vars = []
                for line_y in line_positions_y:
                    # Find characters on this line
                    line_chars = np.abs(positions_y[valid_indices] - line_y) < (np.mean(heights[valid_indices]) * 0.5)
                    if np.sum(line_chars) > 3:
                        line_x_positions = np.sort(valid_positions_x[line_chars])
                        # Calculate spaces between characters
                        spaces = np.diff(line_x_positions)
                        # Calculate variance in spacing
                        if len(spaces) > 1:
                            line_spacing_vars.append(np.var(spaces) / np.mean(spaces))
                
                # Overall spacing irregularity
                if line_spacing_vars:
                    normalized_spacing_var = min(1.0, np.mean(line_spacing_vars) / 4.0)
                
                # Letterpress impression detection (thicker edges on one side - common in old prints)
                # Calculate edge thickness variation around each character
                edge_thickness_var = self._measure_edge_thickness_variation(binary, stats[valid_indices])
                letterpress_impression_score = min(1.0, edge_thickness_var / 2.0)
        
        # 5. Combine all indicators with appropriate weights
        historical_indicators = {
            'yellowing': yellow_ratio * 0.8 + yellow_hue_in_paper * 0.2,
            'paper_saturation': paper_saturation,
            'staining': normalized_light_var,
            'text_fading': text_fading_score,
            'contrast_ratio': contrast_ratio,
            'spacing_irregularity': normalized_spacing_var,
            'letterpress_impression': letterpress_impression_score
        }
        
        # Weighted combination of indicators
        historical_score = (
            historical_indicators['yellowing'] * 0.25 +
            historical_indicators['paper_saturation'] * 0.15 +
            historical_indicators['staining'] * 0.15 +
            historical_indicators['text_fading'] * 0.15 +
            historical_indicators['contrast_ratio'] * 0.10 +
            historical_indicators['spacing_irregularity'] * 0.10 +
            historical_indicators['letterpress_impression'] * 0.10
        )
        
        # Log the detailed analysis results
        self.logger.debug(f"Historical document analysis: {historical_indicators}")
        self.logger.debug(f"Historical score: {historical_score:.3f}")
        
        # Classify as historical if score exceeds threshold
        # Increased threshold to avoid misclassifying modern book covers/publisher pages
        historical_threshold = 0.75  # Higher threshold for confident classification
        self.logger.info(f"Historical detection score: {historical_score:.3f} (threshold: {historical_threshold})")
        return historical_score > historical_threshold
    
    def _cluster_line_positions(self, y_positions: np.ndarray) -> list:
        """
        Cluster Y positions to identify text lines.
        
        Args:
            y_positions: Array of Y coordinates of character components
            
        Returns:
            List of identified line positions (Y coordinates)
        """
        if len(y_positions) < 2:
            return [np.mean(y_positions)] if len(y_positions) > 0 else []
            
        # Sort positions
        sorted_y = np.sort(y_positions)
        
        # Calculate differences between consecutive positions
        diffs = np.diff(sorted_y)
        
        # Find gaps between lines (significantly larger differences)
        mean_diff = np.mean(diffs)
        std_diff = np.std(diffs)
        threshold = mean_diff + std_diff * 1.5
        
        # Identify line breaks
        line_breaks = np.where(diffs > threshold)[0]
        
        # Extract line positions
        lines = []
        start_idx = 0
        
        for break_idx in line_breaks:
            line_positions = sorted_y[start_idx:break_idx+1]
            lines.append(np.mean(line_positions))
            start_idx = break_idx + 1
            
        # Add the last line
        if start_idx < len(sorted_y):
            lines.append(np.mean(sorted_y[start_idx:]))
            
        return lines
    
    def _measure_edge_thickness_variation(self, binary_image: np.ndarray, component_stats: np.ndarray) -> float:
        """
        Measure variation in edge thickness around characters.
        Historical letterpress printing often shows thicker edges on one side.
        
        Args:
            binary_image: Binary image with black text on white background
            component_stats: Stats for character components
            
        Returns:
            Score representing edge thickness variation
        """
        # Skip if too few components
        if len(component_stats) < 5:
            return 0.0
        
        # Create edge image
        edge_img = cv2.Canny(binary_image, 100, 200)
        
        # Prepare to measure edge thickness in different directions
        variations = []
        
        # Check a sample of larger components (likely characters, not noise)
        areas = component_stats[:, cv2.CC_STAT_AREA]
        heights = component_stats[:, cv2.CC_STAT_HEIGHT]
        
        # Only examine larger components
        size_threshold = np.percentile(areas, 25)
        height_threshold = np.percentile(heights, 25)
        
        for i, stats in enumerate(component_stats):
            # Skip small components
            if stats[cv2.CC_STAT_AREA] < size_threshold or stats[cv2.CC_STAT_HEIGHT] < height_threshold:
                continue
                
            x, y, w, h = stats[0:4]
            
            # Ensure we stay within image bounds
            x = max(0, x - 1)
            y = max(0, y - 1)
            w = min(w + 2, binary_image.shape[1] - x)
            h = min(h + 2, binary_image.shape[0] - y)
            
            if w <= 4 or h <= 4:  # Skip very small components
                continue
                
            # Extract ROI
            char_roi = edge_img[y:y+h, x:x+w]
            
            # Measure edge thickness in different directions
            left_edge = char_roi[:, 0:w//4].sum() / (char_roi.shape[0] * w//4 or 1)
            right_edge = char_roi[:, 3*w//4:].sum() / (char_roi.shape[0] * (w - 3*w//4) or 1)
            top_edge = char_roi[0:h//4, :].sum() / (h//4 * char_roi.shape[1] or 1)
            bottom_edge = char_roi[3*h//4:, :].sum() / ((h - 3*h//4) * char_roi.shape[1] or 1)
            
            # Calculate directional variation
            horiz_var = abs(left_edge - right_edge) / (max(left_edge, right_edge) or 1)
            vert_var = abs(top_edge - bottom_edge) / (max(top_edge, bottom_edge) or 1)
            
            # Use the maximum variation found
            variations.append(max(horiz_var, vert_var))
            
            # Limit the number of components checked for performance
            if len(variations) >= 20:
                break
                
        # Return the average variation
        return np.mean(variations) if variations else 0.0
    
    def _detect_historical_font(self, image: Image.Image) -> str:
        """
        Detect the type of historical font used in the document.
        
        Args:
            image: PIL Image object to analyze
            
        Returns:
            String identifying the historical font type
        """
        # Convert to numpy for processing
        img_np = np.array(image)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Extract character components
        _, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.bitwise_not(binary), 8)
        
        if len(stats) <= 1:
            return "unknown"
            
        # Calculate character metrics
        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        
        # Filter out noise and outliers
        valid_indices = np.where((heights > 5) & (widths > 3) & (heights < 100))[0]
        if len(valid_indices) < 10:
            return "unknown"
            
        heights = heights[valid_indices]
        widths = widths[valid_indices]
        
        # Calculate aspect ratios
        aspect_ratios = widths / heights
        
        # Metrics for classification
        mean_aspect = np.mean(aspect_ratios)
        std_aspect = np.std(aspect_ratios)
        
        # Classification based on font characteristics
        if mean_aspect < 0.65 and std_aspect > 0.25:
            return "blackletter"  # Gothic/blackletter fonts
        elif mean_aspect > 0.85:
            return "modern_serif"  # More recent serif fonts
        elif std_aspect > 0.2:
            return "old_style_serif"  # Variable width old style serif
        else:
            return "standard_serif"  # Default historical serif
    
    def _measure_paper_yellowing(self, image: Image.Image) -> float:
        """
        Measure the degree of yellowing/aging in paper.
        
        Args:
            image: PIL Image object to analyze
            
        Returns:
            Float score (0-1) indicating the degree of yellowing
        """
        # Convert to HSV color space for better color analysis
        img_np = np.array(image)
        img_hsv = cv2.cvtColor(img_np, cv2.COLOR_RGB2HSV)
        h, s, v = cv2.split(img_hsv)
        
        # Create mask for light areas (paper background)
        paper_mask = cv2.inRange(v, 180, 255)
        
        if np.sum(paper_mask) == 0:
            return 0.0
            
        # Calculate hue and saturation metrics in paper areas
        paper_hue = h[paper_mask > 0]
        paper_saturation = s[paper_mask > 0]
        
        # Calculate percentage of yellow-range hues in paper
        yellow_hue_mask = np.logical_and(paper_hue >= 20, paper_hue <= 35)
        yellow_ratio = np.sum(yellow_hue_mask) / len(paper_hue) if len(paper_hue) > 0 else 0
        
        # Calculate average saturation in paper
        avg_saturation = np.mean(paper_saturation) / 255.0
        
        # Combine metrics (weighted)
        yellowing_score = (yellow_ratio * 0.7) + (avg_saturation * 0.3)
        
        return min(1.0, yellowing_score)
    
    def _measure_faded_text(self, image: Image.Image) -> float:
        """
        Measure the degree of text fading in the document.
        
        Args:
            image: PIL Image object to analyze
            
        Returns:
            Float score (0-1) indicating the degree of text fading
        """
        # Convert to grayscale
        img_np = np.array(image)
        img_gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
        
        # Threshold to separate text from background
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        text_mask = binary == 0  # Text pixels are black (0)
        
        if np.sum(text_mask) == 0:
            return 0.0
        
        # Get grayscale values of text pixels
        text_intensity = img_gray[text_mask]
        
        # Calculate metrics:
        # 1. Average intensity of text (higher means more faded)
        avg_intensity = np.mean(text_intensity) / 255.0
        
        # 2. Contrast between text and background
        background_intensity = img_gray[~text_mask]
        if len(background_intensity) > 0:
            avg_background = np.mean(background_intensity)
            contrast_ratio = 1.0 - (abs(avg_background - np.mean(text_intensity)) / 255.0)
        else:
            contrast_ratio = 0.5
        
        # 3. Variance in text intensity (lower means more consistent fading)
        intensity_variance = 1.0 - min(1.0, np.var(text_intensity) / 2000)
        
        # Combine metrics (weighted)
        fading_score = (avg_intensity * 0.4) + (contrast_ratio * 0.4) + (intensity_variance * 0.2)
        
        return min(1.0, fading_score)
    
    def _estimate_document_age(self, yellowing_score: float, fading_score: float, font_type: str) -> str:
        """
        Estimate the approximate age of a document based on visual characteristics.
        
        Args:
            yellowing_score: Score indicating paper yellowing
            fading_score: Score indicating text fading
            font_type: Detected historical font type
            
        Returns:
            String indicating estimated age: "pre_1800", "19thC", "early_20thC", or "modern"
        """
        # Very old documents have high yellowing and fading
        if yellowing_score > 0.8 and fading_score > 0.7:
            return "pre_1800"
        
        # Font type is a strong indicator for very old documents
        if font_type == "blackletter":
            return "pre_1800"
        
        # 19th century documents have significant but not extreme aging
        if (yellowing_score > 0.6 and fading_score > 0.5) or font_type == "old_style_serif":
            return "19thC"
            
        # Early 20th century has moderate aging
        if yellowing_score > 0.4 or fading_score > 0.3:
            return "early_20thC"
            
        # Default to modern for low aging scores
        return "modern"