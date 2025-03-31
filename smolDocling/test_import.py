try:
    from docling.core import DoclingDocument
    print("Successfully imported DoclingDocument")
except ImportError as e:
    print(f"Import error: {e}")
    
    # Print Python path to help diagnose
    import sys
    print("\nPython path:")
    for p in sys.path:
        print(p)
