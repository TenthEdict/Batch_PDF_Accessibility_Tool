#!/usr/bin/env python3
"""
Metadata repository for abstracting metadata storage operations.

This module provides repository patterns for working with document metadata,
abstracting the underlying storage and access mechanisms.
"""

import abc
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class MetadataRecord:
    """Metadata record with versioning and tracking."""

    document_path: str
    metadata: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    version: int = 1
    source: str = "unknown"
    checksum: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        # Convert datetime objects to ISO strings
        data["created_at"] = self.created_at.isoformat()
        data["updated_at"] = self.updated_at.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MetadataRecord":
        """Create from dictionary."""
        # Convert ISO strings back to datetime objects
        if isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data["updated_at"], str):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        return cls(**data)


class MetadataRepository(abc.ABC):
    """
    Abstract repository for metadata storage operations.

    This interface defines the contract for metadata storage and retrieval
    operations, allowing different implementations for various storage backends.
    """

    @abc.abstractmethod
    def get_metadata(self, document_path: Union[str, Path]) -> Optional[MetadataRecord]:
        """
        Get metadata record for a document.

        Args:
            document_path: Path to the document

        Returns:
            MetadataRecord if found, None otherwise
        """
        pass

    @abc.abstractmethod
    def save_metadata(self, record: MetadataRecord) -> bool:
        """
        Save metadata record.

        Args:
            record: Metadata record to save

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def update_metadata(
        self,
        document_path: Union[str, Path],
        metadata: Dict[str, Any],
        source: str = "update",
    ) -> bool:
        """
        Update metadata for a document.

        Args:
            document_path: Path to the document
            metadata: Metadata to update
            source: Source of the update

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def delete_metadata(self, document_path: Union[str, Path]) -> bool:
        """
        Delete metadata record for a document.

        Args:
            document_path: Path to the document

        Returns:
            True if successful, False otherwise
        """
        pass

    @abc.abstractmethod
    def list_all_metadata(self) -> List[MetadataRecord]:
        """
        Get all metadata records.

        Returns:
            List of all metadata records
        """
        pass

    @abc.abstractmethod
    def search_metadata(self, query: Dict[str, Any]) -> List[MetadataRecord]:
        """
        Search metadata records by criteria.

        Args:
            query: Search criteria

        Returns:
            List of matching metadata records
        """
        pass

    @abc.abstractmethod
    def exists(self, document_path: Union[str, Path]) -> bool:
        """
        Check if metadata exists for a document.

        Args:
            document_path: Path to the document

        Returns:
            True if metadata exists, False otherwise
        """
        pass


