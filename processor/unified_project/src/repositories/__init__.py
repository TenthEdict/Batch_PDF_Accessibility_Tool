#!/usr/bin/env python3
"""
Repository pattern implementation for data access abstraction.

This module provides repository interfaces and implementations that abstract
data access operations and provide a clean interface for working with
documents, metadata, and configuration data.
"""

from .document_repository import DocumentRepository, FileSystemDocumentRepository
from .metadata_repository import MetadataRepository, FileBasedMetadataRepository
from .config_repository import ConfigRepository, YamlConfigRepository

__all__ = [
    'DocumentRepository',
    'FileSystemDocumentRepository',
    'MetadataRepository', 
    'FileBasedMetadataRepository',
    'ConfigRepository',
    'YamlConfigRepository'
]