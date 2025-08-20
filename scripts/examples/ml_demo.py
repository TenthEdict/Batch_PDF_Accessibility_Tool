#!/usr/bin/env python3
"""
ML-Enhanced Document Processing Demonstration

This script demonstrates the adaptive ML capabilities of the ePubs document processor,
showcasing document-level learning and OCR configuration optimization.
"""

import sys
import json
from pathlib import Path

# Add the project root to Python path to access processor modules
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    from processor.unified_project.src.enhancers.adaptive_ml_enhancer import AdaptiveMLEnhancer
    from processor.unified_project.src.enhancers.intelligent_ocr_enhancer import IntelligentOCREnhancer
    print("✅ ML enhancers imported successfully")
except ImportError as e:
    print(f"❌ Failed to import ML enhancers: {e}")
    print("   Make sure you're running this from the project directory")
    print("   and that all dependencies are installed with: pip install epubs-accessibility[ml]")
    sys.exit(1)


def demonstrate_ml_learning():
    """Demonstrate the ML learning capabilities."""
    print("🧠 ePubs ML-Enhanced Document Processing Demonstration")
    print("=" * 60)
    
    try:
        # Initialize ML enhancer
        print("\n📊 Initializing Adaptive ML Enhancer...")
        ml_enhancer = AdaptiveMLEnhancer()
        print(f"✅ ML enhancer initialized with {len(ml_enhancer.document_profiles)} existing profiles")
        
        # Get learning statistics
        stats = ml_enhancer.get_learning_statistics()
        print(f"\n📈 ML Learning Statistics:")
        print(f"   Total document profiles: {stats['total_document_profiles']}")
        print(f"   Successful profiles: {stats['successful_profiles']}")
        print(f"   Average confidence: {stats['average_confidence']:.3f}")
        print(f"   Average success rate: {stats['average_success_rate']:.3f}")
        print(f"   Knowledge base size: {stats['knowledge_base_size_mb']:.2f} MB")
        
        if stats['last_updated'] > 0:
            import time
            last_updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stats['last_updated']))
            print(f"   Last updated: {last_updated}")
        
        # Demonstrate document feature analysis
        print(f"\n🔍 Document Feature Analysis Example:")
        sample_features = {
            'total_pages': 15,
            'file_size_mb': 2.5,
            'avg_text_length_per_page': 3500,
            'avg_words_per_page': 600,
            'has_images': 1.0,
            'has_tables': 1.0,
            'has_equations': 1.0,
            'is_academic': 1.0,
            'is_image_heavy': 0.0
        }
        
        print(f"   Sample academic paper features: {json.dumps(sample_features, indent=4)}")
        
        # Get ML analysis for sample features
        analysis = ml_enhancer.enhance(sample_features)
        if 'adaptive_ml_analysis' in analysis:
            ml_analysis = analysis['adaptive_ml_analysis']
            
            print(f"\n🎯 ML Analysis Results:")
            if 'pattern_match' in ml_analysis:
                pattern = ml_analysis['pattern_match']
                if pattern.get('pattern_found'):
                    print(f"   ✅ Pattern match found (similarity: {pattern['similarity_score']:.3f})")
                    print(f"   📋 Recommended OCR config: {json.dumps(pattern['recommended_ocr_params'], indent=6)}")
                else:
                    print(f"   ❌ No similar patterns found")
            
            if 'quality_prediction' in ml_analysis:
                quality = ml_analysis['quality_prediction']
                print(f"   📊 Predicted quality: {quality['predicted_quality_score']:.3f}")
                print(f"   🏷️  Document type: {quality['factors']['document_type']}")
                print(f"   ⚡ Complexity: {quality['factors']['complexity']}")
            
            if 'optimization_suggestions' in ml_analysis:
                suggestions = ml_analysis['optimization_suggestions']
                print(f"   💡 Optimization suggestions:")
                for suggestion in suggestions:
                    print(f"      • {suggestion}")
        
        # Demonstrate OCR configuration optimization
        print(f"\n⚙️  OCR Configuration Optimization:")
        optimization = ml_enhancer.optimize_ocr_configuration(sample_features)
        print(f"   📝 Optimal configuration: {json.dumps(optimization['optimal_config'], indent=6)}")
        print(f"   🎯 Confidence: {optimization['confidence']:.3f}")
        print(f"   📍 Source: {optimization['source']}")
        
        # Show document profiles overview
        print(f"\n📚 Document Profiles Overview:")
        for i, (doc_id, profile) in enumerate(list(ml_enhancer.document_profiles.items())[:3]):
            print(f"   Document {i+1} (ID: {doc_id[:8]}...):")
            print(f"      🏷️  Type: {'Academic' if profile.features.get('is_academic', 0) > 0.5 else 'General'}")
            print(f"      📊 Success rate: {profile.success_rate:.3f}")
            print(f"      🎯 Confidence: {profile.confidence_score:.3f}")
            print(f"      ⚙️  OCR PSM: {profile.optimal_ocr_config.get('psm', 'N/A')}")
            print(f"      🔧 OCR OEM: {profile.optimal_ocr_config.get('oem', 'N/A')}")
        
        # Demonstrate intelligent OCR enhancer
        print(f"\n🧠 Intelligent OCR Enhancer:")
        try:
            intelligent_ocr = IntelligentOCREnhancer()
            capabilities = intelligent_ocr.get_capabilities()
            print(f"   🎯 Capabilities: {', '.join(capabilities)}")
            
            processing_stats = intelligent_ocr.get_processing_statistics()
            print(f"   📊 Processing statistics:")
            print(f"      Total processed: {processing_stats['total_processed']}")
            print(f"      Successful OCR: {processing_stats['successful_ocr']}")
            print(f"      Success rate: {processing_stats['success_rate']:.3f}")
            print(f"      Average processing time: {processing_stats['avg_processing_time']:.3f}s")
            print(f"      Average confidence: {processing_stats['avg_confidence']:.3f}")
            
        except Exception as e:
            print(f"   ❌ Could not initialize intelligent OCR enhancer: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Demonstration failed: {e}")
        return False


