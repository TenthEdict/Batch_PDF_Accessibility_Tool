# ML Integration

Machine learning integration for intelligent document processing.

## Setup

### Install ML Dependencies
```bash
pip install epubs-accessibility[ml]
# Or manually
pip install torch transformers scikit-learn joblib numpy
```

### Configuration
```yaml
# config/adaptive_ml.yaml
adaptive_ml:
  learning:
    enabled: true
    min_samples_for_learning: 5
    confidence_threshold: 0.7
  models:
    pattern_classifier:
      model_type: "random_forest"
      n_estimators: 100
  performance:
    batch_size: 16
    max_workers: 4
    timeout_seconds: 60
```

## Processing

### Default Processing (Academic Documents)
```python
from processor.unified_project.src.services.enhancement_service import EnhancementService

service = EnhancementService()

# Intelligent OCR is default for academic documents
success = service.enhance_document(
    input_path="document.pdf",
    output_path="enhanced_document.pdf"
)
```

### Explicit Academic Mode
```python
# Also uses intelligent OCR
success = service.enhance_document(
    input_path="document.pdf",
    output_path="enhanced_document.pdf",
    mode="academic"
)
```

## Pipeline Usage

### Direct ML Enhancer
```python
from processor.unified_project.src.enhancers.adaptive_ml_enhancer import AdaptiveMLEnhancer

ml_enhancer = AdaptiveMLEnhancer()

# Analyze document features
document_features = {
    'text_length': 5000,
    'has_equations': 1.0,
    'has_tables': 0.0,
    'is_academic': 1.0
}

analysis = ml_enhancer.enhance(document_features)
```

### Intelligent OCR Enhancer
```python
from processor.unified_project.src.enhancers.intelligent_ocr_enhancer import IntelligentOCREnhancer

intelligent_ocr = IntelligentOCREnhancer()

success = intelligent_ocr.enhance_file(
    input_path="document.pdf",
    output_path="enhanced_document.pdf"
)

stats = intelligent_ocr.get_processing_statistics()
```

### Demo Script
```bash
# Run ML demo
python processor/unified_project/src/ml_demo.py /path/to/pdfs /path/to/output

# Specific demo types
python processor/unified_project/src/ml_demo.py /path/to/pdfs /path/to/output --demo-type learning
python processor/unified_project/src/ml_demo.py /path/to/pdfs /path/to/output --demo-type integration --verbose
```

### Learning Statistics
```python
stats = ml_enhancer.get_learning_statistics()
print(f"Total patterns: {stats['total_patterns']}")
print(f"Average success rate: {stats['avg_success_rate']:.2%}")
```
