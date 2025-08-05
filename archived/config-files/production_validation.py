#!/usr/bin/env python3
"""
Production-Level Batch Processing Validation Script
"""
import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, List, Any
import logging

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "processor" / "unified_project"))

from src.services.enhancement_service import EnhancementService

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ProductionValidator:
    """Comprehensive validation for production-level batch processing."""
    
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.enhancement_service = EnhancementService()
        self.results = {
            'total_files': 0,
            'successful_processing': 0,
            'failed_processing': 0,
            'title_extraction_accuracy': 0,
            'file_size_reductions': [],
            'processing_times': [],
            'pdf_integrity_checks': [],
            'errors': []
        }
        
    def get_pdf_files(self) -> List[Path]:
        """Get all PDF files from input directory."""
        pdf_files = list(self.input_dir.glob("*.pdf"))
        # Filter out non-academic files
        academic_files = []
        skip_files = ['directions.txt', 'Unit 5 Seminar.pdf', 'PS542_Unit9Assignment_SchippB.pdf']
        
        for pdf_file in pdf_files:
            if pdf_file.name not in skip_files:
                academic_files.append(pdf_file)
        
        return academic_files
    
    def get_file_size(self, file_path: Path) -> int:
        """Get file size in bytes."""
        try:
            return file_path.stat().st_size
        except:
            return 0
    
    def validate_pdf_integrity(self, pdf_path: Path) -> Dict[str, Any]:
        """Validate PDF integrity and accessibility."""
        try:
            import fitz
            doc = fitz.open(str(pdf_path))
            
            integrity_check = {
                'can_open': True,
                'page_count': len(doc),
                'has_text': False,
                'has_images': False,
                'metadata_present': False
            }
            
            # Check if document has text and images
            if len(doc) > 0:
                page = doc[0]
                text = page.get_text()
                integrity_check['has_text'] = len(text.strip()) > 0
                
                # Check for images
                image_list = page.get_images()
                integrity_check['has_images'] = len(image_list) > 0
            
            # Check metadata
            metadata = doc.metadata
            integrity_check['metadata_present'] = bool(metadata.get('title') or metadata.get('author'))
            
            doc.close()
            return integrity_check
            
        except Exception as e:
            logger.error(f"PDF integrity check failed for {pdf_path.name}: {e}")
            return {
                'can_open': False,
                'error': str(e)
            }
    
    def extract_title_for_validation(self, pdf_path: Path) -> str:
        """Extract title using the enhanced algorithm for validation."""
        try:
            from src.enhancers.minimal_pdf_enhancer import MinimalPDFEnhancer
            import pikepdf
            
            enhancer = MinimalPDFEnhancer()
            document = pikepdf.open(str(pdf_path))
            title = enhancer._extract_document_title(document, pdf_path)
            document.close()
            
            return title or "No title extracted"
            
        except Exception as e:
            logger.error(f"Title extraction failed for {pdf_path.name}: {e}")
            return f"Error: {e}"
    
    def process_single_file(self, input_file: Path) -> Dict[str, Any]:
        """Process a single PDF file and collect metrics."""
        logger.info(f"Processing: {input_file.name}")
        
        # Create output filename with "_enhanced" suffix instead of "enhanced_" prefix
        base_name = input_file.stem  # filename without extension
        extension = input_file.suffix  # .pdf
        output_file = self.output_dir / f"{base_name}_enhanced{extension}"
        start_time = time.time()
        
        # Get initial file size
        initial_size = self.get_file_size(input_file)
        
        # Extract title for validation
        extracted_title = self.extract_title_for_validation(input_file)
        
        # Process the file
        try:
            success = self.enhancement_service.enhance_document(
                input_file, output_file, mode="academic"
            )
            
            processing_time = time.time() - start_time
            
            if success and output_file.exists():
                # Get final file size
                final_size = self.get_file_size(output_file)
                size_reduction = ((initial_size - final_size) / initial_size * 100) if initial_size > 0 else 0
                
                # Validate PDF integrity
                integrity_check = self.validate_pdf_integrity(output_file)
                
                return {
                    'filename': input_file.name,
                    'success': True,
                    'processing_time': processing_time,
                    'initial_size': initial_size,
                    'final_size': final_size,
                    'size_reduction_percent': size_reduction,
                    'extracted_title': extracted_title,
                    'integrity_check': integrity_check
                }
            else:
                return {
                    'filename': input_file.name,
                    'success': False,
                    'processing_time': processing_time,
                    'error': 'Processing failed or output file not created',
                    'extracted_title': extracted_title
                }
                
        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Processing failed for {input_file.name}: {e}")
            return {
                'filename': input_file.name,
                'success': False,
                'processing_time': processing_time,
                'error': str(e),
                'extracted_title': extracted_title
            }
    
    def validate_title_accuracy(self, results: List[Dict[str, Any]]) -> float:
        """Validate title extraction accuracy based on known good titles."""
        accurate_titles = 0
        total_titles = 0
        
        # Define expected titles for validation
        expected_titles = {
            "1-s2.0-S0148296321001661-main.pdf": "share or hide",
            "J History Behavioral Science - 2019 - Lussier - Of Maslow  motives  and managers  The hierarchy of needs in American.pdf": "maslow",
            "J Occupat   Organ Psyc - 2016 - Miao - A meta‐analysis of emotional intelligence and work attitudes.pdf": "meta-analysis",
            "Understanding students  motivation towards proactive career behaviours through goal-setting theory and the job demands resources model.pdf": "students"
        }
        
        for result in results:
            if result.get('extracted_title'):
                total_titles += 1
                filename = result['filename']
                extracted = result['extracted_title'].lower()
                
                if filename in expected_titles:
                    expected_key = expected_titles[filename]
                    if expected_key in extracted:
                        accurate_titles += 1
                        logger.info(f"✅ Title accuracy validated for {filename}")
                    else:
                        logger.warning(f"❌ Title accuracy failed for {filename}: got '{extracted}', expected to contain '{expected_key}'")
                else:
                    # For files without expected titles, check if it's not a journal name
                    journal_indicators = ['journal of', 'proceedings', 'ieee', 'acm', 'vol.', 'issue']
                    is_journal = any(indicator in extracted for indicator in journal_indicators)
                    if not is_journal:
                        accurate_titles += 1
                        logger.info(f"✅ Title extraction appears valid for {filename}: '{extracted[:50]}...'")
                    else:
                        logger.warning(f"❌ Possible journal name extracted for {filename}: '{extracted}'")
        
        return (accurate_titles / total_titles * 100) if total_titles > 0 else 0
    
    def run_validation(self) -> Dict[str, Any]:
        """Run comprehensive production validation."""
        logger.info("Starting Production-Level Batch Processing Validation")
        logger.info(f"Input directory: {self.input_dir}")
        logger.info(f"Output directory: {self.output_dir}")
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Get academic PDF files
        pdf_files = self.get_pdf_files()
        logger.info(f"Found {len(pdf_files)} academic PDF files for validation")
        
        self.results['total_files'] = len(pdf_files)
        processing_results = []
        
        # Process each file
        for pdf_file in pdf_files:
            result = self.process_single_file(pdf_file)
            processing_results.append(result)
            
            if result['success']:
                self.results['successful_processing'] += 1
                self.results['processing_times'].append(result['processing_time'])
                if 'size_reduction_percent' in result:
                    self.results['file_size_reductions'].append(result['size_reduction_percent'])
                if 'integrity_check' in result:
                    self.results['pdf_integrity_checks'].append(result['integrity_check'])
            else:
                self.results['failed_processing'] += 1
                self.results['errors'].append({
                    'filename': result['filename'],
                    'error': result.get('error', 'Unknown error')
                })
        
        # Calculate title extraction accuracy
        self.results['title_extraction_accuracy'] = self.validate_title_accuracy(processing_results)
        
        # Calculate summary statistics
        if self.results['processing_times']:
            self.results['avg_processing_time'] = sum(self.results['processing_times']) / len(self.results['processing_times'])
            self.results['max_processing_time'] = max(self.results['processing_times'])
        
        if self.results['file_size_reductions']:
            self.results['avg_size_reduction'] = sum(self.results['file_size_reductions']) / len(self.results['file_size_reductions'])
            self.results['min_size_reduction'] = min(self.results['file_size_reductions'])
            self.results['max_size_reduction'] = max(self.results['file_size_reductions'])
        
        # Calculate success rate
        self.results['success_rate'] = (self.results['successful_processing'] / self.results['total_files'] * 100) if self.results['total_files'] > 0 else 0
        
        return {
            'summary': self.results,
            'detailed_results': processing_results
        }
    
    def print_summary(self, validation_results: Dict[str, Any]):
        """Print validation summary."""
        summary = validation_results['summary']
        
        print("\n" + "="*80)
        print("PRODUCTION-LEVEL BATCH PROCESSING VALIDATION SUMMARY")
        print("="*80)
        
        print(f"📁 Total Files Processed: {summary['total_files']}")
        print(f"✅ Successful Processing: {summary['successful_processing']}")
        print(f"❌ Failed Processing: {summary['failed_processing']}")
        print(f"📊 Success Rate: {summary['success_rate']:.1f}%")
        
        print(f"\n🎯 Title Extraction Accuracy: {summary['title_extraction_accuracy']:.1f}%")
        
        if 'avg_processing_time' in summary:
            print(f"\n⏱️  Processing Performance:")
            print(f"   Average Time: {summary['avg_processing_time']:.2f}s")
            print(f"   Maximum Time: {summary['max_processing_time']:.2f}s")
        
        if 'avg_size_reduction' in summary:
            print(f"\n📦 File Size Reduction:")
            print(f"   Average Reduction: {summary['avg_size_reduction']:.1f}%")
            print(f"   Range: {summary['min_size_reduction']:.1f}% - {summary['max_size_reduction']:.1f}%")
        
        # PDF Integrity Summary
        if summary['pdf_integrity_checks']:
            integrity_pass = sum(1 for check in summary['pdf_integrity_checks'] if check.get('can_open', False))
            print(f"\n🔍 PDF Integrity: {integrity_pass}/{len(summary['pdf_integrity_checks'])} files passed")
        
        if summary['errors']:
            print(f"\n❌ Errors Encountered:")
            for error in summary['errors']:
                print(f"   {error['filename']}: {error['error']}")
        
        print("\n" + "="*80)
        
        # Detailed Results
        print("\nDETAILED PROCESSING RESULTS:")
        print("-"*80)
        for result in validation_results['detailed_results']:
            status = "✅" if result['success'] else "❌"
            print(f"{status} {result['filename']}")
            if result['success']:
                print(f"   Title: {result['extracted_title'][:60]}...")
                if 'size_reduction_percent' in result:
                    print(f"   Size Reduction: {result['size_reduction_percent']:.1f}%")
                print(f"   Processing Time: {result['processing_time']:.2f}s")
            else:
                print(f"   Error: {result.get('error', 'Unknown error')}")
            print()

def main():
    """Main validation function."""
    input_dir = Path("data/input")
    output_dir = Path("validation_output")
    
    if not input_dir.exists():
        print(f"❌ Input directory not found: {input_dir}")
        return
    
    validator = ProductionValidator(input_dir, output_dir)
    validation_results = validator.run_validation()
    validator.print_summary(validation_results)
    
    # Save detailed results
    results_file = output_dir / "validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(validation_results, f, indent=2, default=str)
    
    print(f"\n📄 Detailed results saved to: {results_file}")

if __name__ == "__main__":
    main()
