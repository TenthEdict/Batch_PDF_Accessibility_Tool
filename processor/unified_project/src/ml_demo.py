#!/usr/bin/env python3
"""
ML Demo Script for ePubs Accessibility Enhancement

This script demonstrates the adaptive ML capabilities for document learning
and text layer enhancement. It shows how the system learns from document
patterns and improves OCR success rates over time. The intelligent OCR
processing is the default method for all academic documents and journal articles.
"""

import argparse
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any
import json
import time

# Add the src directory to the path
sys.path.insert(0, str(Path(__file__).parent))

from enhancers.adaptive_ml_enhancer import AdaptiveMLEnhancer
from enhancers.intelligent_ocr_enhancer import IntelligentOCREnhancer
from services.enhancement_service import EnhancementService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def demo_adaptive_ml_learning(input_dir: Path, output_dir: Path):
    """
    Demonstrate adaptive ML learning capabilities.
    
    Args:
        input_dir: Directory containing PDF files to process
        output_dir: Directory to save enhanced files and results
    """
    logger.info("Starting Adaptive ML Learning Demo")
    
    # Initialize adaptive ML enhancer
    try:
        adaptive_ml = AdaptiveMLEnhancer()
        logger.info("✓ Adaptive ML Enhancer initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Adaptive ML Enhancer: {e}")
        return False
    
    # Initialize intelligent OCR enhancer
    try:
        intelligent_ocr = IntelligentOCREnhancer()
        logger.info("✓ Intelligent OCR Enhancer initialized successfully")
    except Exception as e:
        logger.error(f"✗ Failed to initialize Intelligent OCR Enhancer: {e}")
        return False
    
    # Get PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files and demonstrate learning
    results = []
    learning_stats = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"\n--- Processing file {i}/{len(pdf_files)}: {pdf_file.name} ---")
        
        try:
            # Extract document features
            document_features = intelligent_ocr._extract_document_features(pdf_file)
            logger.info(f"Document features: {json.dumps(document_features, indent=2)}")
            
            # Get ML analysis
            ml_analysis = adaptive_ml.enhance(document_features)
            logger.info(f"ML analysis: {json.dumps(ml_analysis, indent=2)}")
            
            # Get optimized OCR parameters
            ocr_params = intelligent_ocr._get_optimized_ocr_parameters(document_features)
            logger.info(f"Optimized OCR parameters: {json.dumps(ocr_params, indent=2)}")
            
            # Perform OCR processing
            ocr_result = intelligent_ocr._perform_intelligent_ocr(pdf_file, ocr_params)
            logger.info(f"OCR result - Success: {ocr_result.success}, Confidence: {ocr_result.confidence_score:.2f}")
            
            # Learn from results
            feedback = {
                'success': ocr_result.success,
                'quality_score': ocr_result.quality_metrics.get('quality_score', 0.0),
                'ocr_params': ocr_params,
                'processing_time': ocr_result.processing_time,
                'confidence_score': ocr_result.confidence_score
            }
            
            adaptive_ml.enhance(document_features, feedback=feedback)
            
            # Collect results
            result = {
                'file': pdf_file.name,
                'features': document_features,
                'ml_analysis': ml_analysis,
                'ocr_params': ocr_params,
                'ocr_result': {
                    'success': ocr_result.success,
                    'confidence': ocr_result.confidence_score,
                    'quality_score': ocr_result.quality_metrics.get('quality_score', 0.0),
                    'processing_time': ocr_result.processing_time
                }
            }
            results.append(result)
            
            # Get learning statistics
            stats = adaptive_ml.get_learning_statistics()
            learning_stats.append(stats)
            logger.info(f"Learning stats: {json.dumps(stats, indent=2)}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            continue
    
    # Save results
    output_dir.mkdir(parents=True, exist_ok=True)
    
    results_file = output_dir / "ml_learning_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_file}")
    
    # Generate summary
    generate_learning_summary(results, learning_stats, output_dir)
    
    return True


def demo_enhancement_service_integration(input_dir: Path, output_dir: Path):
    """
    Demonstrate integration with the enhancement service using default intelligent OCR.
    
    Args:
        input_dir: Directory containing PDF files to process
        output_dir: Directory to save enhanced files
    """
    logger.info("Starting Enhancement Service Integration Demo")
    
    # Initialize enhancement service
    try:
        enhancement_service = EnhancementService()
        logger.info("✓ Enhancement Service initialized successfully")
        
        # Check available enhancers
        available_enhancers = enhancement_service.get_available_enhancers()
        logger.info(f"Available enhancers: {json.dumps(available_enhancers, indent=2)}")
        
        # Get capabilities
        capabilities = enhancement_service.get_enhancement_capabilities()
        logger.info(f"Enhancement capabilities: {json.dumps(capabilities, indent=2)}")
        
    except Exception as e:
        logger.error(f"✗ Failed to initialize Enhancement Service: {e}")
        return False
    
    # Get PDF files
    pdf_files = list(input_dir.glob("*.pdf"))
    if not pdf_files:
        logger.error(f"No PDF files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    
    # Process files using enhancement service
    results = []
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"\n--- Processing file {i}/{len(pdf_files)}: {pdf_file.name} ---")
        
        try:
            # Create output path
            output_file = output_dir / f"{pdf_file.stem}_enhanced.pdf"
            
            # Process with default intelligent OCR (optimized for academic documents)
            success = enhancement_service.enhance_document(
                input_path=pdf_file,
                output_path=output_file
                # No mode specified - uses intelligent OCR by default
            )
            
            result = {
                'file': pdf_file.name,
                'success': success,
                'output_file': str(output_file) if success else None
            }
            results.append(result)
            
            logger.info(f"Processing result: {'✓ Success' if success else '✗ Failed'}")
            
        except Exception as e:
            logger.error(f"Error processing {pdf_file.name}: {e}")
            results.append({
                'file': pdf_file.name,
                'success': False,
                'error': str(e)
            })
            continue
    
    # Save results
    results_file = output_dir / "enhancement_service_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"Results saved to {results_file}")
    
    # Generate summary
    generate_enhancement_summary(results, output_dir)
    
    return True


