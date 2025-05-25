# DEPRECATED: Historical Document Processing

This directory contains historical document processing code that has been **DEPRECATED** as of Phase 2 of the refactoring process.

## Status: DEPRECATED

**Date**: Phase 2 Completion  
**Reason**: Historical document processing is no longer required per user requirements  
**Replacement**: Use the unified processing system in `processor/unified_project/`

## What was deprecated

- Historical OCR processing (`src/accessibility_checker/ocr/historical/`)
- Historical document analysis and preprocessing
- Era-specific word lists and patterns
- Historical font detection algorithms

## Migration Path

All modern document processing capabilities have been consolidated into the unified system:

- **OCR Processing**: Use `processor/unified_project/src/ocr/processor.py`
- **Enhancement Pipeline**: Use `processor/unified_project/src/enhancement/pipeline.py` 
- **CLI Interface**: Use the unified CLI at `epubs` command

## Backwards Compatibility

This code is preserved for reference but is no longer maintained or supported. Users should migrate to the unified processing system.

## For Developers

Do not modify or extend code in this directory. All new development should occur in the unified project structure at `processor/unified_project/`.