#!/usr/bin/env python3
"""
Enhancement domain entities and value objects.

This module defines the Enhancement entity and related business objects
that represent document enhancement operations in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set
import uuid


class EnhancementType(Enum):
    """Enhancement type enumeration."""

    PDF_ACCESSIBILITY = "pdf_accessibility"
    METADATA_ENHANCEMENT = "metadata_enhancement"
    STRUCTURE_ENHANCEMENT = "structure_enhancement"
    OCR_PROCESSING = "ocr_processing"
    ACADEMIC_FORMATTING = "academic_formatting"
    BASIC_CLEANUP = "basic_cleanup"


class EnhancementStatus(Enum):
    """Enhancement processing status enumeration."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EnhancementCapability(Enum):
    """Enhancement capability enumeration."""

    # Metadata capabilities
    METADATA_TITLE = "metadata.title"
    METADATA_AUTHOR = "metadata.author"
    METADATA_LANGUAGE = "metadata.language"
    METADATA_SUBJECT = "metadata.subject"
    METADATA_KEYWORDS = "metadata.keywords"
    METADATA_TITLE_FROM_H1 = "metadata.title_from_h1"

    # Viewer capabilities
    VIEWER_DISPLAY_TITLE = "viewer.display_title"

    # Structure capabilities
    STRUCTURE_HEADINGS = "structure.headings"
    STRUCTURE_BOOKMARKS = "structure.bookmarks"
    STRUCTURE_READING_ORDER = "structure.reading_order"
    STRUCTURE_ACADEMIC = "structure.academic"

    # Accessibility capabilities
    ACCESSIBILITY_PDF_UA = "accessibility.pdf_ua"
    ACCESSIBILITY_ALT_TEXT = "accessibility.alt_text"
    ACCESSIBILITY_COLOR_CONTRAST = "accessibility.color_contrast"
    ACCESSIBILITY_KEYBOARD_NAV = "accessibility.keyboard_navigation"

    # OCR capabilities
    OCR_TEXT_EXTRACTION = "ocr.text_extraction"
    OCR_IMAGE_PROCESSING = "ocr.image_processing"
    OCR_TABLE_DETECTION = "ocr.table_detection"


@dataclass(frozen=True)
class EnhancementIdentifier:
    """Value object for enhancement identification."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class EnhancementConfiguration:
    """Value object for enhancement configuration."""

    capabilities: Set[EnhancementCapability]
    parameters: Dict[str, Any] = field(default_factory=dict)
    mode: str = "accessibility"

    def has_capability(self, capability: EnhancementCapability) -> bool:
        """Check if configuration includes a specific capability."""
        return capability in self.capabilities

    def get_parameter(self, key: str, default: Any = None) -> Any:
        """Get configuration parameter with default."""
        return self.parameters.get(key, default)

    def set_parameter(self, key: str, value: Any) -> None:
        """Set configuration parameter."""
        self.parameters[key] = value

    def add_capability(self, capability: EnhancementCapability) -> None:
        """Add capability to configuration."""
        self.capabilities.add(capability)

    def remove_capability(self, capability: EnhancementCapability) -> None:
        """Remove capability from configuration."""
        self.capabilities.discard(capability)


@dataclass
class EnhancementResult:
    """Value object for enhancement result information."""

    success: bool
    applied_capabilities: List[EnhancementCapability] = field(default_factory=list)
    skipped_capabilities: List[EnhancementCapability] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata_changes: Dict[str, Any] = field(default_factory=dict)
    file_size_change: Optional[int] = None
    processing_time_seconds: Optional[float] = None

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def add_applied_capability(self, capability: EnhancementCapability) -> None:
        """Add a capability that was successfully applied."""
        if capability not in self.applied_capabilities:
            self.applied_capabilities.append(capability)

    def add_skipped_capability(self, capability: EnhancementCapability) -> None:
        """Add a capability that was skipped."""
        if capability not in self.skipped_capabilities:
            self.skipped_capabilities.append(capability)

    def get_success_rate(self) -> float:
        """Get the success rate of applied capabilities."""
        total = len(self.applied_capabilities) + len(self.skipped_capabilities)
        if total == 0:
            return 0.0
        return len(self.applied_capabilities) / total

    def has_errors(self) -> bool:
        """Check if result has errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0


