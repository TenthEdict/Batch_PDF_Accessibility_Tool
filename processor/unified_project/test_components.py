#!/usr/bin/env python3
"""
Quick validation test for new academic web compression components.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
sys.path.append(str(Path(__file__).parent / "src"))

def test_component_imports():
    """Test that all new components can be imported successfully."""
    print("Testing component imports...")
    
    try:
        from enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer
        print("✅ MinimalPDFEnhancer imported successfully")
    except ImportError as e:
        print(f"❌ MinimalPDFEnhancer import failed: {e}")
        return False
    
    try:
        from enhancers.compression_enhancer import CompressionEnhancer
        print("✅ CompressionEnhancer imported successfully")
    except ImportError as e:
        print(f"❌ CompressionEnhancer import failed: {e}")
        return False
    
    try:
        from enhancers.ocr_enhancer import OCREnhancer
        print("✅ OCREnhancer imported successfully")
    except ImportError as e:
        print(f"❌ OCREnhancer import failed: {e}")
        return False
    
    try:
        from services.enhancement_service import EnhancementService
        print("✅ EnhancementService imported successfully")
    except ImportError as e:
        print(f"❌ EnhancementService import failed: {e}")
        return False
    
    return True

def test_enhancer_capabilities():
    """Test that enhancers report their capabilities correctly."""
    print("\nTesting enhancer capabilities...")
    
    try:
        from enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer
        from enhancers.compression_enhancer import CompressionEnhancer
        from enhancers.ocr_enhancer import OCREnhancer
        
        # Test MinimalPDFEnhancer
        minimal_enhancer = MinimalPDFEnhancer()
        capabilities = minimal_enhancer.get_capabilities()
        print(f"✅ MinimalPDFEnhancer capabilities: {len(capabilities)} features")
        for cap in capabilities:
            print(f"   - {cap}")
        
        # Test CompressionEnhancer
        compression_enhancer = CompressionEnhancer()
        capabilities = compression_enhancer.get_capabilities()
        print(f"✅ CompressionEnhancer capabilities: {len(capabilities)} features")
        for cap in capabilities:
            print(f"   - {cap}")
        
        # Test OCREnhancer
        ocr_enhancer = OCREnhancer()
        capabilities = ocr_enhancer.get_capabilities()
        print(f"✅ OCREnhancer capabilities: {len(capabilities)} features")
        for cap in capabilities:
            print(f"   - {cap}")
        
        return True
        
    except Exception as e:
        print(f"❌ Capability testing failed: {e}")
        return False

def test_enhancement_service():
    """Test that EnhancementService initializes with new enhancers."""
    print("\nTesting EnhancementService...")
    
    try:
        from services.enhancement_service import EnhancementService
        
        service = EnhancementService()
        
        # Test available enhancers
        available = service.get_available_enhancers()
        print(f"✅ Available enhancers: {available}")
        
        # Test enhancement capabilities
        capabilities = service.get_enhancement_capabilities()
        print(f"✅ Enhancement capabilities: {len(capabilities)} enhancer types")
        for enhancer_name, caps in capabilities.items():
            print(f"   - {enhancer_name}: {len(caps)} capabilities")
        
        return True
        
    except Exception as e:
        print(f"❌ EnhancementService testing failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Academic Web Compression Component Validation ===\n")
    
    success = True
    success &= test_component_imports()
    success &= test_enhancer_capabilities()
    success &= test_enhancement_service()
    
    print(f"\n=== Validation {'PASSED' if success else 'FAILED'} ===")
    sys.exit(0 if success else 1)
