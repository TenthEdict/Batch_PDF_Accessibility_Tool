#!/usr/bin/env python3
"""
Validation domain entities and value objects.

This module defines the ValidationResult entity and related business objects
that represent document validation operations in the system.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid


class ValidationStandard(Enum):
    """Validation standard enumeration."""
    PDF_UA = "pdf_ua"
    WCAG_2_1 = "wcag_2_1"
    SECTION_508 = "section_508"
    EPUB_ACCESSIBILITY = "epub_accessibility"
    CUSTOM = "custom"


class ValidationCheckStatus(Enum):
    """Validation check status enumeration."""
    PASS = "pass"
    FAIL = "fail"
    WARNING = "warning"
    SKIP = "skip"
    ERROR = "error"


class ValidationSeverity(Enum):
    """Validation issue severity enumeration."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


@dataclass(frozen=True)
class ValidationIdentifier:
    """Value object for validation identification."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))


@dataclass
class ValidationCheck:
    """Value object representing a single validation check."""
    check_id: str
    name: str
    description: str
    status: ValidationCheckStatus
    severity: ValidationSeverity = ValidationSeverity.MEDIUM
    message: Optional[str] = None
    expected_value: Optional[Any] = None
    actual_value: Optional[Any] = None
    location: Optional[str] = None
    suggestion: Optional[str] = None
    
    def is_passing(self) -> bool:
        """Check if validation check is passing."""
        return self.status == ValidationCheckStatus.PASS
    
    def is_failing(self) -> bool:
        """Check if validation check is failing."""
        return self.status == ValidationCheckStatus.FAIL
    
    def has_warning(self) -> bool:
        """Check if validation check has warning."""
        return self.status == ValidationCheckStatus.WARNING
    
    def is_critical(self) -> bool:
        """Check if validation check is critical."""
        return self.severity == ValidationSeverity.CRITICAL
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert check to dictionary representation."""
        return {
            'check_id': self.check_id,
            'name': self.name,
            'description': self.description,
            'status': self.status.value,
            'severity': self.severity.value,
            'message': self.message,
            'expected_value': self.expected_value,
            'actual_value': self.actual_value,
            'location': self.location,
            'suggestion': self.suggestion
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationCheck':
        """Create check from dictionary representation."""
        return cls(
            check_id=data['check_id'],
            name=data['name'],
            description=data['description'],
            status=ValidationCheckStatus(data['status']),
            severity=ValidationSeverity(data['severity']),
            message=data.get('message'),
            expected_value=data.get('expected_value'),
            actual_value=data.get('actual_value'),
            location=data.get('location'),
            suggestion=data.get('suggestion')
        )


@dataclass
class ValidationStandardResult:
    """Value object for validation results against a specific standard."""
    standard: ValidationStandard
    score: float
    max_score: float
    checks: List[ValidationCheck] = field(default_factory=list)
    overall_status: ValidationCheckStatus = ValidationCheckStatus.FAIL
    
    def __post_init__(self):
        """Calculate overall status based on checks."""
        if not self.checks:
            self.overall_status = ValidationCheckStatus.SKIP
            return
        
        # Check for critical failures
        critical_failures = [c for c in self.checks if c.is_critical() and c.is_failing()]
        if critical_failures:
            self.overall_status = ValidationCheckStatus.FAIL
            return
        
        # Check pass rate
        passing_checks = [c for c in self.checks if c.is_passing()]
        pass_rate = len(passing_checks) / len(self.checks)
        
        if pass_rate >= 0.8:
            self.overall_status = ValidationCheckStatus.PASS
        elif pass_rate >= 0.6:
            self.overall_status = ValidationCheckStatus.WARNING
        else:
            self.overall_status = ValidationCheckStatus.FAIL
    
    def get_pass_rate(self) -> float:
        """Get percentage of checks that passed."""
        if not self.checks:
            return 0.0
        
        passing = len([c for c in self.checks if c.is_passing()])
        return passing / len(self.checks)
    
    def get_failing_checks(self) -> List[ValidationCheck]:
        """Get list of failing checks."""
        return [c for c in self.checks if c.is_failing()]
    
    def get_critical_issues(self) -> List[ValidationCheck]:
        """Get list of critical issues."""
        return [c for c in self.checks if c.is_critical() and not c.is_passing()]
    
    def get_warnings(self) -> List[ValidationCheck]:
        """Get list of warning checks."""
        return [c for c in self.checks if c.has_warning()]
    
    def add_check(self, check: ValidationCheck) -> None:
        """Add a validation check and recalculate status."""
        self.checks.append(check)
        self.__post_init__()  # Recalculate overall status
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'standard': self.standard.value,
            'score': self.score,
            'max_score': self.max_score,
            'overall_status': self.overall_status.value,
            'pass_rate': self.get_pass_rate(),
            'checks': [check.to_dict() for check in self.checks]
        }


