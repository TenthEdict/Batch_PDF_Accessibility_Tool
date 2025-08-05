# Comprehensive To-Do List for ePubs_main Project Review (Single-User, macOS/Ubuntu)

## 🔴 Priority 1: Critical Fixes & Maintenance

### Dependency Management
- [ ] **Synchronize dependency specifications** ⚠️
  - [ ] Audit differences between requirements.txt and pyproject.toml
  - [ ] Remove pdfservices-sdk dependency (Adobe services removed)
  - [ ] Consolidate into single source of truth (prefer pyproject.toml)
  - [ ] Add automated dependency sync check to pre-commit hooks
  - [ ] Create platform-specific dependency groups (macOS vs Ubuntu)

### Test Infrastructure
- [ ] **Restore missing test directory structure** 🧪
  - [ ] Create tests/ directory at project root
  - [ ] Move processor/unified_project/tests/* to root tests/
  - [ ] Add __init__.py files for proper test discovery
  - [ ] Create conftest.py with shared fixtures
  - [ ] Verify pytest configuration in pyproject.toml works
  - [ ] Add platform-specific test markers (@pytest.mark.macos, @pytest.mark.ubuntu)

### Code Organization
- [ ] **Integrate standalone scripts into unified architecture** 📁
  - [ ] Move advanced_batch_processor.py into processor/unified_project/src/batch/
  - [ ] Refactor to use service container and dependency injection
  - [ ] Create proper CLI command: `epubs batch-process`
  - [ ] Remove duplicate functionality with process_directory.py

## 🟡 Priority 2: Architecture Improvements

### Utilize Defined Optional Dependencies
- [ ] **Implement ML-powered enhancements** 🤖
  - [ ] Create MLEnhancer using torch/transformers dependencies
  - [ ] Add document structure prediction using Hugging Face models
  - [ ] Implement intelligent table/figure detection
  - [ ] Add to enhancement pipeline as optional stage
  - [ ] Create local model caching to avoid repeated downloads

- [ ] **Apple Silicon optimizations** 🍎 (macOS specific)
  - [ ] Create AppleOptimizedEnhancer using mlx-vlm
  - [ ] Add M1/M2/M3 specific acceleration for OCR
  - [ ] Benchmark performance improvements vs standard processing
  - [ ] Auto-detect Apple Silicon and enable optimizations
  - [ ] Fall back gracefully on Intel Macs

- [ ] **Advanced document analysis** 📊
  - [ ] Integrate docling-core for enhanced structure detection
  - [ ] Create AdvancedAnalysisEnhancer
  - [ ] Add to academic mode pipeline
  - [ ] Store analysis results locally for reprocessing

### Local Caching System
- [ ] **Implement file-based caching** 💾
  - [ ] Create local SQLite cache database
  - [ ] Cache OCR results by document hash
  - [ ] Store intermediate processing results
  - [ ] Add cache management CLI commands:
    - [ ] `epubs cache clear` - Clear all cache
    - [ ] `epubs cache stats` - Show cache usage
    - [ ] `epubs cache prune` - Remove old entries
  - [ ] Use ~/.epubs/cache/ on macOS, ~/.cache/epubs/ on Ubuntu

## 🟢 Priority 3: DevOps & Local Development

### Local Development Environment
- [ ] **Platform-specific setup scripts** 🔧
  - [ ] Create setup_macos.sh:
    - [ ] Install Homebrew dependencies (tesseract, poppler, etc.)
    - [ ] Configure optimal Tesseract data paths
    - [ ] Set up Apple Silicon specific optimizations
  - [ ] Create setup_ubuntu.sh:
    - [ ] Install apt packages
    - [ ] Configure system paths
    - [ ] Set up GPU support if available
  - [ ] Add development environment validation script

### Automated Testing & Quality
- [ ] **Local CI simulation** 🔄
  - [ ] Create local_ci.sh script that runs all checks
  - [ ] Add pre-commit hooks:
    - [ ] Python formatting (black, isort)
    - [ ] Type checking (mypy)
    - [ ] Linting (flake8)
    - [ ] Dependency sync check
  - [ ] Create Makefile with common commands:
    - [ ] `make test` - Run all tests
    - [ ] `make format` - Format code
    - [ ] `make install` - Platform-aware installation
    - [ ] `make benchmark` - Run performance tests

### Performance Monitoring
- [ ] **Local performance tracking** 📈
  - [ ] Add simple metrics collection to SQLite
  - [ ] Track per-document processing times
  - [ ] Create performance report generator
  - [ ] Add `epubs stats` command to view metrics
  - [ ] Compare performance between macOS/Ubuntu

### Docker Improvements (Local Use)
- [ ] **Optimize for local development** 🐳
  - [ ] Create lightweight development container
  - [ ] Add docker-compose for local testing
  - [ ] Mount local directories for easy debugging
  - [ ] Create platform-specific Dockerfiles:
    - [ ] Dockerfile.macos (with macOS specific optimizations)
    - [ ] Dockerfile.ubuntu (with Ubuntu optimizations)

## 🔵 Priority 4: Feature Enhancements

### Input Validation
- [ ] **Local file validation** ✅
  - [ ] Expand src/validation/ module
  - [ ] Add validators:
    - [ ] PDF structure validation
    - [ ] File size warnings (not limits)
    - [ ] Corrupted file detection
    - [ ] Content type verification
  - [ ] Create validation report for each batch
  - [ ] Add `--skip-validation` flag for trusted files

### Processing Features
- [ ] **Local parallel processing** ⚡
  - [ ] Implement multiprocessing for batch jobs
  - [ ] Auto-detect optimal CPU core usage
  - [ ] Add progress bar with rich library
  - [ ] Create `--parallel` flag with core count option
  - [ ] Platform-specific optimizations:
    - [ ] Use Grand Central Dispatch on macOS
    - [ ] Use standard multiprocessing on Ubuntu

- [ ] **Format support expansion** 📄
  - [ ] Utilize defined doc dependencies (docx, pptx, xlsx)
  - [ ] Create format converters to PDF
  - [ ] Add EPUB output support
  - [ ] Implement markdown output for notes
  - [ ] Add `epubs convert` command

### Local Workflow Features
- [ ] **Watch mode for folders** 👁️
  - [ ] Add `epubs watch` command
  - [ ] Monitor input directory for new files
  - [ ] Auto-process new documents
  - [ ] Move completed files to done/ directory
  - [ ] Platform-specific file watching:
    - [ ] FSEvents on macOS
    - [ ] inotify on Ubuntu

## ⚪ Priority 5: Documentation & Quality

### Documentation for Single User
- [ ] **Simplified documentation** 📚
  - [ ] Create QUICKSTART.md with 5-minute setup
  - [ ] Add cookbook with common workflows
  - [ ] Document all CLI commands with examples
  - [ ] Create troubleshooting guide for common issues
  - [ ] Platform-specific installation guides

- [ ] **Configuration documentation** 🚀
  - [ ] Document all YAML configuration options
  - [ ] Create example configs for different use cases
  - [ ] Add performance tuning guide
  - [ ] Document cache management

### Code Quality
- [ ] **Testing improvements** 🎯
  - [ ] Add fixture documents for testing
  - [ ] Create regression test suite
  - [ ] Add performance benchmarks
  - [ ] Platform-specific test cases

- [ ] **User experience enhancements** 💫
  - [ ] Improve error messages with solutions
  - [ ] Add verbose logging options
  - [ ] Create interactive mode for single documents
  - [ ] Add dry-run option for testing

## 📊 Metrics for Success (Local Use)

### Performance Targets
- [ ] Process 100-page document in < 30 seconds on M1 Mac
- [ ] Process 100-page document in < 45 seconds on Ubuntu
- [ ] Batch process 100 documents without memory issues
- [ ] Start-up time < 2 seconds

### Quality Targets
- [ ] 100% success rate on valid PDFs
- [ ] Graceful handling of corrupted files
- [ ] Clear error messages for all failure modes
- [ ] 100% PDF/UA compliance for output

### User Experience
- [ ] Single command to process directory
- [ ] Clear progress indication
- [ ] Resumable batch processing
- [ ] Easy configuration management

## 🎯 Quick Wins (Can be done immediately)

1. [ ] Fix dependency sync issues
2. [ ] Create .gitignore entries for cache/, logs/
3. [ ] Add shell completion for CLI (bash/zsh)
4. [ ] Create example configuration files
5. [ ] Add `--dry-run` flag
6. [ ] Create `epubs doctor` diagnostic command
7. [ ] Add colored terminal output
8. [ ] Create benchmark suite
9. [ ] Add file watcher script
10. [ ] Write platform-specific READMEs

## 📈 Progressive Enhancement Path

### Phase 1 (Next 2 weeks)
- Fix critical dependency issues
- Integrate standalone scripts
- Create platform setup scripts

### Phase 2 (Month 1)
- Implement ML enhancements
- Add Apple Silicon optimizations
- Create local caching system

### Phase 3 (Month 2)
- Add watch mode
- Implement parallel processing
- Expand format support

### Phase 4 (Month 3)
- Complete test coverage
- Optimize performance
- Polish user experience

## 🔍 Platform-Specific Optimizations

### macOS Specific
1. **Leverage Apple frameworks** for PDF processing
2. **Use Spotlight** for document indexing
3. **Integrate with Finder** quick actions
4. **Optimize for Apple Silicon** chips
5. **Use native macOS notifications** for completion

### Ubuntu Specific
1. **Optimize for server environments**
2. **Add systemd service** for watch mode
3. **Use native Linux tools** for performance
4. **GPU acceleration** support where available
5. **Integrate with desktop notifications**

## 💡 Local Workflow Enhancements

1. **Quick enhancement mode** - Drag & drop to dock icon (macOS)
2. **Batch templates** - Save processing configurations
3. **History tracking** - Remember processed files
4. **Incremental processing** - Skip unchanged files
5. **Local model repository** - Cache ML models offline

---

**Note**: This revised to-do list focuses on single-user, local usage on macOS and Ubuntu platforms. All API-related items have been removed, and platform-specific optimizations have been emphasized throughout.
