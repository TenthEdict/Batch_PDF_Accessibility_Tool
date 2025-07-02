#!/usr/bin/env python3
"""
Document repository for abstracting document data access operations.

This module provides repository patterns for working with documents,
abstracting the underlying storage and access mechanisms.
"""

import abc
import logging
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class DocumentInfo:
    """Information about a document."""

    path: Path
    name: str
    size: int
    extension: str
    created_at: datetime
    modified_at: datetime
    exists: bool = True
    metadata: Optional[Dict[str, Any]] = None

    @classmethod
    def from_path(cls, path: Union[str, Path]) -> "DocumentInfo":
        """Create DocumentInfo from a file path."""
        path = Path(path)

        if not path.exists():
            return cls(
                path=path,
                name=path.name,
                size=0,
                extension=path.suffix,
                created_at=datetime.now(),
                modified_at=datetime.now(),
                exists=False,
            )

        stat = path.stat()
        return cls(
            path=path,
            name=path.name,
            size=stat.st_size,
            extension=path.suffix,
            created_at=datetime.fromtimestamp(stat.st_ctime),
            modified_at=datetime.fromtimestamp(stat.st_mtime),
            exists=True,
        )


@dataclass
class DocumentFilter:
    """Filter criteria for document queries."""

    extensions: Optional[List[str]] = None
    min_size: Optional[int] = None
    max_size: Optional[int] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    modified_after: Optional[datetime] = None
    modified_before: Optional[datetime] = None
    name_pattern: Optional[str] = None


class DocumentRepository(abc.ABC):
    """
    Abstract repository for document data access operations.

    This interface defines the contract for document storage and retrieval
    operations, allowing different implementations for various storage backends.
    """

    @abc.abstractmethod
    def get_document(self, path: Union[str, Path]) -> Optional[DocumentInfo]:
        """
        Get document information by path.

        Args:
            path: Document path

        Returns:
            DocumentInfo if found, None otherwise
        """
        pass

    @abc.abstractmethod
    def list_documents(
        self,
        directory: Union[str, Path],
        filter_criteria: Optional[DocumentFilter] = None,
        recursive: bool = False,
    ) -> List[DocumentInfo]:
        """
        List documents in a directory.

        Args:
            directory: Directory to search
            filter_criteria: Optional filter criteria
            recursive: Whether to search recursively

        Returns:
            List of DocumentInfo objects
        """
        pass

    @abc.abstractmethod
    def save_document(
        self,
        source_path: Union[str, Path],
        target_path: Union[str, Path],
        copy: bool = True,
    ) -> bool:
        """
        Save a document to the repository.

        Args:
            source_path: Source document path
            target_path: Target path in repository
            copy: Whether to copy (True) or move (False) the document

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def delete_document(self, path: Union[str, Path]) -> bool:
        """
        Delete a document from the repository.

        Args:
            path: Document path to delete

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def exists(self, path: Union[str, Path]) -> bool:
        """
        Check if a document exists.

        Args:
            path: Document path to check

        Returns:
            True if document exists, False otherwise
        """
        pass

    @abc.abstractmethod
    def get_size(self, path: Union[str, Path]) -> int:
        """
        Get document size in bytes.

        Args:
            path: Document path

        Returns:
            Document size in bytes, -1 if not found
        """
        pass

    @abc.abstractmethod
    def create_directory(self, path: Union[str, Path]) -> bool:
        """
        Create a directory in the repository.

        Args:
            path: Directory path to create

        Returns:
            True if successful, False otherwise
        """
        pass


