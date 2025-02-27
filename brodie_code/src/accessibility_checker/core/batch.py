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
from ..core.document import AccessibilityDocumentProcessor
from ..ocr.processor import OCRProcessor
from ..utils.retry import RetryHandler, OCRError, OCRTimeoutError
from ..ocr.adaptive_config import AdaptiveOCRConfig


class BatchPDFProcessor:

    def __init__(self, input_dir: str, output_dir: str, max_workers: int=4,
        ocr_processor: Optional[OCRProcessor]=None, retry_handler: Optional
        [RetryHandler]=None, config: Dict[str, any]=None) ->None:
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
        self.adaptive_config = AdaptiveOCRConfig(config or {})
        self.document_configs = {}
        self.dir_types = {'corrections': 'corrections', 'reports':
            'reports', 'processed': 'processed_pdfs', 'logs': 'logs', 'ocr':
            'ocr_results'}
        self.create_base_output_dirs()
        self.setup_logging()

    def create_base_output_dirs(self) ->None:
        """Create base output directory structure."""
        for dir_type in self.dir_types.values():
            base_dir = self.output_dir / dir_type
            base_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self) ->None:
        """Configure logging for the batch process."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = self.output_dir / 'logs' / f'batch_process_{timestamp}.log'
        logging.basicConfig(level=logging.INFO, format=
            '%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.
            FileHandler(log_file), logging.StreamHandler()])

    def get_output_subdirs(self, input_file: Path) ->Dict[str, Path]:
        """
        Get output subdirectories for a given input file, maintaining the subdirectory structure.
        """
        try:
            rel_path = input_file.parent.relative_to(self.input_dir)
        except ValueError:
            rel_path = Path()
        output_dirs = {}
        for dir_type, dir_name in self.dir_types.items():
            full_path = self.output_dir / dir_name / rel_path
            full_path.mkdir(parents=True, exist_ok=True)
            output_dirs[dir_type] = full_path
        return output_dirs

    def process_single_pdf(self, pdf_path: Path) ->Dict:
        """Process a single PDF file with improved error handling and OCR support."""
        start_time = time.time()
        stats = {'filename': pdf_path.name, 'size_mb': pdf_path.stat().
            st_size / (1024 * 1024), 'status': 'failed', 'errors': [],
            'warnings': [], 'stats': {}, 'ocr_applied': False, 'ocr_stats': {}}
        processor = None
        try:
            processor = AccessibilityDocumentProcessor(str(pdf_path),
                ocr_processor=self.ocr_processor, retry_handler=self.
                retry_handler, enable_ocr=True)
            try:
                processor.extract_text_with_positions()
            except ProcessingError as e:
                if 'appears to be scanned' in str(e):
                    stats['warnings'].append(
                        'Document appears to be scanned - attempting OCR')
                else:
                    raise
            processor.detect_headings()
            processor.detect_tables()
            processor.analyze_reading_order()
            stats.update({'status': 'success', 'stats': {'num_pages': len(
                processor.doc), 'num_tables': len(processor.tables),
                'num_headings': sum(1 for elem in processor.text_elements if
                elem.heading_level is not None), 'num_corrections': sum(len
                (corr) for corr in processor.corrections.values()),
                'processing_time': time.time() - start_time}, 'ocr_applied':
                bool(processor.ocr_results), 'ocr_stats': {
                'pages_processed': len(processor.ocr_results) if processor.
                ocr_results else 0, 'average_confidence': processor.
                ocr_processor.get_last_confidence() if processor.
                ocr_processor else 0}})
        except Exception as e:
            error_msg = f'Error processing {pdf_path.name}: {str(e)}'
            stats['errors'].append(error_msg)
            logging.error(error_msg, exc_info=True)
        finally:
            if processor and hasattr(processor, 'doc'):
                processor.doc.close()
        return stats

    def process_directory(self) ->pd.DataFrame:
        """Process all PDF files in the input directory and its subdirectories."""
        pdf_files = list(self.input_dir.rglob('*.pdf'))
        logging.info(
            f'Found {len(pdf_files)} PDF files in {self.input_dir} and its subdirectories'
            )
        if not pdf_files:
            logging.warning(
                'No PDF files found in input directory or subdirectories')
            return pd.DataFrame()
        processed_stats = []
        for pdf_path in tqdm(pdf_files, desc='Processing PDFs'):
            try:
                rel_path = pdf_path.parent.relative_to(self.input_dir)
                logging.info(
                    f'Processing file: {pdf_path} (in subdirectory: {rel_path})'
                    )
                stats = self.process_single_pdf(pdf_path)
                processed_stats.append(stats)
                logging.info(f'Completed processing: {pdf_path}')
            except Exception as e:
                logging.error(f'Error processing {pdf_path.name}: {str(e)}')
                processed_stats.append({'filename': pdf_path.name,
                    'subdirectory': str(pdf_path.parent.relative_to(self.
                    input_dir)), 'status': 'failed', 'errors': [str(e)]})
        if processed_stats:
            df = pd.DataFrame(processed_stats)
            df.set_index(['subdirectory', 'filename'], inplace=True)
            self.save_summary_report(df)
            return df
        else:
            return pd.DataFrame()

    def save_summary_report(self, df: pd.DataFrame) ->None:
        """Save a summary report of the processing results."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = (self.output_dir / 'reports' /
            f'batch_summary_{timestamp}.xlsx')
        with pd.ExcelWriter(report_path) as writer:
            summary_df = df.reset_index()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            errors_df = summary_df[summary_df['status'] == 'failed'][[
                'subdirectory', 'filename', 'errors']]
            if not errors_df.empty:
                errors_df.to_excel(writer, sheet_name='Errors', index=False)
            warnings_df = summary_df[summary_df['warnings'].apply(len) > 0][[
                'subdirectory', 'filename', 'warnings']]
            if not warnings_df.empty:
                warnings_df.to_excel(writer, sheet_name='Warnings', index=False
                    )


def main() ->None:
    input_dir = Path('/app/input')
    output_dir = Path('/app/output')
    print(f'Looking for PDFs in: {input_dir}')
    print(f'Current directory structure:')
    os.system(f'ls -R {input_dir}')
    try:
        processor = BatchPDFProcessor(str(input_dir), str(output_dir))
        summary_df = processor.process_directory()
        print('\nProcessing Summary:')
        print(f'Total files processed: {len(summary_df)}')
        if not summary_df.empty:
            success_count = sum(summary_df['status'] == 'success')
            failed_count = sum(summary_df['status'] == 'failed')
            print(f'Successfully processed: {success_count}')
            print(f'Failed: {failed_count}')
            print('\nProcessed files by subdirectory:')
            for (subdir, filename), row in summary_df.iterrows():
                print(f"  {subdir}/{filename}: {row['status']}")
                if row['errors']:
                    print(f"    Errors: {row['errors']}")
            print(f'\nOutput files located in: {output_dir}')
        else:
            print('\nNo files were processed.')
            print(f'Input directory: {input_dir}')
            print(
                'Please ensure PDF files are present in the input directory or its subdirectories'
                )
    except Exception as e:
        logging.error(f'Error in main process: {str(e)}')
        raise


if __name__ == '__main__':
    main()
