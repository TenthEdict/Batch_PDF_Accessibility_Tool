#!/usr/bin/env python3
"""
PDF Accessibility Validation module.

This module provides functionality to validate PDF accessibility features:
- Checks for document metadata (title, author, language)
- Checks for document structure (tagged elements)
- Checks for reading order
- Generates validation reports
"""

import os
import sys
import logging
from pathlib import Path
import json
import csv
from datetime import datetime

try:
    import pikepdf
    from pikepdf import Pdf, Name, String, Dictionary, Array
except ImportError:
    print(
        "Error: pikepdf is not installed. Please install it in your virtual environment:"
    )
    print("pip install pikepdf")
    sys.exit(1)

logger = logging.getLogger(__name__)


class AccessibilityValidator:
    """PDF accessibility validation functionality."""

    def __init__(self):
        """Initialize the accessibility validator."""
        pass

    def validate_pdf(self, pdf_path):
        """
        Validate PDF accessibility features.

        Args:
            pdf_path: Path to the PDF file to validate

        Returns:
            dict: Validation results
        """
        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            logger.error(f"PDF file not found: {pdf_path}")
            return {
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "exists": False,
                "error": "File not found",
            }

        try:
            # Open the PDF file
            with pikepdf.open(pdf_path) as pdf:
                # Extract basic document information
                info = {
                    "filename": pdf_path.name,
                    "path": str(pdf_path),
                    "exists": True,
                    "filesize_bytes": pdf_path.stat().st_size,
                    "page_count": len(pdf.pages),
                    "timestamp": datetime.now().isoformat(),
                }

                # Validate document metadata
                info.update(self._validate_metadata(pdf))

                # Validate document structure
                info.update(self._validate_structure(pdf))

                # Check for PDF/UA compliance
                info.update(self._validate_pdfua(pdf))

                # Overall assessment
                info["overall_score"] = self._calculate_score(info)
                info["passes"] = info["overall_score"] >= 80

                return info

        except Exception as e:
            logger.error(f"Error validating PDF: {e}")
            import traceback

            traceback.print_exc()

            return {
                "filename": pdf_path.name,
                "path": str(pdf_path),
                "exists": True,
                "error": str(e),
                "validation_success": False,
            }

    def _validate_metadata(self, pdf):
        """
        Validate PDF metadata.

        Args:
            pdf: pikepdf.Pdf object

        Returns:
            dict: Metadata validation results
        """
        results = {"metadata": {}, "metadata_score": 0}

        total_checks = 0
        passed_checks = 0

        # Check document metadata
        with pdf.open_metadata() as meta:
            # Check for title
            has_title = "dc:title" in meta and meta["dc:title"].strip()
            results["metadata"]["has_title"] = has_title
            if has_title:
                results["metadata"]["title"] = meta["dc:title"]
                passed_checks += 1
            total_checks += 1

            # Check for author
            has_author = "dc:creator" in meta and meta["dc:creator"].strip()
            results["metadata"]["has_author"] = has_author
            if has_author:
                results["metadata"]["author"] = meta["dc:creator"]
                passed_checks += 1
            total_checks += 1

            # Check for language
            has_language = "dc:language" in meta and meta["dc:language"].strip()
            results["metadata"]["has_language"] = has_language
            if has_language:
                results["metadata"]["language"] = meta["dc:language"]
                passed_checks += 1
            total_checks += 1

        # Check for viewer preferences
        has_viewer_prefs = Name.ViewerPreferences in pdf.Root
        results["metadata"]["has_viewer_preferences"] = has_viewer_prefs

        # Check for display document title preference
        if has_viewer_prefs:
            display_title = (
                Name.DisplayDocTitle in pdf.Root.ViewerPreferences
                and pdf.Root.ViewerPreferences[Name.DisplayDocTitle]
            )
            results["metadata"]["displays_document_title"] = bool(display_title)
            if display_title:
                passed_checks += 1
        else:
            results["metadata"]["displays_document_title"] = False
        total_checks += 1

        # Calculate metadata score
        if total_checks > 0:
            results["metadata_score"] = int((passed_checks / total_checks) * 100)

        return results

    def _validate_structure(self, pdf):
        """
        Validate PDF document structure.

        Args:
            pdf: pikepdf.Pdf object

        Returns:
            dict: Structure validation results
        """
        results = {"structure": {}, "structure_score": 0}

        total_checks = 0
        passed_checks = 0

        # Check if document is marked as tagged
        is_tagged = (
            Name.MarkInfo in pdf.Root
            and Name.Marked in pdf.Root.MarkInfo
            and pdf.Root.MarkInfo[Name.Marked]
        )
        results["structure"]["is_tagged"] = bool(is_tagged)
        if is_tagged:
            passed_checks += 1
        total_checks += 1

        # Check if document has structure tree
        has_structure_tree = Name.StructTreeRoot in pdf.Root
        results["structure"]["has_structure_tree"] = has_structure_tree
        if has_structure_tree:
            passed_checks += 1
        total_checks += 1

        # Check for outlines (bookmarks)
        has_outlines = Name.Outlines in pdf.Root
        results["structure"]["has_outlines"] = has_outlines
        if has_outlines:
            passed_checks += 1
        total_checks += 1

        # Calculate structure score
        if total_checks > 0:
            results["structure_score"] = int((passed_checks / total_checks) * 100)

        return results

    def _validate_pdfua(self, pdf):
        """
        Validate PDF/UA compliance.

        Args:
            pdf: pikepdf.Pdf object

        Returns:
            dict: PDF/UA validation results
        """
        results = {"pdfua": {}, "pdfua_score": 0}

        total_checks = 0
        passed_checks = 0

        # Check metadata for PDF/UA identifiers
        with pdf.open_metadata() as meta:
            # Check for PDF/UA part identifier
            has_part = "pdfaid:part" in meta and meta["pdfaid:part"] == "1"
            results["pdfua"]["has_part_identifier"] = has_part
            if has_part:
                passed_checks += 1
            total_checks += 1

            # Check for PDF/UA conformance identifier
            has_conformance = (
                "pdfaid:conformance" in meta and meta["pdfaid:conformance"] == "A"
            )
            results["pdfua"]["has_conformance_identifier"] = has_conformance
            if has_conformance:
                passed_checks += 1
            total_checks += 1

        # Calculate PDF/UA score
        if total_checks > 0:
            results["pdfua_score"] = int((passed_checks / total_checks) * 100)

        return results

    def _calculate_score(self, results):
        """
        Calculate overall accessibility score.

        Args:
            results: Validation results

        Returns:
            int: Overall accessibility score (0-100)
        """
        weights = {
            "metadata_score": 0.3,  # 30% weight for metadata
            "structure_score": 0.5,  # 50% weight for structure
            "pdfua_score": 0.2,  # 20% weight for PDF/UA compliance
        }

        weighted_score = 0
        for key, weight in weights.items():
            if key in results:
                weighted_score += results[key] * weight

        return int(weighted_score)

    def generate_json_report(self, validation_results, output_path):
        """
        Generate JSON validation report.

        Args:
            validation_results: Validation results
            output_path: Path to save the JSON report

        Returns:
            bool: True if report was generated successfully, False otherwise
        """
        output_path = Path(output_path)

        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Write validation results to JSON file
            with open(output_path, "w") as f:
                json.dump(validation_results, f, indent=2)

            logger.info(f"JSON validation report saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating JSON report: {e}")
            return False

    def generate_csv_report(self, validation_results_list, output_path):
        """
        Generate CSV validation report for multiple PDFs.

        Args:
            validation_results_list: List of validation results
            output_path: Path to save the CSV report

        Returns:
            bool: True if report was generated successfully, False otherwise
        """
        output_path = Path(output_path)

        try:
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Define CSV fields
            fields = [
                "filename",
                "path",
                "exists",
                "overall_score",
                "passes",
                "metadata_score",
                "structure_score",
                "pdfua_score",
                "metadata.has_title",
                "metadata.has_author",
                "metadata.has_language",
                "metadata.displays_document_title",
                "structure.is_tagged",
                "structure.has_structure_tree",
                "structure.has_outlines",
                "pdfua.has_part_identifier",
                "pdfua.has_conformance_identifier",
            ]

            # Write validation results to CSV file
            with open(output_path, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=fields)
                writer.writeheader()

                for result in validation_results_list:
                    # Flatten nested dictionaries
                    flat_result = {
                        "filename": result.get("filename", ""),
                        "path": result.get("path", ""),
                        "exists": result.get("exists", False),
                        "overall_score": result.get("overall_score", 0),
                        "passes": result.get("passes", False),
                        "metadata_score": result.get("metadata_score", 0),
                        "structure_score": result.get("structure_score", 0),
                        "pdfua_score": result.get("pdfua_score", 0),
                    }

                    # Add metadata fields
                    if "metadata" in result:
                        for key, value in result["metadata"].items():
                            flat_result[f"metadata.{key}"] = value

                    # Add structure fields
                    if "structure" in result:
                        for key, value in result["structure"].items():
                            flat_result[f"structure.{key}"] = value

                    # Add PDF/UA fields
                    if "pdfua" in result:
                        for key, value in result["pdfua"].items():
                            flat_result[f"pdfua.{key}"] = value

                    writer.writerow(flat_result)

            logger.info(f"CSV validation report saved to: {output_path}")
            return True
        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            return False

    def batch_validate(self, input_dir, report_format="json", output_dir=None):
        """
        Validate multiple PDF files in a directory.

        Args:
            input_dir: Directory containing PDF files to validate
            report_format: Report format ('json' or 'csv')
            output_dir: Directory to save validation reports

        Returns:
            list: List of validation results
        """
        input_dir = Path(input_dir)

        if not input_dir.exists() or not input_dir.is_dir():
            logger.error(f"Input directory not found: {input_dir}")
            return []

        # Use input directory if output directory is not specified
        if output_dir is None:
            output_dir = input_dir
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Find all PDF files in the input directory
        pdf_files = list(input_dir.glob("*.pdf"))
        if not pdf_files:
            logger.warning(f"No PDF files found in: {input_dir}")
            return []

        logger.info(f"Found {len(pdf_files)} PDF files to validate")

        # Validate each PDF file
        results = []

        for pdf_file in pdf_files:
            logger.info(f"Validating: {pdf_file.name}")
            result = self.validate_pdf(pdf_file)
            results.append(result)

            # Generate individual JSON report if requested
            if report_format == "json":
                output_path = output_dir / f"{pdf_file.stem}_validation.json"
                self.generate_json_report(result, output_path)

        # Generate combined CSV report if requested
        if report_format == "csv":
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"validation_report_{timestamp}.csv"
            self.generate_csv_report(results, output_path)

        logger.info(f"Batch validation complete: {len(results)} PDFs processed")

        return results


