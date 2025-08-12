#!/usr/bin/env python3
"""
Adaptive ML Enhancement Module

This module provides machine learning-enhanced document processing with:
- Document-level OCR configuration optimization
- Similarity-based pattern matching for optimal settings
- Continuous learning from processing results
- Document feature analysis and clustering
- Persistent knowledge base for configuration recommendations

Features:
- Document similarity analysis using feature vectors
- OCR configuration testing and optimization
- Quality-based learning from processing outcomes
- Pattern storage and retrieval for similar documents
- Adaptive parameter tuning based on document characteristics
"""

import logging
import json
import pickle
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, asdict
import time
import tempfile

# ML and data processing imports
try:
    import numpy as np
    import pandas as pd
    from sklearn.metrics.pairwise import cosine_similarity
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.neighbors import NearestNeighbors
    import joblib
    ML_DEPS_AVAILABLE = True
except ImportError as e:
    ML_DEPS_AVAILABLE = False
    np = None
    pd = None

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


@dataclass
class DocumentProfile:
    """Document profile with features and optimal configurations."""
    document_id: str
    features: Dict[str, float]
    optimal_ocr_config: Dict[str, Any]
    quality_metrics: Dict[str, float]
    processing_history: List[Dict[str, Any]]
    created_at: float
    updated_at: float
    success_count: int = 0
    total_attempts: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this configuration."""
        return self.success_count / max(self.total_attempts, 1)

    @property
    def confidence_score(self) -> float:
        """Calculate confidence in this configuration."""
        # Confidence based on success rate and number of attempts
        base_confidence = self.success_rate
        attempt_factor = min(self.total_attempts / 10.0, 1.0)  # More attempts = higher confidence
        return base_confidence * (0.5 + 0.5 * attempt_factor)


@dataclass
class OCRConfigurationTest:
    """Results from testing an OCR configuration."""
    config: Dict[str, Any]
    quality_score: float
    confidence_score: float
    processing_time: float
    text_length: int
    success: bool
    error_message: Optional[str] = None


class AdaptiveMLEnhancer(EnhancerBase):
    """
    Adaptive ML enhancer providing document-level learning and optimization.
    
    Capabilities:
    - Document similarity analysis
    - OCR configuration optimization
    - Pattern-based learning and recommendation
    - Continuous improvement through feedback
    """
    
    def __init__(self, component_name: str = "adaptive_ml_enhancer", environment: Optional[str] = None):
        """Initialize adaptive ML enhancer."""
        super().__init__(component_name, environment)
        
        if not ML_DEPS_AVAILABLE:
            raise ImportError("ML dependencies not available. Install with: pip install epubs-accessibility[ml]")
        
        # Knowledge base storage
        self.knowledge_base_dir = Path.home() / ".epubs" / "ml_knowledge"
        self.knowledge_base_dir.mkdir(parents=True, exist_ok=True)
        
        # Configuration files
        self.profiles_file = self.knowledge_base_dir / "document_profiles.pkl"
        self.scaler_file = self.knowledge_base_dir / "feature_scaler.pkl"
        self.similarity_model_file = self.knowledge_base_dir / "similarity_model.pkl"
        
        # ML components
        self.feature_scaler = None
        self.similarity_model = None
        self.document_profiles: Dict[str, DocumentProfile] = {}
        
        # OCR configuration options for testing
        self.ocr_config_options = {
            'psm': [3, 6, 7, 8, 11, 13],  # Page segmentation modes
            'oem': [1, 2, 3],  # OCR engine modes
            'dpi': [150, 200, 300],  # Resolution options
            'preprocessing': ['none', 'adaptive', 'otsu', 'gaussian']
        }
        
        # Learning parameters
        self.similarity_threshold = 0.8
        self.min_quality_threshold = 0.6
        self.max_config_tests = 5  # Maximum OCR configurations to test per document
        
        # Load existing knowledge base
        self._load_knowledge_base()
        
        logger.info("Adaptive ML Enhancer initialized successfully")

    def get_capabilities(self) -> List[str]:
        """Get ML enhancement capabilities."""
        return [
            "document_similarity_analysis",
            "ocr_configuration_optimization", 
            "pattern_based_learning",
            "quality_prediction",
            "adaptive_parameter_tuning",
            "continuous_improvement",
            "document_clustering",
            "configuration_recommendation"
        ]

    def enhance(self, features: Dict[str, float], feedback: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Enhance document processing using ML analysis.
        
        Args:
            features: Document feature vector
            feedback: Optional feedback from previous processing
            
        Returns:
            Dict containing ML analysis and recommendations
        """
        try:
            start_time = time.time()
            
            # Generate document ID from features
            doc_id = self._generate_document_id(features)
            
            # Process feedback if provided
            if feedback:
                self._process_feedback(doc_id, feedback)
            
            # Find similar documents
            similar_docs = self._find_similar_documents(features)
            
            # Get OCR configuration recommendation
            recommended_config = self._recommend_ocr_config(features, similar_docs)
            
            # Generate analysis results
            analysis = {
                'document_id': doc_id,
                'processing_time': time.time() - start_time,
                'similar_documents_found': len(similar_docs),
                'recommended_ocr_config': recommended_config,
                'adaptive_ml_analysis': {
                    'pattern_match': self._analyze_pattern_match(features, similar_docs),
                    'quality_prediction': self._predict_quality(features, recommended_config),
                    'optimization_suggestions': self._generate_optimization_suggestions(features),
                    'learning_confidence': self._calculate_learning_confidence(similar_docs)
                }
            }
            
            # Store document profile for future learning
            if doc_id not in self.document_profiles:
                self._create_document_profile(doc_id, features, recommended_config)
            
            logger.info(f"ML analysis completed for document {doc_id[:8]}...")
            return analysis
            
        except Exception as e:
            logger.error(f"ML enhancement failed: {e}")
            return {'error': str(e), 'fallback_config': self._get_default_ocr_config()}

    def optimize_ocr_configuration(self, features: Dict[str, float], test_sample_path: Optional[Path] = None) -> Dict[str, Any]:
        """
        Optimize OCR configuration for a specific document through testing.
        
        Args:
            features: Document feature vector
            test_sample_path: Optional path to test sample for configuration testing
            
        Returns:
            Dict containing optimal configuration and test results
        """
        try:
            doc_id = self._generate_document_id(features)
            
            # Check if we have a confident recommendation
            similar_docs = self._find_similar_documents(features)
            if similar_docs and similar_docs[0]['confidence'] > 0.8:
                logger.info(f"Using high-confidence recommendation for document {doc_id[:8]}...")
                return {
                    'optimal_config': similar_docs[0]['config'],
                    'confidence': similar_docs[0]['confidence'],
                    'source': 'similar_document_match',
                    'test_performed': False
                }
            
            # Test multiple configurations if we have a test sample
            if test_sample_path and test_sample_path.exists():
                logger.info(f"Testing OCR configurations for document {doc_id[:8]}...")
                test_results = self._test_ocr_configurations(test_sample_path, features)
                
                if test_results:
                    # Find best configuration
                    best_config = max(test_results, key=lambda x: x.quality_score)
                    
                    # Update document profile with test results
                    self._update_document_profile_with_tests(doc_id, features, test_results)
                    
                    return {
                        'optimal_config': best_config.config,
                        'confidence': best_config.quality_score,
                        'source': 'configuration_testing',
                        'test_performed': True,
                        'test_results': [asdict(result) for result in test_results]
                    }
            
            # Fallback to default configuration
            logger.info(f"Using default configuration for document {doc_id[:8]}...")
            return {
                'optimal_config': self._get_default_ocr_config(),
                'confidence': 0.5,
                'source': 'default_fallback',
                'test_performed': False
            }
            
        except Exception as e:
            logger.error(f"OCR configuration optimization failed: {e}")
            return {
                'optimal_config': self._get_default_ocr_config(),
                'confidence': 0.3,
                'source': 'error_fallback',
                'error': str(e)
            }

    def _find_similar_documents(self, features: Dict[str, float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar documents based on feature similarity."""
        if not self.document_profiles:
            return []
        
        try:
            # Convert features to numpy array
            feature_vector = np.array([features.get(key, 0.0) for key in sorted(features.keys())])
            
            # Get all profile feature vectors
            similar_docs = []
            for profile in self.document_profiles.values():
                profile_vector = np.array([profile.features.get(key, 0.0) for key in sorted(features.keys())])
                
                # Calculate similarity
                similarity = cosine_similarity([feature_vector], [profile_vector])[0][0]
                
                if similarity > self.similarity_threshold:
                    similar_docs.append({
                        'document_id': profile.document_id,
                        'similarity': similarity,
                        'config': profile.optimal_ocr_config,
                        'confidence': profile.confidence_score,
                        'success_rate': profile.success_rate,
                        'quality_metrics': profile.quality_metrics
                    })
            
            # Sort by similarity and confidence
            similar_docs.sort(key=lambda x: (x['similarity'], x['confidence']), reverse=True)
            return similar_docs[:top_k]
            
        except Exception as e:
            logger.warning(f"Could not find similar documents: {e}")
            return []

    def _recommend_ocr_config(self, features: Dict[str, float], similar_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recommend OCR configuration based on similar documents and features."""
        # Start with default configuration
        config = self._get_default_ocr_config()
        
        # If we have similar documents, use their best configuration
        if similar_docs:
            best_match = similar_docs[0]
            if best_match['confidence'] > 0.7:
                config.update(best_match['config'])
                logger.info(f"Using configuration from similar document (similarity: {best_match['similarity']:.3f})")
            
        # Apply feature-based adjustments
        config.update(self._apply_feature_based_adjustments(features))
        
        return config

    def _apply_feature_based_adjustments(self, features: Dict[str, float]) -> Dict[str, Any]:
        """Apply OCR configuration adjustments based on document features."""
        adjustments = {}
        
        # Academic documents
        if features.get('is_academic', 0) > 0.5:
            adjustments.update({
                'psm': 6,  # Uniform block of text
                'oem': 3,  # LSTM only
                'preserve_interword_spaces': '1'
            })
        
        # Table-heavy documents
        if features.get('has_tables', 0) > 0.5:
            adjustments.update({
                'psm': 6,  # Better for tables
                'textord_tablefind_recognize_tables': '1'
            })
        
        # Image-heavy documents  
        if features.get('is_image_heavy', 0) > 0.5:
            adjustments.update({
                'dpi': 200,  # Higher resolution
                'psm': 1,    # Automatic page segmentation with OSD
            })
        
        # Equation-heavy documents
        if features.get('has_equations', 0) > 0.5:
            adjustments.update({
                'psm': 6,   # Uniform text block
                'oem': 3,   # LSTM only
                'dpi': 300  # High resolution for equations
            })
        
        return adjustments

    def _test_ocr_configurations(self, test_sample_path: Path, features: Dict[str, float]) -> List[OCRConfigurationTest]:
        """Test multiple OCR configurations on a document sample."""
        results = []
        
        # Generate test configurations based on document features
        test_configs = self._generate_test_configurations(features)
        
        for config in test_configs[:self.max_config_tests]:
            try:
                result = self._test_single_ocr_config(test_sample_path, config)
                results.append(result)
                
                # Early stopping if we find an excellent configuration
                if result.quality_score > 0.9 and result.success:
                    logger.info("Found excellent OCR configuration, stopping tests")
                    break
                    
            except Exception as e:
                logger.warning(f"OCR configuration test failed: {e}")
                
        return results

    def _test_single_ocr_config(self, sample_path: Path, config: Dict[str, Any]) -> OCRConfigurationTest:
        """Test a single OCR configuration on a document sample."""
        start_time = time.time()
        
        try:
            import fitz  # PyMuPDF
            import pytesseract
            from PIL import Image
            import io
            
            # Open PDF and get first page as test sample
            doc = fitz.open(sample_path)
            page = doc[0]  # Test on first page
            
            # Convert page to image for OCR testing
            mat = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom
            img_data = mat.tobytes("png")
            img = Image.open(io.BytesIO(img_data))
            doc.close()
            
            # Build OCR configuration string
            ocr_config = self._build_ocr_config_string(config)
            
            # Perform OCR with the test configuration
            ocr_text = pytesseract.image_to_string(img, config=ocr_config)
            
            # Get detailed OCR data for confidence scoring
            ocr_data = pytesseract.image_to_data(
                img, 
                config=ocr_config,
                output_type=pytesseract.Output.DICT
            )
            
            # Calculate quality metrics
            confidences = [int(conf) for conf in ocr_data['conf'] if int(conf) > 0]
            avg_confidence = np.mean(confidences) if confidences else 0.0
            
            # Calculate text quality score
            quality_score = self._calculate_text_quality_score(ocr_text, avg_confidence)
            
            processing_time = time.time() - start_time
            success = quality_score > 0.5 and len(ocr_text.strip()) > 50
            
            return OCRConfigurationTest(
                config=config,
                quality_score=quality_score,
                confidence_score=avg_confidence / 100.0,  # Normalize to 0-1
                processing_time=processing_time,
                text_length=len(ocr_text),
                success=success
            )
            
        except Exception as e:
            logger.warning(f"OCR configuration test failed: {e}")
            return OCRConfigurationTest(
                config=config,
                quality_score=0.0,
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                text_length=0,
                success=False,
                error_message=str(e)
            )

    def _build_ocr_config_string(self, config: Dict[str, Any]) -> str:
        """Build Tesseract configuration string from config dict."""
        config_parts = []
        
        # Add PSM and OEM
        config_parts.append(f"--psm {config.get('psm', 3)}")
        config_parts.append(f"--oem {config.get('oem', 3)}")
        
        # Add language
        config_parts.append(f"-l {config.get('language', 'eng')}")
        
        # Add other configuration options using -c syntax
        for key, value in config.items():
            if key not in ['psm', 'oem', 'language', 'dpi']:
                if key == 'preserve_interword_spaces':
                    # Handle preserve_interword_spaces as a config variable
                    config_parts.append(f"-c preserve_interword_spaces={value}")
                elif isinstance(value, bool):
                    if value:
                        config_parts.append(f"-c {key}=1")
                else:
                    config_parts.append(f"-c {key}={value}")
        
        return ' '.join(config_parts)

    def _calculate_text_quality_score(self, text: str, confidence: float) -> float:
        """Calculate quality score for OCR text output."""
        if not text.strip():
            return 0.0
        
        # Base score from confidence
        quality = confidence / 100.0
        
        # Text length factor (reward substantial text output)
        text_length = len(text.strip())
        if text_length > 100:
            quality += 0.1
        if text_length > 500:
            quality += 0.1
        
        # Word count factor
        words = text.split()
        if len(words) > 20:
            quality += 0.1
        
        # Character diversity (good OCR should have varied characters)
        unique_chars = len(set(text.lower()))
        if unique_chars > 20:
            quality += 0.1
        
        # Penalize excessive special characters (indicates OCR errors)
        special_char_ratio = sum(1 for c in text if not c.isalnum() and not c.isspace()) / max(len(text), 1)
        if special_char_ratio > 0.3:
            quality -= 0.2
        
        # Reward presence of common English patterns
        if any(pattern in text.lower() for pattern in ['the ', 'and ', 'of ', 'to ', 'in ']):
            quality += 0.1
        
        return max(0.0, min(1.0, quality))

    def _simulate_ocr_quality(self, config: Dict[str, Any]) -> float:
        """Simulate OCR quality based on configuration (for testing purposes)."""
        # Base quality
        quality = 0.6
        
        # PSM adjustments
        psm = config.get('psm', 3)
        if psm in [6, 7, 8]:  # Good for structured text
            quality += 0.2
        elif psm in [3, 11]:  # General purpose
            quality += 0.1
        
        # OEM adjustments
        oem = config.get('oem', 3)
        if oem == 3:  # LSTM only
            quality += 0.15
        elif oem == 2:  # Legacy + LSTM
            quality += 0.1
        
        # DPI adjustments
        dpi = config.get('dpi', 150)
        if 200 <= dpi <= 300:
            quality += 0.1
        elif dpi > 300:
            quality -= 0.05  # Too high can be counterproductive
        
        # Add some randomness
        quality += np.random.normal(0, 0.1)
        
        return max(0, min(1, quality))

    def _generate_test_configurations(self, features: Dict[str, float]) -> List[Dict[str, Any]]:
        """Generate test configurations based on document features."""
        configs = []
        
        # Base configuration
        base_config = self._get_default_ocr_config()
        configs.append(base_config)
        
        # Academic document configurations
        if features.get('is_academic', 0) > 0.5:
            configs.extend([
                {**base_config, 'psm': 6, 'oem': 3, 'dpi': 200},
                {**base_config, 'psm': 7, 'oem': 3, 'dpi': 250},
                {**base_config, 'psm': 8, 'oem': 3, 'dpi': 300}
            ])
        
        # Table-heavy configurations
        if features.get('has_tables', 0) > 0.5:
            configs.extend([
                {**base_config, 'psm': 6, 'textord_tablefind_recognize_tables': '1'},
                {**base_config, 'psm': 11, 'textord_tablefind_recognize_tables': '1'}
            ])
        
        # Image-heavy configurations
        if features.get('is_image_heavy', 0) > 0.5:
            configs.extend([
                {**base_config, 'psm': 1, 'dpi': 200},
                {**base_config, 'psm': 3, 'dpi': 300, 'oem': 2}
            ])
        
        return configs

    def _get_default_ocr_config(self) -> Dict[str, Any]:
        """Get default OCR configuration."""
        return {
            'psm': 3,
            'oem': 3,
            'dpi': 150,
            'language': 'eng',
            'preserve_interword_spaces': '1'
        }

    def _generate_document_id(self, features: Dict[str, float]) -> str:
        """Generate unique document ID from features."""
        feature_str = json.dumps(features, sort_keys=True)
        return hashlib.md5(feature_str.encode()).hexdigest()

    def _create_document_profile(self, doc_id: str, features: Dict[str, float], config: Dict[str, Any]):
        """Create new document profile."""
        profile = DocumentProfile(
            document_id=doc_id,
            features=features,
            optimal_ocr_config=config,
            quality_metrics={},
            processing_history=[],
            created_at=time.time(),
            updated_at=time.time()
        )
        
        self.document_profiles[doc_id] = profile
        self._save_knowledge_base()

    def _process_feedback(self, doc_id: str, feedback: Dict[str, Any]):
        """Process feedback from OCR processing results."""
        if doc_id not in self.document_profiles:
            return
        
        profile = self.document_profiles[doc_id]
        profile.total_attempts += 1
        
        if feedback.get('success', False):
            profile.success_count += 1
        
        # Update quality metrics
        if 'quality_score' in feedback:
            profile.quality_metrics['latest_quality'] = feedback['quality_score']
        
        # Add to processing history
        profile.processing_history.append({
            'timestamp': time.time(),
            'feedback': feedback
        })
        
        profile.updated_at = time.time()
        self._save_knowledge_base()

    def _update_document_profile_with_tests(self, doc_id: str, features: Dict[str, float], test_results: List[OCRConfigurationTest]):
        """Update document profile with OCR configuration test results."""
        if test_results:
            best_result = max(test_results, key=lambda x: x.quality_score)
            
            if doc_id not in self.document_profiles:
                self._create_document_profile(doc_id, features, best_result.config)
            
            profile = self.document_profiles[doc_id]
            profile.optimal_ocr_config = best_result.config
            profile.quality_metrics.update({
                'best_quality_score': best_result.quality_score,
                'best_confidence_score': best_result.confidence_score,
                'test_count': len(test_results)
            })
            profile.updated_at = time.time()
            
            self._save_knowledge_base()

    def _analyze_pattern_match(self, features: Dict[str, float], similar_docs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze pattern matching results."""
        if not similar_docs:
            return {'pattern_found': False}
        
        best_match = similar_docs[0]
        return {
            'pattern_found': True,
            'similarity_score': best_match['similarity'],
            'confidence': best_match['confidence'],
            'recommended_ocr_params': best_match['config'],
            'success_rate': best_match['success_rate']
        }

    def _predict_quality(self, features: Dict[str, float], config: Dict[str, Any]) -> Dict[str, Any]:
        """Predict processing quality based on features and configuration."""
        # Simple quality prediction based on feature analysis
        predicted_quality = 0.7  # Base prediction
        
        # Adjust based on document characteristics
        if features.get('is_academic', 0) > 0.5:
            predicted_quality += 0.1
        if features.get('has_tables', 0) > 0.5:
            predicted_quality -= 0.1  # Tables are harder
        if features.get('is_image_heavy', 0) > 0.5:
            predicted_quality -= 0.2  # Images are challenging
        
        return {
            'predicted_quality_score': max(0, min(1, predicted_quality)),
            'confidence_interval': [predicted_quality - 0.1, predicted_quality + 0.1],
            'factors': {
                'document_type': 'academic' if features.get('is_academic', 0) > 0.5 else 'general',
                'complexity': 'high' if features.get('has_tables', 0) + features.get('has_equations', 0) > 1 else 'medium'
            }
        }

    def _generate_optimization_suggestions(self, features: Dict[str, float]) -> List[str]:
        """Generate optimization suggestions based on document features."""
        suggestions = []
        
        if features.get('has_equations', 0) > 0.5:
            suggestions.append("Consider using higher DPI (300) for better equation recognition")
        
        if features.get('has_tables', 0) > 0.5:
            suggestions.append("Enable table recognition for improved structure detection")
        
        if features.get('is_image_heavy', 0) > 0.5:
            suggestions.append("Use automatic page segmentation with orientation detection")
        
        if features.get('total_pages', 1) > 50:
            suggestions.append("Consider parallel processing for large documents")
        
        return suggestions

    def _calculate_learning_confidence(self, similar_docs: List[Dict[str, Any]]) -> float:
        """Calculate confidence in learning recommendations."""
        if not similar_docs:
            return 0.0
        
        # Average confidence weighted by similarity
        total_weight = sum(doc['similarity'] for doc in similar_docs)
        if total_weight == 0:
            return 0.0
        
        weighted_confidence = sum(
            doc['confidence'] * doc['similarity'] for doc in similar_docs
        ) / total_weight
        
        return weighted_confidence

    def _load_knowledge_base(self):
        """Load existing knowledge base from disk."""
        try:
            if self.profiles_file.exists():
                with open(self.profiles_file, 'rb') as f:
                    self.document_profiles = pickle.load(f)
                logger.info(f"Loaded {len(self.document_profiles)} document profiles")
            
            if self.scaler_file.exists():
                self.feature_scaler = joblib.load(self.scaler_file)
                
            if self.similarity_model_file.exists():
                self.similarity_model = joblib.load(self.similarity_model_file)
                
        except Exception as e:
            logger.warning(f"Could not load knowledge base: {e}")
            self.document_profiles = {}

    def _save_knowledge_base(self):
        """Save knowledge base to disk."""
        try:
            with open(self.profiles_file, 'wb') as f:
                pickle.dump(self.document_profiles, f)
            
            if self.feature_scaler:
                joblib.dump(self.feature_scaler, self.scaler_file)
                
            if self.similarity_model:
                joblib.dump(self.similarity_model, self.similarity_model_file)
                
        except Exception as e:
            logger.warning(f"Could not save knowledge base: {e}")

    def get_learning_statistics(self) -> Dict[str, Any]:
        """Get statistics about the learning system."""
        total_profiles = len(self.document_profiles)
        successful_profiles = sum(1 for p in self.document_profiles.values() if p.success_rate > 0.5)
        
        avg_confidence = np.mean([p.confidence_score for p in self.document_profiles.values()]) if self.document_profiles else 0.0
        avg_success_rate = np.mean([p.success_rate for p in self.document_profiles.values()]) if self.document_profiles else 0.0
        
        return {
            'total_document_profiles': total_profiles,
            'successful_profiles': successful_profiles,
            'average_confidence': avg_confidence,
            'average_success_rate': avg_success_rate,
            'knowledge_base_size_mb': self._get_knowledge_base_size(),
            'last_updated': max([p.updated_at for p in self.document_profiles.values()]) if self.document_profiles else 0
        }

    def _get_knowledge_base_size(self) -> float:
        """Get knowledge base size in MB."""
        total_size = 0
        for file_path in [self.profiles_file, self.scaler_file, self.similarity_model_file]:
            if file_path.exists():
                total_size += file_path.stat().st_size
        return total_size / (1024 * 1024)
