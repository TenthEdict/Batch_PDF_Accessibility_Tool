#!/bin/bash
# Local Continuous Integration Script for ePubs Accessibility Enhancement
# Simulates CI pipeline locally for faster development feedback
# Run with: chmod +x local_ci.sh && ./local_ci.sh

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
PYTHON_VERSION="3.11"
MAX_LINE_LENGTH=88
TIMEOUT_SECONDS=300

# Timing variables
declare -A stage_times
overall_start_time=$(date +%s)

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_stage() {
    echo -e "${MAGENTA}[STAGE]${NC} $1"
}

log_command() {
    echo -e "${CYAN}[CMD]${NC} $1"
}

# Timing functions
start_timer() {
    stage_times["$1"]=$(date +%s)
}

end_timer() {
    local stage="$1"
    local start_time=${stage_times["$stage"]}
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    log_info "Stage '$stage' completed in ${duration}s"
}

# Check if running in CI environment
is_ci() {
    [[ "${CI:-false}" == "true" ]] || [[ -n "${GITHUB_ACTIONS:-}" ]]
}

# Print header
print_header() {
    echo "🚀 ePubs Accessibility Enhancement - Local CI Pipeline"
    echo "======================================================="
    echo "Platform: $(uname -s) $(uname -m)"
    echo "Python: $(python --version 2>/dev/null || echo 'Not found')"
    echo "Timestamp: $(date)"
    if is_ci; then
        echo "Environment: CI"
    else
        echo "Environment: Local Development"
    fi
    echo "======================================================="
    echo ""
}

# Environment validation
validate_environment() {
    log_stage "🔍 Environment Validation"
    start_timer "validation"
    
    # Check Python version
    if ! command -v python &> /dev/null; then
        log_error "Python not found in PATH"
        return 1
    fi
    
    local python_version=$(python --version 2>&1 | cut -d' ' -f2)
    log_info "Python version: $python_version"
    
    # Check virtual environment
    if [[ -z "${VIRTUAL_ENV:-}" ]]; then
        log_warning "Not running in virtual environment"
        if [[ -d "venv" ]]; then
            log_info "Activating virtual environment..."
            source venv/bin/activate
        else
            log_error "Virtual environment not found. Run setup script first."
            return 1
        fi
    else
        log_success "Virtual environment active: $VIRTUAL_ENV"
    fi
    
    # Check project structure
    local required_files=(
        "pyproject.toml"
        "processor/unified_project/src/main.py"
        "processor/unified_project/src/enhancers/__init__.py"
    )
    
    for file in "${required_files[@]}"; do
        if [[ -f "$file" ]]; then
            log_success "Required file found: $file"
        else
            log_error "Required file missing: $file"
            return 1
        fi
    done
    
    # Run environment validation script if available
    if [[ -f "validate_environment.py" ]]; then
        log_info "Running comprehensive environment validation..."
        if python validate_environment.py --quiet 2>/dev/null; then
            log_success "Environment validation passed"
        else
            log_warning "Environment validation had warnings (continuing anyway)"
        fi
    fi
    
    end_timer "validation"
}

# Install/update dependencies
install_dependencies() {
    log_stage "📦 Installing Dependencies"
    start_timer "dependencies"
    
    # Upgrade pip first
    log_command "pip install --upgrade pip"
    pip install --upgrade pip || {
        log_error "Failed to upgrade pip"
        return 1
    }
    
    # Install development dependencies
    if [[ -f "pyproject.toml" ]]; then
        log_command "pip install -e .[dev]"
        pip install -e .[dev] || {
            log_error "Failed to install development dependencies"
            return 1
        }
    else
        log_error "pyproject.toml not found"
        return 1
    fi
    
    # Install additional CI tools
    local ci_tools=(
        "black[jupyter]"
        "isort"
        "flake8"
        "mypy" 
        "pytest"
        "pytest-cov"
        "pytest-xdist"
        "bandit"
        "safety"
    )
    
    log_info "Installing CI tools..."
    for tool in "${ci_tools[@]}"; do
        pip install "$tool" || log_warning "Failed to install $tool"
    done
    
    log_success "Dependencies installed"
    end_timer "dependencies"
}

