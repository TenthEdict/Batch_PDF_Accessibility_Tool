#!/usr/bin/env python3
"""
ePubs system configuration schema definition.

This module defines the complete configuration schema for the ePubs
Accessibility Enhancement system with validation rules.
"""

from .config_schema import (
    ConfigSchema,
    ConfigSection,
    ConfigField,
    ConfigFieldType,
    ConfigValidationLevel,
    RangeValidator,
    LengthValidator,
    PatternValidator,
    EnumValidator,
)


def create_epubs_config_schema() -> ConfigSchema:
    """
    Create the complete ePubs configuration schema.

    Returns:
        Configured ConfigSchema instance
    """
    schema = ConfigSchema("ePubs Accessibility Enhancement", "3.0")

    # Processing section
    processing_section = ConfigSection(
        name="processing", description="Document processing configuration"
    )

    processing_section.add_field(
        ConfigField(
            name="default_mode",
            field_type=ConfigFieldType.ENUM,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value="accessibility",
            description="Default processing mode",
            validators=[
                EnumValidator(["accessibility", "academic", "basic", "custom"])
            ],
            environment_variable="EPUBS_DEFAULT_MODE",
        )
    )

    processing_section.add_field(
        ConfigField(
            name="max_file_size_mb",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value=100,
            description="Maximum file size in MB",
            validators=[RangeValidator(1, 1000)],
            environment_variable="EPUBS_MAX_FILE_SIZE",
        )
    )

    processing_section.add_field(
        ConfigField(
            name="supported_formats",
            field_type=ConfigFieldType.LIST,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value=[".pdf", ".docx", ".txt"],
            description="Supported file formats",
        )
    )

    processing_section.add_field(
        ConfigField(
            name="backup_originals",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value=True,
            description="Whether to backup original files",
            environment_variable="EPUBS_BACKUP_ORIGINALS",
        )
    )

    processing_section.add_field(
        ConfigField(
            name="validate_output",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value=True,
            description="Whether to validate processed output",
        )
    )

    schema.add_section(processing_section)

    # Enhancement section
    enhancement_section = ConfigSection(
        name="enhancement", description="Document enhancement configuration"
    )

    enhancement_section.add_field(
        ConfigField(
            name="extract_title_from_h1",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Extract document title from H1 elements",
        )
    )

    enhancement_section.add_field(
        ConfigField(
            name="extract_title_from_filename",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Extract document title from filename",
        )
    )

    enhancement_section.add_field(
        ConfigField(
            name="add_pdfua_identifiers",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=False,
            description="Add PDF/UA accessibility identifiers",
        )
    )

    enhancement_section.add_field(
        ConfigField(
            name="display_doc_title",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Display document title in viewer",
        )
    )

    enhancement_section.add_field(
        ConfigField(
            name="default_language",
            field_type=ConfigFieldType.LANGUAGE,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value="en-US",
            description="Default document language",
            validators=[PatternValidator(r"^[a-z]{2}(-[A-Z]{2})?$")],
            environment_variable="EPUBS_DEFAULT_LANGUAGE",
        )
    )

    schema.add_section(enhancement_section)

    # Validation section
    validation_section = ConfigSection(
        name="validation", description="Document validation configuration"
    )

    validation_section.add_field(
        ConfigField(
            name="standards",
            field_type=ConfigFieldType.LIST,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value=["pdf_ua", "wcag_2_1"],
            description="Validation standards to apply",
        )
    )

    validation_section.add_field(
        ConfigField(
            name="generate_reports",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Generate validation reports",
        )
    )

    validation_section.add_field(
        ConfigField(
            name="report_format",
            field_type=ConfigFieldType.ENUM,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value="json",
            description="Default report format",
            validators=[EnumValidator(["json", "html", "csv", "txt"])],
        )
    )

    validation_section.add_field(
        ConfigField(
            name="fail_on_critical",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Fail processing on critical validation errors",
        )
    )

    schema.add_section(validation_section)

    # Logging section
    logging_section = ConfigSection(name="logging", description="Logging configuration")

    logging_section.add_field(
        ConfigField(
            name="level",
            field_type=ConfigFieldType.ENUM,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value="INFO",
            description="Log level",
            validators=[
                EnumValidator(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])
            ],
            environment_variable="LOG_LEVEL",
        )
    )

    logging_section.add_field(
        ConfigField(
            name="format",
            field_type=ConfigFieldType.STRING,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            description="Log message format",
        )
    )

    logging_section.add_field(
        ConfigField(
            name="file_path",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.OPTIONAL,
            description="Log file path (console only if not specified)",
            environment_variable="LOG_FILE",
        )
    )

    logging_section.add_field(
        ConfigField(
            name="max_file_size_mb",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=10,
            description="Maximum log file size in MB",
            validators=[RangeValidator(1, 100)],
        )
    )

    logging_section.add_field(
        ConfigField(
            name="backup_count",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=5,
            description="Number of backup log files to keep",
            validators=[RangeValidator(0, 50)],
        )
    )

    schema.add_section(logging_section)

    # Storage section
    storage_section = ConfigSection(
        name="storage", description="File storage configuration"
    )

    storage_section.add_field(
        ConfigField(
            name="input_directory",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value="./data/input",
            description="Default input directory",
            environment_variable="EPUBS_INPUT_DIR",
        )
    )

    storage_section.add_field(
        ConfigField(
            name="output_directory",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.REQUIRED,
            default_value="./data/output",
            description="Default output directory",
            environment_variable="EPUBS_OUTPUT_DIR",
        )
    )

    storage_section.add_field(
        ConfigField(
            name="backup_directory",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value="./data/backup",
            description="Backup directory for original files",
            environment_variable="EPUBS_BACKUP_DIR",
        )
    )

    storage_section.add_field(
        ConfigField(
            name="temp_directory",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value="./temp",
            description="Temporary processing directory",
            environment_variable="EPUBS_TEMP_DIR",
        )
    )

    storage_section.add_field(
        ConfigField(
            name="metadata_directory",
            field_type=ConfigFieldType.PATH,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value="./data/metadata",
            description="Metadata storage directory",
            environment_variable="EPUBS_METADATA_DIR",
        )
    )

    schema.add_section(storage_section)

    # Performance section
    performance_section = ConfigSection(
        name="performance", description="Performance and resource configuration"
    )

    performance_section.add_field(
        ConfigField(
            name="max_concurrent_jobs",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=2,
            description="Maximum concurrent processing jobs",
            validators=[RangeValidator(1, 10)],
            environment_variable="EPUBS_MAX_JOBS",
        )
    )

    performance_section.add_field(
        ConfigField(
            name="memory_limit_mb",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=512,
            description="Memory limit per job in MB",
            validators=[RangeValidator(128, 2048)],
        )
    )

    performance_section.add_field(
        ConfigField(
            name="timeout_seconds",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=300,
            description="Processing timeout in seconds",
            validators=[RangeValidator(30, 3600)],
        )
    )

    performance_section.add_field(
        ConfigField(
            name="cache_enabled",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Enable result caching",
        )
    )

    performance_section.add_field(
        ConfigField(
            name="cache_size_mb",
            field_type=ConfigFieldType.INTEGER,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=100,
            description="Cache size limit in MB",
            validators=[RangeValidator(10, 1000)],
        )
    )

    schema.add_section(performance_section)

    # Academic section (for academic mode)
    academic_section = ConfigSection(
        name="academic", description="Academic document processing configuration"
    )

    academic_section.add_field(
        ConfigField(
            name="enable_structure_analysis",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Enable academic document structure analysis",
        )
    )

    academic_section.add_field(
        ConfigField(
            name="extract_citations",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Extract and process citations",
        )
    )

    academic_section.add_field(
        ConfigField(
            name="generate_toc",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Generate table of contents",
        )
    )

    academic_section.add_field(
        ConfigField(
            name="preserve_formatting",
            field_type=ConfigFieldType.BOOLEAN,
            validation_level=ConfigValidationLevel.OPTIONAL,
            default_value=True,
            description="Preserve academic formatting",
        )
    )

    schema.add_section(academic_section)

    # Add global validators
    def validate_directory_structure(config: dict) -> list[str]:
        """Validate that required directories can be created."""
        errors = []
        storage_config = config.get("storage", {})

        required_dirs = ["input_directory", "output_directory"]
        for dir_key in required_dirs:
            dir_path = storage_config.get(dir_key)
            if dir_path:
                try:
                    from pathlib import Path

                    Path(dir_path).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    errors.append(f"Cannot create {dir_key} '{dir_path}': {e}")

        return errors

    def validate_performance_settings(config: dict) -> list[str]:
        """Validate performance settings are reasonable."""
        errors = []
        perf_config = config.get("performance", {})

        max_jobs = perf_config.get("max_concurrent_jobs", 2)
        memory_limit = perf_config.get("memory_limit_mb", 512)

        # Check if total memory usage is reasonable
        total_memory = max_jobs * memory_limit
        if total_memory > 4096:  # 4GB
            errors.append(f"Total memory usage ({total_memory}MB) may be too high")

        return errors

    schema.add_global_validator(validate_directory_structure)
    schema.add_global_validator(validate_performance_settings)

    return schema
