#!/usr/bin/env python3
"""
Configuration schema definition and validation system.

This module provides classes for defining configuration schemas
with validation rules and type checking.
"""

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, Union


class ConfigFieldType(Enum):
    """Configuration field type enumeration."""

    STRING = "string"
    INTEGER = "integer"
    FLOAT = "float"
    BOOLEAN = "boolean"
    LIST = "list"
    DICT = "dict"
    PATH = "path"
    URL = "url"
    EMAIL = "email"
    ENUM = "enum"


class ConfigValidationLevel(Enum):
    """Configuration validation level enumeration."""

    REQUIRED = "required"
    OPTIONAL = "optional"
    DEPRECATED = "deprecated"


class ConfigValidator(ABC):
    """Abstract base class for configuration validators."""

    @abstractmethod
    def validate(self, value: Any) -> List[str]:
        """
        Validate a configuration value.

        Args:
            value: Value to validate

        Returns:
            List of validation error messages (empty if valid)
        """
        pass


class RangeValidator(ConfigValidator):
    """Validator for numeric ranges."""

    def __init__(
        self,
        min_value: Optional[Union[int, float]] = None,
        max_value: Optional[Union[int, float]] = None,
    ):
        self.min_value = min_value
        self.max_value = max_value

    def validate(self, value: Any) -> List[str]:
        """Validate numeric range."""
        errors = []

        if not isinstance(value, (int, float)):
            errors.append("Value must be numeric")
            return errors

        if self.min_value is not None and value < self.min_value:
            errors.append(f"Value must be >= {self.min_value}")

        if self.max_value is not None and value > self.max_value:
            errors.append(f"Value must be <= {self.max_value}")

        return errors


class LengthValidator(ConfigValidator):
    """Validator for string/list length."""

    def __init__(
        self, min_length: Optional[int] = None, max_length: Optional[int] = None
    ):
        self.min_length = min_length
        self.max_length = max_length

    def validate(self, value: Any) -> List[str]:
        """Validate length."""
        errors = []

        if not hasattr(value, "__len__"):
            errors.append("Value must have length")
            return errors

        length = len(value)

        if self.min_length is not None and length < self.min_length:
            errors.append(f"Length must be >= {self.min_length}")

        if self.max_length is not None and length > self.max_length:
            errors.append(f"Length must be <= {self.max_length}")

        return errors


class PatternValidator(ConfigValidator):
    """Validator for regex patterns."""

    def __init__(self, pattern: str, flags: int = 0):
        self.pattern = re.compile(pattern, flags)

    def validate(self, value: Any) -> List[str]:
        """Validate regex pattern."""
        errors = []

        if not isinstance(value, str):
            errors.append("Value must be a string")
            return errors

        if not self.pattern.match(value):
            errors.append(f"Value does not match required pattern")

        return errors


class EnumValidator(ConfigValidator):
    """Validator for enum values."""

    def __init__(self, allowed_values: List[Any]):
        self.allowed_values = allowed_values

    def validate(self, value: Any) -> List[str]:
        """Validate enum value."""
        errors = []

        if value not in self.allowed_values:
            errors.append(
                f"Value must be one of: {', '.join(map(str, self.allowed_values))}"
            )

        return errors


class CustomValidator(ConfigValidator):
    """Validator using custom validation function."""

    def __init__(self, validator_func: Callable[[Any], Union[bool, str]]):
        self.validator_func = validator_func

    def validate(self, value: Any) -> List[str]:
        """Validate using custom function."""
        result = self.validator_func(value)

        if result is True:
            return []
        elif result is False:
            return ["Validation failed"]
        elif isinstance(result, str):
            return [result]
        else:
            return ["Unknown validation error"]


