#!/usr/bin/env python3
"""
Domain model module containing core business entities.

This module defines the domain entities that represent the core business
concepts of the ePubs Accessibility Enhancement system.
"""

from .document import Document, DocumentType, DocumentStatus
from .enhancement import (
    Enhancement,
    EnhancementType,
    EnhancementStatus,
    EnhancementCapability,
)
from .validation import ValidationResult, ValidationCheck, ValidationStandard
from .metadata import DocumentMetadata, MetadataField
from .processing import ProcessingJob, ProcessingRequest, ProcessingResult

__all__ = [
    "Document",
    "DocumentType",
    "DocumentStatus",
    "Enhancement",
    "EnhancementType",
    "EnhancementStatus",
    "EnhancementCapability",
    "ValidationResult",
    "ValidationCheck",
    "ValidationStandard",
    "DocumentMetadata",
    "MetadataField",
    "ProcessingJob",
    "ProcessingRequest",
    "ProcessingResult",
]
