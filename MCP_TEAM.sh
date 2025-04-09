#!/bin/bash
#==============================================================================
# MCP_TEAM.sh - Mission Control Protocol Team Manager for Claude
#==============================================================================
# DESCRIPTION:
#   This script manages a team of specialized MCP prompts for claude,
#   allowing dynamic selection of domain-specific expertise as needed during
#   development workflows. Each team member provides specialized guidance for
#   a specific aspect of the ePubs accessibility project.
#
# USAGE:
#   ./MCP_TEAM.sh [OPTIONS]
#
# OPTIONS:
#   -l, --list           List all available MCP team members
#   -m, --member NAME    Select a specific team member by name
#   -i, --index NUMBER   Select a team member by index
#   -a, --all            Display all team members' prompts (concatenated)
#   -h, --help           Display this help message
#
# EXAMPLES:
#   ./MCP_TEAM.sh --list
#   ./MCP_TEAM.sh --member python
#   ./MCP_TEAM.sh --index 3
#   ./MCP_TEAM.sh --member architecture | claude
#
# AUTHOR:
#   Created for ePubs Accessibility Project
#==============================================================================

set -eo pipefail

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Script configuration
SCRIPT_NAME=$(basename "$0")
VERSION="1.0.0"

#==============================================================================
# MCP TEAM DEFINITIONS
#==============================================================================

# Documentation MCP
MCP_DOCUMENTATION=$(cat << 'EOF'
# Documentation Engineering Protocol

## Primary Objective
Generate comprehensive, standards-compliant technical documentation for the ePubs accessibility project following accessibility guidelines and best practices.

## Context Parameters
- Project: ePubs Accessibility Conversion System
- Audience: Technical implementers, accessibility specialists, and future maintainers
- Standards: WCAG 2.1 AA, Section 508, PDF/UA, EPUB Accessibility 1.1

## Required Documentation Components
- System architecture overview with component interaction diagrams
- Process workflow documentation with clear input/output specifications
- API reference documentation with complete parameter descriptions
- Installation and configuration guides with environment requirements
- Troubleshooting procedures with error code references
- Accessibility compliance verification procedures

## Implementation Guidelines
- Structure documentation hierarchically with consistent navigation paths
- Include machine-readable metadata for automated compliance verification
- Provide concrete code examples for all implementation patterns
- Define all acronyms and technical terminology in a glossary
- Use descriptive alt text for all diagrams and technical illustrations
- Implement proper heading hierarchy for screen reader compatibility

## Quality Assurance Parameters
- Ensure all procedures are independently verifiable
- Include version control metadata and change history
- Validate all hyperlinks and cross-references
- Implement consistent formatting for command syntax and code blocks
- Include validation checkpoints for accessibility compliance testing

## Deliverable Specifications
- Generate documentation in accessible Markdown format
- Include embedded JSON schema definitions where applicable
- Provide structure for automated documentation testing
EOF
)

# Bash MCP
MCP_BASH=$(cat << 'EOF'
# Bash Automation Engineering Protocol

## Primary Objective
Develop robust, idempotent bash scripts for automating ePubs accessibility conversion workflows with comprehensive error handling and logging capabilities.

## Execution Context
- Environment: Linux/Unix systems in production and testing environments
- Integration: Adobe Acrobat Server, OCR systems, Python processing pipeline
- Security: Principle of least privilege with secure credential management

## Core Functionality Requirements
- File processing workflow automation with batch capabilities
- Robust error detection and recovery mechanisms
- Detailed logging with standardized severity levels
- Progress monitoring with appropriate status indicators
- Resource cleanup protocols for aborted processes
- Graceful handling of network interruptions

## Implementation Standards
- Follow Google Shell Style Guide conventions
- Implement strict error handling with set -euo pipefail
- Document all functions with standardized header comments
- Use consistent variable naming conventions with descriptive prefixes
- Implement proper quoting and parameter expansion
- Design for idempotent execution with checkpoints

## Security Considerations
- Implement secure temporary file handling with mktemp
- Sanitize all command-line inputs to prevent injection
- Use principle of least privilege for all operations
- Handle credentials via environment variables or secure vaults
- Implement file permission verification before operations

## Performance Optimization
- Utilize parallel processing for batch operations where appropriate
- Implement resource throttling for high-volume operations
- Create efficient pipeline structures to minimize process spawning
- Optimize file operations to reduce I/O overhead

## Deliverable Specifications
- Main script with modular function libraries
- Configuration templates with documented parameters
- Installation verification script
- Usage documentation with example commands
EOF
)

