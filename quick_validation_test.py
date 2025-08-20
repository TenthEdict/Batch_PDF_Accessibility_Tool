#!/usr/bin/env python3
"""
Quick Validation Test for Accessibility Training System

This script performs a basic validation of the training system components
to ensure they are working correctly after the import fixes.

Usage:
    python quick_validation_test.py
"""

import sys
from pathlib import Path

# Add project path for imports
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def test_imports():
    """Test that all required modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        from processor.unified_project.src.training.accessibility_data_extractor import AccessibilityDataExtractor
        print("✅ AccessibilityDataExtractor imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import AccessibilityDataExtractor: {e}")
        return False
    
    try:
        from processor.unified_project.src.training.organize_training_data import TrainingDataOrganizer
        print("✅ TrainingDataOrganizer imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import TrainingDataOrganizer: {e}")
        return False
    
    try:
        from processor.unified_project.src.training import AccessibilityDataExtractor as ImportedADE
        print("✅ Training module __init__.py imports working")
    except ImportError as e:
        print(f"❌ Failed to import from training module: {e}")
        return False
    
    return True

def test_dependencies():
    """Test that required dependencies are available."""
    print("\n🧪 Testing dependencies...")
    
    dependencies = [
        ('fitz', 'PyMuPDF'),
        ('pikepdf', 'pikepdf'),
        ('numpy', 'numpy'),
        ('pandas', 'pandas'),
        ('sklearn', 'scikit-learn')
    ]
    
    missing_deps = []
    for dep_name, package_name in dependencies:
        try:
            __import__(dep_name)
            print(f"✅ {package_name} available")
        except ImportError:
            print(f"❌ {package_name} missing")
            missing_deps.append(package_name)
    
    if missing_deps:
        print(f"\n⚠️  Missing dependencies: {', '.join(missing_deps)}")
        print("Install with: pip install " + " ".join(missing_deps))
        return False
    
    return True

def test_class_instantiation():
    """Test that classes can be instantiated."""
    print("\n🧪 Testing class instantiation...")
    
    try:
        from processor.unified_project.src.training.accessibility_data_extractor import AccessibilityDataExtractor
        
        # Test basic instantiation
        output_dir = Path("/tmp/test_accessibility_extraction")
        output_dir.mkdir(exist_ok=True)
        
        extractor = AccessibilityDataExtractor(output_dir)
        print("✅ AccessibilityDataExtractor instantiated successfully")
        
        # Test basic methods exist
        assert hasattr(extractor, 'extract_document_profile'), "extract_document_profile method missing"
        assert hasattr(extractor, 'batch_extract_profiles'), "batch_extract_profiles method missing"
        print("✅ AccessibilityDataExtractor has required methods")
        
    except Exception as e:
        print(f"❌ Failed to instantiate AccessibilityDataExtractor: {e}")
        return False
    
    try:
        from processor.unified_project.src.training.organize_training_data import TrainingDataOrganizer
        
        # Test basic instantiation
        source_dir = Path("/tmp/test_source")
        output_dir = Path("/tmp/test_output")
        source_dir.mkdir(exist_ok=True)
        output_dir.mkdir(exist_ok=True)
        
        organizer = TrainingDataOrganizer(source_dir, output_dir)
        print("✅ TrainingDataOrganizer instantiated successfully")
        
        # Test basic methods exist
        assert hasattr(organizer, 'validate_source_pdfs'), "validate_source_pdfs method missing"
        assert hasattr(organizer, 'create_training_splits'), "create_training_splits method missing"
        print("✅ TrainingDataOrganizer has required methods")
        
    except Exception as e:
        print(f"❌ Failed to instantiate TrainingDataOrganizer: {e}")
        return False
    
    return True

def test_cli_accessibility():
    """Test that CLI commands are accessible."""
    print("\n🧪 Testing CLI accessibility...")
    
    try:
        import subprocess
        import sys
        
        # Test that the main module can be executed
        result = subprocess.run([
            sys.executable, "-m", "processor.unified_project.src.main", "--help"
        ], cwd=project_root, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0 and "organize-training-data" in result.stdout:
            print("✅ CLI commands accessible and training commands available")
            return True
        else:
            print(f"❌ CLI test failed: return code {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ CLI test failed with exception: {e}")
        return False

def run_validation():
    """Run complete validation test suite."""
    print("🚀 Quick Validation Test for Accessibility Training System")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Dependencies", test_dependencies),
        ("Class Instantiation", test_class_instantiation),
        ("CLI Accessibility", test_cli_accessibility)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running: {test_name}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 VALIDATION RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED - Training system is ready for use!")
        print("\n📋 Next steps:")
        print("1. Place 5-10 compliant PDFs in data/testing/accessibility/sample_pdfs/")
        print("2. Run: python -m processor.unified_project.src.main organize-training-data \\")
        print("        data/testing/accessibility/sample_pdfs \\")
        print("        data/testing/accessibility/organized --verbose")
        print("3. Run: python -m processor.unified_project.src.main extract-accessibility-patterns \\")
        print("        data/testing/accessibility/organized/train \\")
        print("        data/testing/accessibility/results --verbose")
        return True
    else:
        print("⚠️  SOME TESTS FAILED - Review failures before proceeding")
        return False

if __name__ == "__main__":
    success = run_validation()
    sys.exit(0 if success else 1)
