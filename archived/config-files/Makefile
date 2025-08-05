# Makefile for ePubs Accessibility Enhancement Project
# Provides common development commands for macOS and Ubuntu
# Usage: make <target>

# Configuration
PYTHON := python3.11
PIP := pip
VENV_DIR := venv
PROJECT_NAME := epubs-accessibility
PACKAGE_DIR := processor/unified_project/src
TESTS_DIR := tests
CI_REPORTS_DIR := ci_reports

# Platform detection
UNAME_S := $(shell uname -s)
UNAME_M := $(shell uname -m)
IS_MACOS := $(filter Darwin,$(UNAME_S))
IS_LINUX := $(filter Linux,$(UNAME_S))
IS_APPLE_SILICON := $(filter arm64,$(UNAME_M))

# Colors for output
RED := \033[0;31m
GREEN := \033[0;32m
YELLOW := \033[1;33m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Default target
.DEFAULT_GOAL := help

# Help target
.PHONY: help
help: ## Show this help message
	@echo "$(BLUE)ePubs Accessibility Enhancement - Makefile$(NC)"
	@echo "=================================================="
	@echo "Platform: $(UNAME_S) $(UNAME_M)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(BLUE)%-20s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Environment setup
.PHONY: setup
setup: ## Set up development environment (platform-specific)
	@echo "$(BLUE)Setting up development environment...$(NC)"
ifdef IS_MACOS
	@echo "$(GREEN)Running macOS setup...$(NC)"
	@chmod +x setup_macos.sh
	@./setup_macos.sh
else ifdef IS_LINUX
	@echo "$(GREEN)Running Ubuntu setup...$(NC)"
	@chmod +x setup_ubuntu.sh
	@./setup_ubuntu.sh
else
	@echo "$(RED)Unsupported platform: $(UNAME_S)$(NC)"
	@exit 1
endif

.PHONY: venv
venv: ## Create virtual environment
	@echo "$(BLUE)Creating virtual environment...$(NC)"
	@$(PYTHON) -m venv $(VENV_DIR)
	@echo "$(GREEN)Virtual environment created. Activate with: source $(VENV_DIR)/bin/activate$(NC)"

.PHONY: install
install: ## Install package and dependencies
	@echo "$(BLUE)Installing package and dependencies...$(NC)"
	@$(PIP) install --upgrade pip setuptools wheel
ifdef IS_MACOS
ifdef IS_APPLE_SILICON
	@$(PIP) install -e .[ml,apple,advanced,dev]
else
	@$(PIP) install -e .[ml,advanced,dev]
endif
else
	@$(PIP) install -e .[ml,advanced,dev]
endif
	@echo "$(GREEN)Installation completed$(NC)"

.PHONY: install-hooks
install-hooks: ## Install pre-commit hooks
	@echo "$(BLUE)Installing pre-commit hooks...$(NC)"
	@$(PIP) install pre-commit
	@pre-commit install
	@pre-commit install --hook-type commit-msg
	@echo "$(GREEN)Pre-commit hooks installed$(NC)"

# Development commands
.PHONY: format
format: ## Format code with black and isort
	@echo "$(BLUE)Formatting code...$(NC)"
	@black --line-length 88 .
	@isort --profile black --line-length 88 .
	@echo "$(GREEN)Code formatting completed$(NC)"

.PHONY: format-check
format-check: ## Check code formatting without making changes
	@echo "$(BLUE)Checking code formatting...$(NC)"
	@black --check --diff --line-length 88 .
	@isort --check-only --diff --profile black --line-length 88 .

.PHONY: lint
lint: ## Run linting checks
	@echo "$(BLUE)Running linting checks...$(NC)"
	@flake8 --max-line-length=88 --extend-ignore=E203,W503 $(PACKAGE_DIR)/ $(TESTS_DIR)/
	@echo "$(GREEN)Linting completed$(NC)"

.PHONY: type-check
type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(NC)"
	@mypy $(PACKAGE_DIR)/ --ignore-missing-imports --disallow-untyped-defs
	@echo "$(GREEN)Type checking completed$(NC)"

.PHONY: security
security: ## Run security checks
	@echo "$(BLUE)Running security checks...$(NC)"
	@bandit -r $(PACKAGE_DIR)/ -f json -o bandit-report.json || true
	@safety check --json --output safety-report.json || true
	@echo "$(GREEN)Security checks completed$(NC)"

# Testing commands
.PHONY: test
test: ## Run all tests
	@echo "$(BLUE)Running tests...$(NC)"
	@pytest --verbose --tb=short

.PHONY: test-cov
test-cov: ## Run tests with coverage
	@echo "$(BLUE)Running tests with coverage...$(NC)"
	@pytest --verbose --tb=short --cov=$(PACKAGE_DIR) --cov-report=term-missing --cov-report=html:htmlcov --cov-report=xml:coverage.xml

.PHONY: test-fast
test-fast: ## Run tests in parallel (faster)
	@echo "$(BLUE)Running tests in parallel...$(NC)"
	@pytest --verbose --tb=short -n auto

.PHONY: test-integration
test-integration: ## Run integration tests only
	@echo "$(BLUE)Running integration tests...$(NC)"
	@pytest --verbose --tb=short -m integration

.PHONY: test-unit
test-unit: ## Run unit tests only
	@echo "$(BLUE)Running unit tests...$(NC)"
	@pytest --verbose --tb=short -m "not integration"

# Quality assurance
.PHONY: qa
qa: format-check lint type-check security test-cov ## Run all quality assurance checks
	@echo "$(GREEN)All quality assurance checks completed$(NC)"

.PHONY: ci
ci: ## Run full CI pipeline locally
	@echo "$(BLUE)Running local CI pipeline...$(NC)"
	@chmod +x local_ci.sh
	@./local_ci.sh

.PHONY: validate
validate: ## Validate development environment
	@echo "$(BLUE)Validating development environment...$(NC)"
	@$(PYTHON) validate_environment.py

# Application commands
.PHONY: run
run: ## Run the main application with help
	@$(PYTHON) -m $(PACKAGE_DIR).main --help

.PHONY: cache-stats
cache-stats: ## Show cache statistics
	@echo "$(BLUE)Cache statistics:$(NC)"
	@$(PYTHON) -m $(PACKAGE_DIR).main cache stats

.PHONY: cache-clear
cache-clear: ## Clear all caches
	@echo "$(BLUE)Clearing caches...$(NC)"
	@$(PYTHON) -m $(PACKAGE_DIR).main cache clear
	@echo "$(GREEN)Caches cleared$(NC)"

.PHONY: platform-info
platform-info: ## Show platform information and optimizations
	@echo "$(BLUE)Platform information:$(NC)"
	@$(PYTHON) -c "from $(PACKAGE_DIR).utils.platform_detection import get_platform_info, get_optimization_recommendations; import json; info = get_platform_info(); recs = get_optimization_recommendations(); print('Platform Info:'); print(json.dumps(info, indent=2)); print('\nOptimization Recommendations:'); print(json.dumps(recs, indent=2))"

# Benchmarking
.PHONY: benchmark
benchmark: ## Run performance benchmarks
	@echo "$(BLUE)Running performance benchmarks...$(NC)"
	@$(PYTHON) -c "import time; import sys; sys.path.insert(0, '$(PACKAGE_DIR)'); from utils.platform_detection import get_platform_info; start=time.time(); [get_platform_info() for _ in range(100)]; print(f'Platform detection (100x): {time.time()-start:.3f}s')"

.PHONY: benchmark-full
benchmark-full: ## Run comprehensive benchmarks
	@echo "$(BLUE)Running comprehensive benchmarks...$(NC)"
	@mkdir -p $(CI_REPORTS_DIR)
	@$(PYTHON) -c "
import time
import json
import sys
from pathlib import Path

sys.path.insert(0, '$(PACKAGE_DIR)')

try:
    from utils.platform_detection import get_platform_info, get_optimization_recommendations
    
    benchmarks = {}
    
    # Platform detection benchmark
    start_time = time.time()
    for _ in range(100):
        info = get_platform_info()
    benchmarks['platform_detection_100x'] = time.time() - start_time
    
    # Optimization recommendations benchmark
    start_time = time.time()
    for _ in range(100):
        recs = get_optimization_recommendations()
    benchmarks['optimization_recs_100x'] = time.time() - start_time
    
    # Import time benchmark
    start_time = time.time()
    from enhancers import OCREnhancer, PDFEnhancer
    benchmarks['import_time'] = time.time() - start_time
    
    # Save results
    with open('$(CI_REPORTS_DIR)/benchmarks.json', 'w') as f:
        json.dump(benchmarks, f, indent=2)
    
    print('Benchmark Results:')
    for name, duration in benchmarks.items():
        print(f'  {name}: {duration:.3f}s')
        
except Exception as e:
    print(f'Benchmark failed: {e}')
    sys.exit(1)
"

# Documentation
.PHONY: docs
docs: ## Generate documentation
	@echo "$(BLUE)Generating documentation...$(NC)"
	@mkdir -p docs
	@echo "$(YELLOW)Documentation generation not yet implemented$(NC)"

.PHONY: docs-serve
docs-serve: ## Serve documentation locally
	@echo "$(BLUE)Serving documentation...$(NC)"
	@echo "$(YELLOW)Documentation serving not yet implemented$(NC)"

# Cleanup commands
.PHONY: clean
clean: ## Clean up generated files
	@echo "$(BLUE)Cleaning up generated files...$(NC)"
	@rm -rf build/
	@rm -rf dist/
	@rm -rf *.egg-info/
	@rm -rf .pytest_cache/
	@rm -rf .coverage
	@rm -rf htmlcov/
	@rm -rf .mypy_cache/
	@rm -rf $(CI_REPORTS_DIR)/
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name "*~" -delete 2>/dev/null || true
	@echo "$(GREEN)Cleanup completed$(NC)"

.PHONY: clean-cache
clean-cache: ## Clean up cache directories
	@echo "$(BLUE)Cleaning cache directories...$(NC)"
ifdef IS_MACOS
	@rm -rf ~/.epubs/cache/* 2>/dev/null || true
	@rm -rf ~/.cache/epubs/* 2>/dev/null || true
else
	@rm -rf ~/.cache/epubs/* 2>/dev/null || true
	@rm -rf ~/.epubs/logs/* 2>/dev/null || true
endif
	@echo "$(GREEN)Cache cleanup completed$(NC)"

.PHONY: clean-all
clean-all: clean clean-cache ## Clean everything including caches
	@echo "$(GREEN)Complete cleanup finished$(NC)"

# Distribution
.PHONY: build
build: ## Build distribution packages
	@echo "$(BLUE)Building distribution packages...$(NC)"
	@$(PIP) install build
	@python -m build
	@echo "$(GREEN)Build completed$(NC)"

.PHONY: check-dist
check-dist: ## Check distribution packages
	@echo "$(BLUE)Checking distribution packages...$(NC)"
	@$(PIP) install twine
	@twine check dist/*
	@echo "$(GREEN)Distribution check completed$(NC)"

# Development utilities
.PHONY: dev-deps
dev-deps: ## Install development dependencies only
	@echo "$(BLUE)Installing development dependencies...$(NC)"
	@$(PIP) install -e .[dev]

.PHONY: freeze
freeze: ## Generate requirements.txt from current environment
	@echo "$(BLUE)Generating requirements.txt...$(NC)"
	@$(PIP) freeze > requirements-frozen.txt
	@echo "$(GREEN)Requirements saved to requirements-frozen.txt$(NC)"

.PHONY: upgrade-deps
upgrade-deps: ## Upgrade all dependencies
	@echo "$(BLUE)Upgrading dependencies...$(NC)"
	@$(PIP) install --upgrade pip setuptools wheel
	@$(PIP) install -e .[ml,advanced,dev] --upgrade
	@echo "$(GREEN)Dependencies upgraded$(NC)"

# Status and information
.PHONY: status
status: ## Show project status and environment info
	@echo "$(BLUE)ePubs Accessibility Enhancement - Project Status$(NC)"
	@echo "=================================================="
	@echo "Platform: $(UNAME_S) $(UNAME_M)"
	@echo "Python: $$($(PYTHON) --version 2>/dev/null || echo 'Not found')"
	@echo "Virtual Environment: $${VIRTUAL_ENV:-Not activated}"
	@echo "Git Branch: $$(git branch --show-current 2>/dev/null || echo 'Not a git repo')"
	@echo "Git Status: $$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ') modified files"
	@echo ""
	@echo "$(GREEN)Quick Commands:$(NC)"
	@echo "  make setup     - Platform-specific environment setup"
	@echo "  make install   - Install package and dependencies"
	@echo "  make test      - Run tests"
	@echo "  make ci        - Run full CI pipeline"
	@echo "  make clean     - Clean up generated files"

# Watch mode (requires entr or similar)
.PHONY: watch-test
watch-test: ## Watch files and run tests on change (requires entr)
	@echo "$(BLUE)Watching for changes and running tests...$(NC)"
	@echo "$(YELLOW)Requires 'entr' to be installed$(NC)"
	@find $(PACKAGE_DIR) $(TESTS_DIR) -name "*.py" | entr -c make test

.PHONY: watch-format
watch-format: ## Watch files and format on change (requires entr)
	@echo "$(BLUE)Watching for changes and formatting code...$(NC)"
	@echo "$(YELLOW)Requires 'entr' to be installed$(NC)"
	@find $(PACKAGE_DIR) -name "*.py" | entr -c make format

# Special targets for different environments
.PHONY: docker-build
docker-build: ## Build Docker image
	@echo "$(BLUE)Building Docker image...$(NC)"
	@docker build -t $(PROJECT_NAME) .
	@echo "$(GREEN)Docker image built$(NC)"

.PHONY: docker-run
docker-run: ## Run application in Docker
	@echo "$(BLUE)Running application in Docker...$(NC)"
	@docker run --rm -it $(PROJECT_NAME) --help

# Targets that don't create files
.PHONY: all
all: install format lint type-check test ## Install, format, lint, type-check, and test

# Platform-specific targets
ifdef IS_MACOS
.PHONY: macos-optimizations
macos-optimizations: ## Show macOS-specific optimizations
	@echo "$(BLUE)macOS Optimizations:$(NC)"
ifdef IS_APPLE_SILICON
	@echo "  ✅ Apple Silicon detected"
	@echo "  🚀 MLX acceleration available"
else
	@echo "  ℹ️  Intel Mac detected"
endif
	@echo "  📦 Homebrew dependencies managed"
	@echo "  ⚡ macOS-specific performance tuning enabled"
endif

ifdef IS_LINUX
.PHONY: linux-optimizations
linux-optimizations: ## Show Linux-specific optimizations
	@echo "$(BLUE)Linux Optimizations:$(NC)"
	@echo "  📦 APT dependencies managed"
	@echo "  🐧 Linux-specific performance tuning enabled"
	@if command -v nvidia-smi >/dev/null 2>&1; then echo "  🎮 NVIDIA GPU detected"; else echo "  🖥️  CPU-only processing"; fi
endif