def generate_learning_summary(results: List[Dict], learning_stats: List[Dict], output_dir: Path):
    """Generate a summary of the learning demonstration."""
    logger.info("\n--- Learning Summary ---")
    
    # Calculate statistics
    total_files = len(results)
    successful_ocr = sum(1 for r in results if r['ocr_result']['success'])
    avg_confidence = sum(r['ocr_result']['confidence'] for r in results) / total_files if total_files > 0 else 0
    avg_quality = sum(r['ocr_result']['quality_score'] for r in results) / total_files if total_files > 0 else 0
    
    # Get final learning stats
    final_stats = learning_stats[-1] if learning_stats else {}
    
    summary = {
        'total_files_processed': total_files,
        'successful_ocr_count': successful_ocr,
        'success_rate': successful_ocr / total_files if total_files > 0 else 0,
        'average_confidence': avg_confidence,
        'average_quality_score': avg_quality,
        'final_learning_stats': final_stats,
        'pattern_learning_progress': {
            'total_patterns': final_stats.get('total_patterns', 0),
            'pattern_types': final_stats.get('pattern_types', []),
            'avg_success_rate': final_stats.get('avg_success_rate', 0.0)
        }
    }
    
    logger.info(f"Total files processed: {summary['total_files_processed']}")
    logger.info(f"Successful OCR: {summary['successful_ocr_count']}/{summary['total_files_processed']}")
    logger.info(f"Success rate: {summary['success_rate']:.2%}")
    logger.info(f"Average confidence: {summary['average_confidence']:.2f}")
    logger.info(f"Average quality score: {summary['average_quality_score']:.2f}")
    logger.info(f"Total patterns learned: {summary['pattern_learning_progress']['total_patterns']}")
    logger.info(f"Pattern types: {summary['pattern_learning_progress']['pattern_types']}")
    
    # Save summary
    summary_file = output_dir / "learning_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_file}")


def generate_enhancement_summary(results: List[Dict], output_dir: Path):
    """Generate a summary of the enhancement service demonstration."""
    logger.info("\n--- Enhancement Service Summary ---")
    
    # Calculate statistics
    total_files = len(results)
    successful_enhancements = sum(1 for r in results if r['success'])
    
    summary = {
        'total_files_processed': total_files,
        'successful_enhancements': successful_enhancements,
        'success_rate': successful_enhancements / total_files if total_files > 0 else 0,
        'failed_files': [r['file'] for r in results if not r['success']]
    }
    
    logger.info(f"Total files processed: {summary['total_files_processed']}")
    logger.info(f"Successful enhancements: {summary['successful_enhancements']}/{summary['total_files_processed']}")
    logger.info(f"Success rate: {summary['success_rate']:.2%}")
    
    if summary['failed_files']:
        logger.info(f"Failed files: {summary['failed_files']}")
    
    # Save summary
    summary_file = output_dir / "enhancement_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    logger.info(f"Summary saved to {summary_file}")


def main():
    """Main function for the ML demo script."""
    parser = argparse.ArgumentParser(
        description="Demonstrate adaptive ML capabilities for document enhancement"
    )
    parser.add_argument(
        "input_dir",
        type=Path,
        help="Directory containing PDF files to process"
    )
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory to save enhanced files and results"
    )
    parser.add_argument(
        "--demo-type",
        choices=["learning", "integration", "both"],
        default="both",
        help="Type of demonstration to run"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Validate input directory
    if not args.input_dir.exists():
        logger.error(f"Input directory does not exist: {args.input_dir}")
        return 1
    
    # Create output directory
    args.output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info("=" * 60)
    logger.info("ePubs Adaptive ML Demo")
    logger.info("=" * 60)
    logger.info(f"Input directory: {args.input_dir}")
    logger.info(f"Output directory: {args.output_dir}")
    logger.info(f"Demo type: {args.demo_type}")
    
    success = True
    
    try:
        if args.demo_type in ["learning", "both"]:
            logger.info("\n" + "=" * 40)
            logger.info("DEMO 1: Adaptive ML Learning")
            logger.info("=" * 40)
            success &= demo_adaptive_ml_learning(args.input_dir, args.output_dir / "learning_demo")
        
        if args.demo_type in ["integration", "both"]:
            logger.info("\n" + "=" * 40)
            logger.info("DEMO 2: Enhancement Service Integration")
            logger.info("=" * 40)
            success &= demo_enhancement_service_integration(args.input_dir, args.output_dir / "integration_demo")
        
        if success:
            logger.info("\n" + "=" * 60)
            logger.info("✓ All demonstrations completed successfully!")
            logger.info("=" * 60)
            return 0
        else:
            logger.error("\n" + "=" * 60)
            logger.error("✗ Some demonstrations failed!")
            logger.error("=" * 60)
            return 1
            
    except KeyboardInterrupt:
        logger.info("\nDemo interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
