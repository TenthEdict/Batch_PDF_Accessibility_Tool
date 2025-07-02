#!/usr/bin/env python3
"""
Validation service for business logic related to document validation.

This service encapsulates all business operations related to document
accessibility validation and compliance checking.
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..core.interfaces import Validator
from ..core.service_container import ServiceContainer

logger = logging.getLogger(__name__)


class ValidationService:
    """
    Service for coordinating document validation operations.

    This service provides business logic for validating documents
    against accessibility standards and compliance requirements.
    """

    def __init__(self, container: Optional[ServiceContainer] = None):
        """
        Initialize the validation service.

        Args:
            container: Optional service container for dependency injection
        """
        self.container = container
        self.logger = logging.getLogger(__name__)

        # Validation standards and their requirements
        self._validation_standards = {
            "pdf_ua": {
                "name": "PDF/UA (Universal Accessibility)",
                "description": "ISO 14289 standard for accessible PDF documents",
                "checks": [
                    "has_title",
                    "has_language",
                    "has_structure",
                    "has_alt_text",
                    "proper_reading_order",
                ],
            },
            "wcag_2_1": {
                "name": "WCAG 2.1 Guidelines",
                "description": "Web Content Accessibility Guidelines 2.1",
                "checks": [
                    "has_title",
                    "has_language",
                    "proper_contrast",
                    "keyboard_accessible",
                    "screen_reader_friendly",
                ],
            },
            "section_508": {
                "name": "Section 508 Compliance",
                "description": "US Federal accessibility requirements",
                "checks": [
                    "has_title",
                    "has_language",
                    "has_structure",
                    "proper_markup",
                ],
            },
        }

    def validate_document(
        self, document_path: Union[str, Path], standards: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Validate a document against accessibility standards.

        Args:
            document_path: Path to the document to validate
            standards: List of standards to validate against (default: all)

        Returns:
            Dictionary with validation results
        """
        document_path = Path(document_path)

        if standards is None:
            standards = list(self._validation_standards.keys())

        result = {
            "document_path": str(document_path),
            "overall_score": 0.0,
            "overall_status": "fail",
            "standards": {},
            "summary": {
                "total_checks": 0,
                "passed_checks": 0,
                "failed_checks": 0,
                "warnings": 0,
            },
            "recommendations": [],
            "errors": [],
        }

        if not document_path.exists():
            result["errors"].append(f"Document not found: {document_path}")
            return result

        try:
            # Get validator instance
            validator = self._get_validator(document_path)
            if not validator:
                result["errors"].append(
                    f"No validator available for {document_path.suffix}"
                )
                return result

            # Validate against each standard
            total_score = 0.0
            valid_standards = 0

            for standard in standards:
                if standard not in self._validation_standards:
                    result["errors"].append(f"Unknown standard: {standard}")
                    continue

                # Perform validation for this standard
                standard_result = self._validate_against_standard(
                    validator, document_path, standard
                )

                result["standards"][standard] = standard_result

                if standard_result["score"] is not None:
                    total_score += standard_result["score"]
                    valid_standards += 1

                # Update summary
                result["summary"]["total_checks"] += standard_result["total_checks"]
                result["summary"]["passed_checks"] += standard_result["passed_checks"]
                result["summary"]["failed_checks"] += standard_result["failed_checks"]
                result["summary"]["warnings"] += len(
                    standard_result.get("warnings", [])
                )

            # Calculate overall score
            if valid_standards > 0:
                result["overall_score"] = total_score / valid_standards
                result["overall_status"] = (
                    "pass" if result["overall_score"] >= 0.8 else "fail"
                )

            # Generate recommendations
            result["recommendations"] = self._generate_recommendations(result)

            self.logger.info(
                f"Validation completed for {document_path}: {result['overall_score']:.2f}"
            )

        except Exception as e:
            self.logger.error(f"Error validating document {document_path}: {e}")
            result["errors"].append(f"Validation error: {e}")

        return result

    def generate_report(
        self,
        validation_results: Dict[str, Any],
        output_path: Union[str, Path],
        format: str = "json",
    ) -> bool:
        """
        Generate a validation report from results.

        Args:
            validation_results: Results from validate_document
            output_path: Path where report should be saved
            format: Report format ('json', 'html', 'csv', 'txt')

        Returns:
            True if report generation was successful, False otherwise
        """
        output_path = Path(output_path)

        try:
            if format == "json":
                return self._generate_json_report(validation_results, output_path)
            elif format == "html":
                return self._generate_html_report(validation_results, output_path)
            elif format == "csv":
                return self._generate_csv_report(validation_results, output_path)
            elif format == "txt":
                return self._generate_text_report(validation_results, output_path)
            else:
                self.logger.error(f"Unsupported report format: {format}")
                return False

        except Exception as e:
            self.logger.error(f"Error generating {format} report: {e}")
            return False

    def get_validation_standards(self) -> Dict[str, Dict[str, Any]]:
        """
        Get information about available validation standards.

        Returns:
            Dictionary of validation standards and their details
        """
        return self._validation_standards.copy()

    def validate_batch(
        self, documents: List[Union[str, Path]], standards: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Validate multiple documents in batch.

        Args:
            documents: List of document paths to validate
            standards: List of standards to validate against

        Returns:
            List of validation results
        """
        results = []

        for doc_path in documents:
            try:
                result = self.validate_document(doc_path, standards)
                results.append(result)

                if result["overall_status"] == "pass":
                    self.logger.info(
                        f"✓ {Path(doc_path).name}: {result['overall_score']:.2f}"
                    )
                else:
                    self.logger.warning(
                        f"✗ {Path(doc_path).name}: {result['overall_score']:.2f}"
                    )

            except Exception as e:
                self.logger.error(f"Error validating {doc_path}: {e}")
                results.append(
                    {
                        "document_path": str(doc_path),
                        "overall_score": 0.0,
                        "overall_status": "error",
                        "errors": [f"Validation error: {e}"],
                    }
                )

        return results

    def _get_validator(self, document_path: Path) -> Optional[Validator]:
        """
        Get appropriate validator for document type.

        Args:
            document_path: Path to the document

        Returns:
            Validator instance or None
        """
        # Try to get validator from service container
        if self.container and self.container.has("validator"):
            return self.container.get("validator")

        # Fallback: create basic validator based on file type
        extension = document_path.suffix.lower()

        if extension == ".pdf":
            # Try to import and create PDF validator
            try:
                from ..validation.accessibility_validator import AccessibilityValidator

                return AccessibilityValidator()
            except ImportError:
                self.logger.warning("PDF validator not available")
                return None

        # Add more validator types as needed
        return None

    def _validate_against_standard(
        self, validator: Validator, document_path: Path, standard: str
    ) -> Dict[str, Any]:
        """
        Validate document against a specific standard.

        Args:
            validator: Validator instance
            document_path: Path to document
            standard: Standard identifier

        Returns:
            Standard-specific validation results
        """
        standard_info = self._validation_standards[standard]

        result = {
            "standard": standard,
            "name": standard_info["name"],
            "description": standard_info["description"],
            "score": None,
            "status": "fail",
            "checks": {},
            "total_checks": 0,
            "passed_checks": 0,
            "failed_checks": 0,
            "warnings": [],
            "errors": [],
        }

        try:
            # Use the validator to get basic validation results
            validation_data = validator.validate(document_path)

            # Map validation data to standard-specific checks
            checks = standard_info["checks"]
            result["total_checks"] = len(checks)

            for check in checks:
                check_result = self._perform_check(validation_data, check)
                result["checks"][check] = check_result

                if check_result["status"] == "pass":
                    result["passed_checks"] += 1
                elif check_result["status"] == "fail":
                    result["failed_checks"] += 1

                if check_result.get("warnings"):
                    result["warnings"].extend(check_result["warnings"])

            # Calculate score
            if result["total_checks"] > 0:
                result["score"] = result["passed_checks"] / result["total_checks"]
                result["status"] = "pass" if result["score"] >= 0.8 else "fail"

        except Exception as e:
            result["errors"].append(f"Error validating against {standard}: {e}")

        return result

    def _perform_check(
        self, validation_data: Dict[str, Any], check: str
    ) -> Dict[str, Any]:
        """
        Perform a specific validation check.

        Args:
            validation_data: Raw validation data from validator
            check: Check identifier

        Returns:
            Check result
        """
        check_result = {"status": "fail", "message": "", "warnings": []}

        # Map check types to validation data fields
        check_mappings = {
            "has_title": lambda data: bool(data.get("metadata", {}).get("title")),
            "has_language": lambda data: bool(data.get("metadata", {}).get("language")),
            "has_structure": lambda data: data.get("structure_score", 0) > 0.5,
            "has_alt_text": lambda data: data.get("alt_text_coverage", 0) > 0.8,
            "proper_reading_order": lambda data: data.get("reading_order_score", 0)
            > 0.7,
            "proper_contrast": lambda data: data.get("contrast_score", 0) > 0.7,
            "keyboard_accessible": lambda data: data.get(
                "keyboard_accessibility", True
            ),
            "screen_reader_friendly": lambda data: data.get("screen_reader_score", 0)
            > 0.8,
            "proper_markup": lambda data: data.get("markup_score", 0) > 0.7,
        }

        if check in check_mappings:
            try:
                passed = check_mappings[check](validation_data)
                check_result["status"] = "pass" if passed else "fail"
                check_result[
                    "message"
                ] = f"Check '{check}': {'PASS' if passed else 'FAIL'}"
            except Exception as e:
                check_result["status"] = "error"
                check_result["message"] = f"Error performing check '{check}': {e}"
        else:
            check_result["status"] = "skip"
            check_result["message"] = f"Check '{check}' not implemented"

        return check_result

    def _generate_recommendations(
        self, validation_results: Dict[str, Any]
    ) -> List[str]:
        """
        Generate recommendations based on validation results.

        Args:
            validation_results: Complete validation results

        Returns:
            List of recommendation strings
        """
        recommendations = []

        # Check overall score
        if validation_results["overall_score"] < 0.5:
            recommendations.append(
                "Document requires significant accessibility improvements"
            )
        elif validation_results["overall_score"] < 0.8:
            recommendations.append(
                "Document has some accessibility issues that should be addressed"
            )

        # Check specific failed checks across all standards
        failed_checks = {}
        for standard_result in validation_results["standards"].values():
            for check, check_result in standard_result.get("checks", {}).items():
                if check_result["status"] == "fail":
                    failed_checks[check] = failed_checks.get(check, 0) + 1

        # Generate specific recommendations
        if "has_title" in failed_checks:
            recommendations.append("Add a descriptive title to the document")

        if "has_language" in failed_checks:
            recommendations.append(
                "Specify the document language for better accessibility"
            )

        if "has_structure" in failed_checks:
            recommendations.append(
                "Add proper document structure with headings and sections"
            )

        if "has_alt_text" in failed_checks:
            recommendations.append("Add alternative text descriptions for images")

        return recommendations

    def _generate_json_report(self, results: Dict[str, Any], output_path: Path) -> bool:
        """Generate JSON format report."""
        import json

        with open(output_path, "w") as f:
            json.dump(results, f, indent=2, default=str)

        self.logger.info(f"Generated JSON report: {output_path}")
        return True

    def _generate_html_report(self, results: Dict[str, Any], output_path: Path) -> bool:
        """Generate HTML format report."""
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Accessibility Validation Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .header {{ background-color: #f0f0f0; padding: 10px; border-radius: 5px; }}
        .pass {{ color: green; }}
        .fail {{ color: red; }}
        .summary {{ margin: 20px 0; }}
        .standard {{ margin: 15px 0; border: 1px solid #ddd; padding: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Accessibility Validation Report</h1>
        <p><strong>Document:</strong> {results['document_path']}</p>
        <p><strong>Overall Score:</strong> {results['overall_score']:.2f}</p>
        <p><strong>Status:</strong> <span class="{results['overall_status']}">{results['overall_status'].upper()}</span></p>
    </div>
    
    <div class="summary">
        <h2>Summary</h2>
        <ul>
            <li>Total Checks: {results['summary']['total_checks']}</li>
            <li>Passed: {results['summary']['passed_checks']}</li>
            <li>Failed: {results['summary']['failed_checks']}</li>
            <li>Warnings: {results['summary']['warnings']}</li>
        </ul>
    </div>
    
    <div class="standards">
        <h2>Standards</h2>
"""

        for standard, standard_result in results["standards"].items():
            html_content += f"""
        <div class="standard">
            <h3>{standard_result['name']}</h3>
            <p>{standard_result['description']}</p>
            <p><strong>Score:</strong> {standard_result.get('score', 0):.2f}</p>
            <p><strong>Status:</strong> <span class="{standard_result['status']}">{standard_result['status'].upper()}</span></p>
        </div>
"""

        html_content += """
    </div>
</body>
</html>
"""

        with open(output_path, "w") as f:
            f.write(html_content)

        self.logger.info(f"Generated HTML report: {output_path}")
        return True

    def _generate_csv_report(self, results: Dict[str, Any], output_path: Path) -> bool:
        """Generate CSV format report."""
        import csv

        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)

            # Header
            writer.writerow(["Document", "Standard", "Check", "Status", "Score"])

            # Data rows
            document = Path(results["document_path"]).name
            for standard, standard_result in results["standards"].items():
                for check, check_result in standard_result.get("checks", {}).items():
                    writer.writerow(
                        [
                            document,
                            standard,
                            check,
                            check_result["status"],
                            standard_result.get("score", 0),
                        ]
                    )

        self.logger.info(f"Generated CSV report: {output_path}")
        return True

    def _generate_text_report(self, results: Dict[str, Any], output_path: Path) -> bool:
        """Generate text format report."""
        content = f"""
ACCESSIBILITY VALIDATION REPORT
===============================

Document: {results['document_path']}
Overall Score: {results['overall_score']:.2f}
Status: {results['overall_status'].upper()}

SUMMARY
-------
Total Checks: {results['summary']['total_checks']}
Passed: {results['summary']['passed_checks']}
Failed: {results['summary']['failed_checks']}
Warnings: {results['summary']['warnings']}

STANDARDS
---------
"""

        for standard, standard_result in results["standards"].items():
            content += f"""
{standard_result['name']}
{'-' * len(standard_result['name'])}
Score: {standard_result.get('score', 0):.2f}
Status: {standard_result['status'].upper()}

Checks:
"""
            for check, check_result in standard_result.get("checks", {}).items():
                content += f"  - {check}: {check_result['status'].upper()}\n"

        if results.get("recommendations"):
            content += "\nRECOMMENDATIONS\n"
            content += "---------------\n"
            for rec in results["recommendations"]:
                content += f"- {rec}\n"

        with open(output_path, "w") as f:
            f.write(content)

        self.logger.info(f"Generated text report: {output_path}")
        return True