@dataclass
class Enhancement:
    """
    Enhancement entity representing a document enhancement operation.

    This entity tracks the enhancement of a document with specific
    capabilities and configuration.
    """

    identifier: EnhancementIdentifier
    document_id: str
    enhancement_type: EnhancementType
    configuration: EnhancementConfiguration
    status: EnhancementStatus = EnhancementStatus.PENDING
    result: Optional[EnhancementResult] = None
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def start_processing(self) -> None:
        """Mark enhancement as started."""
        self.status = EnhancementStatus.IN_PROGRESS
        self.started_at = datetime.now()

    def complete_successfully(self, result: EnhancementResult) -> None:
        """Mark enhancement as completed successfully."""
        self.status = EnhancementStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.error_message = None

    def fail(
        self, error_message: str, result: Optional[EnhancementResult] = None
    ) -> None:
        """Mark enhancement as failed."""
        self.status = EnhancementStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message
        if result:
            self.result = result

    def skip(self, reason: str) -> None:
        """Mark enhancement as skipped."""
        self.status = EnhancementStatus.SKIPPED
        self.completed_at = datetime.now()
        self.error_message = reason

    def get_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        return None

    def is_complete(self) -> bool:
        """Check if enhancement is complete (success or failure)."""
        return self.status in [
            EnhancementStatus.COMPLETED,
            EnhancementStatus.FAILED,
            EnhancementStatus.SKIPPED,
        ]

    def is_successful(self) -> bool:
        """Check if enhancement completed successfully."""
        return self.status == EnhancementStatus.COMPLETED

    def get_applied_capabilities(self) -> List[EnhancementCapability]:
        """Get list of successfully applied capabilities."""
        if self.result:
            return self.result.applied_capabilities
        return []

    def get_configuration_summary(self) -> Dict[str, Any]:
        """Get summary of enhancement configuration."""
        return {
            "type": self.enhancement_type.value,
            "mode": self.configuration.mode,
            "capabilities_count": len(self.configuration.capabilities),
            "capabilities": [cap.value for cap in self.configuration.capabilities],
            "parameters": self.configuration.parameters,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert enhancement to dictionary representation."""
        data = {
            "id": self.identifier.id,
            "document_id": self.document_id,
            "type": self.enhancement_type.value,
            "status": self.status.value,
            "configuration": {
                "mode": self.configuration.mode,
                "capabilities": [cap.value for cap in self.configuration.capabilities],
                "parameters": self.configuration.parameters,
            },
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error_message": self.error_message,
        }

        if self.result:
            data["result"] = {
                "success": self.result.success,
                "applied_capabilities": [
                    cap.value for cap in self.result.applied_capabilities
                ],
                "skipped_capabilities": [
                    cap.value for cap in self.result.skipped_capabilities
                ],
                "errors": self.result.errors,
                "warnings": self.result.warnings,
                "metadata_changes": self.result.metadata_changes,
                "file_size_change": self.result.file_size_change,
                "processing_time_seconds": self.result.processing_time_seconds,
            }

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Enhancement":
        """Create enhancement from dictionary representation."""
        # Convert datetime strings
        created_at = datetime.fromisoformat(data["created_at"])
        started_at = (
            datetime.fromisoformat(data["started_at"])
            if data.get("started_at")
            else None
        )
        completed_at = (
            datetime.fromisoformat(data["completed_at"])
            if data.get("completed_at")
            else None
        )

        # Create identifier
        identifier = EnhancementIdentifier(id=data["id"])

        # Create configuration
        capabilities = {
            EnhancementCapability(cap) for cap in data["configuration"]["capabilities"]
        }
        configuration = EnhancementConfiguration(
            capabilities=capabilities,
            parameters=data["configuration"]["parameters"],
            mode=data["configuration"]["mode"],
        )

        # Create result if present
        result = None
        if "result" in data:
            result_data = data["result"]
            result = EnhancementResult(
                success=result_data["success"],
                applied_capabilities=[
                    EnhancementCapability(cap)
                    for cap in result_data["applied_capabilities"]
                ],
                skipped_capabilities=[
                    EnhancementCapability(cap)
                    for cap in result_data["skipped_capabilities"]
                ],
                errors=result_data["errors"],
                warnings=result_data["warnings"],
                metadata_changes=result_data["metadata_changes"],
                file_size_change=result_data.get("file_size_change"),
                processing_time_seconds=result_data.get("processing_time_seconds"),
            )

        return cls(
            identifier=identifier,
            document_id=data["document_id"],
            enhancement_type=EnhancementType(data["type"]),
            configuration=configuration,
            status=EnhancementStatus(data["status"]),
            result=result,
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            error_message=data.get("error_message"),
        )

    @classmethod
    def create_for_document(
        cls,
        document_id: str,
        enhancement_type: EnhancementType,
        capabilities: List[EnhancementCapability],
        mode: str = "accessibility",
        parameters: Optional[Dict[str, Any]] = None,
    ) -> "Enhancement":
        """
        Create a new enhancement for a document.

        Args:
            document_id: ID of the document to enhance
            enhancement_type: Type of enhancement to perform
            capabilities: List of capabilities to apply
            mode: Enhancement mode
            parameters: Optional configuration parameters

        Returns:
            New Enhancement instance
        """
        configuration = EnhancementConfiguration(
            capabilities=set(capabilities), parameters=parameters or {}, mode=mode
        )

        return cls(
            identifier=EnhancementIdentifier(),
            document_id=document_id,
            enhancement_type=enhancement_type,
            configuration=configuration,
        )

    def __str__(self) -> str:
        """String representation of the enhancement."""
        return f"Enhancement(id={self.identifier.id[:8]}, type={self.enhancement_type.value}, status={self.status.value})"

    def __repr__(self) -> str:
        """Detailed representation of the enhancement."""
        return (
            f"Enhancement("
            f"id='{self.identifier.id}', "
            f"document_id='{self.document_id}', "
            f"type={self.enhancement_type.value}, "
            f"status={self.status.value}, "
            f"capabilities={len(self.configuration.capabilities)}"
            f")"
        )
