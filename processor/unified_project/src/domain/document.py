#!/usr/bin/env python3
"""
Document domain entity and related value objects.

This module defines the core Document entity and related business objects
that represent documents in the accessibility enhancement system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid


class DocumentType(Enum):
    """Document type enumeration."""
    PDF = "pdf"
    DOCX = "docx"
    DOC = "doc"
    TXT = "txt"
    HTML = "html"
    EPUB = "epub"
    UNKNOWN = "unknown"
    
    @classmethod
    def from_extension(cls, extension: str) -> 'DocumentType':
        """Get document type from file extension."""
        extension = extension.lower().lstrip('.')
        
        mapping = {
            'pdf': cls.PDF,
            'docx': cls.DOCX,
            'doc': cls.DOC,
            'txt': cls.TXT,
            'html': cls.HTML,
            'htm': cls.HTML,
            'epub': cls.EPUB
        }
        
        return mapping.get(extension, cls.UNKNOWN)


class DocumentStatus(Enum):
    """Document processing status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    ENHANCED = "enhanced"
    VALIDATED = "validated"
    FAILED = "failed"
    ARCHIVED = "archived"


@dataclass(frozen=True)
class DocumentIdentifier:
    """Value object for document identification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def __post_init__(self):
        if not self.id:
            object.__setattr__(self, 'id', str(uuid.uuid4()))


@dataclass
class DocumentContent:
    """Value object for document content information."""
    size_bytes: int
    page_count: Optional[int] = None
    text_content: Optional[str] = None
    has_images: bool = False
    has_tables: bool = False
    has_forms: bool = False
    language: Optional[str] = None
    character_count: Optional[int] = None
    word_count: Optional[int] = None
    
    def __post_init__(self):
        if self.text_content and not self.character_count:
            self.character_count = len(self.text_content)
        
        if self.text_content and not self.word_count:
            self.word_count = len(self.text_content.split())


@dataclass
class DocumentLocation:
    """Value object for document location information."""
    original_path: Path
    current_path: Optional[Path] = None
    backup_path: Optional[Path] = None
    output_path: Optional[Path] = None
    
    def __post_init__(self):
        self.original_path = Path(self.original_path)
        if self.current_path:
            self.current_path = Path(self.current_path)
        if self.backup_path:
            self.backup_path = Path(self.backup_path)
        if self.output_path:
            self.output_path = Path(self.output_path)
    
    @property
    def exists(self) -> bool:
        """Check if the current document location exists."""
        path = self.current_path or self.original_path
        return path.exists()
    
    @property
    def effective_path(self) -> Path:
        """Get the effective path for the document."""
        return self.current_path or self.original_path


@dataclass
class Document:
    """
    Core document entity representing a document in the system.
    
    This is the main aggregate root for document-related operations.
    """
    identifier: DocumentIdentifier
    name: str
    document_type: DocumentType
    location: DocumentLocation
    content: DocumentContent
    status: DocumentStatus = DocumentStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: Optional[Dict[str, Any]] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @classmethod
    def create(cls, 
               path: Union[str, Path],
               name: Optional[str] = None) -> 'Document':
        """
        Create a new document from a file path.
        
        Args:
            path: Path to the document file
            name: Optional custom name (defaults to filename)
            
        Returns:
            New Document instance
        """
        path = Path(path)
        
        if not name:
            name = path.stem
        
        # Determine document type
        doc_type = DocumentType.from_extension(path.suffix)
        
        # Create location
        location = DocumentLocation(original_path=path)
        
        # Create content info
        if path.exists():
            size = path.stat().st_size
        else:
            size = 0
        
        content = DocumentContent(size_bytes=size)
        
        return cls(
            identifier=DocumentIdentifier(),
            name=name,
            document_type=doc_type,
            location=location,
            content=content
        )
    
    def update_status(self, new_status: DocumentStatus) -> None:
        """Update document status and timestamp."""
        self.status = new_status
        self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """Add a tag to the document."""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag from the document."""
        if tag in self.tags:
            self.tags.remove(tag)
            self.updated_at = datetime.now()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update document metadata."""
        if self.metadata is None:
            self.metadata = {}
        
        self.metadata.update(metadata)
        self.updated_at = datetime.now()
    
    def set_output_location(self, output_path: Union[str, Path]) -> None:
        """Set the output location for processed document."""
        self.location.output_path = Path(output_path)
        self.updated_at = datetime.now()
    
    def set_backup_location(self, backup_path: Union[str, Path]) -> None:
        """Set the backup location for original document."""
        self.location.backup_path = Path(backup_path)
        self.updated_at = datetime.now()
    
    def update_content_info(self, 
                           size_bytes: Optional[int] = None,
                           page_count: Optional[int] = None,
                           text_content: Optional[str] = None,
                           **kwargs) -> None:
        """Update document content information."""
        if size_bytes is not None:
            self.content.size_bytes = size_bytes
        
        if page_count is not None:
            self.content.page_count = page_count
        
        if text_content is not None:
            self.content.text_content = text_content
            self.content.character_count = len(text_content)
            self.content.word_count = len(text_content.split())
        
        for key, value in kwargs.items():
            if hasattr(self.content, key):
                setattr(self.content, key, value)
        
        self.updated_at = datetime.now()
    
    def is_supported_type(self) -> bool:
        """Check if document type is supported for processing."""
        return self.document_type != DocumentType.UNKNOWN
    
    def can_be_processed(self) -> bool:
        """Check if document can be processed."""
        return (
            self.is_supported_type() and
            self.location.exists and
            self.status in [DocumentStatus.PENDING, DocumentStatus.FAILED]
        )
    
    def is_processing_complete(self) -> bool:
        """Check if document processing is complete."""
        return self.status in [DocumentStatus.ENHANCED, DocumentStatus.VALIDATED]
    
    def get_file_extension(self) -> str:
        """Get the file extension."""
        return self.location.effective_path.suffix.lower()
    
    def get_file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.content.size_bytes / (1024 * 1024)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            'id': self.identifier.id,
            'name': self.name,
            'type': self.document_type.value,
            'status': self.status.value,
            'original_path': str(self.location.original_path),
            'current_path': str(self.location.current_path) if self.location.current_path else None,
            'output_path': str(self.location.output_path) if self.location.output_path else None,
            'size_bytes': self.content.size_bytes,
            'page_count': self.content.page_count,
            'language': self.content.language,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'metadata': self.metadata,
            'tags': self.tags,
            'notes': self.notes
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Document':
        """Create document from dictionary representation."""
        # Convert datetime strings back to datetime objects
        created_at = datetime.fromisoformat(data['created_at'])
        updated_at = datetime.fromisoformat(data['updated_at'])
        
        # Create identifier
        identifier = DocumentIdentifier(id=data['id'])
        
        # Create location
        location = DocumentLocation(
            original_path=Path(data['original_path']),
            current_path=Path(data['current_path']) if data.get('current_path') else None,
            output_path=Path(data['output_path']) if data.get('output_path') else None
        )
        
        # Create content
        content = DocumentContent(
            size_bytes=data['size_bytes'],
            page_count=data.get('page_count'),
            language=data.get('language')
        )
        
        return cls(
            identifier=identifier,
            name=data['name'],
            document_type=DocumentType(data['type']),
            location=location,
            content=content,
            status=DocumentStatus(data['status']),
            created_at=created_at,
            updated_at=updated_at,
            metadata=data.get('metadata', {}),
            tags=data.get('tags', []),
            notes=data.get('notes')
        )
    
    def __str__(self) -> str:
        """String representation of the document."""
        return f"Document(id={self.identifier.id[:8]}, name='{self.name}', type={self.document_type.value}, status={self.status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the document."""
        return (
            f"Document("
            f"id='{self.identifier.id}', "
            f"name='{self.name}', "
            f"type={self.document_type.value}, "
            f"status={self.status.value}, "
            f"path='{self.location.effective_path}'"
            f")"
        )