class FileSystemDocumentRepository(DocumentRepository):
    """
    File system implementation of the document repository.

    This implementation stores documents in the local file system
    and provides standard file operations.
    """

    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the file system document repository.

        Args:
            base_path: Optional base path for relative operations
        """
        self.base_path = Path(base_path) if base_path else None
        self.logger = logging.getLogger(__name__)

    def get_document(self, path: Union[str, Path]) -> Optional[DocumentInfo]:
        """Get document information by path."""
        try:
            resolved_path = self._resolve_path(path)
            if not resolved_path.exists():
                return None

            return DocumentInfo.from_path(resolved_path)

        except Exception as e:
            self.logger.error(f"Error getting document {path}: {e}")
            return None

    def list_documents(
        self,
        directory: Union[str, Path],
        filter_criteria: Optional[DocumentFilter] = None,
        recursive: bool = False,
    ) -> List[DocumentInfo]:
        """List documents in a directory."""
        documents = []

        try:
            resolved_dir = self._resolve_path(directory)
            if not resolved_dir.exists() or not resolved_dir.is_dir():
                return documents

            # Get file pattern
            pattern = "**/*" if recursive else "*"

            for file_path in resolved_dir.glob(pattern):
                if file_path.is_file():
                    doc_info = DocumentInfo.from_path(file_path)

                    # Apply filter criteria
                    if self._matches_filter(doc_info, filter_criteria):
                        documents.append(doc_info)

            self.logger.info(f"Found {len(documents)} documents in {directory}")

        except Exception as e:
            self.logger.error(f"Error listing documents in {directory}: {e}")

        return documents

    def save_document(
        self,
        source_path: Union[str, Path],
        target_path: Union[str, Path],
        copy: bool = True,
    ) -> bool:
        """Save a document to the repository."""
        try:
            source_path = Path(source_path)
            resolved_target = self._resolve_path(target_path)

            if not source_path.exists():
                self.logger.error(f"Source document not found: {source_path}")
                return False

            # Create target directory if needed
            resolved_target.parent.mkdir(parents=True, exist_ok=True)

            # Copy or move the document
            if copy:
                shutil.copy2(source_path, resolved_target)
                operation = "copied"
            else:
                shutil.move(str(source_path), str(resolved_target))
                operation = "moved"

            self.logger.info(f"Successfully {operation} document to {resolved_target}")
            return True

        except Exception as e:
            self.logger.error(
                f"Error saving document {source_path} to {target_path}: {e}"
            )
            return False

    def delete_document(self, path: Union[str, Path]) -> bool:
        """Delete a document from the repository."""
        try:
            resolved_path = self._resolve_path(path)

            if not resolved_path.exists():
                self.logger.warning(f"Document not found for deletion: {path}")
                return True  # Consider it successful if already gone

            if resolved_path.is_file():
                resolved_path.unlink()
                self.logger.info(f"Deleted document: {resolved_path}")
                return True
            else:
                self.logger.error(f"Path is not a file: {resolved_path}")
                return False

        except Exception as e:
            self.logger.error(f"Error deleting document {path}: {e}")
            return False

    def exists(self, path: Union[str, Path]) -> bool:
        """Check if a document exists."""
        try:
            resolved_path = self._resolve_path(path)
            return resolved_path.exists() and resolved_path.is_file()
        except Exception as e:
            self.logger.error(f"Error checking existence of {path}: {e}")
            return False

    def get_size(self, path: Union[str, Path]) -> int:
        """Get document size in bytes."""
        try:
            resolved_path = self._resolve_path(path)
            if resolved_path.exists() and resolved_path.is_file():
                return resolved_path.stat().st_size
            return -1
        except Exception as e:
            self.logger.error(f"Error getting size of {path}: {e}")
            return -1

    def create_directory(self, path: Union[str, Path]) -> bool:
        """Create a directory in the repository."""
        try:
            resolved_path = self._resolve_path(path)
            resolved_path.mkdir(parents=True, exist_ok=True)
            self.logger.info(f"Created directory: {resolved_path}")
            return True
        except Exception as e:
            self.logger.error(f"Error creating directory {path}: {e}")
            return False

    def get_base_path(self) -> Optional[Path]:
        """Get the base path for this repository."""
        return self.base_path

    def set_base_path(self, path: Union[str, Path]) -> None:
        """Set the base path for this repository."""
        self.base_path = Path(path)

    def get_available_space(self) -> Optional[int]:
        """
        Get available disk space in bytes.

        Returns:
            Available space in bytes, None if unable to determine
        """
        try:
            base = self.base_path or Path.cwd()
            stat = shutil.disk_usage(base)
            return stat.free
        except Exception as e:
            self.logger.error(f"Error getting available space: {e}")
            return None

    def _resolve_path(self, path: Union[str, Path]) -> Path:
        """
        Resolve a path relative to the base path.

        Args:
            path: Path to resolve

        Returns:
            Resolved absolute path
        """
        path = Path(path)

        if path.is_absolute():
            return path

        if self.base_path:
            return self.base_path / path

        return path.resolve()

    def _matches_filter(
        self, doc_info: DocumentInfo, filter_criteria: Optional[DocumentFilter]
    ) -> bool:
        """
        Check if document matches filter criteria.

        Args:
            doc_info: Document information to check
            filter_criteria: Filter criteria to apply

        Returns:
            True if document matches filter, False otherwise
        """
        if filter_criteria is None:
            return True

        # Check extensions
        if filter_criteria.extensions:
            if doc_info.extension.lower() not in [
                ext.lower() for ext in filter_criteria.extensions
            ]:
                return False

        # Check size range
        if (
            filter_criteria.min_size is not None
            and doc_info.size < filter_criteria.min_size
        ):
            return False

        if (
            filter_criteria.max_size is not None
            and doc_info.size > filter_criteria.max_size
        ):
            return False

        # Check creation date range
        if (
            filter_criteria.created_after
            and doc_info.created_at < filter_criteria.created_after
        ):
            return False

        if (
            filter_criteria.created_before
            and doc_info.created_at > filter_criteria.created_before
        ):
            return False

        # Check modification date range
        if (
            filter_criteria.modified_after
            and doc_info.modified_at < filter_criteria.modified_after
        ):
            return False

        if (
            filter_criteria.modified_before
            and doc_info.modified_at > filter_criteria.modified_before
        ):
            return False

        # Check name pattern
        if filter_criteria.name_pattern:
            import fnmatch

            if not fnmatch.fnmatch(
                doc_info.name.lower(), filter_criteria.name_pattern.lower()
            ):
                return False

        return True
