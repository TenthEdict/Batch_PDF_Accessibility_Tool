#!/usr/bin/env python3
"""
Metadata domain entities and value objects.

This module defines the DocumentMetadata entity and related business objects
that represent document metadata in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
import re


class MetadataFieldType(Enum):
    """Metadata field type enumeration."""

    TEXT = "text"
    LIST = "list"
    DATE = "date"
    LANGUAGE = "language"
    NUMBER = "number"
    BOOLEAN = "boolean"
    URL = "url"


class MetadataFieldValidation(Enum):
    """Metadata field validation rules."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    RECOMMENDED = "recommended"


@dataclass
class MetadataFieldDefinition:
    """Definition of a metadata field with validation rules."""

    name: str
    field_type: MetadataFieldType
    validation: MetadataFieldValidation = MetadataFieldValidation.OPTIONAL
    description: Optional[str] = None
    max_length: Optional[int] = None
    pattern: Optional[str] = None
    allowed_values: Optional[List[str]] = None
    default_value: Optional[Any] = None

    def validate_value(self, value: Any) -> List[str]:
        """
        Validate a value against this field definition.

        Args:
            value: Value to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        errors = []

        # Check required fields
        if self.validation == MetadataFieldValidation.REQUIRED and (
            value is None or value == ""
        ):
            errors.append(f"Field '{self.name}' is required")
            return errors

        # Skip further validation if value is None/empty and not required
        if value is None or value == "":
            return errors

        # Type validation
        if self.field_type == MetadataFieldType.TEXT and not isinstance(value, str):
            errors.append(f"Field '{self.name}' must be text")
        elif self.field_type == MetadataFieldType.LIST and not isinstance(value, list):
            errors.append(f"Field '{self.name}' must be a list")
        elif self.field_type == MetadataFieldType.NUMBER and not isinstance(
            value, (int, float)
        ):
            errors.append(f"Field '{self.name}' must be a number")
        elif self.field_type == MetadataFieldType.BOOLEAN and not isinstance(
            value, bool
        ):
            errors.append(f"Field '{self.name}' must be a boolean")

        # String-specific validations
        if isinstance(value, str):
            # Length validation
            if self.max_length and len(value) > self.max_length:
                errors.append(
                    f"Field '{self.name}' exceeds maximum length of {self.max_length}"
                )

            # Pattern validation
            if self.pattern and not re.match(self.pattern, value):
                errors.append(f"Field '{self.name}' does not match required pattern")

            # Allowed values validation
            if self.allowed_values and value not in self.allowed_values:
                errors.append(
                    f"Field '{self.name}' must be one of: {', '.join(self.allowed_values)}"
                )

        # Language code validation
        if self.field_type == MetadataFieldType.LANGUAGE and isinstance(value, str):
            if not re.match(r"^[a-z]{2}(-[A-Z]{2})?$", value):
                errors.append(
                    f"Field '{self.name}' must be a valid language code (e.g., 'en', 'en-US')"
                )

        # URL validation
        if self.field_type == MetadataFieldType.URL and isinstance(value, str):
            url_pattern = r"^https?://[^\s/$.?#].[^\s]*$"
            if not re.match(url_pattern, value):
                errors.append(f"Field '{self.name}' must be a valid URL")

        return errors


@dataclass
class MetadataField:
    """Value object representing a metadata field with its value."""

    definition: MetadataFieldDefinition
    value: Any
    source: str = "unknown"
    extracted_at: datetime = field(default_factory=datetime.now)
    confidence: float = 1.0  # Confidence in extracted value (0.0 - 1.0)

    def is_valid(self) -> bool:
        """Check if the field value is valid."""
        return len(self.get_validation_errors()) == 0

    def get_validation_errors(self) -> List[str]:
        """Get validation errors for this field."""
        return self.definition.validate_value(self.value)

    def is_required(self) -> bool:
        """Check if this field is required."""
        return self.definition.validation == MetadataFieldValidation.REQUIRED

    def is_recommended(self) -> bool:
        """Check if this field is recommended."""
        return self.definition.validation == MetadataFieldValidation.RECOMMENDED

    def has_value(self) -> bool:
        """Check if field has a non-empty value."""
        return self.value is not None and self.value != ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "name": self.definition.name,
            "value": self.value,
            "source": self.source,
            "extracted_at": self.extracted_at.isoformat(),
            "confidence": self.confidence,
            "field_type": self.definition.field_type.value,
            "validation": self.definition.validation.value,
        }


@dataclass
class DocumentMetadata:
    """
    DocumentMetadata entity representing complete document metadata.

    This entity manages all metadata fields for a document with validation
    and normalization capabilities.
    """

    document_id: str
    fields: Dict[str, MetadataField] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    version: int = 1

    # Standard field definitions
    STANDARD_FIELDS = {
        "title": MetadataFieldDefinition(
            name="title",
            field_type=MetadataFieldType.TEXT,
            validation=MetadataFieldValidation.REQUIRED,
            description="Document title",
            max_length=200,
        ),
        "author": MetadataFieldDefinition(
            name="author",
            field_type=MetadataFieldType.TEXT,
            validation=MetadataFieldValidation.RECOMMENDED,
            description="Document author(s)",
            max_length=100,
        ),
        "language": MetadataFieldDefinition(
            name="language",
            field_type=MetadataFieldType.LANGUAGE,
            validation=MetadataFieldValidation.REQUIRED,
            description="Document language code",
            default_value="en-US",
        ),
        "subject": MetadataFieldDefinition(
            name="subject",
            field_type=MetadataFieldType.TEXT,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Document subject/topic",
            max_length=150,
        ),
        "keywords": MetadataFieldDefinition(
            name="keywords",
            field_type=MetadataFieldType.LIST,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Document keywords/tags",
        ),
        "creator": MetadataFieldDefinition(
            name="creator",
            field_type=MetadataFieldType.TEXT,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Software/tool that created the document",
            max_length=100,
        ),
        "producer": MetadataFieldDefinition(
            name="producer",
            field_type=MetadataFieldType.TEXT,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Software/tool that produced the final document",
            max_length=100,
        ),
        "creation_date": MetadataFieldDefinition(
            name="creation_date",
            field_type=MetadataFieldType.DATE,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Document creation date",
        ),
        "modification_date": MetadataFieldDefinition(
            name="modification_date",
            field_type=MetadataFieldType.DATE,
            validation=MetadataFieldValidation.OPTIONAL,
            description="Document modification date",
        ),
    }

    def set_field(
        self, name: str, value: Any, source: str = "manual", confidence: float = 1.0
    ) -> None:
        """
        Set a metadata field value.

        Args:
            name: Field name
            value: Field value
            source: Source of the value
            confidence: Confidence in the value (0.0 - 1.0)
        """
        # Get field definition (use standard or create basic one)
        definition = self.STANDARD_FIELDS.get(name)
        if not definition:
            definition = MetadataFieldDefinition(
                name=name,
                field_type=MetadataFieldType.TEXT,
                validation=MetadataFieldValidation.OPTIONAL,
            )

        # Create field
        field_obj = MetadataField(
            definition=definition, value=value, source=source, confidence=confidence
        )

        self.fields[name] = field_obj
        self.updated_at = datetime.now()
        self.version += 1

    def get_field(self, name: str) -> Optional[MetadataField]:
        """Get a metadata field."""
        return self.fields.get(name)

    def get_field_value(self, name: str, default: Any = None) -> Any:
        """Get a metadata field value."""
        field = self.fields.get(name)
        return field.value if field else default

    def has_field(self, name: str) -> bool:
        """Check if metadata has a specific field."""
        return name in self.fields and self.fields[name].has_value()

    def remove_field(self, name: str) -> bool:
        """
        Remove a metadata field.

        Args:
            name: Field name to remove

        Returns:
            True if field was removed, False if it didn't exist
        """
        if name in self.fields:
            del self.fields[name]
            self.updated_at = datetime.now()
            self.version += 1
            return True
        return False

    def get_all_values(self) -> Dict[str, Any]:
        """Get all metadata field values as a dictionary."""
        return {
            name: field.value
            for name, field in self.fields.items()
            if field.has_value()
        }

    def validate(self) -> Dict[str, List[str]]:
        """
        Validate all metadata fields.

        Returns:
            Dictionary mapping field names to lists of validation errors
        """
        validation_errors = {}

        # Validate existing fields
        for name, field in self.fields.items():
            errors = field.get_validation_errors()
            if errors:
                validation_errors[name] = errors

        # Check for missing required fields
        for name, definition in self.STANDARD_FIELDS.items():
            if definition.validation == MetadataFieldValidation.REQUIRED:
                if not self.has_field(name):
                    validation_errors[name] = [f"Required field '{name}' is missing"]

        return validation_errors

    def is_valid(self) -> bool:
        """Check if all metadata is valid."""
        return len(self.validate()) == 0

    def get_required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [
            name
            for name, definition in self.STANDARD_FIELDS.items()
            if definition.validation == MetadataFieldValidation.REQUIRED
        ]

    def get_missing_required_fields(self) -> List[str]:
        """Get list of missing required fields."""
        required = self.get_required_fields()
        return [name for name in required if not self.has_field(name)]

    def get_recommended_fields(self) -> List[str]:
        """Get list of recommended field names."""
        return [
            name
            for name, definition in self.STANDARD_FIELDS.items()
            if definition.validation == MetadataFieldValidation.RECOMMENDED
        ]

    def get_missing_recommended_fields(self) -> List[str]:
        """Get list of missing recommended fields."""
        recommended = self.get_recommended_fields()
        return [name for name in recommended if not self.has_field(name)]

    def get_completeness_score(self) -> float:
        """
        Get metadata completeness score (0.0 - 1.0).

        Score is based on the percentage of standard fields that have values.
        """
        total_fields = len(self.STANDARD_FIELDS)
        filled_fields = len(
            [name for name in self.STANDARD_FIELDS if self.has_field(name)]
        )

        return filled_fields / total_fields if total_fields > 0 else 0.0

    def get_quality_score(self) -> float:
        """
        Get metadata quality score (0.0 - 1.0).

        Score considers completeness, validation, and confidence.
        """
        if not self.fields:
            return 0.0

        # Base score from completeness
        completeness = self.get_completeness_score()

        # Penalty for validation errors
        validation_errors = self.validate()
        error_penalty = len(validation_errors) * 0.1

        # Bonus for high confidence values
        total_confidence = sum(field.confidence for field in self.fields.values())
        avg_confidence = total_confidence / len(self.fields)

        # Calculate final score
        score = (completeness * 0.6) + (avg_confidence * 0.4) - error_penalty
        return max(0.0, min(1.0, score))

    def merge_from_dict(
        self, metadata_dict: Dict[str, Any], source: str = "import"
    ) -> None:
        """
        Merge metadata from a dictionary.

        Args:
            metadata_dict: Dictionary of metadata values
            source: Source identifier for the metadata
        """
        for name, value in metadata_dict.items():
            if value is not None and value != "":
                self.set_field(name, value, source=source)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            "document_id": self.document_id,
            "fields": {name: field.to_dict() for name, field in self.fields.items()},
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "version": self.version,
            "completeness_score": self.get_completeness_score(),
            "quality_score": self.get_quality_score(),
            "validation_errors": self.validate(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DocumentMetadata":
        """Create from dictionary representation."""
        # Convert datetime strings
        created_at = datetime.fromisoformat(data["created_at"])
        updated_at = datetime.fromisoformat(data["updated_at"])

        metadata = cls(
            document_id=data["document_id"],
            created_at=created_at,
            updated_at=updated_at,
            version=data["version"],
        )

        # Recreate fields
        for name, field_data in data["fields"].items():
            definition = cls.STANDARD_FIELDS.get(name)
            if not definition:
                definition = MetadataFieldDefinition(
                    name=name,
                    field_type=MetadataFieldType(field_data["field_type"]),
                    validation=MetadataFieldValidation(field_data["validation"]),
                )

            field = MetadataField(
                definition=definition,
                value=field_data["value"],
                source=field_data["source"],
                extracted_at=datetime.fromisoformat(field_data["extracted_at"]),
                confidence=field_data["confidence"],
            )
            metadata.fields[name] = field

        return metadata

    @classmethod
    def create_for_document(
        cls, document_id: str, initial_metadata: Optional[Dict[str, Any]] = None
    ) -> "DocumentMetadata":
        """
        Create new metadata for a document.

        Args:
            document_id: ID of the document
            initial_metadata: Optional initial metadata values

        Returns:
            New DocumentMetadata instance
        """
        metadata = cls(document_id=document_id)

        if initial_metadata:
            metadata.merge_from_dict(initial_metadata, source="initial")

        return metadata

    def __str__(self) -> str:
        """String representation of the metadata."""
        return f"DocumentMetadata(document_id={self.document_id}, fields={len(self.fields)}, score={self.get_quality_score():.2f})"

    def __repr__(self) -> str:
        """Detailed representation of the metadata."""
        return (
            f"DocumentMetadata("
            f"document_id='{self.document_id}', "
            f"fields={len(self.fields)}, "
            f"version={self.version}, "
            f"quality_score={self.get_quality_score():.2f}"
            f")"
        )
