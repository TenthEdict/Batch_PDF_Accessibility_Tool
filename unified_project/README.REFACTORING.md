# ePubs Accessibility Project - Refactoring Documentation

## Overview

This document provides details about the refactoring work performed on the ePubs Accessibility Project codebase. The refactoring was guided by the following principles:

1. **Proper separation of concerns**
2. **Clear interfaces between components**
3. **Dependency injection for testability**
4. **Configuration-driven architecture**
5. **Rule-based validation**

## Core Architecture

The refactored architecture implements a clean, modular design with the following key components:

### Core Interfaces

All major components now implement abstract base classes defined in `src/core/interfaces.py`:

- `DocumentProcessor`: Abstract interface for document processing pipelines
- `Enhancer`: Abstract interface for document enhancement components
- `Validator`: Abstract interface for accessibility validation
- `OCRProcessor`: Abstract interface for OCR processing
- `MetadataEditor`: Abstract interface for document metadata management
- `ConfigurationProvider`: Abstract interface for configuration management

### Dependency Injection

The codebase now uses dependency injection through the `ServiceContainer` class in `src/core/service_container.py`. This allows for:

- Loose coupling between components
- Easy unit testing with mock dependencies
- Runtime configuration of component implementations

### Configuration Management

Configuration has been unified with a hierarchical approach:

- Default configuration in `config/default.yaml`
- Environment-specific overrides
- Component-specific settings

The `YamlConfigurationProvider` class in `src/core/config.py` handles configuration loading and access.

## Enhancement System

The enhancement system has been completely refactored with a clean inheritance hierarchy:

- `EnhancerBase`: Base class with common functionality
- `PDFEnhancer`: PDF-specific implementation
- `BasicEnhancer`: Implementation of basic accessibility features

Enhancement capabilities are now discoverable through the `get_capabilities()` method.

## Validation System

The validation system has been refactored to use a rule-based approach:

- `ValidationRule`: Abstract base class for individual validation rules
- `ValidationRuleSet`: Collection of rules with weight calculation
- Predefined rule sets for different validation levels:
  - `basic_pdf_ruleset`: Basic accessibility features
  - `structure_pdf_ruleset`: Document structure features
  - `pdfua_ruleset`: Complete PDF/UA compliance

This approach allows for:
- Composable validation rules
- Customizable rule weights
- Detailed validation reports
- Specific recommendations for failing rules

## OCR Processing

OCR processing has been organized into specialized processors:

- `OCRProcessor`: Abstract base interface
- Specialized implementations for different document types

## Next Steps

The following tasks are still pending:

1. **Complete CLI integration**: Update `main.py` to use the new architectural components
2. **Create unit tests**: Add comprehensive unit tests for all components
3. **Update documentation**: Create user and developer documentation
4. **Implement remaining enhancers**: Add advanced and PDF/UA enhancers

## Migration Guide

When migrating existing code to the new architecture:

1. Identify the appropriate interface for your component
2. Create a new implementation class inheriting from the base class
3. Register your implementation with the service container
4. Update any dependencies to use the service container

Example:

```python
from core.interfaces import Enhancer
from core.service_container import get_container

# Register your implementation
container = get_container()
container.register("my_enhancer", lambda c: MyEnhancer())

# Get an implementation
enhancer = container.get_typed("my_enhancer", Enhancer)
```