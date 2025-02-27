import os
import asyncio
from pathlib import Path
import logging
import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import pandas as pd
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor
from .anthropic_processor import create_enhanced_processor
from ..utils.retry import RetryHandler
from ..ocr.processor import OCRProcessor


class EnhancedBatchProcessor:

    def __init__(self, input_dir: str, output_dir: str, max_workers: int=4,
        ocr_processor: Optional[OCRProcessor]=None, retry_handler: Optional
        [RetryHandler]=None, anthropic_api_key: Optional[str]=None,
        anthropic_model: Optional[str]=None) ->None:
        """
        Initialize enhanced batch processor with Anthropic integration.
        
        Args:
            input_dir: Directory containing PDF files
            output_dir: Directory for output files and reports
            max_workers: Maximum number of concurrent processes
            ocr_processor: OCR processor instance
            retry_handler: Retry handler for error recovery
            anthropic_api_key: Optional Anthropic API key (defaults to env var)
            anthropic_model: Optional Anthropic model name
        """
        self.input_dir = Path(input_dir).resolve()
        self.output_dir = Path(output_dir).resolve()
        self.max_workers = max_workers
        self.ocr_processor = ocr_processor
        self.retry_handler = retry_handler
        self.anthropic_api_key = anthropic_api_key or os.getenv(
            'ANTHROPIC_API_KEY')
        self.anthropic_model = anthropic_model
        self.processing_stats: Dict[str, Dict] = {}
        self.dir_types = {'corrections': 'corrections', 'reports':
            'reports', 'processed': 'processed_pdfs', 'logs': 'logs', 'ocr':
            'ocr_results', 'ai_analysis': 'ai_analysis'}
        self.create_output_dirs()
        self.setup_logging()

    def create_output_dirs(self) ->None:
        """Create all necessary output directories."""
        for dir_type in self.dir_types.values():
            base_dir = self.output_dir / dir_type
            base_dir.mkdir(parents=True, exist_ok=True)

    def setup_logging(self) ->None:
        """Configure logging for the batch process."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_file = (self.output_dir / 'logs' /
            f'enhanced_batch_process_{timestamp}.log')
        logging.basicConfig(level=logging.INFO, format=
            '%(asctime)s - %(levelname)s - %(message)s', handlers=[logging.
            FileHandler(log_file), logging.StreamHandler()])

    def get_output_subdirs(self, input_file: Path) ->Dict[str, Path]:
        """Get output subdirectories for a given input file."""
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

    async def process_single_pdf(self, pdf_path: Path) ->Dict:
        """Process a single PDF file with enhanced analysis."""
        start_time = time.time()
        stats = {'filename': pdf_path.name, 'subdirectory': str(pdf_path.
            parent.relative_to(self.input_dir)), 'size_mb': pdf_path.stat()
            .st_size / (1024 * 1024), 'status': 'failed', 'errors': [],
            'warnings': [], 'stats': {}, 'ocr_applied': False, 'ocr_stats':
            {}, 'ai_analysis': {}}
        try:
            output_dirs = self.get_output_subdirs(pdf_path)
            base_name = pdf_path.stem
            corrections_path = output_dirs['corrections'
                ] / f'{base_name}_corrections.json'
            report_path = output_dirs['reports'] / f'{base_name}_report.json'
            processed_path = output_dirs['processed'
                ] / f'{base_name}_processed.pdf'
            ai_analysis_path = output_dirs['ai_analysis'
                ] / f'{base_name}_ai_analysis.json'
            processor = create_enhanced_processor(str(pdf_path), api_key=
                self.anthropic_api_key, model=self.anthropic_model,
                ocr_processor=self.ocr_processor, retry_handler=self.
                retry_handler)
            processor.extract_text_with_positions()
            processor.detect_headings()
            processor.detect_tables()
            processor.analyze_reading_order()
            try:
                processor.doc.save(str(processed_path))
                logging.info(f'Saved processed PDF to: {processed_path}')
            except Exception as e:
                stats['warnings'].append(
                    f'Failed to save processed PDF: {str(e)}')
            try:
                ai_analysis = await processor.analyze_with_claude()
                stats['ai_analysis'] = ai_analysis
                with open(ai_analysis_path, 'w', encoding='utf-8') as f:
                    json.dump(ai_analysis, f, indent=2)
            except Exception as e:
                stats['warnings'].append(f'AI analysis failed: {str(e)}')
                logging.warning(
                    f'AI analysis failed for {pdf_path.name}: {str(e)}')
            await processor.export_enhanced_report(str(report_path))
            stats.update({'status': 'success', 'stats': {'num_pages': len(
                processor.doc), 'num_tables': len(processor.tables),
                'num_headings': sum(1 for elem in processor.text_elements if
                elem.heading_level is not None), 'num_corrections': sum(len
                (corr) for corr in processor.corrections.values()),
                'processing_time': time.time() - start_time}})
        except Exception as e:
            error_msg = f'Error processing {pdf_path.name}: {str(e)}'
            logging.error(error_msg)
            stats['errors'].append(error_msg)
        return stats

    async def process_directory(self) ->pd.DataFrame:
        """Process all PDF files in the input directory and subdirectories."""
        pdf_files = list(self.input_dir.rglob('*.pdf'))
        logging.info(
            f'Found {len(pdf_files)} PDF files in {self.input_dir} and its subdirectories'
            )
        if not pdf_files:
            logging.warning(
                'No PDF files found in input directory or subdirectories')
            return pd.DataFrame()
        tasks = []
        for pdf_path in pdf_files:
            tasks.append(self.process_single_pdf(pdf_path))
        processed_stats = await asyncio.gather(*tasks)
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
            f'enhanced_batch_summary_{timestamp}.xlsx')
        with pd.ExcelWriter(report_path) as writer:
            summary_df = df.reset_index()
            summary_df.to_excel(writer, sheet_name='Summary', index=False)
            if 'ai_analysis' in df.columns:
                ai_summary = summary_df[['subdirectory', 'filename',
                    'ai_analysis']]
                ai_summary.to_excel(writer, sheet_name='AI Analysis', index
                    =False)
            errors_df = summary_df[summary_df['status'] == 'failed'][[
                'subdirectory', 'filename', 'errors']]
            if not errors_df.empty:
                errors_df.to_excel(writer, sheet_name='Errors', index=False)
            warnings_df = summary_df[summary_df['warnings'].apply(len) > 0][[
                'subdirectory', 'filename', 'warnings']]
            if not warnings_df.empty:
                warnings_df.to_excel(writer, sheet_name='Warnings', index=False
                    )


async def main():
    input_dir = Path('/app/input')
    output_dir = Path('/app/output')
    print(f'Looking for PDFs in: {input_dir}')
    print(f'Current directory structure:')
    os.system(f'ls -R {input_dir}')
    try:
        processor = EnhancedBatchProcessor(str(input_dir), str(output_dir),
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'))
        summary_df = await processor.process_directory()
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
            print('Please ensure PDF files are present in the input directory')
    except Exception as e:
        logging.error(f'Error in main process: {str(e)}')
        raise


if __name__ == '__main__':
    asyncio.run(main())