@dataclass
class ConfigField:
    """Configuration field definition with validation rules."""

    name: str
    field_type: ConfigFieldType
    validation_level: ConfigValidationLevel = ConfigValidationLevel.OPTIONAL
    default_value: Any = None
    description: Optional[str] = None
    validators: List[ConfigValidator] = field(default_factory=list)
    environment_variable: Optional[str] = None
    deprecated_message: Optional[str] = None

    def validate_value(self, value: Any) -> List[str]:
        """
        Validate a value against this field definition.

        Args:
            value: Value to validate

        Returns:
            List of validation error messages
        """
        errors = []

        # Check required fields
        if self.validation_level == ConfigValidationLevel.REQUIRED and value is None:
            errors.append(f"Field '{self.name}' is required")
            return errors

        # Skip validation for None optional fields
        if value is None and self.validation_level == ConfigValidationLevel.OPTIONAL:
            return errors

        # Type validation
        type_errors = self._validate_type(value)
        if type_errors:
            errors.extend(type_errors)
            return errors  # Don't continue if type is wrong

        # Custom validators
        for validator in self.validators:
            validator_errors = validator.validate(value)
            errors.extend(validator_errors)

        # Deprecation warning
        if self.validation_level == ConfigValidationLevel.DEPRECATED:
            warning = f"Field '{self.name}' is deprecated"
            if self.deprecated_message:
                warning += f": {self.deprecated_message}"
            errors.append(warning)

        return errors

    def _validate_type(self, value: Any) -> List[str]:
        """Validate value type."""
        errors = []

        if self.field_type == ConfigFieldType.STRING:
            if not isinstance(value, str):
                errors.append(f"Field '{self.name}' must be a string")

        elif self.field_type == ConfigFieldType.INTEGER:
            if not isinstance(value, int):
                errors.append(f"Field '{self.name}' must be an integer")

        elif self.field_type == ConfigFieldType.FLOAT:
            if not isinstance(value, (int, float)):
                errors.append(f"Field '{self.name}' must be a number")

        elif self.field_type == ConfigFieldType.BOOLEAN:
            if not isinstance(value, bool):
                errors.append(f"Field '{self.name}' must be a boolean")

        elif self.field_type == ConfigFieldType.LIST:
            if not isinstance(value, list):
                errors.append(f"Field '{self.name}' must be a list")

        elif self.field_type == ConfigFieldType.DICT:
            if not isinstance(value, dict):
                errors.append(f"Field '{self.name}' must be a dictionary")

        elif self.field_type == ConfigFieldType.PATH:
            if not isinstance(value, str):
                errors.append(f"Field '{self.name}' must be a string path")

        elif self.field_type == ConfigFieldType.URL:
            if not isinstance(value, str):
                errors.append(f"Field '{self.name}' must be a URL string")
            elif not re.match(r"^https?://[^\s/$.?#].[^\s]*$", value):
                errors.append(f"Field '{self.name}' must be a valid URL")

        elif self.field_type == ConfigFieldType.EMAIL:
            if not isinstance(value, str):
                errors.append(f"Field '{self.name}' must be an email string")
            elif not re.match(
                r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", value
            ):
                errors.append(f"Field '{self.name}' must be a valid email address")

        return errors

    def get_effective_value(self, config_value: Any, env_vars: Dict[str, str]) -> Any:
        """
        Get the effective value considering environment variables and defaults.

        Args:
            config_value: Value from configuration
            env_vars: Environment variables

        Returns:
            Effective configuration value
        """
        # Environment variable takes precedence
        if self.environment_variable and self.environment_variable in env_vars:
            env_value = env_vars[self.environment_variable]
            return self._convert_env_value(env_value)

        # Use config value if provided
        if config_value is not None:
            return config_value

        # Fall back to default
        return self.default_value

    def _convert_env_value(self, env_value: str) -> Any:
        """Convert environment variable string to appropriate type."""
        if self.field_type == ConfigFieldType.BOOLEAN:
            return env_value.lower() in ("true", "1", "yes", "on")

        elif self.field_type == ConfigFieldType.INTEGER:
            try:
                return int(env_value)
            except ValueError:
                return env_value  # Let validation catch the error

        elif self.field_type == ConfigFieldType.FLOAT:
            try:
                return float(env_value)
            except ValueError:
                return env_value  # Let validation catch the error

        elif self.field_type == ConfigFieldType.LIST:
            # Split by comma and strip whitespace
            return [item.strip() for item in env_value.split(",") if item.strip()]

        else:
            return env_value

    def to_dict(self) -> Dict[str, Any]:
        """Convert field to dictionary representation."""
        return {
            "name": self.name,
            "type": self.field_type.value,
            "validation_level": self.validation_level.value,
            "default_value": self.default_value,
            "description": self.description,
            "environment_variable": self.environment_variable,
            "deprecated_message": self.deprecated_message,
        }