def main():
    """Command-line interface for PDF accessibility validation."""
    import argparse

    parser = argparse.ArgumentParser(description="Validate PDF accessibility features")

    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")

    # Single PDF command
    single_parser = subparsers.add_parser("single", help="Validate a single PDF file")
    single_parser.add_argument("pdf_path", help="Path to the PDF file to validate")
    single_parser.add_argument("--output", help="Path to save the validation report")
    single_parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Report format (default: json)",
    )

    # Batch command
    batch_parser = subparsers.add_parser("batch", help="Validate multiple PDF files")
    batch_parser.add_argument(
        "input_dir", help="Directory containing PDF files to validate"
    )
    batch_parser.add_argument(
        "--output-dir", help="Directory to save validation reports"
    )
    batch_parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Report format (default: json)",
    )

    args = parser.parse_args()

    validator = AccessibilityValidator()

    if args.command == "single":
        result = validator.validate_pdf(args.pdf_path)

        if args.output:
            output_path = args.output
        else:
            # Default output path
            input_path = Path(args.pdf_path)
            output_path = input_path.with_suffix(f".{args.format}")

        if args.format == "json":
            success = validator.generate_json_report(result, output_path)
        else:  # csv
            success = validator.generate_csv_report([result], output_path)

        # Print summary to console
        print(f"Validation Results for: {result.get('filename', '')}")
        print(f"Overall Score: {result.get('overall_score', 0)}/100")
        print(f"Passes: {'Yes' if result.get('passes', False) else 'No'}")
        print(f"Metadata Score: {result.get('metadata_score', 0)}/100")
        print(f"Structure Score: {result.get('structure_score', 0)}/100")
        print(f"PDF/UA Score: {result.get('pdfua_score', 0)}/100")

        return 0 if success else 1

    elif args.command == "batch":
        results = validator.batch_validate(args.input_dir, args.format, args.output_dir)

        # Print summary to console
        passed = sum(1 for result in results if result.get("passes", False))
        print(f"Batch Validation Results:")
        print(f"Total PDFs: {len(results)}")
        print(f"Passed: {passed}")
        print(f"Failed: {len(results) - passed}")

        return 0 if results else 1

    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    # Configure logging for CLI
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sys.exit(main())
