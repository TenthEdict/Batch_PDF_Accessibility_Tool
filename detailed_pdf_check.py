#!/usr/bin/env python3
import sys
import os

try:
    from PyPDF2 import PdfReader
    HAVE_PYPDF2 = True
except ImportError:
    HAVE_PYPDF2 = False
    print("PyPDF2 not installed. Install with: pip install PyPDF2")
    print("Continuing with limited functionality...\n")

def check_pdf_accessibility(pdf_path):
    """Perform detailed PDF accessibility check using PyPDF2 if available"""
    if not os.path.isfile(pdf_path):
        print(f"Error: File {pdf_path} does not exist")
        return
    
    print(f"Analyzing PDF: {pdf_path}")
    filesize = os.path.getsize(pdf_path) / (1024 * 1024)
    print(f"File size: {filesize:.2f} MB")
    
    if not HAVE_PYPDF2:
        print("Cannot perform detailed analysis without PyPDF2")
        return
    
    try:
        # Open the PDF
        with open(pdf_path, 'rb') as file:
            pdf = PdfReader(file)
            
            # Basic document info
            print("\n=== DOCUMENT PROPERTIES ===")
            info = pdf.metadata
            if info:
                for key, value in info.items():
                    if key.startswith('/'):
                        key = key[1:]
                    print(f"{key}: {value}")
            else:
                print("No metadata found")
            
            # Document structure
            print(f"\n=== DOCUMENT STRUCTURE ===")
            print(f"Pages: {len(pdf.pages)}")
            
            # Check for PDF/UA compliance
            print("\n=== ACCESSIBILITY FEATURES ===")
            
            # Check if document is tagged
            is_tagged = False
            if pdf.trailer:
                if "/MarkInfo" in pdf.trailer.get("/Root", {}):
                    mark_info = pdf.trailer["/Root"]["/MarkInfo"]
                    if "/Marked" in mark_info and mark_info["/Marked"]:
                        is_tagged = True
            
            if is_tagged:
                print("✓ Document is tagged (contains structural markup)")
            else:
                print("✗ Document is NOT tagged - accessibility issues likely")
            
            # Check if document has OCR text
            text_analysis = {
                "pages_with_text": 0,
                "empty_pages": 0,
                "avg_chars_per_page": 0,
                "total_chars": 0
            }
            
            for i, page in enumerate(pdf.pages):
                text = page.extract_text() or ""
                char_count = len(text)
                text_analysis["total_chars"] += char_count
                
                if char_count > 50:  # Assume page has meaningful text if > 50 chars
                    text_analysis["pages_with_text"] += 1
                else:
                    text_analysis["empty_pages"] += 1
            
            if len(pdf.pages) > 0:
                text_analysis["avg_chars_per_page"] = text_analysis["total_chars"] / len(pdf.pages)
            
            # Report text findings
            print(f"\n=== TEXT CONTENT ANALYSIS ===")
            print(f"Pages with significant text: {text_analysis['pages_with_text']} of {len(pdf.pages)}")
            print(f"Pages with no/minimal text: {text_analysis['empty_pages']} of {len(pdf.pages)}")
            print(f"Average characters per page: {text_analysis['avg_chars_per_page']:.1f}")
            
            if text_analysis["avg_chars_per_page"] < 100 and len(pdf.pages) > 0:
                print("⚠️ Low text content detected - document may be image-based with poor OCR")
            
            # Check for annotations (might indicate form fields or comments)
            has_annotations = False
            for page in pdf.pages:
                if "/Annots" in page and page["/Annots"]:
                    has_annotations = True
                    break
            
            if has_annotations:
                print("ℹ️ Document contains annotations (may include form fields)")
            
            # Overall assessment
            print("\n=== OVERALL ACCESSIBILITY ASSESSMENT ===")
            if is_tagged and text_analysis["pages_with_text"] >= len(pdf.pages) * 0.9:
                print("🟢 Document appears to have basic accessibility features")
            elif is_tagged or text_analysis["pages_with_text"] >= len(pdf.pages) * 0.9:
                print("🟡 Document has some accessibility features but may need improvements")
            else:
                print("🔴 Document appears to lack essential accessibility features")
                
            print("\nRecommendations:")
            if not is_tagged:
                print("- Add document structure tags")
            if text_analysis["empty_pages"] > 0:
                print(f"- Review {text_analysis['empty_pages']} pages with missing/minimal text")
            print("- Ensure all images have alternative text")
            print("- Check reading order for logical flow")
            print("- Verify document has appropriate headings structure")
                
    except Exception as e:
        print(f"Error analyzing PDF: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python detailed_pdf_check.py <path_to_pdf>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    check_pdf_accessibility(pdf_path)