"""
Accessibility Training Module

This module provides machine learning training capabilities for PDF accessibility compliance.
Extends the existing Phase 2B ML infrastructure to train models for WCAG, PDF-UA, and ADA compliance.

Components:
- AccessibilityDataExtractor: Extract tag trees and compliance patterns from training data
- AccessibilityFeatureEngineer: Create accessibility-specific feature vectors
- AccessibilityModelTrainer: Train ML models for compliance prediction
- ComplianceValidator: WCAG/PDF-UA/ADA validation framework

Integration:
- Leverages existing AdaptiveMLEnhancer infrastructure
- Extends FAISS vector database with accessibility dimensions
- Integrates with hierarchical caching system for pattern storage
"""

from .accessibility_data_extractor import AccessibilityDataExtractor
from .accessibility_feature_engineer import AccessibilityFeatureEngineer
from .accessibility_model_trainer import AccessibilityModelTrainer
from .compliance_validator import ComplianceValidator

__all__ = [
    'AccessibilityDataExtractor',
    'AccessibilityFeatureEngineer', 
    'AccessibilityModelTrainer',
    'ComplianceValidator'
]
