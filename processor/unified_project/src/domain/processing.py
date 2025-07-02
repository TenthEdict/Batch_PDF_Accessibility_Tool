#!/usr/bin/env python3
"""
Processing domain entities and value objects.

This module defines the ProcessingJob entity and related business objects
that represent document processing operations in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
import uuid

from .document import Document, DocumentStatus
from .enhancement import Enhancement, EnhancementType, EnhancementCapability
from .validation import ValidationResult


class ProcessingJobStatus(Enum):
    """Processing job status enumeration."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class ProcessingMode(Enum):
    """Processing mode enumeration."""

    ACCESSIBILITY = "accessibility"
    ACADEMIC = "academic"
    BASIC = "basic"
    CUSTOM = "custom"


class ProcessingPriority(Enum):
    """Processing priority enumeration."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4


@dataclass(frozen=True)
class ProcessingJobIdentifier:
    """Value object for processing job identification."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ProcessingRequest:
    """Value object representing a processing request."""

    input_path: Path
    output_path: Optional[Path] = None
    mode: ProcessingMode = ProcessingMode.ACCESSIBILITY
    priority: ProcessingPriority = ProcessingPriority.NORMAL

    # Enhancement options
    extract_title_from_h1: bool = True
    extract_title_from_filename: bool = True
    add_pdfua_identifiers: bool = False
    display_doc_title: bool = True

    # Metadata options
    title: Optional[str] = None
    author: Optional[str] = None
    language: str = "en-US"
    subject: Optional[str] = None
    keywords: Optional[List[str]] = None

    # Processing options
    validate_output: bool = True
    generate_report: bool = False
    report_format: str = "json"
    backup_original: bool = True
    overwrite_existing: bool = False

    # Custom capabilities (for CUSTOM mode)
    custom_capabilities: Optional[List[EnhancementCapability]] = None
    custom_parameters: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        self.input_path = Path(self.input_path)
        if self.output_path:
            self.output_path = Path(self.output_path)
        if self.keywords is None:
            self.keywords = []
        if self.custom_capabilities is None:
            self.custom_capabilities = []
        if self.custom_parameters is None:
            self.custom_parameters = {}

    def get_effective_output_path(self) -> Path:
        """Get the effective output path for the request."""
        if self.output_path:
            return self.output_path

        # Generate output path based on input path
        input_path = self.input_path
        stem = input_path.stem
        suffix = input_path.suffix

        # Add mode suffix if not overwriting
        if not self.overwrite_existing:
            output_name = f"{stem}_{self.mode.value}{suffix}"
        else:
            output_name = f"{stem}{suffix}"

        return input_path.parent / output_name

    def validate(self) -> List[str]:
        """
        Validate the processing request.

        Returns:
            List of validation error messages
        """
        errors = []

        # Check input file exists
        if not self.input_path.exists():
            errors.append(f"Input file not found: {self.input_path}")

        # Check input is a file
        if self.input_path.exists() and not self.input_path.is_file():
            errors.append(f"Input path is not a file: {self.input_path}")

        # Check output directory can be created
        output_path = self.get_effective_output_path()
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            errors.append(f"Cannot create output directory: {e}")

        # Check overwrite settings
        if output_path.exists() and not self.overwrite_existing:
            errors.append(
                f"Output file exists and overwrite not allowed: {output_path}"
            )

        # Validate language code
        import re

        if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", self.language):
            errors.append(f"Invalid language code: {self.language}")

        return errors

    def is_valid(self) -> bool:
        """Check if the request is valid."""
        return len(self.validate()) == 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "input_path": str(self.input_path),
            "output_path": str(self.output_path) if self.output_path else None,
            "mode": self.mode.value,
            "priority": self.priority.value,
            "extract_title_from_h1": self.extract_title_from_h1,
            "extract_title_from_filename": self.extract_title_from_filename,
            "add_pdfua_identifiers": self.add_pdfua_identifiers,
            "display_doc_title": self.display_doc_title,
            "title": self.title,
            "author": self.author,
            "language": self.language,
            "subject": self.subject,
            "keywords": self.keywords,
            "validate_output": self.validate_output,
            "generate_report": self.generate_report,
            "report_format": self.report_format,
            "backup_original": self.backup_original,
            "overwrite_existing": self.overwrite_existing,
            "custom_capabilities": [cap.value for cap in self.custom_capabilities]
            if self.custom_capabilities
            else [],
            "custom_parameters": self.custom_parameters,
        }