# Python MCP
MCP_PYTHON=$(cat << 'EOF'
# Python Engineering Protocol

## Primary Objective
Develop maintainable, efficient Python modules for ePubs document processing with robust accessibility analysis and transformation capabilities.

## Technical Parameters
- Python Version: 3.8+
- Key Dependencies: PyPDF2, ReportLab, pytesseract, Pillow, pandas
- Performance Targets: Process 50+ page documents in under 60 seconds
- Compatibility: Cross-platform (Windows, macOS, Linux)

## Core Functionality Requirements
- PDF structure analysis with tag tree traversal
- Document accessibility evaluation against WCAG 2.1 standards
- Automated remediation of common accessibility issues
- Table extraction and semantic restructuring
- Content reflow optimization for screen readers
- Metadata enrichment for accessibility compliance

## Code Quality Standards
- Implement PEP 8 compliance with consistent formatting
- Achieve minimum 90% test coverage with pytest
- Document all public APIs with NumPy docstring format
- Type hint all functions using Python typing module
- Implement comprehensive exception handling hierarchies
- Follow SOLID principles for maintainable architecture

## Performance Optimization
- Implement memory-efficient processing for large documents
- Utilize multiprocessing for parallel page processing
- Implement efficient caching mechanisms for repeated operations
- Optimize image processing operations for OCR preparation
- Profile critical paths and optimize algorithmic complexity

## Security Implementation
- Sanitize all external inputs before processing
- Implement secure file handling with proper permissions
- Validate all configuration parameters against schemas
- Handle sensitive information with appropriate encryption
- Implement resource limits to prevent DoS vulnerabilities

## Deliverable Specifications
- Modular package structure with clear separation of concerns
- Configuration system with environment variable support
- Comprehensive logging with configurable verbosity
- Command-line interface with complete argument handling
- Integration tests covering key workflows
EOF
)

# Adobe Acrobat MCP
MCP_ACROBAT=$(cat << 'EOF'
# Adobe Acrobat Engineering Protocol

## Primary Objective
Develop robust integration solutions for Adobe Acrobat DC to automate accessibility remediation workflows for ePubs document processing.

## Technical Environment
- Adobe Acrobat Version: DC 2023 (continuous track)
- Integration Methods: JavaScript API, Action Wizard, COM Automation
- Document Types: PDF, PDF/UA, PDF/A-1a, PDF/A-2a, PDF/A-3a
- Processing Volume: Capable of handling batches of 1000+ documents

## Core Functionality Requirements
- Automated tag structure generation with semantic correctness
- Reading order optimization for screen reader compatibility
- Table structure remediation with proper header associations
- Automated alternative text generation for non-decorative images
- Form field accessibility enhancement with proper labeling
- Document metadata enrichment for compliance verification
- Bookmark structure generation based on heading hierarchy

## Implementation Approach
- Develop modular JavaScript functions for Acrobat automation
- Create reusable Action Wizard sequences for batch processing
- Implement COM/ActiveX interfaces for external system integration
- Develop robust preflight profiles for accessibility verification
- Create custom accessibility report templates with remediation guidance

## Error Handling Strategy
- Implement comprehensive error trapping in JavaScript functions
- Develop recovery mechanisms for partial processing failures
- Create detailed logging of all remediation actions performed
- Implement verification steps after each significant transformation
- Generate actionable error reports for manual intervention cases

## Performance Optimization
- Implement batch processing strategies for high-volume workflows
- Optimize memory usage for large document processing
- Implement incremental save operations for processing checkpoints
- Balance automation with manual verification for complex structures

## Deliverable Specifications
- JavaScript module library with documentation
- Action Wizard sequences for common remediation tasks
- COM automation interfaces with API documentation
- Preflight profiles for accessibility verification
- Processing templates for batch operations
EOF
)

