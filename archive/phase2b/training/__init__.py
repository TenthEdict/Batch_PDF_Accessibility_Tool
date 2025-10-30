"""
Accessibility Training Module - Phase 1 Implementation

This module provides machine learning training capabilities for PDF accessibility compliance.
Extends the existing Phase 2B ML infrastructure to train models for WCAG, PDF-UA, and ADA compliance.

Phase 1 Components (IMPLEMENTED):
- AccessibilityDataExtractor: Extract tag trees and compliance patterns from training data
- TrainingDataOrganizer: Organize and manage training datasets

Phase 2 Components (PLANNED):
- AccessibilityFeatureEngineer: Create accessibility-specific feature vectors
- AccessibilityModelTrainer: Train ML models for compliance prediction
- ComplianceValidator: WCAG/PDF-UA/ADA validation framework

Integration:
- Leverages existing AdaptiveMLEnhancer infrastructure
- Extends FAISS vector database with accessibility dimensions
- Integrates with hierarchical caching system for pattern storage
"""

# Phase 1 imports (implemented)
from .accessibility_data_extractor import AccessibilityDataExtractor

# Phase 2 imports will be added as components are implemented
# from .accessibility_feature_engineer import AccessibilityFeatureEngineer
# from .accessibility_model_trainer import AccessibilityModelTrainer
# from .compliance_validator import ComplianceValidator

__all__ = [
    'AccessibilityDataExtractor',
    # Phase 2 components will be added here as implemented
    # 'AccessibilityFeatureEngineer', 
    # 'AccessibilityModelTrainer',
    # 'ComplianceValidator'
]