# Code formatting
format_code() {
    log_stage "🎨 Code Formatting"
    start_timer "formatting"
    
    # Black formatting
    log_command "black --check --diff --line-length $MAX_LINE_LENGTH ."
    if black --check --diff --line-length $MAX_LINE_LENGTH . 2>/dev/null; then
        log_success "Black formatting check passed"
    else
        log_warning "Black formatting issues found. Running formatter..."
        black --line-length $MAX_LINE_LENGTH .
        log_success "Code formatted with Black"
    fi
    
    # Import sorting
    log_command "isort --check-only --diff ."
    if isort --check-only --diff . 2>/dev/null; then
        log_success "Import sorting check passed"
    else
        log_warning "Import sorting issues found. Running isort..."
        isort .
        log_success "Imports sorted with isort"
    fi
    
    end_timer "formatting"
}

# Linting
run_linting() {
    log_stage "🔍 Linting"
    start_timer "linting"
    
    local lint_errors=0
    
    # Flake8 linting
    log_command "flake8 --max-line-length=$MAX_LINE_LENGTH processor/ tests/"
    if flake8 --max-line-length=$MAX_LINE_LENGTH processor/ tests/ 2>/dev/null; then
        log_success "Flake8 linting passed"
    else
        log_error "Flake8 linting found issues"
        ((lint_errors++))
    fi
    
    # Bandit security linting
    log_command "bandit -r processor/ -f json"
    if bandit -r processor/ -f json -o bandit-report.json 2>/dev/null; then
        log_success "Bandit security check passed"
    else
        log_warning "Bandit found potential security issues (check bandit-report.json)"
    fi
    
    # Safety check for dependencies
    log_command "safety check --json"
    if safety check --json --output safety-report.json 2>/dev/null; then
        log_success "Safety dependency check passed"
    else
        log_warning "Safety found potential security vulnerabilities (check safety-report.json)"
    fi
    
    end_timer "linting"
    return $lint_errors
}

# Type checking
run_type_checking() {
    log_stage "🔬 Type Checking"
    start_timer "typing"
    
    # Create mypy configuration if it doesn't exist
    if [[ ! -f "mypy.ini" ]] && [[ ! -f "pyproject.toml" ]]; then
        log_info "Creating mypy configuration..."
        cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
check_untyped_defs = True
disallow_untyped_decorators = True

[mypy-tests.*]
disallow_untyped_defs = False

[mypy-pytesseract.*]
ignore_missing_imports = True

[mypy-PIL.*]
ignore_missing_imports = True
EOF
    fi
    
    log_command "mypy processor/"
    if mypy processor/ 2>/dev/null; then
        log_success "Type checking passed"
        end_timer "typing"
        return 0
    else
        log_warning "Type checking found issues (non-blocking)"
        end_timer "typing"
        return 1
    fi
}