class FileBasedMetadataRepository(MetadataRepository):
    """
    File-based implementation of the metadata repository.

    This implementation stores metadata in JSON files alongside documents
    or in a centralized metadata directory.
    """

    def __init__(
        self, storage_path: Optional[Union[str, Path]] = None, centralized: bool = True
    ):
        """
        Initialize the file-based metadata repository.

        Args:
            storage_path: Path where metadata files are stored
            centralized: Whether to store all metadata in one location (True)
                        or alongside each document (False)
        """
        self.storage_path = (
            Path(storage_path) if storage_path else Path.cwd() / ".metadata"
        )
        self.centralized = centralized
        self.logger = logging.getLogger(__name__)

        # Ensure storage directory exists for centralized storage
        if self.centralized:
            self.storage_path.mkdir(parents=True, exist_ok=True)

    def get_metadata(self, document_path: Union[str, Path]) -> Optional[MetadataRecord]:
        """Get metadata record for a document."""
        try:
            metadata_file = self._get_metadata_file_path(document_path)

            if not metadata_file.exists():
                return None

            with open(metadata_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            return MetadataRecord.from_dict(data)

        except Exception as e:
            self.logger.error(f"Error getting metadata for {document_path}: {e}")
            return None

    def save_metadata(self, record: MetadataRecord) -> bool:
        """Save metadata record."""
        try:
            metadata_file = self._get_metadata_file_path(record.document_path)
            metadata_file.parent.mkdir(parents=True, exist_ok=True)

            with open(metadata_file, "w", encoding="utf-8") as f:
                json.dump(record.to_dict(), f, indent=2, ensure_ascii=False)

            self.logger.info(f"Saved metadata for {record.document_path}")
            return True

        except Exception as e:
            self.logger.error(f"Error saving metadata for {record.document_path}: {e}")
            return False

    def update_metadata(
        self,
        document_path: Union[str, Path],
        metadata: Dict[str, Any],
        source: str = "update",
    ) -> bool:
        """Update metadata for a document."""
        try:
            document_path = str(document_path)

            # Get existing record or create new one
            existing_record = self.get_metadata(document_path)

            if existing_record:
                # Update existing record
                existing_record.metadata.update(metadata)
                existing_record.updated_at = datetime.now()
                existing_record.version += 1
                existing_record.source = source
                record = existing_record
            else:
                # Create new record
                record = MetadataRecord(
                    document_path=document_path,
                    metadata=metadata,
                    created_at=datetime.now(),
                    updated_at=datetime.now(),
                    version=1,
                    source=source,
                )

            return self.save_metadata(record)

        except Exception as e:
            self.logger.error(f"Error updating metadata for {document_path}: {e}")
            return False

    def delete_metadata(self, document_path: Union[str, Path]) -> bool:
        """Delete metadata record for a document."""
        try:
            metadata_file = self._get_metadata_file_path(document_path)

            if metadata_file.exists():
                metadata_file.unlink()
                self.logger.info(f"Deleted metadata for {document_path}")

            return True

        except Exception as e:
            self.logger.error(f"Error deleting metadata for {document_path}: {e}")
            return False

    def list_all_metadata(self) -> List[MetadataRecord]:
        """Get all metadata records."""
        records = []

        try:
            if self.centralized:
                # Search in centralized storage
                for metadata_file in self.storage_path.glob("**/*.metadata.json"):
                    try:
                        with open(metadata_file, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        records.append(MetadataRecord.from_dict(data))
                    except Exception as e:
                        self.logger.warning(
                            f"Error reading metadata file {metadata_file}: {e}"
                        )
            else:
                # This would require scanning the entire filesystem
                # For now, return empty list for non-centralized storage
                self.logger.warning(
                    "list_all_metadata not efficiently supported for non-centralized storage"
                )

        except Exception as e:
            self.logger.error(f"Error listing all metadata: {e}")

        return records

    def search_metadata(self, query: Dict[str, Any]) -> List[MetadataRecord]:
        """Search metadata records by criteria."""
        matching_records = []

        try:
            all_records = self.list_all_metadata()

            for record in all_records:
                if self._matches_query(record, query):
                    matching_records.append(record)

            self.logger.info(f"Found {len(matching_records)} records matching query")

        except Exception as e:
            self.logger.error(f"Error searching metadata: {e}")

        return matching_records

    def exists(self, document_path: Union[str, Path]) -> bool:
        """Check if metadata exists for a document."""
        try:
            metadata_file = self._get_metadata_file_path(document_path)
            return metadata_file.exists()
        except Exception as e:
            self.logger.error(
                f"Error checking metadata existence for {document_path}: {e}"
            )
            return False

    def get_storage_info(self) -> Dict[str, Any]:
        """
        Get information about the metadata storage.

        Returns:
            Dictionary with storage information
        """
        info = {
            "storage_path": str(self.storage_path),
            "centralized": self.centralized,
            "total_records": 0,
            "storage_size": 0,
        }

        try:
            if self.centralized and self.storage_path.exists():
                metadata_files = list(self.storage_path.glob("**/*.metadata.json"))
                info["total_records"] = len(metadata_files)

                # Calculate total storage size
                total_size = 0
                for file in metadata_files:
                    total_size += file.stat().st_size
                info["storage_size"] = total_size

        except Exception as e:
            self.logger.error(f"Error getting storage info: {e}")

        return info

    def cleanup_orphaned_metadata(self) -> int:
        """
        Remove metadata records for documents that no longer exist.

        Returns:
            Number of orphaned records cleaned up
        """
        cleaned_count = 0

        try:
            all_records = self.list_all_metadata()

            for record in all_records:
                document_path = Path(record.document_path)
                if not document_path.exists():
                    if self.delete_metadata(document_path):
                        cleaned_count += 1
                        self.logger.info(
                            f"Cleaned up orphaned metadata for {document_path}"
                        )

            self.logger.info(f"Cleaned up {cleaned_count} orphaned metadata records")

        except Exception as e:
            self.logger.error(f"Error cleaning up orphaned metadata: {e}")

        return cleaned_count

    def _get_metadata_file_path(self, document_path: Union[str, Path]) -> Path:
        """
        Get the path where metadata should be stored for a document.

        Args:
            document_path: Path to the document

        Returns:
            Path to the metadata file
        """
        document_path = Path(document_path)

        if self.centralized:
            # Store in centralized location with hashed path structure
            import hashlib

            path_hash = hashlib.md5(str(document_path.resolve()).encode()).hexdigest()

            # Create subdirectories based on first few characters of hash
            subdir = path_hash[:2]
            filename = f"{path_hash}.metadata.json"

            return self.storage_path / subdir / filename
        else:
            # Store alongside the document
            return document_path.parent / f"{document_path.stem}.metadata.json"

    def _matches_query(self, record: MetadataRecord, query: Dict[str, Any]) -> bool:
        """
        Check if a metadata record matches the search query.

        Args:
            record: Metadata record to check
            query: Search query criteria

        Returns:
            True if record matches query, False otherwise
        """
        try:
            # Check document path pattern
            if "document_path" in query:
                import fnmatch

                if not fnmatch.fnmatch(
                    record.document_path.lower(), query["document_path"].lower()
                ):
                    return False

            # Check metadata fields
            if "metadata" in query:
                for key, value in query["metadata"].items():
                    if key not in record.metadata:
                        return False

                    record_value = record.metadata[key]

                    # Handle different value types
                    if isinstance(value, str) and isinstance(record_value, str):
                        if value.lower() not in record_value.lower():
                            return False
                    elif record_value != value:
                        return False

            # Check creation date range
            if "created_after" in query:
                if record.created_at < query["created_after"]:
                    return False

            if "created_before" in query:
                if record.created_at > query["created_before"]:
                    return False

            # Check update date range
            if "updated_after" in query:
                if record.updated_at < query["updated_after"]:
                    return False

            if "updated_before" in query:
                if record.updated_at > query["updated_before"]:
                    return False

            # Check source
            if "source" in query:
                if record.source != query["source"]:
                    return False

            return True

        except Exception as e:
            self.logger.error(
                f"Error matching query for record {record.document_path}: {e}"
            )
            return False
