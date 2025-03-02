#!/usr/bin/env python3
"""
PDF Accessibility Validator

Checks PDFs for accessibility features and compliance, including:
1. Document tagging
2. Document structure
3. Language setting
4. Metadata
5. PDF/UA compliance markers

Usage: python validate_accessibility.py <pdf_file> [--detailed]
"""

import os
import sys
import logging
import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

try:
    import pikepdf
    import fitz  # PyMuPDF
except ImportError as e:
    logger.error(f"Error importing required libraries: {e}")
    logger.error("Please install required libraries with: pip install pikepdf PyMuPDF")
    sys.exit(1)

class AccessibilityChecker:
    """Check PDF accessibility features"""
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.results = {
            "filename": os.path.basename(pdf_path),
            "path": pdf_path,
            "is_accessible": False,
            "issues": [],
            "features": {},
            "metadata": {},
            "structure": {},
            "compliance": {}
        }
        
    def check(self, detailed: bool = False) -> Dict[str, Any]:
        """
        Check PDF for accessibility features
        
        Args:
            detailed: Whether to include detailed information in the results
            
        Returns:
            Dictionary with accessibility check results
        """
        logger.info(f"Checking accessibility of: {self.pdf_path}")
        
        try:
            # Check if file exists
            if not os.path.isfile(self.pdf_path):
                self.results["issues"].append("File not found")
                return self.results
                
            # Open PDF with pikepdf for structure checking
            with pikepdf.open(self.pdf_path) as pdf:
                # Check metadata
                self._check_metadata(pdf)
                
                # Check document language
                self._check_language(pdf)
                
                # Check if tagged
                self._check_tagged(pdf)
                
                # Check document structure
                self._check_structure(pdf)
                
                # Check for PDF/UA compliance
                self._check_pdf_ua_compliance(pdf)
                
                # Check viewer preferences
                self._check_viewer_preferences(pdf)
                
            # Additional checks with PyMuPDF
            with fitz.open(self.pdf_path) as doc:
                # Check for images without alt text
                self._check_images(doc)
                
                # Check for OCR text
                self._check_text_content(doc)
                
                # Add detailed structure analysis if requested
                if detailed:
                    self._analyze_structure_details(doc)
            
            # Determine accessibility status
            required_features = [
                "is_tagged", "has_structure", "has_language", "has_title"
            ]
            
            self.results["is_accessible"] = all(
                self.results["features"].get(feature, False) 
                for feature in required_features
            )
            
            # Generate summary
            self._generate_summary()
            
            return self.results
            
        except Exception as e:
            logger.error(f"Error checking accessibility: {e}")
            import traceback
            traceback.print_exc()
            self.results["issues"].append(f"Error: {str(e)}")
            return self.results
    
    def _check_metadata(self, pdf):
        """Check PDF metadata"""
        try:
            # Extract metadata
            metadata = {}
            if hasattr(pdf, 'docinfo') and pdf.docinfo:
                for key, value in pdf.docinfo.items():
                    metadata[str(key)] = str(value)
            
            # Check for title
            has_title = '/Title' in metadata and metadata['/Title']
            self.results["features"]["has_title"] = has_title
            if not has_title:
                self.results["issues"].append("Missing document title")
            
            # Store metadata
            self.results["metadata"] = metadata
        except Exception as e:
            logger.error(f"Error checking metadata: {e}")
            self.results["issues"].append(f"Metadata error: {str(e)}")
    
    def _check_language(self, pdf):
        """Check document language"""
        try:
            has_language = '/Lang' in pdf.Root
            language = str(pdf.Root.get('/Lang', '')) if has_language else None
            
            self.results["features"]["has_language"] = has_language
            self.results["features"]["language"] = language
            
            if not has_language:
                self.results["issues"].append("Missing document language")
            elif language == '':
                self.results["issues"].append("Empty document language")
        except Exception as e:
            logger.error(f"Error checking language: {e}")
            self.results["issues"].append(f"Language error: {str(e)}")
    
    def _check_tagged(self, pdf):
        """Check if PDF is tagged"""
        try:
            # Check for MarkInfo and Marked flag
            has_mark_info = '/MarkInfo' in pdf.Root
            is_marked = (has_mark_info and 
                       '/Marked' in pdf.Root['/MarkInfo'] and 
                       pdf.Root['/MarkInfo']['/Marked'])
            
            self.results["features"]["is_tagged"] = is_marked
            
            if not is_marked:
                self.results["issues"].append("PDF is not tagged")
        except Exception as e:
            logger.error(f"Error checking if tagged: {e}")
            self.results["issues"].append(f"Tag check error: {str(e)}")
    
    def _check_structure(self, pdf):
        """Check document structure"""
        try:
            # Check for structure tree
            has_structure_tree = '/StructTreeRoot' in pdf.Root
            
            # Check for document structure element
            has_document_element = False
            if has_structure_tree and '/K' in pdf.Root['/StructTreeRoot']:
                k_obj = pdf.Root['/StructTreeRoot']['/K']
                if isinstance(k_obj, pikepdf.Dictionary) and '/S' in k_obj:
                    has_document_element = str(k_obj['/S']) == '/Document'
            
            self.results["features"]["has_structure"] = has_structure_tree
            self.results["features"]["has_document_element"] = has_document_element
            
            # Check for parent tree (required for PDF/UA)
            has_parent_tree = (has_structure_tree and 
                              '/ParentTree' in pdf.Root['/StructTreeRoot'])
            self.results["features"]["has_parent_tree"] = has_parent_tree
            
            # Check for role map
            has_role_map = (has_structure_tree and 
                           '/RoleMap' in pdf.Root['/StructTreeRoot'])
            self.results["features"]["has_role_map"] = has_role_map
            
            if not has_structure_tree:
                self.results["issues"].append("Missing document structure tree")
            elif not has_document_element:
                self.results["issues"].append("Missing document element in structure")
        except Exception as e:
            logger.error(f"Error checking structure: {e}")
            self.results["issues"].append(f"Structure check error: {str(e)}")
    
    def _check_pdf_ua_compliance(self, pdf):
        """Check for PDF/UA compliance markers"""
        try:
            # Check for XMP metadata
            has_xmp = '/Metadata' in pdf.Root
            
            # Check for PDF/UA identifier in XMP
            has_pdf_ua_identifier = False
            if has_xmp:
                try:
                    metadata_str = pdf.Root['/Metadata'].read_bytes().decode('utf-8')
                    has_pdf_ua_identifier = 'pdfuaid:part' in metadata_str or 'pdfua:part' in metadata_str
                except:
                    pass
            
            self.results["compliance"]["has_xmp"] = has_xmp
            self.results["compliance"]["has_pdf_ua_identifier"] = has_pdf_ua_identifier
            
            if not has_xmp:
                self.results["issues"].append("Missing XMP metadata")
            elif not has_pdf_ua_identifier:
                self.results["issues"].append("Missing PDF/UA identifier in XMP metadata")
        except Exception as e:
            logger.error(f"Error checking PDF/UA compliance: {e}")
            self.results["issues"].append(f"PDF/UA check error: {str(e)}")
    
    def _check_viewer_preferences(self, pdf):
        """Check viewer preferences"""
        try:
            # Check for viewer preferences
            has_viewer_prefs = '/ViewerPreferences' in pdf.Root
            
            # Check for DisplayDocTitle preference
            display_doc_title = False
            if has_viewer_prefs and '/DisplayDocTitle' in pdf.Root['/ViewerPreferences']:
                display_doc_title = bool(pdf.Root['/ViewerPreferences']['/DisplayDocTitle'])
            
            self.results["features"]["has_viewer_preferences"] = has_viewer_prefs
            self.results["features"]["display_doc_title"] = display_doc_title
            
            if not display_doc_title:
                self.results["issues"].append("DisplayDocTitle preference not set")
        except Exception as e:
            logger.error(f"Error checking viewer preferences: {e}")
            self.results["issues"].append(f"Viewer preferences error: {str(e)}")
    
    def _check_images(self, doc):
        """Check for images without alt text"""
        try:
            # Count images
            image_count = 0
            alt_text_count = 0
            
            # This is a simplified approach - full implementation would be more complex
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get images on page
                img_list = page.get_images(full=True)
                for img in img_list:
                    image_count += 1
                    
                    # Full implementation would check for actual alt text
                    # but this requires analyzing the marked content - complex
            
            self.results["structure"]["image_count"] = image_count
            self.results["structure"]["images_with_alt_text"] = alt_text_count
            
            if image_count > 0 and alt_text_count < image_count:
                self.results["issues"].append(f"Found {image_count - alt_text_count} images without alt text")
        except Exception as e:
            logger.error(f"Error checking images: {e}")
            self.results["issues"].append(f"Image check error: {str(e)}")
    
    def _check_text_content(self, doc):
        """Check for text content"""
        try:
            # Check if document has text
            text_length = 0
            for page_num in range(len(doc)):
                page = doc[page_num]
                text_length += len(page.get_text())
            
            has_text = text_length > 0
            self.results["features"]["has_text"] = has_text
            self.results["structure"]["text_length"] = text_length
            
            if not has_text:
                self.results["issues"].append("Document has no text content")
        except Exception as e:
            logger.error(f"Error checking text content: {e}")
            self.results["issues"].append(f"Text content check error: {str(e)}")
    
    def _analyze_structure_details(self, doc):
        """Analyze document structure in detail"""
        try:
            structure_details = {}
            
            # Count pages
            structure_details["page_count"] = len(doc)
            
            # Count bookmarks
            toc = doc.get_toc()
            structure_details["bookmark_count"] = len(toc)
            
            # Check for page labels
            try:
                labels = doc.get_page_labels()
                structure_details["has_page_labels"] = len(labels) > 0
            except:
                structure_details["has_page_labels"] = False
            
            # Analyze form fields
            structure_details["form_fields_count"] = 0
            try:
                for page in doc:
                    widgets = page.widgets()
                    structure_details["form_fields_count"] += len(widgets)
            except:
                pass
            
            self.results["structure"].update(structure_details)
        except Exception as e:
            logger.error(f"Error analyzing structure details: {e}")
            self.results["issues"].append(f"Structure analysis error: {str(e)}")
    
    def _generate_summary(self):
        """Generate an accessibility summary"""
        summary = {
            "accessibility_score": self._calculate_score(),
            "complies_with_pdf_ua": self.results["compliance"].get("has_pdf_ua_identifier", False),
            "issue_count": len(self.results["issues"]),
            "critical_issues": self._count_critical_issues(),
            "recommendation": self._get_recommendation()
        }
        
        self.results["summary"] = summary
    
    def _calculate_score(self):
        """Calculate an accessibility score (0-100)"""
        # Define feature weights
        weights = {
            "is_tagged": 25,
            "has_structure": 20,
            "has_language": 15,
            "has_title": 10,
            "display_doc_title": 5,
            "has_text": 10,
            "has_document_element": 5,
            "has_pdf_ua_identifier": 10
        }
        
        score = 0
        for feature, weight in weights.items():
            feature_key = feature
            if feature == "has_pdf_ua_identifier":
                value = self.results["compliance"].get(feature, False)
            else:
                value = self.results["features"].get(feature, False)
                
            if value:
                score += weight
        
        return min(score, 100)
    
    def _count_critical_issues(self):
        """Count critical accessibility issues"""
        critical_patterns = [
            "not tagged", 
            "Missing document", 
            "Missing structure",
            "no text content"
        ]
        
        critical_count = 0
        for issue in self.results["issues"]:
            for pattern in critical_patterns:
                if pattern.lower() in issue.lower():
                    critical_count += 1
                    break
        
        return critical_count
    
    def _get_recommendation(self):
        """Get recommendation based on issues"""
        score = self.results["summary"]["accessibility_score"]
        
        if score >= 90:
            return "PDF meets most accessibility requirements"
        elif score >= 70:
            return "PDF needs minor accessibility improvements"
        elif score >= 40:
            return "PDF needs significant accessibility improvements"
        else:
            return "PDF requires complete accessibility remediation"


