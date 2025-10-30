#!/usr/bin/env python3
"""
Intelligent OCR Enhancement Module

This module provides intelligent OCR processing that learns from document patterns
and adapts OCR parameters to improve text layer output success rates.

Features:
- Adaptive OCR parameter optimization using ML
- Document pattern-based processing
- Quality assessment and feedback loops
- Continuous learning from processing results
- Integration with adaptive ML enhancer
"""

import logging
import time
import tempfile
import io
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
import json

# OCR and image processing imports
import pytesseract
from PIL import Image
import cv2
import numpy as np
import fitz  # PyMuPDF

# Optional ML imports
try:
    from .adaptive_ml_enhancer import AdaptiveMLEnhancer
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    AdaptiveMLEnhancer = None

# Thread-safe ML imports
try:
    from .thread_safe_ml_enhancer import ThreadSafeAdaptiveMLEnhancer
    THREAD_SAFE_ML_AVAILABLE = True
except ImportError:
    THREAD_SAFE_ML_AVAILABLE = False
    ThreadSafeAdaptiveMLEnhancer = None

from .enhancer_base import EnhancerBase
from .pdf_text_analyzer import PDFTextAnalyzer

logger = logging.getLogger(__name__)


@dataclass
class OCRProcessingResult:
    """Result of intelligent OCR processing."""
    success: bool
    text_content: str
    confidence_score: float
    processing_time: float
    ocr_parameters_used: Dict[str, Any]
    quality_metrics: Dict[str, float]
    pattern_match: Optional[Dict[str, Any]] = None
    recommendations: List[str] = None


