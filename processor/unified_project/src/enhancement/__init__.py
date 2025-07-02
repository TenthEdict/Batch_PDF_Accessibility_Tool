"""
Enhancement module for document accessibility improvements.

This module provides a unified enhancement pipeline that orchestrates
multiple enhancers to improve document accessibility.
"""

from .pipeline import EnhancementPipeline, EnhancementConfig, EnhancementOrchestrator

__all__ = ["EnhancementPipeline", "EnhancementConfig", "EnhancementOrchestrator"]