# OCR MCP
MCP_OCR=$(cat << 'EOF'
# Pytesseract OCR Engineering Protocol

## Primary Objective
Develop high-accuracy, performance-optimized OCR integration using pytesseract for extracting accessible text from image-based PDF content in the ePubs accessibility project.

## Technical Parameters
- OCR Engine: Tesseract 5.x via pytesseract
- Image Processing: OpenCV and Pillow
- Language Support: English plus multilingual capability
- Accuracy Targets: >98% for standard text, >90% for complex layouts

## Core Functionality Requirements
- Image preprocessing pipeline optimization for OCR accuracy
- Document layout analysis with structural element detection
- Table recognition with semantic structure preservation
- Mathematical formula detection and specialized processing
- Multi-column text flow detection and sequential ordering
- Language detection and appropriate OCR language pack selection
- Confidence scoring and quality assurance mechanisms

## Implementation Strategy
- Implement modular preprocessing stages with configuration options
- Develop adaptive image enhancement based on document characteristics
- Create specialized handlers for different content types (text, tables, formulas)
- Implement parallel processing for multi-page documents
- Develop post-processing text correction algorithms for common OCR errors
- Create validation mechanisms for structural integrity verification

## Image Preprocessing Techniques
- Dynamic thresholding based on document characteristics
- Skew detection and correction with sub-degree accuracy
- Noise reduction with adaptive filtering techniques
- Resolution standardization with quality preservation
- Contrast enhancement optimized for text clarity
- Border and artifact removal for clean processing

## Text Extraction Optimization
- Configure Tesseract parameters based on document type
- Implement page segmentation mode selection logic
- Optimize OCR engine variables for different content types
- Develop custom dictionaries for specialized terminology
- Implement context-aware text correction algorithms
- Preserve spatial relationships for layout reconstruction

## Performance Considerations
- Implement multi-threaded processing for batch operations
- Optimize memory usage for large document processing
- Implement progressive processing with quality checkpoints
- Balance processing depth with performance requirements
- Implement caching mechanisms for repeated operations

## Deliverable Specifications
- Modular OCR processing pipeline with configuration options
- Quality assessment module with confidence metrics
- Specialized handlers for different content types
- Integration interface for the overall workflow system
- Performance benchmarking suite for optimization
EOF
)

# Architecture MCP
MCP_ARCHITECTURE=$(cat << 'EOF'
# Architecture and Testing Engineering Protocol

## Primary Objective
Design and implement a robust, scalable architecture and comprehensive testing strategy for the ePubs accessibility conversion system, ensuring reliability, maintainability, and compliance with accessibility standards.

## Architecture Requirements
- Implement modular design with well-defined component interfaces
- Develop scalable processing pipeline for high-volume document conversion
- Create fault-tolerant workflow with recovery mechanisms
- Design extensible plugin system for new document types and transformations
- Implement efficient data flow architecture minimizing I/O operations
- Establish clear separation between processing logic and accessibility rules

## System Component Specification
- Document Ingestion Service: Handles document acquisition and validation
- Analysis Engine: Performs structural and accessibility analysis
- Transformation Pipeline: Executes remediation operations
- Quality Verification System: Validates accessibility compliance
- Reporting Service: Generates compliance and exception reports
- Workflow Orchestration: Manages process flow and resource allocation

## Integration Architecture
- Define clear API contracts between all components
- Implement message-based communication for asynchronous operations
- Design stateless components where possible for horizontal scaling
- Create unified logging framework with correlation IDs
- Implement centralized configuration management
- Design service discovery mechanism for dynamic scaling

## Testing Strategy Implementation
- Unit Testing: Minimum 90% code coverage for all components
- Integration Testing: Complete workflow verification with simulated inputs
- Performance Testing: Throughput and resource utilization benchmarks
- Accessibility Compliance Testing: Automated WCAG 2.1 verification
- Regression Testing: Automated test suite for all supported document types
- Fault Injection Testing: System recovery validation under failure conditions

## Test Automation Framework
- Implement behavior-driven development approach with Gherkin specifications
- Create representative document corpus for comprehensive testing
- Develop mock services for external dependency testing
- Implement continuous integration pipeline with automated testing
- Create performance testing harness with load simulation
- Design accessibility compliance test suite with reference benchmarks

## Quality Assurance Metrics
- Establish key performance indicators for system evaluation
- Implement error rate tracking and quality trending
- Create baseline accessibility compliance reports for regression tracking
- Develop processing time metrics for performance optimization
- Implement resource utilization monitoring for efficiency analysis

## Deliverable Specifications
- Architecture design document with component specifications
- Interface contracts with API documentation
- Test strategy document with coverage matrices
- Automated test suite with configuration documentation
- Performance benchmark suite with baseline measurements
- System deployment and scaling documentation
EOF
)

