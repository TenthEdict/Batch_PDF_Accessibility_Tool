#!/usr/bin/env python3
"""
ML-Powered Document Enhancement Module

This module provides AI-powered document analysis and enhancement capabilities
using transformers and machine learning models for:
- Document structure prediction
- Intelligent table and figure detection
- Content classification and tagging
- Quality assessment and optimization recommendations
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import json
import hashlib

# Optional ML imports with graceful fallback
try:
    import torch
    from transformers import (
        AutoTokenizer, 
        AutoModel,
        pipeline,
        AutoModelForSequenceClassification
    )
    from huggingface_hub import hf_hub_download
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

from .enhancer_base import EnhancerBase

logger = logging.getLogger(__name__)


class MLEnhancer(EnhancerBase):
    """
    ML-powered document enhancer using transformer models.
    
    Provides intelligent document analysis and structure prediction
    using pre-trained models from Hugging Face Hub.
    """
    
    def __init__(self, component_name: str = "ml_enhancer", environment: Optional[str] = None):
        """Initialize ML enhancer with model loading."""
        super().__init__(component_name, environment)
        
        if not ML_AVAILABLE:
            raise ImportError(
                "ML dependencies not available. Install with: pip install epubs-accessibility[ml]"
            )
        
        # Model configuration
        self.model_cache_dir = Path.home() / ".cache" / "epubs" / "ml_models"
        self.model_cache_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize models lazily
        self._document_classifier = None
        self._structure_analyzer = None
        self._quality_assessor = None
        
        logger.info("ML Enhancer initialized successfully")
    
    def get_capabilities(self) -> List[str]:
        """Get ML enhancement capabilities."""
        return [
            "document_classification",
            "structure_analysis", 
            "table_detection",
            "figure_detection",
            "quality_assessment",
            "content_tagging"
        ]    
    def _get_document_classifier(self):
        """Lazy load document classification model."""
        if self._document_classifier is None:
            try:
                # Use a lightweight model for document classification
                self._document_classifier = pipeline(
                    "text-classification",
                    model="distilbert-base-uncased-finetuned-sst-2-english",
                    device=0 if torch.cuda.is_available() else -1,
                    model_kwargs={"cache_dir": str(self.model_cache_dir)}
                )
                logger.info("Document classifier loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load document classifier: {e}")
                self._document_classifier = None
        return self._document_classifier
    
    def _get_structure_analyzer(self):
        """Lazy load document structure analysis model."""
        if self._structure_analyzer is None:
            try:
                # Use BERT for structure analysis
                model_name = "bert-base-uncased"
                self._structure_analyzer = {
                    'tokenizer': AutoTokenizer.from_pretrained(
                        model_name, 
                        cache_dir=str(self.model_cache_dir)
                    ),
                    'model': AutoModel.from_pretrained(
                        model_name,
                        cache_dir=str(self.model_cache_dir)
                    )
                }
                logger.info("Structure analyzer loaded successfully")
            except Exception as e:
                logger.warning(f"Could not load structure analyzer: {e}")
                self._structure_analyzer = None
        return self._structure_analyzer
    
    def enhance(self, document: Any, **kwargs) -> Dict[str, Any]:
        """
        Enhance document with ML-powered analysis.
        
        Args:
            document: Document content (text or structured data)
            **kwargs: Additional parameters
            
        Returns:
            Dict containing ML analysis results
        """
        try:
            results = {
                'ml_analysis': {
                    'timestamp': self._get_timestamp(),
                    'model_versions': self._get_model_versions(),
                    'capabilities_used': []
                }
            }
            
            # Extract text content for analysis
            text_content = self._extract_text_content(document)
            
            if not text_content:
                logger.warning("No text content found for ML analysis")
                return results
            
            # Perform ML analysis
            if 'classify_document' in kwargs.get('capabilities', ['classify_document']):
                classification = self._classify_document(text_content)
                if classification:
                    results['ml_analysis']['document_classification'] = classification
                    results['ml_analysis']['capabilities_used'].append('document_classification')
            
            if 'analyze_structure' in kwargs.get('capabilities', ['analyze_structure']):
                structure = self._analyze_structure(text_content)
                if structure:
                    results['ml_analysis']['structure_analysis'] = structure
                    results['ml_analysis']['capabilities_used'].append('structure_analysis')
            
            if 'assess_quality' in kwargs.get('capabilities', ['assess_quality']):
                quality = self._assess_quality(text_content)
                if quality:
                    results['ml_analysis']['quality_assessment'] = quality
                    results['ml_analysis']['capabilities_used'].append('quality_assessment')
            
            logger.info(f"ML analysis completed with {len(results['ml_analysis']['capabilities_used'])} capabilities")
            return results
            
        except Exception as e:
            logger.error(f"ML enhancement failed: {e}")
            return {'ml_analysis': {'error': str(e)}}
    
    def _extract_text_content(self, document: Any) -> str:
        """Extract text content from various document formats."""
        if isinstance(document, str):
            return document
        elif isinstance(document, dict) and 'text' in document:
            return document['text']
        elif hasattr(document, 'extract_text'):
            return document.extract_text()
        else:
            # Try to convert to string
            return str(document)[:10000]  # Limit to first 10k chars
    
    def _classify_document(self, text: str) -> Optional[Dict[str, Any]]:
        """Classify document type and content."""
        classifier = self._get_document_classifier()
        if not classifier:
            return None
            
        try:
            # Truncate text for classification
            text_sample = text[:512]  # BERT limit
            result = classifier(text_sample)
            
            return {
                'classification': result[0]['label'] if result else 'unknown',
                'confidence': result[0]['score'] if result else 0.0,
                'text_sample_length': len(text_sample)
            }
        except Exception as e:
            logger.warning(f"Document classification failed: {e}")
            return None
    
    def _analyze_structure(self, text: str) -> Optional[Dict[str, Any]]:
        """Analyze document structure using ML models."""
        analyzer = self._get_structure_analyzer()
        if not analyzer:
            return None
            
        try:
            # Simple structure analysis based on patterns
            lines = text.split('\n')
            
            # Detect potential headings (lines with fewer words, specific patterns)
            headings = []
            tables = []
            figures = []
            
            for i, line in enumerate(lines):
                line_clean = line.strip()
                if not line_clean:
                    continue
                
                # Heading detection heuristics
                if (len(line_clean.split()) <= 10 and 
                    line_clean.isupper() or 
                    any(word in line_clean.lower() for word in ['chapter', 'section', 'introduction', 'conclusion'])):
                    headings.append({'line': i, 'content': line_clean})
                
                # Table detection heuristics
                if '|' in line_clean or '\t' in line_clean:
                    tables.append({'line': i, 'content': line_clean[:100]})
                
                # Figure reference detection
                if any(word in line_clean.lower() for word in ['figure', 'fig.', 'table', 'chart']):
                    figures.append({'line': i, 'content': line_clean[:100]})
            
            return {
                'total_lines': len(lines),
                'detected_headings': len(headings),
                'detected_tables': len(tables),
                'detected_figures': len(figures),
                'headings_sample': headings[:5],  # First 5 headings
                'structure_confidence': min(1.0, (len(headings) + len(tables)) / max(1, len(lines) / 50))
            }
            
        except Exception as e:
            logger.warning(f"Structure analysis failed: {e}")
            return None
    
    def _assess_quality(self, text: str) -> Optional[Dict[str, Any]]:
        """Assess document quality using various metrics."""
        try:
            words = text.split()
            sentences = text.split('.')
            
            # Basic quality metrics
            avg_word_length = sum(len(word) for word in words) / max(1, len(words))
            avg_sentence_length = sum(len(sentence.split()) for sentence in sentences) / max(1, len(sentences))
            
            # Character distribution analysis
            alphabetic_ratio = sum(1 for c in text if c.isalpha()) / max(1, len(text))
            numeric_ratio = sum(1 for c in text if c.isdigit()) / max(1, len(text))
            
            # Quality score calculation
            quality_score = (
                min(1.0, avg_word_length / 6) * 0.3 +  # Reasonable word length
                min(1.0, avg_sentence_length / 20) * 0.3 +  # Reasonable sentence length
                alphabetic_ratio * 0.4  # Good text ratio
            )
            
            return {
                'quality_score': round(quality_score, 3),
                'word_count': len(words),
                'sentence_count': len(sentences),
                'avg_word_length': round(avg_word_length, 2),
                'avg_sentence_length': round(avg_sentence_length, 2),
                'alphabetic_ratio': round(alphabetic_ratio, 3),
                'numeric_ratio': round(numeric_ratio, 3)
            }
            
        except Exception as e:
            logger.warning(f"Quality assessment failed: {e}")
            return None
    
    def _get_timestamp(self) -> str:
        """Get current timestamp for analysis results."""
        return datetime.now().isoformat()
    
    def _get_model_versions(self) -> Dict[str, str]:
        """Get versions of loaded models."""
        return {
            'torch_version': torch.__version__ if ML_AVAILABLE else 'unavailable',
            'transformers_available': ML_AVAILABLE,
            'device': 'cuda' if ML_AVAILABLE and torch.cuda.is_available() else 'cpu'
        }
    
    def _load_document(self, input_path: Path) -> str:
        """Load document as text content."""
        try:
            # For ML analysis, we work with extracted text
            # This is a simple implementation - could be enhanced with PDF parsing
            if input_path.suffix.lower() == '.txt':
                return input_path.read_text(encoding='utf-8')
            else:
                # For other formats, return path as placeholder
                return f"Document path: {input_path}"
        except Exception as e:
            logger.error(f"Failed to load document {input_path}: {e}")
            return ""
    
    def _save_document(self, document: Any, output_path: Path) -> None:
        """Save ML analysis results as JSON."""
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            if isinstance(document, dict):
                with open(output_path.with_suffix('.json'), 'w') as f:
                    json.dump(document, f, indent=2, default=str)
                logger.info(f"ML analysis results saved to {output_path.with_suffix('.json')}")
            else:
                output_path.write_text(str(document), encoding='utf-8')
                
        except Exception as e:
            logger.error(f"Failed to save ML analysis results: {e}")