#!/usr/bin/env python3
"""
Integration test for simplified ePubs processor.

Tests the complete pipeline:
1. Simple OCR enhancer
2. Simple PDF/UA enhancer
3. Simple enhancement service
4. End-to-end PDF processing
"""

import os
import sys
from pathlib import Path
import tempfile
import shutil

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.processor.simple_enhancement_service import SimpleEnhancementService
from src.processor.simple_ocr_enhancer import SimpleOCREnhancer
from src.processor.simple_pdfua_enhancer import SimplePDFUAEnhancer

try:
    import pikepdf
    PIKEPDF_AVAILABLE = True
except ImportError:
    PIKEPDF_AVAILABLE = False
    print("WARNING: pikepdf not available, some tests will be skipped")


def test_imports():
    """Test that all simplified modules can be imported."""
    print("Testing simplified module imports...")

    try:
        # Import only the simplified modules (not legacy Phase 2B modules)
        import processor.unified_project.src.enhancers.simple_ocr_enhancer
        import processor.unified_project.src.enhancers.simple_pdfua_enhancer
        import processor.unified_project.src.services.simple_enhancement_service
        import processor.unified_project.src.batch.simple_batch_processor
        print("✓ All simplified modules import successfully")
        return True
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_ocr_enhancer_instantiation():
    """Test that OCR enhancer can be instantiated."""
    print("Testing OCR enhancer instantiation...")

    try:
        enhancer = SimpleOCREnhancer()
        assert enhancer is not None
        assert enhancer.text_threshold == 100
        assert enhancer.dpi == 300
        assert enhancer.language == 'eng'
        print("✓ OCR enhancer instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ OCR enhancer instantiation failed: {e}")
        return False


def test_pdfua_enhancer_instantiation():
    """Test that PDF/UA enhancer can be instantiated."""
    print("Testing PDF/UA enhancer instantiation...")

    try:
        enhancer = SimplePDFUAEnhancer()
        assert enhancer is not None
        assert enhancer.name == "simple_pdfua_enhancer"
        print("✓ PDF/UA enhancer instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ PDF/UA enhancer instantiation failed: {e}")
        return False


def test_service_instantiation():
    """Test that enhancement service can be instantiated."""
    print("Testing enhancement service instantiation...")

    try:
        service = SimpleEnhancementService()
        assert service is not None
        assert service.ocr_enhancer is not None
        assert service.pdfua_enhancer is not None
        print("✓ Enhancement service instantiated successfully")
        return True
    except Exception as e:
        print(f"✗ Enhancement service instantiation failed: {e}")
        return False


def test_end_to_end_processing():
    """Test end-to-end PDF processing (if test file exists)."""
    print("Testing end-to-end processing...")

    # Look for a test PDF
    test_pdf_paths = [
        project_root / "data/input/Ahmed et al. - 2025 - Using thematic analysis in qualitative research.pdf",
        project_root / "data/input/test.pdf",
        project_root / "data/output/test_logging_output.pdf",
    ]

    test_pdf = None
    for path in test_pdf_paths:
        if path.exists():
            test_pdf = path
            break

    if not test_pdf:
        print("⚠ No test PDF found, skipping end-to-end test")
        return None

    print(f"Using test PDF: {test_pdf}")

    try:
        # Create temporary output file
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
            output_path = Path(tmp.name)

        # Process the PDF (skip OCR for speed)
        service = SimpleEnhancementService()
        success = service.enhance_document(
            test_pdf,
            output_path,
            skip_ocr=True,
            title="Test Document"
        )

        if not success:
            print("✗ PDF processing failed")
            return False

        # Verify output exists
        if not output_path.exists():
            print("✗ Output PDF not created")
            return False

        # Verify output size
        output_size = output_path.stat().st_size
        if output_size == 0:
            print("✗ Output PDF is empty")
            return False

        print(f"✓ PDF processed successfully ({output_size:,} bytes)")

        # Verify PDF/UA compliance (if pikepdf available)
        if PIKEPDF_AVAILABLE:
            pdf = pikepdf.open(output_path)

            has_tree = "/StructTreeRoot" in pdf.Root

            # MarkInfo must reflect whether a structure tree exists
            marked = bool(pdf.Root.get("/MarkInfo", {}).get("/Marked", False))
            if marked != has_tree:
                print(f"✗ MarkInfo Marked={marked} but StructTreeRoot present={has_tree}")
                return False

            # Check language
            if "/Lang" not in pdf.Root:
                print("✗ Language not set")
                return False

            # No non-standard PDF/UA OutputIntent
            for intent in pdf.Root.get("/OutputIntents", []):
                if intent.get("/S") == "/GTS_PDFUA1":
                    print("✗ Non-standard GTS_PDFUA1 OutputIntent present")
                    return False

            # Untagged output must not claim PDF/UA-1 conformance
            with pdf.open_metadata() as meta:
                if not has_tree and "pdfuaid:part" in meta:
                    print("✗ Untagged PDF claims PDF/UA-1 (pdfuaid:part)")
                    return False

            pdf.close()
            print("✓ Tagging state and metadata verified")

        # Cleanup
        output_path.unlink()

        print("✓ End-to-end processing successful")
        return True

    except Exception as e:
        print(f"✗ End-to-end processing failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n" + "="*70)
    print("ePubs Simplified Integration Tests")
    print("="*70 + "\n")

    results = {}

    # Run tests
    results['imports'] = test_imports()
    results['ocr_instantiation'] = test_ocr_enhancer_instantiation()
    results['pdfua_instantiation'] = test_pdfua_enhancer_instantiation()
    results['service_instantiation'] = test_service_instantiation()
    results['end_to_end'] = test_end_to_end_processing()

    # Summary
    print("\n" + "="*70)
    print("Test Summary")
    print("="*70)

    passed = sum(1 for v in results.values() if v is True)
    failed = sum(1 for v in results.values() if v is False)
    skipped = sum(1 for v in results.values() if v is None)
    total = len(results)

    for test_name, result in results.items():
        status = "✓ PASS" if result is True else "⚠ SKIP" if result is None else "✗ FAIL"
        print(f"{status:10s} {test_name}")

    print(f"\nResults: {passed} passed, {failed} failed, {skipped} skipped out of {total} tests")

    if failed > 0:
        print("\n⚠ Some tests failed")
        return 1
    elif skipped > 0:
        print("\n✓ All available tests passed (some skipped)")
        return 0
    else:
        print("\n✓ All tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