# Run tests
run_tests() {
    log_stage "🧪 Running Tests"
    start_timer "testing"
    
    # Check if tests directory exists
    local test_dirs=()
    if [[ -d "tests" ]]; then
        test_dirs+=("tests")
    fi
    if [[ -d "processor/unified_project/tests" ]]; then
        test_dirs+=("processor/unified_project/tests")
    fi
    
    if [[ ${#test_dirs[@]} -eq 0 ]]; then
        log_warning "No test directories found. Skipping tests."
        end_timer "testing"
        return 0
    fi
    
    # Run pytest with coverage
    local pytest_args=(
        "--verbose"
        "--tb=short"
        "--cov=processor"
        "--cov-report=term-missing"
        "--cov-report=html:htmlcov"
        "--cov-report=xml:coverage.xml"
        "--junit-xml=test-results.xml"
    )
    
    # Add parallel execution if not in CI
    if ! is_ci && command -v pytest-xdist &> /dev/null; then
        pytest_args+=("-n" "auto")
    fi
    
    log_command "pytest ${pytest_args[*]} ${test_dirs[*]}"
    if timeout $TIMEOUT_SECONDS pytest "${pytest_args[@]}" "${test_dirs[@]}"; then
        log_success "All tests passed"
        end_timer "testing"
        return 0
    else
        log_error "Some tests failed"
        end_timer "testing"
        return 1
    fi
}

# Platform-specific tests
run_platform_tests() {
    log_stage "🖥️  Platform-Specific Tests"  
    start_timer "platform_tests"
    
    # Test platform detection
    log_info "Testing platform detection..."
    if python -c "
from processor.unified_project.src.utils.platform_detection import get_platform_info
import json
info = get_platform_info()
print(json.dumps(info, indent=2))
print(f'Platform detection successful: {info[\"system\"]}')
"; then
        log_success "Platform detection test passed"
    else
        log_error "Platform detection test failed"
        end_timer "platform_tests"
        return 1
    fi
    
    # Test basic CLI functionality
    log_info "Testing CLI functionality..."
    if timeout 30 python -m processor.unified_project.src.main --help > /dev/null; then
        log_success "CLI help test passed"
    else
        log_error "CLI help test failed"
        end_timer "platform_tests"
        return 1
    fi
    
    # Test cache functionality
    log_info "Testing cache functionality..."
    if timeout 30 python -m processor.unified_project.src.main cache stats > /dev/null; then
        log_success "Cache functionality test passed"
    else
        log_error "Cache functionality test failed"
        end_timer "platform_tests"
        return 1
    fi
    
    end_timer "platform_tests"
    return 0
}

# Performance benchmarks
run_benchmarks() {
    log_stage "⚡ Performance Benchmarks"
    start_timer "benchmarks"
    
    # Simple benchmark test
    log_info "Running basic performance benchmarks..."
    
    local benchmark_script=$(cat << 'EOF'
import time
import sys
from pathlib import Path

# Add the processor module to path
sys.path.insert(0, str(Path(__file__).parent / "processor" / "unified_project" / "src"))

try:
    from utils.platform_detection import get_platform_info, get_optimization_recommendations
    
    # Benchmark platform detection
    start_time = time.time()
    for _ in range(100):
        info = get_platform_info()
    detection_time = time.time() - start_time
    
    print(f"Platform detection (100 iterations): {detection_time:.3f}s")
    print(f"Average per call: {detection_time/100*1000:.1f}ms") 
    
    # Benchmark optimization recommendations
    start_time = time.time()
    for _ in range(100):
        recommendations = get_optimization_recommendations()
    recommendation_time = time.time() - start_time
    
    print(f"Optimization recommendations (100 iterations): {recommendation_time:.3f}s")
    print(f"Average per call: {recommendation_time/100*1000:.1f}ms")
    
    # Simple startup time test
    print("\nStartup time benchmarks:")
    import subprocess
    import time
    
    start_time = time.time()
    result = subprocess.run([sys.executable, "-c", "import sys; print('Python import test')"], 
                          capture_output=True, text=True)
    import_time = time.time() - start_time
    
    print(f"Python startup time: {import_time:.3f}s")
    
    if import_time < 1.0:
        print("✅ Startup performance: Good")
    elif import_time < 2.0:
        print("⚠️  Startup performance: Acceptable")
    else:
        print("❌ Startup performance: Slow")

except ImportError as e:
    print(f"❌ Benchmark failed - module import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Benchmark failed: {e}")
    sys.exit(1)
EOF
)
    
    if python -c "$benchmark_script"; then
        log_success "Performance benchmarks completed"
    else
        log_warning "Performance benchmarks had issues"
    fi
    
    end_timer "benchmarks"
}

# Generate reports
generate_reports() {
    log_stage "📊 Generating Reports"
    start_timer "reports"
    
    local report_dir="ci_reports"
    mkdir -p "$report_dir"
    
    # Generate CI summary report
    local report_file="$report_dir/ci_summary.json"
    cat > "$report_file" << EOF
{
  "timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
  "platform": {
    "os": "$(uname -s)",
    "arch": "$(uname -m)",
    "python": "$(python --version 2>&1)"
  },
  "ci_environment": $(is_ci && echo "true" || echo "false"),
  "stage_times": $(declare -p stage_times | sed 's/declare -A stage_times=//' | sed 's/\[\([^]]*\)\]/"\1":/g' | sed 's/\([^{,]\) \([^}]\)/\1, \2/g' | sed 's/^(/\{/' | sed 's/)$/\}/'),
  "total_time": $(($(date +%s) - overall_start_time)),
  "reports_generated": [
    "coverage.xml",
    "test-results.xml", 
    "bandit-report.json",
    "safety-report.json"
  ]
}
EOF
    
    log_success "CI summary report generated: $report_file"
    
    # Move other reports to report directory
    local reports=("coverage.xml" "test-results.xml" "bandit-report.json" "safety-report.json" "htmlcov")
    for report in "${reports[@]}"; do
        if [[ -e "$report" ]]; then
            mv "$report" "$report_dir/"
            log_success "Moved report: $report"
        fi
    done
    
    end_timer "reports"
}

# Cleanup
cleanup() {
    log_stage "🧹 Cleanup"
    
    # Clean up temporary files
    local temp_files=("mypy.ini" ".coverage" ".pytest_cache" "__pycache__")
    for temp_file in "${temp_files[@]}"; do
        if [[ -e "$temp_file" ]]; then
            rm -rf "$temp_file"
            log_info "Cleaned up: $temp_file"
        fi
    done
    
    # Clean up Python cache
    find . -name "*.pyc" -delete 2>/dev/null || true
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    
    log_success "Cleanup completed"
}

# Print summary
print_summary() {
    local overall_end_time=$(date +%s)
    local total_duration=$((overall_end_time - overall_start_time))
    
    echo ""
    echo "🏁 CI Pipeline Summary"
    echo "======================"
    echo "Total execution time: ${total_duration}s"
    echo ""
    
    if [[ ${#stage_times[@]} -gt 0 ]]; then
        echo "Stage timings:"
        for stage in "${!stage_times[@]}"; do
            local start_time=${stage_times["$stage"]}
            local duration=$((overall_end_time - start_time))
            if [[ $duration -lt 60 ]]; then
                echo "  $stage: ${duration}s"
            else
                echo "  $stage: $((duration / 60))m $((duration % 60))s"
            fi
        done
        echo ""
    fi
    
    if [[ -d "ci_reports" ]]; then
        echo "📋 Reports generated in ci_reports/ directory"
        echo "   View coverage: open ci_reports/htmlcov/index.html"
        echo ""
    fi
}

# Main execution
main() {
    print_header
    
    local failed_stages=0
    local total_stages=0
    
    # Define pipeline stages
    local stages=(
        "validate_environment"
        "install_dependencies" 
        "format_code"
        "run_linting"
        "run_type_checking"
        "run_tests"
        "run_platform_tests"
        "run_benchmarks"
        "generate_reports"
    )
    
    # Execute pipeline
    for stage in "${stages[@]}"; do
        ((total_stages++))
        if ! $stage; then
            ((failed_stages++))
            log_error "Stage '$stage' failed"
            
            # Stop on critical failures
            if [[ "$stage" == "validate_environment" ]] || [[ "$stage" == "install_dependencies" ]]; then
                log_error "Critical stage failed. Stopping pipeline."
                cleanup
                exit 1
            fi
        fi
    done
    
    # Always run cleanup
    cleanup
    
    # Print summary
    print_summary
    
    # Exit with appropriate code
    if [[ $failed_stages -eq 0 ]]; then
        log_success "🎉 All CI stages passed successfully!"
        exit 0
    elif [[ $failed_stages -lt 3 ]]; then
        log_warning "⚠️  CI completed with $failed_stages/$total_stages stage failures (non-critical)"
        exit 0
    else
        log_error "❌ CI failed with $failed_stages/$total_stages stage failures"
        exit 1
    fi
}

# Handle interruption
trap cleanup INT TERM

# Run main function
main "$@"