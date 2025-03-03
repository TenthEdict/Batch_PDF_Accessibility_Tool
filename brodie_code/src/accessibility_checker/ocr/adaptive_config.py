import cv2
import numpy as np
from typing import Dict, Any, List, Tuple
import logging
from dataclasses import dataclass
import fitz
from PIL import Image
import pytesseract
from pdf2image import convert_from_path


@dataclass
class DocumentCharacteristics:
    """Stores analyzed characteristics of a document"""
    avg_text_density: float
    avg_font_size: float
    has_math_content: bool
    has_tables: bool
    image_quality_score: float
    language_script: str
    layout_complexity: float
    skew_angle: float
    is_historical: bool
    historical_font_type: str
    paper_yellowing_score: float
    faded_text_score: float


class AdaptiveOCRConfig:
    """Adaptive OCR configuration handler that optimizes settings based on document characteristics."""

    def __init__(self, base_config: Dict[str, Any]) ->None:
        self.logger = logging.getLogger(__name__)
        self.base_config = base_config
        self.psm_mappings = {'simple': 3, 'complex': 6, 'table_heavy': 4,
            'mixed': 11, 'single_column': 1, 'multi_column': 2}

    def analyze_document(self, pdf_path: str) ->DocumentCharacteristics:
        """Analyze document characteristics with improved error handling and detection."""
        try:
            pages = convert_from_path(pdf_path, first_page=1, last_page=min
                (5, self._get_page_count(pdf_path)))
            metrics = {'text_density': [], 'font_size': [], 'quality': [],
                'complexity': [], 'skew': []}
            math_content_detected = False
            tables_detected = False
            for page in pages:
                try:
                    img_np = cv2.cvtColor(np.array(page), cv2.COLOR_RGB2BGR)
                    gray = cv2.cvtColor(img_np, cv2.COLOR_BGR2GRAY)
                    page_metrics = self._calculate_page_metrics(gray)
                    for key in metrics:
                        if key in page_metrics:
                            metrics[key].append(page_metrics[key])
                    if self._detect_math_symbols(gray):
                        math_content_detected = True
                    if self._detect_tables(gray):
                        tables_detected = True
                except Exception as e:
                    self.logger.warning(f'Error analyzing page: {str(e)}')
                    continue
            # Detect historical characteristics
            is_historical_doc = self._detect_historical_document(pages[0])
            historical_font = ""
            yellowing_score = 0.0
            faded_text_score = 0.0
            
            if is_historical_doc:
                historical_font = self._detect_historical_font(pages[0])
                yellowing_score = self._measure_paper_yellowing(pages[0])
                faded_text_score = self._measure_faded_text(pages[0])
            
            return DocumentCharacteristics(
                avg_text_density=np.mean(metrics['text_density']) if metrics['text_density'] else 0,
                avg_font_size=np.mean(metrics['font_size']) if metrics['font_size'] else 0, 
                has_math_content=math_content_detected,
                has_tables=tables_detected, 
                image_quality_score=np.mean(metrics['quality']) if metrics['quality'] else 0,
                language_script=self._detect_primary_script(pages[0]),
                layout_complexity=np.mean(metrics['complexity']) if metrics['complexity'] else 0, 
                skew_angle=np.mean(metrics['skew']) if metrics['skew'] else 0,
                is_historical=is_historical_doc,
                historical_font_type=historical_font,
                paper_yellowing_score=yellowing_score,
                faded_text_score=faded_text_score
            )
        except Exception as e:
            self.logger.error(f'Error analyzing document: {str(e)}')
            raise

    def _calculate_page_metrics(self, image: np.ndarray) ->Dict[str, float]:
        """Calculate comprehensive page metrics."""
        metrics = {}
        try:
            _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY +
                cv2.THRESH_OTSU)
            metrics['text_density'] = np.sum(binary == 0) / binary.size
            components = cv2.connectedComponentsWithStats(cv2.bitwise_not(
                binary), 4, cv2.CV_32S)
            if components[0] > 1:
                heights = components[2][1:, cv2.CC_STAT_HEIGHT]
                metrics['font_size'] = np.median(heights[heights < np.
                    percentile(heights, 95)])
            metrics['quality'] = self._calculate_image_quality(image)
            metrics['complexity'] = self._calculate_layout_complexity(image)
            metrics['skew'] = abs(self._calculate_skew_angle(image))
        except Exception as e:
            self.logger.warning(f'Error calculating page metrics: {str(e)}')
        return metrics

    def _get_page_count(self, pdf_path: str) ->int:
        """Get the total number of pages in the PDF."""
        try:
            with fitz.open(pdf_path) as doc:
                return len(doc)
        except Exception as e:
            self.logger.error(f'Error getting page count: {str(e)}')
            return 1

    def get_optimal_config(self, characteristics: DocumentCharacteristics
        ) ->Dict[str, Any]:
        """Generate optimal OCR configuration based on document characteristics."""
        config = self.base_config.copy()
        
        # Handle historical documents with specialized processing
        if characteristics.is_historical:
            self.logger.info(f"Configuring for historical document processing (font: {characteristics.historical_font_type})")
            
            # Set document mode to historical for specialized preprocessing
            config['document_mode'] = 'historical'
            
            # Historical documents often need different PSM mode
            if characteristics.layout_complexity > 0.6:
                config['psm'] = self.psm_mappings['complex']
            else:
                # For simple historical layouts, use mode 6 (assumes a single block of text)
                # This often works better with old typesetting
                config['psm'] = self.psm_mappings['simple']
            
            # Use legacy + LSTM for historical fonts (better accuracy with old fonts)
            config['oem'] = 2
            
            # Historical documents need special preprocessing
            config['preprocessing'] = {
                'enhance_contrast': True, 
                'denoise': True,
                'sharpen': True,
                'historical_mode': True
            }
            
            # Create historical config dictionary to load from base_config
            historical_config = self.base_config.get('additional_params', {}).get('historical_document', {})
            
            # Add historical character whitelist
            historical_chars = historical_config.get('preprocessing', {}).get('historical_char_whitelist', 'ſƺȝȣþðæœ')
            config['char_whitelist'] += historical_chars
            
            # Apply font-specific settings based on detected historical font type
            if characteristics.historical_font_type:
                self.logger.info(f"Applying specialized parameters for {characteristics.historical_font_type} font")
                font_config = historical_config.get('fonts', {}).get(characteristics.historical_font_type, {})
                
                # Apply all font-specific parameters if available
                if font_config:
                    for key, value in font_config.items():
                        if key not in ['psm', 'oem']:  # These are already set
                            config[key] = value
            
            # Apply general historical document parameters
            tesseract_params = historical_config.get('tesseract_params', {})
            for key, value in tesseract_params.items():
                config[key] = value
            
            # Determine appropriate historical dictionary based on estimated age
            # This could be enhanced with more sophisticated document dating
            dictionaries = historical_config.get('dictionaries', {})
            for era, dict_config in dictionaries.items():
                if dict_config.get('enabled', False):
                    filename = dict_config.get('filename')
                    if filename:
                        config['user_words_file'] = filename
                        break
            
            # Adjust parameters based on historical document condition
            if characteristics.paper_yellowing_score > 0.5:
                self.logger.info("Applying yellowed paper optimizations")
                yellowed_params = historical_config.get('condition_adjustments', {}).get('yellowed_paper', {})
                for key, value in yellowed_params.items():
                    config[key] = value
            
            if characteristics.faded_text_score > 0.6:
                self.logger.info("Applying faded text optimizations")
                faded_params = historical_config.get('condition_adjustments', {}).get('faded_text', {})
                for key, value in faded_params.items():
                    config[key] = value
            
            # Check for damaged pages based on image quality score
            if characteristics.image_quality_score < 0.4:
                self.logger.info("Applying damaged page optimizations")
                damaged_params = historical_config.get('condition_adjustments', {}).get('damaged_pages', {})
                for key, value in damaged_params.items():
                    config[key] = value
            
            # Always add deskew for historical documents which often have page warping
            config['deskew'] = True
            
            return config
            
        # Standard document processing (non-historical)
        if characteristics.layout_complexity > 0.7:
            config['psm'] = self.psm_mappings['complex']
        elif characteristics.has_tables:
            config['psm'] = self.psm_mappings['table_heavy']
        elif characteristics.layout_complexity < 0.3:
            config['psm'] = self.psm_mappings['simple']
        else:
            config['psm'] = self.psm_mappings['mixed']
            
        if characteristics.image_quality_score < 0.6:
            config['preprocessing'] = {'enhance_contrast': True, 'denoise':
                True, 'sharpen': True}
                
        if characteristics.has_math_content:
            config['char_whitelist'] += '+-=×÷()[]{}πΣ∫∂√∞∈∀∃≠≤≥±αβγδεθλμπσφω'
            
        if characteristics.language_script != 'Latin':
            config['oem'] = 1
            
        if characteristics.skew_angle > 0.5:
            config['deskew'] = True
            
        if characteristics.avg_text_density > 0.4:
            config['textord_min_linesize'] = 2.5
            
        if characteristics.avg_font_size < 10:
            config['textord_min_xheight'] = 4
            config['enhance_resolution'] = True
            
        return config

    def _detect_math_symbols(self, image: np.ndarray) ->bool:
        """Detect presence of mathematical symbols in image."""
        math_symbols = ['Σ', '∫', '∂', '√', '∞', '≠', '≤', '≥', '±']
        text = pytesseract.image_to_string(image, config='--psm 11 --oem 3')
        return any(symbol in text for symbol in math_symbols)

    def _detect_tables(self, image: np.ndarray) ->bool:
        """Detect presence of tables using line detection."""
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 100, minLineLength=
            100, maxLineGap=10)
        if lines is not None:
            horizontal_lines = 0
            vertical_lines = 0
            for line in lines:
                x1, y1, x2, y2 = line[0]
                if abs(y2 - y1) < 10:
                    horizontal_lines += 1
                if abs(x2 - x1) < 10:
                    vertical_lines += 1
            return horizontal_lines > 3 and vertical_lines > 3
        return False

    def _calculate_image_quality(self, image: np.ndarray) ->float:
        """Calculate image quality score."""
        blur_score = cv2.Laplacian(image, cv2.CV_64F).var()
        _, binary = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.
            THRESH_OTSU)
        contrast = np.std(image)
        blur_score_norm = min(1.0, blur_score / 500)
        contrast_norm = min(1.0, contrast / 127)
        return (blur_score_norm + contrast_norm) / 2

    def _calculate_layout_complexity(self, image: np.ndarray) ->float:
        """Calculate layout complexity score."""
        _, labels, stats, _ = cv2.connectedComponentsWithStats(cv2.
            bitwise_not(image), connectivity=8)
        if len(stats) < 2:
            return 0.0
        heights = stats[1:, cv2.CC_STAT_HEIGHT]
        widths = stats[1:, cv2.CC_STAT_WIDTH]
        positions = stats[1:, [cv2.CC_STAT_LEFT, cv2.CC_STAT_TOP]]
        size_variance = np.var(heights) + np.var(widths)
        position_variance = np.var(positions, axis=0).sum()
        size_score = min(1.0, size_variance / (image.shape[0] * image.shape[1])
            )
        position_score = min(1.0, position_variance / (image.shape[0] *
            image.shape[1]))
        return (size_score + position_score) / 2

    def _calculate_skew_angle(self, image: np.ndarray) ->float:
        """Calculate document skew angle."""
        coords = np.column_stack(np.where(image > 0))
        if len(coords) < 2:
            return 0.0
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = 90 + angle
        return angle

    def _detect_primary_script(self, image: Image.Image) ->str:
        """Detect primary script (writing system) used in the document."""
        text = pytesseract.image_to_string(image, config='--psm 1 --oem 1')
        latin_chars = sum(1 for c in text if ord('a') <= ord(c.lower()) <=
            ord('z'))
        total_chars = len([c for c in text if c.strip()])
        return ('Latin' if total_chars == 0 or latin_chars / total_chars > 
            0.5 else 'Other')
            
    def _detect_historical_document(self, image: Image.Image) -> bool:
        """
        Enhanced detection of historical documents based on visual characteristics.
        
        This analyzes:
        - Paper color and condition (yellowing, staining)
        - Font characteristics typical of older documents
        - Layout and spacing patterns
        - Text degradation and fading patterns
        - Typographical features common in historical documents
        - Print impression characteristics
        
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
        # ----------------------------------------
        
        # Yellowing detection: analyze hue distribution in yellow/sepia range
        yellow_mask1 = cv2.inRange(h, 15, 40)  # Expanded yellow/sepia hue range
        yellow_ratio1 = np.sum(yellow_mask1) / (yellow_mask1.shape[0] * yellow_mask1.shape[1])
        
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
        # ---------------------------------------
        # Detect non-uniform patterns in background (stains, foxing, etc.)
        if np.sum(light_areas) > 0:
            # Calculate local variance in background areas
            local_var = cv2.Laplacian(v, cv2.CV_64F)
            light_var = np.std(local_var[light_areas > 0])
            normalized_light_var = min(1.0, light_var / 50)
        else:
            normalized_light_var = 0
        
        # 3. Text appearance analysis
        # --------------------------
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
        # ---------------------
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
        # -------------------------------------------------
        historical_indicators = {
            'yellowing': yellow_ratio1 * 0.8 + yellow_hue_in_paper * 0.2,
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
        # Lower threshold (0.3) to catch more potential historical documents
        return historical_score > 0.3
        
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

    def _enhance_image_quality(self, image: np.ndarray,
        preprocessing_config: Dict[str, bool]) ->np.ndarray:
        """Apply image enhancement based on preprocessing configuration."""
        enhanced = image.copy()
        if preprocessing_config.get('enhance_contrast'):
            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(enhanced)
        if preprocessing_config.get('denoise'):
            enhanced = cv2.fastNlMeansDenoising(enhanced)
        if preprocessing_config.get('sharpen'):
            blur = cv2.GaussianBlur(enhanced, (0, 0), 3)
            enhanced = cv2.addWeighted(enhanced, 1.5, blur, -0.5, 0)
        
        # Special processing for historical documents
        if preprocessing_config.get('historical_mode'):
            # Apply additional processing specific to historical documents
            # Enhance contrast more aggressively
            enhanced = cv2.equalizeHist(enhanced)
            
            # Apply stronger denoising
            enhanced = cv2.fastNlMeansDenoising(enhanced, h=15)
            
            # Apply morphological operations to strengthen text
            kernel = np.ones((1, 1), np.uint8)
            enhanced = cv2.morphologyEx(enhanced, cv2.MORPH_CLOSE, kernel)
            
        return enhanced

    def update_base_config(self, new_config: Dict[str, Any]) ->None:
        """Update the base configuration with new settings."""
        self.base_config.update(new_config)
        self.logger.info(f'Updated base configuration: {new_config}')

    def get_available_optimizations(self) ->Dict[str, str]:
        """Return dictionary of available optimization strategies."""
        return {'psm_modes': {str(mode): desc for mode, desc in {(3):
            'Fully automatic page segmentation without OSD', (6):
            'Assume a uniform block of text', (4):
            'Assume a single column of variable-sized text', (11):
            'Sparse text with OSD', (1):
            'Automatic page segmentation with OSD', (2):
            'Automatic page segmentation, no OSD or OCR'}.items()},
            'preprocessing': {'enhance_contrast':
            'Improve image contrast using CLAHE', 'denoise':
            'Remove image noise', 'sharpen': 'Enhance text edges'},
            'engine_modes': {'0': 'Legacy engine only', '1':
            'Neural nets LSTM engine only', '2': 'Legacy + LSTM engines',
            '3': 'Default, based on what is available'}}