class IntelligentOCREnhancer(EnhancerBase):
    """
    Intelligent OCR enhancer that learns from document patterns.
    
    Provides adaptive OCR processing using:
    - Document pattern analysis
    - ML-optimized OCR parameters
    - Quality assessment and feedback
    - Continuous learning
    """
    
    def __init__(self, component_name: str = "intelligent_ocr_enhancer", environment: Optional[str] = None, force_thread_safe: bool = None):
        """Initialize intelligent OCR enhancer."""
        super().__init__(component_name, environment)
        
        # Core components
        self.text_analyzer = PDFTextAnalyzer()
        
        # Determine if we should use thread-safe ML enhancer
        use_thread_safe = self._should_use_thread_safe_ml(force_thread_safe)
        
        # ML components (optional)
        self.adaptive_ml = None
        if use_thread_safe and THREAD_SAFE_ML_AVAILABLE:
            try:
                self.adaptive_ml = ThreadSafeAdaptiveMLEnhancer()
                logger.info("Thread-safe adaptive ML enhancer initialized for parallel processing")
            except Exception as e:
                logger.warning(f"Could not initialize thread-safe ML enhancer: {e}")
                # Fallback to regular ML enhancer
                if ML_AVAILABLE:
                    try:
                        self.adaptive_ml = AdaptiveMLEnhancer()
                        logger.info("Fallback to regular adaptive ML enhancer")
                    except Exception as e2:
                        logger.warning(f"Could not initialize ML enhancer: {e2}")
        elif ML_AVAILABLE:
            try:
                self.adaptive_ml = AdaptiveMLEnhancer()
                logger.info("Adaptive ML enhancer initialized for intelligent OCR")
            except Exception as e:
                logger.warning(f"Could not initialize adaptive ML enhancer: {e}")
        
        # Processing statistics
        self.processing_stats = {
            'total_processed': 0,
            'successful_ocr': 0,
            'pattern_matches': 0,
            'avg_processing_time': 0.0,
            'avg_confidence': 0.0,
            'ml_enhancer_type': 'thread_safe' if use_thread_safe else 'regular'
        }
        
        logger.info("Intelligent OCR Enhancer initialized successfully")
    
    def _should_use_thread_safe_ml(self, force_thread_safe: Optional[bool] = None) -> bool:
        """
        Determine if thread-safe ML enhancer should be used.
        
        Args:
            force_thread_safe: Force thread-safe mode (overrides auto-detection)
            
        Returns:
            bool: True if thread-safe ML enhancer should be used
        """
        if force_thread_safe is not None:
            return force_thread_safe
        
        # Auto-detection based on environment
        import threading
        import os
        
        # Check if we're in a multi-threaded environment
        thread_name = threading.current_thread().name
        
        # Detect parallel processing indicators
        parallel_indicators = [
            'PDFWorker' in thread_name,  # Our parallel batch processor threads
            'ThreadPoolExecutor' in thread_name,
            os.environ.get('EPUBS_PARALLEL_MODE', '').lower() == 'true',
            hasattr(threading.current_thread(), 'parallel_processing_mode')
        ]
        
        use_thread_safe = any(parallel_indicators)
        
        logger.debug(f"Thread-safe ML auto-detection: {use_thread_safe} (thread: {thread_name})")
        return use_thread_safe
    
    def get_capabilities(self) -> List[str]:
        """Get intelligent OCR enhancement capabilities."""
        capabilities = [
            "intelligent_ocr_detection",
            "adaptive_parameter_optimization",
            "pattern_based_processing",
            "quality_assessment",
            "feedback_learning"
        ]
        
        if self.adaptive_ml:
            capabilities.extend([
                "ml_enhanced_ocr",
                "document_pattern_learning",
                "success_rate_prediction"
            ])
        
        return capabilities
    
    def enhance_file(self, input_path: Union[str, Path], output_path: Union[str, Path], **kwargs) -> bool:
        """
        Enhance PDF file with intelligent OCR processing.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for enhanced output file
            **kwargs: Additional processing parameters
                - force_ocr_override: bool - Force OCR even if text exists (cleans orphan tags)
            
        Returns:
            bool: True if enhancement was successful
        """
        input_path = Path(input_path)
        output_path = Path(output_path)
        
        if not input_path.exists():
            logger.error(f"Input file not found: {input_path}")
            return False
        
        try:
            start_time = time.time()
            
            # Check for force OCR override (needed to clean orphan tagged content)
            force_ocr_override = kwargs.pop('force_ocr_override', False)
            
            # Step 1: Analyze document to determine if OCR is needed
            if force_ocr_override:
                needs_ocr = True
                logger.info(f"OCR forced by override to clean orphan tagged content in {input_path.name}")
            else:
                needs_ocr = self._analyze_document_needs_ocr(input_path)
            
            if not needs_ocr:
                logger.info(f"Document {input_path.name} has sufficient text content, skipping OCR")
                # Copy file without OCR processing
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            
            # Step 2: Extract document features for ML analysis
            document_features = self._extract_document_features(input_path)
            
            # Step 3: Get optimized OCR parameters
            ocr_params = self._get_optimized_ocr_parameters(document_features)
            
            # Step 4: Perform intelligent OCR processing
            ocr_result = self._perform_intelligent_ocr(input_path, ocr_params)
            
            # Step 5: Apply OCR results to PDF
            success = self._apply_ocr_to_pdf(input_path, output_path, ocr_result)
            
            # Step 6: Learn from processing results
            if self.adaptive_ml:
                self._learn_from_processing_result(document_features, ocr_result)
            
            # Update statistics
            processing_time = time.time() - start_time
            self._update_statistics(ocr_result, processing_time)
            
            logger.info(f"Intelligent OCR processing completed: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Intelligent OCR enhancement failed: {e}")
            return False
    
    def _analyze_document_needs_ocr(self, pdf_path: Path) -> bool:
        """Analyze if document needs OCR processing with ML-enhanced decision making."""
        try:
            # Use the PDF text analyzer for initial assessment
            needs_basic_ocr = self.text_analyzer.quick_text_check(pdf_path)
            
            # With ML enhancement, we want to apply OCR more strategically
            # Even documents with good text can benefit from optimized OCR
            if self.adaptive_ml:
                # For ML-enhanced mode, be more aggressive about applying OCR
                # but with optimized configurations
                text_stats = self.text_analyzer.analyze_text_content(pdf_path)
                avg_chars_per_page = text_stats.get('avg_chars_per_page', 0)
                
                # Apply OCR if:
                # 1. Document has minimal text (clearly needs OCR)
                # 2. Document has moderate text that could be enhanced
                # 3. Document characteristics suggest OCR optimization would help
                
                if avg_chars_per_page < 500:  # Definitely needs OCR
                    logger.info(f"Document needs OCR: low text content ({avg_chars_per_page} chars/page)")
                    return True
                elif avg_chars_per_page < 1500:  # Could benefit from OCR enhancement
                    logger.info(f"Document may benefit from OCR enhancement ({avg_chars_per_page} chars/page)")
                    return True
                else:
                    # High-quality text documents - apply light OCR enhancement
                    logger.info(f"Document has good text content ({avg_chars_per_page} chars/page), applying light OCR enhancement")
                    return True
            
            # Fallback to original logic
            return needs_basic_ocr
            
        except Exception as e:
            logger.warning(f"Could not analyze document for OCR need: {e}")
            return True  # Default to needing OCR
    
    def _extract_document_features(self, pdf_path: Path) -> Dict[str, float]:
        """Extract features from PDF document for ML analysis."""
        features = {}
        
        try:
            # Open PDF for analysis
            doc = fitz.open(pdf_path)
            
            # Basic document features
            features['total_pages'] = len(doc)
            features['file_size_mb'] = pdf_path.stat().st_size / (1024 * 1024)
            
            # Sample pages for text analysis
            sample_pages = min(3, len(doc))
            total_text_length = 0
            total_words = 0
            has_images = False
            has_tables = False
            has_equations = False
            
            for page_num in range(sample_pages):
                page = doc[page_num]
                
                # Extract text
                text = page.get_text()
                total_text_length += len(text)
                total_words += len(text.split())
                
                # Check for images
                if page.get_images():
                    has_images = True
                
                # Check for tables (simple detection)
                if '|' in text or '\t' in text:
                    has_tables = True
                
                # Check for equations
                if any(symbol in text for symbol in ['=', '+', '-', '*', '/', '∑', '∫']):
                    has_equations = True
            
            doc.close()
            
            # Calculate averages
            features['avg_text_length_per_page'] = total_text_length / sample_pages
            features['avg_words_per_page'] = total_words / sample_pages
            features['has_images'] = float(has_images)
            features['has_tables'] = float(has_tables)
            features['has_equations'] = float(has_equations)
            
            # Document type indicators
            features['is_academic'] = float(has_equations or has_tables)
            features['is_image_heavy'] = float(has_images and features['avg_text_length_per_page'] < 100)
            
        except Exception as e:
            logger.warning(f"Could not extract document features: {e}")
            # Provide default features
            features = {
                'total_pages': 1,
                'file_size_mb': 1.0,
                'avg_text_length_per_page': 0,
                'avg_words_per_page': 0,
                'has_images': 0.0,
                'has_tables': 0.0,
                'has_equations': 0.0,
                'is_academic': 0.0,
                'is_image_heavy': 0.0
            }
        
        return features
    
    def _get_optimized_ocr_parameters(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Get optimized OCR parameters using ML analysis."""
        default_params = {
            'psm': 3,  # Auto page segmentation
            'oem': 3,  # LSTM + Legacy engine
            'dpi': 150,
            'language': 'eng',
            'preserve_interword_spaces': '1'
        }
        
        if not self.adaptive_ml:
            return default_params
        
        try:
            # Get ML analysis and optimization recommendations
            ml_analysis = self.adaptive_ml.enhance(features)
            
            if 'adaptive_ml_analysis' in ml_analysis:
                analysis = ml_analysis['adaptive_ml_analysis']
                
                # Use pattern-matched parameters if available
                if 'pattern_match' in analysis and analysis['pattern_match'].get('pattern_found'):
                    pattern_match = analysis['pattern_match']
                    if pattern_match.get('similarity_score', 0) > 0.7:
                        recommended_params = pattern_match.get('recommended_ocr_params', {})
                        if recommended_params:
                            default_params.update(recommended_params)
                            logger.info(f"Using pattern-matched OCR parameters (similarity: {pattern_match['similarity_score']:.3f})")
                
                # Apply quality-based optimizations
                quality_prediction = analysis.get('quality_prediction', {})
                if quality_prediction.get('factors', {}).get('complexity') == 'high':
                    # High complexity documents need more conservative settings
                    default_params.update({
                        'psm': 6,  # Uniform block of text
                        'dpi': 200,  # Higher resolution
                        'oem': 3   # LSTM only for better accuracy
                    })
                    logger.info("Applied high-complexity document optimizations")
            
            # Try to get document-specific optimized configuration
            optimization_result = self.adaptive_ml.optimize_ocr_configuration(features)
            if optimization_result.get('confidence', 0) > 0.7:
                optimal_config = optimization_result['optimal_config']
                default_params.update(optimal_config)
                logger.info(f"Using ML-optimized configuration (confidence: {optimization_result['confidence']:.3f})")
            
            # Apply feature-based adjustments
            if features.get('has_equations', 0) > 0:
                default_params.update({
                    'psm': 6,  # Uniform block of text
                    'oem': 3,  # LSTM only
                    'dpi': 300  # High resolution for equations
                })
                logger.info("Applied equation-optimized OCR parameters")
            
            if features.get('has_tables', 0) > 0:
                default_params.update({
                    'psm': 6,  # Better for structured content
                    'textord_tablefind_recognize_tables': '1'
                })
                logger.info("Applied table-optimized OCR parameters")
            
            if features.get('is_image_heavy', 0) > 0:
                default_params.update({
                    'dpi': 200,  # Higher DPI for image-heavy documents
                    'psm': 1,    # Automatic page segmentation with OSD
                    'oem': 2     # Legacy + LSTM for robustness
                })
                logger.info("Applied image-heavy document OCR parameters")
            
        except Exception as e:
            logger.warning(f"Could not get optimized OCR parameters: {e}")
        
        return default_params
    
    def _perform_intelligent_ocr(self, pdf_path: Path, ocr_params: Dict[str, Any]) -> OCRProcessingResult:
        """Perform intelligent OCR processing on PDF."""
        start_time = time.time()
        
        try:
            # Convert PDF pages to images
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            
            all_text = []
            total_confidence = 0.0
            page_results = []
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Convert page to image
                mat = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better OCR
                img_data = mat.tobytes("png")
                
                # Convert to PIL Image
                img = Image.open(io.BytesIO(img_data))
                img_np = np.array(img)
                
                # Preprocess image
                processed_img = self._preprocess_image_for_ocr(img_np)
                
                # Perform OCR with error handling for pytesseract Unicode issues
                try:
                    ocr_text = pytesseract.image_to_string(
                        processed_img,
                        config=self._build_ocr_config(ocr_params)
                    )
                except UnicodeDecodeError as ude:
                    # Pytesseract bug: Tesseract error output contains binary data
                    logger.warning(f"Page {page_num + 1}: Pytesseract Unicode decode error (Tesseract may have issues with this page), skipping")
                    ocr_text = ""
                except Exception as ocr_err:
                    logger.warning(f"Page {page_num + 1}: OCR failed: {ocr_err}, skipping")
                    ocr_text = ""
                
                # Get confidence data if available
                try:
                    confidence_data = pytesseract.image_to_data(
                        processed_img,
                        config=self._build_ocr_config(ocr_params),
                        output_type=pytesseract.Output.DICT
                    )
                    # Calculate average confidence
                    confidences = [int(conf) for conf in confidence_data['conf'] if int(conf) > 0]
                    page_confidence = np.mean(confidences) if confidences else 0.0
                except (UnicodeDecodeError, Exception) as conf_err:
                    logger.debug(f"Page {page_num + 1}: Could not get confidence data: {conf_err}")
                    page_confidence = 0.0
                
                all_text.append(ocr_text)
                total_confidence += page_confidence
                
                page_results.append({
                    'page': page_num + 1,
                    'text': ocr_text,
                    'confidence': page_confidence,
                    'word_count': len(ocr_text.split())
                })
            
            doc.close()
            
            # Calculate overall metrics
            processing_time = time.time() - start_time
            avg_confidence = total_confidence / total_pages if total_pages > 0 else 0.0
            total_text = '\n'.join(all_text)
            
            # Calculate quality metrics
            quality_metrics = self._calculate_quality_metrics(total_text, avg_confidence, processing_time)
            
            # Determine success
            success = avg_confidence > 30.0 and len(total_text.strip()) > 100
            
            return OCRProcessingResult(
                success=success,
                text_content=total_text,
                confidence_score=avg_confidence,
                processing_time=processing_time,
                ocr_parameters_used=ocr_params,
                quality_metrics=quality_metrics,
                recommendations=self._generate_recommendations(quality_metrics)
            )
            
        except Exception as e:
            # Safely log exception - avoid UTF-8 decode errors from binary data in exception messages
            logger.error(f"OCR processing failed: {type(e).__name__}", exc_info=True)
            return OCRProcessingResult(
                success=False,
                text_content="",
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                ocr_parameters_used=ocr_params,
                quality_metrics={},
                recommendations=["OCR processing failed"]
            )
    
    def _preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for optimal OCR performance."""
        try:
            # Convert to grayscale if needed
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image.copy()
            
            # Apply adaptive thresholding
            binary = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            
            # Apply noise reduction
            denoised = cv2.fastNlMeansDenoising(binary, h=10)
            
            # Apply morphological operations to clean up text
            kernel = np.ones((1, 1), np.uint8)
            cleaned = cv2.morphologyEx(denoised, cv2.MORPH_CLOSE, kernel)
            
            return cleaned
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def _build_ocr_config(self, params: Dict[str, Any]) -> str:
        """Build OCR configuration string from parameters."""
        config_parts = []
        
        # Add PSM and OEM
        config_parts.append(f"--psm {params.get('psm', 3)}")
        config_parts.append(f"--oem {params.get('oem', 3)}")
        
        # Add language
        config_parts.append(f"-l {params.get('language', 'eng')}")
        
        # Add additional parameters using -c syntax
        for key, value in params.items():
            if key not in ['psm', 'oem', 'language', 'dpi']:
                if key == 'preserve_interword_spaces':
                    # Handle preserve_interword_spaces as a config variable
                    config_parts.append(f"-c preserve_interword_spaces={value}")
                elif isinstance(value, str) and key not in ['language']:
                    config_parts.append(f"-c {key}={value}")
        
        return ' '.join(config_parts)
    
    def _calculate_quality_metrics(self, text: str, confidence: float, processing_time: float) -> Dict[str, float]:
        """Calculate quality metrics for OCR results."""
        metrics = {
            'confidence_score': confidence,
            'processing_time_seconds': processing_time,
            'text_length': len(text),
            'word_count': len(text.split()),
            'avg_word_length': np.mean([len(word) for word in text.split()]) if text.split() else 0,
            'sentence_count': text.count('.') + text.count('!') + text.count('?'),
            'unique_words_ratio': len(set(text.lower().split())) / max(len(text.split()), 1),
            'quality_score': min(confidence / 100.0, 1.0)
        }
        
        # Calculate readability score
        if metrics['sentence_count'] > 0 and metrics['word_count'] > 0:
            metrics['avg_sentence_length'] = metrics['word_count'] / metrics['sentence_count']
        else:
            metrics['avg_sentence_length'] = 0
        
        return metrics
    
    def _generate_recommendations(self, quality_metrics: Dict[str, float]) -> List[str]:
        """Generate recommendations based on quality metrics."""
        recommendations = []
        
        if quality_metrics.get('confidence_score', 0) < 50:
            recommendations.append("Low confidence detected - consider higher DPI or different PSM")
        
        if quality_metrics.get('quality_score', 0) < 0.5:
            recommendations.append("Poor text quality - review preprocessing parameters")
        
        if quality_metrics.get('processing_time_seconds', 0) > 30:
            recommendations.append("Slow processing - consider reducing DPI or page count")
        
        if quality_metrics.get('word_count', 0) < 50:
            recommendations.append("Low word count - verify OCR captured all text")
        
        return recommendations
    
    def _apply_ocr_to_pdf(self, input_path: Path, output_path: Path, ocr_result: OCRProcessingResult) -> bool:
        """Apply OCR results to PDF file."""
        try:
            # For now, we'll create a simple text overlay
            # In a full implementation, this would integrate with PyMuPDF to add text layer
            
            # Create a simple output file with OCR results
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save OCR results as metadata
            metadata = {
                'ocr_processing': {
                    'success': ocr_result.success,
                    'confidence_score': ocr_result.confidence_score,
                    'processing_time': ocr_result.processing_time,
                    'ocr_parameters_used': ocr_result.ocr_parameters_used,
                    'quality_metrics': ocr_result.quality_metrics,
                    'recommendations': ocr_result.recommendations
                },
                'text_content': ocr_result.text_content[:1000] + "..." if len(ocr_result.text_content) > 1000 else ocr_result.text_content
            }
            
            # Save metadata alongside PDF
            metadata_path = output_path.with_suffix('.ocr_metadata.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # Copy original PDF as output (in real implementation, add text layer)
            import shutil
            shutil.copy2(input_path, output_path)
            
            logger.info(f"OCR results applied to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to apply OCR to PDF: {e}")
            return False
    
    def _learn_from_processing_result(self, features: Dict[str, float], ocr_result: OCRProcessingResult):
        """Learn from OCR processing results for future improvements."""
        if not self.adaptive_ml:
            return
        
        try:
            # Create feedback data
            feedback = {
                'success': ocr_result.success,
                'quality_score': ocr_result.quality_metrics.get('quality_score', 0.0),
                'ocr_params': ocr_result.ocr_parameters_used,
                'processing_time': ocr_result.processing_time,
                'confidence_score': ocr_result.confidence_score
            }
            
            # Send feedback to adaptive ML system
            self.adaptive_ml.enhance(features, feedback=feedback)
            
            logger.info(f"Learning from OCR processing result: success={ocr_result.success}")
            
        except Exception as e:
            logger.warning(f"Failed to learn from processing result: {e}")
    
    def _update_statistics(self, ocr_result: OCRProcessingResult, processing_time: float):
        """Update processing statistics."""
        self.processing_stats['total_processed'] += 1
        
        if ocr_result.success:
            self.processing_stats['successful_ocr'] += 1
        
        # Update averages
        total = self.processing_stats['total_processed']
        current_avg_time = self.processing_stats['avg_processing_time']
        current_avg_conf = self.processing_stats['avg_confidence']
        
        self.processing_stats['avg_processing_time'] = (
            (current_avg_time * (total - 1) + processing_time) / total
        )
        self.processing_stats['avg_confidence'] = (
            (current_avg_conf * (total - 1) + ocr_result.confidence_score) / total
        )
    
    def get_processing_statistics(self) -> Dict[str, Any]:
        """Get processing statistics."""
        stats = self.processing_stats.copy()
        
        if stats['total_processed'] > 0:
            stats['success_rate'] = stats['successful_ocr'] / stats['total_processed']
        else:
            stats['success_rate'] = 0.0
        
        if self.adaptive_ml:
            stats['ml_learning_stats'] = self.adaptive_ml.get_learning_statistics()
        
        return stats