# Docker MCP
MCP_DOCKER=$(cat << 'EOF'
# Docker Container Engineering Protocol

## Primary Objective
Design and implement robust, secure, and efficient Docker containerization solutions for the ePubs accessibility project, ensuring consistent deployment across environments with minimal configuration drift and optimal resource utilization.

## Technical Environment
- Docker Engine: 24.0+
- Container Registry: Harbor or Docker Hub
- Orchestration: Docker Compose and Kubernetes capability
- Host Systems: Ubuntu 22.04 LTS
- Storage: Volume management with persistence considerations
- Networking: Bridge, overlay, and macvlan options

## Container Design Principles
- Single responsibility containers with clear functional boundaries
- Immutable infrastructure approach with declarative specifications
- Layered architecture minimizing image size and attack surface
- Stateless design where possible with external state management
- Just-enough operating system (JeOS) principle for base images
- Reproducible builds with deterministic dependency resolution

## Implementation Guidelines
- Implement multi-stage builds to minimize final image size
- Create hierarchical Dockerfile inheritance for consistent environments
- Develop comprehensive healthcheck mechanisms with appropriate intervals
- Implement graceful shutdown handling with proper signal management
- Define explicit container dependencies with appropriate startup ordering
- Utilize build arguments for environment-specific customization
- Structure properly labeled and annotated containers for automated discovery

## Security Implementation
- Execute containers with least-privilege non-root users
- Implement read-only filesystems with specific write mount points
- Configure content trust with image signing and verification
- Implement secrets management without environment variable exposure
- Create comprehensive security scanning in CI/CD pipeline
- Establish immutable tags policy with SHA256 digest verification
- Implement network policy controls limiting container communication

## Performance Optimization
- Configure resource constraints (CPU, memory, I/O) appropriate to workload
- Implement efficient layer caching strategies for build acceleration
- Utilize multi-architecture images for platform-specific optimizations
- Develop custom container health metrics with Prometheus integration
- Implement appropriate log rotation and volume management
- Optimize container startup sequence for minimal initialization time
- Configure kernel parameter tuning for container workloads

## CI/CD Integration
- Implement automated image building with version tagging strategy
- Create comprehensive testing of container images before deployment
- Develop blue/green deployment capabilities with rollback mechanisms
- Establish container security scanning with policy enforcement
- Configure image promotion workflow across environments
- Implement deterministic versioning for all container artifacts

## Orchestration Considerations
- Design self-healing container configurations with appropriate restart policies
- Implement resource quotas and limits at orchestrator level
- Develop comprehensive service discovery mechanisms
- Configure network policies enforcing least-privilege communication
- Establish persistent volume claim strategies with backup considerations
- Implement horizontal scaling capabilities with state synchronization
- Design for zero-downtime deployments and updates

## Deliverable Specifications
- Dockerfile templates with standardized structure
- Docker Compose files for development and testing environments
- Container security baseline documentation
- Image build and versioning specification
- Integration testing framework for containerized components
- Deployment manifests for container orchestration
- Resource monitoring and alerting configuration
EOF
)

# Define array of team members
declare -A TEAM_MEMBERS
TEAM_MEMBERS=(
  ["documentation"]="$MCP_DOCUMENTATION"
  ["bash"]="$MCP_BASH"
  ["python"]="$MCP_PYTHON"
  ["acrobat"]="$MCP_ACROBAT"
  ["ocr"]="$MCP_OCR"
  ["architecture"]="$MCP_ARCHITECTURE"
  ["docker"]="$MCP_DOCKER"
)

#==============================================================================
# UTILITY FUNCTIONS
#==============================================================================

