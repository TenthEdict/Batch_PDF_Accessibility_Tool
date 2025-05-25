# Dependency Migration Notice

## ✅ Migration Complete - New Installation Process

The ePubs Accessibility project has successfully migrated from multiple fragmented requirements files to a unified `pyproject.toml` dependency management system.

### What Changed

**Before (Deprecated):**
- Multiple `requirements.txt` files across directories
- Inconsistent version specifications
- Manual dependency management
- Version conflicts between components

**After (Current):**
- Single `pyproject.toml` file with unified dependencies
- Proper version pinning with compatibility ranges
- Optional dependency groups for different use cases
- Professional package metadata and CLI scripts

### New Installation Process

#### Quick Start
```bash
# Clone repository
git clone <repository_url>
cd ePubs_Main

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Unix/MacOS
# venv\Scripts\activate   # Windows

# Install core dependencies
pip install -e .
```

#### Optional Dependencies
```bash
# Web scraping capabilities
pip install -e .[web]

# Document format support (Word, PowerPoint, Excel)
pip install -e .[docs]

# Machine learning features (heavy dependencies)
pip install -e .[ml]

# Development tools
pip install -e .[dev]

# All optional dependencies
pip install -e .[all]
```

### New CLI Scripts

The migration provides unified CLI entry points:

```bash
# Academic paper processing
epubs-process-academic input.pdf output.pdf

# Web scraping
epubs-scrape --url https://example.com

# Workflow automation
epubs-automate --base-url https://example.com
```

### Benefits of Migration

1. **Consistency**: Single source of truth for all dependencies
2. **Security**: Pinned versions with security vulnerability protection
3. **Performance**: Optional heavy dependencies reduce installation time
4. **Maintainability**: Clear dependency categories and purpose
5. **Professional**: Modern Python packaging standards
6. **Extensibility**: Easy to add new optional features

### Rollback (If Needed)

If you need to rollback to the old system:
```bash
# Restore from backups
cp dependency_backups/requirements.txt.backup requirements.txt
cp dependency_backups/processor_unified_project_requirements.txt.backup processor/unified_project/requirements.txt

# Install old way
pip install -r requirements.txt
pip install -r processor/unified_project/requirements.txt
```

### Files Affected

- ✅ `pyproject.toml` - New unified dependency management
- ✅ `requirements-lock.txt` - Locked versions for reproducible builds
- 🔄 `requirements.txt` → `requirements.txt.deprecated`
- 🔄 `processor/unified_project/requirements.txt` → `requirements.txt.deprecated`
- 📁 `dependency_backups/` - Backup of old files

### Next Steps

1. Update any CI/CD pipelines to use `pip install -e .`
2. Update documentation references to new installation process
3. Test all functionality with new dependency versions
4. Remove deprecated files after confidence period (1-2 weeks)

For questions or issues, refer to the comprehensive guides:
- [INSTALLATION.md](./INSTALLATION.md) - Detailed installation guide
- [REFACTORING_PLAN.md](./REFACTORING_PLAN.md) - Complete refactoring roadmap
- [DEPENDENCY_ANALYSIS.md](./DEPENDENCY_ANALYSIS.md) - Technical dependency analysis