@dataclass
class ProcessingResult:
    """Value object representing processing result."""

    success: bool
    output_path: Optional[Path] = None
    backup_path: Optional[Path] = None

    # Processing details
    enhancements_applied: List[Enhancement] = field(default_factory=list)
    validation_result: Optional[ValidationResult] = None
    metadata_extracted: Optional[Dict[str, Any]] = None

    # Error and warning information
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    # Performance metrics
    processing_time_seconds: Optional[float] = None
    input_file_size: Optional[int] = None
    output_file_size: Optional[int] = None

    # Report information
    report_path: Optional[Path] = None

    def add_error(self, error: str) -> None:
        """Add an error to the result."""
        self.errors.append(error)
        self.success = False

    def add_warning(self, warning: str) -> None:
        """Add a warning to the result."""
        self.warnings.append(warning)

    def add_enhancement(self, enhancement: Enhancement) -> None:
        """Add an enhancement to the result."""
        self.enhancements_applied.append(enhancement)

    def get_file_size_change(self) -> Optional[int]:
        """Get the change in file size (output - input)."""
        if self.input_file_size is not None and self.output_file_size is not None:
            return self.output_file_size - self.input_file_size
        return None

    def get_enhancement_count(self) -> int:
        """Get the number of enhancements applied."""
        return len(self.enhancements_applied)

    def get_successful_enhancements(self) -> List[Enhancement]:
        """Get list of successful enhancements."""
        return [e for e in self.enhancements_applied if e.is_successful()]

    def get_failed_enhancements(self) -> List[Enhancement]:
        """Get list of failed enhancements."""
        return [e for e in self.enhancements_applied if not e.is_successful()]

    def has_errors(self) -> bool:
        """Check if result has errors."""
        return len(self.errors) > 0

    def has_warnings(self) -> bool:
        """Check if result has warnings."""
        return len(self.warnings) > 0

    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of the processing result."""
        return {
            "success": self.success,
            "output_generated": self.output_path is not None,
            "enhancements_applied": self.get_enhancement_count(),
            "successful_enhancements": len(self.get_successful_enhancements()),
            "failed_enhancements": len(self.get_failed_enhancements()),
            "validation_score": self.validation_result.overall_score
            if self.validation_result
            else None,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "processing_time": self.processing_time_seconds,
            "file_size_change": self.get_file_size_change(),
        }


@dataclass
class ProcessingJob:
    """
    ProcessingJob entity representing a document processing operation.

    This entity tracks the complete lifecycle of processing a document
    from request to completion.
    """

    identifier: ProcessingJobIdentifier
    request: ProcessingRequest
    document: Optional[Document] = None
    status: ProcessingJobStatus = ProcessingJobStatus.PENDING
    result: Optional[ProcessingResult] = None

    # Timestamps
    created_at: datetime = field(default_factory=datetime.now)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

    # Progress tracking
    progress_percentage: float = 0.0
    current_step: Optional[str] = None
    total_steps: int = 0
    completed_steps: int = 0

    # Error handling
    retry_count: int = 0
    max_retries: int = 3
    last_error: Optional[str] = None

    def start_processing(self) -> None:
        """Mark job as started."""
        self.status = ProcessingJobStatus.RUNNING
        self.started_at = datetime.now()
        self.progress_percentage = 0.0
        self.current_step = "Starting processing"

    def update_progress(self, step: str, completed_steps: Optional[int] = None) -> None:
        """
        Update job progress.

        Args:
            step: Description of current step
            completed_steps: Number of completed steps (optional)
        """
        self.current_step = step

        if completed_steps is not None:
            self.completed_steps = completed_steps
        else:
            self.completed_steps += 1

        if self.total_steps > 0:
            self.progress_percentage = (self.completed_steps / self.total_steps) * 100

    def set_total_steps(self, total: int) -> None:
        """Set the total number of processing steps."""
        self.total_steps = total
        self.completed_steps = 0
        self.progress_percentage = 0.0

    def complete_successfully(self, result: ProcessingResult) -> None:
        """Mark job as completed successfully."""
        self.status = ProcessingJobStatus.COMPLETED
        self.completed_at = datetime.now()
        self.result = result
        self.progress_percentage = 100.0
        self.current_step = "Processing completed"
        self.last_error = None

    def fail(
        self, error_message: str, result: Optional[ProcessingResult] = None
    ) -> None:
        """Mark job as failed."""
        self.status = ProcessingJobStatus.FAILED
        self.completed_at = datetime.now()
        self.last_error = error_message

        if result:
            self.result = result
        else:
            # Create minimal result with error
            self.result = ProcessingResult(success=False, errors=[error_message])

    def cancel(self) -> None:
        """Cancel the processing job."""
        self.status = ProcessingJobStatus.CANCELLED
        self.completed_at = datetime.now()
        self.current_step = "Processing cancelled"

    def pause(self) -> None:
        """Pause the processing job."""
        self.status = ProcessingJobStatus.PAUSED
        self.current_step = "Processing paused"

    def resume(self) -> None:
        """Resume the processing job."""
        if self.status == ProcessingJobStatus.PAUSED:
            self.status = ProcessingJobStatus.RUNNING
            self.current_step = "Processing resumed"

    def retry(self) -> bool:
        """
        Attempt to retry the job.

        Returns:
            True if retry is allowed, False if max retries exceeded
        """
        if self.retry_count >= self.max_retries:
            return False

        self.retry_count += 1
        self.status = ProcessingJobStatus.PENDING
        self.completed_at = None
        self.progress_percentage = 0.0
        self.current_step = f"Retry attempt {self.retry_count}"

        return True

    def get_duration(self) -> Optional[float]:
        """Get processing duration in seconds."""
        if self.started_at and self.completed_at:
            return (self.completed_at - self.started_at).total_seconds()
        elif self.started_at:
            return (datetime.now() - self.started_at).total_seconds()
        return None

    def is_complete(self) -> bool:
        """Check if job is complete (success, failure, or cancelled)."""
        return self.status in [
            ProcessingJobStatus.COMPLETED,
            ProcessingJobStatus.FAILED,
            ProcessingJobStatus.CANCELLED,
        ]

    def is_successful(self) -> bool:
        """Check if job completed successfully."""
        return (
            self.status == ProcessingJobStatus.COMPLETED
            and self.result
            and self.result.success
        )

    def can_be_retried(self) -> bool:
        """Check if job can be retried."""
        return (
            self.status == ProcessingJobStatus.FAILED
            and self.retry_count < self.max_retries
        )

    def get_priority_score(self) -> int:
        """Get priority score for job ordering."""
        base_score = self.request.priority.value

        # Boost priority for retries
        retry_boost = self.retry_count * 0.5

        # Boost priority for older jobs
        age_hours = (datetime.now() - self.created_at).total_seconds() / 3600
        age_boost = min(age_hours * 0.1, 2.0)  # Max 2 point boost

        return base_score + retry_boost + age_boost

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        data = {
            "id": self.identifier.id,
            "status": self.status.value,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "progress_percentage": self.progress_percentage,
            "current_step": self.current_step,
            "total_steps": self.total_steps,
            "completed_steps": self.completed_steps,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries,
            "last_error": self.last_error,
            "request": self.request.to_dict(),
        }

        if self.document:
            data["document"] = self.document.to_dict()

        if self.result:
            data["result"] = self.result.get_summary()

        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ProcessingJob":
        """Create from dictionary representation."""
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
        identifier = ProcessingJobIdentifier(id=data["id"])

        # Create request
        request_data = data["request"]
        request = ProcessingRequest(
            input_path=Path(request_data["input_path"]),
            output_path=Path(request_data["output_path"])
            if request_data.get("output_path")
            else None,
            mode=ProcessingMode(request_data["mode"]),
            priority=ProcessingPriority(request_data["priority"]),
            # ... other request fields
        )

        # Create document if present
        document = None
        if "document" in data:
            from .document import Document

            document = Document.from_dict(data["document"])

        return cls(
            identifier=identifier,
            request=request,
            document=document,
            status=ProcessingJobStatus(data["status"]),
            created_at=created_at,
            started_at=started_at,
            completed_at=completed_at,
            progress_percentage=data["progress_percentage"],
            current_step=data.get("current_step"),
            total_steps=data["total_steps"],
            completed_steps=data["completed_steps"],
            retry_count=data["retry_count"],
            max_retries=data["max_retries"],
            last_error=data.get("last_error"),
        )

    @classmethod
    def create_from_request(cls, request: ProcessingRequest) -> "ProcessingJob":
        """
        Create a new processing job from a request.

        Args:
            request: Processing request

        Returns:
            New ProcessingJob instance
        """
        return cls(identifier=ProcessingJobIdentifier(), request=request)

    def __str__(self) -> str:
        """String representation of the processing job."""
        return f"ProcessingJob(id={self.identifier.id[:8]}, status={self.status.value}, progress={self.progress_percentage:.1f}%)"

    def __repr__(self) -> str:
        """Detailed representation of the processing job."""
        return (
            f"ProcessingJob("
            f"id='{self.identifier.id}', "
            f"status={self.status.value}, "
            f"mode={self.request.mode.value}, "
            f"progress={self.progress_percentage:.1f}%, "
            f"retries={self.retry_count}"
            f")"
        )