# Display script banner
banner() {
  echo -e "\n${BLUE}======================================================${NC}"
  echo -e "${GREEN}  MCP Team Manager v${VERSION} - ePubs Accessibility Project${NC}"
  echo -e "${BLUE}======================================================${NC}\n"
}

# Display help information
show_help() {
  cat << EOF
${CYAN}USAGE:${NC}
  ${SCRIPT_NAME} [OPTIONS]

${CYAN}OPTIONS:${NC}
  -l, --list           List all available MCP team members
  -m, --member NAME    Select a specific team member by name
  -i, --index NUMBER   Select a team member by index
  -a, --all            Display all team members' prompts (concatenated)
  -h, --help           Display this help message

${CYAN}EXAMPLES:${NC}
  ${SCRIPT_NAME} --list
  ${SCRIPT_NAME} --member python
  ${SCRIPT_NAME} --index 3
  ${SCRIPT_NAME} --member architecture | claude

${CYAN}AVAILABLE TEAM MEMBERS:${NC}
EOF
  list_team_members
}

# List all team members
list_team_members() {
  local i=1
  for member in "${!TEAM_MEMBERS[@]}"; do
    local first_line=$(echo "${TEAM_MEMBERS[$member]}" | head -n 1)
    echo -e "  ${GREEN}$i.${NC} ${YELLOW}$member${NC} - ${first_line#\# }"
    ((i++))
  done
}

# Get member by index
get_member_by_index() {
  local index=$1
  local i=1
  for member in "${!TEAM_MEMBERS[@]}"; do
    if [[ $i -eq $index ]]; then
      echo "$member"
      return 0
    fi
    ((i++))
  done
  return 1
}

# Display member prompt
display_member_prompt() {
  local member=$1
  if [[ -n "${TEAM_MEMBERS[$member]}" ]]; then
    echo -e "${TEAM_MEMBERS[$member]}"
    return 0
  else
    echo -e "${RED}Error: Member '$member' not found.${NC}" >&2
    return 1
  fi
}

# Display all member prompts
display_all_prompts() {
  echo -e "${YELLOW}# MCP Team - Complete Prompt Collection${NC}\n"
  for member in "${!TEAM_MEMBERS[@]}"; do
    echo -e "${CYAN}## MCP Team Member: $member${NC}\n"
    echo -e "${TEAM_MEMBERS[$member]}\n\n"
  done
}

# Check command availability
check_command() {
  command -v "$1" >/dev/null 2>&1 || { echo -e "${RED}Error: $1 is required but not installed.${NC}" >&2; return 1; }
}

# Main function
main() {
  # Check for claude command if we're piping output
  if [[ -p /dev/stdout ]]; then
    check_command claude || { echo -e "${YELLOW}Warning: 'claude' command not found. Output may not pipe correctly.${NC}" >&2; }
  fi

  if [[ $# -eq 0 ]]; then
    banner
    show_help
    exit 0
  fi

  while [[ $# -gt 0 ]]; do
    case "$1" in
      -h|--help)
        banner
        show_help
        exit 0
        ;;
      -l|--list)
        banner
        echo -e "${CYAN}AVAILABLE TEAM MEMBERS:${NC}"
        list_team_members
        exit 0
        ;;
      -m|--member)
        if [[ -z "$2" ]]; then
          echo -e "${RED}Error: Member name required.${NC}" >&2
          exit 1
        fi
        display_member_prompt "$2"
        exit $?
        ;;
      -i|--index)
        if [[ -z "$2" ]]; then
          echo -e "${RED}Error: Index number required.${NC}" >&2
          exit 1
        fi
        if ! [[ "$2" =~ ^[0-9]+$ ]]; then
          echo -e "${RED}Error: Index must be a number.${NC}" >&2
          exit 1
        fi
        member=$(get_member_by_index "$2")
        if [[ $? -ne 0 ]]; then
          echo -e "${RED}Error: Index out of range.${NC}" >&2
          exit 1
        fi
        display_member_prompt "$member"
        exit $?
        ;;
      -a|--all)
        display_all_prompts
        exit 0
        ;;
      *)
        echo -e "${RED}Error: Unknown option '$1'${NC}" >&2
        show_help
        exit 1
        ;;
    esac
    shift
  done
}

# Run main function
main "$@"
