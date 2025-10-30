# Scripts Directory

This directory contains utility scripts, examples, and development tools for the ePubs Accessibility Enhancement Project.

## Structure

### `/setup/`
Setup and installation scripts:
- `install_phase2b.sh` - Phase 2B ML dependencies installation script

### `/examples/`
Demonstration and example scripts:
- `ml_demo.py` - ML-Enhanced Document Processing demonstration
- `phase1_architecture_demo.py` - Phase 1 parallel processing architecture demo

### `/tests/`
Development and testing scripts:
- `test_ml_fix.py` - ThreadSafeAdaptiveMLEnhancer document_profiles fix test
- `test_ml_comprehensive_fix.py` - Comprehensive ML component testing
- `test_current_ml_status.py` - ML enhancer status verification
- `test_ml_implementation_status.py` - ML implementation structure analysis
- `test_code_fix_verification.py` - Code change verification
- `test_worker_count_fix.py` - Worker count fix verification

## Usage

### Running Examples
```bash
# From project root
python scripts/examples/ml_demo.py
python scripts/examples/phase1_architecture_demo.py
```

### Running Tests
```bash
# From project root
python scripts/tests/test_ml_fix.py
python scripts/tests/test_worker_count_fix.py
```

### Setup Scripts
```bash
# Make executable and run
chmod +x scripts/setup/install_phase2b.sh
./scripts/setup/install_phase2b.sh
```

## Notes

- All scripts are designed to be run from the project root directory
- Import paths have been updated to work with the new directory structure
- Test scripts are for development purposes and are excluded from the main repository via .gitignore