def print_report(results: Dict[str, Any], detailed: bool = False):
    """
    Print accessibility report
    
    Args:
        results: Accessibility check results
        detailed: Whether to include detailed information
    """
    print("\n" + "=" * 80)
    print(f"PDF ACCESSIBILITY REPORT: {results['filename']}")
    print("=" * 80)
    
    # Print summary
    summary = results.get("summary", {})
    score = summary.get("accessibility_score", 0)
    print(f"\nACCESSIBILITY SCORE: {score}/100")
    print(f"Status: {'🟢 Accessible' if results['is_accessible'] else '🔴 Not Accessible'}")
    print(f"PDF/UA Compliance: {'✓ Yes' if summary.get('complies_with_pdf_ua', False) else '✗ No'}")
    print(f"Issues: {summary.get('issue_count', 0)} ({summary.get('critical_issues', 0)} critical)")
    print(f"\nRECOMMENDATION: {summary.get('recommendation', '')}")
    
    # Print issues
    print("\nISSUES:")
    if results["issues"]:
        for i, issue in enumerate(results["issues"], 1):
            print(f"  {i}. {issue}")
    else:
        print("  No issues found")
    
    # Print accessibility features
    print("\nACCESSIBILITY FEATURES:")
    features = results.get("features", {})
    print(f"  ✓ Tagged PDF: {'Yes' if features.get('is_tagged', False) else 'No'}")
    print(f"  ✓ Document Structure: {'Yes' if features.get('has_structure', False) else 'No'}")
    print(f"  ✓ Document Language: {features.get('language', 'Not specified')}")
    print(f"  ✓ Document Title: {'Yes' if features.get('has_title', False) else 'No'}")
    print(f"  ✓ DisplayDocTitle: {'Yes' if features.get('display_doc_title', False) else 'No'}")
    
    # Print detailed information if requested
    if detailed:
        # Print metadata
        print("\nDOCUMENT METADATA:")
        metadata = results.get("metadata", {})
        if metadata:
            for key, value in metadata.items():
                if value and len(str(value)) < 100:  # Skip empty or very long values
                    print(f"  {key}: {value}")
        else:
            print("  No metadata found")
        
        # Print structure information
        print("\nSTRUCTURE INFORMATION:")
        structure = results.get("structure", {})
        print(f"  Pages: {structure.get('page_count', 'Unknown')}")
        print(f"  Bookmarks: {structure.get('bookmark_count', 0)}")
        print(f"  Images: {structure.get('image_count', 0)} (Alt text: {structure.get('images_with_alt_text', 0)})")
        print(f"  Form Fields: {structure.get('form_fields_count', 0)}")
        print(f"  Text Length: {structure.get('text_length', 0)} characters")
    
    print("\n" + "=" * 80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description='Check PDF for accessibility features')
    parser.add_argument('pdf_file', help='Path to PDF file to check')
    parser.add_argument('--detailed', action='store_true', help='Include detailed information in report')
    parser.add_argument('--json', help='Save results to JSON file')
    
    args = parser.parse_args()
    
    # Check PDF
    checker = AccessibilityChecker(args.pdf_file)
    results = checker.check(detailed=args.detailed)
    
    # Print report
    print_report(results, detailed=args.detailed)
    
    # Save to JSON if requested
    if args.json:
        with open(args.json, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nSaved detailed results to: {args.json}")
    
    # Return success if PDF is accessible
    return 0 if results["is_accessible"] else 1


if __name__ == "__main__":
    sys.exit(main())