@dataclass
class ConfigSection:
    """Configuration section containing related fields."""

    name: str
    description: Optional[str] = None
    fields: Dict[str, ConfigField] = field(default_factory=dict)

    def add_field(self, field: ConfigField) -> None:
        """Add a field to this section."""
        self.fields[field.name] = field

    def get_field(self, name: str) -> Optional[ConfigField]:
        """Get a field by name."""
        return self.fields.get(name)

    def validate_section(
        self, config_data: Dict[str, Any], env_vars: Dict[str, str]
    ) -> Dict[str, List[str]]:
        """
        Validate all fields in this section.

        Args:
            config_data: Configuration data for this section
            env_vars: Environment variables

        Returns:
            Dictionary mapping field names to validation errors
        """
        errors = {}

        for field_name, field in self.fields.items():
            config_value = config_data.get(field_name)
            effective_value = field.get_effective_value(config_value, env_vars)

            field_errors = field.validate_value(effective_value)
            if field_errors:
                errors[field_name] = field_errors

        return errors

    def get_effective_config(
        self, config_data: Dict[str, Any], env_vars: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Get effective configuration for this section.

        Args:
            config_data: Raw configuration data
            env_vars: Environment variables

        Returns:
            Effective configuration with environment variables and defaults applied
        """
        effective_config = {}

        for field_name, field in self.fields.items():
            config_value = config_data.get(field_name)
            effective_value = field.get_effective_value(config_value, env_vars)

            if effective_value is not None:
                effective_config[field_name] = effective_value

        return effective_config


class ConfigSchema:
    """
    Configuration schema definition and validation.

    This class defines the complete configuration schema with sections
    and provides validation capabilities.
    """

    def __init__(self, name: str, version: str = "1.0"):
        self.name = name
        self.version = version
        self.sections: Dict[str, ConfigSection] = {}
        self.global_validators: List[Callable[[Dict[str, Any]], List[str]]] = []

    def add_section(self, section: ConfigSection) -> None:
        """Add a configuration section."""
        self.sections[section.name] = section

    def get_section(self, name: str) -> Optional[ConfigSection]:
        """Get a configuration section by name."""
        return self.sections.get(name)

    def add_global_validator(
        self, validator: Callable[[Dict[str, Any]], List[str]]
    ) -> None:
        """Add a global configuration validator."""
        self.global_validators.append(validator)

    def validate_config(
        self, config_data: Dict[str, Any], env_vars: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Validate complete configuration.

        Args:
            config_data: Configuration data to validate
            env_vars: Environment variables (uses os.environ if None)

        Returns:
            Dictionary with validation results
        """
        if env_vars is None:
            import os

            env_vars = dict(os.environ)

        result = {"valid": True, "errors": {}, "warnings": {}, "effective_config": {}}

        # Validate each section
        for section_name, section in self.sections.items():
            section_data = config_data.get(section_name, {})

            # Validate section fields
            section_errors = section.validate_section(section_data, env_vars)
            if section_errors:
                result["errors"][section_name] = section_errors
                result["valid"] = False

            # Get effective configuration
            effective_section = section.get_effective_config(section_data, env_vars)
            if effective_section:
                result["effective_config"][section_name] = effective_section

        # Run global validators
        global_errors = []
        for validator in self.global_validators:
            try:
                validator_errors = validator(result["effective_config"])
                global_errors.extend(validator_errors)
            except Exception as e:
                global_errors.append(f"Global validator error: {e}")

        if global_errors:
            result["errors"]["_global"] = global_errors
            result["valid"] = False

        return result

    def get_field_documentation(self) -> Dict[str, Any]:
        """
        Get documentation for all configuration fields.

        Returns:
            Dictionary with field documentation
        """
        documentation = {
            "schema_name": self.name,
            "schema_version": self.version,
            "sections": {},
        }

        for section_name, section in self.sections.items():
            section_doc = {
                "name": section.name,
                "description": section.description,
                "fields": {},
            }

            for field_name, field in section.fields.items():
                section_doc["fields"][field_name] = field.to_dict()

            documentation["sections"][section_name] = section_doc

        return documentation

    def generate_example_config(self) -> Dict[str, Any]:
        """
        Generate an example configuration with default values.

        Returns:
            Dictionary with example configuration
        """
        example_config = {}

        for section_name, section in self.sections.items():
            section_config = {}

            for field_name, field in section.fields.items():
                if field.default_value is not None:
                    section_config[field_name] = field.default_value
                elif field.validation_level == ConfigValidationLevel.REQUIRED:
                    # Provide example values for required fields
                    section_config[field_name] = self._get_example_value(field)

            if section_config:
                example_config[section_name] = section_config

        return example_config

    def _get_example_value(self, field: ConfigField) -> Any:
        """Get an example value for a field based on its type."""
        if field.field_type == ConfigFieldType.STRING:
            return f"example_{field.name}"
        elif field.field_type == ConfigFieldType.INTEGER:
            return 42
        elif field.field_type == ConfigFieldType.FLOAT:
            return 3.14
        elif field.field_type == ConfigFieldType.BOOLEAN:
            return True
        elif field.field_type == ConfigFieldType.LIST:
            return ["item1", "item2"]
        elif field.field_type == ConfigFieldType.DICT:
            return {"key": "value"}
        elif field.field_type == ConfigFieldType.PATH:
            return "/path/to/file"
        elif field.field_type == ConfigFieldType.URL:
            return "https://example.com"
        elif field.field_type == ConfigFieldType.EMAIL:
            return "user@example.com"
        else:
            return None