def show_ml_system_architecture():
    """Show the ML system architecture."""
    print(f"\n🏗️  ML System Architecture:")
    print("=" * 40)
    print("""
    📋 Document Analysis
         ↓
    🔍 Feature Extraction
         ↓
    🧠 ML Pattern Matching
         ↓
    ⚙️  OCR Configuration Optimization
         ↓
    🎯 Quality-Based Learning
         ↓
    💾 Knowledge Base Update
    
    Key Components:
    • AdaptiveMLEnhancer: Core learning engine
    • IntelligentOCREnhancer: ML-enhanced OCR processing
    • Document Similarity Analysis: Pattern matching for similar documents
    • Configuration Testing: Real OCR testing for optimization
    • Feedback Learning: Continuous improvement from results
    """)


def show_learning_workflow():
    """Show the document-level learning workflow."""
    print(f"\n🔄 Document-Level Learning Workflow:")
    print("=" * 45)
    print("""
    For Each Document:
    
    1. 📊 Extract Features
       • Document structure (pages, size, content type)
       • Content analysis (tables, equations, images)
       • Academic indicators (citations, figures)
    
    2. 🔍 Find Similar Documents
       • Cosine similarity on feature vectors
       • Confidence-based matching
       • Pattern recognition
    
    3. ⚙️  Apply/Test OCR Configurations
       • Use known optimal configs for similar docs
       • Test multiple configurations if needed
       • Measure quality and confidence
    
    4. 📈 Learn from Results
       • Update document profile
       • Store successful configurations
       • Build similarity patterns
    
    5. 🎯 Improve Future Processing
       • Recommend optimal configs for new docs
       • Predict processing quality
       • Continuous learning loop
    """)


def main():
    """Main demonstration function."""
    print("🚀 Starting ML-Enhanced Document Processing Demonstration")
    
    # Run demonstration
    success = demonstrate_ml_learning()
    
    if success:
        show_ml_system_architecture()
        show_learning_workflow()
        
        print(f"\n✅ ML System Demonstration Complete!")
        print(f"\n🎯 Key Benefits:")
        print("   • Document-specific OCR optimization")
        print("   • Continuous learning and improvement")
        print("   • Pattern recognition for similar documents")
        print("   • Quality prediction and optimization")
        print("   • Adaptive configuration management")
        
        print(f"\n📋 Usage:")
        print("   • Process documents normally - ML learning happens automatically")
        print("   • Each document contributes to the knowledge base")
        print("   • Similar documents benefit from previous learning")
        print("   • System gets smarter with every processed document")
        
        return 0
    else:
        print(f"\n❌ Demonstration failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main())
