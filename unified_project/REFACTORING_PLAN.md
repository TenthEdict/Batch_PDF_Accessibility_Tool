# ePubs Accessibility Project Refactoring Plan

## Current Issues
1. Fragmented functionality across multiple packages
2. Duplicate code and overlapping features
3. Multiple input/output directories
4. Inconsistent configuration approaches
5. Redundant environment setups
6. Scattered unit tests

## Refactoring Plan

### Phase 1: Consolidation
- [x] Archive completed projects (MoslerThesis)
- [x] Create unified project structure
- [x] Consolidate requirements
- [x] Create unified setup.py and Dockerfile

### Phase 2: Code Organization
1. **Core Module Structure**
   - `src/ocr/` - OCR processing from brodie_code and smolDocling
   - `src/accessibility/` - PDF accessibility features
   - `src/enhancement/` - Document quality improvement
   - `src/metadata/` - PDF metadata management
   - `src/validation/` - Accessibility validation
   - `src/utils/` - Common utilities

2. **Configuration**
   - Unified configuration system in `config/`
   - Environment-specific settings
   - Feature toggles

3. **CLI Interface**
   - Single entry point with subcommands
   - Consistent parameter handling

### Phase 3: Feature Integration
1. **OCR Integration**
   - Merge OCR capabilities from brodie_code and smolDocling
   - Create unified historical document OCR pipeline
   - Optimize for different document types

2. **Accessibility Features**
   - Consolidate PDF/UA tagging functionality
   - Unified document structure enhancement
   - Centralized validation

3. **Metadata Management**
   - Move mai_code functionality into unified metadata module
   - Create extensible metadata handling

### Phase 4: Testing & Documentation
1. **Testing**
   - Consolidated test suite in `/tests`
   - Unit and integration tests
   - Sample documents for testing

2. **Documentation**
   - User guides
   - API documentation
   - Development guidelines

### Phase 5: Cleanup
1. Remove duplicate directories after migration
2. Remove redundant input/output directories
3. Update .gitignore
4. Remove unused dependencies