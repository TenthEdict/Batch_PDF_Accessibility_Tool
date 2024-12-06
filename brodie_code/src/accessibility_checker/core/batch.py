import os
from pathlib import Path
import concurrent.futures
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm
from ..core.document import AccessibilityDocumentProcessor  # Changed from .accessibility
from ..ocr.processor import OCRProcessor
from ..utils.retry import RetryHandler, OCRError, OCRTimeoutError

class BatchPDFProcessor:
    def __init__(
        self, 
        input_dir: str, 
        output_dir: str, 
        max_workers: int = 4,
        ocr_processor: Optional[OCRProcessor] = None,
        retry_handler: Optional[RetryHandler] = None
    ):
        """
        Initialize batch processor for PDF accessibility checking.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output files and reports
            max_workers: Maximum number of concurrent processes
            ocr_processor: OCR processor instance for text verification
            retry_handler: Retry handler for error recovery
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.max_workers = max_workers
        self.ocr_processor = ocr_processor
        self.retry_handler = retry_handler
        self.processing_stats: Dict[str, Dict] = {}
        
        # Create output directories
        self.corrections_dir = self.output_dir / "corrections"
        self.reports_dir = self.output_dir / "reports"
        self.processed_dir = self.output_dir / "processed_pdfs"
        self.logs_dir = self.output_dir / "logs"
        self.ocr_dir = self.output_dir / "ocr_results"  # New directory for OCR results
        
        for directory in [self.corrections_dir, self.reports_dir, 
                         self.processed_dir, self.logs_dir, self.ocr_dir]:
            directory.mkdir(parents=True, exist_ok=True)
        
        # Set up logging
        self.setup_logging()

    def setup_logging(self):
        """Configure logging for the batch process."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.logs_dir / f"batch_process_{timestamp}.log"
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )

    def process_single_pdf(self, pdf_path: Path) -> Dict:
        """
        Process a single PDF file and return statistics.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Dict containing processing statistics
        """
        start_time = time.time()
        stats = {
            'filename': pdf_path.name,
            'size_mb': pdf_path.stat().st_size / (1024 * 1024),
            'status': 'failed',
            'errors': [],
            'warnings': [],
            'stats': {},
            'ocr_applied': False,
            'ocr_stats': {}
        }
        
        processor = None
        try:
            # Create output paths
            base_name = pdf_path.stem
            corrections_path = self.corrections_dir / f"{base_name}_corrections.json"
            report_path = self.reports_dir / f"{base_name}_report.json"
            processed_path = self.processed_dir / f"{base_name}_processed.pdf"
            ocr_results_path = self.ocr_dir / f"{base_name}_ocr_results.json"
            
            # Process the PDF
            processor = AccessibilityDocumentProcessor(
                str(pdf_path),
                ocr_processor=self.ocr_processor,
                retry_handler=self.retry_handler
            )
            
            # Extract and analyze document structure
            processor.extract_text_with_positions()
            processor.detect_headings()
            processor.detect_tables()
            processor.analyze_reading_order()
            
            # Save the processed PDF
            try:
                processor.doc.save(str(processed_path))
                logging.info(f"Saved processed PDF to: {processed_path}")
            except Exception as e:
                stats['warnings'].append(f"Failed to save processed PDF: {str(e)}")
                logging.warning(f"Could not save processed PDF for {pdf_path.name}: {str(e)}")
            
            # Verify text with OCR if processor is available
            ocr_stats = {}
            if self.ocr_processor:
                try:
                    ocr_results = processor.verify_text_with_ocr()
                    stats['ocr_applied'] = True
                    ocr_stats = {
                        'pages_processed': len(ocr_results),
                        'confidence_scores': [],
                        'processing_time': 0
                    }
                    
                    # Save OCR results
                    with open(ocr_results_path, 'w', encoding='utf-8') as f:
                        json.dump(ocr_results, f, indent=2)
                        
                except (OCRError, OCRTimeoutError) as e:
                    stats['warnings'].append(f"OCR processing issue: {str(e)}")
                    logging.warning(f"OCR issue for {pdf_path.name}: {str(e)}")
            
            # Export reports
            processor.export_accessibility_report(str(report_path))
            processor.export_corrections(str(corrections_path))
            
            # Collect statistics
            stats['stats'] = {
                'num_pages': len(processor.doc),
                'num_tables': len(processor.tables),
                'num_headings': sum(1 for elem in processor.text_elements 
                                if elem.heading_level is not None),
                'num_corrections': sum(len(corr) for corr in processor.corrections.values()),
                'processing_time': time.time() - start_time
            }
            
            stats['ocr_stats'] = ocr_stats
            
            # Add warnings for potential issues
            if stats['stats']['num_headings'] == 0:
                stats['warnings'].append("No headings detected")
            if any(len(corr) > 10 for corr in processor.corrections.values()):
                stats['warnings'].append("High number of corrections needed on some pages")
                
            stats['status'] = 'success'
            
        except Exception as e:
            stats['status'] = 'failed'
            stats['errors'].append(str(e))
            logging.error(f"Error processing {pdf_path.name}: {str(e)}")
            
        finally:
            # Clean up: close the document
            if processor and processor.doc:
                try:
                    processor.doc.close()
                except Exception as e:
                    logging.error(f"Error closing document {pdf_path.name}: {str(e)}")
        
        return stats

    def process_directory(self) -> pd.DataFrame:
        """
        Process all PDF files in the input directory.
        
        Returns:
            DataFrame containing processing statistics
        """
        # Get list of PDF files
        pdf_files = list(self.input_dir.glob("*.pdf"))
        total_files = len(pdf_files)
        
        if total_files == 0:
            logging.warning("No PDF files found in input directory")
            return pd.DataFrame()
        
        logging.info(f"Starting batch processing of {total_files} PDF files")
        
        # Process files with progress bar
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(self.process_single_pdf, pdf_path): pdf_path 
                      for pdf_path in pdf_files}
            
            with tqdm(total=total_files, desc="Processing PDFs") as pbar:
                for future in concurrent.futures.as_completed(futures):
                    pdf_path = futures[future]
                    try:
                        stats = future.result()
                        self.processing_stats[pdf_path.name] = stats
                    except Exception as e:
                        logging.error(f"Error processing {pdf_path.name}: {str(e)}")
                    pbar.update(1)
        
        # Create summary report
        return self.create_summary_report()

    def create_summary_report(self) -> pd.DataFrame:
        """
        Create a summary report of all processed files.
        
        Returns:
            DataFrame containing processing statistics
        """
        # Convert stats to DataFrame
        df = pd.DataFrame.from_dict(self.processing_stats, orient='index')
        
        # Save detailed JSON report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        detailed_report_path = self.reports_dir / f"batch_summary_{timestamp}.json"
        with open(detailed_report_path, 'w', encoding='utf-8') as f:
            json.dump(self.processing_stats, f, indent=2)
        
        # Save Excel summary
        excel_path = self.reports_dir / f"batch_summary_{timestamp}.xlsx"
        with pd.ExcelWriter(excel_path) as writer:
            # Summary sheet with OCR stats
            summary_df = df[['status', 'size_mb', 'ocr_applied']].copy()
            for stat in ['num_pages', 'num_tables', 'num_headings', 'num_corrections']:
                summary_df[stat] = df['stats'].apply(lambda x: x.get(stat, 0) if isinstance(x, dict) else 0)
            
            # Add OCR statistics if available
            if 'ocr_stats' in df.columns:
                for stat in ['pages_processed', 'confidence_scores']:
                    summary_df[f'ocr_{stat}'] = df['ocr_stats'].apply(
                        lambda x: x.get(stat, None) if isinstance(x, dict) else None
                    )
            
            summary_df.to_excel(writer, sheet_name='Summary')
            
            # Warnings sheet
            warnings_df = pd.DataFrame({
                'filename': df.index,
                'warnings': df['warnings'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else '')
            })
            warnings_df = warnings_df[warnings_df['warnings'] != '']
            warnings_df.to_excel(writer, sheet_name='Warnings', index=False)
            
            # Errors sheet
            errors_df = pd.DataFrame({
                'filename': df.index,
                'errors': df['errors'].apply(lambda x: '\n'.join(x) if isinstance(x, list) else '')
            })
            errors_df = errors_df[errors_df['errors'] != '']
            errors_df.to_excel(writer, sheet_name='Errors', index=False)
            
            # OCR Results sheet if applicable
            if df['ocr_applied'].any():
                ocr_df = pd.DataFrame({
                    'filename': df.index,
                    'ocr_applied': df['ocr_applied'],
                    'ocr_pages_processed': df['ocr_stats'].apply(
                        lambda x: x.get('pages_processed', 0) if isinstance(x, dict) else 0
                    ),
                    'avg_confidence': df['ocr_stats'].apply(
                        lambda x: sum(x.get('confidence_scores', [0])) / len(x.get('confidence_scores', [1]))
                        if isinstance(x, dict) and x.get('confidence_scores') else 0
                    )
                })
                ocr_df.to_excel(writer, sheet_name='OCR Results', index=False)
        
        logging.info(f"Batch processing complete. Reports saved to {self.reports_dir}")
        return df
    
def main():
    # Example usage
    input_dir = "path/to/pdf/directory"
    output_dir = "path/to/output/directory"
    
    processor = BatchPDFProcessor(input_dir, output_dir)
    summary_df = processor.process_directory()
    
    # Print summary statistics
    print("\nProcessing Summary:")
    print(f"Total files processed: {len(summary_df)}")
    print(f"Successfully processed: {sum(summary_df['status'] == 'success')}")
    print(f"Failed: {sum(summary_df['status'] == 'failed')}")
    print(f"\nOutput files located in: {output_dir}")

if __name__ == "__main__":
    main()