@dataclass
class ValidationSummary:
    """Value object for validation summary statistics."""
    total_checks: int = 0
    passed_checks: int = 0
    failed_checks: int = 0
    warning_checks: int = 0
    skipped_checks: int = 0
    critical_issues: int = 0
    
    def get_pass_rate(self) -> float:
        """Get overall pass rate."""
        if self.total_checks == 0:
            return 0.0
        return self.passed_checks / self.total_checks
    
    def get_failure_rate(self) -> float:
        """Get overall failure rate."""
        if self.total_checks == 0:
            return 0.0
        return self.failed_checks / self.total_checks
    
    def has_critical_issues(self) -> bool:
        """Check if there are critical issues."""
        return self.critical_issues > 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'total_checks': self.total_checks,
            'passed_checks': self.passed_checks,
            'failed_checks': self.failed_checks,
            'warning_checks': self.warning_checks,
            'skipped_checks': self.skipped_checks,
            'critical_issues': self.critical_issues,
            'pass_rate': self.get_pass_rate(),
            'failure_rate': self.get_failure_rate()
        }


@dataclass
class ValidationResult:
    """
    ValidationResult entity representing document validation results.
    
    This entity contains the complete validation results for a document
    against multiple accessibility standards.
    """
    identifier: ValidationIdentifier
    document_id: str
    document_path: str
    overall_score: float
    overall_status: ValidationCheckStatus
    standard_results: Dict[ValidationStandard, ValidationStandardResult] = field(default_factory=dict)
    summary: ValidationSummary = field(default_factory=ValidationSummary)
    recommendations: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    validation_duration_seconds: Optional[float] = None
    
    def __post_init__(self):
        """Calculate summary and overall metrics."""
        self._calculate_summary()
        self._calculate_overall_score()
        self._generate_recommendations()
    
    def add_standard_result(self, result: ValidationStandardResult) -> None:
        """Add validation result for a standard."""
        self.standard_results[result.standard] = result
        self._calculate_summary()
        self._calculate_overall_score()
        self._generate_recommendations()
    
    def get_standard_result(self, standard: ValidationStandard) -> Optional[ValidationStandardResult]:
        """Get validation result for a specific standard."""
        return self.standard_results.get(standard)
    
    def has_standard(self, standard: ValidationStandard) -> bool:
        """Check if results include a specific standard."""
        return standard in self.standard_results
    
    def get_all_failing_checks(self) -> List[ValidationCheck]:
        """Get all failing checks across all standards."""
        failing_checks = []
        for result in self.standard_results.values():
            failing_checks.extend(result.get_failing_checks())
        return failing_checks
    
    def get_all_critical_issues(self) -> List[ValidationCheck]:
        """Get all critical issues across all standards."""
        critical_issues = []
        for result in self.standard_results.values():
            critical_issues.extend(result.get_critical_issues())
        return critical_issues
    
    def is_passing(self) -> bool:
        """Check if validation is overall passing."""
        return self.overall_status == ValidationCheckStatus.PASS
    
    def has_critical_issues(self) -> bool:
        """Check if validation has critical issues."""
        return self.summary.has_critical_issues()
    
    def add_error(self, error: str) -> None:
        """Add a validation error."""
        self.errors.append(error)
    
    def add_recommendation(self, recommendation: str) -> None:
        """Add a recommendation."""
        if recommendation not in self.recommendations:
            self.recommendations.append(recommendation)
    
    def _calculate_summary(self) -> None:
        """Calculate validation summary statistics."""
        total_checks = 0
        passed_checks = 0
        failed_checks = 0
        warning_checks = 0
        skipped_checks = 0
        critical_issues = 0
        
        for result in self.standard_results.values():
            total_checks += len(result.checks)
            
            for check in result.checks:
                if check.is_passing():
                    passed_checks += 1
                elif check.is_failing():
                    failed_checks += 1
                    if check.is_critical():
                        critical_issues += 1
                elif check.has_warning():
                    warning_checks += 1
                else:  # SKIP or ERROR
                    skipped_checks += 1
        
        self.summary = ValidationSummary(
            total_checks=total_checks,
            passed_checks=passed_checks,
            failed_checks=failed_checks,
            warning_checks=warning_checks,
            skipped_checks=skipped_checks,
            critical_issues=critical_issues
        )
    
    def _calculate_overall_score(self) -> None:
        """Calculate overall validation score."""
        if not self.standard_results:
            self.overall_score = 0.0
            self.overall_status = ValidationCheckStatus.SKIP
            return
        
        # Calculate weighted average of standard scores
        total_weight = 0
        weighted_score = 0.0
        
        for result in self.standard_results.values():
            weight = result.max_score if result.max_score > 0 else 1.0
            weighted_score += result.score * weight
            total_weight += weight
        
        if total_weight > 0:
            self.overall_score = weighted_score / total_weight
        else:
            self.overall_score = 0.0
        
        # Determine overall status
        if self.summary.has_critical_issues():
            self.overall_status = ValidationCheckStatus.FAIL
        elif self.overall_score >= 0.8:
            self.overall_status = ValidationCheckStatus.PASS
        elif self.overall_score >= 0.6:
            self.overall_status = ValidationCheckStatus.WARNING
        else:
            self.overall_status = ValidationCheckStatus.FAIL
    
    def _generate_recommendations(self) -> None:
        """Generate recommendations based on validation results."""
        self.recommendations = []
        
        # General recommendations based on score
        if self.overall_score < 0.5:
            self.add_recommendation("Document requires significant accessibility improvements")
        elif self.overall_score < 0.8:
            self.add_recommendation("Document has some accessibility issues that should be addressed")
        
        # Specific recommendations based on common failures
        all_failing = self.get_all_failing_checks()
        failing_types = {check.check_id for check in all_failing}
        
        if 'has_title' in failing_types:
            self.add_recommendation("Add a descriptive title to the document")
        
        if 'has_language' in failing_types:
            self.add_recommendation("Specify the document language for better accessibility")
        
        if 'has_structure' in failing_types:
            self.add_recommendation("Add proper document structure with headings and sections")
        
        if 'has_alt_text' in failing_types:
            self.add_recommendation("Add alternative text descriptions for images")
        
        if 'proper_contrast' in failing_types:
            self.add_recommendation("Improve color contrast ratios for better readability")
        
        # Critical issue recommendations
        if self.has_critical_issues():
            self.add_recommendation("Address critical accessibility issues before publication")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation."""
        return {
            'id': self.identifier.id,
            'document_id': self.document_id,
            'document_path': self.document_path,
            'overall_score': self.overall_score,
            'overall_status': self.overall_status.value,
            'summary': self.summary.to_dict(),
            'standard_results': {
                standard.value: result.to_dict()
                for standard, result in self.standard_results.items()
            },
            'recommendations': self.recommendations,
            'errors': self.errors,
            'created_at': self.created_at.isoformat(),
            'validation_duration_seconds': self.validation_duration_seconds
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ValidationResult':
        """Create validation result from dictionary representation."""
        # Convert datetime
        created_at = datetime.fromisoformat(data['created_at'])
        
        # Create identifier
        identifier = ValidationIdentifier(id=data['id'])
        
        # Create summary
        summary_data = data['summary']
        summary = ValidationSummary(
            total_checks=summary_data['total_checks'],
            passed_checks=summary_data['passed_checks'],
            failed_checks=summary_data['failed_checks'],
            warning_checks=summary_data['warning_checks'],
            skipped_checks=summary_data['skipped_checks'],
            critical_issues=summary_data['critical_issues']
        )
        
        # Create standard results
        standard_results = {}
        for standard_name, result_data in data['standard_results'].items():
            standard = ValidationStandard(standard_name)
            checks = [ValidationCheck.from_dict(check_data) for check_data in result_data['checks']]
            
            standard_result = ValidationStandardResult(
                standard=standard,
                score=result_data['score'],
                max_score=result_data['max_score'],
                checks=checks,
                overall_status=ValidationCheckStatus(result_data['overall_status'])
            )
            standard_results[standard] = standard_result
        
        return cls(
            identifier=identifier,
            document_id=data['document_id'],
            document_path=data['document_path'],
            overall_score=data['overall_score'],
            overall_status=ValidationCheckStatus(data['overall_status']),
            standard_results=standard_results,
            summary=summary,
            recommendations=data['recommendations'],
            errors=data['errors'],
            created_at=created_at,
            validation_duration_seconds=data.get('validation_duration_seconds')
        )
    
    @classmethod
    def create_for_document(cls, document_id: str, document_path: str) -> 'ValidationResult':
        """
        Create a new validation result for a document.
        
        Args:
            document_id: ID of the document being validated
            document_path: Path to the document
            
        Returns:
            New ValidationResult instance
        """
        return cls(
            identifier=ValidationIdentifier(),
            document_id=document_id,
            document_path=document_path,
            overall_score=0.0,
            overall_status=ValidationCheckStatus.SKIP
        )
    
    def __str__(self) -> str:
        """String representation of the validation result."""
        return f"ValidationResult(id={self.identifier.id[:8]}, score={self.overall_score:.2f}, status={self.overall_status.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the validation result."""
        return (
            f"ValidationResult("
            f"id='{self.identifier.id}', "
            f"document_id='{self.document_id}', "
            f"score={self.overall_score:.2f}, "
            f"status={self.overall_status.value}, "
            f"standards={len(self.standard_results)}"
            f")"
        )